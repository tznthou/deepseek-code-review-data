#!/usr/bin/env python3
"""D0f 裡跟一般 pass 同位置的 finding：逐組並排，看是重複留言還是同一處兩個問題；另算「位置去重」的代價。$0。

同位置：第二次呼叫（hold-v01x）留下的 finding（標了有效規則編號）跟同一配對的 base-k 有 finding
同 PR、同檔、定位後行號相差 ≤3（同 d0_union.py）。
盲標初篩：兩邊都被標成跟同一則 GT「same」→ 對那則 GT 而言是重複；其餘要人讀。
位置去重 = 同位置的第二次呼叫 finding 直接丟掉（最簡單的正式做法），看規則類 recall 掉多少。
輸出：d0f-colocated.md（逐組並排，給人讀）＋終端摘要。
"""
import collections
import json
import sys

sys.dont_write_bytecode = True
from common import LOOP, QODO, gt_rule_names, load_rules, pr_repo, rule_ids, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402
import score_bench  # noqa: E402
from d0_union import B, DUP_LINES, read_labels  # noqa: E402

PAIRINGS = [("base-1", "hold-v01a"), ("base-2", "hold-v01b")]
OUT = LOOP / "d0f-colocated.md"


def main() -> None:
    prs = split_prs("holdout")
    evalset = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in set(prs)]
    emap = {e["id"]: e for e in evalset}
    by_pr = collections.defaultdict(list)
    for e in evalset:
        by_pr[e["pr"]].append(e)
    items = {k: {e["id"] for e in evalset if e["kind"] == k} for k in ("rule", "func")}
    mapping = json.loads((B / "mapping.json").read_text(encoding="utf-8"))
    labels = read_labels()
    same_by_fid = collections.defaultdict(set)
    for pid, m in mapping.items():
        if labels.get(pid) == "same":
            same_by_fid[m["fid"]].add(m["gid"])
    gt_rule = gt_rule_names()
    idmaps = {repo: rule_ids(rs) for repo, rs in load_rules().items()}

    runs = {}
    for label in sorted({l for p in PAIRINGS for l in p}):
        findings, miss = ls.load_findings(label, prs)
        if miss:
            sys.exit(f"{label} 缺 {miss}")
        loc = collections.defaultdict(set)
        for p in score_bench.pairs_for(findings, by_pr):
            if p["loc_hit"]:
                loc[p["fid"]].add(p["gid"])
        runs[label] = {"findings": findings, "loc": loc,
                       "cited": {f["fid"]: ls.cited_rules(f, idmaps.get(pr_repo(f["pr"]), {})) for f in findings}}

    def cited_hit(label: str, f: dict) -> set[str]:
        return {g for g in runs[label]["loc"][f["fid"]] if gt_rule.get(g) and gt_rule[g] in runs[label]["cited"][f["fid"]]}

    def gts(gids: set[str]) -> str:
        return "；".join(f"{g}（{emap[g]['kind']}）{emap[g]['title']}" for g in sorted(gids)) or "無"

    def show(tag: str, label: str, f: dict) -> list[str]:
        ids = ls.CITE_RE.findall(f["title"]) or ls.CITE_RE.findall(f["body"])
        idmap = idmaps.get(pr_repo(f["pr"]), {})
        cite = "、".join(f"R{i} {idmap.get(f'R{i}', '?')}" for i in ids)
        return [f"**{tag}**（`{f['fid']}`，第 {f['line']} 行，信心 {f['confidence']}" + (f"，引用 {cite}" if cite else "") + "）",
                f"- title：{f['title']}", f"- body：{f['body'][:700]}",
                f"- 盲標 same：{gts(same_by_fid[f['fid']])}", f"- 位置命中：{gts(runs[label]['loc'][f['fid']])}", ""]

    def recall(fs: list[tuple[str, dict]]) -> dict:
        same, cited = set(), set()
        for l, f in fs:
            same |= same_by_fid[f["fid"]]
            cited |= cited_hit(l, f)
        return {"rule_same": len(same & items["rule"]), "func_same": len(same & items["func"]),
                "cited_hit": len(cited & items["rule"]), "same_set": same}

    out = ["# D0f 同位置的 finding：重複留言，還是同一處兩個問題？", "",
           "判準（沿用盲標的 Martian 邊界）：一個 code change 能同時修掉兩則 → 重複；同處但各講各的 → 不同問題。", ""]
    summary, totals = [], collections.Counter()
    for base, second in PAIRINGS:
        idx = collections.defaultdict(list)
        for g in runs[base]["findings"]:
            if g["line"] is not None:
                idx[(g["pr"], g["path"])].append(g)
        kept = [f for f in runs[second]["findings"] if runs[second]["cited"][f["fid"]]]
        groups = [(f, [g for g in idx[(f["pr"], f["path"])] if abs(g["line"] - f["line"]) <= DUP_LINES])
                  for f in kept if f["line"] is not None]
        groups = [(f, near) for f, near in groups if near]
        coloc = {f["fid"] for f, _ in groups}
        for k, (f, near) in enumerate(groups, 1):
            shared = same_by_fid[f["fid"]] & set().union(*(same_by_fid[g["fid"]] for g in near))
            verdict = f"盲標：兩邊都跟 {sorted(shared)} same → 對那則 GT 是重複" if shared else "盲標判不出來，要讀"
            totals["shared" if shared else "read"] += 1
            totals["coloc_cited_hit"] += bool(cited_hit(second, f))
            out += [f"## {second} #{k}：{f['pr']}　`{f['path']}`", ""] + show("規範 pass", second, f)
            for g in near:
                out += show("一般 pass", base, g)
            out += [f"→ {verdict}", "", "---", ""]
        base_fs = [(base, g) for g in runs[base]["findings"]]
        d0f = recall(base_fs + [(second, f) for f in kept])
        dedup = recall(base_fs + [(second, f) for f in kept if f["fid"] not in coloc])
        v00 = recall(base_fs)
        summary.append((base, second, len(kept), len(groups), v00, d0f, dedup))

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"逐組並排 → {OUT.name}")
    print(f"同位置 {totals['shared'] + totals['read']} 組：盲標初篩判得出重複 {totals['shared']}、要讀 {totals['read']}｜"
          f"其中規範 pass 那則是引用命中的 {totals['coloc_cited_hit']} 組")
    n_rule, n_func = len(items["rule"]), len(items["func"])
    for base, second, n_kept, n_col, v00, d0f, dedup in summary:
        print(f"{base}+{second}：留下 {n_kept}、同位置 {n_col}｜規則同一問題 v00 {v00['rule_same']} → D0f {d0f['rule_same']}"
              f" → 位置去重 {dedup['rule_same']}（/{n_rule}）｜引用命中 D0f {d0f['cited_hit']} → 去重 {dedup['cited_hit']}｜"
              f"功能同一問題 {v00['func_same']} → {d0f['func_same']} → {dedup['func_same']}（/{n_func}）")
        print(f"  位置去重會掉的：{gts(d0f['same_set'] - dedup['same_set'])}")


if __name__ == "__main__":
    main()
