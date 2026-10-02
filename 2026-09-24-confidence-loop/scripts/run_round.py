#!/usr/bin/env python3
"""跑一輪：三個標的 × N 次，全部用同一份 rubric。

呼叫方式照 reusable-ai-review-post.yml 的那一步（--diff --meta --rubric --out
--findings-out --rules-dir，模型走 DEEPSEEK_MODEL），不多傳別的參數——兩個入口的
參數會無聲分岔，這支要跟 CI 看到的是同一件事。key 從 keychain 讀進子程序的環境，
不印、不寫檔。

用法：run_round.py <輪次標籤> <rubric 路徑> [--runs 5] [--workers 5]
"""
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import re
import subprocess
import sys
import time

LOOP = pathlib.Path(__file__).resolve().parents[1]
KIT = LOOP.parents[2]  # <repo>/.claude/experiments/<loop> → <repo>
REVIEWER = KIT / ".github/scripts/deepseek_review.py"
RULES_DIR = KIT / "prompts/rules"
MODEL = "deepseek-v4-pro"
USAGE_RE = re.compile(r"usage=(\{.*\})")


def api_key() -> str:
    try:
        key = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", "deepseek-api-key"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit("keychain 裡沒有 deepseek-api-key（見 README「前置」）")
    # 送出前先驗 key 的形狀（避免把存錯的值當成 key 送出去）。
    # 形狀不對就不送，錯誤訊息也不帶值本身。
    if not re.fullmatch(r"sk-[A-Za-z0-9]{20,}", key):
        sys.exit(f"keychain 裡的 deepseek-api-key 不像 DeepSeek key（長度 {len(key)}、"
                 f"sk- 開頭：{key.startswith('sk-')}），不送出")
    return key


def one(label: str, rubric: pathlib.Path, target: str, diff: pathlib.Path, meta: pathlib.Path,
        i: int, env: dict, rules_dir: pathlib.Path = RULES_DIR) -> dict:
    out = LOOP / "rounds" / label
    stem = out / f"{target}-{i}"
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(REVIEWER), "--diff", str(diff), "--meta", str(meta),
         "--rubric", str(rubric), "--out", f"{stem}.md", "--findings-out", f"{stem}.json",
         "--rules-dir", str(rules_dir)],
        env=env, capture_output=True, text=True,
    )
    (stem.with_suffix(".log")).write_text(proc.stderr, encoding="utf-8")
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
    return {"target": target, "run": i, "exit": proc.returncode, "findings": n,
            "seconds": round(time.time() - t0, 1),
            "prompt_tokens": usage.get("prompt_tokens"),
            "cache_hit": usage.get("prompt_cache_hit_tokens"),
            "completion_tokens": usage.get("completion_tokens")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("rubric")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--workers", type=int, default=5)
    # 2026-10-01 追加（prompt-hygiene 實驗）：量 prompts/rules 的改動又不動工作目錄。不給就跟以前一樣
    ap.add_argument("--rules-dir", default=str(RULES_DIR))
    args = ap.parse_args()

    rubric = pathlib.Path(args.rubric).resolve()
    rules_dir = pathlib.Path(args.rules_dir).resolve()
    if not rules_dir.is_dir():
        sys.exit(f"--rules-dir 不存在：{rules_dir}")
    rules = json.loads((LOOP / "expected-rules.json").read_text(encoding="utf-8"))
    out = LOOP / "rounds" / args.label
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} 已經有東西了，不覆寫（換一個標籤）")
    out.mkdir(parents=True, exist_ok=True)

    env = {**os.environ, "DEEPSEEK_API_KEY": api_key(), "DEEPSEEK_MODEL": MODEL}
    env.pop("REVIEW_BLOCKED_TERMS", None)
    jobs = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for target, spec in rules["targets"].items():
            diff = LOOP / spec["diff"]
            meta = LOOP / "targets" / f"meta-{target}.json"
            for i in range(1, args.runs + 1):
                jobs.append(ex.submit(one, args.label, rubric, target, diff, meta, i, env, rules_dir))
        results = sorted((j.result() for j in jobs), key=lambda r: (r["target"], r["run"]))

    manifest = {"label": args.label, "rubric": str(rubric), "rules_dir": str(rules_dir), "model": MODEL,
                "runs": args.runs, "results": results}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(r["exit"] == 0 for r in results)
    tok_in = sum(r["prompt_tokens"] or 0 for r in results)
    tok_hit = sum(r["cache_hit"] or 0 for r in results)
    tok_out = sum(r["completion_tokens"] or 0 for r in results)
    for r in results:
        print(f"{r['target']:6} run{r['run']} exit={r['exit']} findings={r['findings']} {r['seconds']}s")
    print(f"成功 {ok}/{len(results)}｜prompt {tok_in}（cache hit {tok_hit}）｜completion {tok_out}")


if __name__ == "__main__":
    main()
