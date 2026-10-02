#!/usr/bin/env python3
"""替 Qodo 評估集的 100 個 PR 產生「擴到所在函式」的 diff（`git diff -W`）。$0，只做 GET。

做法：每個 fork repo 一個 bare 的 partial clone（blob:none），只抓 merge base 與 head 兩個 commit
（depth=1，照 SHA 抓），diff 需要的 blob 由 git 自己補抓。

「所在函式」由 git 的 funcname 規則決定，有兩種來源，兩種都產：
  plain    只照 repo 自己的 .gitattributes（`--attr-source=<head>`；正式環境 collect 在 checkout 裡
           跑 git diff，讀的就是工作目錄的 .gitattributes）。大多數 repo 沒設 → git 預設規則：
           「行首是英文字母、底線或 $」才算函式開頭 → 縮排的方法（class 裡的）擴成整個 class
  drivers  再加一份依副檔名對應 git 內建 driver 的 attributes（`-c core.attributesFile=`，
           優先序低於 repo 自己的 .gitattributes）。JS／TS／Swift 沒有內建 driver，兩種一樣

輸出 prs/<key>/：
  u3.diff        `git diff -U3`（plain）——正向對照：去掉 hunk 標頭的函式名稱後必須與 Qodo 的 pr.diff 相同
  u3d.diff       `git diff -U3`（drivers）——看 GitHub 的 hunk 標頭是不是就是內建 driver 的結果
  w.diff         `git diff -W`（plain）
  wd.diff        `git diff -W`（drivers）
  mb.json        merge base 與 compare API 的 ahead／behind
  meta.json      複製 Qodo 那份（跑的時候 --meta 用同一份）
index 行的 hash 一律換成 Qodo 那份的縮寫（見 match_index_lines）。

用法：build_diffs.py [--only <key>...]
"""
import argparse
import collections
import concurrent.futures as cf
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
QODO = EXP.parent / "2026-09-25-qodo-bench"
CACHE = EXP / "cache"
OUT = EXP / "prs"
ORG = "agentic-review-benchmarks"
ATTRS = EXP / "scripts" / "builtin-drivers.gitattributes"
HUNK_HEAD = re.compile(r"^(@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@).*$", re.M)


def run(args: list[str]) -> str:
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(args[:5])}…: {proc.stderr.strip()[:400]}")
    return proc.stdout


def git(repo_dir: pathlib.Path, *args: str) -> str:
    return run(["git", "-C", str(repo_dir), *args])


def ensure_repo(repo: str) -> pathlib.Path:
    d = CACHE / f"{repo}.git"
    if not d.exists():
        d.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "--bare", "--quiet", str(d)])
        git(d, "remote", "add", "origin", f"https://github.com/{ORG}/{repo}.git")
        git(d, "config", "remote.origin.promisor", "true")
        git(d, "config", "remote.origin.partialclonefilter", "blob:none")
    return d


