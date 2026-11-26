"""
Kiem tra SHAP da luu cua 10_shap.py (T04 vong 2): chi chay forward, KHONG chay lai SHAP.

Doc <results>/shap_<tag>_<tram>.npz + trong so, dung lai nen (background) seed 0 nhu 10. Ghi ra:
    shap_completeness.csv    sai so completeness theo horizon + "all" (dung dinh nghia gop cua 10)
    shap_net_importance.csv  mean |tong phi theo thoi gian| -> da tru phan triet tieu giua cac buoc
    shap_provenance.csv      f(x) (m/s) so voi du doan da luu cua 07/09 tai cung vi tri test;
                             07/09 luu tren GPU voi autocast fp16 -> lech nho la binh thuong

    py scripts/25_shap_check.py --results results
    py scripts/25_shap_check.py --selftest
"""

import argparse
import importlib.util
import json
import os
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SEED, N_BACKGROUND = 0, 200            # mac dinh cua 10_shap.py, dung cho ca T04a va T04b

# tag -> (bo dac trung, trong so, du doan da luu), duong dan tinh tu --results
TAGS = {
    "Mamba_0": ("all", "models/{}_Mamba_0.pt", "preds/{}_Mamba_0.npz"),
    "losoW8_Mamba_0": ("wind", "models_loso/losoW8_{}_Mamba_0.pt", "preds_loso/losoW8_{}_Mamba_0.npz"),
}
OUTS = ("shap_completeness.csv", "shap_net_importance.csv", "shap_provenance.csv")


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(ok, msg):
    if not ok:
        raise ValueError(msg)


def completeness(total, fx, fb):
    """|tong phi - (f(x) - E f(nen))| trung binh / |f(x) - E f(nen)| trung binh (giong 10)."""
    return float(np.abs(total - (fx - fb)).mean() / np.abs(fx - fb).mean())


def forward(model, x, dev, batch):
    import torch
    with torch.no_grad():
        return np.concatenate([model(torch.from_numpy(x[i:i + batch]).to(dev)).cpu().numpy()
                               for i in range(0, len(x), batch)])


def run_one(dp, mo, results, tag, site, cfg, dev, batch, data_dir):
    import torch

    feats, ckpt, pred = TAGS[tag]
    name = "{} {}".format(tag, site)
    d = dp.select_features(dp.load_site(site, data_dir), feats)
    H, labs = len(dp.HORIZONS), [l for _, l in dp.HORIZONS]
    with np.load(os.path.join(results, "shap_{}_{}.npz".format(tag, site))) as z:
        sv, x, idx = z["shap"].astype(np.float64), z["x"], z["idx"]
        features, horizons = [str(f) for f in z["features"]], [str(h) for h in z["horizons"]]

    check(features == list(d.features) and horizons == labs, name + ": features/horizons khong khop")
    check(sv.shape == (len(idx), d.seq_len, d.n_features, H), "{}: shape {}".format(name, sv.shape))
    check(np.isfinite(sv).all(), name + ": SHAP co NaN/inf")
    # Cung thu tu rut nhu 10; idx khop cung xac nhan seed va so mau nen
    rng = np.random.default_rng(SEED)
    bg_idx = np.sort(rng.choice(d.idx_train, N_BACKGROUND, replace=False))
    ex_idx = np.sort(rng.choice(d.idx_test, len(idx), replace=False))
    check(np.array_equal(idx, ex_idx), name + ": idx khong khop cach rut seed 0 cua 10_shap")
    check(np.array_equal(x, d.windows(idx)), name + ": x trong npz khac cua so du lieu tai idx")

    model = mo.build("Mamba", d.n_features, H, **cfg)
    model.load_state_dict(torch.load(os.path.join(results, ckpt.format(site)), map_location="cpu"))
    model.to(dev).eval()
    fx32 = forward(model, x, dev, batch)
    fx = fx32.astype(np.float64)
    fb = forward(model, d.windows(bg_idx), dev, batch).astype(np.float64).mean(0)
    check(np.isfinite(fx).all() and np.isfinite(fb).all(), name + ": f(x) co NaN/inf")

    total = sv.sum(axis=(1, 2))
    comp = [dict(tag=tag, site=site, horizon=lab, completeness_error=completeness(total[:, j], fx[:, j], fb[j]),
                 n=len(idx)) for j, lab in enumerate(labs)]
    comp.append(dict(tag=tag, site=site, horizon="all", completeness_error=completeness(total, fx, fb), n=len(idx)))

    net = np.abs(sv.sum(axis=1)).mean(axis=0)                         # (F, H)
    imp = []
    for j, lab in enumerate(labs):
        share = net[:, j] / net[:, j].sum()
        rank = (-net[:, j]).argsort().argsort() + 1
        imp += [dict(tag=tag, site=site, horizon=lab, feature=f, mean_abs_net=net[k, j],
                     share=share[k], rank=int(rank[k])) for k, f in enumerate(features)]

    prov = dict(tag=tag, site=site, pred_file=pred.format(site), status="missing", n=0,
                max_abs_diff_ms=np.nan, mean_abs_diff_ms=np.nan)
    path = os.path.join(results, pred.format(site))
    if os.path.exists(path):
        with np.load(path) as z:
            stored = z["y_pred"]
        check(stored.shape == (len(d.idx_test), H), "{}: du doan luu co shape {}".format(name, stored.shape))
        stored = stored[np.searchsorted(d.idx_test, idx)].astype(np.float64)
        check(np.isfinite(stored).all(), name + ": du doan luu co NaN/inf")
        diff = np.abs(d.scaler_y.inverse(fx32.reshape(-1, 1)).reshape(fx32.shape) - stored)
        prov.update(status="compared", n=len(idx), max_abs_diff_ms=diff.max(), mean_abs_diff_ms=diff.mean())
    return comp, imp, prov


