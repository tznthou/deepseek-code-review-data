#!/usr/bin/env python3
"""等 probe 的三個 run 跑完，照 probe-expectations.md 逐項判定 P1–P12。

usage: python3 check_probe.py <since, 例如 2026-09-28T01:57:40Z>
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
res["P1"] = all(re.search(rf"@refs/tags/v1\.5\.0 \({TAG_OBJ}", logs[n]) for n in ("collect", "post"))
res["P2"] = re.search(rf"HEAD is now at {COMMIT} chore: 發布 v1\.5\.0 \(#48\)", logs["post"]) is not None
res["P3"] = col["conclusion"] == "success"
cr_jobs = {j["name"]: j["conclusion"] for j in jobs["code-review"]}
res["P4"] = cr["conclusion"] == "success" and sum(v == "success" for v in cr_jobs.values()) >= 4 \
    and any("dependency" in k.lower() and v == "skipped" for k, v in cr_jobs.items())
res["P5"] = post["conclusion"] == "failure" and "HTTP 401" in logs["post"]
res["P6"] = post_steps.get("取得呼叫方的自訂 rubric 與規範檔") == "success"
# log 會印出 run: 的腳本全文（行首帶色碼），腳本裡本來就寫著那句 warning；真的觸發要看 ##[warning]
# （第一版直接比對字串，P7 被腳本全文判成 FAIL——[[actions-silent-failures]] 記過的同一個坑）
res["P7"] = "repo 規範檔：.github/review-rules.md" in logs["post"] and \
    re.search(r"##\[warning\][^\n]*但檔案不存在", logs["post"]) is None
res["P8"] = post_steps.get("DeepSeek review（repo 規範）") == "skipped" and \
    post_steps.get("貼回 PR（摘要 + inline comments）") == "skipped"
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
