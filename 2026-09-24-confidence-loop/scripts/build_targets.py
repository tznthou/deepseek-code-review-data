#!/usr/bin/env python3
"""產生 loop 用的三個標的 diff（新增整檔的 unified diff，格式照 09-21 的）。

- python.diff：09-21 原檔照搬
- shell-v2.diff：09-21 的 shell.diff 只改第 68 行，把 B2 的保底改成真的保證是數字
  （原本的 `|| echo 0` 在 log 存在但沒有非空白行時會產生兩行 0，見 README）
- probe.diff：新的誤報探針 sandbox/release_notes.py
"""
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
LOOP = HERE.parent
OLD = LOOP.parent / "2026-09-21-flash-3x"
TD = LOOP / "targets"

B2_OLD = '+  total=$(grep -c . "$LOG" 2>/dev/null || echo 0)'
B2_NEW = '+  total=$(grep -c . "$LOG" 2>/dev/null) || total=0'


def new_file_diff(rel: str, text: str, mode: str = "100644") -> str:
    lines = text.splitlines()
    blob = subprocess.run(
        ["git", "hash-object", "--stdin"], input=text, capture_output=True, text=True, check=True
    ).stdout.strip()[:7]
    head = [
        f"diff --git a/{rel} b/{rel}",
        f"new file mode {mode}",
        f"index 0000000..{blob}",
        "--- /dev/null",
        f"+++ b/{rel}",
        f"@@ -0,0 +1,{len(lines)} @@",
    ]
    return "\n".join(head + ["+" + ln for ln in lines]) + "\n"


def main() -> None:
    (TD / "python.diff").write_text((OLD / "python.diff").read_text(encoding="utf-8"), encoding="utf-8")

    shell = (OLD / "shell.diff").read_text(encoding="utf-8")
    assert shell.count(B2_OLD) == 1, "B2 那一行找不到或不唯一"
    (TD / "shell-v2.diff").write_text(shell.replace(B2_OLD, B2_NEW), encoding="utf-8")

    src = (TD / "src/sandbox/release_notes.py").read_text(encoding="utf-8")
    (TD / "probe.diff").write_text(new_file_diff("sandbox/release_notes.py", src), encoding="utf-8")

    for name in ("python.diff", "shell-v2.diff", "probe.diff"):
        body = (TD / name).read_text(encoding="utf-8").splitlines()
        plus = sum(1 for ln in body if ln.startswith("+") and not ln.startswith("+++"))
        print(f"{name}: {plus} 行新增")


if __name__ == "__main__":
    main()
