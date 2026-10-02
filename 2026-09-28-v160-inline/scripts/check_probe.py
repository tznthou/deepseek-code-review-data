#!/usr/bin/env python3
"""等 probe 的三個 run 跑完，照 ../probe-expectations.md 逐項判定 P1–P12（v1.6.0）。

改自 ../../2026-09-28-v150-repo-rules/scripts/check_probe.py：P1/P2 換成 v1.6.0；P6–P8 改成這次沒設規範檔的路徑。
usage: python3 check_probe.py <since, 例如 2026-09-28T06:10:00Z>
"""
import json, re, subprocess, sys, time

REPO = "tznthou/deepseek-review-probe"
SINCE = sys.argv[1]
TAG_OBJ, COMMIT = "40c2a78", "49a5975"


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def runs():
    out = gh("run", "list", "--repo", REPO, "--limit", "30", "--json",
             "databaseId,workflowName,status,conclusion,createdAt,event")
    return [r for r in json.loads(out) if r["createdAt"] > SINCE]


def pick(rs, key):
    return next((r for r in rs if key in r["workflowName"].lower()), None)


deadline = time.time() + 20 * 60
while True:
    rs = runs()
    col, cr, post = pick(rs, "collect"), pick(rs, "code review") or pick(rs, "code-review"), pick(rs, "post")
    done = all(r and r["status"] == "completed" for r in (col, cr, post))
    if done or time.time() > deadline:
        break
    time.sleep(20)

for name, r in (("collect", col), ("code-review", cr), ("post", post)):
    print(f"{name}: {r and (r['databaseId'], r['status'], r['conclusion'], r['createdAt'])}")
if not done:
    sys.exit("逾時：三個 run 沒有全部跑完")

logs = {name: gh("run", "view", str(r["databaseId"]), "--repo", REPO, "--log") for name, r in
        (("collect", col), ("code-review", cr), ("post", post))}
jobs = {name: json.loads(gh("run", "view", str(r["databaseId"]), "--repo", REPO, "--json", "jobs"))["jobs"]
        for name, r in (("code-review", cr), ("post", post))}
post_steps = {s["name"]: s["conclusion"] for j in jobs["post"] for s in j.get("steps", [])}
res = {}
res["P1"] = all(re.search(rf"@refs/tags/v1\.6\.0 \({TAG_OBJ}", logs[n]) for n in ("collect", "post"))
res["P2"] = re.search(rf"HEAD is now at {COMMIT} chore: 發布 v1\.6\.0 \(#55\)", logs["post"]) is not None
res["P3"] = col["conclusion"] == "success"
cr_jobs = {j["name"]: j["conclusion"] for j in jobs["code-review"]}
res["P4"] = cr["conclusion"] == "success" and sum(v == "success" for v in cr_jobs.values()) >= 4 \
    and any("dependency" in k.lower() and v == "skipped" for k, v in cr_jobs.items())
res["P5"] = post["conclusion"] == "failure" and "HTTP 401" in logs["post"]
res["P6"] = post_steps.get("取得呼叫方的自訂 rubric 與規範檔") == "skipped"
res["P7"] = post_steps.get("決定規範檔") == "skipped" and post_steps.get("DeepSeek review（repo 規範）") == "skipped"
res["P8"] = post_steps.get("貼回 PR（摘要 + inline comments）") == "skipped"
# log 會印出 run: 的腳本全文，真的觸發的 warning 要看 ##[warning]（v1.5.0 那次 P7 誤判過）
res["P9"] = len(re.findall(r"##\[warning\]filter-findings 自 v1\.2\.0 起沒有作用", logs["post"])) == 1
res["P10"] = "送出前掃描" not in logs["post"]
downloads = re.findall(r"Download action repository '([^']+)'", "\n".join(logs.values()))
res["P11"] = bool(downloads) and all(re.search(r"@[0-9a-f]{40}$", d) for d in downloads)
res["P12"] = any("上傳 review 產出" in k and v in ("success", "failure") for k, v in post_steps.items())
for k, v in res.items():
    print(f"{'PASS' if v else 'FAIL'} {k}")
print(f"{sum(res.values())}/{len(res)}")
print("code-review jobs:", cr_jobs)
print("post steps:", post_steps)
if not res["P11"]:
    print("非 SHA 的下載：", [d for d in downloads if not re.search(r'@[0-9a-f]{40}$', d)][:10])
