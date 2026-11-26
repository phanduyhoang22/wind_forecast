# HANDOFF — 2026-11-26 18:20 (local, 11:20 UTC) — leader — T05 on Colab, T08b/T19/T20 done

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path: T05 PatchTST E1 A–H, IN_PROGRESS on Colab (full loop: qa after 40/40). 20/40 at 10:18 UTC (A–D done; E next).
- contract: `tasks/STATUS.md` section T05.
- branch / worktree / last commit: main (this handoff commit on top of `a21b4d9`), pushed. No worktrees open. Old branches `worktree-agent-*` remain (not deleted: `branch -D` needs User OK).

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (shift start) -> `tong: 47 PASS, 1 WARN, 0 FAIL, 2 NOT_VERIFIED`.
- Colab status 09:47 UTC -> `Tesla T4, 0 MiB`, no `/content/wind_forecast` (runtime reset); setup cell -> `GPU: Tesla T4 | torch 2.14.1+cu130`, `job dang song: khong`, commit `01950ac`, chain restarted.
- Drive check cell 09:52 UTC -> 67 result CSVs: drive rows = clone rows, all end with newline; `runs.csv` 537 rows; DLinear/LSTM/Mamba/Transformer 15 per site A–H; PatchTST A–C 15, D 12, E–H 0; 16 SHAP npz finite, modified 2026-11-25; preds 219, models 557, preds_loso 264, models_loso 150, preds_wind 40, models_wind 120 (drive = clone).
- Colab status 10:18 UTC -> `PatchTST rows/site: {'A': 15, 'B': 15, 'C': 15, 'D': 15}`, `[20/40] D PatchTST seed=4 1086s ... 1h RMSE=0.5320`, next run training.
- qa T08b round 2 -> PASS (merged `730cfc9`); qa T19 -> PASS, independent recompute of R22/R23 (merged `25fb482`); qa T20 -> PASS (merged `8594f40`).
- `py scripts/24_shift_check.py` on main after T20 merge -> `tong: 59 PASS, 1 WARN, 0 FAIL, 2 NOT_VERIFIED`.

## 3. NOT verified, risks, open findings
- `10_shap.py` has no skip of finished sites: never put it back in the Colab chain.
- Drive `summary_by_site.csv` / `summary_overall.csv` stale: T06 regenerates.
- T08 carry-over: QA-T08b-08 (2.5.3 post-hoc list order), -09 (cite RESULTS R20, not `README.md:106`); Section 2.6 R22/R23 TODO -> cite `scripts/26_feature_set_stats.py`, same-cross 6h = 17.9 (R23e); state exact Wilcoxon n=8 floor (Holm 0.023); M01 DM lag chosen after pilot DM results (disclose).
- Still open TODOs: 4-fold E7/E8 ablation reporting; Fig. 1; DOI.
- R25c "seed 1 n.s. vs zero-shot" not recomputable.
- The WARN in the last shift check was not read.

## 4. Files and commits touched this chat
- `e0598af` STATUS T05/T08b; `730cfc9` merge T08b (`docs/paper/section2_data_methods.md`, `section3_results_transfer.md`); `e1606d7` T08b DONE.
- `9acc313` T19 contract, T02 closed; `25fb482` merge T19 (`scripts/26_feature_set_stats.py`, `results/feature_set_stats.csv`); `8db0469` T19 DONE + RESULTS R23e.
- `8594f40` merge T20 (`scripts/24_shift_check.py`); `a21b4d9` T20 DONE. This commit: NHATKY.md, HANDOFF.md.

## 5. Environment traps
- Python `py` 3.12 (project override). Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab MCP cells now: `lIYdn1woOS1n` = setup (clones `/content/_runner`, execs `notebooks/colab_resume.py`), `ki6QDcWcQFoO` = status (PatchTST rows/site + run.log tail), `rr24v-UeRV_S` = Drive integrity check. IDs change after a runtime reset (notebook comes back empty).
- The previous chat stays open and keeps Colab alive (cron every 14 min). Do not run two keep-alive loops on the same notebook; if that chat is closed, start keep-alive here.
- Edit docs with Edit tool or Python, not PowerShell Set-Content.

## 6. Waiting on the User
- User asked (2026-11-26): keep Colab alive; the old chat keeps the keep-alive cron running.

## 7. Next step
- do: when `all.done` (40/40): copy Drive `runs.csv` to repo, commit + push, qa T05, RESULTS row. Then T07 (`11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear`, needs Drive preds -> run on Colab), T06 aggregate, T08 (with carry-overs above).
- On GPU loss / Colab not reconnectable: commit + push, then `shutdown /s /t 600` (User rule).
- done when: T05 40 PatchTST runs × 3 horizons in `runs.csv`, qa PASS.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. Drive `results/runs.csv` -> expected: PatchTST 15 rows for each of A–H (120), other models 15 per site; ends with newline.
  2. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: unchanged (2026-11-25).
