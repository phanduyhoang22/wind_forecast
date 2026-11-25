"""
Kiem tra dau ca (T17): trang thai that cua repo. Chi doc, khong ghi, khong mang.

Moi dong: PASS|WARN|FAIL|NOT_VERIFIED <nhom> <muc> - <bang chung>. Ma thoat 1 neu co FAIL.

    py scripts/24_shift_check.py
    py scripts/24_shift_check.py --full       (them --selftest cua 08, 11, 22, 23)
    py scripts/24_shift_check.py --selftest
"""

import argparse
import collections
import glob
import itertools
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITES, SEEDS, HORIZONS = list("ABCDEFGH"), [0, 1, 2], ["1h", "3h", "6h"]


def _few(modes, rows):
    return rows, dict(site=SITES, model=["Mamba"], mode=modes, window=["DB", "TN"], weeks=[1, 2, 4],
                      seed=SEEDS, horizon=HORIZONS)


def _loso(model):
    return 144, dict(strategy=["losoW", "globalW"], test_site=SITES, model=[model], seed=SEEDS, horizon=HORIZONS)


# file: (so dong, cot khoa -> moi gia tri phai co)
TABLES = {
    "runs_wind.csv": (120, dict(site=SITES, model=["Mamba"], seed=[0, 1, 2, 3, 4], horizon=HORIZONS)),
    "cross_eval_wind.csv": (576, dict(source=SITES, target=SITES, model=["Mamba"], seed=SEEDS, horizon=HORIZONS)),
    "loso8_wind.csv": _loso("Mamba"),
    "loso8_rf_wind.csv": _loso("RF"),
    "fewshot8_cc.csv": _few(["finetune", "scratch"], 864),
    "fewshot8_ft_free.csv": _few(["finetune"], 432),
    "fewshot8_cpu_cc.csv": _few(["ridge", "rf"], 864),
    "fewshot8_cpu_free.csv": _few(["ridge", "rf"], 864),
    "fewshot8_iv_ft_free.csv": _few(["finetune"], 432),
    "fewshot8_iv_scratch_cc.csv": _few(["scratch"], 432),
    "baselines.csv": (48, dict(site=SITES, model=["persistence", "climatology"], horizon=HORIZONS)),
}
# chay tren Colab, chua co bang khoa o day
REMOTE = ["runs.csv"]

_L = ("transfer_stats.csv", dict(strategy="losoW", model="Mamba", ref="persistence", seed="median", metric="skill"))
_G = (_L[0], dict(_L[1], strategy="globalW"))
_LR, _GR = (_L[0], dict(_L[1], ref="RF")), (_L[0], dict(_G[1], ref="RF"))
_B, _P, _Z = [("fewshot8_stats.csv", dict(model="finetune_free", ref=r, metric="skill"))
              for r in ("best_test", "persistence", "zero_shot")]
