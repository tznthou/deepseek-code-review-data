#!/usr/bin/env python3
"""量實際花費：跑之前存一次餘額，跑完只印差額（餘額本身不印）。

用法：balance.py save <檔案>｜balance.py diff <檔案>
key 沿用 run_bench.api_key()（keychain、送出前驗形狀、不印）。
"""
import json
import pathlib
import sys
import urllib.request

sys.dont_write_bytecode = True
sys.path.insert(0, "<repo>/.claude/experiments/2026-09-25-qodo-bench/scripts")
import run_bench  # noqa: E402


def balances() -> dict[str, float]:
    req = urllib.request.Request("https://api.deepseek.com/user/balance",
                                 headers={"Authorization": f"Bearer {run_bench.api_key()}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return {b["currency"]: float(b["total_balance"]) for b in data.get("balance_infos", [])}


def main() -> None:
    mode, path = sys.argv[1], pathlib.Path(sys.argv[2])
    now = balances()
    if mode == "save":
        path.write_text(json.dumps(now), encoding="utf-8")
        print(f"已存（幣別：{', '.join(now)}）")
    else:
        before = json.loads(path.read_text(encoding="utf-8"))
        for cur, amount in now.items():
            print(f"{cur} 花費 {before.get(cur, amount) - amount:.4f}")


if __name__ == "__main__":
    main()
