"""
Hop dong du lieu DUNG CHUNG cho ca 4 model.

Ly do ton tai: trong code cu, moi notebook tu doc du lieu, tu cat cua so,
tu chia tap. Ket qua la LSTM dung seq_len=24 con Mamba/Transformer dung 12;
Mamba bo cot wind_speed con hai model kia giu; RF khong cat cua so. Bon model
cham diem tren bon tap test khac nhau -> bang so sanh vo nghia.

File nay lam cho dieu do KHONG THE xay ra nua: moi model deu goi cung mot ham
va nhan ve cung mot bo chi so.

Chay truc tiep de in tom tat split + baseline persistence:
    py scripts/04_data_pipeline.py
"""

import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data_v2")
RESULTS_DIR = os.path.join(ROOT, "results")

# --- Hop dong: moi con so duoi day ap dung cho CA BON model ---
SEQ_LEN = 96                       # 96 buoc x 15 phut = 24 gio nhin lai
HORIZONS = [(4, "1h"), (12, "3h"), (24, "6h")]
MAX_H = max(k for k, _ in HORIZONS)
TARGET = "wind_speed"
SPLIT = (0.70, 0.15)               # train, val; phan con lai la test

SITES = {
    "A": "Tram_A_DatLien",
    "B": "Tram_B_VenBien",
    "C": "Tram_C_DoiNui",
    "D": "Tram_D_NgoaiKhoi",
    # Hop #5: 1 tram moi che do, qua cong kiem tra (xem data_v2/PROVENANCE.md)
    "E": "Tram_E_DatLien",
    "F": "Tram_F_VenBien",
    "G": "Tram_G_DoiNui",
    "H": "Tram_H_NgoaiKhoi",
}

# Che do gio cua moi tram (16_cross_eval: cung vs khac che do). E-H them o hop #5,
# chi dua vao SITES sau khi qua cong kiem tra du lieu.
REGIME = {"A": "Inland", "B": "Coastal", "C": "Complex", "D": "Offshore",
          "E": "Inland", "F": "Coastal", "G": "Complex", "H": "Offshore"}


class MinMax:
    """MinMaxScaler toi gian, fit CHI tren train. Tu viet de khong phai keo
    theo sklearn vao code model, va de ro rang rang khong co gi fit len test."""

    def __init__(self, lo=None, hi=None):
        self.lo, self.hi = lo, hi

    def fit(self, a):
        self.lo = a.min(axis=0)
        self.hi = a.max(axis=0)
        span = self.hi - self.lo
        span[span == 0] = 1.0          # cot hang so -> tranh chia 0
        self.span = span
        return self

    def transform(self, a):
        return (a - self.lo) / self.span

    def inverse(self, a):
        return a * self.span + self.lo


class SiteData:
    """Toan bo thu mot model can cho mot tram.

    X      : (N, F) float32, da chuan hoa, chua cat cua so
    y      : (N, H) float32, da chuan hoa; y[t] la nhan cho cua so KET THUC tai t
    y_raw  : (N, H) float32, don vi m/s, dung de cham diem
    idx_*  : chi so t hop le cua tung tap. Cua so la X[t-SEQ_LEN+1 : t+1]
    """

    def __init__(self, site, X, y, y_raw, idx_tr, idx_va, idx_te,
                 features, scaler_y, time_index):
        self.site = site
        self.X, self.y, self.y_raw = X, y, y_raw
        self.idx_train, self.idx_val, self.idx_test = idx_tr, idx_va, idx_te
        self.features = features
        self.scaler_y = scaler_y
        self.time = time_index
        self.seq_len = SEQ_LEN
        self.horizons = HORIZONS

    @property
    def n_features(self):
        return self.X.shape[1]

    def window(self, t):
        """Mot cua so dau vao, ket thuc (bao gom) tai buoc t."""
        return self.X[t - SEQ_LEN + 1: t + 1]

    def windows(self, idx):
        """Nhieu cua so -> (len(idx), SEQ_LEN, F). Chi materialize khi goi."""
        off = np.arange(-SEQ_LEN + 1, 1)
        return self.X[idx[:, None] + off[None, :]]

    def flat(self, idx):
        """Goc nhin cho Random Forest: dac trung tai buoc cuoi cua cua so.
        Dung DUNG bo chi so idx nhu cac model chuoi -> cung tap test."""
        return self.X[idx]

    def __repr__(self):
        return ("SiteData({} | {} dac trung | train {} / val {} / test {})"
                .format(self.site, self.n_features, len(self.idx_train),
                        len(self.idx_val), len(self.idx_test)))


def _valid_idx(start, stop):
    """Chi so t sao cho ca cua so [t-L+1, t] lan nhan t+MAX_H deu nam gon
    trong doan [start, stop). Nho vay khong cua so nao vat qua ranh gioi
    train/val/test -- day la 'purged split', thu ma code cu khong co: o do
    mot cua so train co the chua dung nhung hang la nhan cua mau val."""
    lo = start + SEQ_LEN - 1
    hi = stop - MAX_H
    return np.arange(lo, hi, dtype=np.int64) if hi > lo else np.empty(0, np.int64)


