# Multi-agent spec (reference)

Roles and hard rules: `.claude/rules/agent.md`. This file holds the details.

## Task Contract (one block per task in `tasks/STATUS.md`)
```
## T<NN> — <title>
- owner: | priority: P0-P3 | status: | attempt_count:
- goal:
- scope:
- inputs:
- expected_outputs:
- acceptance_criteria: verifiable conditions, each with a command or check
- dependencies: | allowed_tools: | allowed_paths:
- deadline: (optional) | budget_limit: (optional)
- artifacts:
- test_evidence:
- risks:
- last_update: YYYY-MM-DD
```

## States
Main path: `TODO -> IN_PROGRESS -> READY_FOR_QA -> QA_PASSED -> APPROVAL_PENDING -> DONE`

Light path (light tasks, `rules/agent.md`): same up to `QA_PASSED`, then `QA_PASSED -> DONE` by the Leader, who records the approval and merge. No `APPROVAL_PENDING`.

Exceptions:
- `READY_FOR_QA -> REVISION_REQUIRED -> IN_PROGRESS` when QA fails.
- Any unfinished state -> `BLOCKED` on missing data, permission or dependency.
- `APPROVAL_PENDING -> REVISION_REQUIRED` when the Director asks for changes.
- `CANCELLED` only on a valid instruction from Leader/Director/User within their authority.

Log actor, date and evidence for every transition.

## Failure handling
- Each FAIL: error id, evidence, reproduction, priority, assigned agent.
- Max 3 fix/re-test rounds, then `BLOCKED` and `/meeting` (rules/agent.md): options change approach, split, cancel; the User decides.
- A task waiting on a meeting decision keeps its state and notes `M<NN> DECISION_PENDING`; it is not restarted until the decision is recorded.
- Stop on budget overrun, high risk, data conflict or missing approval.

## Standard flow
1. User -> Director: goal and autonomy limits.
2. Director -> Leader: goal, priority, approval conditions.
3. Leader -> Worker(s): plan, Task Contract, dispatch.
4. Worker(s) -> Leader: output, version, self-check evidence.
5. Leader -> QA: stable version plus acceptance criteria.
6. QA -> Leader: PASS / FAIL / NOT_VERIFIED with evidence.
7. FAIL: Leader assigns fix, QA re-tests.
8. PASS: QA verifies the handoff package; Leader summarizes.
9. Leader -> Director: output, QA report, remaining risks.
10. Director: APPROVE / REVISE / REJECT; asks the User when owner approval is needed.

Light task: steps 9-10 become one Leader approval line in STATUS.md on QA PASS.

## Report templates
- **Worker Report** and **QA Report**: see `.claude/agents/worker.md` and `qa.md`.
- **Leader Report**: progress, tasks done / blocked, cost or tokens used, QA results, proposed next step.
- **Director Decision**: `APPROVE | REVISE | REJECT`, reason, decision scope, whether User approval is needed.

## Done means
Complete outputs, acceptance criteria met, QA PASS with evidence, Leader accepted handoff, Director approved (light task: Leader approved), User approved where required.

## Metrics (record when measurable)
Time per task, fix rounds, QA pass rate, open defects, cost/tokens.

## Limits
This spec describes behavior; it does not enforce it. Enforcement lives in hooks, agent tool lists and permissions.
