# Docs rules

Language: project docs (`tasks/*.md`, `README.md`, `CLAUDE.md`) in English. Only `NHATKY.md` and chat replies are Vietnamese.

## Files and owners
| File | Holds | Who edits |
|---|---|---|
| `tasks/STATUS.md` | Goal, approved decisions, Task Contracts, states, attempts, evidence. Single source of truth for tasks. | Leader; Director adds decision lines |
| `tasks/ROADMAP.md` | Stages of the development pipeline: goal, milestones, target dates, done-criteria, current stage. | Leader, after Director/User approval |
| `tasks/RESULTS.md` | Experiment log, one row per run (see below). Created at the first experiment. | Leader, from worker/qa reports |
| `tasks/MEETINGS.md` | All-hands meeting minutes, newest on top (format in `.claude/commands/meeting.md`). Created at the first meeting. | Leader; Director adds recommendation; decision line from User's answer |
| `tasks/ARCHIVE.md` | Finished tasks from past stages, moved out of STATUS.md. | Leader |
| `README.md` | How to install, run, reproduce; outputs. | Worker (inside a task) |
| `NHATKY.md` | Per-chat journal (see `rules/sessions.md`). | Any chat role |
| `tasks/NHATKY-ARCHIVE.md` | NHATKY entries older than 30 days, moved when NHATKY passes ~300 lines. | Any chat role |

## Rules
- Every state change in STATUS.md records who, when (absolute date) and evidence.
- Approved decisions go in STATUS.md under "Approved decisions" with date; do not re-litigate them.
- `CLAUDE.md` section 7 keeps only the stage list and the current stage (3-6 lines); details live in `tasks/ROADMAP.md`.
- Update ROADMAP.md when a stage starts or ends, or a milestone is approved or reprioritized.
- Update `README.md` when run/install commands or outputs change.
- When a stage ends, move its finished tasks from STATUS.md to `tasks/ARCHIVE.md`, leaving a one-line summary.

## RESULTS.md format
```
| date | run_id | task_id | commit | config / seed | data split | metrics | artifacts path | note |
```
- One row per run, never edit old rows (append a correction row instead).
- Metrics with units and the split they were measured on. Failed or aborted runs are logged too.
- STATUS.md test_evidence points to run_ids instead of copying numbers.
