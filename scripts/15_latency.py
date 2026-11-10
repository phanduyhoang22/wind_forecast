"""
Do latency trung thuc (hop #1, #2) -- tach khoi job huan luyen.

  CPU: torch.set_num_threads co dinh (1 va 4), batch 1 va 256, median + p95
  GPU: neu co (kernel mamba-ssm neu da build), batch 1 va 256, co synchronize
  Mamba-step: che do hoi quy -- giu trang thai (conv + h) va chi cap nhat 1 buoc
              khi co quan sat 15 phut moi; day la cach trien khai dung cua SSM.
  RF: predict 1 mau voi n_jobs=1 (khong phai thong luong / mau nhu trong 07).

Trong so ngau nhien: latency khong phu thuoc gia tri trong so (tru RF -> train
RF that tren tram A voi cau hinh chot).

    py scripts/15_latency.py                  # CPU
    PYTHONPATH=/content/ss_build python scripts/15_latency.py   # Colab, them GPU
"""

import importlib.util
import json
import os
import time

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
NN = ("Mamba", "Transformer", "LSTM", "PatchTST", "DLinear")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class MambaStep:
    """Suy luan hoi quy cho WindMamba: moi buoc moi O(1), khong quet lai 96 buoc."""

    def __init__(self, net, batch):
        self.net = net
        self.state = []
        for blk in net.layers:
            conv = torch.zeros(batch, blk.d_inner, blk.conv1d.kernel_size[0] - 1)
            h = torch.zeros(batch, blk.d_inner, blk.d_state)
            self.state.append([conv, h])

    @torch.no_grad()
    def step(self, xt):                                   # xt: (B, F) -> (B, H)
        x = self.net.embed(xt)
        for blk, st in zip(self.net.layers, self.state):
            res = x
            xi, z = blk.in_proj(blk.norm(x)).chunk(2, dim=-1)
            win = torch.cat([st[0], xi.unsqueeze(-1)], dim=-1)         # (B, d_inner, d_conv)
            st[0] = win[..., 1:]
            xc = F.silu((win * blk.conv1d.weight.squeeze(1)).sum(-1) + blk.conv1d.bias)
            dt, Bm, Cm = torch.split(blk.x_proj(xc), [blk.dt_rank, blk.d_state, blk.d_state], dim=-1)
            dt = F.softplus(blk.dt_proj(dt))                              # (B, d_inner)
            A = -torch.exp(blk.A_log)
            st[1] = torch.exp(dt.unsqueeze(-1) * A) * st[1] + dt.unsqueeze(-1) * Bm.unsqueeze(1) * xc.unsqueeze(-1)
            y = (st[1] * Cm.unsqueeze(1)).sum(-1) + blk.D * xc
            x = res + blk.out_proj(y * F.silu(z))
        return self.net.head(self.net.norm(x))


def timeit(fn, n, sync=None):
    for _ in range(max(3, n // 10)):
        fn()
    ts = []
    for _ in range(n):
        if sync:
            sync()
        s = time.perf_counter()
        fn()
        if sync:
            sync()
        ts.append((time.perf_counter() - s) * 1000)
    return float(np.median(ts)), float(np.percentile(ts, 95))


def main():
    mo = _load("mo", "06_models.py")
    dp = _load("dp", "04_data_pipeline.py")
    tuned = json.load(open(os.path.join(RESULTS, "tuned.json")))
    Fd, H, L = 31, len(dp.HORIZONS), dp.SEQ_LEN
    torch.manual_seed(0)

    # Tu kiem tra: Mamba-step cho cung ket qua voi forward day du
    net = mo.build("Mamba", Fd, H).eval()
    x = torch.randn(2, L, Fd)
    stepper = MambaStep(net, 2)
    for t in range(L):
        out = stepper.step(x[:, t])
    with torch.no_grad():
        full = net(x)
    dev_ = (out - full).abs().max().item()
    assert dev_ < 1e-4, "Mamba-step lech forward day du: {}".format(dev_)
    print("Mamba-step khop forward day du (lech {:.1e})".format(dev_))

    rows = []
    for threads in (1, 4):
        torch.set_num_threads(threads)
        for name in NN:
            m = mo.build(name, Fd, H, **tuned.get(name, {})).eval()
            for b in (1, 256):
                xb = torch.randn(b, L, Fd)
                with torch.no_grad():
                    med, p95 = timeit(lambda: m(xb), 50 if b == 1 else 10)
                rows.append(dict(device="cpu", threads=threads, model=name, batch=b,
                                 ms_median=med, ms_p95=p95, ms_per_sample=med / b))
        st = MambaStep(mo.build("Mamba", Fd, H).eval(), 1)
        xt = torch.randn(1, Fd)
        med, p95 = timeit(lambda: st.step(xt), 200)
        rows.append(dict(device="cpu", threads=threads, model="Mamba-step", batch=1,
                         ms_median=med, ms_p95=p95, ms_per_sample=med))
        print("CPU {} luong: xong".format(threads), flush=True)

    # RF: train that tren tram A (cau hinh chot), predict 1 mau, n_jobs=1
    from sklearn.ensemble import RandomForestRegressor
    d = dp.load_site("A")
    rf = RandomForestRegressor(n_estimators=500, max_depth=tuned.get("RF", {}).get("max_depth", 16),
                               min_samples_split=5, min_samples_leaf=2, max_features="sqrt",
                               random_state=0, n_jobs=-1).fit(d.flat(d.idx_train), d.y[d.idx_train])
    rf.set_params(n_jobs=1)
    one = d.flat(d.idx_test[:1])
    med, p95 = timeit(lambda: rf.predict(one), 30)
    rows.append(dict(device="cpu", threads=1, model="RF", batch=1, ms_median=med, ms_p95=p95, ms_per_sample=med))

    if torch.cuda.is_available():
        print("kernel mamba-ssm:", mo._ss_cuda is not None)
        for name in NN:
            m = mo.build(name, Fd, H, **tuned.get(name, {})).cuda().eval()
            for b in (1, 256):
                xb = torch.randn(b, L, Fd, device="cuda")
                with torch.no_grad():
                    med, p95 = timeit(lambda: m(xb), 50, sync=torch.cuda.synchronize)
                rows.append(dict(device="cuda", threads=0, model=name, batch=b,
                                 ms_median=med, ms_p95=p95, ms_per_sample=med / b))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RESULTS, "latency.csv"), index=False)
    print(df.pivot_table(index=["device", "threads", "batch"], columns="model", values="ms_median")
          .to_string(float_format=lambda v: "%.3f" % v))


if __name__ == "__main__":
    main()
