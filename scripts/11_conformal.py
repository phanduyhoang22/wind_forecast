"""
Khoang du bao bang split conformal prediction.

Hieu chinh tren tap val (|y - y_hat| cua val), ap len tap test:
    q = luong tu muc ceil((n+1)(1-alpha))/n cua phan du val
    khoang = y_hat +- q
Chi so: PICP (ty le phu, muc tieu 1-alpha), PINAW (do rong / bien do y test),
va PICP theo 3 khoang toc do gio (thap/trung/cao) de thay do phu co deu khong.

Luu y phuong phap: chuoi thoi gian khong trao doi duoc (exchangeable), nen do phu
danh nghia khong duoc dam bao -- day chinh la dieu bang PICP kiem tra.

Can results/preds/<tram>_<model>_<seed>.npz va results/models/<...>_val.npz tu 07.

    py scripts/11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear
    py scripts/11_conformal.py --selftest
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


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def conformal_q(resid, alpha):
    n = len(resid)
    level = min(1.0, math.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(resid, level, method="higher"))


def evaluate(y_val, p_val, y_te, p_te, alpha):
    q = conformal_q(np.abs(y_val - p_val), alpha)
    inside = np.abs(y_te - p_te) <= q
    out = dict(q=q, PICP=float(inside.mean()), PINAW=float(2 * q / (y_te.max() - y_te.min())))
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
    r = evaluate(y[:10000], p[:10000], y[10000:], p[10000:], 0.1)
    assert abs(r["PICP"] - 0.9) < 0.01, r
    print("selftest conformal: PICP = {:.3f} (muc tieu 0.900) -> dat".format(r["PICP"]))


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
    rows = []
    for site in dp.SITES:
        d = dp.load_site(site)
        y_val, y_te = d.y_raw[d.idx_val], d.y_raw[d.idx_test]
        for model in [m.strip() for m in args.models.split(",")]:
            for vf in sorted(glob.glob(os.path.join(RESULTS, "models", "{}_{}_*_val.npz".format(site, model)))):
                seed = int(os.path.basename(vf).split("_")[2])
                tf = os.path.join(RESULTS, "preds", "{}_{}_{}.npz".format(site, model, seed))
                if not os.path.exists(tf):
                    continue
                pv, pt = np.load(vf)["y_pred"], np.load(tf)["y_pred"]
                assert pv.shape == y_val.shape and pt.shape == y_te.shape
                for a in alphas:
                    for j, (_, lab) in enumerate(dp.HORIZONS):
                        rows.append(dict(site=site, model=model, seed=seed, horizon=lab, nominal=1 - a,
                                         **evaluate(y_val[:, j], pv[:, j], y_te[:, j], pt[:, j], a)))
    df = pd.DataFrame(rows)
    if not len(df):
        print("Chua co du doan val (models/*_val.npz) -> chay 07 ban moi truoc")
        return
    df.to_csv(os.path.join(RESULTS, "conformal.csv"), index=False)
    agg = df.groupby(["model", "site", "horizon", "nominal"])[
        ["PICP", "PINAW", "PICP_low", "PICP_mid", "PICP_high"]].mean()
    print(agg.to_string(float_format=lambda x: "%.3f" % x))


if __name__ == "__main__":
    main()
