"""SessionStart hook: nạp tasks/HANDOFF.md vào chat mới để không mất bối cảnh giữa các chat.
Cảnh báo khi thiếu file hoặc khi có commit mới hơn bản bàn giao (bản bàn giao có thể đã cũ).
See .claude/rules/sessions.md. Run `python session_start.py --selftest` to check."""
import os
import subprocess
import sys

MAX_CHARS = 8000  # giữ bối cảnh nạp vào nhỏ


def last_commit_time(root):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct"], check=False, cwd=root, capture_output=True, text=True, timeout=5)
        return int(out.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def build(root):
    path = os.path.join(root, "tasks", "HANDOFF.md")
    if not os.path.exists(path):
        return ("No tasks/HANDOFF.md in this project. Read the top entries of NHATKY.md and tasks/STATUS.md before "
                "working; at the end of this chat run /handoff to create it.")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n...[truncated, read tasks/HANDOFF.md]"
    head = "Handoff from the previous chat (tasks/HANDOFF.md). Treat it as the starting context; " \
           "run its mandatory checks before claiming them done."
    commit = last_commit_time(root)
    if commit and commit > os.path.getmtime(path) + 60:
        head += " WARNING: there are commits newer than this handoff; it may be stale, check `git log` and NHATKY.md."
    return head + "\n\n" + text


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import tempfile
        tmp = tempfile.mkdtemp()
        assert "No tasks/HANDOFF.md" in build(tmp)
        os.makedirs(os.path.join(tmp, "tasks"))
        with open(os.path.join(tmp, "tasks", "HANDOFF.md"), "w", encoding="utf-8") as f:
            f.write("# HANDOFF — test — bước tiếp\n" + "x" * (MAX_CHARS + 10))
        out = build(tmp)
        assert "bước tiếp" in out and "truncated" in out and "WARNING" not in out
        subprocess.run(["git", "init", "-q", tmp], check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"],
                       cwd=tmp, check=True)
        os.utime(os.path.join(tmp, "tasks", "HANDOFF.md"), (0, 0))  # bàn giao cũ hơn commit
        assert "WARNING" in build(tmp)
        print("session_start selftest OK")
        sys.exit(0)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    # stdout của SessionStart được đưa vào bối cảnh chat
    sys.stdout.reconfigure(encoding="utf-8")
    print(build(root))
