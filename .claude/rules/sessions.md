# Sessions and journal

## One chat per role, short chats
- Each chat has one role: `director` (goals, approvals) or `leader` (plan, Task Contracts, spawn worker/qa subagents, approve light tasks, merge). Worker and qa are subagents, never chats.
- Start a role chat with `/role <role> [task_id]`. Stay inside that role; the other role's work goes to another chat.
- Open chats from a terminal at uppercase `D:\...` (`cd D:\Project\<project>`, then run `claude`). VS Code chats open at lowercase `d:`, where the harness refuses `worker`/`qa` worktrees.
- In VS Code: keep the editor, but run `claude` in its integrated terminal from `D:\...` (same token cost); one chat per role at a time, never the extension chat and a terminal chat together. Worktree refused there too: say so and fall back to an outside terminal.
- Kit-maintenance chats at `D:\Project` (no CLAUDE.md, no STATUS.md) have no role: label NHATKY entries `kit`, and "Mở chat tiếp" gives the opening prompt instead of `/role`.
- Target 10-15 User messages per chat. The hook `hooks/turn_counter.py` warns from message 12. At the warning, finish the current step, then propose `/handoff`.
- Never rely on chat history across chats: everything the next chat needs goes into `NHATKY.md` and `tasks/STATUS.md`.

## NHATKY.md (project root)
- Journal of what got done, written in Vietnamese for the User. Newest entry on top.
- Write an entry on `/handoff`, and whenever a task changes state to DONE/BLOCKED.
- Entry format:
  ```
  ## YYYY-MM-DD HH:MM — <role> — <topic>
  - Làm được: ... (files/commits, evidence)
  - Quyết định: ...
  - Dở dang / bước tiếp: ...
  - Mở chat tiếp: /role <role> [task_id]
  ```
- Keep entries short (max ~10 lines). Detail and evidence live in STATUS.md, not here.
- When the file passes ~300 lines, move entries older than 30 days to `tasks/NHATKY-ARCHIVE.md`.
