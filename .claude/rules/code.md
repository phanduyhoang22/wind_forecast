# Code rules

- Follow the existing style of the project first; these rules fill gaps only.
- Smallest change that fully solves the task. No abstraction, option or config nobody asked for.
- Reuse what exists (project helpers, stdlib, installed deps) before adding code or dependencies.
- Python: use the shared venv `D:\Project\.venv` (`D:\Project\.venv\Scripts\python.exe`). Never create a per-project venv/conda env. Ask before `pip install` (it affects every project).
- Names: Python `snake_case` files/functions, `PascalCase` classes; JS/TS follow the repo's linter. Names say what, not how. Identifiers in English.
- Layout (when the project has none): `src/` code, `tests/` tests, `scripts/` entry points, `data/` (git-ignored) data, `notebooks/`.
- Comments and docstrings in Vietnamese, short, explaining why. Keep existing comments.

## Tests and lint
- Tests: `pytest` (`D:\Project\.venv\Scripts\python.exe -m pytest tests -q`).
- Lint/format: `ruff check .` and `ruff format .` when ruff is installed; not installed -> skip and say so, never install it without asking.
- New non-trivial logic (branch, loop, parser, math, money, security) ships with a test in `tests/` or an assert-based self-check.
- Run the project's tests before handing off; report the exact command and result.

## Notebooks
- Core logic lives in `src/` (importable, testable). Notebooks are for EDA, figures, and running `src/` on Colab.
- A notebook never holds the only copy of pipeline logic; move it to `src/` before the task is QA'd.

## CPU local, GPU on Colab
- Local machine has no GPU (torch CPU). GPU work runs on Colab via MCP `colab`.
- Same code for both: pick device automatically (`cuda` if available else `cpu`); never hard-code `cuda`.
- Colab notebook = thin runner: get repo, install deps, call `scripts/...`; results/checkpoints saved to Drive, paths in project CLAUDE.md.
- Every GPU script has a small CPU mode (tiny subset / few steps) so tests and QA run locally.

## Commits
- Conventional Commits with the task id: `<type>(<task_id>): <summary>`, e.g. `feat(T03): add --seed to train.py`.
- Types: feat, fix, refactor, test, docs, data, exp (experiment), chore. Small direct changes without a task: `<type>: <summary>`.

## Data science
- No train/test leakage, fixed seeds, record units and time zones, keep raw data untouched.
