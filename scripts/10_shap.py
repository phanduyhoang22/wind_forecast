"""
Giai thich Mamba bang SHAP (GradientExplainer = expected gradients).

Voi moi tram, nap trong so Mamba da train o 07 (results/models/<tram>_Mamba_<seed>.pt),
giai thich N cua so test ngau nhien so voi nen la cua so train ngau nhien.

Gia tri SHAP co dang (mau, 96 buoc, 30 dac trung, 3 horizon). Ghi ra:
    results/shap_importance.csv   mean|SHAP| gop qua thoi gian -> xep hang dac trung
                                  theo tram x horizon (+ nhom dac trung vat ly)
    results/shap_temporal.csv     mean|SHAP| gop qua dac trung -> do quan trong theo
                                  do tre (buoc 0 = hien tai, 95 = 24 gio truoc)
    results/shap_<tram>.npz       mang day du de ve hinh

    py scripts/10_shap.py --sites A,B,C,D --n-explain 1000 --n-background 200
"""

import argparse
import importlib.util
import os
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")

# Nhom dac trung de doc ket qua theo co che vat ly, khong chi theo ten cot
GROUPS = {
    "wind_speed": "quan tinh", "ws_lag_15min": "quan tinh", "ws_lag_1h": "quan tinh",
    "ws_lag_3h": "quan tinh", "ws_lag_6h": "quan tinh", "ws_lag_24h": "quan tinh",
    "ws_rolling_mean_1h": "quan tinh", "ws_rolling_std_1h": "quan tinh",
    "ws_rolling_mean_6h": "quan tinh", "ws_delta": "quan tinh", "ws_delta_1h": "quan tinh",
    "ws_10m": "trac dien gio", "ws_80m": "trac dien gio", "ws_120m": "trac dien gio",
    "ws_200m": "trac dien gio", "shear_alpha": "trac dien gio",
    "shear_alpha_wide": "trac dien gio", "veer_120_80": "trac dien gio",
    "wind_sin": "huong gio", "wind_cos": "huong gio", "u_wind": "huong gio", "v_wind": "huong gio",
    "temperature": "nhiet dong luc", "pressure": "nhiet dong luc", "air_density": "nhiet dong luc",
    "dT_10_100": "nhiet dong luc", "dP_0_200": "nhiet dong luc",
    "hr_sin": "chu ky", "hr_cos": "chu ky", "month_sin": "chu ky", "month_cos": "chu ky",
}


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def as_array(sv, n_out):
    """shap tra ve list theo output (ban cu) hoac mang (..., H) (ban moi)."""
    if isinstance(sv, list):
        return np.stack(sv, axis=-1)
    sv = np.asarray(sv)
    return sv if sv.shape[-1] == n_out else sv[..., None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="A,B,C,D")
    ap.add_argument("--model", default="Mamba")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-explain", type=int, default=1000)
    ap.add_argument("--n-background", type=int, default=200)
    ap.add_argument("--nsamples", type=int, default=200, help="so mau tich phan / mau giai thich")
    ap.add_argument("--batch", type=int, default=50)
    ap.add_argument("--models-dir", default=os.path.join(RESULTS, "models"))
    ap.add_argument("--out-dir", default=RESULTS)
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    import shap
    import torch

    dp = _load("dp", "04_data_pipeline.py")
    mo = _load("mo", "06_models.py")
    dev = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    H = len(dp.HORIZONS)
    labs = [l for _, l in dp.HORIZONS]

    imp_rows, tmp_rows = [], []
    for site in [s.strip().upper() for s in args.sites.split(",")]:
        path = os.path.join(args.models_dir, "{}_{}_{}.pt".format(site, args.model, args.seed))
        if not os.path.exists(path):
            print(site, "-> thieu", path, ", bo qua")
            continue
        d = dp.load_site(site)
        model = mo.build(args.model, d.n_features, H)
        model.load_state_dict(torch.load(path, map_location="cpu"))
        model.to(dev).eval()

        rng = np.random.default_rng(args.seed)
        bg_idx = np.sort(rng.choice(d.idx_train, args.n_background, replace=False))
        ex_idx = np.sort(rng.choice(d.idx_test, args.n_explain, replace=False))
        bg = torch.from_numpy(d.windows(bg_idx)).to(dev)
        ex = d.windows(ex_idx)

        t0 = time.time()
        expl = shap.GradientExplainer(model, bg, batch_size=args.batch)
        parts = []
        for i in range(0, len(ex), args.batch):
            xb = torch.from_numpy(ex[i:i + args.batch]).to(dev)
            parts.append(as_array(expl.shap_values(xb, nsamples=args.nsamples,
                                                   rseed=args.seed + i), H))
        sv = np.concatenate(parts)                                    # (n, L, F, H)
        assert sv.shape == (len(ex), d.seq_len, d.n_features, H), sv.shape

        # Kiem tra tinh day du (completeness): tong SHAP ~ f(x) - E[f(nen)].
        # Expected gradients chi xap xi -> chi bao cao sai so, khong dung lai.
        with torch.no_grad():
            fx = model(torch.from_numpy(ex).to(dev)).cpu().numpy()
            fb = model(bg).cpu().numpy().mean(0)
        gap = np.abs(sv.sum(axis=(1, 2)) - (fx - fb)).mean() / np.abs(fx - fb).mean()
        print("{}  {:.0f}s  completeness error (tuong doi) = {:.3f}".format(
            site, time.time() - t0, gap), flush=True)

        absv = np.abs(sv)
        feat = absv.mean(axis=(0, 1))                                 # (F, H)
        temporal = absv.mean(axis=(0, 2))                             # (L, H)
        for j, lab in enumerate(labs):
            share = feat[:, j] / feat[:, j].sum()
            rank = (-feat[:, j]).argsort().argsort() + 1
            for f, name in enumerate(d.features):
                imp_rows.append(dict(site=site, horizon=lab, feature=name,
                                     group=GROUPS.get(name, "khac"), mean_abs_shap=feat[f, j],
                                     share=share[f], rank=int(rank[f])))
            for t in range(d.seq_len):
                tmp_rows.append(dict(site=site, horizon=lab, lag_steps=d.seq_len - 1 - t,
                                     mean_abs_shap=temporal[t, j]))
        np.savez_compressed(os.path.join(args.out_dir, "shap_{}.npz".format(site)),
                            shap=sv.astype(np.float32), x=ex.astype(np.float32),
                            idx=ex_idx, features=np.array(d.features), horizons=np.array(labs))

        top = pd.DataFrame([r for r in imp_rows if r["site"] == site])
        for lab in labs:
            t5 = top[top.horizon == lab].nsmallest(5, "rank")
            print("   {}  top5: {}".format(lab, ", ".join(
                "{} {:.0%}".format(r.feature, r.share) for r in t5.itertuples())))

    imp = pd.DataFrame(imp_rows)
    if len(imp):
        imp.to_csv(os.path.join(args.out_dir, "shap_importance.csv"), index=False)
        pd.DataFrame(tmp_rows).to_csv(os.path.join(args.out_dir, "shap_temporal.csv"), index=False)
        print("\nTy trong theo nhom vat ly (tram x horizon):")
        print(imp.pivot_table(index=["site", "horizon"], columns="group", values="share", aggfunc="sum")
              .to_string(float_format=lambda x: "%.0f%%" % (100 * x)))


if __name__ == "__main__":
    main()
