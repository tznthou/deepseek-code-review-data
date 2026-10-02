"""release notes 產生器：整理兩個 tag 之間的 commit，貼到團隊頻道的 webhook。

用法：
    export NOTES_WEBHOOK=https://hooks.example.com/services/T000/B000/XXXX
    python3 sandbox/release_notes.py <repo 路徑> <tag>
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

TAG_RE = re.compile(r"^v\d+\.\d+\.\d+$")
DEFAULT_MAX = 50
LABELS = {"feat": "新功能", "fix": "修正", "other": "其他"}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def load_config(path: str) -> dict:
    # 設定檔是選配的：沒有就全部用預設值
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise SystemExit(f"設定檔 {path} 不是合法的 JSON：{e}")


def max_items() -> int:
    raw = os.environ.get("NOTES_MAX", "")
    if not raw:
        return DEFAULT_MAX
    try:
        return int(raw)
    except ValueError:
        log(f"[warn] NOTES_MAX={raw!r} 不是整數，改用預設值 {DEFAULT_MAX}")
        return DEFAULT_MAX


def list_tags(repo: str) -> list[str]:
    out = subprocess.run(
        ["git", "tag", "--list", "v*", "--sort=v:refname"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
    return [t for t in out.splitlines() if TAG_RE.match(t)]


def commits_between(repo: str, prev: str, tag: str) -> list[tuple[str, str]]:
    proc = subprocess.run(
        ["git", "log", "--format=%h %s", f"{prev}..{tag}"],
        cwd=repo, capture_output=True, text=True,
    )
    commits = []
    for line in proc.stdout.splitlines():
        if " " not in line:
            continue
        sha, subject = line.split(" ", 1)
        commits.append((sha, subject))
    return commits


def group(commits: list[tuple[str, str]]) -> list[tuple[str, list[str]]]:
    groups: dict[str, list[str]] = {kind: [] for kind in LABELS}
    for sha, subject in commits:
        prefix = subject.split(":", 1)[0]
        kind = prefix if prefix in groups else "other"
        groups[kind].append(f"{subject} ({sha})")
    return [(LABELS[k], items) for k, items in groups.items() if items]


def render(title: str, sections, footer=[]) -> str:
    lines = [title]
    for label, items in sections:
        lines.append(f"\n{label}")
        lines += [f"• {item}" for item in items]
    lines += footer
    return "\n".join(lines)


def post(url: str, text: str) -> bool:
    body = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    # 不重試：webhook 端沒有冪等鍵，重送一次頻道裡就會出現兩則一樣的公告
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except urllib.error.URLError as e:
        log(f"[error] 貼到 {url} 失敗：{e}")
        return False


def main() -> int:
    if len(sys.argv) != 3:
        log("用法：release_notes.py <repo 路徑> <tag>")
        return 2
    repo, tag = sys.argv[1], sys.argv[2]
    if not TAG_RE.match(tag):
        log(f"tag 格式要像 v1.2.3：{tag}")
        return 2
    url = os.environ.get("NOTES_WEBHOOK")
    if not url:
        log("請先設定 NOTES_WEBHOOK")
        return 2

    tags = list_tags(repo)
    if tag not in tags:
        log(f"找不到 tag {tag}")
        return 2
    prev = tags[tags.index(tag) - 1]
    commits = commits_between(repo, prev, tag)
    if not commits:
        log(f"{prev}..{tag} 之間沒有新 commit")
        return 0

    cfg = load_config(os.path.join(repo, ".release-notes.json"))
    latest = commits[0][0]
    title = f"*{cfg.get('title', '發版公告')}* {tag}（最新 {latest}）"
    text = render(title, group(commits[: max_items()]))
    if not post(url, text):
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
