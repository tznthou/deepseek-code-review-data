#!/usr/bin/env python3
"""事後分析（不是跑前定稿的判準）：A／B 的 precision 與 AUC 差距有沒有超出雜訊。

同一次跑的 finding 彼此相關，所以以「一次跑」為單位重新分組；分組在同一個標的內進行
（每個標的 A、B 各 10 次跑），維持兩組的標的組成相同。雙尾 p = |置換差| ≥ |實測差| 的比例。
用法：python3 scripts/posthoc_permutation.py [--n 10000]
"""

import argparse
import csv
import json
import pathlib
import random
import sys

LOOP = pathlib.Path(__file__).resolve().parents[2] / "2026-09-24-confidence-loop"
sys.path.insert(0, str(LOOP / "scripts"))
import analyze_round as ar  # noqa: E402

ROUNDS = {"A": ["ph-A1", "ph-A2"], "B": ["ph-B1", "ph-B2"]}
TARGETS = ["probe", "python", "shell"]


def load_runs() -> list[dict]:
    runs = []
    for arm, labs in ROUNDS.items():
        for lab in labs:
            rdir = LOOP / "rounds" / lab
            key = json.loads((rdir / "key.json").read_text(encoding="utf-8"))
            labels = {r["id"]: r["label"] for r in csv.DictReader((rdir / "labels-auto.csv").open(encoding="utf-8"))}
            labels.update({r["id"]: r["label"] for r in csv.DictReader((rdir / "labels-manual.csv").open(encoding="utf-8"))})
            for t in TARGETS:
                for path in sorted(rdir.glob(f"{t}-*.json")):
                    run = int(path.stem.rsplit("-", 1)[1])
                    items = json.loads(path.read_text(encoding="utf-8"))
                    rows = [(key[f"{lab}:{t}:{run}:{k}"]["confidence"], labels[f"{lab}:{t}:{run}:{k}"])
                            for k in range(1, len(items) + 1)]
                    runs.append({"arm": arm, "target": t, "rows": rows})
    return runs


def stats(runs: list[dict], arm: str) -> tuple[float, float]:
    rows = [r for x in runs if x["arm"] == arm for r in x["rows"]]
    pos = [c for c, lb in rows if lb == "valid"]
    neg = [c for c, lb in rows if lb != "valid"]
    return len(pos) / len(rows), float(ar.auc(pos, neg))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    args = ap.parse_args()
    runs = load_runs()
    assert len(runs) == 60, len(runs)
    (pa, aa), (pb, ab) = stats(runs, "A"), stats(runs, "B")
    obs_p, obs_auc = pb - pa, ab - aa
    print(f"實測：precision A {pa:.1%} → B {pb:.1%}（{obs_p * 100:+.1f}pp）｜AUC 嚴格 A {aa:.3f} → B {ab:.3f}（{obs_auc:+.3f}）")

    rng = random.Random(20261001)
    hit_p = hit_auc = 0
    by_t = {t: [x for x in runs if x["target"] == t] for t in TARGETS}
    for _ in range(args.n):
        perm = []
        for t in TARGETS:
            arms = [x["arm"] for x in by_t[t]]
            rng.shuffle(arms)
            perm += [{**x, "arm": a} for x, a in zip(by_t[t], arms)]
        (qa, ua), (qb, ub) = stats(perm, "A"), stats(perm, "B")
        hit_p += abs(qb - qa) >= abs(obs_p) - 1e-12
        hit_auc += abs(ub - ua) >= abs(obs_auc) - 1e-12
    print(f"置換 {args.n} 次（以一次跑為單位、標的內分組）：precision 雙尾 p = {hit_p / args.n:.3f}｜AUC 雙尾 p = {hit_auc / args.n:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
