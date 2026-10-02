#!/usr/bin/env python3
"""全部候選在調參組的彙整：兩次平均、兩次差距、跟 v01 差幾個標準誤（σ 用各組 a/b 差距估）。$0。"""
import math
import sys

sys.dont_write_bytecode = True
import loop_score as ls  # noqa: E402

VERSIONS = ["v01", "v02", "v03", "v04", "v05", "v06"]
KEYS = ("M_cited_hit", "rule_pos_hit", "func_pos_hit", "hi_unmatched_per_pr", "findings_per_pr", "cite_rate")


def main() -> None:
    rows = {}
    for v in ["v00"] + VERSIONS:
        labels = list(ls.V00) if v == "v00" else [f"{v}a", f"{v}b"]
        runs = [ls.score(l, "tune") for l in labels]
        rows[v] = {k: sum(r[k] for r in runs) / 2 for k in KEYS}
        rows[v]["gap"] = abs(runs[0]["M_cited_hit"] - runs[1]["M_cited_hit"])
    gaps = [rows[v]["gap"] for v in VERSIONS]
    # a−b ~ N(0, 2σ²) ⇒ E|a−b| = 2σ/√π；兩個版本各取兩次平均，差的標準誤 = σ
    sigma = (sum(gaps) / len(gaps)) * math.sqrt(math.pi) / 2
    print(f"單次 run 的 σ ≈ {sigma:.4f}（由 {len(gaps)} 組 a/b 差距估）；版本間差的標準誤 ≈ {sigma:.4f}\n")
    print("| 版本 | M | 兩次差 | vs v01（標準誤） | 規則位置 | 功能位置 | 高信心未對上/PR | finding/PR | 有標編號 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for v, r in rows.items():
        z = "—" if v in ("v00", "v01") else f"{(r['M_cited_hit'] - rows['v01']['M_cited_hit']) / sigma:+.1f}"
        print(f"| {v} | {r['M_cited_hit']:.3f} | {r['gap']:.3f} | {z} | {r['rule_pos_hit']:.3f} | {r['func_pos_hit']:.3f} | "
              f"{r['hi_unmatched_per_pr']:.2f} | {r['findings_per_pr']:.2f} | {r['cite_rate']:.2f} |")


if __name__ == "__main__":
    main()
