"""
T21 (hop M19, M20): LOSO-W 8 fold phu thuoc bao nhieu vao MinMax fit tren train cua CHINH tram dich?

Trong 09 tram dich dung scaler cua train cua no (04_data_pipeline.py:180-181) -> mo hinh "zero-shot"
van thay min/max lich su cua tram dich (L09). File nay danh gia lai cung mo hinh, chi doi scaler cua tram dich:
  S0     scaler hien tai (fit tren train cua tram dich) = tai lap R21 (Mamba) / R16 (RF)
  S1     (chinh) sx/sy fit tren doan train GOP cua 7 tram nguon cua fold -> khong dung du lieu tram dich
  S2_DB, S2_TN (phu) sx/sy fit tren cua so k = 4 tuan cua tram dich, dung cua so cua 18_fewshot.py
Mamba-W: chi suy luan tu results/models_loso/losoW8_<fold>_Mamba_<seed>.pt (khong train lai).
RF-W (do sau 16): fit lai tren CPU (khong luu mo hinh), cung du lieu nguon nhu 09 -> cung mo hinh voi moi bien the.
Them (M20): S0/S1 tren val cua 7 tram nguon (S1 = scaler S1 cua fold) -> mean |delta skill| cho nguong RevIN (T27).

    py scripts/27_loso_scaler.py --models Mamba --seeds 3                       (Colab T4)
    py scripts/27_loso_scaler.py --models RF --seeds 3                          (CPU, mot job mot luc)
    py scripts/27_loso_scaler.py --stats                                        -> results/loso8_scaler_stats.csv
    py scripts/27_loso_scaler.py --selftest
    py scripts/27_loso_scaler.py --folds A --seeds 1 --max-batches 2 --random-init --out <scratch>/s.csv   (chay thu CPU)
"""

import argparse
import copy
import importlib.util
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
VARIANTS = ["S0", "S1", "S2_DB", "S2_TN"]
K_WEEKS = 4                 # hop dong T21: k = 4 tuan
TOL = 1e-4                  # S0 phai tai lap R21 trong 1e-4 m/s
TRIGGER_PP = 2.0            # M20: nguong RevIN, mean |delta skill| tren val tram nguon


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


g = _load("g", "09_global_loso.py")
dp, bm = g.dp, g.bm
fs = _load("fs", "18_fewshot.py")           # WINDOWS, STEPS_PER_WEEK
ts = _load("ts", "22_transfer_stats.py")    # compare (Wilcoxon chinh xac + Holm), check
SITES, SEEDS, HORIZONS = ts.SITES, ts.SEEDS, ts.HORIZONS


def load_all(data_dir):
    """SiteData (scaler S0) + du lieu tho chua chuan hoa cua 8 tram."""
    sites = {s: dp.load_site(s, data_dir) for s in SITES}
    raw = {s: dp._read_site(s, data_dir)[sites[s].features].to_numpy(np.float32) for s in SITES}
    return sites, raw


def fit_rows(variant, target, sites):
    """Hang (theo tung tram) dung de fit scaler cua tram dich. QA kiem tra o day: S1 khong co tram dich."""
    n_tr = {s: int(len(sites[s].X) * dp.SPLIT[0]) for s in sites}     # nhu 04: train = hang [:n_tr]
    if variant == "S0":
        return {target: np.arange(n_tr[target])}
    if variant == "S1":
        return {s: np.arange(n_tr[s]) for s in sites if s != target}
    # S2: cung cach cat cua so voi 18_fewshot.py (end_i theo thoi gian tren idx_train cua tram dich)
    tr = sites[target].idx_train
    end_i = int(np.searchsorted(sites[target].time[tr], pd.Timestamp(fs.WINDOWS[variant[3:]]), side="right"))
    return {target: tr[max(0, end_i - K_WEEKS * fs.STEPS_PER_WEEK):end_i]}


def fit_scalers(raw, rows, wcol):
    a = np.vstack([raw[s][r] for s, r in rows.items()])
    return dp.MinMax().fit(a), dp.MinMax().fit(a[:, wcol:wcol + 1])


def rescale(d, Xr, sx, sy):
    """SiteData moi cua cung tram, chuan hoa bang sx/sy khac (giong 04_data_pipeline.py:182-183)."""
    X = sx.transform(Xr).astype(np.float32)
    y = sy.transform(d.y_raw.reshape(-1, 1)).reshape(d.y_raw.shape).astype(np.float32)
    return dp.SiteData(d.site, X, y, d.y_raw, d.idx_train, d.idx_val, d.idx_test, d.features, sy, d.time)


