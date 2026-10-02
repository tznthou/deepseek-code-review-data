#!/usr/bin/env python3
"""把 R（真實 PR）的 finding 從 `04` 貼出的摘要 review 撈下來。

每一則非空的 review body 就是一次 run：摘要表逐筆列 severity／位置／標題／信心，
footer 有模型名稱。輸出 real-findings.json，對錯另外在 labels-R.csv 用標題對既有紀錄。
"""
import json
import pathlib
import re
import subprocess

OUT = pathlib.Path(__file__).resolve().parents[1]
REPO = "tznthou/deepseek-code-review"
PRS = [1, 2, 3, 21, 22, 27]

ROW = re.compile(r"^\| [^|]+ \| (\w+) \| `([^`]+)` \| (.+) \| ([0-9.]+) \|$")
MODEL = re.compile(r"model `([^`]+)`")


def reviews(pr: int) -> list[dict]:
    raw = subprocess.run(
        ["gh", "api", f"repos/{REPO}/pulls/{pr}/reviews", "--paginate"],
        check=True, capture_output=True, text=True,
    ).stdout
    return [r for r in json.loads(raw) if r.get("body")]


def main() -> None:
    rows = []
    for pr in PRS:
        for run_idx, rv in enumerate(reviews(pr), 1):
            body = rv["body"]
            model = MODEL.search(body)
            for line in body.splitlines():
                m = ROW.match(line.strip())
                if m:
                    rows.append({
                        "pr": pr,
                        "run": run_idx,
                        "submitted_at": rv["submitted_at"],
                        "model": model.group(1) if model else "?",
                        "severity": m.group(1),
                        "loc": m.group(2),
                        "title": m.group(3),
                        "confidence": float(m.group(4)),
                    })
    for i, r in enumerate(rows, 1):
        r["id"] = f"R{i:02d}"
    (OUT / "real-findings.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(r["id"], f"#{r['pr']}", f"run{r['run']}", r["submitted_at"][:16], r["model"], r["loc"], r["title"][:48], sep=" | ")
    print("total", len(rows))


if __name__ == "__main__":
    main()