_C = (_B[0], dict(model="finetune_cc", ref="finetune_free", metric="skill"))
_O = ("fewshot8_per_site.csv", dict(variant="best_test", weeks="all", seed="median"))
# (dong RESULTS.md, chu dung truoc so, so viet trong tai lieu, nguon, cot, horizon); CSV va tai lieu phai cung khop.
# globalW 6h lay tu R21c: gia tri 23.8 trong R21 da duoc dinh chinh. Mot so thi dung cho moi horizon.
HEADLINE = [
    ("R21", "LOSO skill 1h/3h/6h mean ", "+8.9/+8.7/+12.4%", _L, "mean", HORIZONS),
    ("R21", "beats persistence ", "8/8, 6/8, 7/8", _L, "wins", HORIZONS),
    ("R21", "Wilcoxon 2-sided Holm p ", "0.023 / 0.078 / 0.078", _L, "p_holm", HORIZONS),
    ("R21", "globalW ", "+14.1/+17.9", _G, "mean", ["1h", "3h"]),
    ("R21", "23.8%, ", "8/8", _G, "wins", HORIZONS),
    ("R21", "all horizons, Holm p ", "0.023", _G, "p_holm", HORIZONS),
    ("R21c", "globalW 6h mean skill is ", "+24.0%", _G, "mean", ["6h"]),
    ("R21c", "mean RMSE gain ", "2.9/4.0/6.0%", _LR, "mean", HORIZONS),
    ("R21c", "6.0%, ", "6/8", _LR, "wins", HORIZONS),
    ("R21c", "wins each, Holm p ", "0.117", _LR, "p_holm", HORIZONS),
    ("R21c", "globalW vs RF: ", "+3.4/+5.3/+7.5%", _GR, "mean", HORIZONS),
    ("R21c", "7.5%, ", "8/8", _GR, "wins", HORIZONS),
    ("R21c", "7.5%, 8/8, p ", "0.023", _GR, "p_holm", HORIZONS),
    ("R25", "{scratch, Ridge, RF}: skill 1h/3h/6h ", "+15.2/+21.7/+22.9%", _B, "mean", HORIZONS),
    ("R25", "22.9%, ", "8/8", _B, "wins", HORIZONS),
    ("R25", "8/8 sites, Holm p ", "0.023", _B, "p_holm", HORIZONS),
    ("R25", "vs persistence ", "+9.7/+11.2/+15.6%", _P, "mean", HORIZONS),
    ("R25", "15.6%, ", "8/8, 7/8, 7/8", _P, "wins", HORIZONS),
    ("R25", "7/8, p ", "0.023/0.031/0.031", _P, "p_holm", HORIZONS),
    ("R25", "vs zero-shot ", "+0.8/+2.6/+3.7%", _Z, "mean", HORIZONS),
    ("R25", "3.7%, p ", "0.313/0.078/0.023", _Z, "p_holm", HORIZONS),
    ("R25", "finetune const vs free ", "−1.4/−3.1/−3.8%", _C, "mean", HORIZONS),
    ("R25", "−3.8% (p ", "0.031/0.023/0.031", _C, "p_holm", HORIZONS),
    ("R25c", "mean skill ", "−9.1/−15.8/−11.1%", _O, "skill", HORIZONS),
]


def git(root, *args):
    # --no-optional-locks: git status khong ghi lai index; CEILING: khong nhan nham repo o thu muc cha
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.dirname(root))
    return subprocess.run(["git", "--no-optional-locks", "-C", root, *args], capture_output=True, check=True,
                          timeout=30, env=env, encoding="utf-8", errors="replace").stdout.rstrip("\n")


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_branch(root):
    b = git(root, "branch", "--show-current") or "(detached)"
    return "PASS" if b == "main" else "WARN", "{} @ {}".format(b, git(root, "rev-parse", "--short", "HEAD"))


def check_origin(root):
    ahead, behind = git(root, "rev-list", "--left-right", "--count", "HEAD...origin/main").split()
    return ("PASS" if ahead == behind == "0" else "WARN",
            "ahead {}, behind {} (khong fetch, ref origin/main co the cu)".format(ahead, behind))


def check_dirty(root):
    s = git(root, "status", "--porcelain", "-uno").splitlines()
    return "WARN" if s else "PASS", "{} file tracked chua commit {}".format(len(s), "; ".join(s[:5]))


def check_worktrees(root):
    w = [x[9:] for x in git(root, "worktree", "list", "--porcelain").splitlines() if x.startswith("worktree ")]
    return "WARN" if len(w) > 1 else "PASS", "{} worktree phu {}".format(len(w) - 1, "; ".join(w[1:]))


def check_handoff(root):
    p = "tasks/HANDOFF.md"
    if not os.path.exists(os.path.join(root, p)):
        return "NOT_VERIFIED", p + " khong co"
    # file sach thi dung gio commit: mtime doi khi checkout
    if git(root, "status", "--porcelain", "--ignored", "--", p):
        t = os.path.getmtime(os.path.join(root, p))
    else:
        t = int(git(root, "log", "-1", "--format=%ct", "--", p))
    late = int(git(root, "log", "-1", "--format=%ct")) - t
    return ("WARN", "cu hon HEAD {:.1f} gio".format(late / 3600)) if late > 0 else ("PASS", "khong cu hon HEAD")


