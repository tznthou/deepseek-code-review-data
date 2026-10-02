#!/usr/bin/env python3
"""兩輪之間的信度：同一個 PR 跑兩次，finding 位置重疊多少。

配對：同檔、定位後行號差 ≤ 2（跟合成標的的自動 loc 分群同一套判準，數字才能比）。
定位不到的 finding（resolve_line 回 None）不參與配對，但計入分母。
每個 PR：Jaccard = 配對數 / (A + B − 配對數)；兩輪都 0 筆的 PR 跳過。

用法：reliability.py <標籤A> <標籤B>
"""
import json
import pathlib
import statistics
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "scripts"))
from score_bench import load_round  # noqa: E402


def main() -> None:
    a_lab, b_lab = sys.argv[1], sys.argv[2]
    _, _, fa = load_round(a_lab)
    _, _, fb = load_round(b_lab)
    by_a, by_b = {}, {}
    for f in fa:
        by_a.setdefault(f["pr"], []).append(f)
    for f in fb:
        by_b.setdefault(f["pr"], []).append(f)
    jac, both, only = [], 0, 0
    total_a = total_b = 0
    for pr in sorted(set(by_a) | set(by_b)):
        A, B = by_a.get(pr, []), by_b.get(pr, [])
        total_a += len(A)
        total_b += len(B)
        used = set()
        m = 0
        for x in A:
            if x["line"] is None:
                continue
            for j, y in enumerate(B):
                if j in used or y["line"] is None:
                    continue
                if x["path"] == y["path"] and abs(x["line"] - y["line"]) <= 2:
                    used.add(j)
                    m += 1
                    break
        union = len(A) + len(B) - m
        if union:
            jac.append(m / union)
        both += m
    print(f"{a_lab} vs {b_lab}：PR {len(jac)}｜finding {total_a} vs {total_b}｜兩輪都報 {both}")
    print(f"每個 PR 的 Jaccard：中位數 {statistics.median(jac):.2f}、平均 {statistics.mean(jac):.2f}、"
          f"四分位 {statistics.quantiles(jac, n=4)[0]:.2f}–{statistics.quantiles(jac, n=4)[2]:.2f}")
    print(f"整體：第一輪的 finding 有 {both / total_a:.0%} 在第二輪同位置出現")
    q = statistics.quantiles(jac, n=4)
    print(f"JSON {json.dumps({'median': round(statistics.median(jac), 2), 'mean': round(statistics.mean(jac), 2), 'q1': round(q[0], 2), 'q3': round(q[2], 2), 'overlap_a': round(both / total_a, 4)})}")


if __name__ == "__main__":
    main()
