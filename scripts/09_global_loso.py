"""
Tong quat hoa giua cac vung: Global pooled va Leave-One-Site-Out (LOSO).

  global : 1 model hoc tren train cua CA 4 tram, cham tren test tung tram
  loso   : 4 fold; hoc tren train cua 3 tram (val cua 3 tram do de early stop),
           cham tren test tram con lai
           (khong fine-tune, khong thay mot nhan nao cua tram bi giu lai)

Ca hai KHONG dung site ID: model khong biet mau den tu tram nao, nen khoang
cach LOSO - global la chi phi chuyen giao thuan tuy.

Chuan hoa: moi tram dung MinMax fit tren doan train cua chinh no (04). Voi
tram bi giu lai, dieu nay chi dung thong ke khi hau (min/max toc do gio lich su),
khong dung nhan cua giai doan test -- tuong duong mot tram moi co du lieu NWP/
reanalysis lich su nhung chua co mo hinh.

Dung lai nguyen run_nn cua 07: lop Pooled gia lap giao dien SiteData.

    py scripts/09_global_loso.py --models Mamba,LSTM --seeds 3
    py scripts/09_global_loso.py --models Mamba --seeds 1 --epochs 1 --max-batches 3   # chay thu
"""

import argparse
import importlib.util
import os
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dp = _load("dp", "04_data_pipeline.py")
bm = _load("bm", "07_run_benchmark.py")


class RowScaler:
    """Dao chuan hoa theo tung dong test -- moi dong thuoc mot tram khac nhau.
    run_nn goi inverse(p.reshape(-1, 1)) dung mot lan tren du doan test."""

    def __init__(self, lo, span):
        self.lo, self.span = lo, span

    def inverse(self, a):
        return a * self.span + self.lo


class Pooled:
    """Ghep nhieu SiteData thanh mot khoi. Chi so cua moi tram duoc cong offset
    nen cua so khong bao gio vat qua ranh gioi giua hai tram."""

    def __init__(self, sites, train_sites, test_sites):
        ds = {s: sites[s] for s in sites}
        order = list(ds)
        f0 = ds[order[0]].features
        assert all(ds[s].features == f0 for s in order), "dac trung cac tram khong cung thu tu"
        off, n = {}, 0
        for s in order:
            off[s] = n
            n += len(ds[s].X)
        self.X = np.vstack([ds[s].X for s in order])
        self.y = np.vstack([ds[s].y for s in order])
        self.y_raw = np.vstack([ds[s].y_raw for s in order])

        self.idx_train = np.concatenate([ds[s].idx_train + off[s] for s in train_sites])
        self.idx_val = np.concatenate([ds[s].idx_val + off[s] for s in train_sites])
        self.idx_test = np.concatenate([ds[s].idx_test + off[s] for s in test_sites])
        self.test_site = np.concatenate([[s] * len(ds[s].idx_test) for s in test_sites])

        H = len(dp.HORIZONS)
        lo = np.concatenate([np.full(len(ds[s].idx_test) * H, ds[s].scaler_y.lo[0]) for s in test_sites])
        sp = np.concatenate([np.full(len(ds[s].idx_test) * H, ds[s].scaler_y.span[0]) for s in test_sites])
        self.scaler_y = RowScaler(lo.reshape(-1, 1).astype(np.float32), sp.reshape(-1, 1).astype(np.float32))
        self.seq_len = dp.SEQ_LEN
        self.horizons = dp.HORIZONS
        self.features = f0

    @property
    def n_features(self):
        return self.X.shape[1]


def folds(site_list):
    yield "global", "ALL", site_list, site_list
    for s in site_list:
        yield "loso", s, [x for x in site_list if x != s], [s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="Mamba")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--data-dir", default=dp.DATA_DIR)
    ap.add_argument("--out", default=os.path.join(RESULTS, "loso.csv"))
    ap.add_argument("--device", default=None)
    ap.add_argument("--max-batches", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    pdir = os.path.join(os.path.dirname(args.out), "preds_loso")
    os.makedirs(pdir, exist_ok=True)
    site_list = list(dp.SITES)
    sites = {s: dp.load_site(s, args.data_dir) for s in site_list}
    models = [m.strip() for m in args.models.split(",")]

    done = set()
    if os.path.exists(args.out):
        prev = pd.read_csv(args.out)
        done = set(zip(prev.strategy, prev.fold, prev.model, prev.seed))

    plan = [(st, fold, tr, te, m, seed) for st, fold, tr, te in folds(site_list)
            for m in models for seed in range(args.seeds)]
    for i, (st, fold, tr, te, name, seed) in enumerate(plan, 1):
        tag = "[{}/{}] {} fold={} {} seed={}".format(i, len(plan), st, fold, name, seed)
        if (st, fold, name, seed) in done:
            print(tag, "-> da co, bo qua")
            continue
        d = Pooled(sites, tr, te)
        t0 = time.time()
        y_pred, info = bm.run_nn(d, seed, name, epochs=args.epochs, patience=args.patience,
                                 batch_size=args.batch_size, device=args.device,
                                 max_batches=args.max_batches)
        rows = []
        for s in te:
            sel = d.test_site == s
            m = dp.metrics(d.y_raw[d.idx_test][sel], y_pred[sel])
            np.savez_compressed(os.path.join(pdir, "{}_{}_{}_{}.npz".format(st, s, name, seed)),
                                y_pred=y_pred[sel].astype(np.float32))
            for h, r in m.iterrows():
                rows.append(dict(strategy=st, fold=fold, test_site=s, model=name, seed=seed,
                                 horizon=h, **r.to_dict(), **info))
        out = pd.DataFrame(rows)
        print("{}  {:.0f}s  ep={}  |  {}".format(
            tag, time.time() - t0, info["best_epoch"],
            "  ".join("{}:{} RMSE={:.4f}".format(r.test_site, r.horizon, r.RMSE)
                      for r in out.itertuples() if r.horizon == "1h")), flush=True)
        out.to_csv(args.out, mode="a" if os.path.exists(args.out) else "w",
                   header=not os.path.exists(args.out), index=False)

    print("\nGhi vao", args.out)


if __name__ == "__main__":
    main()
