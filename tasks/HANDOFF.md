# HANDOFF — 2026-11-27 01:15 (local, 2026-11-26 18:15 UTC) — leader — T05 QA_PASSED, T07 qa FAIL (row gap), F-T05-01 check running

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- T05 PatchTST E1 A-H: QA_PASSED, full loop, awaiting Director APPROVE (User opens `/role director T05`).
- T07 conformal (E11): qa round 1 FAIL on criterion (2) only, attempt_count 1, REVISE pending User choice (a)/(b) (see section 6).
- F-T05-01 (open): `shap_Mamba_0_{A-D}.npz` on Drive modified 2026-11-26 01:34-02:24Z (re-run of T04a), not 2026-11-25. Recompute check running on Colab.
- contract: `tasks/STATUS.md` sections T05, T07.
- branch / worktree / last commit: main, pushed (this handoff commit on top of `d0e12ad`). No worktrees open.

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (start of chat) -> `tong: 65 PASS, 0 WARN, 0 FAIL, 2 NOT_VERIFIED`.
- Colab setup cell -> `GPU: Tesla T4 | torch 2.14.1+cu130`, `job dang song: khong`, clone `8ab4bb9`; chain skipped finished keys: `[39/40] H PatchTST seed=3 -> da co, bo qua`.
- Colab status 18:03 UTC -> `XONG HET`, `[40/40] H PatchTST seed=4  1229s  ep=33 ... 1h RMSE=0.7720  3h RMSE=1.3266  6h RMSE=1.7178`.
- Drive runs.csv (after explicit copy + remount) -> `600`, `{'A': 15, ..., 'H': 15}` PatchTST; local check: 600 rows, newline end, 15 per (model, site), 0 dup keys, 501 old rows identical (max RMSE diff 0.0); git diff +99 / -0.
- Colab `11_conformal.py --selftest` -> `PICP = 0.891 (muc tieu 0.900) -> dat`; full run `exit=0`, `1321 results/conformal.csv` (1320 rows; RF only E-H).
- Colab: `25_shap_check.py --results <Drive results> --tuned <clone>/results/tuned.json --out-dir <Drive>/results/shapchk_F-T05-01` -> `started` (result not read yet).
- qa T05 -> PASS (details STATUS T05). qa T07 -> FAIL criterion (2), others PASS (details STATUS T07).

## 3. NOT verified, risks, open findings
- F-T05-01: compare `Drive results/shapchk_F-T05-01/{shap_completeness,shap_net_importance,shap_provenance}.csv` with repo `results/` copies (R27). Not done. `run.log` there ends with `exit=<code>`.
- T07 NN conformal rows not recomputed by qa (preds only on Colab/Drive). QA-T07-01 MED (row gap + silent skip in `11_conformal.py` lines 83, 86-87); QA-T07-02 LOW (`np.quantile(method="higher")`); QA-T07-03 LOW (PINAW normalised by test range); QA-T07-04 INFO (no "nominal coverage" claim; high-wind tercile and sites G, H worst).
- QA-T05-01 LOW (24_shift_check has no runs.csv key table), QA-T05-02 LOW (12/120 PatchTST rows at 50-epoch cap), QA-T05-03 LOW (PatchTST below persistence at 1h for D, H: disclose).
- Drive `summary_*.csv` stale: T06 regenerates. T08 open TODOs: 4-fold E7/E8 ablation reporting; Fig. 1; DOI.

## 4. Files and commits touched this chat
- `8ab4bb9` Colab pause note; `b3b5476` Drive check + F-T05-01; `5fc2cc9` runs.csv 600 rows (T05); `549bfec` conformal.csv + RESULTS R28/R29; `6633991` T05 qa PASS; `d0e12ad` T07 qa FAIL. This commit: NHATKY.md, HANDOFF.md, STATUS.md.
- Drive new: `results/conformal.csv`, `results/conformal.log`, `results/shapchk_F-T05-01/`.

## 5. Environment traps
- Python `py` 3.12 (project override). Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab MCP notebook cells: `lIYdn1woOS1n` = setup (clone `/content/_runner`, exec `notebooks/colab_resume.py`), `8R8wSfTe8kKD` = scratch/status (content changes each use). The chain finished (`all.done`); the 5-min sync loop still runs. Re-running setup with no job alive restarts the whole chain (all keys skip) — harmless but not needed.
- Keep-alive cron `e23b42ee` (14 min) lives in THIS chat; if this chat is closed, start a new keep-alive in the next Leader chat. Do not run two.
- New files on Drive may not appear in `title contains` search at once; `parentId = '1Wj8vFwqzCwRVlI3eG82ecpQGjU8hRGwR' and createdTime > ...` finds them.
- qa hook blocks heredocs and `>` in qa Bash: qa uses single-line `py -c`.

## 6. Waiting on the User
- Director APPROVE / REVISE for T05 (QA_PASSED).
- T07 choice: (a) regenerate RF A-D val preds on CPU (one site at a time) + make `11_conformal.py` print missing pairs, or (b) accept RF E-H as a disclosed deviation. Both: light task for QA-T07-02/03. Leader recommends (a).
- User (2026-11-27): keep Colab running; no shutdown.

## 7. Next step
- do: (1) read F-T05-01 check output on Drive, compare with R27 CSVs; if numbers differ -> `/meeting` (QA finding may invalidate SHAP results). (2) After Director decision: merge/close T05 (DONE, NHATKY). (3) T07 per User choice, Task Contract with worker + qa. (4) T06 aggregate (needs T05 DONE). Then T08.
- done when: T05 DONE; F-T05-01 closed with evidence; T07 qa PASS.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site) for 5 NN models x A-H, ends with newline; equal to repo `results/runs.csv` after CR strip.
  2. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  3. Drive `results/shapchk_F-T05-01/run.log` -> expected: ends `exit=0`; its 3 CSVs vs repo `results/shap_{completeness,net_importance,provenance}.csv` -> max abs diff reported (expected ~1e-6 if npz content unchanged).
  4. Drive `results/shap_*.npz` modifiedTime -> expected: E-H E1 and all losoW8 2026-11-25; A-D E1 2026-11-26 01:34-02:24Z (F-T05-01); no newer change.
