"""
Vong lap benchmark: model x tram x seed -> results/runs.csv

Moi ket qua trong bai phai di thang tu file nay ra bang, khong qua buoc chep
tay. Code cu chi `print` roi nguoi chep lai -- va do chinh la cho so lieu
trong ban thao lech khoi so lieu notebook thuc su sinh ra.

Chay local (nhe, de thu):
    py scripts/07_run_benchmark.py --sites A --models Mamba --seeds 1 --epochs 2

Chay day du tren Colab:
    py scripts/07_run_benchmark.py --seeds 5
"""

import argparse
import importlib.util
import json
import os
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dp = _load("dp", "04_data_pipeline.py")


# ----------------------------------------------------------------------------

def run_rf(d, seed, n_estimators=500, max_depth=16, **_):
    from sklearn.ensemble import RandomForestRegressor

    # RF nhin dac trung tai buoc cuoi cua cua so -- CUNG bo chi so voi cac
    # model chuoi, nen cung tap test, khac voi code cu.
    Xtr, ytr = d.flat(d.idx_train), d.y[d.idx_train]
    Xte = d.flat(d.idx_test)

    m = RandomForestRegressor(
        n_estimators=n_estimators, max_depth=max_depth, min_samples_split=5,
        min_samples_leaf=2, max_features="sqrt", random_state=seed, n_jobs=-1)

    t0 = time.time()
    m.fit(Xtr, ytr)
    train_s = time.time() - t0

    t0 = time.time()
    pred = m.predict(Xte)
    lat_ms = (time.time() - t0) / len(Xte) * 1000

    y_pred = d.scaler_y.inverse(pred.reshape(-1, 1)).reshape(pred.shape)
    n_params = int(sum(e.tree_.node_count for e in m.estimators_))
    return y_pred, dict(train_s=train_s, latency_ms=lat_ms, params=n_params,
                        epochs=1, best_epoch=1)


def run_nn(d, seed, name, epochs=50, patience=10, batch_size=64, lr=1e-3,
           weight_decay=0.01, device=None, max_batches=0, save_path=None, **kw):
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset

    mo = _load("mo", "06_models.py")
    torch.manual_seed(seed)
    np.random.seed(seed)
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

    X = torch.from_numpy(d.X)
    Y = torch.from_numpy(d.y)
    L = d.seq_len

    class W(Dataset):
        def __init__(self, idx):
            self.idx = torch.from_numpy(idx)

        def __len__(self):
            return len(self.idx)

        def __getitem__(self, i):
            t = int(self.idx[i])
            return X[t - L + 1: t + 1], Y[t]

    pin = dev.type == "cuda"
    tr = DataLoader(W(d.idx_train), batch_size=batch_size, shuffle=True,
                    drop_last=True, pin_memory=pin)
    va = DataLoader(W(d.idx_val), batch_size=256, shuffle=False, pin_memory=pin)
    te = DataLoader(W(d.idx_test), batch_size=256, shuffle=False, pin_memory=pin)

    model = mo.build(name, d.n_features, len(d.horizons), **kw).to(dev)
    if dev.type == "cuda":
        # Selective scan la chuoi phep toan tung phan tu -> compile gop kernel, nhanh ~3.5x tren T4.
        # Khong doi toan hoc, khong doi state_dict; latency CPU van do tren ban eager.
        for blk in getattr(model, "layers", []):
            if hasattr(blk, "ssm"):
                blk.ssm = torch.compile(blk.ssm)
    opt = torch.optim.AdamW(mo.param_groups(model, weight_decay), lr=lr)
    sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, "min", patience=3, factor=0.5)
    lossf = nn.MSELoss()

    # Mixed precision: cac lop tuyen tinh chay fp16, rieng selective scan van
    # o fp32 (xem MambaBlock._ssm_fp32). Tren T4 nhanh khoang 2x.
    amp = dev.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=amp)

    best, best_ep, wait, state = float("inf"), 0, 0, None
    t0 = time.time()
    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        model.train()
        for bi, (xb, yb) in enumerate(tr):
            if max_batches and bi >= max_batches:   # chi dung khi chay thu
                break
            xb, yb = xb.to(dev, non_blocking=True), yb.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=amp):
                loss = lossf(model(xb), yb)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()

        model.eval()
        vl, n = 0.0, 0
        with torch.no_grad():
            for bi, (xb, yb) in enumerate(va):
                if max_batches and bi >= max_batches:
                    break
                xb, yb = xb.to(dev), yb.to(dev)
                with torch.amp.autocast("cuda", enabled=amp):
                    vl += lossf(model(xb), yb).item() * len(xb)
                n += len(xb)
        vl /= max(n, 1)
        sched.step(vl)

        if ep <= 3 or ep % 10 == 0:
            print("      ep {:02d}  val={:.5f}  {:.1f}s".format(ep, vl, time.time() - ep_t0),
                  flush=True)

        if vl < best - 1e-6:
            best, best_ep, wait = vl, ep, 0
            state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= patience:
                break
    train_s = time.time() - t0

    model.load_state_dict(state)
    model.eval()
    if save_path:                                   # 10_shap.py can trong so da train
        torch.save(state, save_path)

    # Do do tre tren CPU, batch 1 -- dieu kien trien khai bien
    cpu_model = mo.build(name, d.n_features, len(d.horizons), **kw)
    cpu_model.load_state_dict(state)
    cpu_model.eval()
    one = torch.from_numpy(d.X[d.idx_test[0] - L + 1: d.idx_test[0] + 1]).unsqueeze(0)
    with torch.no_grad():
        for _ in range(10):
            cpu_model(one)
        lat = []
        for _ in range(100):
            s = time.perf_counter()
            cpu_model(one)
            lat.append((time.perf_counter() - s) * 1000)

    preds = []
    with torch.no_grad():
        for xb, _ in te:
            with torch.amp.autocast("cuda", enabled=amp):
                preds.append(model(xb.to(dev)).float().cpu().numpy())
    p = np.vstack(preds)
    y_pred = d.scaler_y.inverse(p.reshape(-1, 1)).reshape(p.shape)

    return y_pred, dict(train_s=train_s, latency_ms=float(np.median(lat)),
                        params=mo.count_params(model), epochs=ep, best_epoch=best_ep)


# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="A,B,C,D")
    ap.add_argument("--models", default="RF,LSTM,Transformer,Mamba")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--data-dir", default=dp.DATA_DIR)
    ap.add_argument("--out", default=os.path.join(RESULTS, "runs.csv"))
    ap.add_argument("--device", default=None)
    ap.add_argument("--max-batches", type=int, default=0,
                    help="gioi han so batch/epoch -- CHI de chay thu, dat 0 khi chay that")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    mdir = os.path.join(os.path.dirname(args.out), "models")
    os.makedirs(mdir, exist_ok=True)
    sites = [s.strip().upper() for s in args.sites.split(",")]
    models = [m.strip() for m in args.models.split(",")]

    done = set()
    if os.path.exists(args.out):                       # cho phep chay tiep
        prev = pd.read_csv(args.out)
        done = set(zip(prev.site, prev.model, prev.seed))
        print("Da co {} luot chay truoc, se bo qua.\n".format(len(done) // len(dp.HORIZONS)))

    rows = []
    total = len(sites) * len(models) * args.seeds
    i = 0
    for site in sites:
        d = dp.load_site(site, args.data_dir)
        for name in models:
            for seed in range(args.seeds):
                i += 1
                tag = "[{}/{}] {} {} seed={}".format(i, total, site, name, seed)
                if (site, name, seed) in done:
                    print(tag, "-> da co, bo qua")
                    continue
                t0 = time.time()
                if name == "RF":
                    y_pred, info = run_rf(d, seed)
                else:
                    y_pred, info = run_nn(
                        d, seed, name, epochs=args.epochs, patience=args.patience,
                        batch_size=args.batch_size, device=args.device,
                        max_batches=args.max_batches,
                        save_path=os.path.join(mdir, "{}_{}_{}.pt".format(site, name, seed)))
                m = dp.metrics(d.y_raw[d.idx_test], y_pred)

                # Luu du doan tung mau -> 08 can cho kiem dinh Diebold-Mariano
                pdir = os.path.join(os.path.dirname(args.out), "preds")
                os.makedirs(pdir, exist_ok=True)
                np.savez_compressed(os.path.join(pdir, "{}_{}_{}.npz".format(site, name, seed)),
                                    y_pred=y_pred.astype(np.float32))

                for h, r in m.iterrows():
                    rows.append(dict(site=site, model=name, seed=seed, horizon=h,
                                     **r.to_dict(), **info))
                print("{}  {:.0f}s  ep={}  {:>8,}p  {:.2f}ms  |  {}".format(
                    tag, time.time() - t0, info["best_epoch"], info["params"],
                    info["latency_ms"],
                    "  ".join("{} RMSE={:.4f}".format(h, r.RMSE) for h, r in m.iterrows())))

                pd.DataFrame(rows).to_csv(
                    args.out, mode="a" if os.path.exists(args.out) else "w",
                    header=not os.path.exists(args.out), index=False)
                rows = []

    print("\nGhi vao {}".format(args.out))


if __name__ == "__main__":
    main()
