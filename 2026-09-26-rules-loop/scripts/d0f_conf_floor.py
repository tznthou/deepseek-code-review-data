#!/usr/bin/env python3
"""D0f 規範 pass 的信心下限：真的違規落在哪些信心值？設下限會不會誤殺？$0。

規範 pass 留下的 finding（標了有效規則編號）依信心值分組，逐組數「真的違規」：
  - 引用命中：位置命中 ＋ 引用的正是 GT 那條規則（holdout 驗過 96% 準）
  - 盲標 same（只有 holdout）：跟某則規則類 GT 被標成同一個問題
兩個切分都算：holdout（hold-v01a/b，有盲標）、調參組（v01a/b，只有引用命中，但 PR 多一倍）。
不挑門檻：列完整分布，再看 kit 現有的 0.7（post_review.py 的 --min-confidence）一刀下去的結果。
另外看 kit 現有的行內條件（嚴重度 ≥ minor 且信心 ≥ 0.7）會不會把真的違規擋在行內留言外。
用法：d0f_conf_floor.py [--list-below 0.7]
"""
import argparse
import collections
import json
import sys

sys.dont_write_bytecode = True
from common import QODO, gt_rule_names, load_rules, pr_repo, rule_ids, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402
import score_bench  # noqa: E402
from d0_union import B, read_labels  # noqa: E402

SPLITS = {"holdout": [("base-1", "hold-v01a"), ("base-2", "hold-v01b")],
          "tune": [("base-1", "v01a"), ("base-2", "v01b")]}
KIT_FLOOR = 0.7
INLINE_SEV = {"blocker", "major", "minor"}  # post_review.py 預設 --min-severity minor


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-below", type=float, default=KIT_FLOOR)
    args = ap.parse_args()

    mapping = json.loads((B / "mapping.json").read_text(encoding="utf-8"))
    labels = read_labels()
    same_by_fid = collections.defaultdict(set)
    for pid, m in mapping.items():
        if labels.get(pid) == "same":
            same_by_fid[m["fid"]].add(m["gid"])
    labeled = {m["run"] for m in mapping.values()}
    gt_rule = gt_rule_names()
    idmaps = {repo: rule_ids(rs) for repo, rs in load_rules().items()}

    for split, pairings in SPLITS.items():
        prs = split_prs(split)
        evalset = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in set(prs)]
        emap = {e["id"]: e for e in evalset}
        by_pr = collections.defaultdict(list)
        for e in evalset:
            by_pr[e["pr"]].append(e)
        rule_items = {e["id"] for e in evalset if e["kind"] == "rule"}

        rows, gt_cover = [], collections.defaultdict(lambda: collections.defaultdict(list))
        for _base, second in pairings:
            findings, miss = ls.load_findings(second, prs)
            if miss:
                sys.exit(f"{second} 缺 {miss}")
            sev = {}
            for pr in prs:
                for k, f in enumerate(json.loads((ls.rounds_dir(second) / f"{pr}.json").read_text(encoding="utf-8")), 1):
                    sev[f"{second}:{pr}:{k}"] = f.get("severity", "?")
            loc = collections.defaultdict(set)
            for p in score_bench.pairs_for(findings, by_pr):
                if p["loc_hit"]:
                    loc[p["fid"]].add(p["gid"])
            for f in findings:
                cited = ls.cited_rules(f, idmaps.get(pr_repo(f["pr"]), {}))
                if not cited:
                    continue
                hit = {g for g in loc[f["fid"]] if gt_rule.get(g) in cited} & rule_items
                blind = (same_by_fid[f["fid"]] & rule_items) if second in labeled else None
                r = {"run": second, "fid": f["fid"], "pr": f["pr"], "conf": f["confidence"],
                     "sev": sev[f["fid"]], "hit": hit, "blind": blind, "title": f["title"]}
                rows.append(r)
                for g in hit | (blind or set()):
                    gt_cover[second][g].append(r["conf"])

        true_ = lambda r: bool(r["hit"]) or bool(r["blind"])  # noqa: E731
        print(f"=== {split}（{len(prs)} PR、規則類 {len(rule_items)} 則；兩輪合計）===")
        print(f"規範 pass 留下 {len(rows)} 則；「真的違規」= 引用命中" + ("或盲標 same" if split == "holdout" else "（沒有盲標）"))
        dist = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            dist[r["conf"]][0] += 1
            dist[r["conf"]][1] += true_(r)
        print("信心  則數  真的違規")
        for c in sorted(dist, reverse=True):
            print(f"{c:<5} {dist[c][0]:>4}  {dist[c][1]:>4}")
        lo = [r for r in rows if r["conf"] < KIT_FLOOR]
        print(f"→ 信心 < {KIT_FLOOR}：{len(lo)} 則，其中真的違規 {sum(map(true_, lo))} 則")

        # GT 層級：下限 0.7 之後，引用命中（與盲標 same）的規則類 GT 還剩幾則
        for second in {p[1] for p in pairings}:
            cov = gt_cover[second]
            kept = {g for g, cs in cov.items() if max(cs) >= KIT_FLOOR}
            print(f"  {second}：規範 pass 抓到的規則類 GT {len(cov)} 則 → 下限 {KIT_FLOOR} 後 {len(kept)} 則"
                  + (f"（掉的：{sorted(set(cov) - kept)}）" if set(cov) - kept else ""))

        inline_ok = [r for r in rows if r["conf"] >= KIT_FLOOR and r["sev"] in INLINE_SEV]
        tr = [r for r in rows if true_(r)]
        print(f"嚴重度分布（留下的）：{dict(collections.Counter(r['sev'] for r in rows))}｜真的違規：{dict(collections.Counter(r['sev'] for r in tr))}")
        print(f"過得了 kit 行內門檻（嚴重度 ≥ minor 且信心 ≥ {KIT_FLOOR}）：{len(inline_ok)}/{len(rows)} 則；"
              f"真的違規 {sum(map(true_, inline_ok))}/{len(tr)} 則")
        print(f"\n信心 < {args.list_below} 的逐則：")
        for r in sorted((r for r in rows if r["conf"] < args.list_below), key=lambda r: r["conf"]):
            tag = "真的違規" if true_(r) else "沒對上 GT"
            print(f"  {r['fid']:<24} 信心 {r['conf']}｜{r['sev']:<7}｜{tag}"
                  f"{'（引用命中 ' + ','.join(sorted(r['hit'])) + '）' if r['hit'] else ''}｜{r['title'][:70]}")
        print()


if __name__ == "__main__":
    main()
