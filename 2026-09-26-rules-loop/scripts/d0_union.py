#!/usr/bin/env python3
"""D 的評分：「一般 pass（v00）＋另一次附規範的呼叫」合併後會怎樣。$0。

  <name>  = base-k ∪ 第二次呼叫（全留）
  <name>f = base-k ∪ 第二次呼叫裡「標了有效規則編號」的 finding（程式過濾，不靠 prompt）
預設第二次呼叫 = hold-v01a/b（v01 原樣）→ D0／D0f；D1 用 --second hold-d1a hold-d1b --name D1 --alone D1單獨。
配對同 D-plan：base-1 ↔ 第一個、base-2 ↔ 第二個。

同一問題：blind/ 的盲標（標記員看不到編號、也不知道是哪個條件；2026-09-26 標完），只有 base-1/2、hold-v01a/b 有；
  組合裡有沒標過的 run 就印「—」，不把沒標的當成 no。
位置命中、引用命中、高信心未對上：跟 loop_score 同一套算法（多對多配對，任一 finding 命中就算）。
重複：第二次呼叫的 finding 跟同一配對的一般 pass 同 PR、同檔，定位後行號相差 ≤3。
用法：d0_union.py [--second A B] [--name D0] [--alone v01] [--json 輸出.json]
"""
import argparse
import collections
import csv
import json
import sys

sys.dont_write_bytecode = True
from common import LOOP, QODO, gt_rule_names, load_rules, pr_repo, rule_ids, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402
import score_bench  # noqa: E402

B = LOOP / "blind"
BASES = ("base-1", "base-2")
DUP_LINES = 3


