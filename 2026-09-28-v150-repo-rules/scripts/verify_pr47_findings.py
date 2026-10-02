#!/usr/bin/env python3
"""逐筆實跑 PR #47 的 AI review finding。"""
import importlib.util, json, pathlib, sys

KIT = pathlib.Path("<repo>")
sys.path.insert(0, str(KIT / ".github/scripts"))


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, KIT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dr = load("dr", ".github/scripts/deepseek_review.py")
pr = load("pr", ".github/scripts/post_review.py")

print("== F1：fence 結束行會不會被當成新條目 ==")
for label, text in {
    "條目底下縮排的 fence，結束行帶字": "- 條目甲\n  ```\n  code\n  ```- 看起來像條目\n- 條目乙\n",
    "節裡的 fence，結束行帶 - ": "## 只有散文的節\n```\n- 在 code 裡\n```\n## 下一節\n- 條目丙\n",
    "fence 裡有 - 開頭的行": "- 條目丁\n  ```\n- 這行在 code block 裡\n  ```\n",
}.items():
    rules = dr.parse_repo_rules(text)
    print(f"  {label}: {[(r['kind'], r['label'], r['head'], r['rest']) for r in rules]}")

print("== F2：一般 finding 進 post 之前是否已排序 ==")
raw = {"findings": [
    {"path": "a.py", "line": 1, "severity": "minor", "confidence": 0.9, "title": "m", "existing_code": "x"},
    {"path": "a.py", "line": 2, "severity": "blocker", "confidence": 0.8, "title": "b", "existing_code": "y"},
    {"path": "a.py", "line": 3, "severity": "major", "confidence": 0.95, "title": "j", "existing_code": "z"},
]}
print("  normalize 之後：", [f["severity"] for f in dr.normalize(raw)["findings"]])

print("== F5：line 是 None 時 merge_into 會不會丟例外 ==")
print("  normalize 對 line=None：", dr.normalize({"findings": [
    {"path": "a.py", "line": None, "severity": "minor", "existing_code": "abc_def_ghi"}]})["findings"][0]["line"])
try:
    pr.merge_into([{"path": "a.py", "line": 5}], [{"path": "a.py", "line": None}])
    print("  merge_into 餵 None：沒有例外")
except TypeError as err:
    print(f"  merge_into 餵 None：TypeError（{err}）——但進得來嗎？見下")
# 進 merge_into 之前要先過 select_inline；有 diff 時行號一定由 resolve_line 定出整數，定不到就跳過
index = {"a.py": {5: "abc_def_ghi = 1"}}
sel, skipped, _ = pr.select_inline([{"path": "a.py", "line": None, "severity": "minor", "confidence": 0.9,
                                     "title": "t", "existing_code": ""}], 1, 0.7, "minor", {"a.py": {5}}, index)
print(f"  line=None、沒有片段的 finding 過 select_inline：selected={len(sel)} skipped={[r for _, r in skipped]}")