def as_val(d):
    """Ban sao nong, idx_test := idx_val -> Pooled cham val cua tram nguon nhu mot khoi 'test'."""
    d = copy.copy(d)
    d.idx_test = d.idx_val
    return d


def build_fold(fold, sites, raw, nmax=0):
    """Mot Pooled cho ca fold: train = 7 nguon (S0, thu tu nhu 09 -> RF giong het R16),
    khoi cham: tram dich x 4 bien the (test) + 7 nguon x {S0, S1} (val)."""
    sources = [s for s in SITES if s != fold]
    wcol = sites[fold].features.index(dp.TARGET)
    blocks = {s: as_val(sites[s]) for s in sources}
    meta = {s: ("S0", "val", s, sites[s].scaler_y) for s in sources}     # khoa -> (bien the, tap, tram, sy)
    sc = {}
    for v in VARIANTS:
        sc[v] = fit_scalers(raw, fit_rows(v, fold, sites), wcol)
        blocks[fold + "|" + v] = rescale(sites[fold], raw[fold], *sc[v])
        meta[fold + "|" + v] = (v, "test", fold, sc[v][1])
    for s in sources:
        blocks[s + "|S1"] = as_val(rescale(sites[s], raw[s], *sc["S1"]))
        meta[s + "|S1"] = ("S1", "val", s, sc["S1"][1])
    if nmax:                                         # chay thu: cat ngan moi tap chi so
        for k, b in blocks.items():
            b = blocks[k] = copy.copy(b)
            b.idx_train, b.idx_val, b.idx_test = b.idx_train[:nmax], b.idx_val[:nmax], b.idx_test[:nmax]
    keys = [fold + "|" + v for v in VARIANTS] + sources + [s + "|S1" for s in sources]
    return g.Pooled(blocks, sources, keys, features="wind"), meta, keys


def predict_nn(d, keys, state, cfg, device=None):
    """Suy luan nhu phan test cua run_nn (07): batch 256 theo thu tu, autocast fp16 tren cuda.
    Moi khoi bat dau batch moi -> khoi S0 cung cach chia batch voi R21."""
    import torch
    mo = bm._load("mo", "06_models.py")
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = mo.build("Mamba", d.n_features, len(d.horizons), **cfg)
    model.load_state_dict(state)
    model = model.to(dev).eval()
    if dev.type == "cuda" and mo._ss_cuda is None:   # nhu run_nn khi khong co kernel
        for blk in getattr(model, "layers", []):
            if hasattr(blk, "ssm"):
                blk.ssm = torch.compile(blk.ssm)
    amp = dev.type == "cuda"
    X, off = torch.from_numpy(d.X), torch.arange(-d.seq_len + 1, 1)
    preds = []
    with torch.no_grad():
        for k in keys:
            seg = torch.from_numpy(d.idx_test[d.test_site == k])
            for i in range(0, len(seg), 256):
                xb = X[seg[i:i + 256, None] + off]
                with torch.amp.autocast("cuda", enabled=amp):
                    preds.append(model(xb.to(dev)).float().cpu().numpy())
    p = np.vstack(preds)
    return d.scaler_y.inverse(p.reshape(-1, 1)).reshape(p.shape)


def reference():
    """R21 (Mamba-W LOSO) + R16 (RF-W d16 LOSO): RMSE goc cho kiem tra tai lap S0."""
    r = pd.concat([pd.read_csv(os.path.join(RESULTS, f)) for f in ("loso8_wind.csv", "loso8_rf_wind.csv")])
    return r[r.strategy == "losoW"][["fold", "model", "seed", "horizon", "RMSE"]]


