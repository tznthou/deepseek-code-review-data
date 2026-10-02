#!/usr/bin/env python3
"""Phase F：移 v1 之後，probe 原本的 caller（@v1、沒設 repo-rules-path）逐項判定 F1–F8。

usage: python3 check_probe_f.py <since>
"""
import json, re, subprocess, sys, time

REPO = "tznthou/deepseek-review-probe"
SINCE = sys.argv[1]
TAG_OBJ, COMMIT = "fce93b1", "babdcc6"


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def pick(rs, key):
    return next((r for r in rs if key in r["workflowName"].lower()), None)


deadline = time.time() + 20 * 60
while True:
    rs = [r for r in json.loads(gh("run", "list", "--repo", REPO, "--limit", "30", "--json",
                                   "databaseId,workflowName,status,conclusion,createdAt")) if r["createdAt"] > SINCE]
    col, cr, post = pick(rs, "collect"), pick(rs, "code review"), pick(rs, "post")
    done = all(r and r["status"] == "completed" for r in (col, cr, post))
    if done or time.time() > deadline:
        break
    time.sleep(20)
for name, r in (("collect", col), ("code-review", cr), ("post", post)):
    print(f"{name}: {r and (r['databaseId'], r['conclusion'], r['createdAt'])}")
if not done:
    sys.exit("逾時")
logs = {n: gh("run", "view", str(r["databaseId"]), "--repo", REPO, "--log") for n, r in
        (("collect", col), ("code-review", cr), ("post", post))}
cr_jobs = {j["name"]: j["conclusion"] for j in json.loads(gh("run", "view", str(cr["databaseId"]), "--repo", REPO, "--json", "jobs"))["jobs"]}
steps = {s["name"]: s["conclusion"] for j in json.loads(gh("run", "view", str(post["databaseId"]), "--repo", REPO, "--json", "jobs"))["jobs"]
         for s in j.get("steps", [])}
res = {
    "F1": all(re.search(rf"@refs/tags/v1 \({TAG_OBJ}", logs[n]) for n in ("collect", "post")),
    "F2": re.search(rf"HEAD is now at {COMMIT} chore: 發布 v1\.5\.0 \(#48\)", logs["post"]) is not None,
    "F3": col["conclusion"] == "success",
    "F4": cr["conclusion"] == "success" and sum(v == "success" for v in cr_jobs.values()) >= 4
          and any("dependency" in k.lower() and v == "skipped" for k, v in cr_jobs.items()),
    "F5": post["conclusion"] == "failure" and "HTTP 401" in logs["post"],
    "F6": len(re.findall(r"##\[warning\]filter-findings 自 v1\.2\.0 起沒有作用", logs["post"])) == 1,
    "F7": "送出前掃描" not in logs["post"],
    "F8": steps.get("決定規範檔") == "skipped" and steps.get("DeepSeek review（repo 規範）") == "skipped"
          and steps.get("取得呼叫方的自訂 rubric 與規範檔") == "skipped",
}
for k, v in res.items():
    print(f"{'PASS' if v else 'FAIL'} {k}")
print(f"{sum(res.values())}/{len(res)}")
print("post steps:", steps)
