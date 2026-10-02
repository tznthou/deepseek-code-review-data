#!/usr/bin/env python3
"""【事後探索，不在跑前寫定的判準內】各輪 finding 的定位結果分布：定位不到的筆數、定位方式的分布。$0。

起因：verdict 的 L（位置命中）fc 臂比基準低 12–24，S（盲標 same）卻是 fc-1 +4；附記只印了 fc 臂「定位不到」
（fc-1 38、fc-2 39），沒有基準臂的對照。這裡補印五輪同一項，看 L 的落差有沒有一部分是定位失敗造成的量測落差。
"""
import collections
import pathlib
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import score_ctx  # noqa: E402

print(f"{'輪':<7}{'finding':>8}{'定位不到':>9}{'比例':>7}  定位方式分布")
for r in score_ctx.ROUNDS:
    _, _, fs = score_ctx.load(r)
    unloc = sum(f["line"] is None for f in fs)
    how = collections.Counter(f["how"] for f in fs)
    print(f"{r:<7}{len(fs):>8}{unloc:>9}{unloc / len(fs):>7.1%}  {dict(how)}")
