"""
Tuning nhe, cung ngan sach cho moi mo hinh (chot o hop #1, 09/11/2026).

Luoi CO DINH TRUOC, 1 seed, chi cham tren VAL (khong nhin test):
    mang no-ron : lr {3e-4, 1e-3} x dropout {0.1, 0.2}   (+ warmup 1 epoch, decay chi tren ma tran)
    PatchTST    : them revin {False, True}
    RF          : max_depth {12, 16, 24}
Tram tune: A (dat lien) va D (ngoai khoi) -- hai dau cua dai che do gio.
Chon cau hinh co val MSE (thang da chuan hoa) trung binh 2 tram nho nhat, ap chung cho ca 4 tram.

Ghi: results/tune.csv (moi lan thu), results/tuned.json (cau hinh chot, 07 doc file nay).

    py scripts/12_tune.py --models RF                                   # CPU
    py scripts/12_tune.py --models LSTM,Transformer,Mamba,PatchTST,DLinear   # GPU
"""

import argparse
import importlib.util
import itertools
import json
import os
import time

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def grid(model):
    if model == "RF":
        return [{"max_depth": d} for d in (12, 16, 24)]
    base = [{"lr": lr, "dropout": dr} for lr, dr in itertools.product((3e-4, 1e-3), (0.1, 0.2))]
    if model == "PatchTST":
        return [dict(c, revin=r) for c in base for r in (False, True)]
    if model == "DLinear":                       # khong co dropout -> chi luoi lr
        return [{"lr": lr} for lr in (3e-4, 1e-3)]
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="LSTM,Transformer,Mamba,PatchTST,DLinear")
    ap.add_argument("--sites", default="A,D")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--max-batches", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(RESULTS, "tune.csv"))
    args = ap.parse_args()

    bm = _load("bm", "07_run_benchmark.py")
    dp = bm.dp
    sites = [s.strip().upper() for s in args.sites.split(",")]
    data = {s: dp.load_site(s) for s in sites}
    models = [m.strip() for m in args.models.split(",")]

    done = set()
    if os.path.exists(args.out):
        prev = pd.read_csv(args.out)
        done = set(zip(prev.model, prev.config, prev.site))

    for name in models:
        for cfg in grid(name):
            key = json.dumps(cfg, sort_keys=True)
            for s in sites:
                tag = "{} {} {}".format(name, key, s)
                if (name, key, s) in done:
                    print(tag, "-> da co")
                    continue
                t0 = time.time()
                if name == "RF":
                    _, info = bm.run_rf(data[s], 0, **cfg)
                else:
                    _, info = bm.run_nn(data[s], 0, name, epochs=args.epochs, patience=args.patience,
                                        batch_size=args.batch_size, max_batches=args.max_batches, **cfg)
                row = dict(model=name, config=key, site=s, val_best=info["val_best"],
                           best_epoch=info["best_epoch"], train_s=info["train_s"])
                print("{}  val={:.6f}  ep={}  {:.0f}s".format(tag, row["val_best"], row["best_epoch"],
                                                            time.time() - t0), flush=True)
                pd.DataFrame([row]).to_csv(args.out, mode="a" if os.path.exists(args.out) else "w",
                                           header=not os.path.exists(args.out), index=False)

    # Chot: trung binh val qua cac tram, chi xet cau hinh da chay du moi tram
    df = pd.read_csv(args.out)
    g = df.groupby(["model", "config"]).agg(val=("val_best", "mean"), n=("site", "nunique"),
                                            ep=("best_epoch", "mean")).reset_index()
    g = g[g.n == len(sites)]
    path = os.path.join(os.path.dirname(args.out), "tuned.json")
    tuned = json.load(open(path)) if os.path.exists(path) else {}
    print("\nKet qua tuning (val MSE trung binh {} tram):".format(len(sites)))
    for m, sub in g.groupby("model"):
        sub = sub.sort_values("val")
        print(sub.to_string(index=False, float_format=lambda x: "%.6f" % x))
        tuned[m] = json.loads(sub.iloc[0].config)
    json.dump(tuned, open(path, "w"), indent=1)
    print("\nChot ->", path, tuned)


if __name__ == "__main__":
    main()
