"""UserPromptSubmit hook: count User messages per chat and nudge a /handoff at 12 and 15+.
See .claude/rules/sessions.md. Run `python turn_counter.py --selftest` to check.
shortcut: one tiny counter file per session in hooks/.turns, never cleaned; delete the folder if it grows."""
import json
import os
import sys

WARN, LIMIT = 12, 15
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".turns")


def bump(session_id, folder=DIR):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "".join(c for c in session_id if c.isalnum() or c in "-_") or "unknown")
    n = 1
    if os.path.exists(path):
        with open(path) as f:
            n = int(f.read() or 0) + 1
    with open(path, "w") as f:
        f.write(str(n))
    return n


def message(n):
    if n >= LIMIT:
        return (f"User message {n} in this chat (limit {LIMIT}). Answer this message, then tell the User in Vietnamese "
                "to run /handoff and continue in a new chat to save tokens.")
    if n >= WARN:
        return f"User message {n}/{LIMIT} in this chat. Finish the current step soon and propose /handoff."
    return None


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import tempfile
        tmp = tempfile.mkdtemp()
        counts = [bump("s1", tmp) for _ in range(15)]
        assert counts[-1] == 15 and bump("s2", tmp) == 1
        assert message(11) is None and "12/15" in message(12) and "limit" in message(15)
        print("turn_counter selftest OK")
        sys.exit(0)
    data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
    msg = message(bump(data.get("session_id", "unknown")))
    if msg:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}}))
