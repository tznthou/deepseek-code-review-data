"""抓 public run 頁面，印出 Annotations 區塊的文字。usage: python3 ann2.py <owner/repo> <run_id>"""
import html, re, subprocess, sys
repo, rid = sys.argv[1], sys.argv[2]
s = subprocess.run(["curl", "-sS", "-m", "30", "-L", f"https://github.com/{repo}/actions/runs/{rid}"], capture_output=True, text=True).stdout
t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))
i = t.find("Annotations")
print(f"{repo} run {rid}:", t[i:i+700] if i >= 0 else "(no Annotations block)")
