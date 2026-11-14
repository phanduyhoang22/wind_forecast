"""
Dong goi data_v2/ thanh .npz de tai len Google Drive.

CSV 52.6 MB/tram -> npz nen 10.9 MB/tram (nho hon 4.8x, doc nhanh hon 4x).
Ca 4 tram khoang 44 MB, thoai mai cho Drive va nhanh khi Colab doc.

    py scripts/05_pack_for_colab.py

Sau do tai CA THU MUC data_v2/ (cac file .npz) len Drive tai:
    MyDrive/WIND_FORECAST_DATA/data_v2/
"""

import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data_v2")


def main():
    import sys
    global DATA_DIR
    if len(sys.argv) > 1:                      # vd: py scripts/05_pack_for_colab.py data_2016
        DATA_DIR = os.path.join(ROOT, sys.argv[1])
    csvs = sorted(f for f in os.listdir(DATA_DIR) if f.endswith("_15min.csv"))
    if not csvs:
        raise SystemExit("Khong thay file *_15min.csv trong data_v2/")

    tot_csv = tot_npz = 0
    for name in csvs:
        src = os.path.join(DATA_DIR, name)
        dst = src.replace(".csv", ".npz")
        df = pd.read_csv(src, parse_dates=["time"]).set_index("time")

        np.savez_compressed(
            dst,
            X=df.to_numpy(np.float32),
            time=df.index.values.astype("int64"),
            cols=np.array(list(df.columns), dtype="U32"),
        )

        # Doc lai va doi chieu -- khong tin vao "chac la dung"
        z = np.load(dst, allow_pickle=False)
        back = pd.DataFrame(z["X"], columns=[str(c) for c in z["cols"]],
                            index=pd.to_datetime(z["time"]))
        assert list(back.columns) == list(df.columns), "lech ten cot"
        assert back.shape == df.shape, "lech kich thuoc"
        assert back.index.equals(df.index), "lech chi so thoi gian"
        dev = float(np.abs(back.to_numpy() - df.to_numpy(np.float32)).max())
        assert dev == 0.0, "lech gia tri: {}".format(dev)

        a, b = os.path.getsize(src), os.path.getsize(dst)
        tot_csv += a
        tot_npz += b
        print("{:<30} {:6.1f} MB -> {:5.1f} MB  ({:.1f}x)  doi chieu OK"
              .format(name.replace(".csv", ""), a / 1e6, b / 1e6, a / b))

    print("\nTong: {:.1f} MB -> {:.1f} MB".format(tot_csv / 1e6, tot_npz / 1e6))
    print("\nBuoc tiep theo -- tai len Google Drive:")
    print("   MyDrive/WIND_FORECAST_DATA/data_v2/*.npz")
    print("   (chi can cac file .npz, khong can .csv)")


if __name__ == "__main__":
    main()