def read_labels() -> dict[str, str]:
    labels = {}
    for part in sorted(B.glob("labels-part*.csv")):
        with open(part, newline="", encoding="utf-8") as fh:
            labels.update({r["pair"].strip(): r["label"].strip().lower() for r in csv.DictReader(fh)})
    return labels


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--second", nargs=2, default=["hold-v01a", "hold-v01b"])
    ap.add_argument("--name", default="D0")
    ap.add_argument("--alone", default="v01", help="第二次呼叫單獨那一欄的名稱")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    pairings = list(zip(BASES, args.second))

    prs = split_prs("holdout")
    evalset = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in set(prs)]
    by_pr = collections.defaultdict(list)
    for e in evalset:
        by_pr[e["pr"]].append(e)
    items = {k: {e["id"] for e in evalset if e["kind"] == k} for k in ("rule", "func")}

    mapping = json.loads((B / "mapping.json").read_text(encoding="utf-8"))
    labels = read_labels()
    missing = set(mapping) - set(labels)
    if missing:
        sys.exit(f"盲標缺 {len(missing)} 組，不算")
    labeled = {m["run"] for m in mapping.values()}
    same_by_fid = collections.defaultdict(set)
    for pid, m in mapping.items():
        if labels[pid] == "same":
            same_by_fid[m["fid"]].add(m["gid"])

    gt_rule = gt_rule_names()
    idmaps = {repo: rule_ids(rs) for repo, rs in load_rules().items()}
    runs = {}
    for label in sorted({l for p in pairings for l in p}):
        findings, miss = ls.load_findings(label, prs)
        if miss:
            sys.exit(f"{label} 缺 {miss}")
        loc = collections.defaultdict(set)
        for p in score_bench.pairs_for(findings, by_pr):
            if p["loc_hit"]:
                loc[p["fid"]].add(p["gid"])
        # 盲標的 fid 是標記當時用同一支 load_findings 編的；對不上就代表 round 檔被動過，停
        known = {m["fid"] for m in mapping.values() if m["run"] == label}
        if not known <= {f["fid"] for f in findings}:
            sys.exit(f"{label} 的 finding 編號跟盲標對不上")
        runs[label] = {"findings": findings, "loc": loc,
                       "cited": {f["fid"]: ls.cited_rules(f, idmaps.get(pr_repo(f["pr"]), {})) for f in findings}}

    def pick(label: str, cited_only: bool) -> list[tuple[str, dict]]:
        r = runs[label]
        return [(label, f) for f in r["findings"] if not cited_only or r["cited"][f["fid"]]]

    def dups(base: str, second: list[tuple[str, dict]]) -> int:
        idx = collections.defaultdict(list)
        for f in runs[base]["findings"]:
            if f["line"] is not None:
                idx[(f["pr"], f["path"])].append(f["line"])
        return sum(any(abs(f["line"] - x) <= DUP_LINES for x in idx[(f["pr"], f["path"])])
                   for _, f in second if f["line"] is not None)

    def metrics(fs: list[tuple[str, dict]], members: set[str]) -> dict:
        same, loc, cited_hit = set(), set(), set()
        for l, f in fs:
            same |= same_by_fid[f["fid"]]
            hits = runs[l]["loc"][f["fid"]]
            loc |= hits
            cited_hit |= {g for g in hits if gt_rule.get(g) and gt_rule[g] in runs[l]["cited"][f["fid"]]}
        hi = [(l, f) for l, f in fs if f["confidence"] >= ls.HI_CONF and f["line"] is not None]
        unmatched = sum(not runs[l]["loc"][f["fid"]] for l, f in hi)
        n = len(prs)
        blind = members <= labeled
        return {
            "rule_same": len(same & items["rule"]) / len(items["rule"]) if blind else None,
            "func_same": len(same & items["func"]) / len(items["func"]) if blind else None,
            "all_same_n": len(same & (items["rule"] | items["func"])) if blind else None,
            "cited_hit": len(cited_hit & items["rule"]) / len(items["rule"]),
            "cited_hit_n": len(cited_hit & items["rule"]),
            "rule_pos": len(loc & items["rule"]) / len(items["rule"]),
            "func_pos": len(loc & items["func"]) / len(items["func"]),
            "findings_pr": len(fs) / n,
            "hi_pr": len(hi) / n,
            "hi_unmatched_pr": unmatched / n,
            "hi_unmatched_n": unmatched,
            "rule_items": len(items["rule"]),
            "prs": n,
        }

    names = ("v00", args.alone, args.name, args.name + "f")
    rows = collections.defaultdict(list)
    for base, second in pairings:
        second_all, second_cited = pick(second, False), pick(second, True)
        variants = {
            names[0]: (pick(base, False), {base}, []),
            names[1]: (second_all, {second}, None),
            names[2]: (pick(base, False) + second_all, {base, second}, second_all),
            names[3]: (pick(base, False) + second_cited, {base, second}, second_cited),
        }
        for name, (fs, members, kept) in variants.items():
            m = metrics(fs, members)
            m["second_pr"] = len(kept) / len(prs) if kept is not None else None
            m["dup_n"] = dups(base, kept) if kept is not None else None
            m["pairing"] = f"{base}+{second}"
            rows[name].append(m)

    print(f"holdout {len(prs)} PR｜規則類 {len(items['rule'])}、功能性 {len(items['func'])}｜"
          f"配對 {', '.join('+'.join(p) for p in pairings)}，下面是兩組平均（括號內是兩組各自的值）\n")
    cols = [("rule_same", "規則同一問題", 3), ("func_same", "功能同一問題", 3), ("all_same_n", "同一問題合計(則)", 1),
            ("cited_hit", "引用命中", 3), ("rule_pos", "規則位置", 3), ("func_pos", "功能位置", 3),
            ("findings_pr", "finding/PR", 2), ("hi_pr", "高信心/PR", 2), ("hi_unmatched_pr", "高信心未對上/PR", 2),
            ("second_pr", "第二次呼叫留下/PR", 2), ("dup_n", "跟一般 pass 重複(筆)", 1)]
    for key, label, nd in cols:
        cells = []
        for v in names:
            vals = [r[key] for r in rows[v]]
            if any(x is None for x in vals):
                cells.append(f"{v} —")
                continue
            cells.append(f"{v} {sum(vals) / len(vals):.{nd}f}（{' / '.join(f'{x:.{nd}f}' for x in vals)}）")
        print(f"{label:<14} " + "｜".join(cells))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
