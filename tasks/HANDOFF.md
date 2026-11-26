# HANDOFF — 2026-11-26 19:30 (local, 12:30 UTC) — leader — T05 on Colab, T08c done

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path: T05 PatchTST E1 A–H, IN_PROGRESS on Colab (full loop: qa after 40/40). 23/40 at 12:28 UTC (A–D done, E 3 seeds; E seed 3 at epoch 30).
- contract: `tasks/STATUS.md` section T05 (acceptance criteria now include the 3 HANDOFF checks of section 7).
- branch / worktree / last commit: main, pushed (this handoff commit on top of `7c8fee7`). No worktrees open. Old branches `worktree-agent-*` remain (`branch -D` needs User OK).

## 2. Verified (command -> real output)
- `py scripts/24_shift_check.py --full` (shift start) -> `tong: 65 PASS, 0 WARN, 0 FAIL, 2 NOT_VERIFIED` (runs.csv no key table; colab drive = status cell).
- Colab status 12:10 UTC -> `Tesla T4, 0 MiB`, 0 jobs, no clone (runtime reset). Setup cell -> `GPU: Tesla T4 | torch 2.14.1+cu130`, `job dang song: khong`, commit `e7c17b2`, chain restarted.
- Colab status 12:28 UTC -> `PatchTST rows/site: {'A': 15, 'B': 15, 'C': 15, 'D': 15, 'E': 9}`, `Tesla T4, 667 MiB`, 3 processes, `ep 30 ... val=0.00479`.
- qa T08c round 2 -> PASS (`24_shift_check --full` 0 FAIL); merged `ea1104d`; docs `7c8fee7`, pushed.

## 3. NOT verified, risks, open findings
- Drive checks (runs.csv PatchTST 120 rows; shap npz modifiedTime 2026-11-25) not run this chat.
- `10_shap.py` has no skip of finished sites: never put it back in the Colab chain.
- Drive `summary_by_site.csv` / `summary_overall.csv` stale: T06 regenerates.
- T08 open TODOs: 4-fold E7/E8 ablation reporting (§2.5.2 TODO); Fig. 1; DOI. qa note: paper DM claims rest on a pilot without saved predictions (T08c qa, outside scope).
- R25c "seed 1 n.s. vs zero-shot" not recomputable.

## 4. Files and commits touched this chat
- `ea1104d` merge T08c (`docs/paper/section2_data_methods.md`); `7c8fee7` T08c contract/QA/DONE + QA-T08c-03 fix (STATUS.md, NHATKY.md, section2). This commit: NHATKY.md, HANDOFF.md.
- Colab MCP notebook: `CpfLXatdw-jL` = setup (clone `/content/_runner`, exec `notebooks/colab_resume.py`), `lIYdn1woOS1n` = status (PatchTST rows/site + run.log tail). IDs change after a reset.

## 5. Environment traps
- Python `py` 3.12 (project override). Open chats from a terminal at `D:\Project\wind_forecast`.
- This chat stays open and keeps Colab alive (cron `263058e4`, every 14 min, session-only). Do not start a second keep-alive while it runs; if this chat is closed, start keep-alive in the new chat.
- The MCP notebook may come back empty after a browser reconnect even when the runtime is alive: run the status cell first, setup only if 0 jobs.
- Edit docs with Edit tool or Python, not PowerShell Set-Content.

## 6. Waiting on the User
- User (2026-11-26): keep Colab running; this chat keeps the keep-alive cron.

## 7. Next step
- do: when `all.done` (40/40): copy Drive `runs.csv` to repo, commit + push, qa T05, RESULTS row. Then T07 (`11_conformal.py --models Mamba,LSTM,Transformer,PatchTST,DLinear`, needs Drive preds -> Colab), T06 aggregate, T08.
- On GPU loss / Colab not reconnectable: commit + push, then `shutdown /s /t 600` (User rule).
- done when: T05 40 PatchTST runs × 3 horizons in `runs.csv`, qa PASS.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. Drive `results/runs.csv` -> expected: PatchTST 15 rows for each of A–H (120), other models 15 per site; ends with newline.
  2. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: unchanged (2026-11-25).
