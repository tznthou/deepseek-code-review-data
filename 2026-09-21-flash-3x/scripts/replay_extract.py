#!/usr/bin/env python3
"""用 v1.2.2 的 extract_json 重跑三次失敗 log 留下的原始輸出，看錯誤訊息能不能一字不差重現。

另外：原始輸出的長度、有沒有 code fence、直接 json.loads 停在哪裡、那個位置附近長什麼樣。
只印位置與短片段，不印整份內容。
"""
import ast
import json
import pathlib
import re
import subprocess

REPO = pathlib.Path("<repo>")
RUNS = REPO / ".claude/experiments/2026-09-21-flash-3x/runs"
src = subprocess.run(["git", "-C", str(REPO), "show", "v1.2.2:.github/scripts/deepseek_review.py"],
                     capture_output=True, text=True, check=True).stdout
tree = ast.parse(src)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "extract_json")
ns = {"json": json, "re": re}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "v122_extract_json", "exec"), ns)
extract_json = ns["extract_json"]
print("v1.2.2 extract_json:", ast.get_source_segment(src, fn).count("\n") + 1, "行")

for name in ["python--deepseek-flash--1", "shell--deepseek-flash--2", "shell--deepseek-flash--3"]:
    lines = (RUNS / f"{name}.log").read_text().splitlines()
    logged_err = next(l for l in lines if l.startswith("[error]")).split("：", 1)[1]
    i = lines.index("--- 原始輸出 ---")
    raw = "\n".join(lines[i + 1:])
    try:
        extract_json(raw)
        got = "（解析成功）"
    except Exception as e:  # noqa: BLE001
        got = str(e)
    fences = [m.start() for m in re.finditer(r"```", raw)]
    try:
        json.loads(raw)
        direct = "直接 json.loads 成功"
    except json.JSONDecodeError as e:
        ctx = raw[max(0, e.pos - 25):e.pos + 15].replace("\n", "⏎")
        direct = f"直接 json.loads：{e.msg} @char {e.pos}｜附近：{ctx!r}"
    print(f"== {name}")
    print(f"   原始輸出長度 {len(raw)} 字元；fence 位置 {fences[:6]}")
    print(f"   log 的錯誤：{logged_err}")
    print(f"   重跑的錯誤：{got}")
    print(f"   一致：{logged_err.strip() == got.strip() or logged_err.strip().endswith(got.strip())}")
    print(f"   {direct}")
    print(f"   含「明確的注」：{raw.count('明確的注')} 次；後面 6 字：{[raw[m.end():m.end() + 6] for m in re.finditer('明確的注', raw)]}")