def check_table(path, rows, levels):
    if not os.path.exists(path):
        return "NOT_VERIFIED", "khong co file"
    err = []
    with open(path, "rb") as f:
        raw = f.read()
    if not raw.endswith(b"\n"):
        err.append("thieu newline cuoi file")
    try:
        df = pd.read_csv(path)
    except (ValueError, pd.errors.ParserError) as e:
        return "FAIL", "khong doc duoc: {}".format(e)
    lack = [c for c in [*levels, "RMSE"] if c not in df]
    if lack:
        return "FAIL", "thieu cot {}".format(lack)
    if len(df) != rows:
        err.append("{} dong, can {}".format(len(df), rows))
    got = list(df[list(levels)].itertuples(index=False, name=None))
    want = set(itertools.product(*levels.values()))
    miss, odd, dup = want - set(got), set(got) - want, len(got) - len(set(got))
    for what, s in (("thieu", miss), ("la", odd)):
        if s:
            err.append("khoa {} {} vd {}".format(what, len(s), sorted(s, key=str)[0]))
    if dup:
        err.append("khoa trung {}".format(dup))
    r = pd.to_numeric(df.RMSE, errors="coerce")
    if not np.isfinite(r).all():
        err.append("RMSE NaN/inf {}".format(int((~np.isfinite(r)).sum())))
    if (r <= 0).any():
        err.append("RMSE <= 0")
    return ("FAIL", "; ".join(err)) if err else ("PASS", "{} dong, du khoa, RMSE hop le".format(len(df)))


def check_remote(path):
    return "NOT_VERIFIED", ("co file nhung chua co bang khoa" if os.path.exists(path)
                            else "khong co file tai may (chi tren Drive/Colab)")


def check_tasks(text):
    tasks, bad = {}, []
    for part in re.split(r"(?m)^## (?=T\d)", text)[1:]:
        tid = re.match(r"\w+", part).group()
        m = re.search(r"\bstatus: *([A-Z_]+)([^|\n]*)", part)
        if tid in tasks or not m:
            bad.append(tid)
        tasks[tid] = (m.group(1), m.group(0)[8:].strip()) if m else ("", "?")
    if not tasks:
        return "FAIL", "khong thay task nao"
    is_open = ["{} {}".format(t, s) for t, (k, s) in tasks.items() if k not in ("DONE", "CANCELLED")]
    ev = "{} task mo: {}".format(len(is_open), ", ".join(is_open))
    return ("WARN", "thieu status hoac trung id {}; {}".format(bad, ev)) if bad else ("PASS", ev)


def result_rows(text):
    """[(run_id, dong)] cua bang RESULTS.md, theo thu tu."""
    return [(m.group(1), m.group(0)) for m in re.finditer(r"(?m)^\|[^|]*\| *(R\d\w*) *\|.*$", text)]


def check_run_ids(text):
    n = collections.Counter(i for i, _ in result_rows(text))
    dup = [i for i, k in n.items() if k > 1]
    if not n:
        return "FAIL", "khong thay run_id nao"
    return ("FAIL", "run_id trung {}".format(dup)) if dup else ("PASS", "{} run_id, khong trung".format(len(n)))


def check_qa(text):
    rows, left = result_rows(text), []
    for k, (i, line) in enumerate(rows):
        if "not yet QA'd" in line and not any(
                "QA PASS" in later and (j.startswith(i + "c") or re.search(r"\b{}\b".format(i), later))
                for j, later in rows[k + 1:]):
            left.append(i)
    return ("WARN", "chua QA: {}".format(left)) if left else ("PASS", "khong con dong chua QA")


