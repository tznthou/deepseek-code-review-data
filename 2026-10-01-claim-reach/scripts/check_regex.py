#!/usr/bin/env python3
"""reach.py 的 regex 先用已知答案驗過，再拿去跑真資料。"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reach import ABSENCE_RE, BROAD_RE, first_hit  # noqa: E402

SHOULD_ABSENCE = [
    "The null check is missing before dereferencing `ptr`.",
    "Variable `tmp` is unused.",
    "The return value is not checked.",
    "This error is never handled... it is never called anywhere.",
    "`foo` is undefined in this scope.",
    "The function does not validate its input.",
    "The code lacks bounds checking.",
    "There is no null check here.",
    "Calls `free` without checking the result.",
    "You forgot to close the file.",
    "The lock is not released on the error path.",
]
SHOULD_NOT = [
    "Consider renaming this variable for clarity.",
    "This loop could be simplified using a list comprehension.",
    "The `IPAddress(long)` constructor expects host byte order.",
    "Prefer `const` over `let` here.",
]
BROAD_ONLY = ["The timeout value is hardcoded to 30 seconds.", "Avoid hard-coded paths."]

fail = 0
for s in SHOULD_ABSENCE:
    if not first_hit(s, ABSENCE_RE):
        print(f"FAIL 應命中 absence：{s}")
        fail += 1
for s in SHOULD_NOT:
    if first_hit(s, BROAD_RE):
        print(f"FAIL 不應命中：{s} → {first_hit(s, BROAD_RE)}")
        fail += 1
for s in BROAD_ONLY:
    if first_hit(s, ABSENCE_RE) or not first_hit(s, BROAD_RE):
        print(f"FAIL 應只命中 broad：{s}")
        fail += 1

total = len(SHOULD_ABSENCE) + len(SHOULD_NOT) + len(BROAD_ONLY)
print(f"{total - fail}/{total} 通過")
sys.exit(1 if fail else 0)
