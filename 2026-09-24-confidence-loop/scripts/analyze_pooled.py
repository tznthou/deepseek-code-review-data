#!/usr/bin/env python3
"""stuck 之後的重跑比較：把同一份 rubric 的兩輪合併，再比 A 組與 B 組。

判定規則在重跑之前寫進 .autoresearch-confidence.md（2026-09-24 追加）：
合併後 AUC(B) − AUC(A) ≥ 0.05，而且 anti-criteria a–e 在合併資料上全過 → B 成為 keep 候選。
AUC 是在合併後的全部 finding 上重算，不是兩輪平均。

用法：analyze_pooled.py --a v00,v04 --b v02,v05
"""
import argparse
import json
import pathlib
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analyze_round as ar  # noqa: E402

LOOP = pathlib.Path(__file__).resolve().parents[1]


def pooled(labels_: list[str]) -> dict:
    rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
    kinds = {it["id"]: it["kind"] for it in rules["items"]}
    rows, runs_total, runs_ok, per_t = [], 0, 0, {}
    for lab in labels_:
        rdir = LOOP / "rounds" / lab
        man = json.loads((rdir / "manifest.json").read_text(encoding="utf-8"))
        key = json.loads((rdir / "key.json").read_text(encoding="utf-8"))
        labels = {r["id"]: r for r in ar.read_csv(rdir / "labels-auto.csv")}
        labels.update({r["id"]: r for r in ar.read_csv(rdir / "labels-manual.csv")})
        missing = set(key) - set(labels)
        if missing:
            raise SystemExit(f"{lab} 還有 {len(missing)} 筆沒標")
        runs_total += len(man["results"])
        for r in man["results"]:
            ok = r["exit"] == 0 and r["findings"] is not None
            runs_ok += ok
            t = per_t.setdefault(r["target"], {"runs_ok": 0, "a_recall": 0})
            t["runs_ok"] += ok
        for target, spec in rules["targets"].items():
            src = ar.source_lines(LOOP / spec["diff"])
            for path in sorted(rdir.glob(f"{target}-*.json")):
                run = int(path.stem.rsplit("-", 1)[1])
                try:
                    items = json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                hit_a = set()
                for k, f in enumerate(items, 1):
                    fid = f"{lab}:{target}:{run}:{k}"
                    lb = labels[fid]
                    code = [ln.strip() for ln in str(f.get("existing_code", "")).splitlines() if ln.strip()]
                    rows.append({"target": target, "conf": key[fid]["confidence"], "label": lb["label"],
                                 "ev_ok": bool(f.get("evidence")) and bool(code) and code[0] in src})
                    if lb["label"] == "valid" and kinds.get(lb.get("item", "")) == "A":
                        hit_a.add(lb["item"])
                per_t[target]["a_recall"] += len(hit_a)

    m = {"rounds": labels_, "runs_total": runs_total, "runs_ok": runs_ok, "findings": len(rows)}
    for mode, ok in (("strict", {"valid"}), ("lenient", {"valid", "disputed"})):
        pos = [r["conf"] for r in rows if r["label"] in ok]
        neg = [r["conf"] for r in rows if r["label"] not in ok]
        a = ar.auc(pos, neg)
        m[f"auc_{mode}"], m[f"auc_{mode}_exact"] = float(a), str(a)
        m[f"ci_{mode}"] = ar.boot(pos, neg)
        m[f"n_{mode}"] = (len(pos), len(neg))
        if mode == "strict":
            m["gate"] = (sum(x >= ar.GATE for x in pos) / len(pos), sum(x >= ar.GATE for x in neg) / len(neg))
    for t in per_t:
        pos = [r["conf"] for r in rows if r["target"] == t and r["label"] == "valid"]
        neg = [r["conf"] for r in rows if r["target"] == t and r["label"] != "valid"]
        a = ar.auc(pos, neg)
        per_t[t].update({"auc_strict": None if a is None else float(a), "n": (len(pos), len(neg))})
    m["per_target"] = per_t
    m["evidence_rate"] = sum(r["ev_ok"] for r in rows) / len(rows)
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    # 2026-10-01 追加（prompt-hygiene 實驗）：量「不劣化」時門檻是 −1/20。不給就是原本的 keep 門檻 +1/20
    ap.add_argument("--min-delta", default="1/20")
    args = ap.parse_args()
    min_delta = Fraction(args.min_delta)
    A, B = pooled(args.a.split(",")), pooled(args.b.split(","))
    for name, m in (("A", A), ("B", B)):
        print(f"== {name} {'+'.join(m['rounds'])}：runs {m['runs_ok']}/{m['runs_total']}，findings {m['findings']}")
        print(f"   AUC 嚴格 {m['auc_strict']:.3f}（CI {m['ci_strict']}，成立/不成立 {m['n_strict']}）"
              f"｜寬鬆 {m['auc_lenient']:.3f}（CI {m['ci_lenient']}）")
        print(f"   0.7 門檻放行：成立 {m['gate'][0]:.0%}、不成立 {m['gate'][1]:.0%}｜evidence {m['evidence_rate']:.0%}")
        for t, pt in m["per_target"].items():
            a = "—" if pt["auc_strict"] is None else f"{pt['auc_strict']:.3f}"
            print(f"   {t:6} AUC {a}（成立/不成立 {pt['n']}）A 類召回 {pt['a_recall']}／{pt['runs_ok']} 次成功跑")

    def per5(pt: dict) -> float:
        return pt["a_recall"] * 5 / pt["runs_ok"] if pt["runs_ok"] else 0.0

    a_fail, b_fail = A["runs_total"] - A["runs_ok"], B["runs_total"] - B["runs_ok"]
    anti = {"a_runs_ok": b_fail <= max(1, a_fail),
            "b_findings_not_halved": B["findings"] >= 0.5 * A["findings"],
            "c_evidence_rate": B["evidence_rate"] >= A["evidence_rate"] - 0.10}
    for t in B["per_target"]:
        anti[f"d_recall_{t}"] = per5(B["per_target"][t]) >= per5(A["per_target"][t]) - 1
    pa, pb = A["per_target"]["probe"]["auc_strict"], B["per_target"]["probe"]["auc_strict"]
    anti["e_probe_auc_not_worse"] = pa is None or (pb is not None and pb >= pa - 0.05)
    delta = Fraction(B["auc_strict_exact"]) - Fraction(A["auc_strict_exact"])
    print("\nanti-criteria：" + "、".join(f"{k}={'✓' if v else '✗'}" for k, v in anti.items()))
    print(f"合併 AUC 差（B − A）：{float(delta):+.3f}（需 ≥ {float(min_delta):+.2f}）")
    ok = delta >= min_delta and all(anti.values())
    print(f"判定：{'B 通過' if ok else '維持 A（baseline）'}")


if __name__ == "__main__":
    main()
