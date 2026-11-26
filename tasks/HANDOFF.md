# HANDOFF — 2026-11-27 01:25 (local, 2026-11-26 18:25 UTC) — leader — T07 round 2 worker mid-run (RF A-D val), M17 decided

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- T07 conformal round 2 (M17 option A, User 2026-11-27), full loop, attempt_count 1 -> round 2 IN_PROGRESS. Contract: `tasks/STATUS.md` T07 "ROUND 2 contract".
- T05 DONE (Director APPROVE `5f8790d`, Leader DONE `7b6531b`).
- F-T05-01: completeness on current npz = R27 to 3 decimals (STATUS T05); full CSV diff + qa close still open. SHAP numbers stay blocked for T08 until closed.
- branch / worktree / last commit: main `aba8221` + this handoff. Worker worktree `D:\Project\wind_forecast\.claude\worktrees\agent-af25ad602b8f31bd8`, branch `worktree-agent-af25ad602b8f31bd8`, commit `b0a73d1 fix(T07): conformal exact quantile, train-range PINAW, fail on missing preds` (11_conformal.py fixes; NOT pre-checked, NOT qa'd).

## 2. Verified (command -> real output)
- Colab status 18:20 UTC -> `3 MiB` GPU idle, shapchk `run.log` ends `exit=0`, `0 file du doan luu bi thieu`.
- shapchk pooled completeness E1 A-H `0.094/0.072/0.073/0.064/0.087/0.082/0.072/0.066`, losoW8 `0.085/0.079/0.076/0.069/0.079/0.073/0.066/0.072` = R27.
- Worker scratch (`C:\Users\User\AppData\Local\Temp\claude\8e7e329b3f27fbe2\466e9487-1ea2-478e-b411-2c8b00b99d32\scratchpad\t07`) at 01:23 local: `gate/` (A seed 0), `A/preds/A_RF_0..4.npz`, `B/models/B_RF_0_val.npz`, `B_RF_1_val.npz` -> gate passed presumably (worker went on), B running; one python process ~2.4 GB RAM. Worker report NOT received.
- M17 minutes + decision: `tasks/MEETINGS.md` M17; Approved decisions line in STATUS.

## 3. NOT verified, risks, open findings
- Worker gate result (array_equal + node count) not seen by Leader: read `scratch\t07\gate\runs.csv` vs `results/runs_rf.csv` and compare npz yourself.
- Whether the background RF job survives this chat closing: unknown. If `B/C/D` dirs are incomplete, re-run missing sites one per command (see section 7).
- Nothing copied to `results/models/` on main yet (check worktree `results/models/{A-D}_RF_*_val.npz`).
- Open findings: QA-T07-01..04 (STATUS T07); QA-T05-01..03 (paper disclosure: PatchTST 50-epoch cap 12/120, below persistence 1h D/H); T08 TODOs (E7/E8 ablation, Fig. 1, DOI); Drive summary_*.csv stale (T06).

## 4. Files and commits touched this chat
- main: `8ab4bb9`, `b3b5476`, `5fc2cc9` (runs.csv 600), `549bfec` (conformal.csv R28/R29), `6633991`, `d0e12ad`, `3b57ef3` (handoff 1), `7b6531b` (T05 DONE), `c52719d`/`398d00f` (M17), `aba8221` (NHATKY).
- Drive new: `results/conformal.csv`, `conformal.log`, `results/shapchk_F-T05-01/` (3 CSV + run.log).

## 5. Environment traps
- Python `py` 3.12. Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab alive (T4, idle, chain finished, 5-min sync loop running). Cells: `lIYdn1woOS1n` setup, `8R8wSfTe8kKD` scratch/status. Keep-alive cron `e23b42ee` dies with this chat: start a new 14-min keep-alive in the next chat (User keeps Colab; no shutdown).
- RF depth 24: one site per process (MemoryError risk on 16 GB).
- `07_run_benchmark.py --out <dir>/runs.csv` writes models/ and preds/ next to --out (results/ untouched); fresh --out = no skip.
- qa hook blocks heredocs and `>`: qa uses single-line `py -c`.

## 6. Waiting on the User
- none (M17 decided). User keeps Colab running.

## 7. Next step
- do: (1) check worker state: scratch `t07/{A,B,C,D}` each with 5 `preds/*_RF_*.npz` and 5 `models/*_val.npz`; if missing, run per site in the worktree: `py scripts/07_run_benchmark.py --models RF --sites X --seeds 5 --out <scratch>\t07\X\runs.csv`. (2) verify 20/20 test preds `np.array_equal` to `results/preds/X_RF_s.npz` and node count = `runs_rf.csv`; copy 20 val npz into the worktree `results/models/`, commit on the worker branch. (3) Leader pre-check `b0a73d1` diff (allowed_paths only), selftest; spawn qa with the full round 2 contract. (4) qa PASS -> merge to main, Colab re-run `11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear,RF` (pull main in /content/wind_forecast first; copy the 20 new RF val npz there), 1440 rows, RESULTS correction row for R29 + new row. (5) close F-T05-01 (full CSV diff). (6) T06.
- done when: T07 conformal.csv 1440 rows, qa PASS, Director APPROVE.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site) for 5 NN models x A-H, ends with newline.
  2. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: E1 E-H and losoW8 A-H 2026-11-25; E1 A-D 2026-11-26 01:34-02:24Z (F-T05-01); nothing newer.
  4. 20/20 RF A-D re-run test preds `np.array_equal` to existing `results/preds/` -> expected: all True (else STOP, meeting).
