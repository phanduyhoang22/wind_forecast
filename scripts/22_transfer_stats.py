"""
Thong ke chuyen giao LOSO-8 (hop M13, dieu kien 3-4).

Doc results/loso8_wind.csv, loso8_rf_wind.csv, baselines.csv va ghi:
    results/transfer_stats.csv      Wilcoxon chinh xac hai phia, n = 8 tram, Holm tren 3 horizon
    results/transfer_per_site.csv   skill tung tram: seed trung vi (median) va tung seed

metric = skill (chinh): 1 - RMSE_model / RMSE_ref, ref la persistence hoac RF.
metric = d_rmse (phu):  RMSE_ref - RMSE_model (m/s). Ca hai: > 0 nghia la model tot hon.
Skill dung RMSE trung vi qua seed. Chon quy uoc nay sau khi xem ket qua (phai neu trong bai).

    py scripts/22_transfer_stats.py
    py scripts/22_transfer_stats.py --selftest
"""

import argparse
import importlib.util
import itertools
import os

import numpy as np
import pandas as pd
from scipy.stats import rankdata, wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
SITES = list("ABCDEFGH")
SEEDS = [0, 1, 2]
HORIZONS = ["1h", "3h", "6h"]


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


holm = _load("agg", "08_aggregate.py").holm


def rank_biserial(x):
    """(W+ - W-) / tong hang; > 0 nghia la model tot hon."""
    r = rankdata(np.abs(x))
    return float((r[x > 0].sum() - r[x < 0].sum()) / r.sum())


def compare(a, b):
    """a, b: RMSE tram x horizon cua model va doi chung -> bang kiem dinh ca 2 metric."""
    out = []
    for metric, x in (("skill", 1 - a / b), ("d_rmse", b - a)):
        rows = []
        for h in HORIZONS:
            v = x[h].to_numpy()
            # p chinh xac chi dung khi khong co hieu bang 0 hay trung hang
            if not np.isfinite(v).all() or (v == 0).any() or len(np.unique(np.abs(v))) < len(v):
                raise ValueError("gia tri NaN/0/trung hang, Wilcoxon khong chinh xac: {} {}".format(metric, h))
            rows.append(dict(metric=metric, horizon=h, n=len(v), wins=int((v > 0).sum()),
                             mean=v.mean(), median=np.median(v), rank_biserial=rank_biserial(v),
                             p_raw=wilcoxon(v, alternative="two-sided", method="exact").pvalue))
        df = pd.DataFrame(rows)
        df["p_holm"] = holm(df.p_raw)
        out.append(df)
    return pd.concat(out)


def check(df, cols, levels, name):
    """Dung ngay neu thieu, thua, trung dong hoac RMSE hong."""
    want = set(itertools.product(*levels))
    got = list(df[cols].itertuples(index=False, name=None))
    if set(got) != want or len(got) != len(want):
        raise ValueError("{}: thieu {}, la {}, trung {}".format(
            name, sorted(want - set(got)), sorted(set(got) - want), len(got) - len(set(got))))
    if not (np.isfinite(df.RMSE) & (df.RMSE > 0)).all():
        raise ValueError(name + ": RMSE khong hop le")