def run(args):
    if (args.max_batches or args.random_init) and \
            os.path.abspath(args.out).startswith(os.path.abspath(RESULTS) + os.sep):
        sys.exit("chay thu (--max-batches/--random-init) khong duoc ghi vao results/")
    import torch
    cfg = {"Mamba": json.load(open(os.path.join(RESULTS, "tuned.json")))["Mamba"],
           "RF": json.load(open(os.path.join(RESULTS, "tuned_rf_d16.json")))["RF"]}   # RF-W do sau 16 (R16)
    sites, raw = load_all(args.data_dir)
    ref = reference().set_index(["fold", "model", "seed", "horizon"]).RMSE
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    done = set()
    if os.path.exists(args.out):
        prev = pd.read_csv(args.out)
        done = set(zip(prev.fold, prev.model, prev.seed))
    models = [m.strip() for m in args.models.split(",")]
    for fold in [f.strip().upper() for f in args.folds.split(",")]:
        d = None
        for name in models:
            for seed in range(args.seeds):
                tag = "fold={} {} seed={}".format(fold, name, seed)
                if (fold, name, seed) in done:
                    print(tag, "-> da co, bo qua")
                    continue
                if d is None:                        # ghep mot lan moi fold
                    d, meta, keys = build_fold(fold, sites, raw, args.max_batches * 256)
                t0 = time.time()
                if name == "RF":
                    y_pred, _ = bm.run_rf(d, seed, **cfg["RF"])
                else:
                    f = os.path.join(args.models_dir, "losoW8_{}_{}_{}.pt".format(fold, name, seed))
                    if os.path.exists(f):
                        state = torch.load(f, map_location="cpu")
                    elif args.random_init:           # chi de chay thu khi khong co checkpoint
                        torch.manual_seed(seed)
                        state = bm._load("mo", "06_models.py").build(name, d.n_features, len(d.horizons),
                                                                      **cfg[name]).state_dict()
                    else:
                        print("thieu", f)
                        continue
                    y_pred = predict_nn(d, keys, state, cfg[name], args.device)
                rows = []
                for k in keys:
                    v, split, s, sy = meta[k]
                    sel = d.test_site == k
                    for h, r in dp.metrics(d.y_raw[d.idx_test][sel], y_pred[sel]).iterrows():
                        rows.append(dict(fold=fold, model=name, seed=seed, variant=v, split=split, site=s,
                                         horizon=h, **r.to_dict(), n=int(sel.sum()), ws_lo=float(sy.lo[0]),
                                         ws_hi=float(sy.hi[0]), sec=time.time() - t0))
                out = pd.DataFrame(rows)
                out.to_csv(args.out, mode="a" if os.path.exists(args.out) else "w",
                           header=not os.path.exists(args.out), index=False)
                s0 = out[(out.variant == "S0") & (out.split == "test")].set_index("horizon").RMSE
                diff = np.max([abs(s0[h] - ref.get((fold, name, seed, h), np.nan)) for h in HORIZONS])   # thieu ref -> nan -> dung
                t = out[out.split == "test"].pivot(index="variant", columns="horizon", values="RMSE")
                print("{}  {:.0f}s  S0-R21 max|d|={:.2e}  1h RMSE {}".format(
                    tag, time.time() - t0, diff, "  ".join("{}={:.4f}".format(v, t.loc[v, "1h"]) for v in VARIANTS)),
                    flush=True)
                if not args.max_batches and not args.random_init and not diff <= TOL:
                    sys.exit("DUNG: S0 khong tai lap R21/R16 ({} > {}), khong ket luan S1/S2".format(diff, TOL))
    print("\nGhi vao", args.out)


def analyze(runs, ref, pers_test, pers_val):
    """-> (bang thong ke dai, tai lap S0 dat?). pers_*: Series RMSE persistence theo (site, horizon)."""
    out = []
    m = runs[(runs.variant == "S0") & (runs.split == "test")].merge(
        ref, on=["fold", "model", "seed", "horizon"], how="left", suffixes=("", "_ref"))
    if m.RMSE_ref.isna().any():
        raise ValueError("S0 khong co dong tuong ung trong R21/R16")
    m["d"] = (m.RMSE - m.RMSE_ref).abs()
    for (name, h), x in m.groupby(["model", "horizon"]):
        out.append(dict(section="repro", model=name, horizon=h, n=len(x), value=x.d.max(), ok=bool(x.d.max() <= TOL)))
    ok = all(r["ok"] for r in out)
    if not ok:                                       # hop dong: khong ket luan S1/S2
        return pd.DataFrame(out), False
    pt = pers_test.unstack()[HORIZONS]
    for name in sorted(set(runs.model)):
        te = runs[(runs.model == name) & (runs.split == "test")]
        med = {}
        for v in VARIANTS:
            x = te[te.variant == v]
            ts.check(x, ["site", "seed", "horizon"], [SITES, SEEDS, HORIZONS], "{} {}".format(name, v))
            med[v] = x.groupby(["site", "horizon"]).RMSE.median().unstack()[HORIZONS]
            out += ts.compare(med[v], pt.loc[med[v].index]).assign(section="test", model=name, variant=v,
                                                                   ref="persistence").to_dict("records")
            for s in SITES:
                for h in HORIZONS:
                    out.append(dict(section="site", model=name, variant=v, site=s, horizon=h,
                                    RMSE=med[v].loc[s, h], skill=1 - med[v].loc[s, h] / pt.loc[s, h],
                                    d_rmse_vs_S0=med[v].loc[s, h] - med["S0"].loc[s, h]))
        va = runs[(runs.model == name) & (runs.split == "val")]
        if len(va) != 2 * 56 * len(SEEDS) * len(HORIZONS) or (va.site == va.fold).any() or \
                va.duplicated(["variant", "fold", "site", "seed", "horizon"]).any():
            raise ValueError(name + ": val tram nguon thieu/thua dong")
        # M20: skill cua seed trung vi tren val tram nguon, |S1 - S0| theo (fold, tram nguon), trung binh 56 cap
        med = va.groupby(["variant", "fold", "site", "horizon"]).RMSE.median().reset_index()
        med["skill"] = 1 - med.RMSE / pers_val.loc[list(zip(med.site, med.horizon))].to_numpy()
        p = med.pivot_table(index=["fold", "site", "horizon"], columns="variant", values="skill")
        dsk = 100 * (p.S1 - p.S0).abs()
        for h in HORIZONS:
            x = dsk.xs(h, level="horizon")
            out.append(dict(section="source_val", model=name, horizon=h, n=len(x), value=x.mean(),
                            trigger_fires=bool(x.mean() >= TRIGGER_PP)))
    return pd.DataFrame(out), True


