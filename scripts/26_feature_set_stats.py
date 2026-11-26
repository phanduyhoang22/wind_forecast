"""
Thong ke bo dac trung W (19 dac trung gio) vs 31 dac trung cho Mamba (RESULTS R22, R23; bai bao muc 2.6).

Doc results/runs.csv (Mamba 31, bo qua model khac), runs_wind.csv (Mamba W),
cross_eval_nn.csv (Mamba 31), cross_eval_wind.csv (Mamba W), baselines.csv (persistence)
va ghi results/feature_set_stats.csv.

Bien the dung (co dinh truoc, khong chinh de khop so):
- skill = 1 - RMSE_model / RMSE_persistence cua tram dich; persistence lay tu baselines.csv.
- Gop seed TRUOC: RMSE trung vi qua seed (R22: 5 seed; R23: 3 seed) roi moi tinh skill.
  R22 bao them bien the seed-mean (RMSE trung binh qua seed).
- R23: own = cap nguon = dich; same = 1 cap nguon cung vung khac tram (doi tac cua dich);
  cross = trung binh skill qua 6 nguon khac vung cua moi dich (trung voi 1 - mean RMSE / persistence
  vi cung mau so). Don vi kiem dinh = tram dich, n = 8.
- W-31 = skill_W - skill_31 (diem %) theo tung tram; same-cross = skill_same - skill_cross (W).
  "vs persistence" = kiem dinh skill so voi 0.
- Wilcoxon hang co dau, hai phia, p CHINH XAC (scipy method="exact"); khong cho phep hieu bang 0
  hay trung |hieu| (bao loi thay vi xu ly zero/tie). Holm tren 3 horizon trong moi
  (phan tich, bien the, dai luong).
- mean/median trong CSV la don vi ti le (0.01 = 1 diem %).

    py scripts/26_feature_set_stats.py
    py scripts/26_feature_set_stats.py --selftest
"""

import argparse
import importlib.util
import os

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
SITES = list("ABCDEFGH")
HORIZONS = ["1h", "3h", "6h"]


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ts = _load("ts", "22_transfer_stats.py")
holm, rank_biserial, check = ts.holm, ts.rank_biserial, ts.check


def test_values(x, **tag):
    """x: tram x horizon (hieu hoac skill) -> Wilcoxon chinh xac hai phia moi horizon, Holm qua 3 horizon."""
    rows = []
    for h in HORIZONS:
        v = x[h].to_numpy()
        # cung dieu kien voi compare() cua 22: p chinh xac chi dung khi khong co 0 hay trung hang
        if not np.isfinite(v).all() or (v == 0).any() or len(np.unique(np.abs(v))) < len(v):
            raise ValueError("gia tri NaN/0/trung hang, Wilcoxon khong chinh xac: {} {}".format(tag, h))
        rows.append(dict(tag, horizon=h, n=len(v), wins=int((v > 0).sum()), mean=v.mean(), median=np.median(v),
                         rank_biserial=rank_biserial(v),
                         p_raw=wilcoxon(v, alternative="two-sided", method="exact").pvalue))
    df = pd.DataFrame(rows)
    df["p_holm"] = holm(df.p_raw)
    return df


def own_site(r31, rw, pers, agg):
    """R22: skill tung tram (gop seed bang agg) cho W, 31 va hieu W-31."""
    s = {k: 1 - d.groupby(["site", "horizon"]).RMSE.agg(agg).unstack()[HORIZONS] / pers
         for k, d in (("W", rw), ("31", r31))}
    return [test_values(s["W"], analysis="own_site", variant=agg, quantity="skill_W"),
            test_values(s["31"], analysis="own_site", variant=agg, quantity="skill_31"),
            test_values(s["W"] - s["31"], analysis="own_site", variant=agg, quantity="W_minus_31")]


def regimes(c):
    """Cap nguon cung vung tu cot same_regime; moi dich phai co dung 2 nguon cung vung (ke ca chinh no)."""
    p = c.drop_duplicates(["source", "target"])
    same = p[p.same_regime.astype(bool)]
    if (same.groupby("target").size().reindex(SITES) != 2).any() or not (p.source == p.target).le(p.same_regime).all():
        raise ValueError("same_regime khong hop le")
    return set(zip(same.source, same.target))


def cross_site(cw, c31, pers):
    """R23: skill own / same / cross theo tram dich, seed trung vi."""
    out = {}
    pairs = None
    for k, c in (("W", cw), ("31", c31)):
        pr = regimes(c)
        if pairs is not None and pr != pairs:
            raise ValueError("same_regime khac nhau giua W va 31")
        pairs = pr
        m = c.groupby(["source", "target", "horizon"]).RMSE.median().reset_index()
        m["skill"] = 1 - m.RMSE / np.array([pers.loc[t, h] for t, h in zip(m.target, m.horizon)])
        grp = np.where(m.source == m.target, "own",
                       np.where([(s, t) in pairs for s, t in zip(m.source, m.target)], "same", "cross"))
        for g in ("own", "same", "cross"):
            out[g, k] = m[grp == g].groupby(["target", "horizon"]).skill.mean().unstack()[HORIZONS]
    res = [test_values(out[g, k], analysis="cross_site", variant="median", quantity="{}_{}".format(g, k))
           for g in ("own", "same", "cross") for k in ("W", "31")]
    res += [test_values(out[g, "W"] - out[g, "31"], analysis="cross_site", variant="median",
                        quantity=g + "_W_minus_31") for g in ("same", "cross")]
    res.append(test_values(out["same", "W"] - out["cross", "W"], analysis="cross_site", variant="median",
                           quantity="same_minus_cross_W"))
    return res


