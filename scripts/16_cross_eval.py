"""
Ma tran cham cheo giua cac tram (hop #5): tach "cung che do" voi "khac che do".

Mo hinh hoc tai tram nguon s (trong so E1 o results/models/<s>_<model>_<seed>.pt)
du bao tren tap test cua tram dich t. Dau vao cua t chuan hoa bang scaler train
cua chinh t (thong ke khi hau khong nhan -- giong LOSO), du doan doi ve m/s bang
scaler_y cua t. Duong cheo (s == t) = ket qua E1.

RF khong luu mo hinh -> huan luyen lai tren tram nguon (CPU, cau hinh tuned).

Khac LOSO: moi mo hinh chi hoc tu MOT tram. Phai ghi ro trong bai.

    py scripts/16_cross_eval.py --sites A,B,C,D,E,F,G,H --models Mamba,Transformer,RF --seeds 3
"""

import argparse
import importlib.util
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def predict_nn(mo, name, state, cfg, d, dev, batch=512):
    import torch
    m = mo.build(name, d.n_features, len(d.horizons), **cfg)
    m.load_state_dict(state)
    m.to(dev).eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(d.idx_test), batch):
            xb = torch.from_numpy(d.windows(d.idx_test[i:i + batch])).to(dev)
            out.append(m(xb).float().cpu().numpy())
    p = np.vstack(out)
    return d.scaler_y.inverse(p.reshape(-1, 1)).reshape(p.shape)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="A,B,C,D")
    ap.add_argument("--models", default="Mamba,Transformer,RF")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(RESULTS, "cross_eval.csv"))
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    import torch
    dp = _load("dp", "04_data_pipeline.py")
    mo = _load("mo", "06_models.py")
    bm = _load("bm", "07_run_benchmark.py")
    tuned = json.load(open(os.path.join(RESULTS, "tuned.json")))
    dev = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    sites = [s.strip().upper() for s in args.sites.split(",")]
    data = {s: dp.load_site(s) for s in sites}

    done = set()
    if os.path.exists(args.out):
        prev = pd.read_csv(args.out)
        done = set(zip(prev.source, prev.model, prev.seed))

    for name in [m.strip() for m in args.models.split(",")]:
        for src in sites:
            for seed in range(args.seeds):
                if (src, name, seed) in done:
                    continue
                rows = []
                if name == "RF":
                    from sklearn.ensemble import RandomForestRegressor
                    d = data[src]
                    rf = RandomForestRegressor(n_estimators=500, min_samples_split=5, min_samples_leaf=2,
                                               max_features="sqrt", random_state=seed, n_jobs=-1,
                                               **tuned.get("RF", {})).fit(d.flat(d.idx_train), d.y[d.idx_train])
                for tgt in sites:
                    t = data[tgt]
                    if name == "RF":
                        p = rf.predict(t.flat(t.idx_test))
                        yp = t.scaler_y.inverse(p.reshape(-1, 1)).reshape(p.shape)
                    else:
                        f = os.path.join(RESULTS, "models", "{}_{}_{}.pt".format(src, name, seed))
                        if not os.path.exists(f):
                            print("thieu", f)
                            break
                        yp = predict_nn(mo, name, torch.load(f, map_location="cpu"),
                                        tuned.get(name, {}), t, dev)
                    met = dp.metrics(t.y_raw[t.idx_test], yp)
                    for h, r in met.iterrows():
                        rows.append(dict(source=src, target=tgt, model=name, seed=seed, horizon=h,
                                         same_regime=dp.REGIME[src] == dp.REGIME[tgt], **r.to_dict()))
                if rows:
                    pd.DataFrame(rows).to_csv(args.out, mode="a" if os.path.exists(args.out) else "w",
                                              header=not os.path.exists(args.out), index=False)
                    print("{} {} seed={}: {}".format(name, src, seed, "  ".join(
                        "{}={:.3f}".format(r["target"], r["RMSE"]) for r in rows if r["horizon"] == "1h")),
                        flush=True)

    df = pd.read_csv(args.out)
    print("\nRMSE 1h (hang = tram nguon, cot = tram dich), trung binh seed:")
    for name, g in df[df.horizon == "1h"].groupby("model"):
        print("\n" + name)
        print(g.pivot_table(index="source", columns="target", values="RMSE").round(3).to_string())


if __name__ == "__main__":
    main()
