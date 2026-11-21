---
description: All-hands meeting (Leader, worker, qa, Director, User) to decide on a result that impacts the project
argument-hint: <topic / trigger, e.g. "T07 results: ablation beats full model">
---

Topic: $ARGUMENTS. Run the meeting per `.claude/rules/agent.md` (All-hands meeting). Keep every brief short to save tokens.

1. **Brief (Leader).** Write a draft entry at the top of `tasks/MEETINGS.md` (create with `# MEETINGS` if missing):
   trigger, the result with evidence (run_ids from RESULTS.md, QA report, commits), the one question to decide, and 2-3 concrete options (always include "keep current plan").
2. **Opinions (in parallel, one message, both subagents read-only for this meeting):**
   - Spawn `qa`: "Meeting mode. Is the evidence valid and sufficient (leakage, seeds, splits, bugs)? Risks of each option? Verdict on evidence: SOLID / WEAK / INVALID."
   - Spawn `worker`: "Meeting mode: do NOT edit, create or commit anything. For each option: feasibility, effort (hours/GPU runs), technical risks, what you would do first."
   Give both the brief text, not the whole history.
3. **Leader view:** impact of each option on ROADMAP stages, schedule, cost (GPU/Colab quota), open tasks.
4. **Director:** weigh all views, recommend ONE option with reason, record dissent and conditions. Evidence judged INVALID by qa -> recommend fixing evidence first, not a direction change.
5. **User decides.** Present in Vietnamese: question, options table (option | qa | worker | leader | pros/cons), Director recommendation. Wait for the User's choice. Until then the meeting is `DECISION_PENDING` and tasks affected by it are not started.
6. **Record:** complete the MEETINGS.md entry (format below); copy the decision to STATUS.md "Approved decisions" with date and meeting id; update ROADMAP.md if a stage changes; turn action items into Task Contracts (`TODO`); add a NHATKY.md entry.

Minutes format (English):
```
## M<NN> — YYYY-MM-DD — <topic>
- trigger:
- evidence: run_ids / QA report / commits
- question:
- options: A) ... B) ... C) keep current plan
- qa: <evidence verdict + risks>
- worker: <feasibility / effort per option>
- leader: <roadmap / schedule / cost impact>
- director recommendation: <option + reason>; dissent:
- decision (User): <option>, YYYY-MM-DD   | status: DECIDED / DECISION_PENDING
- action items: T.. , T..
```
