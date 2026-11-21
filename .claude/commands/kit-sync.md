---
description: Update a set-up project's kit copy from the master kit D:\Project\.claude (new and changed files, with User approval)
argument-hint: <project folder, e.g. D:\Project\wind_forecast; empty = current project>
---

Target project: $ARGUMENTS (empty: the current project). Kit source: `D:\Project\.claude`. `/setup-project` keeps existing files, so kit edits reach a project only through this command.
Follow `.claude/policies/file-safety.md`: never overwrite a file before the User approves it.

1. **Check.** Target is `D:\Project` itself, or has no `.claude/`: stop and say so (no kit copy: suggest `/setup-project`).
2. **Compare** the set `/setup-project` copies: `rules/`, `agents/`, `commands/` (except `setup-project.md`), `references/`, `policies/`, `hooks/*.py`, `settings.json`.
   Use `diff -rq --strip-trailing-cr <kit>/<item> <target>/.claude/<item>` per item; skip `hooks/.turns/`, `__pycache__/`, `worktrees/`.
3. **List** three groups: new (kit only), changed (both, differ), target-only. Nothing new or changed: say the kit is in sync and stop.
4. **Ask.** Show `diff -u --strip-trailing-cr` of each changed file; ask the User which files to copy and overwrite. Target-only files: never delete, only list.
   Changed `settings.json`: show the diff and propose a merge of the kit `hooks` block instead of overwriting.
5. **Copy** the approved new and changed files; re-run step 2 until only skipped or target-only differences remain.
6. **NHATKY.md** in the target: new entry on top (format in `.claude/rules/sessions.md`): files synced, files skipped.
7. **Commit** in the target repo, one commit (NHATKY.md included): `chore: sync kit files`.
8. Reply in Vietnamese: files added, overwritten, skipped, target-only; commit hash.
