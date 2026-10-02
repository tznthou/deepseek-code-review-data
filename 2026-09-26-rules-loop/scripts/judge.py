#!/usr/bin/env python3
"""一個候選跑完之後的判定：兩次平均 M、跟目前最佳比、Guard、暴衝檢查，加上各 repo 分項當證據。

用法：judge.py <候選版本> <目前最佳版本>     例：judge.py v02 v01（v00 = Qodo 的 base-1／base-2）
δ 固定 0.020：v01 兩次 run 定的，見 .autoresearch-rules.md，定了不改。
"""
import collections
import subprocess
import sys

sys.dont_write_bytecode = True
from common import LOOP, pr_repo, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402

DELTA = 0.020
JUMP = 0.10
SHOW = (("rule_pos_hit", "規則位置"), ("func_pos_hit", "功能位置"), ("findings_per_pr", "finding/PR"),
        ("hi_unmatched_per_pr", "高信心未對上/PR"), ("cite_rate", "有標編號"))


def labels(v: str) -> list[str]:
    return list(ls.V00) if v == "v00" else [f"{v}a", f"{v}b"]


def mean(runs: list[dict], key: str) -> float:
    return sum(r[key] for r in runs) / len(runs)


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit("用法：judge.py <候選版本> <目前最佳版本>")
    v, best = sys.argv[1], sys.argv[2]
    cand = [ls.score(l, "tune") for l in labels(v)]
    base = [ls.score(l, "tune") for l in labels(best)]
    for s in base + cand:
        print(ls.line(s))
    m, mb = mean(cand, "M_cited_hit"), mean(base, "M_cited_hit")
    print(f"\n{v} 平均 M {m:.3f} vs {best} {mb:.3f}（差 {m - mb:+.3f}，keep 門檻 +{DELTA:.3f}）")
    for key, name in SHOW:
        print(f"  {name}：{mean(base, key):.3f} → {mean(cand, key):.3f}")

    g = subprocess.run([sys.executable, str(LOOP / "scripts/guard.py")] + labels(v), capture_output=True, text=True)
    print("\n" + (g.stdout.strip() or g.stderr.strip()))
    if m - mb >= JUMP:
        print(f"\n⚠️ 單輪跳升 {m - mb:+.3f} ≥ {JUMP}：先抽查引用命中是不是真的，再決定 keep")
    keep = g.returncode == 0 and m >= mb + DELTA
    print(f"\n判定：{'keep' if keep else 'discard'}（條件：平均 M ≥ {mb:.3f} + {DELTA:.3f} 且 guard 通過）")

    print(f"\n=== 各 repo 引用命中（{best} a/b → {v} a/b，分母 = 規則類 GT）===")
    by_repo = collections.defaultdict(list)
    for p in split_prs("tune"):
        by_repo[pr_repo(p)].append(p)
    for repo, prs in sorted(by_repo.items()):
        b = [ls.score(l, "tune", prs) for l in labels(best)]
        c = [ls.score(l, "tune", prs) for l in labels(v)]
        print(f"  {repo:<12} {'/'.join(str(x['cited_hit_n']) for x in b):>7} → "
              f"{'/'.join(str(x['cited_hit_n']) for x in c):<7} of {c[0]['rule_items']}")
    return 0 if keep else 1


if __name__ == "__main__":
    sys.exit(main())
