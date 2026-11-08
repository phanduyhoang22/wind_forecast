"""
Dung tap dac trung tren luoi 15 phut THAT (khong noi suy).

Doc data_raw/*.csv  ->  ghi data_v2/<Tram>_15min.csv

Nguyen tac chong ro ri: moi dac trung tai thoi diem t chi dung thong tin
tai t hoac truoc t. Rolling khong can giua (khong center). Nhan y(t+h)
KHONG nam trong file -- do code huan luyen tu sinh bang sliding window.

    py scripts/03_build_dataset.py
"""

import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data_raw")
OUT_DIR = os.path.join(ROOT, "data_v2")

R_SPECIFIC = 287.05      # J/(kg.K) cho khong khi kho
STEPS_PER_HOUR = 4       # luoi 15 phut

WS = {h: "wind speed at {}m (m/s)".format(h) for h in (10, 40, 80, 100, 120, 160, 200)}
WD = {h: "wind direction at {}m (deg)".format(h) for h in (10, 80, 100, 120)}
TA = {h: "air temperature at {}m (C)".format(h) for h in (10, 80, 100, 120)}
PR = {0: "surface air pressure (Pa)", 100: "air pressure at 100m (Pa)",
      200: "air pressure at 200m (Pa)"}


def read_nrel_csv(path):
    import csv as _csv
    with open(path, newline="", encoding="utf-8") as f:
        head = [r for _, r in zip(range(8), _csv.reader(f))]
    hdr = next((i for i, r in enumerate(head) if r and r[0].strip() == "Year"), None)
    if hdr is None:
        raise ValueError("Khong thay header 'Year' trong " + path)
    meta = dict(zip(head[0][0::2], head[0][1::2])) if hdr == 1 else {}
    df = pd.read_csv(path, skiprows=hdr)
    df.columns = [c.strip() for c in df.columns]
    df["time"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
    return df.set_index("time").drop(columns=["Year", "Month", "Day", "Hour", "Minute"]), meta


def angdiff(a, b):
    """Hieu goc, boc ve [-180, 180]."""
    return (a - b + 180.0) % 360.0 - 180.0


def build(df):
    out = pd.DataFrame(index=df.index)

    # --- bien muc tieu: toc do gio tai do cao hub 100 m ---
    out["wind_speed"] = df[WS[100]]

    # --- trang thai khi quyen tai t ---
    out["temperature"] = df[TA[100]]
    out["pressure"] = df[PR[100]]
    tempK = df[TA[100]] + 273.15
    out["air_density"] = df[PR[100]] / (R_SPECIFIC * tempK)

    # --- huong gio dang chu ky + phan ra u/v ---
    rad = np.deg2rad(df[WD[100]])
    out["wind_sin"] = np.sin(rad)
    out["wind_cos"] = np.cos(rad)
    out["u_wind"] = -df[WS[100]] * np.sin(rad)
    out["v_wind"] = -df[WS[100]] * np.cos(rad)

    # --- trac dien dung: nhung dac trung CHI co nho du lieu nhieu do cao ---
    # so mu shear (dinh luat luy thua): alpha = ln(v2/v1) / ln(z2/z1)
    # Kep ve [-0.5, 1.5]: khi gio rat nhe ty so v2/v1 bung ra gia tri vo nghia
    # vat ly, va duoi cuc tri do se lam hong MinMaxScaler o buoc huan luyen.
    out["shear_alpha"] = (np.log(df[WS[120]] / df[WS[80]].clip(lower=0.1))
                          / np.log(120.0 / 80.0)).clip(-0.5, 1.5)
    # shear dai rong hon, bat ca lop bien phia duoi
    out["shear_alpha_wide"] = (np.log(df[WS[200]] / df[WS[10]].clip(lower=0.1))
                               / np.log(200.0 / 10.0)).clip(-0.5, 1.5)
    # veer: doi huong gio theo do cao (deg)
    out["veer_120_80"] = angdiff(df[WD[120]], df[WD[80]])
    # proxy do on dinh khi quyen: gradient nhiet thang dung
    out["dT_10_100"] = df[TA[10]] - df[TA[100]]
    # gradient ap suat thang dung
    out["dP_0_200"] = df[PR[0]] - df[PR[200]]
    # gio tai vai muc de mo ta trac dien
    out["ws_10m"] = df[WS[10]]
    out["ws_80m"] = df[WS[80]]
    out["ws_120m"] = df[WS[120]]
    out["ws_200m"] = df[WS[200]]

    # --- chu ky thoi gian ---
    hr = out.index.hour + out.index.minute / 60.0
    out["hr_sin"] = np.sin(2 * np.pi * hr / 24.0)
    out["hr_cos"] = np.cos(2 * np.pi * hr / 24.0)
    mo = out.index.month
    out["month_sin"] = np.sin(2 * np.pi * mo / 12.0)
    out["month_cos"] = np.cos(2 * np.pi * mo / 12.0)

    # --- dong hoc tu hoi quy (chi nhin ve qua khu) ---
    ws = out["wind_speed"]
    out["ws_lag_15min"] = ws.shift(1)
    out["ws_lag_1h"] = ws.shift(STEPS_PER_HOUR)
    out["ws_lag_3h"] = ws.shift(3 * STEPS_PER_HOUR)
    out["ws_lag_6h"] = ws.shift(6 * STEPS_PER_HOUR)
    out["ws_lag_24h"] = ws.shift(24 * STEPS_PER_HOUR)
    out["ws_rolling_mean_1h"] = ws.rolling(STEPS_PER_HOUR).mean()
    out["ws_rolling_std_1h"] = ws.rolling(STEPS_PER_HOUR).std()
    out["ws_rolling_mean_6h"] = ws.rolling(6 * STEPS_PER_HOUR).mean()
    out["ws_delta"] = ws.diff()
    out["ws_delta_1h"] = ws.diff(STEPS_PER_HOUR)

    return out


def main():
    if not os.path.isdir(RAW_DIR):
        sys.exit("Chua co data_raw/. Chay scripts/01_download_seawtk.py truoc.")
    os.makedirs(OUT_DIR, exist_ok=True)

    groups = {}
    for p in sorted(glob.glob(os.path.join(RAW_DIR, "*.csv"))):
        groups.setdefault(os.path.basename(p).rsplit("_", 2)[0], []).append(p)
    if not groups:
        sys.exit("data_raw/ rong.")

    summary = []
    for station, paths in sorted(groups.items()):
        frames, meta = [], {}
        for p in paths:
            d, m = read_nrel_csv(p)
            frames.append(d)
            meta = meta or m
        raw = pd.concat(frames).sort_index()
        raw = raw[~raw.index.duplicated(keep="first")]

        feat = build(raw)
        n_before = len(feat)
        feat = feat.dropna()                       # cat phan dau thieu lag/rolling

        step = feat.index.to_series().diff().dropna()
        gaps = int((step != pd.Timedelta("15min")).sum())

        dest = os.path.join(OUT_DIR, station + "_15min.csv")
        feat.to_csv(dest, index_label="time", float_format="%.6f")

        summary.append({
            "Station": station,
            "Lat": float(meta.get("Latitude", "nan")),
            "Lon": float(meta.get("Longitude", "nan")),
            "From": str(feat.index[0]), "To": str(feat.index[-1]),
            "Samples": len(feat), "Features": feat.shape[1] - 1,
            "Mean_ws": feat["wind_speed"].mean(), "Std_ws": feat["wind_speed"].std(),
            "Gaps": gaps,
        })
        print("{:<22} {:>7} mau ({} bi cat do lag), {} dac trung + target, gap={}"
              .format(station, len(feat), n_before - len(feat), feat.shape[1] - 1, gaps))

    s = pd.DataFrame(summary)
    print("\n--- Thay the cho Table 1 cua ban thao ---")
    print(s.to_string(index=False, float_format=lambda x: "%.4f" % x))
    s.to_csv(os.path.join(OUT_DIR, "_summary_table1.csv"), index=False)
    print("\nGhi vao: {}".format(OUT_DIR))


if __name__ == "__main__":
    main()
