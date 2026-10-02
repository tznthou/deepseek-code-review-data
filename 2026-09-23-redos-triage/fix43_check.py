"""#43 修法候選: finditer 前先砍到最後一個 』 為止。驗兩件事: 與原版輸出逐筆相同 / 變線性。"""
import random
import re
import time

PAT = re.compile(r"『(.+?)』", re.S)  # 與 locate.py:143 同一個 regex


def old(src):
    return [m.group(1) for m in PAT.finditer(src)]


def new(src):
    head = src[: src.rfind("』") + 1]  # rfind 找不到回 -1 → 空字串 → 本來就不會有 match
    return [m.group(1) for m in PAT.finditer(head)]


# 1) 等價性: 隨機字串 (含換行, re.S 的情境) + 手寫邊界
random.seed(20260923)
alpha = ["『", "』", "a", "\n", " ", "`"]
n_cases = 300_000
for _ in range(n_cases):
    s = "".join(random.choice(alpha) for _ in range(random.randint(0, 40)))
    assert old(s) == new(s), repr(s)
edge = ["", "『", "』", "『』", "『』』", "『a』", "』『a", "『a『b』", "『』x』", "『\n』", "a『bc』d『e"]
for s in edge:
    assert old(s) == new(s), repr(s)
print(f"等價: 隨機 {n_cases:,} 筆 + 邊界 {len(edge)} 筆 全部相同")

# 2) 時間: 原版平方的形狀, 以及刻意讓 』 只出現在前段的形狀
shapes = {
    "『a*k (無結尾)": lambda k: "『" + "『a" * k,
    "』 + 『a*k (結尾在最前)": lambda k: "』" + "『a" * k,
    "『a*k + 』 + 『a*k": lambda k: "『a" * k + "』" + "『a" * k,
}
for name, mk in shapes.items():
    row = []
    for n in (16_000, 64_000, 128_000):
        s = mk(n // 2)
        t = time.perf_counter(); new(s); dt_new = time.perf_counter() - t
        row.append(f"{n//1000}K={dt_new*1000:.2f}ms")
    print(f"new  {name:<24} " + "  ".join(row))
# 對照: 原版在同一形狀 (只跑小的, 大的前面量過)
s = "』" + "『a" * 32_000
t = time.perf_counter(); old(s); print(f"old  』 + 『a*k (64K)          {time.perf_counter()-t:.2f}s  ← 只查「有沒有 』」擋不住這個")