def check_paths(text, results):
    """CSV trong backtick; 'Drive' dung truoc trong cung o thi chi co tren Drive."""
    paths = {}
    for _, line in result_rows(text):
        for cell in line.split("|"):
            for m in re.finditer(r"`([^`\s]+\.csv)`", cell):
                p = m.group(1).removeprefix("results/")
                paths[p] = paths.get(p, False) or "Drive" in cell[:m.start()]
    miss = [p for p in paths if not glob.glob(os.path.join(results, p))]
    out = []
    for status, drive, what in (("FAIL", False, "khong co tai may"), ("NOT_VERIFIED", True, "chi co tren Drive")):
        s = [p for p in miss if paths[p] == drive]
        if s:
            out.append((status, "{}: {}".format(what, ", ".join(s))))
    return out + [("PASS", "{}/{} duong dan co tai may".format(len(paths) - len(miss), len(paths)))]


def check_headline(item, text, results):
    rid, before, nums, (name, where), col, hs = item
    rows = dict(result_rows(text))
    # sau so khong duoc con chu so, nhu vay moi la dung so do
    if rid not in rows or not re.search(re.escape(before + nums) + r"(?![\d.]*\d)", rows[rid]):
        return "FAIL", "RESULTS.md {} khong con '{}{}'".format(rid, before, nums)
    path = os.path.join(results, name)
    if not os.path.exists(path):
        return "NOT_VERIFIED", name + " khong co"
    # bo mau so "/8" cua so tram thang
    clean = nums.replace("/8", "") if col == "wins" else nums
    want = re.findall(r"[+-]?\d+(?:\.\d+)?", clean.replace("−", "-"))
    want = want * len(hs) if len(want) == 1 else want
    df = pd.read_csv(path, dtype={"seed": str, "weeks": str})
    for c, v in where.items():
        df = df[df[c] == v]
    got, ok = [], len(want) == len(hs)
    for h, w in zip(hs, want):
        x = df[df.horizon == h][col]
        # per_site: 8 tram moi horizon, lay trung binh; bang stats: dung 1 dong
        v = float(x.mean()) if len(x) == (8 if col == "skill" else 1) else math.nan
        v *= 100 if col in ("mean", "skill") else 1
        digits = len(w.partition(".")[2])
        ok &= abs(v - float(w)) <= (0.5 * 10 ** -digits + 1e-9 if digits else 1e-9)
        got.append("{:.{}f}".format(v, digits + 1 if digits else 0))
    return "PASS" if ok else "FAIL", "tai lieu {} | {} {}".format(nums, name, "/".join(got))


