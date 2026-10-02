#!/usr/bin/env python3
"""把對錯標記跟信心值 join 起來，照 PREREG.md 算鑑別力並下判定。

S、R 分開算、不合併；「有爭議」分嚴格版（算不成立）與寬鬆版（算成立）各報一次。
數字全部由這支腳本算出，RESULTS 不手抄。
"""
import json
import pathlib
import random
import statistics
from fractions import Fraction

OUT = pathlib.Path(__file__).resolve().parents[1]
GATE = 0.7  # post_review.py:210 的預設 min-confidence
BOOT = 2000
SEED = 20260924
# 判定門檻用分數比，不用浮點：第一次跑時 gap 應為 1 - 8/10 = 0.20，浮點算成
# 0.19999…，剛好卡在「≥ 0.20」的門檻上被判錯邊。
AUC_YES, AUC_NO = Fraction(7, 10), Fraction(6, 10)
GAP_YES, GAP_NO = Fraction(1, 5), Fraction(1, 10)


def read_labels(name: str) -> dict[str, str]:
    lines = (OUT / name).read_text(encoding="utf-8").splitlines()[1:]
    return {ln.split(",", 3)[0]: ln.split(",", 3)[1] for ln in lines if ln.strip()}


def auc(pos: list[float], neg: list[float]) -> Fraction:
    wins = sum(
        Fraction(1) if p > n else Fraction(1, 2) if p == n else Fraction(0)
        for p in pos
        for n in neg
    )
    return wins / (len(pos) * len(neg))


def pass_rate(xs: list[float]) -> Fraction:
    return Fraction(sum(x >= GATE for x in xs), len(xs))


def boot_ci(pos: list[float], neg: list[float]) -> tuple[float, float]:
    rng = random.Random(SEED)
    vals = sorted(
        auc([rng.choice(pos) for _ in pos], [rng.choice(neg) for _ in neg]) for _ in range(BOOT)
    )
    return vals[int(0.05 * BOOT)], vals[int(0.95 * BOOT) - 1]


def verdict(n_pos: int, n_neg: int, a: Fraction, gap: Fraction) -> str:
    if min(n_pos, n_neg) < 5:
        return "只描述（有一類不到 5 筆）"
    if a >= AUC_YES and gap >= GAP_YES:
        return "有鑑別力"
    if a <= AUC_NO or gap <= GAP_NO:
        return "沒有鑑別力"
    return "弱／無法判定"


def report(title: str, conf: dict[str, float], labels: dict[str, str], lines: list[str]) -> dict:
    out = {}
    lines += [f"## {title}", ""]
    for mode in ("嚴格", "寬鬆"):
        ok = {"valid"} | ({"disputed"} if mode == "寬鬆" else set())
        pos = sorted(conf[i] for i, lb in labels.items() if lb in ok)
        neg = sorted(conf[i] for i, lb in labels.items() if lb not in ok)
        a = auc(pos, neg)
        lo, hi = boot_ci(pos, neg)
        gap = pass_rate(pos) - pass_rate(neg)
        v = verdict(len(pos), len(neg), a, gap)
        out[mode] = v
        lines += [
            f"### {mode}版（有爭議算{'成立' if mode == '寬鬆' else '不成立'}）",
            "",
            f"- 成立 n={len(pos)}，中位數 {statistics.median(pos):.2f}：{pos}",
            f"- 不成立 n={len(neg)}，中位數 {statistics.median(neg):.2f}：{neg}",
            f"- 0.7 門檻放行率：成立 {float(pass_rate(pos)):.0%}、不成立 {float(pass_rate(neg)):.0%}，"
            f"gap = {float(gap):+.2f}（精確值 {gap}）",
            f"- AUC = {float(a):.2f}（bootstrap 90% CI {float(lo):.2f}–{float(hi):.2f}）",
            f"- **判定：{v}**",
            "",
        ]
    if out["嚴格"] != out["寬鬆"]:
        lines += ["⚠️ 兩版判定不一致 → 結論取決於有爭議那幾筆怎麼算", ""]
    return out


def main() -> None:
    key_s = json.loads((OUT / "key-S.json").read_text(encoding="utf-8"))
    conf_s = {k: v["confidence"] for k, v in key_s.items()}
    labels_s = read_labels("labels-S.csv")
    real = json.loads((OUT / "real-findings.json").read_text(encoding="utf-8"))
    conf_r = {r["id"]: r["confidence"] for r in real}
    labels_r = read_labels("labels-R.csv")

    assert set(conf_s) == set(labels_s), "S 的標記與信心值 id 對不上"
    assert set(conf_r) == set(labels_r), "R 的標記與信心值 id 對不上"

    lines = ["# baseline 結果（scripts/analyze.py 產生，不要手改）", ""]
    report("S：埋點標的（v4-pro，7 次跑）", conf_s, labels_s, lines)
    report("R：真實 PR（v4-pro，kit 自己的 PR）", conf_r, labels_r, lines)

    lines += ["## S 分標的（只描述，不判定）", ""]
    for tgt, prefix in (("python", ("py-",)), ("shell", ("sh-",))):
        ids = [i for i, v in key_s.items() if v["source"].startswith(prefix)]
        for lb in ("valid", "disputed", "invalid"):
            xs = sorted(conf_s[i] for i in ids if labels_s[i] == lb)
            lines.append(f"- {tgt} {lb} n={len(xs)}：{xs}")
    lines.append("")
    text = "\n".join(lines)
    (OUT / "RESULTS-baseline.md").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