def stats(args):
    runs = pd.read_csv(args.out)
    sites = {s: dp.load_site(s, args.data_dir) for s in SITES}
    pv = pd.concat({s: dp.persistence(d, d.idx_val).RMSE for s, d in sites.items()}, names=["site", "horizon"])
    base = pd.read_csv(os.path.join(RESULTS, "baselines.csv"))
    pt = base[base.model == "persistence"].set_index(["site", "horizon"]).RMSE
    tab, ok = analyze(runs, reference(), pt, pv)
    tab.to_csv(args.stats_out, index=False)
    print(tab.to_string(index=False, float_format=lambda x: "%.4g" % x))
    if not ok:
        sys.exit("DUNG: S0 khong tai lap R21/R16 trong {} m/s, khong ket luan S1/S2".format(TOL))
    for name, x in tab[tab.section == "source_val"].groupby("model"):
        print("{}: RevIN trigger (mean |d skill| >= {} pp o horizon bat ky, val tram nguon) -> {}".format(
            name, TRIGGER_PP, "BAT" if x.trigger_fires.any() else "khong bat"))
    print("\nGhi vao", args.stats_out)


def _selftest(data_dir):
    sites, raw = load_all(data_dir)
    t = "A"
    n_tr = {s: int(len(sites[s].X) * dp.SPLIT[0]) for s in SITES}
    wcol = sites[t].features.index(dp.TARGET)
    # S0 = dung scaler cua pipeline
    sx, sy = fit_scalers(raw, fit_rows("S0", t, sites), wcol)
    d0 = rescale(sites[t], raw[t], sx, sy)
    assert np.array_equal(d0.X, sites[t].X) and np.array_equal(d0.y, sites[t].y, equal_nan=True)
    assert np.array_equal(sy.lo, sites[t].scaler_y.lo) and np.array_equal(sy.span, sites[t].scaler_y.span)
    # S1: khong hang nao cua tram dich, chi train cua 7 nguon
    r1 = fit_rows("S1", t, sites)
    assert t not in r1 and sorted(r1) == [s for s in SITES if s != t]
    assert all(r.min() == 0 and r.max() == n_tr[s] - 1 for s, r in r1.items())
    sx1, _ = fit_scalers(raw, r1, wcol)
    assert np.array_equal(sx1.lo, np.min([raw[s][:n_tr[s]].min(0) for s in r1], 0))
    # S2: dung k tuan lien tuc trong train tram dich, ket thuc dung moc cua 18_fewshot
    for w, end in fs.WINDOWS.items():
        r2 = fit_rows("S2_" + w, t, sites)
        assert list(r2) == [t]
        r = r2[t]
        tm = sites[t].time[r]
        assert len(r) == K_WEEKS * 7 * 96 and (np.diff(r) == 1).all() and tm[-1] == pd.Timestamp(end)
        assert np.isin(r, sites[t].idx_train).all() and r.max() < n_tr[t] and not np.isin(r, sites[t].idx_test).any()
        assert tm[0] == pd.Timestamp(end) - pd.Timedelta(weeks=K_WEEKS) + pd.Timedelta(minutes=15)
    # Pooled cua fold: thu tu khoi, khoi S0 giong du lieu goc, khoi val dung idx_val
    d, meta, keys = build_fold(t, sites, raw, nmax=300)
    w = [i for i, f in enumerate(sites[t].features) if f in dp.FEATURE_SETS["wind"]]
    assert keys[0] == "A|S0" and len(keys) == 4 + 14 and d.features == [sites[t].features[i] for i in w]
    s0 = d.idx_test[d.test_site == "A|S0"]
    assert np.array_equal(d.X[s0], sites[t].X[sites[t].idx_test[:300]][:, w])
    assert np.array_equal(d.y_raw[d.idx_test[d.test_site == "B"]], sites["B"].y_raw[sites["B"].idx_val[:300]])
    assert meta["B|S1"][:3] == ("S1", "val", "B") and len(d.idx_train) == 7 * 300
    assert meta["B|S1"][3].lo[0] == np.min([raw[s][:n_tr[s], wcol].min() for s in SITES if s != t])
    # thong ke: Wilcoxon/Holm cua 22 + nguong RevIN tren du lieu gia
    ts._selftest()
    rng = np.random.default_rng(0)
    rows = []
    for f in SITES:
        for k in SEEDS:
            for h in HORIZONS:
                r0 = 1 + 0.1 * SITES.index(f) + 0.01 * k
                for v in VARIANTS:
                    rows.append(dict(fold=f, model="Mamba", seed=k, variant=v, split="test", site=f, horizon=h,
                                     RMSE=r0 * (1 + 0.01 * VARIANTS.index(v))))
                for s in SITES:
                    if s != f:   # val: S1 lech 3 pp skill o 6h, 1 pp o horizon khac
                        dv = 0.03 if h == "6h" else 0.01
                        rows += [dict(fold=f, model="Mamba", seed=k, variant="S0", split="val", site=s, horizon=h, RMSE=1.0),
                                 dict(fold=f, model="Mamba", seed=k, variant="S1", split="val", site=s, horizon=h,
                                      RMSE=1.0 + 2 * dv)]
    runs = pd.DataFrame(rows)
    ref = runs[(runs.variant == "S0") & (runs.split == "test")][["fold", "model", "seed", "horizon", "RMSE"]]
    idx = pd.MultiIndex.from_product([SITES, HORIZONS], names=["site", "horizon"])
    pt = pd.Series(10 + rng.uniform(0, 1, len(idx)), index=idx)      # model thang ca 8 tram
    pv = pd.Series(2.0, index=idx)
    tab, ok = analyze(runs, ref, pt, pv)
    assert ok and (tab[tab.section == "repro"].value == 0).all()
    te = tab[(tab.section == "test") & (tab.metric == "skill")]
    assert len(te) == 4 * 3 and (te.wins == 8).all() and np.allclose(te.p_raw, 2 / 2 ** 8)
    sv = tab[tab.section == "source_val"].set_index("horizon")
    assert np.allclose(sv.value, [1.0, 1.0, 3.0]) and list(sv.trigger_fires) == [False, False, True]
    sd = tab[(tab.section == "site") & (tab.variant == "S1")]
    assert np.allclose(sd.d_rmse_vs_S0, sd.RMSE / 1.01 * 0.01)
    bad = ref.copy()
    bad.loc[bad.index[0], "RMSE"] += 2e-4
    assert analyze(runs, bad, pt, pv)[1] is False
    print("selftest 27: dat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--stats", action="store_true", help="doc --out, ghi --stats-out")
    ap.add_argument("--models", default="Mamba", help="Mamba (suy luan, GPU) va/hoac RF (fit lai, CPU)")
    ap.add_argument("--folds", default=",".join(SITES))
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--data-dir", default=dp.DATA_DIR)
    ap.add_argument("--models-dir", default=os.path.join(RESULTS, "models_loso"))
    ap.add_argument("--out", default=os.path.join(RESULTS, "loso8_scaler.csv"))
    ap.add_argument("--stats-out", default=os.path.join(RESULTS, "loso8_scaler_stats.csv"))
    ap.add_argument("--device", default=None)
    ap.add_argument("--max-batches", type=int, default=0, help="chay thu: moi tap chi so cat con N*256")
    ap.add_argument("--random-init", action="store_true", help="chay thu: Mamba trong so ngau nhien neu thieu .pt")
    args = ap.parse_args()
    if args.selftest:
        _selftest(args.data_dir)
    elif args.stats:
        stats(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
