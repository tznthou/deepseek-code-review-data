#!/usr/bin/env python3
"""holdout 盲標的計分：合併 labels-part*.csv → 對回 mapping.json → 算「同一個問題」recall 與幾個一致率。$0。

輸出：
- 每個 run、每種 kind 的同一問題 recall（含 partial 另列），條件平均（v00 = base-1/base-2、v01 = hold-v01a/b）
- 主 session 30 組抽樣 vs 標記員：三類一致率、same 與否一致率
- 漂移：base-1 的新標籤 vs Qodo 當時的舊標籤（同一組配對）
- v01 的引用命中在 holdout 上有幾成被標成 same（代理指標的準確率）；規則類同一問題裡沒標編號的有幾筆
"""
import collections
import csv
import json
import math
import sys

sys.dont_write_bytecode = True
from common import LOOP, QODO, gt_rule_names, load_rules, pr_repo, rule_ids, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402

B = LOOP / "blind"
RUNS = {"v00": ("base-1", "base-2"), "v01": ("hold-v01a", "hold-v01b")}
VALID = {"same", "partial", "no"}


def read_csv(path) -> dict[str, str]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["pair"].strip(): r["label"].strip().lower() for r in csv.DictReader(fh)}


def main() -> None:
    mapping = json.loads((B / "mapping.json").read_text(encoding="utf-8"))
    labels, dup = {}, []
    for part in sorted(B.glob("labels-part*.csv")):
        for pid, lab in read_csv(part).items():
            if pid in labels:
                dup.append(pid)
            labels[pid] = lab
    missing = sorted(set(mapping) - set(labels))
    extra = sorted(set(labels) - set(mapping))
    invalid = sorted(p for p, l in labels.items() if l not in VALID)
    print(f"標籤 {len(labels)} / 配對 {len(mapping)}｜缺 {len(missing)}｜多 {len(extra)}｜重複 {len(dup)}｜不合法 {len(invalid)}")
    if missing or invalid:
        print(f"  缺：{missing[:20]}  不合法：{invalid[:20]}")
    print("  分佈：", dict(collections.Counter(labels.values())))

    ev = [e for e in json.loads((QODO / "evalset.json").read_text(encoding="utf-8")) if e["pr"] in set(split_prs("holdout"))]
    items = {k: [e["id"] for e in ev if e["kind"] == k] for k in ("rule", "func")}

    # 每個 run 的同一問題 recall
    res = {}
    for cond, runs in RUNS.items():
        for run in runs:
            same = {m["gid"] for p, m in mapping.items() if m["run"] == run and labels.get(p) == "same"}
            part = {m["gid"] for p, m in mapping.items() if m["run"] == run and labels.get(p) in ("same", "partial")}
            res[run] = {k: (sum(g in same for g in ids) / len(ids), sum(g in part for g in ids) / len(ids),
                            sum(g in same for g in ids)) for k, ids in items.items()}
    print(f"\n=== holdout 同一問題 recall（規則類 {len(items['rule'])}、功能性 {len(items['func'])}）===")
    for cond, runs in RUNS.items():
        for run in runs:
            r = res[run]
            print(f"  {cond} {run:<10} 規則 {r['rule'][0]:.3f}（{r['rule'][2]}，含 partial {r['rule'][1]:.3f}）｜"
                  f"功能 {r['func'][0]:.3f}（{r['func'][2]}，含 partial {r['func'][1]:.3f}）")
    for k in ("rule", "func"):
        v0 = [res[r][k][0] for r in RUNS["v00"]]
        v1 = [res[r][k][0] for r in RUNS["v01"]]
        gaps = [abs(v0[0] - v0[1]), abs(v1[0] - v1[1])]
        sigma = (sum(gaps) / 2) * math.sqrt(math.pi) / 2  # a−b ~ N(0, 2σ²)
        d = sum(v1) / 2 - sum(v0) / 2
        z = d / sigma if sigma else float("inf")
        print(f"  → {k}：v00 平均 {sum(v0) / 2:.3f}、v01 平均 {sum(v1) / 2:.3f}，差 {d:+.3f}"
              f"（σ≈{sigma:.3f}，約 {z:+.1f} 個標準誤；σ 只由兩組 a/b 估，很粗）")

    # 主 session 抽樣 vs 標記員
    spot = read_csv(B / "spot-main.csv")
    both = [p for p in spot if p in labels]
    exact = sum(spot[p] == labels[p] for p in both)
    same_agree = sum((spot[p] == "same") == (labels[p] == "same") for p in both)
    print(f"\n主 session 抽樣 vs 標記員：三類一致 {exact}/{len(both)}｜same 與否一致 {same_agree}/{len(both)}")
    for p in both:
        if spot[p] != labels[p]:
            print(f"  分歧 {p}：主 session {spot[p]}、標記員 {labels[p]}（{mapping[p]['cond']} {mapping[p]['kind']}）")

    # 漂移：base-1 新標籤 vs Qodo 舊標籤
    old = read_csv(QODO / "rounds/base-1/labels.csv")
    pairs = [(p, m["qodo_pair"]) for p, m in mapping.items() if m["run"] == "base-1" and m["qodo_pair"] in old]
    ex = sum(labels.get(p) == old[q] for p, q in pairs)
    sa = sum((labels.get(p) == "same") == (old[q] == "same") for p, q in pairs)
    print(f"漂移（base-1 新 vs Qodo 舊，同一組配對）：三類一致 {ex}/{len(pairs)}｜same 與否一致 {sa}/{len(pairs)}")

    # 引用命中的準確率、沒標編號的同一問題
    gt_rule = gt_rule_names()
    idmaps = {repo: rule_ids(rs) for repo, rs in load_rules().items()}
    prs = split_prs("holdout")
    for run in RUNS["v01"]:
        findings, _ = ls.load_findings(run, prs)
        fmap = {f["fid"]: f for f in findings}
        cited, cited_same, cited_gids, rule_same = 0, 0, set(), set()
        for p, m in mapping.items():
            if m["run"] != run or m["kind"] != "rule":
                continue
            if labels.get(p) == "same":
                rule_same.add(m["gid"])
            f = fmap[m["fid"]]
            if m["loc_hit"] and gt_rule.get(m["gid"]) in ls.cited_rules(f, idmaps.get(pr_repo(f["pr"]), {})):
                cited += 1
                cited_same += labels.get(p) == "same"
                cited_gids.add(m["gid"])
        print(f"{run}：引用命中配對 {cited} 組，被標 same {cited_same}｜規則類同一問題 {len(rule_same)} 則，"
              f"其中引用命中沒接住的 {len(rule_same - cited_gids)} 則")

    (B / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
