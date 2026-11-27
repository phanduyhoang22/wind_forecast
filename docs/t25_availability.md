# T25 step 1 — NREL SEA WTK v3 availability for 2007–2015

Task: T25 step 1 (light, read-only). Date: 2026-11-28. No data saved; one API probe (site A, 2007,
round 2) held in memory and discarded.

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
| 2007 | yes | 15 / 30 / 60 min | yes | Sources 1, 3; probe site A: HTTP 200, 35,040 rows |
| 2008 | yes (leap year) | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2009 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2010 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2011 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2012 | yes (leap year) | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2013 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2014 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |
| 2015 | yes | 15 / 30 / 60 min | yes | Sources 1, 3 |

Docs are unambiguous. One probe (site A, 2007, 15 min) confirmed HTTP 200 and a full year;
see "2007 probe" below. Other site/year pairs were not probed; the 8 sites already return data
for 2016–2021 from the same grid, so the same grid cells should exist for 2007–2015.

## Requests and time estimate
- Format: 1 request = 1 site x 1 year (CSV streaming rule). 8 sites x 9 years = **72 requests**.
- Limits: 10,000/day and 1/s (CSV), 1,000/hour per key. 72 requests fit in one hour and one day.
- With the script default `--sleep 2.0` plus server time per request (previous runs: one
  year-file per request, ~35k rows), expected wall time is minutes to about 1 hour.
- Calendar days: **1**.
- Command (not run): `py scripts/01_download_seawtk.py --years 2007-2015 --sites A,B,C,D,E,F,G,H --raw-dir <new dir>`
  (use a new raw dir; `data_raw*/` are read-only per CLAUDE.md).

## Notes / risks
- Leap days are kept (correction of round 1, QA-T25-01). `data_2016/Tram_A_DatLien_15min.npz`
  runs 2016-01-02 00:00 .. 2016-12-31 23:45, 35,040 rows, 96 rows on 29 Feb. The raw file
  `data_raw_2016/Tram_A_DatLien_2016_15min.csv` has 35,136 rows (2016-01-01 00:00 .. 12-31 23:45).
- The first local day of the built series is dropped, not the first day of each year file.
  Cause: `scripts/03_build_dataset.py` concatenates all year files (line 140), builds lags, then
  `feat.dropna()` (line 145, "cat phan dau thieu lag/rolling") removes the 24 h lag warm-up
  (96 rows). It is not a UTC -> UTC+7 trim: the API (`utc=false`) already returns local time
  from Jan 1 00:00 (see probe). data_v2 likewise starts 2017-01-02.
- Relevance for 2007–2015: if those years are built together with 2016–2021 as one series, only
  2007-01-01 is lost; if each year is built separately, each loses its first day. Year boundaries
  inside one concatenated build lose nothing.
- Disclosure (open item, PROVENANCE not edited): `data_v2/PROVENANCE.md` line 47 already states
  "175,200 mẫu/trạm sau khi cắt phần đầu thiếu lag 24h" for data_v2; the 2016 section
  (35,040 samples/site) does not state the reason or the start date 2016-01-02.

## 2007 probe (QA-T25-03, 1 request, 2026-11-28)
Request: site A (21.0 N, 105.8 E), year 2007, interval 15, built with `build_url()` from
`scripts/01_download_seawtk.py` (same attributes, `utc=false`, `leap_day=true`). Key and email
read from env vars at runtime, never printed. Body kept in memory only, discarded; no file saved.
Probe script lived in the session scratch dir, outside the repo.

```
HTTP 200 bytes 5091707
header_line 1 rows 35040
columns ['Year', 'Month', 'Day', 'Hour', 'Minute', 'wind speed at 10m (m/s)', 'wind speed at 40m (m/s)', 'wind speed at 80m (m/s)', 'wind speed at 100m (m/s)', 'wind speed at 120m (m/s)', 'wind speed at 160m (m/s)', 'wind speed at 200m (m/s)', 'wind direction at 10m (deg)', 'wind direction at 80m (deg)', 'wind direction at 100m (deg)', 'wind direction at 120m (deg)', 'air temperature at 10m (C)', 'air temperature at 80m (C)', 'air temperature at 100m (C)', 'air temperature at 120m (C)', 'surface air pressure (Pa)', 'air pressure at 100m (Pa)', 'air pressure at 200m (Pa)']
first ['2007', '1', '1', '0', '0'] last ['2007', '12', '31', '23', '45']
feb29_rows 0
```
35,040 = 365 x 96, full year at 15 min, same 23 columns as the 2017 raw file layout
(`data_raw/Tram_A_DatLien_2017_15min.csv`: 35,040 rows, 2017-01-01 00:00 .. 12-31 23:45).
2007 is not a leap year, so 0 rows on 29 Feb is expected. Other sites and years 2008–2015 were
not probed (one probe allowed).

## HANDOFF §7 checks (2026-11-28, run in worktree at 2b5fab3)
1. `py scripts/24_shift_check.py --full` -> `tong: 61 PASS, 4 WARN, 1 FAIL, 3 NOT_VERIFIED`, exit 1.
   - FAIL `docs csv_paths - khong co tai may: references.csv` (known QA-T23-01, only FAIL).
   - WARN `git branch - worktree-agent-af6c794624b7bf286 @ 2b5fab3` (worktree, expected).
   - WARN `git origin - ahead 1, behind 0` (this task's unpushed commit, expected).
   - WARN `git worktrees - 9 worktree phu` (stale agent worktrees; cleanup is Leader's job).
   - WARN `git handoff - cu hon HEAD 5.2 gio` (HEAD includes this task's commit).
   - NOT_VERIFIED `results runs.csv - co file nhung chua co bang khoa`.
   - NOT_VERIFIED `docs csv_paths - chi co tren Drive: t21/loso8_scaler.csv`.
   - NOT_VERIFIED `colab drive - chay status cell (cell 3, notebook MCP Colab)`.
2. Drive `results/runs.csv` 600 rows / 15 per (model, site) / 85118 B — Leader evidence (Colab
   2026-11-28 21:35); NOT_VERIFIED by worker.
3. Drive shap npz newest <= 2026-11-26T02:24Z — Leader evidence (same); NOT_VERIFIED by worker.
4. `git diff --stat 2f2d0ae HEAD -- results/ scripts/` ->
   ` scripts/27_loso_scaler.py | 365 +++...` / ` 1 file changed, 365 insertions(+)` (only merged T21 script).
5. `git diff --stat 6d2819a HEAD -- docs/paper/` -> empty.
6. Drive `results/t21/loso8_scaler.csv` md5 27fc5a927319d616e40ae39b2716ba00, 1296 rows, Mamba
   only — Leader evidence (same); NOT_VERIFIED by worker.
7. `results/t21_rf.log` (main repo): 2 `fold=` lines at local 04:53; RF run in progress.
- Host rename: NREL docs now live under `developer.nlr.gov`; `developer.nrel.gov` fails DNS
  (seen 2026-11-28).
