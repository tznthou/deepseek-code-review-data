#!/usr/bin/env python3
"""抽查引用命中是不是真的：隨機抽 N 筆（seed 固定），並排印出標準答案與 finding，給人判「同一個問題」。

用法：spotcheck.py <標籤> [N=8] [seed=1]
"""
import collections
import json
import random
import sys

sys.dont_write_bytecode = True
from common import QODO, gt_rule_names, load_rules, pr_repo, rule_ids, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402
import score_bench  # noqa: E402


def main() -> None:
    label = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    prs = split_prs("tune")
    evalset = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in set(prs)]
    emap = {e["id"]: e for e in evalset}
    by_pr = collections.defaultdict(list)
    for e in evalset:
        by_pr[e["pr"]].append(e)
    findings, _ = ls.load_findings(label, prs)
    fmap = {f["fid"]: f for f in findings}
    idmaps = {repo: rule_ids(rs) for repo, rs in load_rules().items()}
    gt_rule = gt_rule_names()
    hits = []
    for p in score_bench.pairs_for(findings, by_pr):
        f = fmap[p["fid"]]
        want = gt_rule.get(p["gid"])
        if p["loc_hit"] and want and want in ls.cited_rules(f, idmaps.get(pr_repo(f["pr"]), {})):
            hits.append((p["gid"], p["fid"]))
    hits = sorted(set(hits))
    print(f"{label}：引用命中配對 {len(hits)} 組，抽 {min(n, len(hits))} 組（seed {seed}）\n")
    for gid, fid in random.Random(seed).sample(hits, min(n, len(hits))):
        e, f = emap[gid], fmap[fid]
        print(f"## {gid}  ⇄  {fid}（信心 {f['confidence']:.2f}）")
        print(f"GT 規則：{gt_rule[gid]}")
        print(f"GT：{e['title']} — {e['description'][:220]}")
        print(f"finding：{f['title'][:120]}")
        print(f"         {f['body'][:260]}\n")


if __name__ == "__main__":
    main()
