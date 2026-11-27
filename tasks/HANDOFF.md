# HANDOFF — 2026-11-27 20:00 (local) — leader — M19 + M20 decided, next: T21 ‖ T23

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path: T21 TODO (full loop, contract complete incl. M20 amendment); T23 TODO (full loop, stub only: write the full contract first); T24–T27 TODO stubs; T22 TODO P3.
- contract: `tasks/STATUS.md` sections T21, T22, "T23–T27"; plan `tasks/ROADMAP.md` stage S3b; decisions STATUS Approved decisions M19, M20; minutes `tasks/MEETINGS.md` M19, M20.
- branch / worktree / last commit: main `eddaecd` + this handoff commit, pushed. Leftover worktree `.claude/worktrees/agent-af25ad602b8f31bd8` (merged, harmless, shift-check WARN).

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (start of chat) -> `tong: 64 PASS, 1 WARN, 0 FAIL, 2 NOT_VERIFIED` (WARN = leftover worktree; NOT_VERIFIED = runs.csv key table, Colab status cell).
- Drive search `title contains 'losoW8_' and '.pt'` -> 24 files `losoW8_{A..H}_Mamba_{0,1,2}.pt`, one parent folder; A_0..2 and B_0 created 2026-11-15, 286057 B (others 286093 B, created 11-21/11-24) = untagged 8-fold run renamed per M09 (T21 S0 gate checks it).
- Drive `runs.csv` -> 85118 B, modified 2026-11-26T18:31:14Z; local `results/runs.csv` 85118 B (sizes equal).
- Drive search `shap_` modified > 2026-11-26T03:00Z -> only csv files (18:31Z sync), no `shap_*.npz`.
- `git diff --stat 2f2d0ae HEAD -- results/ scripts/` -> empty; `git diff --stat 6d2819a HEAD -- docs/paper/` -> empty.
- `24_shift_check.py` HEADLINE table covers R21/R21c/R23/R23e/R25/R25c numbers (all PASS in the run above).

## 3. NOT verified, risks, open findings
- 2007–2015 SEA-WTK availability for the 8 sites and the NREL daily cap: not checked (T25 step 1).
- Literature list (M20, 22 papers) read at abstract/snippet level only; read in full and check bibliographic data before citing. TSFM pretraining-corpus overlap with NREL data not checked (WindFM excluded).
- qa did not recompute R21/R23/R25 in M20 (covered by shift check + earlier qa T08a/T19).
- `lightgbm` not installed (T23 needs it; install allowed, CLAUDE.md §8).
- Colab not connected this chat; no keep-alive running; runtime state unknown (last known: T4 idle, no repo clone).
- Earlier open: QA-T05-01 (no runs.csv key table in shift check), QA-T06-06 (`check_qa` misses "qa pending"); latency R04 single run with random weights; Section 2.5.4 alignment and §3.x numbering (small docs task, S6).
- Drive `MyDrive/WIND_FORECAST_DATA/tmp_t06/` (~34 MB) still to delete when convenient.

## 4. Files and commits touched this chat
- `f01dccb` M19 minutes + T21/T22 contracts; `f4482e7` M20 views; `8828f72` M20 decision, T21 amendment, T23–T27 stubs, T22 -> P3; `eddaecd` ROADMAP S3b, CLAUDE.md §7, limitations pointer. Files: `tasks/MEETINGS.md`, `tasks/STATUS.md`, `tasks/ROADMAP.md`, `NHATKY.md`, `CLAUDE.md`, `docs/limitations_and_improvements.md`.

## 5. Environment traps
- Python `py` 3.12. Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab: MCP notebook opens empty after a reset: paste the setup cell from `notebooks/colab_resume.py`; Drive LOSO weights in `results/models_loso/` (Drive), local folder empty; RF LOSO models were never saved (refit on CPU, depth 16, one job at a time).
- qa hook blocks heredocs and `>`: qa uses single-line `py -I -c`.
- Max 2 workers in parallel: T21 (scripts/27, results/loso8_scaler*) and T23 (new files) touch different paths.
- `paper_wind_prediction_ver2.md` untracked old draft: leave it.

## 6. Waiting on the User
- none. M19 and M20 decided by the agent meeting under User delegation (2026-11-25, 2026-11-27). Downloading 2007–2015 (T25) uses the free NREL API; anything paid/public/irreversible still needs the User.

## 7. Next step
- do: (1) write the full T23 contract (pre-registration: references, window, LightGBM grid, Holm family m <= 6); (2) connect Colab (status cell, keep-alive 14 min); (3) spawn worker T21 and worker T23 in parallel (worktrees), then qa each; (4) then T24 contract.
- done when: T21 and T23 DONE with QA PASS, RESULTS rows added, RevIN trigger (T21 source-val mean |Δskill| >= 2 pp at any horizon) evaluated and recorded.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  2. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site), ends with newline (85118 B).
  3. Drive `results/shap_*.npz` modifiedTime -> expected: nothing newer than 2026-11-26T02:24Z.
  4. `git diff --stat 2f2d0ae HEAD -- results/ scripts/` -> expected: only the task's own files.
  5. `git diff --stat 6d2819a HEAD -- docs/paper/` -> expected: empty unless the task edits the paper.
  6. Drive `results/models_loso/losoW8_*.pt` -> expected: 24 files (A–H × seeds 0–2) before T21 runs.
