#!/usr/bin/env python3
"""用「改動前」的 post_review.py（v1.4.1）產生 golden：三組固定輸入的 --dry-run stdout。

D0f 會改 post_review.py，而它影響所有 @v1 caller。沒設規範檔的 caller 輸出必須逐字不變，
所以基準一定要用舊版產生：這裡從 git 取 v1.4.1 的 post_review.py 與 locate.py 到暫存目錄執行，
工作樹已經改過也不受影響。之後不可以用新版重產。
"""
import json, os, pathlib, subprocess, sys, tempfile

KIT = pathlib.Path("<repo>")
OUT = pathlib.Path(sys.argv[1])
REF = "v1.4.1"

# 空白的 context 行必須是一個空格（" "）：用 list 組出來，不靠字串裡的行尾空白。
# 第一版就是行尾空白被吃掉，兩行變成空字串，後面的行號全部少 2。
DIFF = "\n".join([
    "diff --git a/app/handler.py b/app/handler.py",
    "--- a/app/handler.py",
    "+++ b/app/handler.py",
    "@@ -10,5 +10,10 @@ def handle(req):",
    "     user = req.user",
    '+    uid = req.args.get("id")',
    '+    rows = db.execute("SELECT * FROM t WHERE id=" + uid)',
    "+    print(rows)",
    "+    print(rows)",
    "+    return rows",
    "     return user.name",
    " ",
    " ",
    " def other():",
    "diff --git a/app/util.py b/app/util.py",
    "--- a/app/util.py",
    "+++ b/app/util.py",
    "@@ -1,4 +1,6 @@",
    " import os",
    "+import sys",
    '+DEBUG = os.environ.get("DEBUG")',
    " ",
    " def helper():",
    "     return 1",
]) + "\n"

REVIEW = "<!-- deepseek-review -->\n## 🤖 DeepSeek Code Review — 💬 有需要留意的問題\n\n固定的摘要內文（golden 用）。\n"


def f(path, line, sev, conf, title, body="", code="", evidence=""):
    return {"path": path, "line": line, "side": "RIGHT", "severity": sev, "confidence": conf,
            "title": title, "body": body, "existing_code": code, "evidence": evidence}


CASES = [
    {"name": "empty", "args": [], "findings": []},
    {"name": "normal", "args": [], "findings": [
        # 片段在本檔唯一命中：模型報 20 → 12
        f("app/handler.py", 20, "blocker", 0.9, "SQL 注入", "字串串接組 SQL。",
          'rows = db.execute("SELECT * FROM t WHERE id=" + uid)'),
        # 沒有片段：退回模型行號 13
        f("app/handler.py", 13, "minor", 0.75, "用 print 除錯", "改用 logger。"),
        # 片段只在別的檔案唯一命中：path 改寫成 app/util.py
        f("app/handler.py", 3, "major", 0.8, "DEBUG 沒有預設值", "環境變數沒設時是 None。",
          'DEBUG = os.environ.get("DEBUG")'),
    ]},
    {"name": "mixed-skip", "args": ["--max-inline", "1"], "findings": [
        f("app/handler.py", 12, "nit", 0.9, "命名可以更清楚"),                          # 嚴重度不足
        f("app/handler.py", 12, "major", 0.5, "低信心的推測"),                          # 信心不足
        f("app/handler.py", 99, "major", 0.9, "定不到的 finding", "",
          "this snippet is not in the diff"),                                           # 片段與行號都定不到
        f("app/handler.py", 15, "minor", 0.8, "多重命中", "", "print(rows)"),           # 片段多重命中（13、14）
        f("app/handler.py", 15, "minor", 0.8, "片段太短退回行號", "", "return"),        # 片段 < 8 字元 → 模型行號 15
        f("app/util.py", 2, "major", 0.85, "沒用到的 import", "", "import sys"),        # 過門檻
        f("app/handler.py", 11, "minor", 0.7, "沒驗證 id", "", 'uid = req.args.get("id")'),  # 過門檻，被 max-inline 截掉
    ]},
]


def main():
    results = []
    env = {**os.environ, "GH_TOKEN": "dummy-for-dry-run"}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for name in ("post_review.py", "locate.py"):
            src = subprocess.run(["git", "-C", str(KIT), "show", f"{REF}:.github/scripts/{name}"],
                                 capture_output=True, text=True, check=True).stdout
            (td / name).write_text(src, encoding="utf-8")
        post = td / "post_review.py"
        assert "rules_status" not in post.read_text(encoding="utf-8"), "取到的不是改動前的版本"
        (td / "pr.diff").write_text(DIFF, encoding="utf-8")
        (td / "review.md").write_text(REVIEW, encoding="utf-8")
        for case in CASES:
            (td / "findings.json").write_text(json.dumps(case["findings"], ensure_ascii=False), encoding="utf-8")
            cmd = [sys.executable, str(post), "--repo", "o/r", "--pr", "1", "--sha", "abc",
                   "--review", str(td / "review.md"), "--findings", str(td / "findings.json"),
                   "--diff", str(td / "pr.diff"), "--dry-run", *case["args"]]
            p = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if p.returncode != 0:
                raise SystemExit(f"{case['name']} exit {p.returncode}: {p.stderr}")
            print(f"== {case['name']} ==\n{p.stderr}")
            results.append({**case, "stdout": p.stdout})
    OUT.write_text(json.dumps({
        "_note": f"由 {REF} 的 post_review.py 與 locate.py（git show {REF}:…）產生，2026-09-28。"
                 "不要用新版重產：這份就是「沒設規範檔的 caller 行為不變」的基準。",
        "diff": DIFF, "review": REVIEW, "cases": results}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


main()
