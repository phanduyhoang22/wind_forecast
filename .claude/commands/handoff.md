---
description: Close this chat - write a NHATKY.md entry and the prompt to start the next chat
---

1. Write a new entry at the top of `NHATKY.md` (project root; create it with a `# NHATKY` title if missing) using the format in `.claude/rules/sessions.md`. Facts only: what was done with evidence, decisions, open items. Note: $ARGUMENTS
2. Overwrite `tasks/HANDOFF.md` from `.claude/references/handoff-template.md`, filling every section ("none" if empty). Section 2 holds only commands you really ran this chat with their real output; section 7 lists the mandatory checks the next chat must run. The hook `session_start.py` loads this file into the next chat.
3. If you are the Leader and task states changed, make sure `tasks/STATUS.md` is updated too. Commit NHATKY.md, HANDOFF.md and STATUS.md together.
4. Reply in Vietnamese with: the NHATKY entry you wrote, a 3-line summary of HANDOFF.md, and one line the User copies into a new chat, e.g. `/role leader T05`.
