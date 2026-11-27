# HANDOFF — 2026-11-27 17:25 (local, 10:25 UTC) — leader — T07 DONE, F-T05-01 closed, T06 QA_PASSED, M18 decided

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- T06 round 2 (full loop), state QA_PASSED, round 2 contract TODO (M18 = A + B(1)): independent recompute of NN DM + NN regime rows, then Director APPROVE -> DONE.
- contract: `tasks/STATUS.md` section T06 ("ROUND 2 contract (TODO)"); decision: STATUS Approved decisions M18, `tasks/MEETINGS.md` M18.
- branch / worktree / last commit: main `d7b1d1d` + this handoff commit. No open task branch. Leftover worktree `.claude/worktrees/agent-af25ad602b8f31bd8` (branch `worktree-agent-af25ad602b8f31bd8`, merged) is locked by a dead pid; harmless.
- Done this chat: T07 DONE (conformal 1440 rows, R30, R29c); F-T05-01 CLOSED (qa PASS; R27 SHAP usable in T08).

## 2. Verified (command -> real output)
- RF C, D re-run (worktree, `07_run_benchmark.py --models RF --sites X --seeds 5 --out <scratch>\t07\X\runs.csv`) -> `C exit=0`, `D exit=0`, 5 preds + 5 val each.
- `py <scratch>\verify_rf.py <old scratch>\t07` -> 20/20 `array_equal True`, params equal, `total mismatch 0`.
- Colab `11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear,RF` -> `exit=0`; 1440 rows, 240 per model, 0 dup, finite; md5 `58d708db8bec8b0ebb886366ce520ca3` on Drive = repo.
- Colab 09:38Z: Drive `runs.csv` 600 rows, 15-15 per (model, site), newline True; `shap_*.npz` times: losoW8 A-H 2026-11-25T14:03-14:38Z, E1 E-H 2026-11-25T04:31-05:01Z, E1 A-D 2026-11-26T01:34-02:24Z.
- shapchk CSV diff vs repo R27 -> max abs diff 2.0e-09 / 2.6e-10 / 0.0 (qa PASS).
- Colab T06 (`08_aggregate.py --selftest`, `08_aggregate.py`, `14_regime.py`) -> `exit=0`; summary_by_site 144, overall 18, cost 6, dm_tests 120, dm_per_seed 600, dm_per_seed_summary 120 (n=5), regime 1176; 0 NaN/inf.
- `py scripts/24_shift_check.py --full` (after `58a2648`) -> `62 PASS, 3 WARN, 0 FAIL, 2 NOT_VERIFIED` (qa round 2: 63/2/0/2).
- Colab status cell last run 10:04:29 UTC -> `3 MiB` (T4 idle).

## 3. NOT verified, risks, open findings
- NN DM rows (`dm_per_seed.csv`, `dm_tests.csv`) and NN regime rows (`regime.csv`) not independently recomputed: T06 round 2.
- Open findings: QA-T06-02..-06 (paper disclosures, bound by M18); QA-T07-04 (no nominal-coverage claim), QA-T07-06 INFO; QA-T05-01..03 (paper disclosure); T08 TODOs (E7/E8 ablation, Fig. 1, DOI).
- `24_shift_check` `check_qa` does not catch "qa pending" rows (QA-T06-06); R31 note still says "qa pending" (do not edit old row; add correction row when T06 is APPROVED).
- Colab notebook has helper cells 2-5 (setup/conformal/T06) that delete and re-clone `/content/wind_forecast` if re-run: run only the status cell `npN7bCc2XqnR` and new cells. Twice this chat a wrong cell was run (no harm, verified).

## 4. Files and commits touched this chat
- main: `621aad9` (20 RF A-D val npz), `dc6587b` (merge T07), `4335e88`, `f799e33` (conformal.csv 1440, R29c/R30, T07 DONE), `917953a` (F-T05-01 closed), `2f2d0ae` (T06 results, R31), `58a2648` (R31 paths), `b87ec0d`, `eef7308` (M18 minutes), `d7b1d1d` (M18 decided, T06 round 2 contract).
- Drive new: `results/conformal.csv`, `conformal.log` (overwritten), `results/t06/` (7 CSV + `t06.log`).

## 5. Environment traps
- Python `py` 3.12. Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab: runtime alive (T4 idle), Drive mounted, `/content/wind_forecast` cloned at 4335e88 with Drive `preds/` + `models/` copied in (240 + 240 npz). No 5-min sync loop running. Status cell id `npN7bCc2XqnR`. Keep-alive cron dies with this chat: start a new 14-min keep-alive.
- Drive downloads via connector land in the session `tool-results` dir (not context); copy them from there.
- Drive NN preds: `MyDrive/WIND_FORECAST_DATA/results/preds/` (240 npz incl. 40 RF). qa has no Drive access: Leader must download into a scratch dir outside the repo.
- qa hook blocks heredocs and `>`: qa uses single-line `py -c`.

## 6. Waiting on the User
- none (M18 decided by the agent meeting under User delegation).

## 7. Next step
- do: (1) start Colab keep-alive; (2) download the 200 NN npz (`{A-H}_{Mamba,LSTM,Transformer,PatchTST,DLinear}_{0-4}.npz`) from Drive `results/preds/` into a scratch dir (connector `download_file_content`, or zip on Colab and download one file); check count and names; (3) spawn qa with the T06 round 2 contract (own recompute of per-seed DM + Holm, ensemble DM, NN regime rows vs committed CSVs); (4) on qa PASS: Director APPROVE T06, RESULTS correction row closing "qa pending" for R31, T06 DONE; (5) then T08 (E1 section under M18 wording rules).
- done when: T06 round 2 qa PASS and Director APPROVE recorded in STATUS.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  2. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site), ends with newline.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: as in section 2 (nothing newer).
  4. 200 downloaded NN npz -> expected: 5 per (site, model), `y_pred` shape (26161, 3) = y_test.
  5. Independent recompute vs committed `dm_per_seed.csv` / `dm_tests.csv` / `regime.csv` -> expected: RMSE/skill diff <= 1e-6, DM stat diff <= 1e-4, win/loss flags 600/600 and better/worse 120/120 identical.
