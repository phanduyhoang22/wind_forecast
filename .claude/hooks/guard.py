"""PreToolUse guard: ask the User before destructive commands or edits to secret files.
See .claude/policies/file-safety.md. Run `python guard.py --selftest` to check patterns.
shortcut: keyword match, not a sandbox; tighten patterns if something slips through.
Known holes (keyword filter): git worktree remove, git apply/am, find -delete, python -c, backticks, quoting tricks,
pwsh -File / -EncodedCommand, nested cmd /c cmd /c. False positive: powershell -c Write-Host rd -r."""
import json
import re
import sys
import time

# token không chứa khoảng trắng; nhánh nháy kép / nháy đơn / ký tự thường tách rời nhau để tránh ReDoS
TOKEN = r"""(?:"[^"]*"|'[^']*'|[^\s;&|"'])"""
# tuỳ chọn (-C x, -c a='b c', --no-pager, -C "D:/my dir"), giá trị không bắt đầu bằng "-"
OPT = r"""-""" + TOKEN + r"""+(?:\s+(?:"[^"]*"|'[^']*'|[^-\s;&|"'])""" + TOKEN + r"""*)?\s+"""
# đầu lệnh: đầu dòng hoặc sau ; && || |, có thể qua cmd [/s /d] /c|/k hoặc powershell/pwsh [tuỳ chọn]
CMD_START = (r"""(^|[;&|\n])\s*(cmd(\.exe)?\s+(/\S+\s+)*/[ck]\s+["']?|(powershell|pwsh)(\.exe)?\s+(?:"""
             + OPT + r""")*["'{]?\s*)?""")
CMD_RISKY = re.compile(
    r"\brm\s+-[a-zA-Z]*[rRf]"                      # rm -r / -rf / -f
    r"|\bRemove-Item\b[^|;]*-(Recurse|Force)"
    r"|\bgit(\.exe)?\s+(?:" + OPT + r")*(reset\s+--hard|clean\s+-[a-zA-Z]*f|push\b[^|;]*(--force|\s-f\b)|branch\s+-D"
    r"|stash\s+(drop|clear)"                        # mất stash
    r"|checkout\b[^|;&]*\s(--|\.|-f|--force)(\s|$)"  # checkout -- path / . / -f: ghi đè file đang sửa
    r"|restore\b(?!(\s+(--staged|-S)\b)+\s+[^-\s]))"  # ghi đè worktree, trừ khi chỉ --staged
    # rd/rmdir/del chỉ khớp ở đầu lệnh (đầu dòng hoặc sau ; && || |), tránh "grep rd -r ."
    r"|" + CMD_START + r"(rmdir|rd|del)\b[^|;&]*\s/[a-z]*s(\s|$)"  # Windows xoá đệ quy /s
    r"|" + CMD_START + r"(rmdir|rd)\b[^|;&]*\s-r"                   # PowerShell rd -r / -Recurse
    r"|\b(DROP|TRUNCATE)\s+(TABLE|DATABASE)\b"
    r"|\bformat\s+[a-zA-Z]:",
    re.IGNORECASE,
)
SECRET_FILE = re.compile(r"(^|[\\/])(\.env(\.[\w.-]+)?|credentials[\w.-]*|id_rsa[\w.-]*|[\w.-]+\.pem)$", re.IGNORECASE)


def reason(tool, tool_input):
    if tool in ("Bash", "PowerShell"):
        if CMD_RISKY.search(tool_input.get("command", "")):
            return "Destructive command (file-safety policy). Confirm?"
    elif tool in ("Write", "Edit", "NotebookEdit"):
        path = tool_input.get("file_path", "") or tool_input.get("notebook_path", "")
        if SECRET_FILE.search(path):
            return "Writing a secret/credential file (file-safety policy). Confirm?"
    return None


def selftest():
    assert reason("Bash", {"command": "rm -rf build"})
    assert reason("PowerShell", {"command": "Remove-Item x -Recurse -Force"})
    assert reason("Bash", {"command": "git push origin main --force"})
    assert reason("Bash", {"command": "git reset --hard HEAD~1"})
    assert reason("Write", {"file_path": "C:/p/.env"})
    assert reason("Edit", {"file_path": "/p/.env.local"})
    assert not reason("Bash", {"command": "rm file.txt"})
    assert not reason("Bash", {"command": "git push origin main"})
    assert not reason("Bash", {"command": "pytest -q"})
    assert not reason("Write", {"file_path": "src/env_utils.py"})
    for c in ["rmdir /s x", "rd /s /q x", "RD /Q /S x", "del /s *.tmp", "del /q /s x",
              "git checkout -- .", "git checkout HEAD -- src/a.py", "git restore .", "git restore src/a.py",
              "git stash drop", "git stash clear", "git restore --staged --worktree a.py",
              "git clean -fd", "git branch -D x", "DROP TABLE t", "format C:",
              "git checkout .", "git checkout -f main", "git checkout --force main", "rd -r x", "rd -Recurse x",
              "cd a && rd /s /q b", "x; rmdir /s y", "a || del /s b", "ls | rd -r x", "cd a\nrd /s b",
              "git -C x reset --hard", "git -c a=b push --force", "git --no-pager reset --hard",
              "git.exe reset --hard", "GIT -C x clean -fd", 'git -C "D:/my dir" checkout -- .',
              "cmd /c rd /s x", "cmd /k del /s y", "cmd.exe /c rmdir /s /q z", "powershell rd -r x",
              'powershell -c "rd -r x"', "pwsh -Command rd -r x",
              "powershell -ExecutionPolicy Bypass -c rd -r x", "pwsh -wd D:/x -c rd -r x",
              "cmd /s /c rd /s x", "cmd /d /c rd /s x", "git -c a='b c' push --force"]:
        assert reason("Bash", {"command": c}), c
    for c in ["rmdir emptydir", "del file.txt", "git checkout main", "git checkout -b feat",
              "git restore --staged a.py", "git stash", "git stash list", "git stash pop", "git status",
              "git checkout --detach abc", "git reset --soft HEAD~1", "pytest -q", "git checkout -b x",
              "grep rd -r .", "cat rd.txt -r", "echo rd -rf",
              "git -C x status", "git --no-pager log", "git --version", "cmd /c dir", "powershell -c Get-ChildItem"]:
        assert not reason("Bash", {"command": c}), c
    # chống ReDoS: mỗi chuỗi dài phải xong < 0.1 s
    for c in ["git " + "-a 'b' " * 800 + "x", "git " + '-a "b" ' * 800 + "x", "git " + "-a b " * 2000 + "x",
              "cmd /c " * 2000, "powershell " + "-a b " * 2000]:
        t = time.perf_counter()
        CMD_RISKY.search(c)
        assert time.perf_counter() - t < 0.1, c[:30]
    print("guard selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    why = reason(data.get("tool_name", ""), data.get("tool_input", {}) or {})
    if why:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": why,
        }}))