def _read_site(site, data_dir):
    """Doc .npz truoc (nhe hon 5x, nhanh hon 4x -- dung tren Colab/Drive),
    khong co thi doc .csv. Ca hai cho ra ket qua y het nhau."""
    npz = os.path.join(data_dir, SITES[site] + "_15min.npz")
    if os.path.exists(npz):
        z = np.load(npz, allow_pickle=False)
        return pd.DataFrame(z["X"], columns=[str(c) for c in z["cols"]],
                            index=pd.to_datetime(z["time"]))
    csv = os.path.join(data_dir, SITES[site] + "_15min.csv")
    if os.path.exists(csv):
        return pd.read_csv(csv, parse_dates=["time"]).set_index("time")
    raise FileNotFoundError("Khong thay {} (.npz hoac .csv)".format(SITES[site]))


def load_site(site, data_dir=DATA_DIR):
    df = _read_site(site, data_dir)
    if df.isna().any().any():
        raise ValueError("{} con NaN".format(site))

    features = [c for c in df.columns]          # gom ca wind_speed lam dac trung
    Xr = df[features].to_numpy(np.float32)
    ws = df[TARGET].to_numpy(np.float32)

    N = len(df)
    n_tr = int(N * SPLIT[0])
    n_va = int(N * (SPLIT[0] + SPLIT[1]))

    # Nhan: y_raw[t, j] = toc do gio tai t + horizon_j
    y_raw = np.full((N, len(HORIZONS)), np.nan, np.float32)
    for j, (k, _) in enumerate(HORIZONS):
        y_raw[:N - k, j] = ws[k:]

    # Chuan hoa: fit CHI tren hang train
    sx = MinMax().fit(Xr[:n_tr])
    sy = MinMax().fit(ws[:n_tr].reshape(-1, 1))
    X = sx.transform(Xr).astype(np.float32)
    y = sy.transform(y_raw.reshape(-1, 1)).reshape(y_raw.shape).astype(np.float32)

    return SiteData(
        site, X, y, y_raw,
        _valid_idx(0, n_tr), _valid_idx(n_tr, n_va), _valid_idx(n_va, N),
        features, sy, df.index,
    )


def metrics(y_true, y_pred):
    """RMSE / MAE / R2 cho tung horizon. Nhan vao (n, H) don vi m/s."""
    out = []
    for j, (_, lab) in enumerate(HORIZONS):
        t, p = y_true[:, j], y_pred[:, j]
        rmse = float(np.sqrt(np.mean((t - p) ** 2)))
        mae = float(np.mean(np.abs(t - p)))
        r2 = float(1 - np.sum((t - p) ** 2) / np.sum((t - t.mean()) ** 2))
        out.append({"horizon": lab, "RMSE": rmse, "MAE": mae, "R2": r2})
    return pd.DataFrame(out).set_index("horizon")


def persistence(d, idx):
    """Baseline: y_hat(t+h) = ws(t). Muc san moi model phai vuot.
    Chay tren DUNG tap chi so idx -> so sanh duoc truc tiep."""
    ws_col = d.features.index(TARGET)
    now = d.scaler_y.inverse(d.X[idx, ws_col].reshape(-1, 1)).ravel()
    return metrics(d.y_raw[idx], np.repeat(now[:, None], len(HORIZONS), axis=1))


def climatology(d, idx_fit, idx):
    """Baseline yeu hon: luon doan trung binh cua tap train."""
    ws_col = d.features.index(TARGET)
    mu = d.scaler_y.inverse(d.X[idx_fit, ws_col].reshape(-1, 1)).mean()
    return metrics(d.y_raw[idx], np.full((len(idx), len(HORIZONS)), mu, np.float32))


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print("Hop dong chung: SEQ_LEN={} ({} gio nhin lai) | horizons={} | split={}"
          .format(SEQ_LEN, SEQ_LEN / 4, [l for _, l in HORIZONS], SPLIT))
    print()

    rows = []
    for s in SITES:
        d = load_site(s)
        span = lambda i: "{} -> {}".format(d.time[i[0]].date(), d.time[i[-1]].date())
        print("=" * 74)
        print(d)
        print("   train {}   val {}   test {}"
              .format(span(d.idx_train), span(d.idx_val), span(d.idx_test)))

        for name, m in (("persistence", persistence(d, d.idx_test)),
                        ("climatology", climatology(d, d.idx_train, d.idx_test))):
            print("\n   {} tren tap test:".format(name))
            print("      " + m.to_string(float_format=lambda x: "%.4f" % x)
                  .replace("\n", "\n      "))
            for h, r in m.iterrows():
                rows.append(dict(site=s, model=name, horizon=h, **r.to_dict()))
        print()

    df = pd.DataFrame(rows)
    out = os.path.join(RESULTS_DIR, "baselines.csv")
    df.to_csv(out, index=False)
    print("=" * 74)
    print("Ghi baseline vao {}".format(out))
    print()
    print("Persistence R2 theo tram x horizon (muc san):")
    print(df[df.model == "persistence"]
          .pivot(index="site", columns="horizon", values="R2")[["1h", "3h", "6h"]]
          .to_string(float_format=lambda x: "%.4f" % x))


if __name__ == "__main__":
    main()
