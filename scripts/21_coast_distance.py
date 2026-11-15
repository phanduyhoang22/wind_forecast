"""
Hop #6/#8: khoang cach tu o luoi tram toi bo bien (mat na dat/bien global-land-mask, ~1 km).
Dieu kien Q3: tram F (ven bien) cach bo <= 5 km. Tim trong ban kinh ~0.15 do (~16 km).

    pip install global-land-mask
    py scripts/21_coast_distance.py
"""
import math
import os

import numpy as np
import pandas as pd
from global_land_mask import globe

CELLS = {"A": (20.9954, 105.7896), "B": (11.7217, 109.1090), "C": (14.0017, 108.0117), "D": (10.4920, 109.3011),
         "E": (19.8426, 105.5427), "F": (13.8480, 109.2736), "G": (16.6404, 106.6400), "H": (20.3038, 107.1887)}


def coast_km(lat0, lon0, radius=0.15, step=0.002):
    land = globe.is_land(lat0, lon0)
    g = np.arange(-radius, radius + step / 2, step)
    la, lo = np.meshgrid(lat0 + g, lon0 + g, indexing="ij")
    other = globe.is_land(la, lo) != land
    if not other.any():
        return land, None                                   # xa hon ban kinh tim
    d = np.hypot((la - lat0) * 111.0, (lo - lon0) * 111.0 * math.cos(math.radians(lat0)))
    return land, float(d[other].min())


if __name__ == "__main__":
    rows = [dict(site=s, on_land=bool(coast_km(*c)[0]), coast_km=coast_km(*c)[1]) for s, c in CELLS.items()]
    df = pd.DataFrame(rows)
    print(df.round(1).to_string(index=False))
    df.to_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "coast_distance.csv"), index=False)
