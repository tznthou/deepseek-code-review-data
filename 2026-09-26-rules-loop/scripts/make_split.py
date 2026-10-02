#!/usr/bin/env python3
"""每個 repo 各自 70/30 切成調參組與 holdout，seed 固定。

split.json 已存在就不覆寫：切分一旦定了就不動，否則 holdout 會被看過。
"""
import collections
import json
import random
import sys

sys.dont_write_bytecode = True
from common import QODO, SPLIT, pr_repo  # noqa: E402

SEED = 20260926
HOLDOUT_SHARE = 0.3


def main() -> None:
    if SPLIT.exists():
        sys.exit(f"[stop] {SPLIT} 已存在，不覆寫")
    evalset = json.loads((QODO / "evalset.json").read_text(encoding="utf-8"))
    by_repo = collections.defaultdict(list)
    for pr in sorted({e["pr"] for e in evalset}):
        by_repo[pr_repo(pr)].append(pr)

    rng = random.Random(SEED)
    tune, holdout = [], []
    for repo in sorted(by_repo):
        prs = sorted(by_repo[repo], key=lambda k: int(k.rsplit("-", 1)[1]))
        rng.shuffle(prs)
        k = round(len(prs) * HOLDOUT_SHARE)
        holdout += prs[:k]
        tune += prs[k:]

    def items(prs: list[str]) -> dict:
        s = set(prs)
        c = collections.Counter(e["kind"] for e in evalset if e["pr"] in s)
        return {"prs": len(prs), "rule": c["rule"], "func": c["func"]}

    out = {"seed": SEED, "method": f"每個 repo 各自抽 {HOLDOUT_SHARE:.0%} 當 holdout（random.Random(seed)，repo 依名稱排序）",
           "counts": {"tune": items(tune), "holdout": items(holdout)},
           "tune": sorted(tune), "holdout": sorted(holdout)}
    SPLIT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
