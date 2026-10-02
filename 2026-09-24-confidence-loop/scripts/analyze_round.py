#!/usr/bin/env python3
"""算一輪的 metric 與 anti-criteria（定義見 .autoresearch-confidence.md，跑前定稿）。

主 metric：三個標的合併的 AUC（嚴格版：有爭議算不成立）。
anti-criteria 對照 baseline（v00）與目前最佳（--best）。數字只由這支產生。

用法：analyze_round.py <輪次標籤> [--baseline v00] [--best <標籤>]
"""
import argparse
import csv
import json
import pathlib
import random
from fractions import Fraction

LOOP = pathlib.Path(__file__).resolve().parents[1]
GATE = 0.7
KEEP_DELTA = Fraction(5, 100)
TARGET_AUC = Fraction(9, 10)


def auc(pos: list[float], neg: list[float]):
    if not pos or not neg:
        return None
    wins = sum(Fraction(1) if p > n else Fraction(1, 2) if p == n else Fraction(0) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def boot(pos, neg, n=2000, seed=20260924):
    if not pos or not neg:
        return None
    rng = random.Random(seed)
    vals = sorted(float(auc([rng.choice(pos) for _ in pos], [rng.choice(neg) for _ in neg])) for _ in range(n))
    return round(vals[int(0.05 * n)], 3), round(vals[int(0.95 * n) - 1], 3)


def source_lines(diff: pathlib.Path) -> set[str]:
    lines, in_hunk = set(), False
    for raw in diff.read_text(encoding="utf-8").splitlines():
        if raw.startswith("@@"):
            in_hunk = True
        elif in_hunk and raw.startswith("+"):
            lines.add(raw[1:].strip())
    return lines


def read_csv(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def metrics(label: str) -> dict:
    rdir = LOOP / "rounds" / label
    rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
    kinds = {it["id"]: it["kind"] for it in rules["items"]}
    manifest = json.loads((rdir / "manifest.json").read_text(encoding="utf-8"))
    key = json.loads((rdir / "key.json").read_text(encoding="utf-8"))
    labels = {r["id"]: r for r in read_csv(rdir / "labels-auto.csv")}
    labels.update({r["id"]: r for r in read_csv(rdir / "labels-manual.csv")})
    missing = sorted(set(key) - set(labels))
    if missing:
        raise SystemExit(f"{len(missing)} 筆還沒標：{missing[:5]}…")

    findings = {}
    for target in rules["targets"]:
        for path in sorted(rdir.glob(f"{target}-*.json")):
            run = int(path.stem.rsplit("-", 1)[1])
            try:
                items = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for k, f in enumerate(items, 1):
                findings[f"{label}:{target}:{run}:{k}"] = {**f, "target": target, "run": run}

    m = {"label": label, "runs_total": len(manifest["results"]),
         "runs_ok": sum(r["exit"] == 0 and r["findings"] is not None for r in manifest["results"]),
         "findings": len(key), "per_target": {}}
    for mode, ok in (("strict", {"valid"}), ("lenient", {"valid", "disputed"})):
        pos = [key[i]["confidence"] for i in key if labels[i]["label"] in ok]
        neg = [key[i]["confidence"] for i in key if labels[i]["label"] not in ok]
        a = auc(pos, neg)
        m[f"auc_{mode}"] = None if a is None else float(a)
        m[f"auc_{mode}_exact"] = None if a is None else str(a)
        m[f"ci_{mode}"] = boot(pos, neg)
        m[f"n_pos_{mode}"], m[f"n_neg_{mode}"] = len(pos), len(neg)
        if mode == "strict":
            pr = lambda xs: sum(x >= GATE for x in xs) / len(xs) if xs else None  # noqa: E731
            m["gate_pass_valid"], m["gate_pass_invalid"] = pr(pos), pr(neg)

    ev_ok = 0
    for target, spec in rules["targets"].items():
        src = source_lines(LOOP / spec["diff"])
        ids = [i for i in key if findings[i]["target"] == target]
        pos = [key[i]["confidence"] for i in ids if labels[i]["label"] == "valid"]
        neg = [key[i]["confidence"] for i in ids if labels[i]["label"] != "valid"]
        a = auc(pos, neg)
        recall = 0
        for run in range(1, manifest["runs"] + 1):
            recall += len({labels[i]["item"] for i in ids
                           if findings[i]["run"] == run and labels[i]["label"] == "valid"
                           and kinds.get(labels[i].get("item", "")) == "A"})
        for i in ids:
            code = [ln.strip() for ln in str(findings[i].get("existing_code", "")).splitlines() if ln.strip()]
            if findings[i].get("evidence") and code and code[0] in src:
                ev_ok += 1
        runs_ok_t = sum(r["target"] == target and r["exit"] == 0 and r["findings"] is not None
                        for r in manifest["results"])
        m["per_target"][target] = {"findings": len(ids), "valid": len(pos), "not_valid": len(neg),
                                   "auc_strict": None if a is None else float(a), "a_recall": recall,
                                   "runs_ok": runs_ok_t}
    m["evidence_rate"] = ev_ok / len(key) if key else None
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--baseline", default="v00")
    ap.add_argument("--best", default=None)
    args = ap.parse_args()

    m = metrics(args.label)
    (LOOP / "rounds" / args.label / "metrics.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"== {args.label}：findings {m['findings']}，runs {m['runs_ok']}/{m['runs_total']}")
    print(f"AUC 嚴格 {m['auc_strict']:.3f}（CI {m['ci_strict']}，成立 {m['n_pos_strict']} / 不成立 {m['n_neg_strict']}）"
          if m["auc_strict"] is not None else "AUC 嚴格：無法計算（有一類是 0 筆）")
    if m["auc_lenient"] is not None:
        print(f"AUC 寬鬆 {m['auc_lenient']:.3f}（CI {m['ci_lenient']}）")
    if m["gate_pass_valid"] is not None and m["gate_pass_invalid"] is not None:
        print(f"0.7 門檻放行：成立 {m['gate_pass_valid']:.0%}、不成立 {m['gate_pass_invalid']:.0%}")
    for t, pt in m["per_target"].items():
        a = "—" if pt["auc_strict"] is None else f"{pt['auc_strict']:.3f}"
        print(f"  {t:6} findings {pt['findings']:3}  成立 {pt['valid']:3}  不成立 {pt['not_valid']:3}  AUC {a}  A 類召回 {pt['a_recall']}")
    print(f"evidence 引用率 {m['evidence_rate']:.0%}")

    if args.label == args.baseline:
        hit = m["auc_strict"] is not None and Fraction(m["auc_strict_exact"]) >= TARGET_AUC
        print(f"\nbaseline 達標（AUC ≥ 0.90）？{'是 → 不開 loop' if hit else '否 → 開 loop'}")
        return

    base = json.loads((LOOP / "rounds" / args.baseline / "metrics.json").read_text(encoding="utf-8"))
    best = json.loads((LOOP / "rounds" / (args.best or args.baseline) / "metrics.json").read_text(encoding="utf-8"))
    # 2026-09-24 追加（v00 之後、v01 之前）：baseline 自己就有 1 次輸出被截斷（14/15），
    # 所以 a 容許的失敗數 = max(1, baseline 的失敗數)；d 的召回換算成每 5 次成功跑再比。
    base_fail = base["runs_total"] - base["runs_ok"]
    anti = {
        "a_runs_ok": m["runs_total"] - m["runs_ok"] <= max(1, base_fail),
        "b_findings_not_halved": m["findings"] >= 0.5 * base["findings"],
        "c_evidence_rate": m["evidence_rate"] >= base["evidence_rate"] - 0.10,
    }

    def per5(pt: dict) -> float:
        return pt["a_recall"] * 5 / pt["runs_ok"] if pt["runs_ok"] else 0.0

    for t in m["per_target"]:
        anti[f"d_recall_{t}"] = per5(m["per_target"][t]) >= per5(base["per_target"][t]) - 1
    bp, cp = best["per_target"]["probe"]["auc_strict"], m["per_target"]["probe"]["auc_strict"]
    anti["e_probe_auc_not_worse"] = bp is None or (cp is not None and cp >= bp - 0.05)
    cur = Fraction(m["auc_strict_exact"]) if m["auc_strict_exact"] else Fraction(1)
    improved = cur >= Fraction(best["auc_strict_exact"]) + KEEP_DELTA
    print("\nanti-criteria：" + "、".join(f"{k}={'✓' if v else '✗'}" for k, v in anti.items()))
    print(f"主 metric：{float(cur):.3f} vs 最佳 {best['label']} {best['auc_strict']:.3f}（需 +0.05）→ "
          f"{'進步' if improved else '沒進步'}")
    verdict = "keep" if improved and all(anti.values()) else "discard"
    if improved and cur - Fraction(best["auc_strict_exact"]) >= Fraction(1, 10):
        verdict += "（⚠️ 單輪 +0.10 以上：爆衝觸發，先請子超盲抽 10 筆標記再定）"
    print(f"建議：{verdict}")


if __name__ == "__main__":
    main()
