#!/usr/bin/env python3
"""v1.6.0 兩段式發版的 probe：caller 暫釘 @v1.6.0（kit-ref 一起），post 另外傳 inline-comments: true。

改自 ../../2026-09-28-v150-repo-rules/scripts/probe_v150.py（這次不建規範檔）。
stage   先把三支 caller 的原文存到 ../probe-orig/（已存在且跟遠端不同就中止），再改：
        `reusable-*.yml@v1` → `@v1.6.0`；post 與 codeql 加 `kit-ref: v1.6.0`；post 再加 `inline-comments: true`
restore 三支 caller PUT 回原文並逐字比對
show    印出三支 caller 目前的 uses:／kit-ref／inline-comments 行
usage: python3 probe_v160.py stage|restore|show [--dry-run]
"""
import base64, difflib, json, pathlib, re, subprocess, sys

REPO = "tznthou/deepseek-review-probe"
FILES = ["ai-review-collect.yml", "ai-review-post.yml", "code-review.yml"]
TAG = "v1.6.0"
ORIG = pathlib.Path(__file__).resolve().parent.parent / "probe-orig"


def gh(*args: str, input_: str | None = None, ok404: bool = False):
    r = subprocess.run(["gh", "api", *args], input=input_, capture_output=True, text=True)
    if r.returncode != 0:
        if ok404 and "404" in r.stderr + r.stdout:
            return None
        sys.exit(f"gh api failed: {' '.join(args)}: {r.stderr.strip()}")
    return json.loads(r.stdout) if r.stdout.strip() else None


def get(path: str):
    cur = gh(f"repos/{REPO}/contents/{path}?ref=main", ok404=True)
    if cur is None:
        return None, None
    return cur["sha"], base64.b64decode(cur["content"]).decode("utf-8")


def put(path: str, sha: str | None, text: str, msg: str) -> str:
    body = {"message": msg, "content": base64.b64encode(text.encode("utf-8")).decode("ascii"), "branch": "main"}
    if sha:
        body["sha"] = sha
    res = gh("-X", "PUT", f"repos/{REPO}/contents/{path}", "--input", "-", input_=json.dumps(body))
    return f"{res['commit']['sha'][:7]} {res['commit']['committer']['date']}"


def staged(name: str, text: str) -> str:
    new, n = re.subn(r"(reusable-[\w-]+\.yml)@v1$", rf"\1@{TAG}", text, flags=re.M)
    want = {"ai-review-collect.yml": 1, "ai-review-post.yml": 1, "code-review.yml": 2}[name]
    if n != want:
        sys.exit(f"{name}: 預期換 {want} 處 @v1，實際 {n} 處（已經 stage 過？）")
    extra = {"ai-review-post.yml": (r"      filter-findings: true", f"      kit-ref: {TAG}\n      inline-comments: true"),
             "code-review.yml": (r"      languages: '\[\"python\"\]'", f"      kit-ref: {TAG}")}.get(name)
    if extra:
        new, k = re.subn(rf"^({extra[0]})$", lambda m: m.group(1) + "\n" + extra[1], new, flags=re.M)
        if k != 1:
            sys.exit(f"{name}: 錨點命中 {k} 次，預期 1")
    return new


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "show"
    dry = "--dry-run" in sys.argv
    wf = lambda n: f".github/workflows/{n}"
    if mode == "show":
        for name in FILES:
            _, text = get(wf(name))
            print(f"{name}: " + " | ".join(ln.strip() for ln in text.splitlines()
                                            if any(k in ln for k in ("uses:", "kit-ref", "inline-comments"))))
        return 0
    if mode == "stage":
        for name in FILES:
            sha, text = get(wf(name))
            saved = ORIG / name
            if saved.exists() and saved.read_text(encoding="utf-8") != text:
                sys.exit(f"{name}: probe-orig 的原文跟遠端不同，先確認哪一份才是原文")
            new = staged(name, text)
            sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), name, name + " (staged)"))
            if dry:
                continue
            ORIG.mkdir(exist_ok=True)
            if not saved.exists():
                saved.write_text(text, encoding="utf-8")
            print(f"  PUT {name}: {put(wf(name), sha, new, f'驗 {TAG}：caller 暫時釘 @{TAG}（kit-ref 一起），post 傳 inline-comments: true')}")
        return 0
    if mode == "restore":
        bad = 0
        for name in FILES:
            orig = (ORIG / name).read_text(encoding="utf-8")
            sha, cur = get(wf(name))
            if cur == orig:
                print(f"  {name}: 已經是原文")
                continue
            if dry:
                continue
            print(f"  PUT {name}: {put(wf(name), sha, orig, f'還原：caller 改回 @v1（{TAG} 驗完）')}")
            _, after = get(wf(name))
            same = after == orig
            bad += not same
            print(f"  {name}: 還原後逐字比對 {'一致' if same else '不一致！'}")
        return 1 if bad else 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main())
