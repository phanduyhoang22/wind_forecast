---
description: Close the current ROADMAP stage - archive its tasks, update ROADMAP.md and CLAUDE.md, journal, propose a meeting
argument-hint: <stage, e.g. "Stage 2 (implement)"; empty = current stage>
---

Stage: $ARGUMENTS (empty: the current stage in `tasks/ROADMAP.md`). Leader only. Follow `.claude/rules/docs.md`.

1. **Check.** Every milestone/task of the stage is `DONE` in `tasks/STATUS.md` (merged, QA `PASS`, approved), and the User approved ending the stage (delegation counts if recorded). Otherwise stop: list what is missing and ask.
2. **Archive.** Move the stage's finished tasks from STATUS.md to `tasks/ARCHIVE.md` (create with `# ARCHIVE` and one intro line if missing), under `## Stage <n> (<name>) — closed YYYY-MM-DD`, task blocks unchanged.
   In STATUS.md leave one line per stage: `Archived: T01 (<summary>, merge <hash>), ... -> tasks/ARCHIVE.md`.
   Add a dated line to "Approved decisions": stage closed, tasks archived, next stage starts, who approved.
3. **ROADMAP.md.** Mark the stage `(done YYYY-MM-DD)`; mark the next stage as current (none left: say all stages done).
4. **CLAUDE.md section 7.** Update the current stage (3-6 lines, details stay in ROADMAP.md). No project `CLAUDE.md` (e.g. the kit at `D:\Project`): skip.
5. **NHATKY.md.** New entry on top (format in `.claude/rules/sessions.md`).
6. **Commit.** One docs commit (steps 2-5, NHATKY.md included): `docs: close stage <n> (<name>); archive T.., T..`.
7. **Meeting.** End of a ROADMAP stage is a meeting trigger (`.claude/rules/agent.md`): propose `/meeting stage <n> end: <topic>` to the User; start no task of the next stage until the decision is recorded.
8. Reply in Vietnamese: stage closed, tasks archived, commit hash, next stage, the proposed `/meeting` line.
