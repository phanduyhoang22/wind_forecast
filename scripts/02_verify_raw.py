"""
Kiem dinh du lieu tho truoc khi dung. Chay NGAY sau khi tai xong.

Muc dich: bat dung cai loi da lam hong dataset cu -- du lieu 15 phut
duoc noi suy tuyen tinh tu du lieu gio, khien 50% nhan o horizon ngan
tro thanh ham tat dinh cua input.

    py scripts/02_verify_raw.py
"""

import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data_raw")

# 15 phut/buoc -> 1h = 4 buoc, 3h = 12 buoc, 6h = 24 buoc
HORIZONS = [(4, "1h"), (12, "3h"), (24, "6h")]
WS_COL_CANDIDATES = ["wind speed at 100m (m/s)", "windspeed_100m", "wind speed at 100m"]


def read_nrel_csv(path):
    """CSV cua NREL co dong metadata (it cot hon) truoc header thuc su.
    Dung module csv de do -- pandas nghen vi so cot khong deu."""
    import csv as _csv
    with open(path, newline="", encoding="utf-8") as f:
        head = [r for _, r in zip(range(8), _csv.reader(f))]
    hdr = next((i for i, r in enumerate(head) if r and r[0].strip() == "Year"), None)
    if hdr is None:
        raise ValueError("Khong tim thay dong header bat dau bang 'Year' trong " + path)
    df = pd.read_csv(path, skiprows=hdr)
    df.columns = [c.strip() for c in df.columns]
    parts = {c.lower(): c for c in df.columns}
    df["time"] = pd.to_datetime(dict(
        year=df[parts["year"]], month=df[parts["month"]], day=df[parts["day"]],
        hour=df[parts["hour"]], minute=df[parts["minute"]]))
    return df.set_index("time").drop(columns=[parts[k] for k in
                                              ("year", "month", "day", "hour", "minute")])


def pick_ws(df):
    for c in df.columns:
        lc = c.lower()
        if "wind speed" in lc and "100" in lc:
            return c
    for c in df.columns:
        if "wind speed" in c.lower():
            return c
    raise ValueError("Khong thay cot toc do gio trong: " + ", ".join(df.columns))


def test_interpolation(df, ws_col):
    """Diem giua co nam dung tren duong thang noi 2 diem ben canh khong?
    Neu co phase nao = 0.000000 -> du lieu bi noi suy, KHONG dung duoc."""
    v = df[ws_col].to_numpy(float)
    mins = df.index.minute.to_numpy()
    mid = (v[:-2] + v[2:]) / 2.0
    resid = np.abs(v[1:-1] - mid)
    out = {}
    for m in sorted(np.unique(mins)):
        sel = mins[1:-1] == m
        if sel.sum():
            out[int(m)] = float(resid[sel].mean())
    return out


def test_leak(df, ws_col):
    """Quy tac tam thuong y(t+k) = v(t) + k*(v(t)-v(t-1)).
    Neu RMSE = 0 o phase nao -> nhan bi ro ri hoan toan."""
    v = df[ws_col].to_numpy(float)
    mins = df.index.minute.to_numpy()
    rows = []
    for k, lab in HORIZONS:
        pred = v[1:-k] + k * (v[1:-k] - v[:-k - 1])
        true = v[1 + k:]
        err = true - pred
        phase = mins[1:-k]
        r = {"horizon": lab}
        for m in sorted(np.unique(mins)):
            sel = phase == m
            r[":%02d" % m] = float(np.sqrt(np.mean(err[sel] ** 2))) if sel.sum() else np.nan
        r["tong"] = float(np.sqrt(np.mean(err ** 2)))
        rows.append(r)
    return pd.DataFrame(rows).set_index("horizon")


def test_persistence(df, ws_col, frac=0.15):
    v = df[ws_col].to_numpy(float)
    s = int(len(v) * (1 - frac))
    rows = []
    for k, lab in HORIZONS:
        true, pred = v[s + k:], v[s:-k]
        rmse = float(np.sqrt(np.mean((true - pred) ** 2)))
        r2 = 1 - np.sum((true - pred) ** 2) / np.sum((true - true.mean()) ** 2)
        rows.append({"horizon": lab, "RMSE": rmse, "R2": float(r2)})
    return pd.DataFrame(rows).set_index("horizon")


def main():
    if not os.path.isdir(RAW_DIR):
        sys.exit("Chua co thu muc data_raw/. Chay scripts/01_download_seawtk.py truoc.")

    groups = {}
    for p in sorted(glob.glob(os.path.join(RAW_DIR, "*.csv"))):
        station = os.path.basename(p).rsplit("_", 2)[0]
        groups.setdefault(station, []).append(p)
    if not groups:
        sys.exit("data_raw/ rong.")

    verdict_ok = True
    for station, paths in groups.items():
        df = pd.concat([read_nrel_csv(p) for p in paths]).sort_index()
        df = df[~df.index.duplicated(keep="first")]
        ws = pick_ws(df)

        step = df.index.to_series().diff().dropna()
        gaps = int((step != step.mode()[0]).sum())

        print("=" * 78)
        print("{}  |  {} -> {}".format(station, df.index[0], df.index[-1]))
        print("  {} dong, {} cot, buoc {} , gap={}, NaN={}"
              .format(len(df), len(df.columns), step.mode()[0], gaps, int(df.isna().sum().sum())))
        print("  cot toc do gio dung de kiem dinh: '{}'".format(ws))
        print("  mean={:.3f} m/s  std={:.3f}".format(df[ws].mean(), df[ws].std()))

        interp = test_interpolation(df, ws)
        print("\n  [1] Residual so voi noi suy tuyen tinh, theo phut:")
        bad = [m for m, r in interp.items() if r < 1e-9]
        for m, r in interp.items():
            flag = "  <-- NOI SUY!" if r < 1e-9 else ""
            print("        :{:02d}  {:.6f}{}".format(m, r, flag))
        if bad:
            verdict_ok = False
            print("      => HONG: cac phase {} la noi suy tuyen tinh.".format(bad))
        else:
            print("      => DAT: moi phase deu co bien thien that.")

        print("\n  [2] Ro ri nhan (RMSE cua quy tac ngoai suy tuyen tinh 2 diem):")
        leak = test_leak(df, ws)
        print(leak.to_string(float_format=lambda x: "%.5f" % x).replace("\n", "\n      "))
        if (leak.drop(columns=["tong"]).to_numpy() < 1e-9).any():
            verdict_ok = False
            print("      => HONG: co phase RMSE = 0, nhan bi ro ri hoan toan.")
        else:
            print("      => DAT: khong co phase nao du doan duoc chinh xac.")

        print("\n  [3] Baseline persistence tren 15% cuoi (muc san de vuot qua):")
        print(test_persistence(df, ws).to_string(
            float_format=lambda x: "%.4f" % x).replace("\n", "\n      "))
        print()

    print("=" * 78)
    print("KET LUAN: {}".format(
        "du lieu DUNG DUOC, sang buoc feature engineering."
        if verdict_ok else
        "du lieu VAN HONG -- dung lai, khong dung tap nay."))


if __name__ == "__main__":
    main()
