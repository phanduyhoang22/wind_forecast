# T25 step 1 — NREL SEA WTK v3 availability for 2007–2015

Task: T25 step 1 (light, read-only). Date: 2026-11-28. No data downloaded, no API probe sent.

## Question
Does the endpoint used by `scripts/01_download_seawtk.py`
(`/api/wind-toolkit/v2/wind/wtk-seasiawind-v3-download.csv`, WRF 9 km/60 min -> sup3r 3 km/15 min)
serve 2007–2015 at 15 min / 100 m for the 8 sites (A–H, coordinates in `data_v2/PROVENANCE.md`),
and what are the request limits?

## Sources (read 2026-11-28)
1. API endpoint docs: https://developer.nlr.gov/docs/wind/wind-toolkit/wtk-seasiawind-v3-download/
   (the old host `developer.nrel.gov` no longer resolves; the script already uses `developer.nlr.gov`).
   - `names`: years 2007 through 2021, each listed as an option; description: data covers
     "the years 2007 to 2021".
   - `interval`: 15, 30, 60 min; native resolution 15 min.
   - `attributes`: windspeed / winddirection / temperature at 10, 40, 80, 100, 120, 160, 200 m;
     pressure at 0, 100, 200 m. All 18 attributes requested by the script are in the list.
   - Rate limits (.csv format): "10,000 a day at a frequency of no more than 1 per second";
     other formats: 2,000/day, 1 per 2 s; 20 in-flight requests per user; queue fail-safe.
   - CSV streaming: "single location, single year only" (matches the script: 1 point x 1 year).
2. Developer network rate limits: https://developer.nlr.gov/docs/rate-limits/
   - Default API key: "1,000 requests per hour" (header `X-RateLimit-Limit`); no default daily
     limit stated beyond the endpoint limit above (DEMO_KEY only: 50/day).
3. NREL technical report NREL/TP-5000-85481, https://www.nrel.gov/docs/fy23osti/85481.pdf
   (cited in the script docstring; summary via search result): hybrid WRF + GAN super-resolution,
   wind/temperature/pressure, January 2007 – December 2021, 3 km, 15 min.
4. In-repo empirical evidence: `data_2016/` (8 sites, 35,040 samples/site, `data_v2/PROVENANCE.md`
   section "Tập test lùi thời gian 2016") was downloaded through the same endpoint at 15 min, so a
   pre-2017 year has already been served successfully for all 8 sites.

## Availability per year

| year | available | interval(s) | 100 m | evidence |
|---|---|---|---|---|
| 2007 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 (docs + report, Jan 2007 start) |
| 2008 | yes (leap year) | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2009 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2010 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2011 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2012 | yes (leap year) | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2013 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2014 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2015 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |

Docs were unambiguous, so no API probe was sent (acceptance criterion 3: probe only if unclear).
Per-site availability is not listed by the docs; the 8 sites already return data for 2016–2021
from the same grid, so the same grid cells should exist for 2007–2015 (not probed).

## Requests and time estimate
- Format: 1 request = 1 site x 1 year (CSV streaming rule). 8 sites x 9 years = **72 requests**.
- Limits: 10,000/day and 1/s (CSV), 1,000/hour per key. 72 requests fit in one hour and one day.
- With the script default `--sleep 2.0` plus server time per request (previous runs: one
  year-file per request, ~35k rows), expected wall time is minutes to about 1 hour.
- Calendar days: **1**.
- Command (not run): `py scripts/01_download_seawtk.py --years 2007-2015 --sites A,B,C,D,E,F,G,H --raw-dir <new dir>`
  (use a new raw dir; `data_raw*/` are read-only per CLAUDE.md).

## Notes / risks
- Leap years 2008 and 2012: the script sends `leap_day=true`; `data_2016/` (leap year) has
  35,040 = 365 x 96 samples, so the build step seems to drop 29 Feb. Check consistency in the
  build step if 2007–2015 is used.
- Not verified by probe: actual HTTP 200 + row count for any 2007–2015 request.
- Host rename: NREL docs now live under `developer.nlr.gov`; `developer.nrel.gov` fails DNS
  (seen 2026-11-28).
