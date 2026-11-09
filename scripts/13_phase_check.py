"""
Kiem tra "ket cau GAN" (hop #1): du lieu goc WRF la 60 phut; 3/4 diem 15 phut
do GAN sup3r sinh. Neu loi ch tap trung o diem GAN sinh thi mot phan sai so
1h la du bao ket cau GAN, khong phai khi quyen.

Voi moi model/tram/horizon: RMSE tach theo phut cua THOI DIEM DICH (:00 = diem
WRF goc, :15/:30/:45 = diem GAN), va RMSE chi tren diem :00 (chuoi theo gio).

    py scripts/13_phase_check.py
"""

import glob
import importlib.util
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


def main():
    dp = _load("dp", "04_data_pipeline.py")
    rows = []
    for site in dp.SITES:
        d = dp.load_site(site)
        y = d.y_raw[d.idx_test]
        ws = d.features.index(dp.TARGET)
        now = d.scaler_y.inverse(d.X[d.idx_test, ws].reshape(-1, 1)).ravel()
        preds = {"persistence": np.repeat(now[:, None], len(dp.HORIZONS), axis=1)}
        for f in glob.glob(os.path.join(RESULTS, "preds", "{}_*.npz".format(site))):
            model = os.path.basename(f).split("_")[1]
            preds.setdefault(model, []).append(np.load(f)["y_pred"])
        for model, p in preds.items():
            p = np.mean(p, axis=0) if isinstance(p, list) else p
            for j, (k, lab) in enumerate(dp.HORIZONS):
                minute = d.time[d.idx_test + k].minute          # phut cua thoi diem dich
                err = y[:, j] - p[:, j]
                r = dict(site=site, model=model, horizon=lab,
                         RMSE_all=float(np.sqrt(np.mean(err ** 2))))
                for m in (0, 15, 30, 45):
                    r["RMSE_:%02d" % m] = float(np.sqrt(np.mean(err[minute == m] ** 2)))
                rows.append(r)
    df = pd.DataFrame(rows)
    df["GAN/WRF"] = df[["RMSE_:15", "RMSE_:30", "RMSE_:45"]].mean(axis=1) / df["RMSE_:00"]
    df.to_csv(os.path.join(RESULTS, "phase_check.csv"), index=False)
    print(df.to_string(index=False, float_format=lambda x: "%.4f" % x))


if __name__ == "__main__":
    main()
