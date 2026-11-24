"""
Thong ke few-shot T12 (hop M14, dieu kien 1-4; chot truoc khi doc diem test).

Doc fewshot8_cc.csv, fewshot8_ft_free.csv, fewshot8_cpu_cc.csv, fewshot8_cpu_free.csv,
loso8_wind.csv, baselines.csv trong results/ va ghi:
    results/fewshot8_stats.csv      Wilcoxon chinh xac hai phia, n = 8 tram, Holm tren 3 horizon cho tung phep so
    results/fewshot8_per_site.csv   skill tung tram so voi persistence: seed trung vi (median) va tung seed;
                                    weeks = all la trung binh 6 o, weeks = 1/2/4 chi de mo ta
    results/fewshot8_cells.csv      tung o cua so x tuan (chi mo ta, khong kiem dinh)

skill o = 1 - RMSE_model / RMSE_ref (RMSE trung vi qua seed), roi trung binh 6 o moi tram.
d_rmse (phu) = RMSE_ref - RMSE_model (m/s), cung trung binh 6 o. > 0 nghia la model tot hon.
best_test: doi chung co RMSE test thap nhat moi tram/o/horizon (oracle, bat loi cho finetune).
best_val:  doi chung co val_best (trung vi seed) thap nhat moi tram/o, chung cho 3 horizon.

    py scripts/23_fewshot_stats.py
    py scripts/23_fewshot_stats.py --selftest
"""

import argparse
import importlib.util
import itertools
import os
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ts = _load("ts", "22_transfer_stats.py")
RESULTS, SITES, SEEDS, HORIZONS = ts.RESULTS, ts.SITES, ts.SEEDS, ts.HORIZONS
WINDOWS, WEEKS = ["DB", "TN"], [1, 2, 4]
FILES = {"fewshot8_cc.csv": ("cc", ["finetune", "scratch"]), "fewshot8_ft_free.csv": ("free", ["finetune"]),
         "fewshot8_cpu_cc.csv": ("cc", ["ridge", "rf"]), "fewshot8_cpu_free.csv": ("free", ["ridge", "rf"])}
REFS = ["scratch_cc", "ridge_cc", "rf_cc"]
CELL = ["site", "window", "weeks"]
# dong dau la phep so chinh duy nhat; khong hieu chinh giua cac phep so
PAIRS = ([("finetune_free", "best_test", "primary")]
         + [("finetune_free", r, "secondary") for r in ["persistence", "zero_shot"] + REFS + ["best_val"]]
         + [("finetune_cc", "finetune_free", "secondary")]
         + [("finetune_free", r, "sensitivity") for r in ("ridge_free", "rf_free")])


def read_runs(frames):
    """Kiem tra tung file roi gop; variant = mode + cach xu ly lich (cc = month_* co dinh)."""
    out = []
    for f, (cal, modes) in FILES.items():
        d = frames[f]
        ts.check(d, ["model", "mode"] + CELL + ["seed", "horizon"],
                 [["Mamba"], modes, SITES, WINDOWS, WEEKS, SEEDS, HORIZONS], f)
        if not np.isfinite(d.val_best).all() or (d.groupby(["mode"] + CELL + ["seed"]).val_best.nunique() != 1).any():
            raise ValueError(f + ": val_best hong hoac khac nhau giua cac horizon")
        out.append(d.assign(variant=d["mode"] + "_" + cal))
    return pd.concat(out, ignore_index=True)


def add_refs(wide, zero, pers):
    """Gan persistence, zero-shot (hang so trong 6 o) vao bang RMSE (site, window, weeks, horizon) x variant."""
    key = list(zip(wide.index.get_level_values("site"), wide.index.get_level_values("horizon")))
    return wide.assign(zero_shot=zero.loc[key].to_numpy(), persistence=pers.loc[key].to_numpy())


def site_mean(x):
    """Trung binh 6 o -> bang tram x horizon."""
    return x.groupby(["site", "horizon"]).mean().unstack()


def compare(a, b):
    # trung binh cua skill = 1 - trung binh ti so; d_rmse trung binh = hieu hai trung binh
    ratio = site_mean(a / b)
    s = ts.compare(ratio, ratio * 0 + 1)
    d = ts.compare(site_mean(a), site_mean(b))
    return pd.concat([s[s.metric == "skill"], d[d.metric == "d_rmse"]])


