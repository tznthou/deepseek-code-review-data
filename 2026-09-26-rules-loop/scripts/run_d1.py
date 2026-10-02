#!/usr/bin/env python3
"""D1 的 runner：就是 run_rules.py，只把 wrapper 換成 review_rules_pass.py。

run_rules.py 是凍結的 Guard target，這裡只 import：換掉模組層的 WRAPPER，main() 執行時
one() 與 manifest 的 wrapper_sha256 都讀到新的，同一個標籤換過 wrapper 照樣拒跑。
設定限定 iterations/v01.json（D1 = v01 ＋ 範圍說明，子超 2026-09-26 確認）。

用法：run_d1.py <標籤> --config iterations/v01.json --split holdout
"""
import pathlib
import sys

sys.dont_write_bytecode = True
from common import LOOP  # noqa: E402
import run_rules as rr  # noqa: E402

V01 = LOOP / "iterations/v01.json"


def config_is_v01(argv: list[str]) -> bool:
    try:
        return pathlib.Path(argv[argv.index("--config") + 1]).resolve() == V01
    except (ValueError, IndexError):
        return False


if __name__ == "__main__":
    if not config_is_v01(sys.argv):
        sys.exit(f"D1 的設定一定是 --config {V01}")
    rr.WRAPPER = LOOP / "scripts/review_rules_pass.py"
    rr.main()
