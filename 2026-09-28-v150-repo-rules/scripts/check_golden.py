#!/usr/bin/env python3
"""用 golden 的輸入跑「現在的」post_review.py --dry-run，逐字比對 stdout。"""
import difflib, json, os, pathlib, subprocess, sys, tempfile

KIT = pathlib.Path("<repo>")
g = json.loads((KIT / "tools/fixtures/post_review_golden.json").read_text(encoding="utf-8"))
env = {**os.environ, "GH_TOKEN": "dummy-for-dry-run"}
bad = 0
with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    (td / "pr.diff").write_text(g["diff"], encoding="utf-8")
    (td / "review.md").write_text(g["review"], encoding="utf-8")
    for case in g["cases"]:
        (td / "findings.json").write_text(json.dumps(case["findings"], ensure_ascii=False), encoding="utf-8")
        cmd = [sys.executable, str(KIT / ".github/scripts/post_review.py"), "--repo", "o/r", "--pr", "1",
               "--sha", "abc", "--review", str(td / "review.md"), "--findings", str(td / "findings.json"),
               "--diff", str(td / "pr.diff"), "--dry-run", *case["args"], *sys.argv[1:]]
        out = subprocess.run(cmd, capture_output=True, text=True, env=env)
        same = out.returncode == 0 and out.stdout == case["stdout"]
        print(f"{'OK  ' if same else 'DIFF'} {case['name']} (exit {out.returncode})")
        if not same:
            bad += 1
            print("".join(difflib.unified_diff(case["stdout"].splitlines(True), out.stdout.splitlines(True),
                                               "golden", "now")) or out.stderr)
sys.exit(1 if bad else 0)
