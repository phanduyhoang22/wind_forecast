"""
Tap test lui thoi gian 2016 (hop #5): bu cho tap test chinh thieu thang 1-3.

2016 nam ngoai hoan toan train/val (2017-2021) va khong dung cho tuning. Mo hinh
KHONG huan luyen lai: dung trong so E1 (results/models/), scaler fit tren train
2017-2020 cua chinh tram (giong 04). RF khong luu -> huan luyen lai tren train
cung cau hinh tuned roi cham 2016.

Chuan bi du lieu:
    py scripts/01_download_seawtk.py --years 2016 --raw-dir data_raw_2016
    py scripts/03_build_dataset.py --raw-dir data_raw_2016 --out-dir data_2016

Chay:
    py scripts/17_backtest_2016.py --sites A,B,C,D --models Mamba,Transformer,LSTM,DLinear,RF --seeds 5
"""

import argparse
import importlib.util
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")
SEASON = {1: "DB", 2: "DB", 3: "DB", 4: "chuyen mua", 5: "TN", 6: "TN", 7: "TN", 8: "TN", 9: "TN",
          10: "chuyen mua", 11: "dau DB", 12: "dau DB"}


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Backtest:
    """Giao dien giong SiteData (X, windows, flat, scaler_y, ...) cho du lieu 2016."""

    def __init__(self, dp, site, test_dir):
        ref = dp.load_site(site)                                 # scaler_y + danh sach dac trung
        df_tr = dp._read_site(site, dp.DATA_DIR)
        n_tr = int(len(df_tr) * dp.SPLIT[0])
        sx = dp.MinMax().fit(df_tr[ref.features].to_numpy(np.float32)[:n_tr])
        df = dp._read_site(site, test_dir)[ref.features]
        assert df.index.max() < df_tr.index.min(), "tap 2016 chong len giai doan train"
        ws = df[dp.TARGET].to_numpy(np.float32)
        N = len(df)
        self.X = sx.transform(df.to_numpy(np.float32)).astype(np.float32)
        self.y_raw = np.full((N, len(dp.HORIZONS)), np.nan, np.float32)
        for j, (k, _) in enumerate(dp.HORIZONS):
            self.y_raw[:N - k, j] = ws[k:]
        self.idx_test = np.arange(dp.SEQ_LEN - 1, N - dp.MAX_H, dtype=np.int64)
        self.scaler_y, self.features, self.time = ref.scaler_y, ref.features, df.index
        self.seq_len, self.horizons, self.ref = dp.SEQ_LEN, dp.HORIZONS, ref

    @property
    def n_features(self):
        return self.X.shape[1]

    def windows(self, idx):
        return self.X[idx[:, None] + np.arange(-self.seq_len + 1, 1)[None, :]]

    def flat(self, idx):
        return self.X[idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="A,B,C,D")
    ap.add_argument("--models", default="Mamba,Transformer,LSTM,DLinear,RF")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--test-dir", default=os.path.join(ROOT, "data_2016"))
    ap.add_argument("--out", default=os.path.join(RESULTS, "backtest_2016.csv"))
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    import torch
    dp = _load("dp", "04_data_pipeline.py")
    mo = _load("mo", "06_models.py")
    xe = _load("xe", "16_cross_eval.py")
    tuned = json.load(open(os.path.join(RESULTS, "tuned.json")))
    dev = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))

    rows = []
    for site in [s.strip().upper() for s in args.sites.split(",")]:
        d = Backtest(dp, site, args.test_dir)
        y = d.y_raw[d.idx_test]
        season = np.array([SEASON[m] for m in d.time[d.idx_test].month])
        now = d.scaler_y.inverse(d.X[d.idx_test, d.features.index(dp.TARGET)].reshape(-1, 1)).ravel()
        preds = {("persistence", 0): np.repeat(now[:, None], len(dp.HORIZONS), axis=1)}
        for name in [m.strip() for m in args.models.split(",")]:
            for seed in range(args.seeds):
                if name == "RF":
                    from sklearn.ensemble import RandomForestRegressor
                    r = d.ref
                    rf = RandomForestRegressor(n_estimators=500, min_samples_split=5, min_samples_leaf=2,
                                               max_features="sqrt", random_state=seed, n_jobs=-1,
                                               **tuned.get("RF", {})).fit(r.flat(r.idx_train), r.y[r.idx_train])
                    p = rf.predict(d.flat(d.idx_test))
                    preds[(name, seed)] = d.scaler_y.inverse(p.reshape(-1, 1)).reshape(p.shape)
                else:
                    f = os.path.join(RESULTS, "models", "{}_{}_{}.pt".format(site, name, seed))
                    if not os.path.exists(f):
                        continue
                    preds[(name, seed)] = xe.predict_nn(mo, name, torch.load(f, map_location="cpu"),
                                                        tuned.get(name, {}), d, dev)
        for (name, seed), p in preds.items():
            for j, (_, lab) in enumerate(dp.HORIZONS):
                e = y[:, j] - p[:, j]
                rows.append(dict(site=site, model=name, seed=seed, horizon=lab, season="ca nam",
                                 RMSE=float(np.sqrt(np.mean(e ** 2)))))
                for s in np.unique(season):
                    m = season == s
                    rows.append(dict(site=site, model=name, seed=seed, horizon=lab, season=s,
                                     RMSE=float(np.sqrt(np.mean(e[m] ** 2)))))
        print(site, "xong", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    t = df.groupby(["season", "horizon", "model"]).RMSE.mean().unstack("model")
    print("\nRMSE 2016 (trung binh tram x seed):")
    print(t.round(3).to_string())


if __name__ == "__main__":
    main()
