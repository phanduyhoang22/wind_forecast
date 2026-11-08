"""
Bon kien truc, mot giao dien chung: forward((B, L, F)) -> (B, len(HORIZONS)).

Diem khac biet lon nhat so voi code cu:

1. MambaBlock o day LA selective state-space model that (S6, Gu & Dao 2023):
   co A, co B va C sinh tu input, co buoc thoi gian delta, co hoi quy trang
   thai h_t = A_bar h_{t-1} + B_bar x_t. Block cu khong co thu nao trong so do
   -- no la gated depthwise CNN, khong phai SSM.

2. Transformer dat dim_feedforward TUONG MINH. Mac dinh cua PyTorch la 2048,
   tuc 32x d_model=64, khien Transformer phinh len 564K tham so. Con so "Mamba
   it hon 10x tham so" trong ban thao den tu do, khong phai tu self-attention.

    py scripts/06_models.py        # in so tham so + tu kiem tra S6
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


# ----------------------------------------------------------------------------
# Mamba: selective state-space model (S6)
# ----------------------------------------------------------------------------

def _scan_sequential(dA, dBx, C):
    """Ban tham chieu, de doc, dung de doi chieu. O(L) buoc tuan tu."""
    B, L, D, N = dA.shape
    h = dA.new_zeros(B, D, N)
    ys = []
    for t in range(L):
        h = dA[:, t] * h + dBx[:, t]
        ys.append(torch.einsum("bdn,bn->bd", h, C[:, t]))
    return torch.stack(ys, dim=1)


def _scan_parallel(dA, dBx, C):
    """Hillis-Steele associative scan: log2(L) buoc thay vi L.

    Hoi quy h_t = a_t h_{t-1} + b_t co toan tu ket hop:
        (a1,b1) . (a2,b2) = (a1 a2,  a2 b1 + b2)
    nen quet duoc song song. Voi L=96 thi 7 buoc thay cho 96 -- khac biet
    giua chay duoc va khong chay duoc khi nhan 5 seed x 4 tram.
    """
    L = dA.shape[1]
    a, b = dA, dBx
    d = 1
    while d < L:
        a_prev = F.pad(a[:, :-d], (0, 0, 0, 0, d, 0), value=1.0)
        b_prev = F.pad(b[:, :-d], (0, 0, 0, 0, d, 0), value=0.0)
        b = a * b_prev + b
        a = a * a_prev
        d *= 2
    return torch.einsum("bldn,bln->bld", b, C)


class MambaBlock(nn.Module):
    """Khoi Mamba (S6). Tham chieu: Gu & Dao 2023, Alg. 2."""

    def __init__(self, d_model, d_state=16, d_conv=4, expand=2, dt_rank=None,
                 dropout=0.1, dt_min=1e-3, dt_max=1e-1, scan="parallel"):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_inner = expand * d_model
        self.dt_rank = math.ceil(d_model / 16) if dt_rank is None else dt_rank
        self.scan = scan

        self.norm = nn.LayerNorm(d_model)
        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, d_conv,
                                groups=self.d_inner, padding=d_conv - 1)

        # x_proj sinh delta, B, C TU CHINH INPUT -- day la co che "selective",
        # thu quyet dinh Mamba khac S4 va la thu block cu khong he co.
        self.x_proj = nn.Linear(self.d_inner, self.dt_rank + 2 * d_state, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)

        # Khoi tao dt_proj sao cho softplus(bias) trai deu tren [dt_min, dt_max].
        std = self.dt_rank ** -0.5
        nn.init.uniform_(self.dt_proj.weight, -std, std)
        dt = torch.exp(torch.rand(self.d_inner)
                       * (math.log(dt_max) - math.log(dt_min)) + math.log(dt_min))
        dt = dt.clamp(min=1e-4)
        with torch.no_grad():                       # nghich dao softplus
            self.dt_proj.bias.copy_(dt + torch.log(-torch.expm1(-dt)))

        # A khoi tao kieu S4D-real: A_n = -(n+1), giu duoi dang log de A luon am.
        A = torch.arange(1, d_state + 1, dtype=torch.float32).repeat(self.d_inner, 1)
        self.A_log = nn.Parameter(torch.log(A))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        self.A_log._no_weight_decay = True          # khong phat weight decay len
        self.D._no_weight_decay = True              # tham so dong hoc cua SSM

        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)
        self.dropout = nn.Dropout(dropout)

    def ssm(self, x):
        """x: (B, L, d_inner) -> (B, L, d_inner)."""
        A = -torch.exp(self.A_log)                                  # (d_inner, N)
        dbc = self.x_proj(x)
        dt, Bm, Cm = torch.split(
            dbc, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        dt = F.softplus(self.dt_proj(dt))                           # (B, L, d_inner)

        # Roi rac hoa ZOH: A_bar = exp(dt A),  B_bar x = dt B x
        dA = torch.exp(dt.unsqueeze(-1) * A)                        # (B,L,d_inner,N)
        dBx = dt.unsqueeze(-1) * Bm.unsqueeze(2) * x.unsqueeze(-1)  # (B,L,d_inner,N)

        scan = _scan_parallel if self.scan == "parallel" else _scan_sequential
        return scan(dA, dBx, Cm) + self.D * x                       # + duong tat D

    def _ssm_fp32(self, x):
        """Chay SSM o float32 ngay ca khi dang bat mixed precision.

        Ly do: quet tich luy exp(dt*A) qua L buoc, o float16 thi tich luy
        underflow ve 0 va mat han tin hieu duong dai -- dung thu ma SSM sinh ra
        de bat. Cac lop tuyen tinh van duoc chay fp16, chi rieng quet la fp32."""
        if x.is_cuda and torch.is_autocast_enabled():
            with torch.autocast(device_type="cuda", enabled=False):
                return self.ssm(x.float()).to(x.dtype)
        return self.ssm(x)

    def forward(self, x):
        residual = x
        x = self.norm(x)
        x_in, z = self.in_proj(x).chunk(2, dim=-1)

        L = x_in.shape[1]
        x_in = self.conv1d(x_in.transpose(1, 2))[:, :, :L].transpose(1, 2)
        x_in = F.silu(x_in)

        y = self._ssm_fp32(x_in)
        y = y * F.silu(z)                # cong gate SiLU, nhan SAU khi qua SSM
        return residual + self.dropout(self.out_proj(y))


class WindMamba(nn.Module):
    def __init__(self, n_features, n_out, d_model=64, n_layers=2,
                 d_state=16, dropout=0.1, scan="parallel"):
        super().__init__()
        self.embed = nn.Linear(n_features, d_model)
        self.layers = nn.ModuleList([
            MambaBlock(d_model, d_state=d_state, dropout=dropout, scan=scan)
            for _ in range(n_layers)])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Sequential(nn.Linear(d_model, 32), nn.ReLU(),
                                  nn.Linear(32, n_out))

    def forward(self, x):
        x = self.embed(x)
        for layer in self.layers:
            x = layer(x)
        return self.head(self.norm(x)[:, -1, :])


# ----------------------------------------------------------------------------
# Transformer
# ----------------------------------------------------------------------------

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float()
                        * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class WindTransformer(nn.Module):
    def __init__(self, n_features, n_out, d_model=64, n_heads=4, n_layers=2,
                 dim_feedforward=128, dropout=0.1, max_len=512):
        # dim_feedforward=128 la 2x d_model -- ty le FFN thong thuong.
        # Mac dinh 2048 cua PyTorch la 32x, va chinh no tao ra con so 564K
        # tham so trong Table 6 cua ban thao.
        super().__init__()
        self.input_proj = nn.Linear(n_features, d_model)
        self.pos = PositionalEncoding(d_model, max_len)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=dim_feedforward,
            dropout=dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Sequential(nn.Linear(d_model, 32), nn.ReLU(),
                                  nn.Linear(32, n_out))

    def forward(self, x):
        x = self.encoder(self.pos(self.input_proj(x)))
        return self.head(self.norm(x)[:, -1, :])


# ----------------------------------------------------------------------------
# LSTM
# ----------------------------------------------------------------------------

class WindLSTM(nn.Module):
    def __init__(self, n_features, n_out, d_model=64, n_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(n_features, d_model, n_layers, batch_first=True,
                            dropout=dropout if n_layers > 1 else 0.0)
        self.head = nn.Sequential(nn.Linear(d_model, 32), nn.ReLU(),
                                  nn.Linear(32, n_out))

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


# ----------------------------------------------------------------------------
# Baseline hien dai: DLinear (Zeng et al., AAAI 2023), PatchTST (Nie et al., ICLR 2023)
# Ca hai la mo hinh channel-independent: du bao cho tung bien roi tron lai bang
# mot lop tuyen tinh tren truc bien -> dau ra (B, H) giong cac model kia.
# ----------------------------------------------------------------------------

class WindDLinear(nn.Module):
    def __init__(self, n_features, n_out, seq_len=96, kernel=25):
        super().__init__()
        self.kernel = kernel
        self.lin_s = nn.Linear(seq_len, n_out)       # thanh phan mua vu
        self.lin_t = nn.Linear(seq_len, n_out)       # thanh phan xu huong
        self.mix = nn.Linear(n_features, 1)

    def forward(self, x):                            # (B, L, F)
        x = x.transpose(1, 2)                        # (B, F, L)
        pad = (self.kernel - 1) // 2
        xp = torch.cat([x[..., :1].expand(-1, -1, pad), x,
                        x[..., -1:].expand(-1, -1, self.kernel - 1 - pad)], dim=-1)
        trend = F.avg_pool1d(xp, self.kernel, stride=1)
        out = self.lin_s(x - trend) + self.lin_t(trend)   # (B, F, H)
        return self.mix(out.transpose(1, 2)).squeeze(-1)


class WindPatchTST(nn.Module):
    # shortcut: khong dung RevIN vi input da MinMax theo train; them RevIN neu PatchTST kem bat thuong
    def __init__(self, n_features, n_out, seq_len=96, patch_len=16, stride=8,
                 d_model=64, n_heads=4, n_layers=2, dim_feedforward=128, dropout=0.1):
        super().__init__()
        self.patch_len, self.stride = patch_len, stride
        n_patch = (seq_len - patch_len) // stride + 1
        self.embed = nn.Linear(patch_len, d_model)
        self.pos = nn.Parameter(torch.zeros(1, n_patch, d_model))
        layer = nn.TransformerEncoderLayer(d_model, n_heads, dim_feedforward,
                                           dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.head = nn.Linear(n_patch * d_model, n_out)
        self.mix = nn.Linear(n_features, 1)

    def forward(self, x):                            # (B, L, F)
        B, L, Fd = x.shape
        p = x.transpose(1, 2).unfold(-1, self.patch_len, self.stride)  # (B, F, P, patch)
        z = self.embed(p.reshape(B * Fd, -1, self.patch_len)) + self.pos
        z = self.encoder(z).reshape(B, Fd, -1)       # (B, F, P*d)
        out = self.head(z)                           # (B, F, H)
        return self.mix(out.transpose(1, 2)).squeeze(-1)


# ----------------------------------------------------------------------------

BUILDERS = {
    "LSTM": WindLSTM,
    "Transformer": WindTransformer,
    "Mamba": WindMamba,
    "PatchTST": WindPatchTST,
    "DLinear": WindDLinear,
}


def build(name, n_features, n_out, **kw):
    return BUILDERS[name](n_features, n_out, **kw)


def count_params(m):
    return sum(p.numel() for p in m.parameters() if p.requires_grad)


def param_groups(model, weight_decay):
    """AdamW khong duoc phat weight decay len A_log va D -- day la tham so
    dong hoc cua SSM, khong phai trong so tuyen tinh."""
    decay, no_decay = [], []
    for p in model.parameters():
        if not p.requires_grad:
            continue
        (no_decay if getattr(p, "_no_weight_decay", False) else decay).append(p)
    return [{"params": decay, "weight_decay": weight_decay},
            {"params": no_decay, "weight_decay": 0.0}]


# ----------------------------------------------------------------------------
# Tu kiem tra
# ----------------------------------------------------------------------------

def _self_test():
    torch.manual_seed(0)
    B, L, Fdim, H = 4, 96, 31, 3

    print("Tham so voi n_features={}, L={}, d_model=64, 2 lop:\n".format(Fdim, L))
    for name in BUILDERS:
        m = build(name, Fdim, H)
        y = m(torch.randn(B, L, Fdim))
        assert y.shape == (B, H), (name, y.shape)
        print("   {:<12} {:>8,} tham so   out {}".format(name, count_params(m), tuple(y.shape)))

    ff = build("Transformer", Fdim, H, dim_feedforward=2048)
    print("   {:<12} {:>8,} tham so   <- mac dinh PyTorch, loi cua code cu"
          .format("Transformer", count_params(ff)))

    print("\nDoi chieu selective scan (song song vs tuan tu):")
    blk = MambaBlock(64, scan="parallel").eval()
    x = torch.randn(2, L, blk.d_inner)
    with torch.no_grad():
        blk.scan = "parallel"
        yp = blk.ssm(x)
        blk.scan = "sequential"
        ys = blk.ssm(x)
    dev = (yp - ys).abs().max().item()
    rel = dev / ys.abs().max().item()
    print("   lech tuyet doi lon nhat = {:.3e}  (tuong doi {:.3e})".format(dev, rel))
    assert rel < 1e-4, "hai ban quet khong khop -- scan song song bi sai"
    print("   => hai ban quet khop nhau")

    print("\nKiem tra tinh nhan qua (buoc t khong duoc nhin thay t+1):")
    blk = MambaBlock(64, scan="parallel").eval()
    net = WindMamba(Fdim, H).eval()
    x1 = torch.randn(1, L, Fdim)
    x2 = x1.clone()
    x2[0, L // 2 + 1:] += 10.0            # doi toan bo phan TUONG LAI
    with torch.no_grad():
        h1 = net.embed(x1)
        h2 = net.embed(x2)
        for l1 in net.layers:
            h1, h2 = l1(h1), l1(h2)
    dev = (h1[0, :L // 2 + 1] - h2[0, :L // 2 + 1]).abs().max().item()
    print("   lech o phan qua khu = {:.3e}".format(dev))
    assert dev < 1e-5, "ro ri tuong lai -- khoi khong nhan qua"
    print("   => nhan qua, khong ro ri tuong lai")

    print("\nKiem tra A luon am (dieu kien on dinh cua SSM):")
    A = -torch.exp(blk.A_log)
    print("   A trong [{:.3f}, {:.3f}]".format(A.min().item(), A.max().item()))
    assert (A < 0).all()
    print("   => dat")


if __name__ == "__main__":
    _self_test()
