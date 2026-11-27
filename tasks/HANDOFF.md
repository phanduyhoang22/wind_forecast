# HANDOFF — 2026-11-27 23:40 (local) — leader — T21 phase B running, T23 qa pending

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- T21 (full loop) IN_PROGRESS: phase A code qa PASS, merged `2ef6c47`; phase B Mamba done on Colab (R35); RF refit running locally in background (`py -u scripts/27_loso_scaler.py --models RF --seeds 3`, log `results/t21_rf.log`, writes `results/loso8_scaler.csv`), started this chat.
- T23 (full loop) IN_PROGRESS: phase A code done on branch `worktree-agent-a33af13b679889703` @ `8f26658` (not merged, not pushed); qa phase A was running in background when this chat closed: its report is lost with the chat -> re-run qa T23 phase A.
- contract: `tasks/STATUS.md` sections T21, T23 (incl. "Leader clarifications" / "Leader decisions" lines); RESULTS R32–R35.
- branch / last commit: main `4de2c81` + this handoff commit, pushed. Remote branch `t21-phaseA` (= 20da2d7, used by Colab).

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (start) -> `tong: 64 PASS, 1 WARN, 0 FAIL, 2 NOT_VERIFIED`.
- Colab cell (Drive) -> `runs.csv bytes 85118 rows 600 ends_nl True`; `per (model,site) counts: [15]`; `shap npz newest: 2026-11-26T02:24:22`; `losoW8 pt: 24`; `GPU: Tesla T4 | torch 2.14.1+cu130`.
- Colab T21 Mamba -> `done: True`, 24 `fold=` lines, no `DUNG`/`Traceback`, `1296` rows, md5 `27fc5a927319d616e40ae39b2716ba00`; log lines e.g. `fold=E Mamba seed=2 ... S0-R21 max|d|=0.00e+00`.
- qa T21 phase A -> PASS (criteria 2, 3, 4; criterion 1 logic; RF fold A seed 0 `S0-R21 max|d|=0.00e+00`; stats on R21/R16 reproduce `results/transfer_stats.csv`). Findings QA-T21-01 (low: rows written before the stop check; never just re-run after a stop), -02 (info: source-val check only counts rows), -03 (info: RF fold A test RMSE seen, disclose).
- worker T23 -> `28_references.py --selftest` `dat (N=1 vs baselines.csv: lech max 4.44e-16 m/s)`; `29_lgbm.py --selftest` `dat`; timing pilot 194.0 s, 5.41 GB -> projection 33.4 h -> `--lag-step 4` (R34).

## 3. NOT verified, risks, open findings
- Mamba T21 CSV is only on Drive `MyDrive/WIND_FORECAST_DATA/results/t21/loso8_scaler.csv` (md5 27fc5a92); must be merged (row-concat, keys disjoint by model) into local `results/loso8_scaler.csv` after the RF run, then check md5 of the Drive copy.
- RF run result unknown at close (expected ~1.5–3 h, ~2.2 GB RAM). If it prints `DUNG`, stop; do not re-run on the same file (QA-T21-01).
- T23 qa phase A not finished; LightGBM full runs not started (E1 ~3–3.5 h, LOSO ~8–10 h, LOSO RAM 5–6 GB not measured). Never run LightGBM in parallel with T21 RF.
- `--stats` for T21 not run; RevIN trigger not evaluated yet.
- Test scores seen before code QA: R32 (fold H RF) and QA-T21-03 (fold A RF); design was committed before (aaa048b); disclose.
- Earlier open: 2007–2015 availability (T25), literature full-text check, QA-T05-01, QA-T06-06, Drive `tmp_t06/` cleanup.
- Colab: keep-alive cron cancelled (GPU job done); runtime will idle out. Not needed until T24.

## 4. Files and commits touched this chat
- `aaa048b` T23 pre-registered contract, T21 check (vi); `0bd0565` Leader clarifications T21/T23, R32–R34; `2ef6c47` merge T21 script `scripts/27_loso_scaler.py`; `4de2c81` R35, T21 state; this handoff commit. Files: `tasks/STATUS.md`, `tasks/RESULTS.md`, `scripts/27_loso_scaler.py`, `NHATKY.md`, `tasks/HANDOFF.md`.

## 5. Environment traps
- Python `py` 3.12. Open chats from a terminal at `D:\Project\wind_forecast`.
- Worktrees open: `agent-af25ad602b8f31bd8` (old), `agent-a6bd9797059b684f5` (T21, merged), `agent-a33af13b679889703` (T23, NOT merged), `agent-ac2542476bb6056b9` (qa). Remove merged ones without `branch -D`/`rm -rf` (guard).
- Colab notebook resets empty; minimal setup cell = mount Drive, clone, copy kernel (do not re-run the old CHAIN). Never re-run a clone cell while a job runs.
- `results/t21_rf.log` is a local log (do not commit unless allowed).

## 6. Waiting on the User
- none (agent-meeting delegation in force; paid/public/irreversible still need the User).

## 7. Next step
- do: (1) wait for the RF run, read `results/t21_rf.log`; (2) download Drive `results/t21/loso8_scaler.csv`, append its Mamba rows to `results/loso8_scaler.csv`; (3) `py scripts/27_loso_scaler.py --stats` -> `results/loso8_scaler_stats.csv`, record RevIN trigger; (4) qa T21 phase B (recompute stats), Director approve, commit results, RESULTS row; (5) re-run qa T23 phase A, merge, then LightGBM E1 -> LOSO (one at a time), `--stats`, qa phase B; (6) a claim change vs M13 or a Mamba loss to LightGBM/smart persistence -> `/meeting`.
- done when: T21 and T23 DONE with qa PASS, RESULTS rows, RevIN trigger recorded.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  2. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site), ends with newline (85118 B).
  3. Drive `results/shap_*.npz` modifiedTime -> expected: nothing newer than 2026-11-26T02:24Z.
  4. `git diff --stat 2f2d0ae HEAD -- results/ scripts/` -> expected: only the task's own files (+ `scripts/27_loso_scaler.py` merged).
  5. `git diff --stat 6d2819a HEAD -- docs/paper/` -> expected: empty unless the task edits the paper.
  6. Drive `results/t21/loso8_scaler.csv` md5 -> expected: `27fc5a927319d616e40ae39b2716ba00`, 1296 rows, Mamba only.
  7. `results/t21_rf.log` -> expected: 24 `fold=` RF lines, no `DUNG`.
