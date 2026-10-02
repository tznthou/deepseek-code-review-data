#!/usr/bin/env python3
"""$0 驗證：Qodo 的結構化規範寫成簡單格式後，kit 的渲染是否跟實驗 v01 的 render.render() 逐字相同。

相同 → 正式版送出去的規範區塊，就是 holdout 上盲標驗過的那一段（至少對 Qodo 這種整理好的規範）。
"""
import importlib.util, json, pathlib, sys

KIT = pathlib.Path("<repo>")
LOOP = KIT / ".claude/experiments/2026-09-26-rules-loop/scripts"
sys.path.insert(0, str(LOOP))
sys.path.insert(0, str(KIT / ".github/scripts"))
sys.dont_write_bytecode = True
import render  # noqa: E402  實驗的渲染（v01 設定）
from common import load_rules  # noqa: E402

spec = importlib.util.spec_from_file_location("dr", KIT / ".github/scripts/deepseek_review.py")
dr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dr)

V01 = {"placement": "after_diff", "fields": "full", "format": "list", "header": "h1"}
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None

same = diff = 0
for repo, rules in sorted(load_rules().items()):
    # 簡單格式：每條一個 `- ` 條目，內容就是 v01 清單那一行扣掉編號
    lines = []
    for r in rules:
        tail = "；".join(f"{render.LABELS[k]}：{render._text(r[k])}"
                        for k in render.FIELD_KEYS["full"] if r.get(k))
        lines.append(f"- **{r['title']}**" + (f" — {tail}" if tail else ""))
    simple = "\n".join(lines) + "\n"
    ours, _ = dr.render_repo_rules(dr.parse_repo_rules(simple))
    theirs, _ = render.render(repo, V01)
    if ours == theirs:
        same += 1
    else:
        diff += 1
        a, b = ours.splitlines(), theirs.splitlines()
        first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        print(f"DIFF {repo}: 條數 kit {len(dr.parse_repo_rules(simple))} / v01 {len(rules)}；第 {first} 行起不同")
        print(f"   kit: {a[first][:120] if first < len(a) else '(沒有)'}")
        print(f"   v01: {b[first][:120] if first < len(b) else '(沒有)'}")
    if OUT and repo == sys.argv[2]:
        OUT.write_text(simple, encoding="utf-8")
print(f"逐字相同 {same} 個 repo、不同 {diff} 個")