def run(results, tags, sites, out_dir, tuned, dev, batch, data_dir=None):
    dp, mo = _load("dp", "04_data_pipeline.py"), _load("mo", "06_models.py")
    check(tags and set(tags) <= set(TAGS), "tag khong hop le: {}".format(tags))
    check(sites and set(sites) <= set(dp.SITES), "tram khong hop le: {}".format(sites))
    full = set(tags) == set(TAGS) and set(sites) == set(dp.SITES)
    for f in OUTS:                     # chay mot phan khong duoc de len bang day du
        check(full or not os.path.exists(os.path.join(out_dir, f)),
              "chay mot phan: {} da co trong {}, chon --out-dir khac".format(f, out_dir))
    need = [tuned] + [os.path.join(results, p) for t in tags for s in sites
                      for p in ("shap_{}_{}.npz".format(t, s), TAGS[t][1].format(s))]
    missing = [p for p in need if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError("thieu {} file:\n  {}".format(len(missing), "\n  ".join(missing)))
    with open(tuned) as f:
        cfg = json.load(f)["Mamba"]

    rows = ([], [], [])
    for tag in tags:
        for site in sites:
            c, i, p = run_one(dp, mo, results, tag, site, cfg, dev, batch, data_dir or dp.DATA_DIR)
            rows[0].extend(c)
            rows[1].extend(i)
            rows[2].append(p)
            print("{} {}  completeness {}  | provenance {} n={} max={:.2e} mean={:.2e} m/s".format(
                tag, site, " ".join("{}={:.3f}".format(r["horizon"], r["completeness_error"]) for r in c),
                p["status"], p["n"], p["max_abs_diff_ms"], p["mean_abs_diff_ms"]), flush=True)
    os.makedirs(out_dir, exist_ok=True)
    for f, r in zip(OUTS, rows):
        pd.DataFrame(r).to_csv(os.path.join(out_dir, f), index=False)
    n_miss = sum(p["status"] == "missing" for p in rows[2])
    print("Ghi vao {} ({} file du doan luu bi thieu)".format(out_dir, n_miss))


def selftest():
    import torch

    dp, mo = _load("dp", "04_data_pipeline.py"), _load("mo", "06_models.py")
    cfg, n, H = dict(dropout=0.1, lr=3e-4), 12, len(dp.HORIZONS)

    def fails(exc, fn):
        try:
            fn()
        except exc as e:
            return str(e)
        raise AssertionError("phai bao loi {}".format(exc.__name__))

    with tempfile.TemporaryDirectory() as tmp:
        res, cpu = os.path.join(tmp, "res"), torch.device("cpu")
        for sub in ("models", "models_loso", "preds", "preds_loso"):
            os.makedirs(os.path.join(res, sub))
        tuned = os.path.join(res, "tuned.json")
        with open(tuned, "w") as f:
            json.dump({"Mamba": cfg}, f)

        saved = {}
        for tag, (feats, ckpt, pred) in TAGS.items():
            d = dp.select_features(dp.load_site("A"), feats)
            torch.manual_seed(1)
            model = mo.build("Mamba", d.n_features, H, **cfg).eval()
            torch.save(model.state_dict(), os.path.join(res, ckpt.format("A")))
            rng = np.random.default_rng(0)
            bg = np.sort(rng.choice(d.idx_train, 200, replace=False))
            ex = np.sort(rng.choice(d.idx_test, n, replace=False))
            with torch.no_grad():
                fx = model(torch.from_numpy(d.windows(ex))).numpy()
                fb = model(torch.from_numpy(d.windows(bg))).numpy().astype(np.float64).mean(0)
            # Attribution biet truoc: dac trung 0 nhan 3/4 do lech, dac trung 1 nhan 1/4;
            # dac trung 2 triet tieu theo thoi gian (+5, -5) -> net phai = 0
            sv = np.zeros((n, d.seq_len, d.n_features, H))
            sv[:, :, 0] = 0.75 * (fx - fb)[:, None] / d.seq_len
            sv[:, :, 1] = 0.25 * (fx - fb)[:, None] / d.seq_len
            sv[:, 0, 2], sv[:, 1, 2] = 5, -5
            saved[tag] = dict(x=d.windows(ex), idx=ex, features=np.array(d.features),
                              horizons=np.array([l for _, l in dp.HORIZONS])), sv, fx - fb
            stored = np.full((len(d.idx_test), H), np.nan, np.float32)   # chi vi tri idx moi hop le
            stored[ex - d.idx_test[0]] = d.scaler_y.inverse(fx) + 0.25   # lech biet truoc 0.25 m/s
            np.savez(os.path.join(res, pred.format("A")), y_pred=stored)

        def write(tag, sv=None, **kw):
            z, sv0, _ = saved[tag]
            np.savez(os.path.join(res, "shap_{}_A.npz".format(tag)),
                     **{**z, "shap": (sv0 if sv is None else sv).astype(np.float32), **kw})

        def go(out, tags=tuple(TAGS), sites=("A",)):
            run(res, tags, sites, os.path.join(tmp, out), tuned, cpu, 5)
            return [pd.read_csv(os.path.join(tmp, out, f)) for f in OUTS]

        def rejects(exc):
            msg = fails(exc, lambda: go("bad"))
            assert not os.path.exists(os.path.join(tmp, "bad")), "loi ma van ghi file"
            return msg

        for tag in TAGS:
            write(tag)
        comp, imp, prov = go("ok")
        assert len(comp) == 2 * (H + 1) and set(comp.horizon) == {"1h", "3h", "6h", "all"} and (comp.n == n).all()
        assert (comp.completeness_error < 1e-4).all(), comp
        assert len(imp) == H * (31 + 19)
        for (tag, _, lab), g in imp.groupby(["tag", "site", "horizon"]):
            z, _, dev = saved[tag]
            g = g.set_index("feature").loc[z["features"]]
            assert np.allclose(g["share"].iloc[:3], [0.75, 0.25, 0], atol=1e-4) and list(g["rank"].iloc[:2]) == [1, 2]
            want = 0.75 * np.abs(dev[:, list(z["horizons"]).index(lab)]).mean()
            assert np.isclose(g.mean_abs_net.iloc[0], want, rtol=1e-4)
        assert (prov.status == "compared").all() and (prov.n == n).all()
        assert np.allclose(prov[["max_abs_diff_ms", "mean_abs_diff_ms"]], 0.25, atol=1e-4)

        # Nhieu: chi horizon 0 bi nhan 1.1 -> sai so 0.1 o do, 0 o cac horizon khac,
        # "all" theo dung dinh nghia gop (ti so cua trung binh, khong phai trung binh cua ti so)
        tag = "Mamba_0"
        bad = saved[tag][1].copy()
        bad[:, :, :2, 0] *= 1.1
        write(tag, bad)
        e = go("pert", (tag,))[0].set_index("horizon").completeness_error
        dev = np.abs(saved[tag][2])
        assert np.allclose(e[["1h", "3h", "6h"]], [0.1, 0, 0], atol=1e-4)
        assert np.isclose(e["all"], 0.1 * dev[:, 0].sum() / dev.sum(), atol=1e-5)

        # Dau vao sai -> bao loi, khong ghi gi
        z = saved[tag][0]
        write(tag, x=z["x"] + 1e-3)
        assert "x trong npz" in rejects(ValueError)
        write(tag, idx=z["idx"] + 1)
        assert "idx" in rejects(ValueError)
        write(tag, features=z["features"][::-1])
        assert "features" in rejects(ValueError)
        nan = saved[tag][1].copy()
        nan[0, 0, 0, 0] = np.nan
        write(tag, nan)
        assert "NaN" in rejects(ValueError)
        write(tag)
        for rel in ("shap_{}_A.npz".format(tag), "models_loso/losoW8_A_Mamba_0.pt", "tuned.json"):
            p = os.path.join(res, rel)
            os.rename(p, p + ".bak")
            assert os.path.basename(p) in rejects(FileNotFoundError)
            os.rename(p + ".bak", p)
        # Chay mot phan khong de len ket qua da co
        assert "mot phan" in fails(ValueError, lambda: go("ok"))

        os.remove(os.path.join(res, TAGS[tag][2].format("A")))
        prov = go("nopred")[2].set_index("tag")
        assert list(prov.loc[[tag, "losoW8_Mamba_0"], "status"]) == ["missing", "compared"]
        assert prov.loc[tag, "n"] == 0 and np.isnan(prov.loc[tag, "max_abs_diff_ms"])
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(os.path.dirname(HERE), "results"))
    ap.add_argument("--sites", default="A,B,C,D,E,F,G,H")
    ap.add_argument("--tags", default=",".join(TAGS))
    ap.add_argument("--out-dir", default=None, help="mac dinh = --results")
    ap.add_argument("--tuned", default=None, help="mac dinh <results>/tuned.json (Drive khong dong bo file nay)")
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--device", default=None)
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    import torch
    dev = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    run(args.results, [t.strip() for t in args.tags.split(",")],
        [s.strip().upper() for s in args.sites.split(",")], args.out_dir or args.results,
        args.tuned or os.path.join(args.results, "tuned.json"), dev, args.batch, args.data_dir)


if __name__ == "__main__":
    main()
