"""
Kiem tra hop #6 (CPU, re):

1. Chu ky ngay (Q3): pha cuc dai gio trung binh theo gio dia phuong cua tung tram.
   Tram ven bien thuc su phai co cuc dai buoi chieu (gio bien), khac dat lien/ngoai khoi.
2. "Ma tram ngam" (E7): bo phan loai doan tram tu 1 vector dac trung tai 1 thoi diem.
   Neu bien khi tuong tuyet doi (ap suat, nhiet do, mat do) doan dung gan 100% con bo chi
   toc do gio (W) thap han -> co bang chung bien tuyet doi mang danh tinh tram.

    py scripts/19_site_checks.py
"""

import importlib.util
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")
METEO = ["temperature", "pressure", "air_density", "dT_10_100", "dP_0_200"]


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    from sklearn.ensemble import RandomForestClassifier
    g = _load("g", "09_global_loso.py")
    dp = g.dp
    sites = list(dp.SITES)

    print("1) Gio cuc dai trung binh theo gio dia phuong (ws 100 m, 2017-2021):")
    rows = []
    for s in sites:
        df = dp._read_site(s, dp.DATA_DIR)
        cyc = df["wind_speed"].groupby(df.index.hour).mean()
        rows.append(dict(site=s, regime=dp.REGIME[s], gio_cuc_dai=int(cyc.idxmax()), gio_cuc_tieu=int(cyc.idxmin()),
                         bien_do=float(cyc.max() - cyc.min()), bien_do_tuong_doi=float((cyc.max() - cyc.min()) / cyc.mean())))
    cy = pd.DataFrame(rows)
    print(cy.round(2).to_string(index=False))
    cy.to_csv(os.path.join(RESULTS, "diurnal_cycle.csv"), index=False)

    print("\n2) Doan tram tu dac trung tai 1 thoi diem (8 lop, 20k mau train / 20k mau test):")
    rng = np.random.default_rng(0)
    out = []
    for name, cols in (("khi tuong tuyet doi", METEO), ("chi toc do gio (W)", sorted(g.FEATURE_SETS["wind"]))):
        Xtr, ytr, Xte, yte = [], [], [], []
        for k, s in enumerate(sites):
            d = dp.load_site(s)
            idx = [d.features.index(c) for c in cols]
            raw = dp._read_site(s, dp.DATA_DIR)[d.features].to_numpy(np.float32)  # gia tri GOC, chua chuan hoa theo tram
            tr = rng.choice(d.idx_train, 2500, replace=False)
            te = rng.choice(d.idx_test, 2500, replace=False)
            Xtr.append(raw[tr][:, idx]); Xte.append(raw[te][:, idx])
            ytr += [k] * len(tr); yte += [k] * len(te)
        clf = RandomForestClassifier(n_estimators=200, max_depth=16, n_jobs=-1, random_state=0)
        clf.fit(np.vstack(Xtr), ytr)
        acc = float((clf.predict(np.vstack(Xte)) == np.array(yte)).mean())
        out.append(dict(bo_dac_trung=name, so_bien=len(cols), do_chinh_xac=acc))
        print("   {:<22} {:>2} bien  do chinh xac = {:.3f}  (ngau nhien = 0.125)".format(name, len(cols), acc))
    pd.DataFrame(out).to_csv(os.path.join(RESULTS, "site_id_classifier.csv"), index=False)


if __name__ == "__main__":
    main()
