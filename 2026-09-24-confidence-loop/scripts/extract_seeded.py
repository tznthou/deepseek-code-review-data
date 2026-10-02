#!/usr/bin/env python3
"""把 S（埋點標的）的 v4-pro finding 抽成盲標單。

標記單拿掉 confidence 與 severity，只留判斷對錯需要的欄位；信心值另外存進
key-S.json，標完才 join（PREREG.md「盲標」）。順便把兩個標的還原成帶行號的全文，
判預期表以外的 finding 時要讀 code。
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent
EXP = OUT.parent  # .claude/experiments

SOURCES = [("py-3way", EXP / "2026-09-21-three-way-review/findings.json")]
SOURCES += [
    (f"py-r{i}", EXP / f"2026-09-21-flash-3x/runs/python--deepseek-v4-pro--{i}.json")
    for i in (1, 2, 3)
]
SOURCES += [
    (f"sh-r{i}", EXP / f"2026-09-21-flash-3x/runs/shell--deepseek-v4-pro--{i}.json")
    for i in (1, 2, 3)
]
TARGETS = {
    "pr_stats.py": EXP / "2026-09-21-flash-3x/python.diff",
    "repo_sync.sh": EXP / "2026-09-21-flash-3x/shell.diff",
}


def new_file_lines(diff_path: pathlib.Path) -> list[str]:
    """新增整檔的 diff：hunk 之後每一行都是 `+`，去掉記號就是 NEW 檔內容。"""
    lines, in_hunk = [], False
    for raw in diff_path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("@@"):
            in_hunk = True
            continue
        if in_hunk and raw.startswith("+"):
            lines.append(raw[1:])
    return lines


def main() -> None:
    sheet = ["# S 盲標單（不含 confidence、severity）", ""]
    key = {}
    n = 0
    for source, path in SOURCES:
        data = json.loads(path.read_text(encoding="utf-8"))
        findings = data if isinstance(data, list) else data.get("findings", [])
        for f in findings:
            n += 1
            fid = f"S{n:02d}"
            key[fid] = {
                "source": source,
                "confidence": float(f["confidence"]),
                "severity": f["severity"],
            }
            sheet += [
                f"## {fid} ｜ {source} ｜ `{f['path']}:{f['line']}`",
                "",
                f"**{f['title']}**",
                "",
                "existing_code:",
                "```",
                f.get("existing_code", ""),
                "```",
                "",
                f"body：{f['body']}",
                "",
                f"evidence：{f.get('evidence', '')}",
                "",
            ]
    (OUT / "label-sheet-S.md").write_text("\n".join(sheet), encoding="utf-8")
    (OUT / "key-S.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")

    tdir = OUT / "targets"
    tdir.mkdir(exist_ok=True)
    for name, diff in TARGETS.items():
        body = new_file_lines(diff)
        numbered = [f"{i:4d}  {line}" for i, line in enumerate(body, 1)]
        (tdir / f"{name}.txt").write_text("\n".join(numbered) + "\n", encoding="utf-8")
        print(f"{name}: {len(body)} 行")
    print(f"S findings: {n}")


if __name__ == "__main__":
    main()
