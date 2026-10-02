#!/usr/bin/env python3
"""$0 模擬 II：自動分群（production 做得到的）vs oracle 分群；以及「聯集 + 分層」設計。

自動分群兩種：
  loc     同 path、行號差 ≤ 2，跨 run 連通分量
  snippet existing_code 正規化後共用至少一行（去空白後 ≥ 8 字元），跨 run 連通分量
設計：
  vote2   3 次跑，support ≥ 2 才輸出（全部當 inline）
  tiered  3 次跑取聯集；support ≥ 2 且代表 conf ≥ 0.7 → inline，其餘 → 摘要表
  現況    單次跑；conf ≥ 0.7 → inline，其餘 → 摘要表
"""
import csv
import itertools
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path("<repo>/.claude/experiments/2026-09-24-confidence-loop")
RULES = json.loads((ROOT / "expected-rules.json").read_text())
A_ITEMS = defaultdict(set)
for it in RULES["items"]:
    if it["kind"] == "A":
        A_ITEMS[it["target"]].add(it["id"])


def load(label):
    d = ROOT / "rounds" / label
    labels = {}
    for fn in ("labels-auto.csv", "labels-manual.csv"):
        with open(d / fn, newline="") as fh:
            for row in csv.DictReader(fh):
                labels[row["id"]] = (row["item"], row["label"])
    runs = defaultdict(dict)
    for p in sorted(d.glob("*-*.json")):
        stem = p.stem
        if stem.count("-") != 1:
            continue
        target, run = stem.split("-")
        if target not in A_ITEMS:
            continue
        try:
            items = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        fs = []
        for k, f in enumerate(items, 1):
            fid = f"{label}:{target}:{run}:{k}"
            item, lab = labels[fid]
            try:
                line = int(f.get("line"))
            except (TypeError, ValueError):
                line = -999
            fs.append({"id": fid, "item": item, "label": lab, "conf": float(f["confidence"]),
                       "path": f.get("path"), "line": line,
                       "snip": {ln.strip() for ln in str(f.get("existing_code", "")).splitlines()
                                if len("".join(ln.split())) >= 8}})
        runs[target][f"{label}:{run}"] = fs
    return runs


def components(findings, linked):
    parent = list(range(len(findings)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, j in itertools.combinations(range(len(findings)), 2):
        if linked(findings[i], findings[j]):
            parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i, f in enumerate(findings):
        groups[find(i)].append(f)
    return list(groups.values())


def link_loc(a, b):
    return a["path"] == b["path"] and abs(a["line"] - b["line"]) <= 2


def link_snip(a, b):
    return a["path"] == b["path"] and bool(a["snip"] & b["snip"])


def cluster(trip_findings, scheme):
    """trip_findings: [(run_key, finding)]；回傳 clusters（每個是 finding list，帶 _run）。"""
    flat = [{**f, "_run": rk} for rk, fs in trip_findings for f in fs]
    if scheme == "oracle":
        g = defaultdict(list)
        for f in flat:
            g[f["item"]].append(f)
        return list(g.values())
    return components(flat, link_loc if scheme == "loc" else link_snip)


def ok(label):  # strict
    return label == "valid"


def evaluate(runs, scheme, n=3, samples=400, seed=5):
    rng = random.Random(seed)
    agg = defaultdict(list)
    purity_mixed_item = purity_mixed_label = total_clusters = 0
    for target, rs in runs.items():
        keys = sorted(rs)
        A = A_ITEMS[target]
        combos = list(itertools.combinations(keys, n))
        if len(combos) > samples:
            combos = [tuple(rng.sample(keys, n)) for _ in range(samples)]
        for combo in combos:
            cl = cluster([(rk, rs[rk]) for rk in combo], scheme)
            for c in cl:
                total_clusters += 1
                if len({f["item"] for f in c}) > 1:
                    purity_mixed_item += 1
                if len({ok(f["label"]) for f in c}) > 1:
                    purity_mixed_label += 1
            info = []
            for c in cl:
                sup = len({f["_run"] for f in c})
                rep = max(c, key=lambda f: f["conf"])
                items = {f["item"] for f in c}
                info.append((sup, rep, items))
            # vote2
            kept = [x for x in info if x[0] >= 2]
            agg[(target, "vote2", "n")].append(len(kept))
            agg[(target, "vote2", "ok")].append(sum(ok(x[1]["label"]) for x in kept))
            agg[(target, "vote2", "rec")].append(len(set().union(*[x[2] for x in kept]) & A) / len(A) if kept else 0)
            # tiered
            inline = [x for x in info if x[0] >= 2 and x[1]["conf"] >= 0.7]
            agg[(target, "tier_inline", "n")].append(len(inline))
            agg[(target, "tier_inline", "ok")].append(sum(ok(x[1]["label"]) for x in inline))
            agg[(target, "tier_inline", "rec")].append(len(set().union(*[x[2] for x in inline]) & A) / len(A) if inline else 0)
            agg[(target, "tier_all", "n")].append(len(info))
            agg[(target, "tier_all", "ok")].append(sum(ok(x[1]["label"]) for x in info))
            agg[(target, "tier_all", "rec")].append(len(set().union(*[x[2] for x in info]) & A) / len(A) if info else 0)
    return agg, purity_mixed_item, purity_mixed_label, total_clusters


def baseline(runs):
    agg = defaultdict(list)
    for target, rs in runs.items():
        A = A_ITEMS[target]
        for rk, fs in rs.items():
            inline = [f for f in fs if f["conf"] >= 0.7]
            for name, sel in (("single_inline", inline), ("single_all", fs)):
                agg[(target, name, "n")].append(len(sel))
                agg[(target, name, "ok")].append(sum(ok(f["label"]) for f in sel))
                agg[(target, name, "rec")].append(len({f["item"] for f in sel} & A) / len(A))
    return agg


def show(agg, names):
    for target in ("python", "shell", "probe"):
        cells = []
        for nm in names:
            n = sum(agg[(target, nm, "n")]); k = sum(agg[(target, nm, "ok")])
            m = len(agg[(target, nm, "n")])
            cells.append(f"{nm}: {n/m:4.1f}筆 P={k/n if n else float('nan'):.3f} R={statistics.mean(agg[(target, nm, 'rec')]):.3f}")
        print(f"  {target:<7}" + " ｜ ".join(cells))


if __name__ == "__main__":
    for rset in (["v02", "v05"], ["v00", "v04"]):
        runs = defaultdict(dict)
        for lab in rset:
            for t, rs in load(lab).items():
                runs[t].update(rs)
        print(f"\n######## {' + '.join(rset)}（strict）########")
        print("現況（單次跑）:")
        show(baseline(runs), ["single_inline", "single_all"])
        for scheme in ("oracle", "loc", "snippet"):
            agg, mi, ml, tc = evaluate(runs, scheme)
            print(f"分群={scheme}: cluster 混到不同 item {mi}/{tc} ({mi/tc:.1%})，混到對錯兩種 {ml}/{tc} ({ml/tc:.1%})")
            show(agg, ["vote2", "tier_inline", "tier_all"])
