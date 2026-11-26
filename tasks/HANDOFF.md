# HANDOFF — 2026-11-27 00:18 (local, 2026-11-26 17:18 UTC) — leader — T05 38/40 on Colab, status cell hanging

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path: T05 PatchTST E1 A–H, IN_PROGRESS on Colab (full loop: qa after 40/40). 38/40 at 17:01 UTC (A–G done, H seeds 0–2 done, seed 3 at epoch 10).
- contract: `tasks/STATUS.md` section T05 (acceptance criteria include the 3 checks of section 7).
- branch / worktree / last commit: main, pushed (this handoff commit on top of `8c36d84`). No worktrees open. Old branches `worktree-agent-*` remain (`branch -D` needs User OK).

## 2. Verified (command -> real output)
- Colab status 17:01 UTC -> `PatchTST rows/site: {... 'G': 15, 'H': 9}`, `Tesla T4, 667 MiB`, 3 processes, `[38/40] H PatchTST seed=2 1434s ... 1h RMSE=0.9527`, `ep 10 ... val=0.00308`.
- Colab status at ~17:15 UTC -> no output after 120 s (moved to background, MCP task still pending at handoff).
- Drive search `title = 'run.log'` at 17:18 UTC -> `modifiedTime 2026-11-26T17:08:43Z` (sync loop is every 5 min; 9.5 min old = at least one missed sync, runtime possibly lost — not proven).
- Earlier this chat: shift check `65 PASS, 0 WARN, 0 FAIL, 2 NOT_VERIFIED`; T08c qa PASS, merged `ea1104d`, docs `7c8fee7`; handoff `8c36d84`.

## 3. NOT verified, risks, open findings
- Whether the runtime is alive after 17:08 UTC. If lost, H seed 3 (and 4) must re-run; the chain skips finished keys (Drive `runs.csv` holds 38/40 if the 17:08 sync included seed 2).
- Drive checks (runs.csv PatchTST 120 rows; shap npz modifiedTime 2026-11-25) not run.
- `10_shap.py` has no skip of finished sites: never put it back in the Colab chain.
- Drive `summary_by_site.csv` / `summary_overall.csv` stale: T06 regenerates.
- T08 open TODOs: 4-fold E7/E8 ablation reporting; Fig. 1; DOI.

## 4. Files and commits touched this chat
- `ea1104d` merge T08c; `7c8fee7` T08c DONE; `8c36d84` handoff 1. This commit: NHATKY.md, HANDOFF.md.
- Colab MCP notebook: `CpfLXatdw-jL` = setup (clone `/content/_runner`, exec `notebooks/colab_resume.py`), `lIYdn1woOS1n` = status. IDs change after a reset.

## 5. Environment traps
- Python `py` 3.12 (project override). Open chats from a terminal at `D:\Project\wind_forecast`.
- This chat had keep-alive cron `263058e4` (14 min, session-only). If this chat stays open it keeps firing; do not start a second keep-alive while it runs. If it is closed, start keep-alive in the new chat.
- The MCP notebook may come back empty after a browser reconnect: run the status cell first, setup only if 0 jobs.
- Stale-output check: if a status cell hangs, check Drive `results/run.log` modifiedTime; > 15 min old = runtime lost.

## 6. Waiting on the User
- User (2026-11-26): keep Colab running until T05 is done.

## 7. Next step
- do: check runtime (status cell; if hanging, Drive run.log age). Lost -> reconnect, setup cell, chain resumes H. When `all.done` (40/40): copy Drive `runs.csv` to repo, commit + push, qa T05, RESULTS row. Then T07 (conformal, Colab), T06 aggregate, T08.
- On GPU loss / Colab not reconnectable: commit + push, then `shutdown /s /t 600` (User rule).
- done when: T05 40 PatchTST runs × 3 horizons in `runs.csv`, qa PASS.
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. Drive `results/runs.csv` -> expected: PatchTST 15 rows for each of A–H (120), other models 15 per site; ends with newline.
  2. `py scripts/24_shift_check.py --full` -> expected: 0 FAIL; read every WARN / NOT_VERIFIED.
  3. Drive `results/shap_*.npz` modifiedTime -> expected: unchanged (2026-11-25).
