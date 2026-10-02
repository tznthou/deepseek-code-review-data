#!/usr/bin/env python3
"""抓 Qodo PR-Review-Bench 的 100 個 PR：資料集檔案（釘 revision）＋每個 PR 的 diff 與 metadata。

輸出（全部在本實驗目錄下）：
  data/bench.jsonl、data/rules_for_repo.jsonl、data/revision.txt
  prs/<repo>-<n>/pr.diff      `pulls/{n}` 帶 diff media type（等同 `git diff base...head`）
  prs/<repo>-<n>/meta.json    跟 collect 產的格式一樣：number、title、base_ref、head_sha
  prs/<repo>-<n>/pr.json      state、base／head SHA、檔案數、增減行數（留底用）
  prs/manifest.json

只做 GET，不寫任何東西到 GitHub。重跑時已經抓過的 PR 會跳過。
"""
import concurrent.futures as cf
import json
import pathlib
import subprocess
import sys
import urllib.request

EXP = pathlib.Path(__file__).resolve().parents[1]
DATA = EXP / "data"
PRS = EXP / "prs"
HF = "https://huggingface.co"
DATASET = "Qodo/PR-Review-Bench"
FILES = ["git_code_review_bench_100_w_open_prs.jsonl", "rules_for_repo.jsonl"]


def hf_revision() -> str:
    with urllib.request.urlopen(f"{HF}/api/datasets/{DATASET}", timeout=60) as r:
        return json.load(r)["sha"]


def download_dataset() -> str:
    DATA.mkdir(parents=True, exist_ok=True)
    rev_file = DATA / "revision.txt"
    if rev_file.exists():
        return rev_file.read_text().strip()
    rev = hf_revision()
    for name in FILES:
        url = f"{HF}/datasets/{DATASET}/resolve/{rev}/{name}"
        out = DATA / ("bench.jsonl" if name.startswith("git_code_review") else name)
        with urllib.request.urlopen(url, timeout=120) as r:
            out.write_bytes(r.read())
    rev_file.write_text(rev + "\n")
    return rev


def gh(args: list[str]) -> str:
    proc = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:300])
    return proc.stdout


def fetch_one(url: str) -> dict:
    # https://github.com/<owner>/<repo>/pull/<n>
    parts = url.rstrip("/").split("/")
    owner, repo, num = parts[-4], parts[-3], parts[-1]
    key = f"{repo}-{num}"
    d = PRS / key
    if (d / "pr.diff").exists() and (d / "meta.json").exists():
        return {"key": key, "status": "cached"}
    d.mkdir(parents=True, exist_ok=True)
    try:
        pr = json.loads(gh([f"repos/{owner}/{repo}/pulls/{num}"]))
        diff = gh(["-H", "Accept: application/vnd.github.v3.diff", f"repos/{owner}/{repo}/pulls/{num}"])
    except RuntimeError as e:
        return {"key": key, "status": "error", "error": str(e)}
    (d / "pr.diff").write_text(diff, encoding="utf-8")
    meta = {"number": pr["number"], "title": pr["title"], "base_ref": pr["base"]["ref"],
            "head_sha": pr["head"]["sha"]}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    keep = {"url": url, "state": pr["state"], "base_sha": pr["base"]["sha"], "head_sha": pr["head"]["sha"],
            "changed_files": pr.get("changed_files"), "additions": pr.get("additions"),
            "deletions": pr.get("deletions"), "created_at": pr.get("created_at")}
    (d / "pr.json").write_text(json.dumps(keep, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"key": key, "status": "ok", "diff_chars": len(diff)}


def main() -> None:
    rev = download_dataset()
    rows = [json.loads(l) for l in (DATA / "bench.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    urls = [r["pr_url_to_review"] for r in rows]
    PRS.mkdir(parents=True, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(fetch_one, urls))
    for r in results:
        d = PRS / r["key"]
        if r["status"] != "error" and (d / "pr.diff").exists():
            r["diff_chars"] = len((d / "pr.diff").read_text(encoding="utf-8"))
    (PRS / "manifest.json").write_text(json.dumps({"dataset_revision": rev, "prs": results},
                                                  ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [r for r in results if r["status"] == "error"]
    print(f"dataset revision {rev}｜PR {len(results)}｜失敗 {len(bad)}")
    for r in bad:
        print(f"  ✗ {r['key']}: {r['error']}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
