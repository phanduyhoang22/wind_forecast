"""
T23 (hop M20): LightGBM lam doi chung manh, cung hop dong du lieu voi moi model.

Moi horizon mot regressor; dau vao = cua so 96 buoc lam phang (E1 96x31, LOSO 96x19).
--lag-step 4 = phuong an du phong tinh toan (chi lag 0, 4, ..., 92 -> 24xF), chon bang
--time-pilot, KHONG bang diem so.

Quy trinh (thiet ke dang ky truoc, STATUS.md T23):
  1) chon luoi {num_leaves 31,63,127} x {lr 0.03,0.1}, seed 0, tren val
     (E1: tram A + D; LOSO: val gop cua tram nguon fold A + D); tieu chi = val MSE (thang
     chuan hoa) trung binh qua don vi x 3 horizon (chinh sach M01). Dong stage=select khong co diem test.
  2) dong bang cau hinh do cho moi tram / fold: E1 seed 0-4, LOSO seed 0-2.
  n_estimators <= 3000, early stopping 100 vong tren val; subsample 0.8, colsample 0.5,
  bagging_freq 1; con lai mac dinh. Chay tiep duoc: bo qua khoa da co trong CSV.

    py scripts/29_lgbm.py --selftest
    py scripts/29_lgbm.py --time-pilot                                  # 1 lan fit, tram A, 1h
    py scripts/29_lgbm.py --setting e1 --lag-step 4                     # -> results/lgbm_e1.csv
    py scripts/29_lgbm.py --setting loso --lag-step 4                   # -> results/lgbm_loso8.csv
    py scripts/29_lgbm.py --stats                                       # -> results/references_stats.csv
    # CPU mode (chay thu, chi ra thu muc nhap):
    py scripts/29_lgbm.py --setting e1 --sites A --seeds 1 --lag-step 4 --max-rows 500 --n-estimators 50 --out <scratch>/e1.csv
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
ts = _load("ts", "22_transfer_stats.py")         # compare (Wilcoxon chinh xac), check, holm

GRID = [(nl, lr) for nl in (31, 63, 127) for lr in (0.03, 0.1)]
PARAMS = dict(objective="regression", bagging_fraction=0.8, feature_fraction=0.5, bagging_freq=1, verbose=-1)
N_EST, EARLY = 3000, 100
SELECT_UNITS = ["A", "D"]
SEEDS = {"e1": 5, "loso": 3}
PILOT_CFG = (63, 0.03)                           # diem luoi o giua, lr cham -> uoc luong than trong
BUDGET_S = 12 * 3600
HORIZONS = [lab for _, lab in dp.HORIZONS]


def lags(step):
    """Cac lag dung (lag 0 = buoc t). step 1 -> 0..95, step 4 -> 0, 4, ..., 92."""
    return np.arange(0, dp.SEQ_LEN, step)


def design(X, idx, step):
    """Cua so phang (len(idx), L*F): X[t-l] voi l thuoc lags(step), lag xa truoc, lag 0 cuoi.
    Moi offset <= 0 -> khong nhin tuong lai; |offset| <= SEQ_LEN-1 -> nam trong cua so cua t."""
    off = -lags(step)[::-1]
    return X[idx[:, None] + off[None, :]].reshape(len(idx), -1)


def fit(Xtr, ytr, Xva, yva, num_leaves, learning_rate, seed, n_est=N_EST):
    """Chi nhan train + val: early stopping va val MSE tinh tren val, test khong vao day."""
    import lightgbm as lgb
    p = dict(PARAMS, num_leaves=num_leaves, learning_rate=learning_rate, seed=seed)
    dtr = lgb.Dataset(Xtr, ytr)
    dva = lgb.Dataset(Xva, yva, reference=dtr)
    b = lgb.train(p, dtr, n_est, valid_sets=[dva], callbacks=[lgb.early_stopping(EARLY, verbose=False)])
    return b, float(b.best_score["valid_0"]["l2"])


def predict(b, X, idx, step, chunk=20000):
    """Du doan theo khoi -> khong materialize ca tap test cung luc."""
    return np.concatenate([b.predict(design(X, idx[i:i + chunk], step), num_iteration=b.best_iteration)
                           for i in range(0, len(idx), chunk)])


def subsample(idx, max_rows):
    """CPU mode: lay deu max_rows chi so (giu thu tu thoi gian); 0 = giu nguyen."""
    return idx if not max_rows or len(idx) <= max_rows else idx[np.linspace(0, len(idx) - 1, max_rows).astype(int)]


def run_job(d, j, cfg, seed, step, scaler, with_test, max_rows=0, n_est=N_EST):
    """Mot lan fit cho horizon j. scaler: MinMax y cua tram duoc cham (LOSO: tram dich)."""
    tr, va = subsample(d.idx_train, max_rows), subsample(d.idx_val, max_rows)
    t0 = time.time()
    b, vmse = fit(design(d.X, tr, step), d.y[tr, j], design(d.X, va, step), d.y[va, j], *cfg, seed, n_est)
    row = dict(num_leaves=cfg[0], learning_rate=cfg[1], lag_step=step, best_iter=b.best_iteration,
               val_mse=vmse, train_s=time.time() - t0, RMSE=np.nan, MAE=np.nan, R2=np.nan)  # select: khong cham test
    if with_test:
        te = subsample(d.idx_test, max_rows)
        p = scaler.inverse(predict(b, d.X, te, step).reshape(-1, 1)).ravel()
        t = d.y_raw[te, j]
        row.update(RMSE=float(np.sqrt(np.mean((t - p) ** 2))), MAE=float(np.mean(np.abs(t - p))),
                   R2=float(1 - np.sum((t - p) ** 2) / np.sum((t - t.mean()) ** 2)))
    return row


def choose(sel):
    """Cau hinh co val MSE trung binh (don vi x horizon) nho nhat; hoa -> thu tu GRID."""
    m = sel.groupby(["num_leaves", "learning_rate"]).val_mse.mean()
    return min(GRID, key=lambda c: m[c])


def projection(t_fit, n_sites=8):
    """Tong thoi gian CPU (s) cho ca thiet ke, tu 1 lan fit E1 (tram A, 1 diem luoi, 1 horizon).
    shortcut: chi phi ~ so dong x so dac trung, so vong cay coi nhu bang lan pilot."""
    n_sel = len(GRID) * len(SELECT_UNITS) * len(HORIZONS)
    e1 = (n_sel + n_sites * SEEDS["e1"] * len(HORIZONS)) * t_fit
    loso = (n_sel + n_sites * SEEDS["loso"] * len(HORIZONS)) * t_fit * (n_sites - 1) * 19 / 31
    return e1, loso


class Units:
    """E1: don vi = tram (31 dac trung). LOSO: don vi = fold, Pooled cua 09 voi dac trung W."""

    def __init__(self, setting, sites):
        self.setting, self.sites, self.cur = setting, sites, (None, None)
        if setting == "loso":
            self.gl = _load("gl", "09_global_loso.py")
            self.data = {s: dp.load_site(s) for s in sites}

    def get(self, u):
        if self.cur[0] != u:
            self.cur = (None, None)                  # giai phong khoi cu truoc khi ghep khoi moi
            if self.setting == "e1":
                d = dp.load_site(u)
                self.cur = (u, (d, d.scaler_y))
            else:
                src = [s for s in self.sites if s != u]
                d = self.gl.Pooled(self.data, src, [u], features="wind")
                self.cur = (u, (d, self.data[u].scaler_y))
        return self.cur[1]

    def key(self, u):
        return dict(site=u) if self.setting == "e1" else dict(strategy="losoW", fold=u, test_site=u)


def run(args):
    out = args.out or os.path.join(RESULTS, "lgbm_e1.csv" if args.setting == "e1" else "lgbm_loso8.csv")
    if args.max_rows and os.path.abspath(os.path.dirname(out)) == os.path.abspath(RESULTS):
        raise SystemExit("--max-rows chi de chay thu: dung --out ngoai results/")
    sites = [s.strip().upper() for s in args.sites.split(",")]
    units = [s.strip().upper() for s in args.folds.split(",")] if args.folds else sites
    seeds = args.seeds or SEEDS[args.setting]
    prev = pd.read_csv(out) if os.path.exists(out) else pd.DataFrame()
    if len(prev) and set(prev.lag_step) != {args.lag_step}:
        raise SystemExit("{} da co lag_step {}, khong tron".format(out, sorted(set(prev.lag_step))))
    ucol = "site" if args.setting == "e1" else "fold"
    done = set() if not len(prev) else set(zip(prev.stage, prev[ucol], prev.seed, prev.horizon,
                                               prev.num_leaves, prev.learning_rate))
    U = Units(args.setting, sites)

    def job(stage, u, seed, j, cfg):
        k = (stage, u, seed, HORIZONS[j]) + cfg
        tag = "{} {} seed={} {} cfg={}".format(stage, u, seed, HORIZONS[j], cfg)
        if k in done:
            print(tag, "-> da co, bo qua")
            return
        d, scaler = U.get(u)
        r = run_job(d, j, cfg, seed, args.lag_step, scaler, stage == "final", args.max_rows, args.n_estimators)
        row = dict(stage=stage, **U.key(u), model="LightGBM", seed=seed, horizon=HORIZONS[j], **r)
        print("{}  {:.0f}s  iter={}  val_mse={:.6f}".format(tag, r["train_s"], r["best_iter"], r["val_mse"]),
              flush=True)
        pd.DataFrame([row]).to_csv(out, mode="a" if os.path.exists(out) else "w",
                                   header=not os.path.exists(out), index=False)
        done.add(k)

    sel_units = [u for u in SELECT_UNITS if u in units] or units[:1]
    for u in sel_units:
        for cfg in GRID:
            for j in range(len(HORIZONS)):
                job("select", u, 0, j, cfg)
    sel = pd.read_csv(out)
    sel = sel[(sel.stage == "select") & sel[ucol].isin(sel_units)]
    n = sel.groupby(["num_leaves", "learning_rate"]).size()
    assert len(n) == len(GRID) and (n == len(sel_units) * len(HORIZONS)).all(), "luoi chon chua du"
    cfg = choose(sel)
    print("Cau hinh chot (val, {}): num_leaves={} lr={}".format(sel_units, *cfg))
    for u in units:
        for seed in range(seeds):
            for j in range(len(HORIZONS)):
                job("final", u, seed, j, cfg)
    print("\nGhi vao", out)


def time_pilot(step):
    """Do 1 lan fit (E1, tram A, 1h, PILOT_CFG, seed 0, du lieu day du), khong tinh diem test."""
    d = dp.load_site("A")
    r = run_job(d, 0, PILOT_CFG, 0, step, d.scaler_y, with_test=False)
    e1, lo = projection(r["train_s"])
    print("pilot: lag_step={} cfg={} train_s={:.1f} best_iter={} (gom tao cua so + Dataset + train)"
          .format(step, PILOT_CFG, r["train_s"], r["best_iter"]))
    print("du kien: E1 {:.1f} h + LOSO {:.1f} h = {:.1f} h (nguong {:.0f} h) -> {}".format(
        e1 / 3600, lo / 3600, (e1 + lo) / 3600, BUDGET_S / 3600,
        "--lag-step 4 (du phong)" if e1 + lo > BUDGET_S else "--lag-step 1 (cua so day du)"))


def median_rmse(df, ucol, seeds, name):
    ts.check(df, [ucol, "seed", "horizon"], [ts.SITES, seeds, HORIZONS], name)
    return df.groupby([ucol, "horizon"]).RMSE.median().unstack()[HORIZONS].rename_axis("site")


def stats(runs_e1, loso_nn, lgb_e1, lgb_loso, refs, base, loso_rf=None):
    """Ho Holm m = 6 (xac nhan): Mamba vs LightGBM, E1 + LOSO-W, 3 horizon, Wilcoxon chinh xac n = 8
    tren skill = 1 - RMSE_Mamba / RMSE_LightGBM cua seed trung vi (quy uoc cua 22). Con lai: mo ta."""
    f = lambda df: df[df.stage == "final"]
    e1 = {"Mamba": median_rmse(runs_e1[runs_e1.model == "Mamba"], "site", list(range(5)), "E1 Mamba"),
          "LightGBM": median_rmse(f(lgb_e1), "site", list(range(5)), "E1 LightGBM")}
    lo = {"Mamba": median_rmse(loso_nn[(loso_nn.strategy == "losoW") & (loso_nn.model == "Mamba")],
                               "test_site", list(range(3)), "LOSO Mamba-W"),
          "LightGBM": median_rmse(f(lgb_loso), "test_site", list(range(3)), "LOSO LightGBM-W")}
    conf = pd.concat([ts.compare(e1["Mamba"], e1["LightGBM"]).assign(setting="E1"),
                      ts.compare(lo["Mamba"], lo["LightGBM"]).assign(setting="losoW")])
    conf["p_holm"] = conf.groupby("metric").p_raw.transform(ts.holm)    # m = 6 trong moi metric
    conf = conf.assign(table="confirmatory", model="Mamba", ref="LightGBM")

    # Mo ta: skill moi model vs persistence / P1 / P2 (seed trung vi), khong hieu chinh
    for m in sorted(set(runs_e1.model) - {"Mamba"}):
        g = runs_e1[runs_e1.model == m]
        e1[m] = median_rmse(g, "site", sorted(g.seed.unique()), "E1 " + m)
    if loso_rf is not None:
        g = loso_rf[loso_rf.strategy == "losoW"]
        lo["RF"] = median_rmse(g, "test_site", sorted(g.seed.unique()), "LOSO RF-W")
    pers = base[base.model == "persistence"].pivot(index="site", columns="horizon", values="RMSE")[HORIZONS]
    ref = lambda st, m: refs[(refs.setting == st) & (refs.model == m)].pivot(
        index="test_site", columns="horizon", values="RMSE")[HORIZONS].rename_axis("site")
    desc = []
    for st, models in (("E1", e1), ("losoW", lo)):
        for rname, r in (("persistence", pers), ("SmartPersistence", ref(st, "SmartPersistence")),
                         ("Blend", ref(st, "Blend"))):
            for m, a in models.items():
                try:
                    c = ts.compare(a, r)
                except ValueError as e:                  # hoa/0 -> khong co p chinh xac, bao ro
                    print("bo qua mo ta", st, m, rname, e)
                    continue
                desc.append(c.assign(setting=st, table="descriptive", model=m, ref=rname, p_holm=np.nan))
    out = pd.concat([conf] + desc, ignore_index=True)
    key = ["table", "setting", "model", "ref", "metric", "horizon"]
    return out[key + [c for c in out if c not in key]]


def _selftest():
    # 1) cua so phang: hinh dang, thu tu lag, khong nhin tuong lai
    T, F = 400, 3
    X = np.stack([np.arange(T) * 10 + k for k in range(F)], 1).astype(np.float32)   # X[t, k] = 10t + k
    idx = np.arange(dp.SEQ_LEN - 1, 300)
    for step, L in ((1, 96), (4, 24)):
        Z = design(X, idx, step)
        assert Z.shape == (len(idx), L * F)
        tt = (Z.reshape(len(idx), L, F)[:, :, 0] // 10).astype(int)          # buoc thoi gian cua moi lag
        assert (tt[:, -1] == idx).all() and (tt <= idx[:, None]).all()       # lag 0 = t, khong co t' > t
        assert (tt[:, 0] == idx - (dp.SEQ_LEN - step)).all() and (np.diff(tt, axis=1) == step).all()
    assert np.array_equal(design(X, idx, 1), np.stack([X[t - 95: t + 1].ravel() for t in idx]))
    # 2) split that: purged; LOSO: train/val gop khong cham hang cua tram dich, test chi tram dich
    data = {s: dp.load_site(s) for s in dp.SITES}
    for d in data.values():
        for a, b in ((d.idx_train, d.idx_val), (d.idx_val, d.idx_test)):
            assert a.max() + dp.MAX_H < b.min() - dp.SEQ_LEN + 1
    gl = _load("gl", "09_global_loso.py")
    start = np.cumsum([0] + [len(data[s].X) for s in dp.SITES])      # Pooled ghep theo thu tu dp.SITES
    keep = [i for i, f in enumerate(data["A"].features) if f in dp.FEATURE_SETS["wind"]]
    for u in SELECT_UNITS:
        src = [s for s in dp.SITES if s != u]
        P = gl.Pooled(data, src, [u], features="wind")
        site_of = lambda i: np.array(list(dp.SITES))[np.searchsorted(start, i, side="right") - 1]
        assert P.n_features == 19
        assert u not in set(site_of(P.idx_train)) | set(site_of(P.idx_val)) and set(site_of(P.idx_test)) == {u}
        for i in (P.idx_train, P.idx_val, P.idx_test):          # cua so + nhan nam gon trong mot tram
            b = start[np.searchsorted(start, i, side="right") - 1]
            assert (i - dp.SEQ_LEN + 1 >= b).all() and (np.searchsorted(start, i + dp.MAX_H, side="right")
                                                         == np.searchsorted(start, i, side="right")).all()
        s0 = src[0]
        assert np.array_equal(design(P.X, P.idx_train[:5], 1), design(data[s0].X[:, keep], data[s0].idx_train[:5], 1))
    del data
    # 3) fit nho: early stopping dung val duoc dua vao; val_mse = l2 that cua mo hinh tai best_iter
    rng = np.random.default_rng(0)
    Xs = rng.normal(size=(600, 8)).astype(np.float32)
    ys = Xs[:, 0] * 2 + rng.normal(scale=0.1, size=600)
    b, v = fit(Xs[:400], ys[:400], Xs[400:], ys[400:], 31, 0.1, 0, n_est=300)
    assert 1 <= b.best_iteration <= 300
    assert np.isclose(v, np.mean((b.predict(Xs[400:], num_iteration=b.best_iteration) - ys[400:]) ** 2), rtol=1e-6)
    # 4) chon luoi = argmin val MSE trung binh; uoc luong thoi gian
    sel = pd.DataFrame([dict(num_leaves=c[0], learning_rate=c[1], val_mse=1.0 + i + (u == "D") * 0.5)
                        for i, c in enumerate(GRID) for u in "AD"])
    assert choose(sel) == GRID[0]
    sel.loc[sel.num_leaves == 127, "val_mse"] = 0.1
    assert choose(sel) == (127, 0.03)
    e1, lo = projection(1.0)
    assert e1 == 36 + 120 and np.isclose(lo, (36 + 72) * 7 * 19 / 31)
    # 5) bang Holm m = 6 tren du lieu gia: thang ca 8 tram -> p = 2/256, Holm x6
    S, k = ts.SITES, np.arange(1.0, 9.0)
    mk = lambda st, m, seeds, rm: pd.DataFrame([dict(stage="final", strategy=st, site=s, fold=s, test_site=s,
                                                     model=m, seed=q, horizon=h, RMSE=rm(i) + 1e-3 * q)
                                                for i, s in enumerate(S) for q in seeds for h in HORIZONS])
    rm_l = lambda i: 10 * k[i]
    rm_m = lambda i: 10 * k[i] - k[i] ** 1.5
    rm_r = lambda i: 20 * k[i] + k[i] ** 2
    runs_e1 = pd.concat([mk("-", "Mamba", range(5), rm_m), mk("-", "LSTM", range(5), rm_l)])
    loso_nn = mk("losoW", "Mamba", range(3), rm_m)
    refs = pd.concat([pd.DataFrame([dict(setting=st, test_site=s, model=m, horizon=h, RMSE=rm_r(i) + 0.1 * (m == "Blend"))
                                    for i, s in enumerate(S) for h in HORIZONS])
                      for st in ("E1", "losoW") for m in ("SmartPersistence", "Blend")])
    base = pd.DataFrame([dict(site=s, model="persistence", horizon=h, RMSE=rm_r(i)) for i, s in enumerate(S)
                         for h in HORIZONS])
    out = stats(runs_e1, loso_nn, mk("-", "LightGBM", range(5), rm_l), mk("losoW", "LightGBM", range(3), rm_l),
                refs, base)
    c = out[out.table == "confirmatory"]
    assert len(c) == 12 and (c.wins == 8).all()
    assert np.allclose(c.p_raw, 2 / 256) and np.allclose(c.p_holm, 12 / 256)
    dsc = out[out.table == "descriptive"]
    assert len(dsc) == (3 + 2) * 3 * 6 and set(dsc.model) == {"Mamba", "LSTM", "LightGBM"} and dsc.p_holm.isna().all()
    try:
        stats(runs_e1, loso_nn, mk("-", "LightGBM", range(4), rm_l), mk("losoW", "LightGBM", range(3), rm_l),
              refs, base)
    except ValueError:
        pass
    else:
        raise AssertionError("thieu seed LightGBM ma khong bao loi")
    print("selftest: dat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--time-pilot", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--setting", choices=["e1", "loso"])
    ap.add_argument("--lag-step", type=int, choices=[1, 4], help="bat buoc khi chay: 1 day du, 4 du phong")
    ap.add_argument("--sites", default=",".join(dp.SITES))
    ap.add_argument("--folds", default=None, help="LOSO: chi chay cac fold nay (mac dinh: moi tram)")
    ap.add_argument("--seeds", type=int, default=0, help="0 = theo thiet ke (E1 5, LOSO 3)")
    ap.add_argument("--max-rows", type=int, default=0, help="CPU mode: so dong moi tap, chi de chay thu")
    ap.add_argument("--n-estimators", type=int, default=N_EST)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.selftest:
        _selftest()
    elif args.time_pilot:
        time_pilot(args.lag_step or 1)
    elif args.stats:
        rd = lambda f: pd.read_csv(os.path.join(RESULTS, f))
        rf = os.path.join(RESULTS, "loso8_rf_wind.csv")
        out = stats(rd("runs.csv"), rd("loso8_wind.csv"), rd("lgbm_e1.csv"), rd("lgbm_loso8.csv"),
                    rd("references.csv"), rd("baselines.csv"), pd.read_csv(rf) if os.path.exists(rf) else None)
        path = args.out or os.path.join(RESULTS, "references_stats.csv")
        out.to_csv(path, index=False)
        print(out[out.table == "confirmatory"].to_string(index=False, float_format=lambda x: "%.4f" % x))
        print("\nGhi vao", path)
    else:
        if not args.setting or not args.lag_step:
            ap.error("can --setting va --lag-step (xem --time-pilot)")
        run(args)


if __name__ == "__main__":
    main()
