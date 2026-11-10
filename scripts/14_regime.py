"""
Phan tich theo che do gio (hop #2) -- hau kiem tren du doan da luu, khong train lai.

Tach tap test (04-12/2021, thieu loi gio mua Dong Bac thang 1-3) theo:
    mua    : gio mua Tay Nam (5-9), chuyen mua (4, 10), dau Dong Bac (11-12)
    ngay   : thoi diem phat du bao 06:00-17:59 gio dia phuong = ngay, con lai = dem
    ramp   : |v(t+h) - v(t)| thuoc 5% lon nhat (theo tram x horizon) = ramp
Voi moi tram x model x horizon x che do: RMSE trung binh qua seed (mo hinh don)
va skill so voi persistence trong cung che do.

    py scripts/14_regime.py
"""

import glob
import importlib.util
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
SEASON = {4: "chuyen mua", 5: "TN", 6: "TN", 7: "TN", 8: "TN", 9: "TN", 10: "chuyen mua",
          11: "dau DB", 12: "dau DB", 1: "DB", 2: "DB", 3: "DB"}


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rmse(e):
    return float(np.sqrt(np.mean(e ** 2))) if len(e) else np.nan


def main():
    dp = _load("dp", "04_data_pipeline.py")
    rows = []
    for site in dp.SITES:
        d = dp.load_site(site)
        y = d.y_raw[d.idx_test]
        ws = d.features.index(dp.TARGET)
        now = d.scaler_y.inverse(d.X[d.idx_test, ws].reshape(-1, 1)).ravel()
        t = d.time[d.idx_test]
        groups = {"mua": np.array([SEASON[m] for m in t.month]),
                  "ngay_dem": np.where((t.hour >= 6) & (t.hour < 18), "ngay", "dem")}
        preds = {"persistence": [np.repeat(now[:, None], len(dp.HORIZONS), axis=1)]}
        for f in sorted(glob.glob(os.path.join(RESULTS, "preds", "{}_*.npz".format(site)))):
            preds.setdefault(os.path.basename(f).split("_")[1], []).append(np.load(f)["y_pred"])
        for j, (_, lab) in enumerate(dp.HORIZONS):
            jump = np.abs(y[:, j] - now)
            g = dict(groups, ramp=np.where(jump >= np.quantile(jump, 0.95), "ramp", "thuong"))
            for model, ps in preds.items():
                for kind, lab_arr in g.items():
                    for val in np.unique(lab_arr):
                        sel = lab_arr == val
                        r = [rmse(y[sel, j] - p[sel, j]) for p in ps]
                        rows.append(dict(site=site, model=model, horizon=lab, regime=kind, value=val,
                                         n=int(sel.sum()), RMSE=float(np.mean(r)), RMSE_std=float(np.std(r))))
    df = pd.DataFrame(rows)
    pers = df[df.model == "persistence"].set_index(["site", "horizon", "regime", "value"]).RMSE
    df["skill"] = 1 - df.RMSE / [pers[k] for k in zip(df.site, df.horizon, df.regime, df.value)]
    df.to_csv(os.path.join(RESULTS, "regime.csv"), index=False)

    for kind in ("mua", "ngay_dem", "ramp"):
        sub = df[(df.regime == kind) & (df.model != "persistence")]
        print("\n=== Skill vs persistence theo {} (trung binh 4 tram) ===".format(kind))
        print(sub.groupby(["horizon", "value", "model"]).skill.mean().unstack("model")
              .to_string(float_format=lambda x: "%.3f" % x))
    print("\nSo mau theo mua:", df[(df.regime == "mua") & (df.model == "persistence") & (df.horizon == "1h")]
          .groupby("value").n.sum().to_dict())


if __name__ == "__main__":
    main()
