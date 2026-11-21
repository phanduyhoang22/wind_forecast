# File safety policy

Before writing, overwriting or deleting a file:
1. Look at the target first (read it or list it). Never overwrite a file you have not read.
2. Prefer edits over full rewrites; prefer moving to a backup over deleting.
3. Deleting more than one file, a directory, or anything under `data/`, raw data, or outside the project: ask the User first.
4. Never edit `.env`, credential files, keys (`*.pem`, `id_rsa*`) or `.git/` internals unless the User asks explicitly.
5. Never commit secrets; check `git diff --staged` for keys/tokens before committing.
6. Generated outputs (models, results, caches) go to git-ignored folders.
7. Destructive git (`reset --hard`, `clean -f`, `push --force`, force branch delete `-D`): ask the User first; mention what will be lost.
8. Routine, no need to ask: the Leader removing a task worktree it created and `git branch -d` of a branch already merged (or of a QA detached worktree).

Enforced in part by `.claude/hooks/guard.py` (asks for confirmation on matching commands and secret files).
