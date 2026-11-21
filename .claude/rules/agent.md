# Multi-agent workflow (always on)

Reply to the User in Vietnamese. Files under `.claude/` are written in English.

## Roles
- **User**: project owner, final authority. Approves anything irreversible, external, paid or public.
- **Director** (chat role): clarifies goals, scope, priority, success criteria; decides `APPROVE` / `REVISE` / `REJECT` with reason, only after STATUS.md records QA `PASS` for that task (light tasks: the Leader approves). Escalates owner-level decisions to the User.
- **Leader** (chat role): breaks the goal into tasks, writes Task Contracts in `tasks/STATUS.md`, spawns `worker` and `qa` subagents, pre-checks worker output, records QA results, merges approved work.
- **worker** (subagent, max 2 at once): does one task inside its `scope` and `allowed_paths`, in its own worktree. Never widens scope or declares the project done.
- **qa** (subagent): independent, read-only. Never edits what it verifies, never passes what it did not run.
- Worker and qa are never chat roles: they always run as subagents spawned by the Leader, so their work stays out of the main chat context.

## When the full loop applies
- Code, logic, data, experiments, or any change over ~10 lines that is not a light task: Task Contract -> worker -> Leader pre-check -> qa -> Director -> Leader merges.
- Light task: code/logic change <= ~50 lines in <= 2 files, touching no data and nothing public, paid or irreversible.
  - Contract in STATUS.md: goal, acceptance_criteria, allowed_paths (3 lines min); pass it in full in the worker and qa prompts (not committed yet). Flow: worker (worktree) -> Leader pre-check -> qa.
  - On QA `PASS` the Leader records the approval (no separate Director step) and merges. Contract, evidence and merge go in ONE docs commit at merge.
- Small change, done directly by the main chat (no worker/qa): typo, wording in docs/README, config of 1-2 lines, total <= ~10 lines, touching no logic and no data. Still log it in `NHATKY.md`.
- Always exempt: answering questions, reading/exploring, Leader edits to `tasks/STATUS.md` and `NHATKY.md`.
- Unsure whether it is small or light: treat it as the full loop.
- Simple task: 1 worker -> qa. Independent tasks: 2 workers in parallel (never on the same files). High-risk or direction change: ask the User first.
- Do not spawn extra agents for small subtasks; give them to the existing worker.

## All-hands meeting
- Run `/meeting <topic>` (Leader, worker, qa, Director, then User decides) when a result can change the project:
  - an experiment result that beats or misses the target, or contradicts the current approach;
  - a QA finding that invalidates earlier results;
  - a task `BLOCKED` after 3 rounds;
  - a proposed change of scope, data, method, model or stage; the end of a ROADMAP stage.
- The Leader must propose the meeting as soon as a trigger appears; it does not start dependent tasks until the decision is recorded.
- Final decision belongs to the User; the Director only recommends. Minutes go to `tasks/MEETINGS.md`.

## Git
- Worker/qa need a git repo (worktree isolation). No repo: ask the User before `git init`.
- After Director `APPROVE` (light task: Leader approval on QA `PASS`), the Leader merges the worker branch into the main branch, records the merge commit in STATUS.md, and removes the worktree.

## Hard rules
- No QA `PASS`, no approval. `QA_PASSED` is not `DONE`.
- Missing inputs or acceptance criteria: mark the task `BLOCKED` and ask; do not guess silently.
- Max 3 fix/re-test rounds per task, then `BLOCKED` and report options (split, change approach, cancel).
- A test that could not run is `NOT_VERIFIED`, never `PASS`.
- Every handoff names `task_id`, files/commit, changes, evidence, next step.
- No evidence, not done: report commands run and their real output.

Contract fields, state machine and report templates: `.claude/references/multi-agent-spec.md`.
