# HANDOFF — 2026-11-27 18:00 (local, 11:00 UTC) — leader — T06 DONE, T08 DONE, next: improvement meeting

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path: none open. T06 DONE (full loop, round 2 recompute), T08 DONE (full loop, Results E1 draft). Next: `/meeting` on the improvement backlog (`docs/limitations_and_improvements.md` section 2), before the Discussion task.
- contract: `tasks/STATUS.md` sections T06, T08 (closed). No new contract written yet.
- branch / worktree / last commit: main `939d210` + this handoff commit, pushed. Leftover worktree `.claude/worktrees/agent-af25ad602b8f31bd8` (branch `worktree-agent-af25ad602b8f31bd8` @ `621aad9`, merged, locked by a dead pid); harmless, shows as shift-check WARN.

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (start of chat) -> `tong: 64 PASS, 1 WARN, 0 FAIL, 2 NOT_VERIFIED` (WARN = leftover worktree).
- Colab (runtime had been reset; Drive remounted 10:12Z) -> `runs.csv rows 600 per (model,site) min/max 15 15 n groups 40 newline True`; shap_*.npz mtimes E1 A-D 2026-11-26T01:34-02:24Z, E1 E-H 2026-11-25T04:31-05:01Z, losoW8 A-H 2026-11-25T14:03-14:38Z (= previous HANDOFF).
- 200 NN preds zipped per site on Colab, downloaded via Drive connector -> md5 8/8 equal Colab; 200 npz in session scratch.
- qa T06 round 2 -> PASS: dm_per_seed 600/600 (DM stat diff 3.2e-06, flags 600/600), dm_tests 120/120, regime 1176/1176 (RMSE diff <= 1.4e-07); RESULTS R31c.
- qa T08 round 2 on `6d2819a` -> PASS; shift check `61 PASS, 4 WARN, 0 FAIL, 2 NOT_VERIFIED`.
- `git diff --stat 1ffa753 6d2819a` -> `docs/paper/section3_results.md | 10 +++++-----` only.
- `py scripts/24_shift_check.py --full` (after T06 docs) -> `63 PASS, 2 WARN, 0 FAIL, 2 NOT_VERIFIED`.
- Colab status cell `lIYdn1woOS1n` last run 10:42:08 UTC -> `Tesla T4, 0 MiB`, `drive mounted: True`, `repo: False`.

## 3. NOT verified, risks, open findings
- Drive checks (runs.csv, shap mtimes) rest on Leader Colab evidence; qa has no Drive access.
- New finding QA-T06-07 LOW (ramp-regime ties at q95, skill shift < 1e-3): disclosed in Section 3.3/3.6.
- Open for paper (outside T08): Section 2.5.4 alignment (day 06:00-17:59, params/training time not reported, 95% level added, 2016 back-test and GAN-phase check promised but not in Results); two Results files both use §3.x numbering (provisional); Discussion not written; QA-T08 INFO PatchTST 6h Welch 7.97 vs 7.96 in an HTML comment.
- Latency (R04) is a single 2026-11-10 run with random weights.
- `24_shift_check` has no runs.csv key table (QA-T05-01) and `check_qa` misses "qa pending" (QA-T06-06).

## 4. Files and commits touched this chat
- `8e2fc16` T06 qa round 2 PASS, R31c, DONE; `6b55183` T08 contract; `1ffa753`, `6d2819a` worker (new `docs/paper/section3_results.md`, line 9 of `section3_results_transfer.md`); `265ba61` merge T08; `939d210` T08 DONE.
- Drive new: `MyDrive/WIND_FORECAST_DATA/tmp_t06/nn_{A-H}.zip` (~34 MB, temporary; delete when convenient, User files only).

## 5. Environment traps
- Python `py` 3.12. Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab: runtime alive (T4 idle), Drive mounted, NO repo clone (runtime reset this chat). Notebook now has: cell 0 `lIYdn1woOS1n` (status: UTC, GPU, Drive), cell 1 `-jTlWOdlfjgi` (drive mount + preds count), cell 2 `DFGi2Qrefqvn` (checks + zips; do not re-run, rewrites tmp_t06). Keep-alive cron dies with this chat: start a new 14-min keep-alive running only the status cell.
- No GPU job is queued; Colab only needed if the improvement meeting approves GPU runs.
- qa hook blocks heredocs and `>`: qa uses single-line `py -I -c`.
- Drive connector downloads land in the session `tool-results` dir.

## 6. Waiting on the User
- none. The improvement meeting decision is delegated to the agent meeting (User 2026-11-25), except anything paid/public/irreversible; L13 (download 2007-2015 data) changes M08 and needs the meeting.

## 7. Next step
- do: (1) start Colab keep-alive (status cell only); (2) `/meeting` on the improvement backlog (`docs/limitations_and_improvements.md` §2: L09 normalization, L06/L11/L07/L10 references, L05 source selection, L13 2007-2015 data, L03/L02), deciding what runs before the Discussion; (3) light/full tasks from the decision; Section 2.5.4 alignment and §3.x renumbering as a small docs task; (4) Discussion task.
- done when: meeting decision recorded in `tasks/MEETINGS.md` and STATUS Approved decisions, with the next Task Contract written.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  2. Drive `results/runs.csv` -> expected: 600 rows, 15 per (model, site), ends with newline.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: as in section 2 (nothing newer).
  4. `git diff --stat 2f2d0ae HEAD -- results/ scripts/` -> expected: empty unless a new task changed them.
  5. `docs/paper/section3_results.md` unchanged since `6d2819a` unless the task edits it (`git diff --stat 6d2819a HEAD -- docs/paper/`).
