# HANDOFF — <YYYY-MM-DD HH:MM> — <role> — <topic>

Overwritten by `/handoff`. The next chat gets this file at start (hook `session_start.py`). Facts only; write "none" instead of deleting a section.

## 1. Current task
- task_id / state / path (light | full): ...
- contract: `tasks/STATUS.md` section <task_id> (or ROADMAP item)
- branch / worktree / last commit: ...

## 2. Verified (command -> real output)
- `<command>` -> `<output line that proves it>`

## 3. NOT verified, risks, open findings
- ...

## 4. Files and commits touched this chat
- ...

## 5. Environment traps
- e.g. open chats from a terminal at `D:\...` (not VS Code `d:`); python `D:\Project\.venv\Scripts\python.exe`; branch name; worktrees still open.

## 6. Waiting on the User
- decisions or approvals still pending: ...

## 7. Next step
- do: ...
- done when: ...
- mandatory checks (the next worker/qa must run each one and report its real output; not run -> `NOT_VERIFIED`):
  1. `<command>` -> expected: ...
