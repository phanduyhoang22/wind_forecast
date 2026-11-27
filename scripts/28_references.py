"""
T23 (hop M20): hai muc tham chieu manh hon persistence, khong hoc may.

  P1 smart persistence : y_hat(t+h) = trung binh N buoc wind_speed cuoi, N thuoc NS, chon tren val
  P2 blend (Nielsen et al. 1998): y_hat = a_h * ws(t) + (1 - a_h) * mu; mu, a_h chi tu train

E1   : theo tram; N chon tren val cua chinh tram, mu / a_h tu train cua tram.
LOSO : 8 fold; N chon tren val GOP cua 7 tram nguon, mu / a_h tu train gop cua tram nguon.
       Tram dich chi dung tap test de cham (khong mot so nao cua tram dich vao viec chon).

Rat nhanh (vai giay/tram) nen moi lan chay tinh lai toan bo va ghi de results/references.csv.

    py scripts/28_references.py
    py scripts/28_references.py --selftest
"""

import argparse
import importlib.util
import os
from types import SimpleNamespace

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
NS = [1, 2, 4, 8, 16, 32, 48, 96]            # tang dan: hoa -> giu N nho hon


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dp = _load("dp", "04_data_pipeline.py")


def ws_raw(d):
    """wind_speed (m/s, float32) doi nguoc dung nhu persistence() cua 04."""
    c = d.features.index(dp.TARGET)
    return d.scaler_y.inverse(d.X[:, c].reshape(-1, 1)).ravel()


def smart_pers(ws, idx, n):
    """Trung binh ws[t-n+1 .. t] voi moi t trong idx. n <= SEQ_LEN nen chi dung du lieu
    trong cua so dau vao cua t (khong vuot ranh gioi split, khong nhin tuong lai)."""
    assert 1 <= n <= dp.SEQ_LEN
    c = np.concatenate([[0.0], np.cumsum(ws, dtype=np.float64)])
    return ((c[idx + 1] - c[idx + 1 - n]) / n).astype(np.float32)


def choose_n(data, j):
    """N co MSE val (m/s) nho nhat, gop moi tram trong data = [(SiteData, ws)].
    Chi dung idx_val -> khong cham train lan test."""
    sse = {n: sum(float(np.sum((d.y_raw[d.idx_val, j] - smart_pers(w, d.idx_val, n)) ** 2)) for d, w in data)
           for n in NS}
    n_val = sum(len(d.idx_val) for d, _ in data)
    best = min(NS, key=sse.get)
    return best, float(np.sqrt(sse[best] / n_val))


def blend_params(data, j):
    """mu = trung binh ws tren train (nhu climatology() cua 04); a_h = tu tuong quan tre h
    tren cap (ws(t), ws(t+h)), t thuoc idx_train (t + MAX_H van trong train). Cap chi trong tung tram."""
    x = np.concatenate([w[d.idx_train] for d, w in data]).astype(np.float64)
    y = np.concatenate([d.y_raw[d.idx_train, j] for d, _ in data]).astype(np.float64)
    mu = x.mean()
    return float(np.sum((x - mu) * (y - mu)) / np.sum((x - mu) ** 2)), float(mu)


def evaluate(src, target, setting, fold):
    """src: [(SiteData, ws)] de chon/uoc tham so; target: (SiteData, ws) de cham test."""
    d, w = target
    idx = d.idx_test
    H = len(dp.HORIZONS)
    p1, p2 = np.empty((len(idx), H), np.float32), np.empty((len(idx), H), np.float32)
    par = []
    for j in range(H):
        n, v = choose_n(src, j)
        a, mu = blend_params(src, j)
        p1[:, j] = smart_pers(w, idx, n)
        p2[:, j] = (a * w[idx] + (1 - a) * mu).astype(np.float32)
        par.append((n, v, a, mu))
    rows = []
    for model, p in (("SmartPersistence", p1), ("Blend", p2)):
        for j, (h, r) in enumerate(dp.metrics(d.y_raw[idx], p).iterrows()):
            n, v, a, mu = par[j]
            extra = dict(N=n, val_rmse=v) if model == "SmartPersistence" else dict(a_h=a, mu=mu)
            rows.append(dict(setting=setting, fold=fold, test_site=d.site, model=model, horizon=h,
                             **extra, **r.to_dict()))
    return rows