def check_script(name):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    try:
        p = subprocess.run([sys.executable, os.path.join(HERE, name), "--selftest"], env=env, timeout=300,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return "NOT_VERIFIED", "qua 300 s"
    last = (p.stdout.strip().splitlines() or ["(khong in gi)"])[-1]
    return "FAIL" if p.returncode else "PASS", "exit {}: {}".format(p.returncode, last)


def guard(fn, *args):
    """Khong chay duoc thi NOT_VERIFIED, khong bao gio PASS."""
    try:
        r = fn(*args)
    except Exception as e:
        r = "NOT_VERIFIED", "khong chay duoc: {}: {}".format(type(e).__name__, str(e).splitlines()[:1])
    return r if isinstance(r, list) else [r]


def run_checks(root, full):
    results = os.path.join(root, "results")
    jobs = [("git", n, f, root) for n, f in (("branch", check_branch), ("origin", check_origin), ("dirty", check_dirty),
                                             ("worktrees", check_worktrees), ("handoff", check_handoff))]
    jobs += [("results", n, check_table, os.path.join(results, n), *t) for n, t in TABLES.items()]
    jobs += [("results", n, check_remote, os.path.join(results, n)) for n in REMOTE]

    def doc(name, fn, *args):
        return fn(read_text(os.path.join(root, "tasks", name)), *args)
    jobs += [("docs", "tasks", doc, "STATUS.md", check_tasks), ("docs", "run_ids", doc, "RESULTS.md", check_run_ids),
             ("docs", "qa", doc, "RESULTS.md", check_qa), ("docs", "csv_paths", doc, "RESULTS.md", check_paths, results)]
    jobs += [("recompute", "{}:{}".format(i[0], i[4]), doc, "RESULTS.md",
              lambda t, i=i: check_headline(i, t, results)) for i in HEADLINE]
    if full:
        jobs += [("selftest", s, check_script, s)
                 for s in ("08_aggregate.py", "11_conformal.py", "22_transfer_stats.py", "23_fewshot_stats.py")]
    jobs.append(("colab", "drive", lambda: ("NOT_VERIFIED", "chay status cell (cell 3, notebook MCP Colab)")))
    n = collections.Counter()
    for group, name, fn, *args in jobs:
        for status, ev in guard(fn, *args):
            n[status] += 1
            print("{} {} {} - {}".format(status, group, name, ev), flush=True)
    print("tong: " + ", ".join("{} {}".format(n[s], s) for s in ("PASS", "WARN", "FAIL", "NOT_VERIFIED")))
    return 1 if n["FAIL"] else 0


def _selftest():
    with tempfile.TemporaryDirectory() as tmp:
        for name, (rows, levels) in TABLES.items():
            assert math.prod(len(v) for v in levels.values()) == rows, name
        # bang ket qua: sach thi PASS, moi loi phai bi bat dung ly do
        rows, levels = TABLES["baselines.csv"]
        d = pd.DataFrame(itertools.product(*levels.values()), columns=list(levels)).assign(RMSE=1.0)
        p = os.path.join(tmp, "t.csv")

        def state(df, cut=False):
            text = df.to_csv(index=False, lineterminator="\n")
            with open(p, "w", newline="") as f:
                f.write(text[:-1] if cut else text)
            return check_table(p, rows, levels)
        assert check_table(p, rows, levels)[0] == "NOT_VERIFIED"
        assert state(d)[0] == "PASS"
        swap = pd.concat([d[1:], d[1:2]])   # dung so dong nhung thieu 1 khoa, trung 1 khoa
        for df, word in ((d[1:], "dong, can"), (swap, "khoa thieu"), (swap, "khoa trung"),
                         (d.assign(RMSE=[np.nan] + [1.0] * 47), "NaN"), (d.assign(RMSE=[np.inf] + [1.0] * 47), "NaN/inf"),
                         (d.assign(RMSE=[0.0] + [1.0] * 47), "<= 0"), (d.assign(RMSE=["x"] + [1.0] * 47), "NaN"),
                         (d.replace("A", "Z"), "khoa la"), (d.drop(columns="site"), "thieu cot"), (d[:0], "dong, can")):
            s, ev = state(df)
            assert s == "FAIL" and word in ev, (word, s, ev)
        s, ev = state(d, cut=True)
        assert s == "FAIL" and "newline" in ev
        open(p, "w").close()
        assert check_table(p, rows, levels)[0] == "FAIL"
        assert check_remote(p)[0] == "NOT_VERIFIED"

        # handoff: repo git tam, gio commit dat san
        repo = os.path.join(tmp, "repo")
        os.makedirs(os.path.join(repo, "tasks"))

        def commit(name, when):
            with open(os.path.join(repo, name), "w") as f:
                f.write(str(when))
            env = dict(os.environ, GIT_COMMITTER_DATE="{} +0000".format(when))
            for a in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                      "-c", "core.hooksPath=" + os.path.join(tmp, "none"), "commit", "-qm", "x"]):
                subprocess.run(["git", "-C", repo] + a, env=env, check=True, capture_output=True)
        subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True, capture_output=True)
        commit("a", 1700000000)
        assert check_handoff(repo)[0] == "NOT_VERIFIED"
        commit("tasks/HANDOFF.md", 1700000100)
        assert [f(repo)[0] for f in (check_handoff, check_branch, check_dirty, check_worktrees)] == ["PASS"] * 4
        assert guard(check_origin, repo)[0][0] == "NOT_VERIFIED"   # khong co origin
        commit("a", 1700007300)
        s, ev = check_handoff(repo)
        assert s == "WARN" and "2.0 gio" in ev
        assert guard(check_dirty, os.path.join(repo, "tasks"))[0][0] == "NOT_VERIFIED"   # khong phai goc repo
        with open(os.path.join(repo, "tasks", "HANDOFF.md"), "w") as f:
            f.write("moi")
        assert check_handoff(repo)[0] == "PASS" and check_dirty(repo)[0] == "WARN"

        # tai lieu
        s, ev = check_tasks("## T01 x\n- status: DONE\n## T02 y\n- owner: a | status: TODO (cho) | n: 1\n")
        assert s == "PASS" and "T02 TODO (cho)" in ev and "T01" not in ev
        assert check_tasks("## T01 x\n- goal\n")[0] == "WARN" and check_tasks("")[0] == "FAIL"
        bad, ok = "| d | R1 | not yet QA'd |\n", "| d | R1c | QA PASS |\n"
        assert check_qa(bad)[0] == "WARN" and check_qa(bad + ok)[0] == "PASS" and check_qa(ok + bad)[0] == "WARN"
        assert check_qa(bad + ok.replace("R1c", "R10"))[0] == "WARN"
        assert check_run_ids(bad + ok)[0] == "PASS" and check_run_ids(bad + bad)[0] == "FAIL"
        assert check_run_ids("")[0] == "FAIL"
        r = check_paths("| d | R1 | `results/t.csv`, `x*.csv`, Drive `results/y.csv` |", tmp)
        assert [s for s, _ in r] == ["FAIL", "NOT_VERIFIED", "PASS"] and "x*" in r[0][1] and "y.csv" in r[1][1]

        # so chinh: doi CSV hoac doi tai lieu deu FAIL
        item = ("R1", "skill ", "+8.9/−1.4/+3.0%", ("s.csv", dict(ref="p")), "mean", HORIZONS)
        doc, f = "| d | R1 | skill +8.9/−1.4/+3.0%, 8/8 |", os.path.join(tmp, "s.csv")
        assert check_headline(item, doc, tmp)[0] == "NOT_VERIFIED"
        sd = pd.DataFrame(dict(ref="p", horizon=HORIZONS, mean=[0.0888, -0.0138, 0.03], wins=[8, 6, 8]))
        sd.to_csv(f, index=False)
        assert check_headline(item, doc, tmp)[0] == "PASS"
        assert check_headline(item, doc.replace("8.9", "8.8"), tmp)[0] == "FAIL"
        wins = ("R1", "thang ", "8/8, 6/8, 8/8", item[3], "wins", HORIZONS)
        wdoc = "| d | R1 | thang 8/8, 6/8, 8/8 |"
        assert check_headline(wins, wdoc, tmp)[0] == "PASS"
        sd.assign(wins=[8, 7, 8]).to_csv(f, index=False)
        assert check_headline(wins, wdoc, tmp)[0] == "FAIL"
        one = ("R1", "p ", "0.023", item[3], "mean", HORIZONS)
        assert check_headline(one, "| d | R1 | p 0.0235 |", tmp)[0] == "FAIL"
        for x in (sd.assign(mean=[0.0888, 0.0138, 0.03]), sd[1:], pd.concat([sd, sd]), sd.assign(mean=np.nan)):
            x.to_csv(f, index=False)
            assert check_headline(item, doc, tmp)[0] == "FAIL"
        assert guard(lambda: 1 / 0)[0][0] == "NOT_VERIFIED"
    print("selftest: dat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.selftest:
        _selftest()
        return 0
    return run_checks(ROOT, args.full)


if __name__ == "__main__":
    sys.exit(main())
