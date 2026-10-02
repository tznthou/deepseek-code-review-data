#!/usr/bin/env python3
"""rules loop 的 runner：參數跟 Qodo 的 run_bench.py（也就是 CI）相同，只多附 repo 規範。

- 一輪一個標籤，輸出在 rounds/<標籤>/；同一個標籤換了設定、切分、rubric 或腳本就拒跑，不混在一起。
- 可以續跑：同標籤下已經成功的 PR 會跳過。
- 不給 --config = 不附規範，直接跑 kit 原本的 deepseek_review.py（對照用；v00 用 Qodo 既有的 base-1、base-2）。
- key 沿用 run_bench.api_key()：從 keychain 讀、送出前驗形狀、不印不寫檔。

用法：run_rules.py <標籤> [--config iterations/v01.json] [--split tune|holdout|all] [--only PR ...] [--workers 5]
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

sys.dont_write_bytecode = True
from common import KIT, LOOP, QODO, pr_repo, split_prs  # noqa: E402

sys.path.insert(0, str(QODO / "scripts"))
import render  # noqa: E402
import run_bench  # noqa: E402  api_key() 與 MODEL 共用 Qodo 那份，兩個入口不分岔

WRAPPER = LOOP / "scripts/review_with_rules.py"
REVIEWER = KIT / ".github/scripts/deepseek_review.py"
RUBRIC = KIT / "prompts/review-rubric.md"
RULES_DIR = KIT / "prompts/rules"
USAGE_RE = re.compile(r"usage=(\{.*\})")
IDENTITY = ("config_sha256", "split", "only", "rubric_sha256", "wrapper_sha256", "render_sha256")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(out: pathlib.Path, cfg: pathlib.Path | None, key: str, env: dict) -> dict:
    src = QODO / "prs" / key
    stem = out / key
    kit_args = ["--diff", str(src / "pr.diff"), "--meta", str(src / "meta.json"), "--rubric", str(RUBRIC),
                "--out", f"{stem}.md", "--findings-out", f"{stem}.json", "--rules-dir", str(RULES_DIR)]
    if cfg:
        cmd = [sys.executable, str(WRAPPER), "--rules-config", str(cfg), "--repo", pr_repo(key)] + kit_args
    else:
        cmd = [sys.executable, str(REVIEWER)] + kit_args
    t0 = time.time()
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
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


def summary(manifest: dict, keys: list[str]) -> None:
    res = [manifest["results"][k] for k in keys if k in manifest["results"]]
    ok = sum(r["exit"] == 0 for r in res)
    tin = sum(r["prompt_tokens"] or 0 for r in res)
    thit = sum(r["cache_hit"] or 0 for r in res)
    tout = sum(r["completion_tokens"] or 0 for r in res)
    # 離峰價（USD / 1M）：miss 0.66、hit 0.022、output 1.98；尖峰加倍（同 run_bench.py）
    cost = ((tin - thit) * 0.66 + thit * 0.022 + tout * 1.98) / 1e6
    print(f"[{datetime.datetime.now(datetime.UTC):%H:%M:%S} UTC] {manifest['label']}：成功 {ok}/{len(keys)}｜"
          f"findings {sum(r['findings'] or 0 for r in res)}｜prompt {tin}（hit {thit}）｜completion {tout}｜"
          f"離峰估價 ${cost:.3f}（尖峰 ×2）")
    for r in res:
        if r["exit"] != 0:
            print(f"  ✗ {r['pr']} exit={r['exit']}（看 {r['pr']}.log）")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--config", default=None, help="呈現設定（iterations/vNN.json）；不給 = 不附規範")
    ap.add_argument("--split", choices=("tune", "holdout", "all"), default="tune")
    ap.add_argument("--only", nargs="+", default=None, help="只跑這幾個 PR（smoke 用）")
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()

    cfg = pathlib.Path(args.config).resolve() if args.config else None
    if cfg:
        render.check(json.loads(cfg.read_text(encoding="utf-8")))  # 設定不合法就在花錢之前停
    keys = split_prs(args.split)
    if args.only:
        unknown = sorted(set(args.only) - set(keys))
        if unknown:
            sys.exit(f"不在 {args.split} 裡：{unknown}")
        keys = [k for k in keys if k in args.only]

    out = LOOP / "rounds" / args.label
    out.mkdir(parents=True, exist_ok=True)
    man_path = out / "manifest.json"
    ident = {"config": str(cfg) if cfg else None, "config_sha256": sha(cfg) if cfg else None,
             "config_content": json.loads(cfg.read_text(encoding="utf-8")) if cfg else None,
             "split": args.split, "only": sorted(args.only) if args.only else None,
             "rubric_sha256": sha(RUBRIC), "wrapper_sha256": sha(WRAPPER),
             "render_sha256": sha(LOOP / "scripts/render.py")}
    if man_path.exists():
        manifest = json.loads(man_path.read_text(encoding="utf-8"))
        changed = [k for k in IDENTITY if manifest.get(k) != ident[k]]
        if changed:
            sys.exit(f"標籤 {args.label} 之前的 {changed} 跟這次不同，不混在同一輪（換一個標籤）")
    else:
        manifest = {"label": args.label, **ident,
                    "kit_head": subprocess.run(["git", "-C", str(KIT), "rev-parse", "HEAD"], capture_output=True,
                                               text=True).stdout.strip(),
                    "dataset_revision": (QODO / "data/revision.txt").read_text().strip(),
                    "model": run_bench.MODEL,
                    "started_utc": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
                    "results": {}}

    todo = [k for k in keys if manifest["results"].get(k, {}).get("exit") != 0]
    print(f"[{datetime.datetime.now(datetime.UTC):%H:%M:%S} UTC] {args.label}：{args.split} 共 {len(keys)}，"
          f"要跑 {len(todo)}（設定：{cfg.name if cfg else '不附規範'}）")
    if todo:
        env = {**os.environ, "DEEPSEEK_API_KEY": run_bench.api_key(), "DEEPSEEK_MODEL": run_bench.MODEL}
        env.pop("REVIEW_BLOCKED_TERMS", None)
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            for r in ex.map(lambda k: one(out, cfg, k, env), todo):
                manifest["results"][r["pr"]] = r
                man_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    summary(manifest, keys)


if __name__ == "__main__":
    main()