def analyze(r31, rw, c31, cw, base):
    base = base[base.model == "persistence"]
    check(base, ["site", "horizon"], [SITES, HORIZONS], "persistence")
    pers = base.pivot(index="site", columns="horizon", values="RMSE")[HORIZONS]
    r31, c31 = r31[r31.model == "Mamba"], c31[c31.model == "Mamba"]
    for d, name in ((r31, "runs 31"), (rw, "runs W")):
        check(d, ["site", "seed", "horizon"], [SITES, range(5), HORIZONS], name)
    for d, name in ((c31, "cross 31"), (cw, "cross W")):
        check(d, ["source", "target", "seed", "horizon"], [SITES, SITES, range(3), HORIZONS], name)
    res = own_site(r31, rw, pers, "median") + own_site(r31, rw, pers, "mean") + cross_site(cw, c31, pers)
    return pd.concat(res, ignore_index=True)


def _selftest():
    # p chinh xac: 8 hieu cung dau -> 2 / 2^8; mot hieu am o hang 1 -> W- = 1 -> p = 2 * 2 / 2^8
    x = np.arange(1.0, 9.0)
    assert np.isclose(wilcoxon(x, method="exact").pvalue, 2 / 256)
    assert np.isclose(wilcoxon(np.r_[-1.0, x[1:]], method="exact").pvalue, 4 / 256)
    # dem tay: n = 8, W- = 3, so tap con {1..8} co tong <= 3 la 5 -> p hai phia 2 * 5 / 256
    assert np.isclose(wilcoxon(np.r_[-1.0, -2.0, x[2:]], method="exact").pvalue, 10 / 256)
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
    assert np.allclose(holm([4 / 256, 2 / 256, 2 / 256]), [6 / 256] * 3)
    t = test_values(pd.DataFrame({h: x for h in HORIZONS}, index=SITES), q="t")
    assert (t.wins == 8).all() and np.allclose(t.p_holm, 6 / 256) and (t.rank_biserial == 1).all()
    for bad in (np.r_[0.0, x[1:]], np.r_[2.0, x[1:]], np.r_[-2.0, x[1:]]):
        try:
            test_values(pd.DataFrame({h: bad for h in HORIZONS}, index=SITES))
        except ValueError:
            continue
        raise AssertionError("0/trung hang ma khong bao loi")

    # du lieu gia: W kem 31 o moi tram -> own W_minus_31 am 8/8; cap cung vung = (A,B), (C,D), ...
    rng = np.random.default_rng(0)
    base = pd.DataFrame([dict(site=s, model="persistence", horizon=h, RMSE=2.0) for s in SITES for h in HORIZONS])
    runs = lambda off: pd.DataFrame([dict(site=s, model="Mamba", seed=k, horizon=h, RMSE=1 + off + rng.uniform(0, .2))
                                     for s in SITES for k in range(5) for h in HORIZONS])
    reg = {s: i // 2 for i, s in enumerate(SITES)}
    cross = lambda off: pd.DataFrame([dict(source=a, target=b, model="Mamba", seed=k, horizon=h,
                                           same_regime=reg[a] == reg[b],
                                           RMSE=(1 if a == b else 1.5 if reg[a] == reg[b] else 2.5) + off
                                           + rng.uniform(0, .1))
                                      for a in SITES for b in SITES for k in range(3) for h in HORIZONS])
    r31, rw, c31, cw = runs(0), runs(0.3), cross(0), cross(0.2)
    r = analyze(pd.concat([r31, r31.assign(model="LSTM")]), rw, c31, cw, base)
    assert len(r) == 3 * 6 + 3 * 9
    g = r.set_index(["analysis", "variant", "quantity", "horizon"]).sort_index()
    assert (g.loc[("own_site", "median", "W_minus_31"), "wins"] == 0).all()
    assert (g.loc[("cross_site", "median", "same_minus_cross_W"), "wins"] == 8).all()
    assert (g.loc[("cross_site", "median", "cross_W"), "wins"] == 0).all()
    for args in ((r31[1:], rw, c31, cw), (r31, rw, c31.assign(same_regime=False), cw),
                 (r31, rw, c31, cw.assign(same_regime=cw.source == cw.target))):
        try:
            analyze(*args, base)
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
    rd = lambda f: pd.read_csv(os.path.join(RESULTS, f))
    r = analyze(rd("runs.csv"), rd("runs_wind.csv"), rd("cross_eval_nn.csv"), rd("cross_eval_wind.csv"),
                rd("baselines.csv"))
    r.to_csv(os.path.join(RESULTS, "feature_set_stats.csv"), index=False)
    show = r.assign(mean_pct=100 * r["mean"])[["analysis", "variant", "quantity", "horizon", "n", "wins",
                                                "mean_pct", "rank_biserial", "p_raw", "p_holm"]]
    print(show.to_string(index=False, float_format=lambda x: "%.4f" % x))


if __name__ == "__main__":
    main()
