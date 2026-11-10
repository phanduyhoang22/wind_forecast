"""
Tong hop ket qua benchmark -> bang cho bai bao.

Doc results/runs*.csv (+ baselines.csv, preds/) va ghi:
    results/summary_by_site.csv   mean +- std theo model x tram x horizon, kem skill score
    results/summary_overall.csv   trung binh 4 tram (Table 4)
    results/summary_cost.csv      tham so, thoi gian train, latency (Table 6)
    results/dm_tests.csv          Diebold-Mariano: Mamba vs tung model, theo tram x horizon

Skill score = 1 - RMSE_model / RMSE_persistence. SS > 0 nghia la vuot persistence.

    py scripts/08_aggregate.py                      # runs.csv + runs_rf.csv
    py scripts/08_aggregate.py --runs results/pilot.csv results/runs_rf.csv
    py scripts/08_aggregate.py --selftest
"""

import argparse
import glob
import importlib.util
import math
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
REF = "Mamba"


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dm_test(e1, e2, h, lag=96):
    """Diebold-Mariano voi sai so binh phuong, phuong sai HAC Bartlett va hieu
    chinh mau nho Harvey-Leybourne-Newbold. Lag = max(h-1, lag): chuoi 15 phut
    co sai so tu tuong quan ca ngay, lag h-1 lam |stat| bi phong dai (hop #1).
    d = e1^2 - e2^2. stat < 0 nghia la model 1 tot hon. Tra ve (stat, p hai phia)."""
    d = e1 ** 2 - e2 ** 2
    n = len(d)
    dc = d - d.mean()
    var = np.dot(dc, dc) / n
    L = max(h - 1, lag)
    for k in range(1, L + 1):
        var += 2 * (1 - k / (L + 1)) * np.dot(dc[k:], dc[:-k]) / n
    if var <= 0:
        return float("nan"), float("nan")
    stat = d.mean() / math.sqrt(var / n)
    stat *= math.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)     # HLN
    p = math.erfc(abs(stat) / math.sqrt(2))                       # ~ N(0,1) voi n lon
    return float(stat), float(p)


def summarize(runs, base):
    pers = base[base.model == "persistence"].set_index(["site", "horizon"]).RMSE
    g = runs.groupby(["model", "site", "horizon"])
    by_site = g[["RMSE", "MAE", "R2"]].agg(["mean", "std"])
    by_site.columns = ["_".join(c) for c in by_site.columns]
    by_site["n_seeds"] = g.seed.nunique()
    by_site = by_site.reset_index()
    by_site["skill"] = 1 - by_site.RMSE_mean / [pers[(s, h)] for s, h in zip(by_site.site, by_site.horizon)]

    # Trung binh 4 tram: lay trung binh theo tram trong tung seed, roi mean/std qua seed
    per_seed = runs.groupby(["model", "horizon", "seed"])[["RMSE", "MAE", "R2"]].mean()
    overall = per_seed.groupby(["model", "horizon"]).agg(["mean", "std"])
    overall.columns = ["_".join(c) for c in overall.columns]
    overall = overall.reset_index()
    sk = by_site.groupby(["model", "horizon"]).skill.mean().rename("skill_avg")
    overall = overall.merge(sk.reset_index(), on=["model", "horizon"])

    cost = (runs.drop_duplicates(["model", "site", "seed"])
            .groupby("model")[["params", "train_s", "latency_ms", "best_epoch"]]
            .agg(["mean", "std"]))
    cost.columns = ["_".join(c) for c in cost.columns]
    return by_site, overall, cost.reset_index()


