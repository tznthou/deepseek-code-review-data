#!/usr/bin/env python3
"""同位置合併的射程：過得了 kit 行內門檻的 finding 裡，有多少跟別則落在同一處。$0。

同一處 = 同 PR、同檔、行號相差 ≤3（可串接：1110、1112、1115 算一組）。
行內門檻照 post_review.py：嚴重度 ≥ minor、信心 ≥ 0.7、定位得到、行號在 diff 可留言範圍內；每 PR 最多 8 則。
兩種同位置分開算：
  - 單一 pass 自己就有的（base-1/base-2，100 PR）：合併若做成通用的，現有 kit 的行為也會跟著變
  - 跨 pass 的（D0f holdout：base-k ＋ hold-v01x 標了有效編號的）：D0f 才有的
"""
import collections
import json
import sys

sys.dont_write_bytecode = True
from common import KIT, QODO, load_rules, pr_repo, rule_ids, split_prs  # noqa: E402
import loop_score as ls  # noqa: E402

sys.path.insert(0, str(KIT / ".github/scripts"))
import post_review  # noqa: E402

MIN_CONF, MAX_INLINE, WINDOW = 0.7, 8, 3
SEV_OK = {"minor", "major", "blocker"}
IDMAPS = {repo: rule_ids(rs) for repo, rs in load_rules().items()}


def eligible(run: str, prs: list[str], cited_only: bool = False) -> list[dict]:
    out = []
    for pr in prs:
        valid = post_review.parse_valid_lines((QODO / "prs" / pr / "pr.diff").read_text(encoding="utf-8"))
        raw = json.loads((ls.rounds_dir(run) / f"{pr}.json").read_text(encoding="utf-8"))
        fs, _ = ls.load_findings(run, [pr])
        for f, r in zip(fs, raw, strict=True):
            if cited_only and not ls.cited_rules(f, IDMAPS.get(pr_repo(pr), {})):
                continue
            if r.get("severity") not in SEV_OK or f["confidence"] < MIN_CONF or f["line"] is None:
                continue
            if f["line"] not in valid.get(f["path"], set()):
                continue
            out.append({**f, "src": run})
    return out


def groups(fs: list[dict]) -> list[list[dict]]:
    by = collections.defaultdict(list)
    for f in fs:
        by[(f["pr"], f["path"])].append(f)
    out = []
    for xs in by.values():
        xs.sort(key=lambda f: f["line"])
        cur = [xs[0]]
        for f in xs[1:]:
            if f["line"] - cur[-1]["line"] <= WINDOW:
                cur.append(f)
            else:
                out.append(cur)
                cur = [f]
        out.append(cur)
    return out


def over_cap(items_per_pr: collections.Counter) -> int:
    return sum(n > MAX_INLINE for n in items_per_pr.values())


def main() -> None:
    allp = split_prs("all")
    print(f"=== 單一 pass 自己就有的同位置（v00，{len(allp)} PR）===")
    for run in ("base-1", "base-2"):
        fs = eligible(run, allp)
        gs = groups(fs)
        multi = [g for g in gs if len(g) > 1]
        per_pr = collections.Counter(f["pr"] for f in fs)
        per_pr_merged = collections.Counter(g[0]["pr"] for g in gs)
        print(f"{run}：過行內門檻 {len(fs)} 則（{len(fs) / len(allp):.2f}/PR）｜同一處 ≥2 則的組 {len(multi)}，"
              f"涵蓋 {sum(map(len, multi))} 則、{len({g[0]['pr'] for g in multi})} 個 PR｜"
              f"通用合併後行內留言 {len(fs)} → {len(gs)}｜超過 {MAX_INLINE} 則的 PR {over_cap(per_pr)} → {over_cap(per_pr_merged)}")

    hold = split_prs("holdout")
    print(f"\n=== D0f 跨 pass 的同位置（holdout {len(hold)} PR）===")
    for base, second in (("base-1", "hold-v01a"), ("base-2", "hold-v01b")):
        b, s = eligible(base, hold), eligible(second, hold, cited_only=True)
        gs = groups(b + s)
        cross = [g for g in gs if {f["src"] for f in g} == {base, second}]

        def cross_only_count(g: list[dict]) -> int:
            """只合併跨 pass：規範 finding 併進同一處的一般 finding，一般 pass 自己的幾則照舊各貼各的。"""
            gen = sum(f["src"] == base for f in g)
            return gen if 0 < gen < len(g) else len(g)

        cross_only = sum(cross_only_count(g) for g in gs)
        per_pr = collections.Counter(f["pr"] for f in b + s)
        print(f"{base}+{second}：一般 {len(b)}＋規範 {len(s)} = {len(b) + len(s)} 則｜跨 pass 同一處 {len(cross)} 組"
              f"（{', '.join(sorted(g[0]['pr'] for g in cross))}）｜行內留言：不合併 {len(b) + len(s)}、"
              f"只合併跨 pass {cross_only}、通用合併 {len(gs)}｜超過 {MAX_INLINE} 則的 PR（不合併）{over_cap(per_pr)}")


if __name__ == "__main__":
    main()