def analyze(frames, loso, base):
    runs = read_runs(frames)
    base = base[base.model == "persistence"]
    ts.check(base, ["site", "horizon"], [SITES, HORIZONS], "persistence")
    pers = base.set_index(["site", "horizon"]).RMSE
    loso = loso[(loso.strategy == "losoW") & (loso.model == "Mamba")]
    ts.check(loso, ["test_site", "seed", "horizon"], [SITES, SEEDS, HORIZONS], "losoW Mamba")
    if (loso.fold != loso.test_site).any():
        raise ValueError("losoW Mamba: fold khac test_site")
    loso = loso.rename(columns={"test_site": "site"})

    idx = CELL + ["horizon"]
    med = add_refs(runs.groupby(idx + ["variant"]).RMSE.median().unstack(),
                   loso.groupby(["site", "horizon"]).RMSE.median(), pers)
    val = runs[runs.variant.isin(REFS)].groupby(CELL + ["variant"]).val_best.median().unstack()[REFS]
    # oracle chon theo tung horizon, best_val chon mot lan moi o
    chosen = pd.DataFrame({"best_test": med[REFS].idxmin(axis=1)})
    chosen["best_val"] = val.idxmin(axis=1).loc[list(med.index.droplevel("horizon"))].to_numpy()
    for c in chosen:
        med[c] = [med.at[i, r] for i, r in chosen[c].items()]

    tests = pd.concat([compare(med[m], med[r]).assign(model=m, ref=r, role=role) for m, r, role in PAIRS])
    tables = [("median", med)] + [
        (str(s), add_refs(runs[runs.seed == s].pivot(index=idx, columns="variant", values="RMSE"),
                          loso[loso.seed == s].set_index(["site", "horizon"]).RMSE, pers)) for s in SEEDS]
    sites = []
    for seed, w in tables:
        # skill tren tung o roi moi trung binh (persistence hang so trong tram)
        sk = (1 - w.drop(columns="persistence").div(w.persistence, axis=0)).stack().rename("skill")
        sk = sk.rename_axis(idx + ["variant"]).reset_index()
        for weeks, g in [("all", sk)] + list(sk.groupby("weeks")):
            sites.append(g.groupby(["variant", "site", "horizon"]).skill.mean().reset_index()
                         .assign(weeks=str(weeks), seed=seed))
    cells = med.rename_axis(columns="variant").stack().rename("RMSE").reset_index()
    skill = (1 - med.div(med.persistence, axis=0)).rename_axis(columns="variant").stack().rename("skill")
    cells = cells.merge(skill.reset_index(), on=idx + ["variant"], validate="1:1")
    pick = chosen.rename_axis(columns="variant").stack().rename("chosen").reset_index()
    cells = cells.merge(pick, on=idx + ["variant"], how="left", validate="1:1")
    key = ["role", "model", "ref", "metric", "horizon"]
    return tests[key + [c for c in tests if c not in key]], pd.concat(sites), cells


