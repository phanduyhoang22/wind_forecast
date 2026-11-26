# HANDOFF — 2026-11-26 ~09:15 (local, 02:10 UTC) — leader — T05 on Colab, T08b round 2 pending

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path: T05 PatchTST E1 A–H, IN_PROGRESS on Colab (full loop: qa after 40/40). T08b Section 2 alignment, qa FAIL round 1, round 2 pending (full loop).
- contract: `tasks/STATUS.md` sections T05, T08b (round-2 findings QA-T08b-01..-07 listed there).
- branch / worktree / last commit: main `08c1538` (pushed). T08b work on branch `worktree-agent-abfd31a775e2a64a4` (commit `70b6a36`, not merged; worktree `.claude/worktrees/agent-abfd31a775e2a64a4` still exists). QA worktree `.claude/worktrees/agent-a13e8058accfc2532` left behind, removable.

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (start of chat) -> `tong: 46 PASS, 2 WARN, 0 FAIL, 2 NOT_VERIFIED`, exit 0.
- Colab setup cell (`/content/_runner` clone + exec `notebooks/colab_resume.py`) -> `GPU: Tesla T4 | torch 2.14.1+cu130`, commit `6807cab`.
- Drive check cell -> all result CSVs end with newline and row counts match the clone; `runs.csv` 528 rows on Drive (git 501); PatchTST A–C 15 rows each, D 3; 16 SHAP npz finite; losoW8 24 models, globalW8 3.
- Status cell 02:10:06 UTC -> `[18/40] D PatchTST seed=2 1361s ... 1h RMSE=0.6333`; now on run 19/40, ~18–23 min/run.
- qa T04 round 2 -> PASS (merged `d406f57`); R27c Colab recompute -> completeness max diff 6.3e-08, provenance 4.8e-06 m/s, 300/300 net rows exact; seed 0 vs 1 preds mean diff 0.21–0.38 m/s.
- qa T08a -> PASS (merged `a56b751`). qa T08b -> FAIL round 1 (3 MED, 4 LOW, wording only).

## 3. NOT verified, risks, open findings
- `10_shap.py` has no skip of finished sites: never put it back in the Colab chain (removed from `notebooks/colab_resume.py` in `918d299`).
- Drive `summary_by_site.csv` / `summary_overall.csv` are stale (all `*_std` NaN, 60 rows): do not use; T06 regenerates.
- T08b open: R22/R23 Wilcoxon variant has no committed script (new [TODO] in 2.6); whether to report 4-fold E7/E8 ablation; Holm family wording vs `08_aggregate.py`.
- R25c "seed 1 n.s. vs zero-shot" not recomputable (no per-seed CSV).
- PowerShell 5.1 `Get-Content -Raw | Set-Content -Encoding utf8` corrupted STATUS.md once (fixed before commit). Edit docs with the Edit tool or Python, not Set-Content.

## 4. Files and commits touched this chat
- `d406f57` merge T04 round 2 (`scripts/25_shap_check.py`, `results/shap_{completeness,net_importance,provenance}.csv`).
- `918d299` T04 DONE, R27, `notebooks/colab_resume.py` (T04a/T04b removed from chain).
- `c81d92b` R27c. `a56b751` merge T08a (`docs/paper/section3_results_transfer.md`). `b1c644d` T08a DONE, R27d, draft fixes -01/-03.
- `08c1538` T08b QA FAIL round 1. This handoff commit: NHATKY.md, HANDOFF.md.

## 5. Environment traps
- Python `py` 3.12 (project override). Open chats from a terminal at `D:\Project\wind_forecast`.
- Colab MCP notebook cells: 1 = setup (`lIYdn1woOS1n`), 2 = status (`XwL1rHKVc26i`), 3 = scratch check (`xr3q3WhJdFHe`), 4 = scratch (`bf7EJaxCeGcG`). T05 runs as a standalone bash job (`07_run_benchmark.py --models PatchTST`, then `touch results/all.done`); the Drive sync loop is alive.
- In a Colab `subprocess` shell, `pkill -f <pattern>` kills its own shell if the pattern is in the command line.
- Status cell prints E1 test RMSE (fine for E1; never print few-shot test scores).

## 6. Waiting on the User
- User asked (2026-11-26): keep the Colab runtime alive with a status cell every 14 min until this Colab session ends; token budget low, no new work in this chat.

## 7. Next step
- do: keep-alive status cell every ~14 min. When `all.done` (40/40): copy `runs.csv` (and models/preds stay on Drive) to the repo, commit + push, qa T05, log RESULTS row. Then T08b round 2 (send the same worker branch the QA-T08b findings), T07 conformal, T06 aggregate, T08.
- On GPU loss / Colab not reconnectable: commit + push, then `shutdown /s /t 600` (User rule).
- done when: T05 40 PatchTST runs × 3 horizons in `runs.csv`, qa PASS.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. Drive `results/runs.csv` -> expected: PatchTST 15 rows for each of A–H (120), other models unchanged at 15 per site; ends with newline.
  2. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: unchanged (not rewritten this session).