def dm_all(runs, pred_dir, dp):
    """So Mamba voi tung model, dung du doan trung binh qua cac seed."""
    rows = []
    if not os.path.isdir(pred_dir) or REF not in set(runs.model):
        return pd.DataFrame(rows)
    for site in sorted(runs.site.unique()):
        d = dp.load_site(site)
        y = d.y_raw[d.idx_test]

        def ens(model):
            fs = sorted(glob.glob(os.path.join(pred_dir, "{}_{}_*.npz".format(site, model))))
            return np.mean([np.load(f)["y_pred"] for f in fs], axis=0) if fs else None

        ref = ens(REF)
        if ref is None:
            continue
        for other in sorted(set(runs.model) - {REF}):
            p = ens(other)
            if p is None:
                continue
            for j, (k, lab) in enumerate(dp.HORIZONS):
                stat, pv = dm_test(y[:, j] - ref[:, j], y[:, j] - p[:, j], k)
                rows.append(dict(site=site, horizon=lab, vs=other, dm_stat=stat, p_value=pv))
    df = pd.DataFrame(rows)
    if len(df):
        df["p_holm"] = holm(df.p_value.to_numpy())
        df["mamba_better"] = (df.dm_stat < 0) & (df.p_holm < 0.05)
        df["mamba_worse"] = (df.dm_stat > 0) & (df.p_holm < 0.05)
    return df


def dm_per_seed(runs, pred_dir, dp):
    """Tang chinh (hop #2): mo hinh DON. Seed i cua Mamba vs seed i cua X,
    DM tung cap, Holm tren toan ho phep so; dem k/5 seed thang/thua co y nghia.
    Kem kiem dinh ghep (t ghep) tren hieu RMSE theo seed."""
    from scipy import stats
    rows = []
    for site in sorted(runs.site.unique()):
        d = dp.load_site(site)
        y = d.y_raw[d.idx_test]
        for other in sorted(set(runs.model) - {REF}):
            seeds = sorted(set(runs[(runs.site == site) & (runs.model == REF)].seed)
                           & set(runs[(runs.site == site) & (runs.model == other)].seed))
            for s in seeds:
                fa = os.path.join(pred_dir, "{}_{}_{}.npz".format(site, REF, s))
                fb = os.path.join(pred_dir, "{}_{}_{}.npz".format(site, other, s))
                if not (os.path.exists(fa) and os.path.exists(fb)):
                    continue
                a, b = np.load(fa)["y_pred"], np.load(fb)["y_pred"]
                for j, (k, lab) in enumerate(dp.HORIZONS):
                    stat, pv = dm_test(y[:, j] - a[:, j], y[:, j] - b[:, j], k)
                    rows.append(dict(site=site, horizon=lab, vs=other, seed=s, dm_stat=stat, p_value=pv))
    df = pd.DataFrame(rows)
    if not len(df):
        return df, df
    df["p_holm"] = holm(df.p_value.to_numpy())
    df["win"] = (df.dm_stat < 0) & (df.p_holm < 0.05)
    df["loss"] = (df.dm_stat > 0) & (df.p_holm < 0.05)
    summ = df.groupby(["site", "horizon", "vs"]).agg(n=("seed", "size"), wins=("win", "sum"),
                                                    losses=("loss", "sum")).reset_index()
    # t ghep tren RMSE theo seed (n = so seed chung)
    pr = []
    for (site, h, other), _ in summ.groupby(["site", "horizon", "vs"]):
        ra = runs[(runs.site == site) & (runs.horizon == h) & (runs.model == REF)].set_index("seed").RMSE
        rb = runs[(runs.site == site) & (runs.horizon == h) & (runs.model == other)].set_index("seed").RMSE
        c = ra.index.intersection(rb.index)
        diff = (ra[c] - rb[c]).to_numpy()
        p = stats.ttest_rel(ra[c], rb[c]).pvalue if len(c) > 1 and diff.std() > 0 else np.nan
        pr.append(dict(site=site, horizon=h, vs=other, d_rmse=diff.mean(), p_ttest=p))
    summ = summ.merge(pd.DataFrame(pr), on=["site", "horizon", "vs"])
    return df, summ


def holm(p):
    """Hieu chinh Holm-Bonferroni cho ho phep so (tram x horizon x doi thu)."""
    p = np.nan_to_num(np.asarray(p, float), nan=1.0)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (len(p) - i) * p[j]))
        adj[j] = run
    return adj


