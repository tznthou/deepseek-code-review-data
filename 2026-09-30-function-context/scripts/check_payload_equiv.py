#!/usr/bin/env python3
"""$0 檢查：現在的 deepseek_review.py 與 09-25 基準線用的版本（c04b0d0），送出的 payload 是否逐字相同。

base-1／base-2 是 c04b0d0 跑的；之後 v1.5.0 加了規範那次呼叫、v1.6.0 改了 post。沒傳 --repo-rules 時
prompt 理論上沒變，這裡用攔截代替推論：把 chat_completion 換成「記下 payload 就丟例外」，
兩個版本各對 100 個 PR 跑一次 main()，比對 payload。不送出任何東西（key 是假值、呼叫在送出前就被攔下）。

參數照 run_bench.one（--diff --meta --rubric --out --findings-out --rules-dir）。
"""
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
EXP = pathlib.Path(__file__).resolve().parents[1]
QODO = EXP.parent / "2026-09-25-qodo-bench"
KIT = EXP.parents[2]
OLD_REV = "c04b0d0"


class Captured(Exception):
    pass


def load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def payload_of(mod, key: str, tmp: pathlib.Path) -> dict:
    box = {}

    def fake(base_url, api_key, payload, timeout, retries):
        box["payload"] = payload
        raise Captured()

    mod.chat_completion = fake
    src = QODO / "prs" / key
    sys.argv = ["deepseek_review.py", "--diff", str(src / "pr.diff"), "--meta", str(src / "meta.json"),
                "--rubric", str(KIT / "prompts/review-rubric.md"), "--out", str(tmp / "o.md"),
                "--findings-out", str(tmp / "o.json"), "--rules-dir", str(KIT / "prompts/rules")]
    rc = mod.main()
    if "payload" not in box:
        raise SystemExit(f"{key}: 沒攔到 payload（main 回 {rc}）")
    return box["payload"]


def main() -> None:
    os.environ["DEEPSEEK_API_KEY"] = "sk-fake-not-sent"
    os.environ["DEEPSEEK_MODEL"] = "deepseek-v4-pro"
    os.environ.pop("REVIEW_BLOCKED_TERMS", None)
    os.environ.pop("GITHUB_STEP_SUMMARY", None)
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        old_src = subprocess.run(["git", "-C", str(KIT), "show", f"{OLD_REV}:.github/scripts/deepseek_review.py"],
                                 capture_output=True, text=True, check=True).stdout
        (tmp / "old_review.py").write_text(old_src, encoding="utf-8")
        sys.path.insert(0, str(KIT / ".github/scripts"))  # 兩版都 import 同一份 locate（payload 組好之後才用到）
        old = load("old_review", tmp / "old_review.py")
        new = load("new_review", KIT / ".github/scripts/deepseek_review.py")
        if "--mutate" in sys.argv[1:]:  # 反向對照：範本多一個空白，應該 100 個全部「不同」
            new.USER_TEMPLATE += " "
        keys = sorted(p.name for p in (QODO / "prs").iterdir() if (p / "pr.diff").exists())
        diff = []
        for k in keys:
            a, b = payload_of(old, k, tmp), payload_of(new, k, tmp)
            if json.dumps(a, ensure_ascii=False, sort_keys=True) != json.dumps(b, ensure_ascii=False, sort_keys=True):
                diff.append(k)
        print(f"PR {len(keys)}｜payload 逐字相同 {len(keys) - len(diff)}｜不同 {len(diff)} {diff[:10]}")
        sys.exit(1 if diff or len(keys) != 100 else 0)


if __name__ == "__main__":
    main()
