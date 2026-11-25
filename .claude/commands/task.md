---
description: Run the full multi-agent loop (Leader -> worker -> qa -> Director) for a goal
argument-hint: <goal>
---

Goal from the User: $ARGUMENTS

Act as Director + Project Leader (the one allowed exception to one-chat-per-role) per `.claude/rules/agent.md` and `.claude/references/multi-agent-spec.md`.

1. Read the project `CLAUDE.md` and `tasks/STATUS.md`. No STATUS.md: suggest `/setup-project` and stop. Not a git repo: say worker/qa worktree isolation needs git and ask before `git init`.
2. Director: restate the goal, scope, priority and success criteria in 3-5 lines. If anything is ambiguous or high-risk, ask the User before going on.
3. Leader: split into tasks; write each Task Contract into `tasks/STATUS.md` (status `TODO`). Missing inputs: `BLOCKED` + question.
   Pick the path per task (`rules/agent.md`): light (contract = goal, acceptance_criteria, allowed_paths) or full; unsure -> full.
4. Spawn `worker` per task (max 2 in parallel, only for independent files). Set `IN_PROGRESS`.
   Spawn with `isolation: "worktree"`. Harness refuses it: the chat was likely opened at lowercase `d:`; reopen it at `D:\...` (uppercase) and retry.
5. Pre-check the Worker Report (scope respected, self-check ran). Set `READY_FOR_QA`.
6. Spawn `qa` with the task contract (incl. any `tasks/HANDOFF.md` mandatory checks) and the worker's branch/commit; qa runs `git checkout --detach <commit>` in its own worktree first (prompts tell qa to `cd` into it; `git -C` is blocked). Record the QA Report in STATUS.md.
7. FAIL: assign the fix to a worker, re-run qa. Max 3 rounds, then `BLOCKED` and report options.
8. PASS: set `APPROVAL_PENDING`, give the Leader Report, then the Director Decision. Ask the User for anything that needs owner approval.
   Light task: on PASS the Leader records the approval and goes to step 9; contract, evidence and merge in one docs commit.
9. APPROVE: merge the worker branch into the main branch, record the merge commit in STATUS.md, remove the worktree, set `DONE`, add a NHATKY.md entry.