def run(sites):
    data = {s: dp.load_site(s) for s in sites}
    data = {s: (d, ws_raw(d)) for s, d in data.items()}
    rows = []
    for s in sites:
        rows += evaluate([data[s]], data[s], "E1", s)
    if len(sites) > 1:
        for s in sites:
            src = [data[x] for x in sites if x != s]
            assert all(d.site != s for d, _ in src), "tram dich lot vao tram nguon"
            rows += evaluate(src, data[s], "losoW", s)
    return pd.DataFrame(rows), data


def check_split(d):
    """Cua so + nhan cua train ket thuc truoc khi cua so val bat dau; val truoc test."""
    for a, b in ((d.idx_train, d.idx_val), (d.idx_val, d.idx_test)):
        assert a.max() + dp.MAX_H < b.min() - dp.SEQ_LEN + 1, "split khong purged"


def _selftest():
    rng = np.random.default_rng(0)
    # 1) trung binh truot dung, khong nhin tuong lai
    ws = rng.uniform(0, 20, 400).astype(np.float32)
    idx = np.arange(dp.SEQ_LEN - 1, 300)
    for n in NS:
        ref = np.array([ws[t - n + 1: t + 1].mean() for t in idx])
        assert np.allclose(smart_pers(ws, idx, n), ref, atol=1e-4), n
        ws2 = ws.copy()
        ws2[idx[50] + 1:] += 100                              # doi tuong lai -> du doan tai t khong doi
        assert np.array_equal(smart_pers(ws2, idx[:51], n), smart_pers(ws, idx[:51], n))
    # 2) AR(1) phi: a_h ~ phi^h; mu ~ trung binh; val khong anh huong a_h, mu
    phi, N = 0.95, 200_000
    x = np.empty(N)
    x[0] = 0
    e = rng.normal(size=N)
    for t in range(1, N):
        x[t] = phi * x[t - 1] + e[t]
    x = (x + 10).astype(np.float32)
    ks = [k for k, _ in dp.HORIZONS]
    y_raw = np.stack([np.r_[x[k:], np.full(k, np.nan, np.float32)] for k in ks], 1)
    fake = SimpleNamespace(idx_train=np.arange(dp.SEQ_LEN, N // 2), idx_val=np.arange(N // 2 + 200, N - 100),
                           y_raw=y_raw)
    for j, k in enumerate(ks):
        a, mu = blend_params([(fake, x)], j)
        assert abs(a - phi ** k) < 0.03 and abs(mu - 10) < 0.5, (k, a, mu)
        y2 = y_raw.copy()
        y2[fake.idx_val] += 50
        assert blend_params([(SimpleNamespace(**{**vars(fake), "y_raw": y2}), x)], j) == (a, mu)
    # 3) du lieu that: split purged; P1 N=1 tai lai persistence cua results/baselines.csv (< 1e-6 m/s)
    base = pd.read_csv(os.path.join(RESULTS, "baselines.csv"))
    pers = base[base.model == "persistence"].set_index(["site", "horizon"]).RMSE
    worst = 0.0
    for s in dp.SITES:
        d = dp.load_site(s)
        check_split(d)
        w = ws_raw(d)
        m = dp.metrics(d.y_raw[d.idx_test], np.repeat(smart_pers(w, d.idx_test, 1)[:, None], 3, 1))
        for h, r in m.iterrows():
            worst = max(worst, abs(r.RMSE - pers[(s, h)]))
    assert worst < 1e-6, worst
    print("selftest: dat (N=1 vs baselines.csv: lech max {:.2e} m/s)".format(worst))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sites", default=",".join(dp.SITES))
    ap.add_argument("--out", default=os.path.join(RESULTS, "references.csv"))
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    sites = [s.strip().upper() for s in args.sites.split(",")]
    df, _ = run(sites)
    df.to_csv(args.out, index=False)
    f4 = lambda x: "%.4f" % x
    for st, g in df.groupby("setting", sort=False):
        print("\n{} RMSE (m/s, test):".format(st))
        print(g.pivot_table(index=["test_site", "horizon"], columns="model", values="RMSE").to_string(float_format=f4))
        print("N chon (P1):", g[g.model == "SmartPersistence"].pivot(index="test_site", columns="horizon", values="N")
              .to_dict("index"))
    print("\nGhi vao", args.out)


if __name__ == "__main__":
    main()
