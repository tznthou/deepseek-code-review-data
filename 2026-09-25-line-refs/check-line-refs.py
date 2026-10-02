#!/usr/bin/env python3
"""掃公開文件與 code 註解裡的 `檔名:行號` 引用，印出引用處上下文與目標行，供人工比對（唯讀）。"""
import pathlib
import re
import subprocess

R = pathlib.Path("<repo>")
tracked = subprocess.run(["git", "-C", str(R), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
tracked_paths = [R / p for p in tracked]

by_name = {}
for p in tracked_paths:
    by_name.setdefault(p.name, []).append(p)

REF = re.compile(r"([A-Za-z0-9_.\-/]+\.(?:yml|yaml|py|md|sh|json|txt)):(\d+)(?:[-–](\d+))?")

# CHANGELOG 的行號是當時的歷史紀錄，不該跟著改；research.md 是調研文件，另外標出
SOURCES = [p for p in tracked_paths if p.suffix in {".md", ".py", ".yml", ".sh"}]

def resolve(ref):
    cand = R / ref
    if cand.exists():
        return [cand]
    name = pathlib.PurePath(ref).name
    hits = by_name.get(name, [])
    # 引用帶目錄時，要求結尾吻合
    if "/" in ref:
        hits = [h for h in hits if str(h).endswith(ref.lstrip("./"))]
    return hits

rows = []
for src in SOURCES:
    try:
        lines = src.read_text(encoding="utf-8").splitlines()
    except Exception:
        continue
    for i, line in enumerate(lines, 1):
        for m in REF.finditer(line):
            ref, a, b = m.group(1), int(m.group(2)), m.group(3)
            targets = resolve(ref)
            rel_src = src.relative_to(R)
            if not targets:
                rows.append((str(rel_src), i, m.group(0), "UNRESOLVED（repo 外或已不存在）", line.strip()[:160], ""))
                continue
            if len(targets) > 1:
                rows.append((str(rel_src), i, m.group(0), f"AMBIGUOUS {len(targets)}", line.strip()[:160], ""))
                continue
            t = targets[0]
            tl = t.read_text(encoding="utf-8").splitlines()
            end = int(b) if b else a
            if a > len(tl):
                got = f"OUT OF RANGE（檔案只有 {len(tl)} 行）"
            else:
                got = " ⏎ ".join(x.strip() for x in tl[a - 1:min(end, a + 2)])[:200]
            rows.append((str(rel_src), i, m.group(0), str(t.relative_to(R)), line.strip()[:160], got))

for src, i, ref, tgt, ctx, got in rows:
    print(f"■ {src}:{i}  →  {ref}")
    print(f"   引用處：{ctx}")
    print(f"   目標：{tgt}")
    if got:
        print(f"   目標行：{got}")
    print()
print(f"共 {len(rows)} 筆引用")
