#!/usr/bin/env python3
"""量 4 筆 CodeQL py/polynomial-redos alert。

*_real 走 repo 裡真正的函式（不重寫 regex）；*_bare 是對照組，直接跑同一個
regex 但拿掉保護它的上下文，用來驗「為什麼安全」的推論，而不只是看結果。

用法: python3 redos_bench.py                # 全跑，印表 + 寫 JSON
      python3 redos_bench.py --one CASE N   # （內部）子行程跑單一量測
"""
import json
import os
import platform
import re
import subprocess
import sys
import time

REPO = "<repo>"
SCRIPTS = os.path.join(REPO, ".github", "scripts")
RULES = os.path.join(REPO, "prompts", "rules")
TIMEOUT = 120

LINEAR_SIZES = [1_000_000, 2_000_000, 4_000_000, 8_000_000, 16_000_000]
QUAD_SIZES = [4_000, 8_000, 16_000, 32_000, 64_000, 128_000]

# name -> (sizes, 預期)
CASES = {
    "41_real": (LINEAR_SIZES, "linear"),
    "41_real_crlf": (LINEAR_SIZES, "linear"),
    "41_bare_noM": (QUAD_SIZES, "quadratic"),
    "42_real": (LINEAR_SIZES, "linear"),
    "44_real": (LINEAR_SIZES, "linear"),
    "42_bare_multiline": (QUAD_SIZES, "quadratic"),
    "43_real": (QUAD_SIZES, "quadratic"),
    "43_closed": (QUAD_SIZES, "linear"),
}


def rep(unit: str, n: int) -> str:
    return unit * max(1, n // len(unit))


def build(case: str, n: int):
    """回傳 (輸入字串, 要計時的函式, 結果合理性檢查)。檢查失敗 = 沒走到該走的路徑。"""
    sys.path.insert(0, SCRIPTS)
    import deepseek_review  # noqa: E402
    import locate  # noqa: E402
    import post_review  # noqa: E402

    if case in ("41_real", "41_real_crlf"):
        unit = "a b/a\r" if case.endswith("crlf") else "a b/a"
        # 第二行讓 python.md 被挑中：證明 findall 掃完整份、第二段迴圈也跑了
        s = "diff --git a/a b/" + rep(unit, n) + "\ndiff --git a/x.py b/x.py\n"
        return s, (lambda: deepseek_review.select_rules(s, RULES)), (lambda r: r[1] == ["python.md"])
    if case == "41_bare_noM":
        s = "diff --git a/a b/" + rep("a b/a", n) + "\nX"
        return s, (lambda: re.findall(r"^diff --git a/.+ b/(.+)$", s)), (lambda r: r == [])
    if case in ("42_real", "44_real"):
        # hunk 讓 key 底下有一行：證明 header regex 的結果真的被拿去用
        s = "diff --git " + " b/" + rep(" b/a", n) + "\n@@ -0,0 +1 @@\n+x\n"
        if case == "42_real":
            return s, (lambda: locate.index_diff(s)), (
                lambda r: len(r) == 1 and len(next(iter(r))) >= n * 0.9 and next(iter(r.values())) == {1: "x"}
            )
        return s, (lambda: post_review.parse_valid_lines(s)), (
            lambda r: len(r) == 1 and len(next(iter(r))) >= n * 0.9 and next(iter(r.values())) == {1}
        )
    if case == "42_bare_multiline":
        s = " b/" + rep(" b/a", n) + "\nX"
        return s, (lambda: locate._GIT_HEADER.search(s)), (lambda r: r is None)
    if case == "43_real":
        s = "『" + rep("『a", n)
        return s, (lambda: locate.extract_snippets(s)), (lambda r: r == [])
    if case == "43_closed":
        s = "『" + rep("『a", n) + "』"
        return s, (lambda: locate.extract_snippets(s)), (lambda r: len(r) == 1 and len(r[0]) >= n * 0.9)
    raise SystemExit(f"unknown case {case}")


def one(case: str, n: int) -> None:
    s, fn, check = build(case, n)
    t0 = time.perf_counter()
    r = fn()
    best = time.perf_counter() - t0
    ok = bool(check(r))
    if best < 1.0:  # 短的多跑兩次取最小值，壓掉雜訊
        for _ in range(2):
            t0 = time.perf_counter()
            fn()
            best = min(best, time.perf_counter() - t0)
    print(json.dumps({"case": case, "n": n, "len": len(s), "secs": best, "sanity": ok}))


def classify(rows):
    ratios = [
        rows[i]["secs"] / rows[i - 1]["secs"]
        for i in range(1, len(rows))
        if rows[i - 1]["secs"] > 0.002 and rows[i]["secs"] is not None  # 太短的比值是雜訊
    ]
    tail = ratios[-3:]
    if not tail:
        return "too-fast", ratios
    med = sorted(tail)[len(tail) // 2]
    return ("linear" if med < 2.8 else "quadratic" if med > 3.2 else "unclear"), ratios


def main() -> None:
    results = {}
    for case, (sizes, expected) in CASES.items():
        rows = []
        for n in sizes:
            try:
                p = subprocess.run(
                    [sys.executable, __file__, "--one", case, str(n)],
                    capture_output=True, text=True, timeout=TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                rows.append({"case": case, "n": n, "secs": None, "timeout": True})
                break
            if p.returncode != 0:
                rows.append({"case": case, "n": n, "secs": None, "error": p.stderr.strip()[-400:]})
                break
            rows.append(json.loads(p.stdout))
        timed = [r for r in rows if r.get("secs") is not None]
        verdict, ratios = classify(timed)
        results[case] = {"expected": expected, "observed": verdict, "ratios": ratios, "rows": rows}
        print(f"\n== {case}  預期={expected}  觀測={verdict}  比值={[round(x, 2) for x in ratios]}")
        for r in rows:
            if r.get("secs") is None:
                print(f"   n={r['n']:>10,}  {'TIMEOUT >%ds' % TIMEOUT if r.get('timeout') else 'ERROR ' + r.get('error', '')}")
            else:
                print(f"   n={r['n']:>10,}  len={r['len']:>10,}  {r['secs']:>9.4f} s  sanity={'OK' if r['sanity'] else 'FAIL'}")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "redos-results.json")
    meta = {"python": sys.version, "machine": platform.machine(), "platform": platform.platform()}
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "results": results}, fh, ensure_ascii=False, indent=2)
    print(f"\n{meta}\n寫入 {out}")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--one":
        one(sys.argv[2], int(sys.argv[3]))
    else:
        main()
