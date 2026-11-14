"""
E9 few-shot (hop #3, #5): tram moi can bao nhieu du lieu tai cho de vuot persistence?

Voi moi tram dich t:
  - "finetune": khoi tao tu mo hinh LOSO chi-toc-do-gio (hoc o 3 tram kia,
    results/models_loso/losoW_<t>_<model>_<seed>.pt), fine-tune lr 1e-4
  - "scratch" : hoc tu dau, cung kien truc + cung du lieu (baseline bat buoc)
Du lieu dich: k tuan (k = 1, 2, 4) lay tu PHAN TRAIN cua t, o 2 cua so mua:
  "DB" ket thuc 2020-03-31 (gio mua Dong Bac), "TN" ket thuc 2020-07-01 (Tay Nam).
Val = val cua t (early stopping), test = test cua t. Khong dung test de chon gi.
Scaler cua t fit tren toan bo train cua t -> gia dinh co thong ke khi hau lich su
(ghi ro trong bai).

    py scripts/18_fewshot.py --sites A,B,C,D --models Mamba --seeds 3
"""

import argparse
import importlib.util
import json
import os
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
WINDOWS = {"DB": "2020-03-31 23:45", "TN": "2020-07-01 00:00"}
STEPS_PER_WEEK = 7 * 96


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="A,B,C,D")
    ap.add_argument("--models", default="Mamba")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--weeks", default="1,2,4")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--max-batches", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(RESULTS, "fewshot.csv"))
    args = ap.parse_args()

    import torch
    g = _load("g", "09_global_loso.py")
    dp, bm = g.dp, g.bm
    tuned = json.load(open(os.path.join(RESULTS, "tuned.json")))
    sites = [s.strip().upper() for s in args.sites.split(",")]
    data = {s: dp.load_site(s) for s in sites}

    done = set()
    if os.path.exists(args.out):
        prev = pd.read_csv(args.out)
        done = set(zip(prev.site, prev.model, prev.mode, prev.window, prev.weeks, prev.seed))

    for t in sites:
        d = g.Pooled({t: data[t]}, [t], [t], features="wind")   # chi toc do gio, nhu LOSO-W
        full_train = d.idx_train.copy()
        times = data[t].time
        for name in [m.strip() for m in args.models.split(",")]:
            cfg = dict(tuned.get(name, {}))
            for win, end in WINDOWS.items():
                end_i = int(np.searchsorted(times[full_train], pd.Timestamp(end)))
                for k in [int(x) for x in args.weeks.split(",")]:
                    sub = full_train[max(0, end_i - k * STEPS_PER_WEEK):end_i]
                    for seed in range(args.seeds):
                        for mode in ("finetune", "scratch"):
                            key = (t, name, mode, win, k, seed)
                            if key in done:
                                continue
                            init = None
                            if mode == "finetune":
                                f = os.path.join(RESULTS, "models_loso", "losoW_{}_{}_{}.pt".format(t, name, seed))
                                if not os.path.exists(f):
                                    print("thieu", f)
                                    continue
                                init = torch.load(f, map_location="cpu")
                            d.idx_train = sub
                            kw = dict(cfg)
                            if mode == "finetune":
                                kw["lr"] = 1e-4
                            t0 = time.time()
                            y_pred, info = bm.run_nn(d, seed, name, epochs=args.epochs, patience=args.patience,
                                                     batch_size=64, max_batches=args.max_batches,
                                                     init_state=init, **kw)
                            m = dp.metrics(d.y_raw[d.idx_test], y_pred)
                            rows = [dict(site=t, model=name, mode=mode, window=win, weeks=k, seed=seed,
                                         n_train=len(sub), horizon=h, **r.to_dict()) for h, r in m.iterrows()]
                            pd.DataFrame(rows).to_csv(args.out, mode="a" if os.path.exists(args.out) else "w",
                                                      header=not os.path.exists(args.out), index=False)
                            print("{} {} {:<8} {} {}w seed={}  {:.0f}s  1h RMSE={:.4f}".format(
                                t, name, mode, win, k, seed, time.time() - t0, m.loc["1h", "RMSE"]), flush=True)
        d.idx_train = full_train

    df = pd.read_csv(args.out)
    print("\nRMSE 1h trung binh (tram x seed):")
    print(df[df.horizon == "1h"].pivot_table(index=["window", "weeks"], columns=["model", "mode"],
                                             values="RMSE").round(3).to_string())


if __name__ == "__main__":
    main()