def keys() -> list[str]:
    rows = [json.loads(l) for l in (QODO / "data/bench.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for r in rows:
        parts = r["pr_url_to_review"].rstrip("/").split("/")
        out.append(f"{parts[-3]}-{parts[-1]}")
    return out


def match_index_lines(diff: str, qodo: str) -> str:
    """把 `index <完整 hash>..<完整 hash>` 換成 Qodo 那份的縮寫。

    GitHub 的縮寫長度看 repo 物件數（這批 11–14 字元），本機 partial clone 算出來的不一樣。
    逐行配對，而且要求 Qodo 的縮寫是完整 hash 的前綴——順便驗證兩邊指的是同一個 blob。
    """
    lines = diff.split("\n")
    ours = [i for i, l in enumerate(lines) if l.startswith("index ")]
    theirs = [l for l in qodo.split("\n") if l.startswith("index ")]
    if len(ours) != len(theirs):
        raise RuntimeError(f"index 行數不同：本機 {len(ours)}、Qodo {len(theirs)}")
    for i, q in zip(ours, theirs):
        full_a, full_b = lines[i].split()[1].split("..")
        qa, qb = q.split()[1].split("..")
        if not (full_a.startswith(qa) and full_b.startswith(qb)) or lines[i].split()[2:] != q.split()[2:]:
            raise RuntimeError(f"index 行對不上：{lines[i][:60]} vs {q[:60]}")
        lines[i] = q
    return "\n".join(lines)


def strip_funcname(diff: str) -> str:
    return HUNK_HEAD.sub(r"\1", diff)


def one(key: str) -> dict:
    src = QODO / "prs" / key
    pr = json.loads((src / "pr.json").read_text(encoding="utf-8"))
    repo = pr["url"].rstrip("/").split("/")[-3]
    dst = OUT / key
    dst.mkdir(parents=True, exist_ok=True)

    mb_path = dst / "mb.json"
    if mb_path.exists():
        mb = json.loads(mb_path.read_text(encoding="utf-8"))
    else:
        cmp = json.loads(run(["gh", "api", f"repos/{ORG}/{repo}/compare/{pr['base_sha']}...{pr['head_sha']}"]))
        mb = {"merge_base": cmp["merge_base_commit"]["sha"], "base_sha": pr["base_sha"], "head_sha": pr["head_sha"],
              "status": cmp["status"], "ahead_by": cmp["ahead_by"], "behind_by": cmp["behind_by"]}
        mb_path.write_text(json.dumps(mb, indent=1), encoding="utf-8")

    d = ensure_repo(repo)
    base, head = mb["merge_base"], mb["head_sha"]
    # ⚠️ 檢查要關掉 lazy fetch：partial clone 裡 `cat-file -e` 碰到缺的 commit 會自動去遠端補，
    # 而且補的是整段歷史（不帶 depth；2026-09-30 實測 Ghost 一次 390 MB）。
    no_lazy = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
    missing = [s for s in (base, head)
               if subprocess.run(["git", "-C", str(d), "cat-file", "-e", f"{s}^{{commit}}"],
                                 capture_output=True, env=no_lazy).returncode]
    if missing:
        git(d, "fetch", "--quiet", "--depth=1", "--filter=blob:none", "origin", *missing)

    qodo = (src / "pr.diff").read_text(encoding="utf-8")
    plain = [f"--attr-source={head}"]
    drivers = plain + ["-c", f"core.attributesFile={ATTRS}"]
    out = {}
    for name, pre, ctx in (("u3", plain, "-U3"), ("u3d", drivers, "-U3"), ("w", plain, "-W"), ("wd", drivers, "-W")):
        text = match_index_lines(git(d, *pre, "diff", "--full-index", ctx, base, head), qodo)
        (dst / f"{name}.diff").write_text(text, encoding="utf-8")
        out[name] = text
    shutil.copyfile(src / "meta.json", dst / "meta.json")

    return {"key": key, "repo": repo, "mb_is_base": base == pr["base_sha"],
            "u3_same_body": strip_funcname(out["u3"]) == strip_funcname(qodo),
            "u3_exact": out["u3"] == qodo, "u3d_exact": out["u3d"] == qodo,
            "qodo": len(qodo), "w": len(out["w"]), "wd": len(out["wd"]),
            "ratio_w": round(len(out["w"]) / len(qodo), 2), "ratio_wd": round(len(out["wd"]) / len(qodo), 2)}


def one_safe(key: str) -> dict:
    try:
        r = one(key)
    except RuntimeError as e:
        r = {"key": key, "error": str(e)}
    print(json.dumps(r, ensure_ascii=False), flush=True)
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    todo = args.only or keys()
    # 同一個 repo 的 PR 共用一個 bare repo（git 有鎖），依序跑；不同 repo 平行
    groups = collections.defaultdict(list)
    for k in todo:
        groups[k.rsplit("-", 1)[0]].append(k)
    with cf.ThreadPoolExecutor(max_workers=len(groups)) as ex:
        done = {}
        for rs in ex.map(lambda ks: [one_safe(k) for k in ks], groups.values()):
            done.update({r["key"]: r for r in rs})
    results = [done[k] for k in todo]
    if not args.only:
        (OUT / "manifest.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = [r for r in results if "error" not in r]
    print(f"共 {len(results)}｜錯誤 {len(results) - len(ok)}｜去掉函式名稱後與 Qodo 相同 "
          f"{sum(r['u3_same_body'] for r in ok)}｜逐字相同 plain {sum(r['u3_exact'] for r in ok)}"
          f"、drivers {sum(r['u3d_exact'] for r in ok)}")
    if len(ok) != len(results) or not all(r["u3_same_body"] for r in ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
