"""
Khoang du bao bang split conformal prediction.

Hieu chinh tren tap val (|y - y_hat| cua val), ap len tap test:
    q = phan du val thu k = ceil((n+1)(1-alpha)) sau khi sap xep tang (k > n -> lon nhat)
    khoang = y_hat +- q
Chi so: PICP (ty le phu, muc tieu 1-alpha), PINAW (do rong / bien do y TRAIN theo
tung horizon -- khong dung bien do test de mau so khong phu thuoc tap danh gia),
va PICP theo 3 khoang toc do gio (thap/trung/cao) de thay do phu co deu khong.

Luu y phuong phap: chuoi thoi gian khong trao doi duoc (exchangeable), nen do phu
danh nghia khong duoc dam bao -- day chinh la dieu bang PICP kiem tra.

Can results/preds/<tram>_<model>_<seed>.npz va results/models/<...>_val.npz tu 07.

    py scripts/11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear
    py scripts/11_conformal.py --selftest
"""

import argparse
import importlib.util
import math
import os
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SEEDS = range(5)


def conformal_q(resid, alpha):
    # Lay dung phan tu thu k (khong noi suy) -- np.quantile "higher" lech 1 bac o mot so n
    r = np.sort(np.asarray(resid))
    n = len(r)
    k = math.ceil((n + 1) * (1 - alpha))
    return float(r[min(k, n) - 1])


def missing_pairs(results, sites, models, seeds=SEEDS):
    """Moi cap (tram, model, seed) phai co ca du doan val lan test; tra ve file thieu."""
    miss = []
    for site in sites:
        for model in models:
            for seed in seeds:
                for f in (os.path.join(results, "models", "{}_{}_{}_val.npz".format(site, model, seed)),
                          os.path.join(results, "preds", "{}_{}_{}.npz".format(site, model, seed))):
                    if not os.path.exists(f):
                        miss.append(f)
    return miss


def evaluate(y_val, p_val, y_te, p_te, alpha, y_range):
    q = conformal_q(np.abs(y_val - p_val), alpha)
    inside = np.abs(y_te - p_te) <= q
    out = dict(q=q, PICP=float(inside.mean()), PINAW=float(2 * q / y_range))
    cuts = np.quantile(y_te, [1 / 3, 2 / 3])
    for name, sel in (("PICP_low", y_te <= cuts[0]),
                      ("PICP_mid", (y_te > cuts[0]) & (y_te <= cuts[1])),
                      ("PICP_high", y_te > cuts[1])):
        out[name] = float(inside[sel].mean())
    return out


def _selftest():
    rng = np.random.default_rng(0)
    y = rng.normal(size=20000)
    p = y + rng.normal(scale=0.3, size=20000)
    r = evaluate(y[:10000], p[:10000], y[10000:], p[10000:], 0.1, 10.0)
    assert abs(r["PICP"] - 0.9) < 0.01, r
    print("selftest conformal: PICP = {:.3f} (muc tieu 0.900) -> dat".format(r["PICP"]))

    # n = 19, alpha 0.1 -> k = ceil(20*0.9) = 18 -> q = phan du thu 18 = 18
    assert conformal_q(np.arange(19, 0, -1.0), 0.1) == 18.0
    assert conformal_q(np.arange(1, 20.0), 0.01) == 19.0          # k > n -> lon nhat
    # PINAW dung bien do truyen vao, khong phai bien do y test
    r = evaluate(np.zeros(19), -np.arange(1, 20.0), np.arange(6.0), np.zeros(6), 0.1, 4.0)
    assert r["q"] == 18.0 and r["PINAW"] == 2 * 18.0 / 4.0, r
    print("selftest conformal: q(1..19, alpha 0.1) = 18, PINAW theo bien do train -> dat")

    # Thieu file -> liet ke dung tung file thieu
    with tempfile.TemporaryDirectory() as tmp:
        for sub, name in (("models", "A_RF_0_val.npz"), ("preds", "A_RF_0.npz"), ("preds", "A_RF_1.npz")):
            os.makedirs(os.path.join(tmp, sub), exist_ok=True)
            open(os.path.join(tmp, sub, name), "w").close()
        miss = missing_pairs(tmp, ["A"], ["RF"], range(3))
        assert sorted(os.path.relpath(f, tmp) for f in miss) == sorted(
            [os.path.join("models", "A_RF_1_val.npz"), os.path.join("models", "A_RF_2_val.npz"),
             os.path.join("preds", "A_RF_2.npz")]), miss
        assert missing_pairs(tmp, ["A"], ["RF"], range(1)) == []
    print("selftest conformal: liet ke cap (tram, model, seed) thieu -> dat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="Mamba")
    ap.add_argument("--alphas", default="0.1,0.05")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return

    dp = _load("dp", "04_data_pipeline.py")
    alphas = [float(a) for a in args.alphas.split(",")]
    models = [m.strip() for m in args.models.split(",")]
    # Thieu bat ky cap nao -> dung, khong ghi gi (tranh conformal.csv thieu dong ma khong ai biet)
    miss = missing_pairs(RESULTS, list(dp.SITES), models)
    if miss:
        for f in miss:
            print("THIEU:", f)
        print("Thieu {} file du doan -> khong ghi conformal.csv".format(len(miss)))
        sys.exit(1)
    rows = []
    for site in dp.SITES:
        d = dp.load_site(site)
        y_val, y_te = d.y_raw[d.idx_val], d.y_raw[d.idx_test]
        y_tr = d.y_raw[d.idx_train]
        for model in models:
            for seed in SEEDS:
                vf = os.path.join(RESULTS, "models", "{}_{}_{}_val.npz".format(site, model, seed))
                tf = os.path.join(RESULTS, "preds", "{}_{}_{}.npz".format(site, model, seed))
                pv, pt = np.load(vf)["y_pred"], np.load(tf)["y_pred"]
                assert pv.shape == y_val.shape and pt.shape == y_te.shape
                for a in alphas:
                    for j, (_, lab) in enumerate(dp.HORIZONS):
                        rng_tr = float(y_tr[:, j].max() - y_tr[:, j].min())
                        rows.append(dict(site=site, model=model, seed=seed, horizon=lab, nominal=1 - a,
                                         **evaluate(y_val[:, j], pv[:, j], y_te[:, j], pt[:, j], a, rng_tr)))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RESULTS, "conformal.csv"), index=False)
    agg = df.groupby(["model", "site", "horizon", "nominal"])[
        ["PICP", "PINAW", "PICP_low", "PICP_mid", "PICP_high"]].mean()
    print(agg.to_string(float_format=lambda x: "%.3f" % x))


if __name__ == "__main__":
    main()
