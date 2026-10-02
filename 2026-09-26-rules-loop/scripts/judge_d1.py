#!/usr/bin/env python3
"""D1 的判決。判準在跑之前定稿（子超 2026-09-26 確認），數字寫死在這裡，跑完才讀結果。

D1 取代 D0f 的條件，兩條都要過（D1f = base-k ∪ D1 裡標了有效規則編號的 finding）：
  1. 引用命中兩次平均 ≥ 0.181（= D0f 的 0.151 ＋ 0.03）。holdout 規則類 83 則、兩次共 166 則次，
     換成整數就是兩次合計 ≥ 30 則（D0f 是 25 則）；30/166 = 0.1807，顯示成三位小數正好是 0.181
  2. 合併後高信心未對上/PR 兩次平均 ≤ 0.86（= v00 × 1.15）。31 PR × 2 = 62，換成整數是兩次合計 ≤ 53 筆
否則正式功能用 D0f（第二次呼叫 = v01 的 prompt ＋ 只留標了編號的 finding）。
用法：judge_d1.py <d0_union.py --name D1 --json 的輸出>
"""
import json
import sys

CITED_MIN_N = 30          # 兩次合計（= 平均 ≥ 0.181）
HI_UNMATCHED_MAX_N = 53   # 兩次合計（= 平均 ≤ 0.86）


def main() -> int:
    rows = json.loads(open(sys.argv[1], encoding="utf-8").read())["D1f"]
    if len(rows) != 2:
        sys.exit(f"D1f 應該有兩組配對，拿到 {len(rows)}")
    cited = sum(r["cited_hit_n"] for r in rows)
    unmatched = sum(r["hi_unmatched_n"] for r in rows)
    ok1, ok2 = cited >= CITED_MIN_N, unmatched <= HI_UNMATCHED_MAX_N
    print(f"1. 引用命中：兩次合計 {cited} 則（{' / '.join(str(r['cited_hit_n']) for r in rows)}），"
          f"平均 {cited / (2 * rows[0]['rule_items']):.3f}｜門檻 ≥ {CITED_MIN_N} 則（0.181）→ {'過' if ok1 else '沒過'}")
    print(f"2. 高信心未對上：兩次合計 {unmatched} 筆（{' / '.join(str(r['hi_unmatched_n']) for r in rows)}），"
          f"平均 {unmatched / (2 * rows[0]['prs']):.2f}/PR｜門檻 ≤ {HI_UNMATCHED_MAX_N} 筆（0.86）→ {'過' if ok2 else '沒過'}")
    print("→ D1 取代 D0f" if ok1 and ok2 else "→ D1 不取代，正式功能用 D0f")
    return 0


if __name__ == "__main__":
    sys.exit(main())
