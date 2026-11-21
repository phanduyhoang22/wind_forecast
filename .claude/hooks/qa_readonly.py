"""Block Bash commands that write/delete while running as the qa agent (exit 2 = block).
shortcut: keyword filter, not a real sandbox; upgrade if absolute guarantees are needed.
Known holes (keyword filter): git branch -D, git worktree remove, git apply/am, find -delete, python -c, backticks, quoting tricks.
Run `python qa_readonly.py --selftest` to check patterns."""
import json
import re
import sys

BAD = re.compile(
    r"(^|[;&|\s(])(rm|mv|cp|dd|tee|touch|mkdir|rmdir|chmod|chown|truncate|ln|sed\s+-i|"
    r"git\s+(commit|push|reset|checkout|merge|rebase|add|rm|stash|clean|tag|switch|restore)|"
    r"pip\s+install|npm|curl|wget)(\s|$)|>"
    # Chặn hẳn git có -C/-c/--git-dir/--work-tree/--namespace: giá trị có thể chứa lệnh hoặc alias
    r"|\bgit\s+(-\S*\s+)*(-[Cc]|--(git-dir|work-tree|namespace)\b)"
)
# Chỉ bỏ -P/--no-pager: vô hại, không mang giá trị
NOPAGER = re.compile(r"\bgit\s+((-P|--no-pager)\s+)+")
# Cho qa checkout commit của worker: rev không được bắt đầu bằng "-", phải đứng trước hết lệnh/&&/;/|
DETACH = re.compile(r"\bgit\s+(checkout|switch)\s+--detach\s+[\w./^~@][\w./^~@-]*(?=\s*($|&&|;|\|))")


def blocked(cmd):
    chk = re.sub(r"\d?>\s*(&\d|/dev/null)", "", cmd)  # allow 2>&1, >/dev/null
    chk = NOPAGER.sub("git ", chk)
    chk = DETACH.sub(" ", chk)  # bỏ đoạn detach hợp lệ, phần còn lại vẫn bị quét
    return bool(BAD.search(chk))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        assert blocked("rm -rf x") and blocked("echo hi > f.txt") and blocked("git commit -m x")
        assert not blocked("pytest -q 2>&1") and not blocked("git diff main") and not blocked("ls >/dev/null")
        for c in ["git checkout --detach abc123", "git switch --detach feature/x",
                  "git checkout --detach abc123 && python -m pytest -q 2>&1",
                  "git --no-pager diff", "git -P log", "cd x && git diff main", "git checkout --detach abc"]:
            assert not blocked(c), c
        for c in ["git checkout main", "git checkout -- .", "git checkout --detach abc && rm -rf x",
                  "git switch -c new", "git checkout --detach abc > f.txt", "git checkout abc -- file.py",
                  "git checkout --detach -- x", "git checkout --detach -c x", "git checkout --detach abc file.py",
                  "mv a b", "git push", "git reset --hard", "pip install x", "git commit -m x",
                  "git -C D:/x checkout main", "git -c a=b checkout main", "git --git-dir=.git reset --hard",
                  "git -C x -c a=b commit -m y", "git --work-tree=. restore .", "git --git-dir .git reset --hard",
                  "git -C x checkout --detach abc && rm -rf y",
                  "git -C x;rm -rf y", "git -C x&&rm -rf y", "git -c a=b>out.txt log", "git --no-pager=a>b status",
                  "git -C x|tee f", "git -P checkout main", "git -c a=b -P commit -m x",
                  "git -C \"D:/my dir\" checkout main", "git -C 'D:/my dir' reset --hard",
                  "git -C D:/x diff main", "git -C x log --oneline", "git -c core.pager=cat show HEAD",
                  "git -C x checkout --detach abc", "git -C x diff main", "git -c core.pager=./x.sh log",
                  "git -c alias.z='!rm -rf y' z", "git -C \"$(rm -rf y)\" status", "git -C $(rm -rf y) status",
                  "git -c a=$(rm -rf y) log", "git --git-dir=$(rm -rf y) log", "git -C x$(rm -rf y) log",
                  "git -C \"x\"y checkout main", "git -P -C x log", "git -cX log", "git --namespace=n log"]:
            assert blocked(c), c
        print("qa_readonly selftest OK")
        sys.exit(0)
    cmd = json.loads(sys.stdin.buffer.read().decode("utf-8-sig")).get("tool_input", {}).get("command", "")
    if blocked(cmd):
        print("QA read-only: command blocked: " + cmd, file=sys.stderr)
        sys.exit(2)