def _selftest():
    rng = np.random.default_rng(0)
    level = dict(finetune_free=1.0, finetune_cc=1.1, scratch_cc=1.6, ridge_cc=1.6, rf_cc=1.6, ridge_free=1.9, rf_free=2.0)
    oracle = {"1h": "scratch_cc", "3h": "ridge_cc", "6h": "rf_cc"}   # moi horizon mot doi chung thang
    frames = {}
    for f, (cal, modes) in FILES.items():
        rows = []
        for mode, s, w, k, seed, h in itertools.product(modes, SITES, WINDOWS, WEEKS, SEEDS, HORIZONS):
            v = mode + "_" + cal
            rows.append(dict(site=s, model="Mamba", mode=mode, window=w, weeks=k, seed=seed, horizon=h,
                             val_best=0.1 if v == "rf_cc" else 0.2,
                             RMSE=level[v] - 0.2 * (oracle[h] == v) + rng.uniform(0, 0.05)))
        d = pd.DataFrame(rows)
        r = d["mode"] == "ridge"   # ridge tat dinh: ba seed y het nhau
        d.loc[r, "RMSE"] = d[r].groupby(CELL + ["horizon"]).RMSE.transform("first")
        frames[f] = d
    loso = pd.DataFrame([dict(strategy=st, fold=s, test_site=s, model="Mamba", seed=k, horizon=h, RMSE=rng.uniform(1.2, 1.3))
                         for st in ("losoW", "globalW") for s in SITES for k in SEEDS for h in HORIZONS])
    base = pd.DataFrame([dict(site=s, model="persistence", horizon=h, RMSE=rng.uniform(1.7, 1.8))
                         for s in SITES for h in HORIZONS])
    tests, sites, cells = analyze(frames, loso, base)
    assert len(tests) == len(PAIRS) * 6 and (tests.role == "primary").sum() == 6
    t = tests[tests.model == "finetune_free"]
    assert (t.wins == 8).all() and np.allclose(t.p_raw, 2 / 2 ** 8) and np.allclose(t.p_holm, 6 / 2 ** 8)
    assert (tests[tests.model == "finetune_cc"].wins == 0).all()   # thua thi dau phai am
    c = cells[cells.variant == "best_test"]
    assert len(c) == 144 and (c.chosen == c.horizon.map(oracle)).all()
    c = cells[cells.variant == "best_val"]
    assert len(c) == 144 and (c.chosen == "rf_cc").all()
    assert (cells.chosen.notna() == cells.variant.isin(["best_test", "best_val"])).all()

    # tinh lai doc lap trung binh 6 o (skill va d_rmse)
    def rmse(f, mode, s, w, k, h):
        d = frames[f]
        return d[(d["mode"] == mode) & (d.site == s) & (d.window == w) & (d.weeks == k) & (d.horizon == h)].RMSE.median()
    sk, dr = [], []
    for s in SITES:
        ab = np.array([(rmse("fewshot8_ft_free.csv", "finetune", s, w, k, "3h"), rmse("fewshot8_cpu_cc.csv", "ridge", s, w, k, "3h"))
                       for w in WINDOWS for k in WEEKS])
        sk.append((1 - ab[:, 0] / ab[:, 1]).mean())
        dr.append((ab[:, 1] - ab[:, 0]).mean())
    for ref in ("best_test", "ridge_cc"):
        q = tests[(tests.model == "finetune_free") & (tests.ref == ref) & (tests.horizon == "3h")].set_index("metric")
        assert np.isclose(q.loc["skill", "mean"], np.mean(sk)) and np.isclose(q.loc["d_rmse", "mean"], np.mean(dr))
    p = base.set_index(["site", "horizon"]).RMSE
    g = sites[(sites.variant == "ridge_cc") & (sites.seed == "median") & (sites.weeks == "all")
              & (sites.site == "A") & (sites.horizon == "3h")].skill.item()
    want = np.mean([1 - rmse("fewshot8_cpu_cc.csv", "ridge", "A", w, k, "3h") / p["A", "3h"] for w in WINDOWS for k in WEEKS])
    assert np.isclose(g, want)
    z = loso[(loso.strategy == "losoW") & (loso.test_site == "B") & (loso.horizon == "6h")].RMSE.median()
    c = cells[(cells.variant == "zero_shot") & (cells.site == "B") & (cells.horizon == "6h")]
    assert len(c) == 6 and np.allclose(c.RMSE, z) and np.allclose(c.skill, 1 - z / p["B", "6h"])

    # thu tu dong trong file khong duoc anh huong ket qua
    mix = analyze({f: d.sample(frac=1, random_state=1) for f, d in frames.items()}, loso, base)
    pd.testing.assert_frame_equal(mix[0], tests)

    def edit(d, col, val):
        d = d.copy()
        d.loc[d.index[0], col] = val
        return d
    bad = [(frames, edit(loso, "fold", "H"), base), (frames, loso.drop(0), base), (frames, loso, base[1:]),
           (frames, pd.concat([loso, loso[:1]]), base), (frames, loso, pd.concat([base, base[:1]]))]
    for f, d in frames.items():
        for x in (d.drop(0), pd.concat([d, d[:1]]), d[d.site != "H"], d[d.seed != 2],
                  pd.concat([d, d[d.seed == 0].assign(seed=3)]), pd.concat([d, d[:3].assign(weeks=8)]),
                  pd.concat([d, d[:3].assign(mode="khac")]), edit(d, "model", "LSTM"), edit(d, "RMSE", np.nan),
                  edit(d, "val_best", np.nan), edit(d, "val_best", 9.0)):
            bad.append(({**frames, f: x}, loso, base))
    for b in bad:
        try:
            analyze(*b)
        except ValueError:
            continue
        raise AssertionError("du lieu thieu/hong ma khong bao loi")

    # dau vao thieu (dong hoac ca file) -> bao loi va khong ghi gi; du thi ghi dung 3 file
    cc = frames["fewshot8_cc.csv"]
    with tempfile.TemporaryDirectory() as tmp:
        for name, d in {**frames, "loso8_wind.csv": loso, "baselines.csv": base}.items():
            if name != "fewshot8_cc.csv":
                d.to_csv(os.path.join(tmp, name), index=False)
        for part, n_in in ((None, 5), (cc[:400], 6), (cc, 6)):
            if part is not None:
                part.to_csv(os.path.join(tmp, "fewshot8_cc.csv"), index=False)
            try:
                run(tmp)
                assert part is cc
            except (ValueError, FileNotFoundError):
                assert part is not cc
            assert len(os.listdir(tmp)) == n_in + 3 * (part is cc)
    print("selftest: dat")


def run(folder):
    """Phan tich xong het roi moi ghi."""
    def read(f):
        return pd.read_csv(os.path.join(folder, f))
    tests, sites, cells = analyze({f: read(f) for f in FILES}, read("loso8_wind.csv"), read("baselines.csv"))
    for name, df in (("stats", tests), ("per_site", sites), ("cells", cells)):
        df.to_csv(os.path.join(folder, "fewshot8_{}.csv".format(name)), index=False)
    return tests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        _selftest()
        return
    print(run(RESULTS).to_string(index=False, float_format=lambda x: "%.4f" % x))


if __name__ == "__main__":
    main()
