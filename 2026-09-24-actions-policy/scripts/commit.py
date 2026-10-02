"""在 probe 的 trigger 分支上改 app.py 建一個 commit（contents API），印出新 commit 的 SHA 與建立時間。
usage: python3 commit.py <label> <message-file>
"""
import base64, json, subprocess, sys

REPO = "tznthou/deepseek-review-probe"
label, msg_file = sys.argv[1], sys.argv[2]

def gh(*args, input_=None):
    r = subprocess.run(["gh", "api", *args], input=input_, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"gh api failed: {r.stderr.strip()}")
    return json.loads(r.stdout) if r.stdout.strip() else None

cur = gh(f"repos/{REPO}/contents/app.py?ref=trigger")
text = base64.b64decode(cur["content"]).decode("utf-8")
text = text.rstrip("\n") + f"\n# policy probe: {label}\n"
body = {
    "message": open(msg_file, encoding="utf-8").read(),
    "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
    "sha": cur["sha"],
    "branch": "trigger",
}
res = gh("-X", "PUT", f"repos/{REPO}/contents/app.py", "--input", "-", input_=json.dumps(body))
print(res["commit"]["sha"][:7], res["commit"]["committer"]["date"])
