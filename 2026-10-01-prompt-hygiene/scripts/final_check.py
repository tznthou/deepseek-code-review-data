#!/usr/bin/env python3
"""追加判準（README「追加」，08:09 UTC 定稿）：A1–A4 vs B1–B4 合併，precision 差（B − A）≥ −3pp → 出貨。

兩個版本都算：
  (i)  跑前定稿的標記流程：自動標記＋人工判定＋抽查
  (ii) 再加上殘差檢查（blind3/，第二批抽查發現自動規則系統性套錯之後才加，兩組一起盲標）
另附：AUC（嚴格）、以一次跑為單位、標的內分組的置換檢定（precision）。
用法：python3 scripts/final_check.py [--n 5000]
"""

import argparse
import csv
import json
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
LOOP = HERE.parent / "2026-09-24-confidence-loop"
sys.path.insert(0, str(LOOP / "scripts"))
import analyze_round as ar  # noqa: E402

ARMS = {"A": [f"ph-A{i}" for i in range(1, 5)], "B": [f"ph-B{i}" for i in range(1, 5)]}
TARGETS = ["probe", "python", "shell"]
RESIDUAL = set(json.loads((HERE / "blind3" / "blind-map.json").read_text(encoding="utf-8")).values())
RESIDUAL_CHANGED = {r["code"] for r in csv.DictReader((HERE / "blind3" / "blind-labels.csv").open(encoding="utf-8"))}
RESIDUAL_MAP = json.loads((HERE / "blind3" / "blind-map.json").read_text(encoding="utf-8"))
RESIDUAL_IDS = {RESIDUAL_MAP[c] for c in RESIDUAL_CHANGED}


def load_runs(with_residual: bool) -> list[dict]:
    runs = []
    for arm, labs in ARMS.items():
        for lab in labs:
            rdir = LOOP / "rounds" / lab
            key = json.loads((rdir / "key.json").read_text(encoding="utf-8"))
            labels = {r["id"]: r["label"] for r in csv.DictReader((rdir / "labels-auto.csv").open(encoding="utf-8"))}
            for r in csv.DictReader((rdir / "labels-manual.csv").open(encoding="utf-8")):
                if not with_residual and r["id"] in RESIDUAL_IDS:
                    continue
                labels[r["id"]] = r["label"]
            for t in TARGETS:
                for path in sorted(rdir.glob(f"{t}-*.json")):
                    run = int(path.stem.rsplit("-", 1)[1])
                    n = len(json.loads(path.read_text(encoding="utf-8")))
                    rows = [(key[f"{lab}:{t}:{run}:{k}"]["confidence"], labels[f"{lab}:{t}:{run}:{k}"])
                            for k in range(1, n + 1)]
                    runs.append({"arm": arm, "target": t, "rows": rows})
    return runs


def stats(runs: list[dict], arm: str) -> dict:
    rows = [r for x in runs if x["arm"] == arm for r in x["rows"]]
    pos = [c for c, lb in rows if lb == "valid"]
    neg = [c for c, lb in rows if lb != "valid"]
    return {"n": len(rows), "valid": len(pos), "prec": len(pos) / len(rows), "auc": float(ar.auc(pos, neg))}


def perm_p(runs: list[dict], obs: float, n: int) -> float:
    rng = random.Random(20261001)
    by_t = {t: [x for x in runs if x["target"] == t] for t in TARGETS}
    hit = 0
    for _ in range(n):
        perm = []
        for t in TARGETS:
            arms = [x["arm"] for x in by_t[t]]
            rng.shuffle(arms)
            perm += [{**x, "arm": a} for x, a in zip(by_t[t], arms)]
        d = stats(perm, "B")["prec"] - stats(perm, "A")["prec"]
        hit += abs(d) >= abs(obs) - 1e-12
    return hit / n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    args = ap.parse_args()
    print(f"殘差檢查：重看 {len(RESIDUAL)} 筆、改掉 {len(RESIDUAL_IDS)} 筆\n")
    for name, with_res in (("(i) 跑前定稿的流程", False), ("(ii) 加上殘差檢查", True)):
        runs = load_runs(with_res)
        assert len(runs) == 120, len(runs)
        a, b = stats(runs, "A"), stats(runs, "B")
        d = b["prec"] - a["prec"]
        verdict = "出貨" if d >= -0.03 else "不出貨（拆開量）"
        print(f"== {name}")
        print(f"   A：{a['valid']}/{a['n']} = {a['prec']:.1%}｜AUC 嚴格 {a['auc']:.3f}")
        print(f"   B：{b['valid']}/{b['n']} = {b['prec']:.1%}｜AUC 嚴格 {b['auc']:.3f}")
        print(f"   precision 差（B − A）{d * 100:+.1f}pp（門檻 ≥ −3.0pp）→ {verdict}")
        print(f"   置換檢定（以一次跑為單位、標的內分組，{args.n} 次）precision 雙尾 p = {perm_p(runs, d, args.n):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
