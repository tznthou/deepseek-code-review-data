#!/usr/bin/env python3
"""$0 模擬：多次取樣 + k-of-N 投票，對 precision / A 類 recall 的影響。

資料：2026-09-24 confidence loop 的已標記輪次（每筆 finding 有 item = 依內容分群的 ID）。
分群用的是人工 / 規則指派的 item（oracle clustering）→ 投票效益的**上限**；
production 要自動分群，只會更差。

單位：cluster（同一次跑裡同 item 的多筆算一個）。代表 finding = cluster 內 confidence 最高者，
cluster 的對錯取代表 finding 的標記（production 也只會貼一則）。

strict：disputed 算不成立；lenient：disputed 算成立。
"""
import csv
import itertools
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("<repo>/.claude/experiments/2026-09-24-confidence-loop")
RULES = json.loads((ROOT / "expected-rules.json").read_text())
A_ITEMS = defaultdict(set)
for it in RULES["items"]:
    if it["kind"] == "A":
        A_ITEMS[it["target"]].add(it["id"])

PREFIX = {"python": "PY", "shell": "SH", "probe": "PR"}


def load_round(label: str):
    d = ROOT / "rounds" / label
    key = json.loads((d / "key.json").read_text())
    labels = {}
    for fn in ("labels-auto.csv", "labels-manual.csv"):
        with open(d / fn, newline="") as fh:
            for row in csv.DictReader(fh):
                labels[row["id"]] = (row["item"], row["label"])
    missing = set(key) - set(labels)
    if missing:
        sys.exit(f"{label}: {len(missing)} 筆沒有標記，例如 {sorted(missing)[:3]}")
    runs = defaultdict(lambda: defaultdict(list))  # target -> run_key -> [finding]
    for fid, meta in key.items():
        rnd, target, run, idx = fid.split(":")
        item, lab = labels[fid]
        runs[target][f"{rnd}:{run}"].append(
            {"item": item, "label": lab, "conf": meta["confidence"], "sev": meta["severity"]}
        )
    return runs


def clusters_of_run(findings):
    """同一次跑內依 item 合併；回傳 item -> 代表 finding（conf 最高）。"""
    best = {}
    for f in findings:
        cur = best.get(f["item"])
        if cur is None or f["conf"] > cur["conf"]:
            best[f["item"]] = f
    return best


def is_ok(label, mode):
    return label == "valid" or (mode == "lenient" and label == "disputed")


def vote(runs_subset, k, mode, gate=None):
    """runs_subset: list of per-run cluster dicts。回傳 (kept_total, kept_ok, a_found)。"""
    support = defaultdict(int)
    rep = {}
    for cl in runs_subset:
        for item, f in cl.items():
            support[item] += 1
            if item not in rep or f["conf"] > rep[item]["conf"]:
                rep[item] = f
    kept = [i for i, s in support.items() if s >= k]
    if gate is not None:
        kept = [i for i in kept if rep[i]["conf"] >= gate]
    ok = sum(1 for i in kept if is_ok(rep[i]["label"], mode))
    return len(kept), ok, set(kept)


def summarize(round_labels, n_samples=3000, seed=7):
    rng = random.Random(seed)
    merged = defaultdict(dict)
    for lab in round_labels:
        for target, runs in load_round(lab).items():
            for rk, fs in runs.items():
                merged[target][rk] = clusters_of_run(fs)

    print(f"\n######## 資料：{' + '.join(round_labels)} ########")
    for target in ("python", "shell", "probe"):
        run_keys = sorted(merged[target])
        R = len(run_keys)
        A = A_ITEMS[target]
        print(f"\n=== {target}：{R} 次跑，A 類 {len(A)} 項 ===")

        # ---- 信度 baseline：每個 item 在 R 次跑裡出現幾次 ----
        freq = defaultdict(int)
        labs = defaultdict(set)
        for rk in run_keys:
            for item, f in merged[target][rk].items():
                freq[item] += 1
                labs[item].add(f["label"])
        rows = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        print("item 出現頻率（次/總跑數）與標記：")
        for item, c in rows:
            tag = "A" if item in A else " "
            print(f"   {tag} {item:<22} {c:>2}/{R}  {','.join(sorted(labs[item]))}")

        # 兩兩 Jaccard（item 集合）
        jac = []
        for a, b in itertools.combinations(run_keys, 2):
            sa, sb = set(merged[target][a]), set(merged[target][b])
            if sa | sb:
                jac.append(len(sa & sb) / len(sa | sb))
        print(f"兩兩 run 的 item 集合 Jaccard：平均 {statistics.mean(jac):.2f}（中位數 {statistics.median(jac):.2f}，n={len(jac)}）")

        # ---- 投票模擬 ----
        print(f"{'設定':<22}{'每次輸出cluster數':>10}{'precision嚴格':>14}{'precision寬鬆':>14}{'A類recall':>11}{'API呼叫':>8}")
        configs = [(1, 1, None, "單次跑（現況）"), (1, 1, 0.7, "單次跑、只看≥0.7"),
                   (3, 1, None, "3次聯集"), (3, 2, None, "3次取2"), (3, 3, None, "3次全中"),
                   (5, 3, None, "5次取3"), (5, 1, None, "5次聯集")]
        for n, k, gate, name in configs:
            if n > R:
                continue
            combos = list(itertools.combinations(run_keys, n))
            if len(combos) > n_samples:
                combos = [tuple(rng.sample(run_keys, n)) for _ in range(n_samples)]
            tot = ok_s = ok_l = 0
            rec = []
            for combo in combos:
                subset = [merged[target][rk] for rk in combo]
                t, s, kept = vote(subset, k, "strict", gate)
                _, l, _ = vote(subset, k, "lenient", gate)
                tot += t; ok_s += s; ok_l += l
                rec.append(len(kept & A) / len(A))
            m = len(combos)
            ps = ok_s / tot if tot else float("nan")
            pl = ok_l / tot if tot else float("nan")
            print(f"{name:<22}{tot/m:>10.2f}{ps:>14.3f}{pl:>14.3f}{statistics.mean(rec):>11.3f}{n:>8}")


if __name__ == "__main__":
    summarize(["v02", "v05"])   # 現行 rubric（v1.4.0）
    summarize(["v00", "v04"])   # 舊 rubric，當複製組
