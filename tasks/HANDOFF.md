# HANDOFF — 2026-11-28 06:06 (local) — leader — T21 RF done, T23 phase A merged, T25 step 1 done

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- T21 (full loop) IN_PROGRESS: phase A merged `2ef6c47`; phase B Mamba done on Colab (R35, Drive only); RF done locally 24/24 (R36, `results/loso8_scaler.csv` RF only, 1296 rows, md5 ce48458df70d04ec71bf9caf9cc43938, committed `14bb563`). Next: copy Drive Mamba CSV via Colab, merge, `--stats`, RevIN trigger, qa phase B, Director approve.
- T23 (full loop) IN_PROGRESS: phase A qa round 2 PASS on `55af237`, merged `32b3589` (attempt 2). Phase B (LightGBM E1 -> LOSO) not started (User: no LightGBM tonight).
- T25 step 1 (light) DONE: `docs/t25_availability.md`, qa PASS round 2, merge `5a20aa8`. Step 2 (hash checkpoints/configs/eval/stats/claims) after T21/T23.
- contract: `tasks/STATUS.md` sections T21, T23, T24–T27 (T25 step 1 contract there); RESULTS R32–R36.
- branch / last commit: main `14bb563` + this handoff commit, pushed.

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (start) -> `tong: 64 PASS, 1 WARN, 1 FAIL, 3 NOT_VERIFIED` (FAIL = references.csv, QA-T23-01); after T23 merge -> `tong: 63 PASS, 2 WARN, 0 FAIL, 3 NOT_VERIFIED`.
- Colab cell (2026-11-28, Drive mounted) -> `GPU: Tesla T4 | torch 2.14.1+cu130`; `runs.csv bytes 85118 rows 600 ends_nl True | per (model,site) counts: [15]`; `shap npz newest: 2026-11-26T02:24:22`; `t21 md5 27fc5a927319d616e40ae39b2716ba00 rows 1296 models ['Mamba']`.
- RF log at end -> `fold=24 bad=0 alive=False`; last line `fold=H RF seed=2  170s  S0-R21 max|d|=1.11e-16 ...`.
- `results/loso8_scaler.csv` -> `1296 ... {'RF': 1296}`, md5 `ce48458df70d04ec71bf9caf9cc43938`, splits test+val, variants S0/S1/S2_DB/S2_TN, 8 folds, seeds 0–2.
- qa T23 round 2 -> PASS (select_units A,D + SystemExit; negative runs rc=1 no file; d_rmse `secondary`; merge 86fdd51 content = 8f26658; P1 N=1 max|d| 0.0 on 39 rows; selftests `dat`; lightgbm 4.7.0).
- qa T25 round 2 -> PASS (probe A/2007 HTTP 200, 35,040 rows; no secrets; first local day lost only per built series by `03_build_dataset.py` dropna, leap days kept).

## 3. NOT verified, risks, open findings
- T21 `--stats` not run; RevIN trigger not evaluated; Mamba rows only on Drive `MyDrive/WIND_FORECAST_DATA/results/t21/loso8_scaler.csv` (file id 1TP2cguiIcoWv3Qe36tdXav6R6mbTO4OD, md5 27fc5a92). Merge = row-concat (keys disjoint by model) into `results/loso8_scaler.csv`.
- Descriptive only (R36): S2 variants much worse than S0 for RF (1h mean test RMSE 1.13–1.17 vs 0.69 m/s); interpret after stats.
- QA-T23-04 (low): LightGBM resume key lacks the source pool -> LOSO only with default 8 sites, fresh CSV (STATUS rule). LightGBM timings only with no other CPU job.
- T25: 2008–2015 and sites B–H not probed (docs only). 2016 PROVENANCE section does not state the 2016-01-02 start (disclosure item).
- git author email equals the NREL email and is on every public commit (User informed, no action taken).
- Earlier open: literature full-text check, QA-T05-01, QA-T06-06, Drive `tmp_t06/` cleanup, test scores seen before code QA (R32, QA-T21-03) to disclose.

## 4. Files and commits touched this chat
- `5a20aa8` merge T25 step 1 (`docs/t25_availability.md`); `0439458` T25 docs; `32b3589` merge T23 phase A (`scripts/28_references.py`, `scripts/29_lgbm.py`, `results/references.csv`); `99ea95b` T23 docs; `43a516c` T21 note; `14bb563` RF results (`results/loso8_scaler.csv`, RESULTS R36); this handoff commit. Files: `tasks/STATUS.md`, `tasks/RESULTS.md`, `NHATKY.md`, `tasks/HANDOFF.md`.

## 5. Environment traps
- Python `py` 3.12. Open chats from a terminal at `D:\Project\wind_forecast`.
- Background jobs must be started detached (`Start-Process ... -RedirectStandardOutput`), or they die with the chat. Their logs are read with Get-Content (Select-String misreads the encoding).
- 11 worktrees open (merged: a33af13 T23 old, a35e331 T23, af6c794 T25, a6bd979 T21; qa detached: a556df2, a58b133, ac25424, ad83b5a, ae69049; old af25ad6). Clean without `branch -D`/`rm -rf` (guard).
- Colab notebook resets empty; minimal cell = mount Drive + checks (no CHAIN re-run). No keep-alive now.
- Local-only, untracked: `results/t21_rf.log`, `results/t21_rf.err`, `paper_wind_prediction_ver2.md` (old draft).

## 6. Waiting on the User
- none (agent-meeting delegation in force; paid/public/irreversible still need the User).

## 7. Next step
- do: (1) connect Colab, copy Drive `results/t21/loso8_scaler.csv` into the repo (e.g. via a Colab cell writing to a git-free path, then download; or Drive connector), check md5 27fc5a92, append Mamba rows to `results/loso8_scaler.csv`; (2) `py scripts/27_loso_scaler.py --stats` -> `results/loso8_scaler_stats.csv`, record RevIN trigger (mean |Δskill| >= 2 pp on source-site val, Mamba only); (3) qa T21 phase B (recompute stats), Director approve, RESULTS row; (4) T23 phase B: LightGBM E1 (detached, no other CPU job) -> LOSO all 8 sites, fresh CSV -> `--stats`, qa phase B; (5) a claim change vs M13 or Mamba loss to LightGBM/smart persistence -> `/meeting`; (6) then T24 (GPU) and T25 step 2.
- done when: T21 and T23 DONE with qa PASS, RESULTS rows, RevIN trigger recorded.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  2. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site), ends with newline (85118 B).
  3. Drive `results/shap_*.npz` modifiedTime -> expected: nothing newer than 2026-11-26T02:24Z.
  4. `git diff --stat 2f2d0ae HEAD -- results/ scripts/` -> expected: only task files (`27_loso_scaler.py`, `28_references.py`, `29_lgbm.py`, `references.csv`, `loso8_scaler.csv`, + the current task's own).
  5. `git diff --stat 6d2819a HEAD -- docs/paper/` -> expected: empty unless the task edits the paper.
  6. Drive `results/t21/loso8_scaler.csv` md5 -> expected: `27fc5a927319d616e40ae39b2716ba00`, 1296 rows, Mamba only.
  7. local `results/loso8_scaler.csv` before merge -> expected: md5 `ce48458df70d04ec71bf9caf9cc43938`, 1296 rows, RF only; after merge 2592 rows, no duplicate (fold, model, seed, variant, split, site, horizon) keys.
