---
description: Start a role chat (director | leader) with minimal context
argument-hint: <director|leader> [task_id]
---

Role and task for this chat: $ARGUMENTS

1. Only `director` or `leader` are chat roles. Anything else (worker, qa): say they run as subagents of the Leader and stop.
2. Read only: project `CLAUDE.md`, the top 3 entries of `NHATKY.md`, and in `tasks/STATUS.md` the goal, approved decisions and the open tasks (or only the given task_id). Do not read more until needed.
3. Act strictly as that role, per `.claude/rules/agent.md`:
   - `director`: clarify goals, approve/revise/reject full-loop tasks that have QA PASS (light tasks: the Leader approves). No file edits except STATUS.md decision lines and NHATKY.md.
   - `leader`: plan, write Task Contracts, spawn `worker` and `qa` subagents, update STATUS.md, merge approved work.
4. Reply in Vietnamese with a 3-5 line summary of where things stand and the next step for this role.
