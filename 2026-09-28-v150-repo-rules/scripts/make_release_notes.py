#!/usr/bin/env python3
"""從 main 的 CHANGELOG 取 [1.5.0] 那一節當 Release body；相對連結轉成指向 main 的絕對網址。"""
import pathlib, re, subprocess, sys

KIT = "<repo>"
BLOB = "https://github.com/tznthou/deepseek-code-review/blob/main/"
text = subprocess.run(["git", "-C", KIT, "show", "origin/main:CHANGELOG.md"], capture_output=True, text=True, check=True).stdout
m = re.search(r"^## \[1\.5\.0\] - 2026-09-28\n(.*?)(?=^## \[1\.4\.1\])", text, flags=re.S | re.M)
if not m:
    sys.exit("找不到 [1.5.0] 那一節")
body = m.group(1).strip() + "\n"
# (path) 或 (path#anchor)；http 開頭與 #anchor 開頭的不動
body, n = re.subn(r"\]\((?!https?://|#)([^)]+)\)", lambda x: f"]({BLOB}{x.group(1)})", body)
out = pathlib.Path(sys.argv[1])
out.write_text(body, encoding="utf-8")
print(f"{len(body)} 字元、轉了 {n} 個相對連結 → {out}")
print("相對連結殘留：", re.findall(r"\]\((?!https?://)[^)]+\)", body) or "無")
