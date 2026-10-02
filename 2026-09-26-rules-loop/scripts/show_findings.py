#!/usr/bin/env python3
"""把指定 finding、它引用的規則全文、diff 裡附近幾行並排印出來，給人判斷是不是真的違規。$0。

diff 保留 +／-／空白前綴（看得出哪幾行是這次新增的），目標行標 >>。
用法：show_findings.py <fid>...（fid = <run>:<pr>:<序號>，同 loop_score 的編法）
"""
import json
import re
import sys

sys.dont_write_bytecode = True
from common import QODO, load_rules, pr_repo, rule_ids  # noqa: E402
import loop_score as ls  # noqa: E402

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
CTX = 8


def diff_window(pr: str, path: str, line: int | None) -> list[str]:
    rows, cur, n = [], None, 0
    for raw in (QODO / "prs" / pr / "pr.diff").read_text(encoding="utf-8").splitlines():
        if raw.startswith("diff --git "):
            cur, n = None, 0
            continue
        if n == 0 and raw.startswith("+++ "):  # 檔頭只出現在第一個 hunk 之前
            t = raw[4:].strip()
            cur = t[2:] if t.startswith("b/") else t
            continue
        m = HUNK.match(raw)
        if m:
            n = int(m.group(1))
            continue
        if cur != path or n == 0:
            continue
        if raw.startswith("-"):
            rows.append((None, raw))
        else:
            rows.append((n, raw))
            n += 1
    if line is None:
        return [f"（定位不到行號；此檔在 diff 裡 {sum(1 for x, _ in rows if x)} 行）"]
    hit = [i for i, (x, _) in enumerate(rows) if x is not None and abs(x - line) <= CTX]
    if not hit:
        return [f"（diff 裡沒有第 {line} 行附近的內容）"]
    return [f"{'>>' if x == line else '  '} {x if x else '':>5} {raw[:160]}" for x, raw in rows[hit[0]:hit[-1] + 1]]


def main() -> None:
    for fid in sys.argv[1:]:
        run, pr, k = fid.rsplit(":", 2)
        f = next(x for x in ls.load_findings(run, [pr])[0] if x["fid"] == fid)
        raw = json.loads((ls.rounds_dir(run) / f"{pr}.json").read_text(encoding="utf-8"))[int(k) - 1]
        rules = load_rules()[pr_repo(pr)]
        idmap = rule_ids(rules)
        print(f"################ {fid}（信心 {f['confidence']}、{raw.get('severity')}、{f['path']}:{f['line']}）")
        print(f"title：{f['title']}\nbody：{f['body']}\n")
        for i in sorted(set(ls.CITE_RE.findall(f["title"]) or ls.CITE_RE.findall(f["body"]))):
            r = next((r for r in rules if r["title"] == idmap.get(f"R{i}")), None)
            if r:
                print(f"規則 R{i}：{r['title']}")
                for key in ("objective", "success_criteria", "failure_criteria"):
                    if r.get(key):
                        v = r[key] if isinstance(r[key], str) else json.dumps(r[key], ensure_ascii=False)
                        print(f"  {key}：{v[:500]}")
        print("\ndiff：")
        print("\n".join(diff_window(pr, f["path"], f["line"])))
        print()


if __name__ == "__main__":
    main()