def _selftest():
    rng = np.random.default_rng(0)
    y = rng.normal(size=5000)
    a = y + rng.normal(scale=0.5, size=5000)
    b = y + rng.normal(scale=0.5, size=5000)
    s, p = dm_test(y - a, y - b, 4)
    assert p > 0.01, ("hai du bao ngang nhau ma DM bao khac", s, p)
    c = y + rng.normal(scale=1.0, size=5000)
    s, p = dm_test(y - a, y - c, 4)
    assert s < 0 and p < 1e-6, ("a tot hon ro rang ma DM khong bat duoc", s, p)
    print("selftest DM: dat")
    adj = holm([0.01, 0.04, 0.03, 0.5])
    assert np.allclose(adj, [0.04, 0.09, 0.09, 0.5]), adj
    print("selftest Holm: dat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return

    paths = args.runs or [p for p in (os.path.join(RESULTS, "runs.csv"),
                                      os.path.join(RESULTS, "runs_rf.csv")) if os.path.exists(p)]
    runs = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    base = pd.read_csv(os.path.join(RESULTS, "baselines.csv"))
    print("Doc:", ", ".join(os.path.basename(p) for p in paths),
          "| {} luot".format(len(runs.drop_duplicates(["site", "model", "seed"]))))

    by_site, overall, cost = summarize(runs, base)
    by_site.to_csv(os.path.join(RESULTS, "summary_by_site.csv"), index=False)
    overall.to_csv(os.path.join(RESULTS, "summary_overall.csv"), index=False)
    cost.to_csv(os.path.join(RESULTS, "summary_cost.csv"), index=False)

    f4 = lambda x: "%.4f" % x
    print("\nRMSE theo tram (mean qua seed) | persistence de so:")
    piv = by_site.pivot_table(index=["site", "horizon"], columns="model", values="RMSE_mean")
    piv["persistence"] = base[base.model == "persistence"].set_index(["site", "horizon"]).RMSE
    print(piv.to_string(float_format=f4))
    print("\nSkill score theo tram:")
    print(by_site.pivot_table(index=["site", "horizon"], columns="model", values="skill")
          .to_string(float_format=f4))
    print("\nTrung binh 4 tram:")
    print(overall.pivot_table(index="horizon", columns="model", values="RMSE_mean")
          .to_string(float_format=f4))
    print("\nChi phi:")
    print(cost.to_string(index=False, float_format=lambda x: "%.3g" % x))

    dp = _load("dp", "04_data_pipeline.py")
    dm = dm_all(runs, os.path.join(RESULTS, "preds"), dp)
    seed_dm, seed_sum = dm_per_seed(runs, os.path.join(RESULTS, "preds"), dp)
    if len(seed_sum):
        seed_dm.to_csv(os.path.join(RESULTS, "dm_per_seed.csv"), index=False)
        seed_sum.to_csv(os.path.join(RESULTS, "dm_per_seed_summary.csv"), index=False)
        print("\nDM MO HINH DON (seed i vs seed i, Holm tren {} phep so): thang/thua tren n seed".format(len(seed_dm)))
        seed_sum["kq"] = seed_sum.wins.astype(str) + "/" + seed_sum.losses.astype(str) + " of " + seed_sum.n.astype(str)
        print(seed_sum.pivot_table(index=["site", "horizon"], columns="vs", values="kq", aggfunc="first").to_string())
        print("\nHieu RMSE Mamba - X (am = Mamba tot hon) | p t ghep:")
        print(seed_sum.pivot_table(index=["site", "horizon"], columns="vs", values="d_rmse")
              .to_string(float_format=lambda x: "%+.4f" % x))
    if len(dm):
        dm.to_csv(os.path.join(RESULTS, "dm_tests.csv"), index=False)
        print("\nDM ENSEMBLE 5 seed (phuong phap rieng, chi phi x5; stat<0 = Mamba tot hon):")
        print(dm.pivot_table(index=["site", "horizon"], columns="vs", values="dm_stat")
              .to_string(float_format=lambda x: "%.2f" % x))
    else:
        print("\n(Chua co du doan trong results/preds -> bo qua DM)")


if __name__ == "__main__":
    main()
