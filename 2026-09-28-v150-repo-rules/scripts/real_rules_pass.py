#!/usr/bin/env python3
"""真 API 跑一次正式版的「規範那次呼叫」（cal.com-11），再用 post_review --dry-run 看合併與摘要。

key 沿用 run_bench.api_key()：從 keychain 讀、送出前驗形狀、不印不寫檔。
"""
import json, os, pathlib, re, subprocess, sys, tempfile

KIT = pathlib.Path("<repo>")
QODO = KIT / ".claude/experiments/2026-09-25-qodo-bench"
SCRATCH = pathlib.Path(__file__).parent
PR = "cal.com-11"
sys.path.insert(0, str(QODO / "scripts"))
sys.dont_write_bytecode = True
import run_bench  # noqa: E402

out = SCRATCH / "real-run"
out.mkdir(exist_ok=True)
rules_file = out / "cal.com-rules.md"
subprocess.run([sys.executable, str(SCRATCH / "compare_v01_render.py"), str(rules_file), "cal.com"], check=True,
               capture_output=True)
print(f"規範檔：{rules_file}（{len(rules_file.read_text(encoding='utf-8').splitlines())} 行）")

src = QODO / "prs" / PR
env = {**os.environ, "DEEPSEEK_API_KEY": run_bench.api_key(), "DEEPSEEK_MODEL": run_bench.MODEL,
       "REVIEW_BLOCKED_TERMS": "", "GITHUB_STEP_SUMMARY": str(out / "step-summary.md")}
(out / "step-summary.md").write_text("", encoding="utf-8")
cmd = [sys.executable, str(KIT / ".github/scripts/deepseek_review.py"),
       "--diff", str(src / "pr.diff"), "--meta", str(src / "meta.json"),
       "--rubric", str(KIT / "prompts/review-rubric.md"), "--rules-dir", str(KIT / "prompts/rules"),
       "--repo-rules", str(rules_file), "--timeout", "120", "--retries", "1",
       "--out", str(out / "rules-review.md"), "--findings-out", str(out / "rules-findings.json")]
p = subprocess.run(cmd, capture_output=True, text=True, env=env)
print(f"deepseek_review exit {p.returncode}")
print(p.stderr[-1500:])
if p.returncode != 0:
    sys.exit(1)

usage = json.loads(re.search(r"usage=(\{.*\})", p.stderr).group(1))
hit = usage.get("prompt_cache_hit_tokens", 0)
miss = usage.get("prompt_cache_miss_tokens", usage.get("prompt_tokens", 0) - hit)
comp = usage.get("completion_tokens", 0)
# 離峰價（USD / 1M）：miss 0.66、hit 0.022、output 1.98；尖峰加倍（同 run_bench.py）
off = (miss * 0.66 + hit * 0.022 + comp * 1.98) / 1e6
print(f"tokens：miss {miss}、hit {hit}、output {comp} → 離峰 ${off:.4f}／尖峰 ${off * 2:.4f}")

rules = json.loads((out / "rules-findings.json").read_text(encoding="utf-8"))
print("規範 finding：", [(f["path"].split("/")[-1], f["line"], f.get("rule"), f["confidence"], f["title"][:60]) for f in rules])
print("Step Summary：", (out / "step-summary.md").read_text(encoding="utf-8").strip())

base = QODO / "rounds/base-1"
post = subprocess.run(
    [sys.executable, str(KIT / ".github/scripts/post_review.py"), "--repo", "o/r", "--pr", "1", "--sha", "abc",
     "--review", str(base / f"{PR}.md"), "--findings", str(base / f"{PR}.json"), "--diff", str(src / "pr.diff"),
     "--rules-findings", str(out / "rules-findings.json"), "--rules-status", "success", "--dry-run"],
    capture_output=True, text=True, env={**os.environ, "GH_TOKEN": "dummy-for-dry-run"})
print(f"post_review exit {post.returncode}；{post.stderr.strip().splitlines()[-2:]}")
body = post.stdout
i = body.find("### 違反 repo 規範")
print(body[i:i + 900] if i >= 0 else body[-900:])
(out / "post-dry-run.txt").write_text(body, encoding="utf-8")