def analyze(runs, base):
    base = base[base.model == "persistence"]
    check(base, ["site", "horizon"], [SITES, HORIZONS], "persistence")
    pers = base.pivot(index="site", columns="horizon", values="RMSE")
    tests, sites = [], []
    for st in ["losoW", "globalW"]:
        if st == "globalW" and st not in set(runs.strategy):
            continue
        rmse = {}
        for m in ["Mamba", "RF"]:
            d = runs[(runs.strategy == st) & (runs.model == m)]
            check(d, ["test_site", "seed", "horizon"], [SITES, SEEDS, HORIZONS], st + " " + m)
            if (d.fold != (d.test_site if st == "losoW" else "ALL")).any():
                raise ValueError(st + " " + m + ": fold khong khop chien luoc")
            by_seed = {str(s): g.pivot(index="test_site", columns="horizon", values="RMSE")
                       for s, g in d.groupby("seed")}
            rmse[m] = d.groupby(["test_site", "horizon"]).RMSE.median().unstack()
            for seed, a in [("median", rmse[m])] + list(by_seed.items()):
                tests.append(compare(a, pers).assign(strategy=st, model=m, ref="persistence", seed=seed))
                t = a.rename_axis("site").stack().rename("RMSE").reset_index()
                t["RMSE_persistence"] = [pers.loc[s, h] for s, h in zip(t.site, t.horizon)]
                t["skill"] = 1 - t.RMSE / t.RMSE_persistence
                sites.append(t.assign(strategy=st, model=m, seed=seed))
        tests.append(compare(rmse["Mamba"], rmse["RF"]).assign(strategy=st, model="Mamba", ref="RF", seed="median"))
    key = ["strategy", "model", "ref", "seed", "metric", "horizon"]
    tests, sites = pd.concat(tests), pd.concat(sites)
    key_site = ["strategy", "model", "seed", "site", "horizon"]
    return (tests[key + [c for c in tests if c not in key]],
            sites[key_site + [c for c in sites if c not in key_site]])


def _selftest():
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
    x = np.arange(1.0, 9.0)
    assert rank_biserial(x) == 1 and rank_biserial(-x) == -1
    assert np.isclose(rank_biserial(np.array([-1.0, 2.0, 3.0])), 4 / 6)
    b = pd.DataFrame({h: 10 * x for h in HORIZONS}, index=SITES)
    a = pd.DataFrame({h: 10 * x - x ** 1.5 for h in HORIZONS}, index=SITES)
    r = compare(a, b)
    assert (r.wins == 8).all() and (r.rank_biserial == 1).all() and (r["mean"] > 0).all()
    assert np.allclose(r.p_raw, 2 / 2 ** 8) and np.allclose(r.p_holm, 6 / 2 ** 8)
    assert (compare(b, a).rank_biserial == -1).all()

    rng = np.random.default_rng(0)
    runs = pd.DataFrame([dict(strategy="losoW", fold=s, test_site=s, model=m, seed=k, horizon=h, RMSE=rng.uniform(1, 2))
                         for m in ("Mamba", "RF") for s in SITES for k in SEEDS for h in HORIZONS])
    base = pd.DataFrame([dict(site=s, model="persistence", horizon=h, RMSE=rng.uniform(1, 2))
                         for s in SITES for h in HORIZONS])
    tests, sites = analyze(runs, base)
    assert len(tests) == 54 and len(sites) == 192
    bad_fold, bad_rmse = runs.copy(), runs.copy()
    bad_fold.loc[0, "fold"] = "H"
    bad_rmse.loc[0, "RMSE"] = np.nan
    part = runs[runs.seed == 0].assign(strategy="globalW", fold="ALL")
    for rr, bb in ((runs[runs.test_site != "H"], base), (runs.drop(0), base), (runs[runs.seed != 2], base),
                   (pd.concat([runs, runs[:1]]), base), (pd.concat([runs, part]), base),
                   (bad_fold, base), (bad_rmse, base), (runs, base[1:]), (runs[runs.model != "RF"], base)):
        try:
            analyze(rr, bb)
        except ValueError:
            continue
        raise AssertionError("du lieu thieu/hong ma khong bao loi")
    print("selftest: dat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        _selftest()
        return
    runs = pd.concat([pd.read_csv(os.path.join(RESULTS, f)) for f in ("loso8_wind.csv", "loso8_rf_wind.csv")],
                     ignore_index=True)
    tests, sites = analyze(runs, pd.read_csv(os.path.join(RESULTS, "baselines.csv")))
    tests.to_csv(os.path.join(RESULTS, "transfer_stats.csv"), index=False)
    sites.to_csv(os.path.join(RESULTS, "transfer_per_site.csv"), index=False)
    print(tests.to_string(index=False, float_format=lambda x: "%.4f" % x))


if __name__ == "__main__":
    main()
