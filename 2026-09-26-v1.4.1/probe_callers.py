#!/usr/bin/env python3
"""D5：probe main 上三支 caller 暫時改釘 @v1.4.1（stage），驗完原樣還原（restore）。

stage   先把原文存到 probe-orig/（已存在且跟遠端不同就中止），再改：
        `reusable-*.yml@v1` → `@v1.4.1`，post 與 codeql 加 `kit-ref: v1.4.1`（[[floating-major-tag-contract]]）
restore 直接 PUT probe-orig/ 的原文，再 GET 回來逐字比對
show    印出三支 caller 目前的 uses:／kit-ref 行
usage: python3 probe_callers.py stage|restore|show [--dry-run]
"""
import base64
import difflib
import json
import pathlib
import re
import subprocess
import sys

REPO = "tznthou/deepseek-review-probe"
FILES = ["ai-review-collect.yml", "ai-review-post.yml", "code-review.yml"]
TAG = "v1.4.1"
ORIG = pathlib.Path(__file__).parent / "probe-orig"


def gh(*args: str, input_: str | None = None):
    r = subprocess.run(["gh", "api", *args], input=input_, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"gh api failed: {' '.join(args)}: {r.stderr.strip()}")
    return json.loads(r.stdout) if r.stdout.strip() else None


def get(name: str) -> tuple[str, str]:
    cur = gh(f"repos/{REPO}/contents/.github/workflows/{name}?ref=main")
    return cur["sha"], base64.b64decode(cur["content"]).decode("utf-8")


def put(name: str, sha: str, text: str, msg: str) -> str:
    body = {
        "message": msg,
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        "sha": sha,
        "branch": "main",
    }
    res = gh("-X", "PUT", f"repos/{REPO}/contents/.github/workflows/{name}", "--input", "-", input_=json.dumps(body))
    return f"{res['commit']['sha'][:7]} {res['commit']['committer']['date']}"


def staged(name: str, text: str) -> str:
    new, n = re.subn(r"(reusable-[\w-]+\.yml)@v1$", rf"\1@{TAG}", text, flags=re.M)
    want = {"ai-review-collect.yml": 1, "ai-review-post.yml": 1, "code-review.yml": 2}[name]
    if n != want:
        sys.exit(f"{name}: 預期換 {want} 處 @v1，實際 {n} 處（已經 stage 過？）")
    anchor = {"ai-review-post.yml": r"      filter-findings: true", "code-review.yml": r"      languages: '\[\"python\"\]'"}.get(name)
    if anchor:
        new, k = re.subn(rf"^({anchor})$", rf"\1\n      kit-ref: {TAG}", new, flags=re.M)
        if k != 1:
            sys.exit(f"{name}: kit-ref 錨點命中 {k} 次，預期 1")
    return new


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "show"
    dry = "--dry-run" in sys.argv
    if mode == "show":
        for name in FILES:
            _, text = get(name)
            print(f"{name}: " + " | ".join(ln.strip() for ln in text.splitlines() if "uses:" in ln or "kit-ref" in ln))
        return 0
    if mode == "stage":
        for name in FILES:
            sha, text = get(name)
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
            print(f"  PUT {name}: {put(name, sha, new, f'驗 {TAG}：caller 暫時釘 @{TAG}（kit-ref 一起）')}")
        return 0
    if mode == "restore":
        bad = 0
        for name in FILES:
            orig = (ORIG / name).read_text(encoding="utf-8")
            sha, cur = get(name)
            if cur == orig:
                print(f"  {name}: 已經是原文")
                continue
            sys.stdout.writelines(difflib.unified_diff(cur.splitlines(True), orig.splitlines(True), name + " (now)", name + " (orig)"))
            if dry:
                continue
            print(f"  PUT {name}: {put(name, sha, orig, f'還原：caller 改回 @v1（{TAG} 驗完）')}")
            _, after = get(name)
            same = after == orig
            bad += not same
            print(f"  {name}: 還原後逐字比對 {'一致' if same else '不一致！'}")
        return 1 if bad else 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main())
