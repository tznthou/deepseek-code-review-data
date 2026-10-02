#!/usr/bin/env python3
"""rules loop 的 Guard：全部通過才 exit 0，任何一條不過 = 這一輪 discard。

完整  調參組每個 PR 都有輸出（不完整的一輪不能拿來比）
G1    功能性位置命中（調參組）≥ v00 − 2pp
G2    高信心、定位得到、卻沒對上任何標準答案的 finding（每 PR，調參組）≤ v00 × 1.15
G3    Guard target 的 sha256 跟開跑時的快照（guard-targets.sha256）一致
v00 = Qodo 既有的 base-1、base-2 在調參組上的平均。
給兩個標籤（同一個設定的兩次 run）時，G1、G2 用兩次的平均判；完整性每一次都要成立。
（v00 兩輪之間，高信心未對上/PR 就差了 0.59 vs 0.71，單一次 run 判 G2 容易被雜訊誤殺。）

用法：guard.py <標籤> [<同設定的第二個標籤>]
"""
import subprocess
import sys

sys.dont_write_bytecode = True
from common import LOOP  # noqa: E402
import loop_score  # noqa: E402

FUNC_TOL = 0.02
UNMATCHED_TOL = 1.15
SNAPSHOT = LOOP / "guard-targets.sha256"


def main() -> int:
    labels = sys.argv[1:]
    if not 1 <= len(labels) <= 2:
        sys.exit("用法：guard.py <標籤> [<同設定的第二個標籤>]")
    v0 = [loop_score.score(l, "tune") for l in loop_score.V00]
    base_func = sum(s["func_pos_hit"] for s in v0) / len(v0)
    base_unm = sum(s["hi_unmatched_per_pr"] for s in v0) / len(v0)
    runs = [loop_score.score(l, "tune") for l in labels]
    func = sum(s["func_pos_hit"] for s in runs) / len(runs)
    unm = sum(s["hi_unmatched_per_pr"] for s in runs) / len(runs)
    missing = sum(len(s["missing"]) for s in runs)
    checks = [
        ("完整：調參組每個 PR 都有輸出", not missing, f"缺 {missing} 個"),
        (f"G1 功能性位置命中 ≥ v00 − {FUNC_TOL * 100:.0f}pp", func >= base_func - FUNC_TOL,
         f"{func:.3f}，門檻 {base_func - FUNC_TOL:.3f}（{len(runs)} 次平均）"),
        (f"G2 高信心未對上/PR ≤ v00 × {UNMATCHED_TOL}", unm <= base_unm * UNMATCHED_TOL,
         f"{unm:.2f}，門檻 {base_unm * UNMATCHED_TOL:.2f}（{len(runs)} 次平均）"),
    ]
    if SNAPSHOT.exists():
        r = subprocess.run(["shasum", "-a", "256", "-c", str(SNAPSHOT)], capture_output=True, text=True)
        bad = [l for l in r.stdout.splitlines() if not l.endswith(": OK")]
        checks.append(("G3 Guard target 沒被改", r.returncode == 0, "；".join(bad) or "全部 OK"))
    else:
        checks.append(("G3 Guard target 沒被改", False, f"找不到快照 {SNAPSHOT.name}（開跑前要先建）"))
    for name, ok, detail in checks:
        print(("PASS " if ok else "FAIL ") + f"{name}：{detail}")
    return 0 if all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
