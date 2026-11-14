"""
Tai du lieu gio 15-phut THAT tu NREL Southeast Asia Wind Toolkit v3.

Nguon : WRF 9km/60min -> GAN super-resolution (sup3r) -> 3km/15min
        https://docs.nrel.gov/docs/fy23osti/85481.pdf
Endpoint: /api/wind-toolkit/v2/wind/wtk-seasiawind-v3-download.csv
Nam    : 2007-2021 | Interval: 15/30/60 phut | 1 diem x 1 nam moi request

Cach dung:
    set NREL_API_KEY=...
    set NREL_EMAIL=ban@email.com
    py scripts/01_download_seawtk.py
    py scripts/01_download_seawtk.py --years 2015-2021     # doi khoang nam
    py scripts/01_download_seawtk.py --sites A,D           # chi vai tram

Dang ky API key mien phi (co ngay): https://developer.nlr.gov/signup/
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://developer.nlr.gov/api/wind-toolkit/v2/wind/wtk-seasiawind-v3-download.csv"

# Toa do lay tu Table 1 cua ban thao. WKT dung thu tu POINT(lon lat).
#
# Tram B da doi: (11.6, 108.9) trong ban thao goc nam sau trong dat lien ~25 km,
# chi cho mean 4.43 m/s -- khong xung nhan "Coastal". Luoi ERA5 ~31 km cua tap
# du lieu cu tron gio bien vao dat lien nen che mat sai sot nay. Diem moi nam
# tren vanh dai dien gio Ninh Thuan thuc, mean 7.45 m/s.
SITES = {
    "A": {"name": "Tram_A_DatLien",   "lat": 21.0, "lon": 105.8, "regime": "Inland"},
    "B": {"name": "Tram_B_VenBien",   "lat": 11.72, "lon": 109.11, "regime": "Coastal"},
    "C": {"name": "Tram_C_DoiNui",    "lat": 14.0, "lon": 108.0, "regime": "Complex Terrain"},
    "D": {"name": "Tram_D_NgoaiKhoi", "lat": 10.5, "lon": 109.3, "regime": "Offshore"},
    # Hop #5 (13/11/2026): them 1 tram moi che do -> so chuyen giao cung vs khac che do.
    # Toa do de xuat, PHAI qua cong kiem tra (mean, khoang cach bo, khong trung dao) truoc khi dung.
    "E": {"name": "Tram_E_DatLien",   "lat": 19.85, "lon": 105.55, "regime": "Inland"},           # dong bang Thanh Hoa
    "F": {"name": "Tram_F_VenBien",   "lat": 13.85, "lon": 109.28, "regime": "Coastal"},          # bo bien Binh Dinh. Cong: Tuy Phong tuong quan B 0.81; Bac Lieu/Soc Trang mean < 5.6
    "G": {"name": "Tram_G_DoiNui",    "lat": 16.65, "lon": 106.65, "regime": "Complex Terrain"},  # Huong Hoa, Quang Tri
    "H": {"name": "Tram_H_NgoaiKhoi", "lat": 20.30, "lon": 107.20, "regime": "Offshore"},         # vinh Bac Bo (Vung Tau 9.80,108.60 truot cong: tuong quan voi D 0.95)
}

ATTRIBUTES = [
    # gio nhieu do cao -> tinh duoc shear exponent va veer
    "windspeed_10m", "windspeed_40m", "windspeed_80m", "windspeed_100m",
    "windspeed_120m", "windspeed_160m", "windspeed_200m",
    "winddirection_10m", "winddirection_80m", "winddirection_100m", "winddirection_120m",
    # nhiet do nhieu do cao -> proxy do on dinh khi quyen
    "temperature_10m", "temperature_80m", "temperature_100m", "temperature_120m",
    # ap suat -> tinh air_density theo khi ly tuong
    "pressure_0m", "pressure_100m", "pressure_200m",
]

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_raw")


def parse_years(spec):
    if "-" in spec:
        a, b = spec.split("-")
        return list(range(int(a), int(b) + 1))
    return [int(y) for y in spec.split(",")]


def build_url(lat, lon, year, interval, api_key, email, full_name, affiliation):
    q = {
        "wkt": "POINT({} {})".format(lon, lat),
        "attributes": ",".join(ATTRIBUTES),
        "names": str(year),
        "interval": str(interval),
        "utc": "false",        # gio dia phuong -> dac trung chu ky ngay dung mui gio VN
        "leap_day": "true",    # giu 29/02 de chuoi thoi gian lien tuc, khong thung lo
        "email": email,
        "api_key": api_key,
    }
    if full_name:
        q["full_name"] = full_name
    if affiliation:
        q["affiliation"] = affiliation
    q["reason"] = "academic research"
    q["mailing_list"] = "false"
    return BASE + "?" + urllib.parse.urlencode(q)


def download_one(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "wind-forecast-research/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        try:
            errs = json.loads(detail).get("errors", [detail])
            detail = "; ".join(errs)
        except Exception:
            pass
        raise RuntimeError("HTTP {} - {}".format(e.code, detail))

    # Neu request qua lon, API tra JSON bao "se gui email" thay vi CSV
    head = body[:200].lstrip()
    if head.startswith(b"{"):
        raise RuntimeError("API tra JSON thay vi CSV: " + body[:400].decode("utf-8", "replace"))

    with open(dest, "wb") as f:
        f.write(body)
    return len(body)


def sniff(path):
    """Doc thu file de bao so dong du lieu + ten cot."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    hdr_idx = next((i for i, r in enumerate(rows[:10]) if r and r[0].strip() == "Year"), None)
    if hdr_idx is None:
        return None, None, len(rows)
    return hdr_idx, rows[hdr_idx], len(rows) - hdr_idx - 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2017-2021", help="vd 2017-2021 hoac 2019,2020,2021")
    ap.add_argument("--sites", default="A,B,C,D")
    ap.add_argument("--interval", type=int, default=15, choices=[15, 30, 60])
    ap.add_argument("--api-key", default=os.environ.get("NREL_API_KEY", ""))
    ap.add_argument("--email", default=os.environ.get("NREL_EMAIL", ""))
    ap.add_argument("--full-name", default=os.environ.get("NREL_NAME", ""))
    ap.add_argument("--affiliation", default=os.environ.get("NREL_AFFILIATION", ""))
    ap.add_argument("--raw-dir", default=RAW_DIR, help="vd data_raw_2016 cho tap test lui thoi gian")
    ap.add_argument("--sleep", type=float, default=2.0, help="gian cach request (API cho 1/giay)")
    args = ap.parse_args()

    if not args.api_key or not args.email:
        sys.exit(
            "Thieu API key hoac email.\n"
            "  Dang ky mien phi: https://developer.nlr.gov/signup/\n"
            "  PowerShell:  $env:NREL_API_KEY='...'; $env:NREL_EMAIL='ban@email.com'\n"
            "  hoac:        py scripts/01_download_seawtk.py --api-key ... --email ...")

    years = parse_years(args.years)
    sites = [s.strip().upper() for s in args.sites.split(",")]
    os.makedirs(args.raw_dir, exist_ok=True)

    jobs = [(s, y) for s in sites for y in years]
    print("NREL SEA WTK v3 | {} tram x {} nam = {} request | interval={} phut"
          .format(len(sites), len(years), len(jobs), args.interval))
    print("Luu vao: {}\n".format(args.raw_dir))

    failed = []
    for i, (site, year) in enumerate(jobs, 1):
        meta = SITES[site]
        dest = os.path.join(args.raw_dir, "{}_{}_{}min.csv".format(meta["name"], year, args.interval))
        tag = "[{}/{}] {} {} ({})".format(i, len(jobs), site, year, meta["regime"])

        if os.path.exists(dest) and os.path.getsize(dest) > 10000:
            _, _, n = sniff(dest)
            print("{:<34} da co, bo qua ({} dong)".format(tag, n))
            continue

        url = build_url(meta["lat"], meta["lon"], year, args.interval,
                        args.api_key, args.email, args.full_name, args.affiliation)
        try:
            nbytes = download_one(url, dest)
            hdr_idx, cols, nrows = sniff(dest)
            print("{:<34} OK  {:>7.1f} KB  {:>6} dong  {} cot"
                  .format(tag, nbytes / 1024, nrows, len(cols) if cols else "?"))
        except Exception as e:
            print("{:<34} LOI: {}".format(tag, e))
            failed.append((site, year, str(e)))
            if os.path.exists(dest):
                os.remove(dest)
        time.sleep(args.sleep)

    print()
    if failed:
        print("That bai {}/{} request:".format(len(failed), len(jobs)))
        for s, y, e in failed:
            print("   {} {} -> {}".format(s, y, e))
    else:
        print("Tai xong toan bo. Buoc tiep theo:")
        print("   py scripts/02_verify_raw.py")


if __name__ == "__main__":
    main()
