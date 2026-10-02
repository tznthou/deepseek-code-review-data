#!/usr/bin/env python3
"""對 Qodo PR-Review-Bench 的 100 個 PR 跑一輪 review，參數照 CI。

呼叫方式與 reusable-ai-review-post.yml 那一步相同（--diff --meta --rubric --out --findings-out
--rules-dir，模型走 DEEPSEEK_MODEL），不多傳別的參數——兩個入口的參數會無聲分岔。
key 從 keychain 讀進子程序的環境，送出前先驗形狀，不印、不寫檔（沿用 confidence loop 的 run_round.py）。

可以續跑：同一個標籤下已經成功的 PR 會跳過。

用法：run_bench.py <輪次標籤> [--rubric <路徑>] [--limit N] [--workers 5]
"""
import argparse
import concurrent.futures as cf
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time

EXP = pathlib.Path(__file__).resolve().parents[1]
KIT = EXP.parents[2]
REVIEWER = KIT / ".github/scripts/deepseek_review.py"
RULES_DIR = KIT / "prompts/rules"
DEFAULT_RUBRIC = KIT / "prompts/review-rubric.md"
MODEL = "deepseek-v4-pro"
USAGE_RE = re.compile(r"usage=(\{.*\})")


def api_key() -> str:
    try:
        key = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", "deepseek-api-key"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit("keychain 裡沒有 deepseek-api-key")
    # 形狀不對就不送（避免把存錯的值當成 key 送出去），錯誤訊息不帶值本身。
    if not re.fullmatch(r"sk-[A-Za-z0-9]{20,}", key):
        sys.exit(f"keychain 裡的 deepseek-api-key 不像 DeepSeek key（長度 {len(key)}、"
                 f"sk- 開頭：{key.startswith('sk-')}），不送出")
    return key


def pr_keys() -> list[str]:
    rows = [json.loads(l) for l in (EXP / "data/bench.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    keys = []
    for r in rows:
        parts = r["pr_url_to_review"].rstrip("/").split("/")
        keys.append(f"{parts[-3]}-{parts[-1]}")
    return keys


def one(out: pathlib.Path, rubric: pathlib.Path, key: str, env: dict) -> dict:
    src = EXP / "prs" / key
    stem = out / key
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(REVIEWER), "--diff", str(src / "pr.diff"), "--meta", str(src / "meta.json"),
         "--rubric", str(rubric), "--out", f"{stem}.md", "--findings-out", f"{stem}.json",
         "--rules-dir", str(RULES_DIR)],
        env=env, capture_output=True, text=True,
    )
    stem.with_suffix(".log").write_text(proc.stderr, encoding="utf-8")
    usage = {}
    m = USAGE_RE.search(proc.stderr)
    if m:
        try:
            usage = json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    n = None
    if proc.returncode == 0:
        try:
            n = len(json.loads(pathlib.Path(f"{stem}.json").read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            n = None
    return {"pr": key, "exit": proc.returncode, "findings": n, "seconds": round(time.time() - t0, 1),
            "prompt_tokens": usage.get("prompt_tokens"), "cache_hit": usage.get("prompt_cache_hit_tokens"),
            "completion_tokens": usage.get("completion_tokens")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--rubric", default=str(DEFAULT_RUBRIC))
    ap.add_argument("--limit", type=int, default=None, help="只跑前 N 個（試跑用）")
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()

    rubric = pathlib.Path(args.rubric).resolve()
    out = EXP / "rounds" / args.label
    out.mkdir(parents=True, exist_ok=True)
    man_path = out / "manifest.json"
    manifest = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else {
        "label": args.label, "rubric": str(rubric),
        "rubric_sha256": hashlib.sha256(rubric.read_bytes()).hexdigest(),
        "kit_head": subprocess.run(["git", "-C", str(KIT), "rev-parse", "HEAD"], capture_output=True,
                                   text=True).stdout.strip(),
        "dataset_revision": (EXP / "data/revision.txt").read_text().strip(),
        "model": MODEL, "results": {}}
    if manifest["rubric_sha256"] != hashlib.sha256(rubric.read_bytes()).hexdigest():
        sys.exit("這個標籤之前用的是另一份 rubric，不混在同一輪（換一個標籤）")

    keys = pr_keys()[: args.limit] if args.limit else pr_keys()
    todo = [k for k in keys if manifest["results"].get(k, {}).get("exit") != 0]
    print(f"[{datetime.datetime.now(datetime.UTC):%H:%M:%S} UTC] {args.label}：共 {len(keys)}，要跑 {len(todo)}")
    if not todo:
        return

    env = {**os.environ, "DEEPSEEK_API_KEY": api_key(), "DEEPSEEK_MODEL": MODEL}
    env.pop("REVIEW_BLOCKED_TERMS", None)
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(lambda k: one(out, rubric, k, env), todo):
            manifest["results"][r["pr"]] = r
            man_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    res = [manifest["results"][k] for k in keys if k in manifest["results"]]
    ok = sum(r["exit"] == 0 for r in res)
    tin = sum(r["prompt_tokens"] or 0 for r in res)
    thit = sum(r["cache_hit"] or 0 for r in res)
    tout = sum(r["completion_tokens"] or 0 for r in res)
    # 離峰價（USD / 1M）：miss 0.66、hit 0.022、output 1.98；尖峰加倍
    cost = ((tin - thit) * 0.66 + thit * 0.022 + tout * 1.98) / 1e6
    print(f"[{datetime.datetime.now(datetime.UTC):%H:%M:%S} UTC] 成功 {ok}/{len(res)}｜findings "
          f"{sum(r['findings'] or 0 for r in res)}｜prompt {tin}（hit {thit}）｜completion {tout}｜"
          f"離峰估價 ${cost:.3f}（尖峰 ×2）")
    for r in res:
        if r["exit"] != 0:
            print(f"  ✗ {r['pr']} exit={r['exit']}（看 {r['pr']}.log）")


if __name__ == "__main__":
    main()
