#!/usr/bin/env python3
"""Guard：每一輪的 rubric 在送出去之前先過這關（外部、機械式的 pass/fail）。

1. 沒有寫給人看的元評論標記（同 tools/selftest.py 的那組字）
2. 輸出格式那段的 JSON 欄位全部還在（少一個，下游的解析與定位就會壞）
3. 不含標的專屬字串——擋「照著考卷調 prompt」
4. Guard target（標的、規則、harness、reviewer、kit 正在用的 rubric）的 hash 跟啟動快照一致

用法：guard.py <rubric 路徑>        # 檢查
      guard.py --snapshot           # 建立啟動快照（只在 loop 開跑前做一次）
"""
import hashlib
import pathlib
import re
import sys

LOOP = pathlib.Path(__file__).resolve().parents[1]
KIT = LOOP.parents[2]
SNAP = LOOP / "guard-snapshot.txt"

META = re.compile(r"(實測無效|待驗證|TODO|FIXME|這條沒用|先留著)")
SCHEMA_KEYS = ["summary", "verdict", "findings", "path", "line", "side", "severity",
               "confidence", "title", "body", "existing_code", "evidence"]
TARGET_TOKENS = [
    "pr_stats", "repo_sync", "release_notes", "collect_authors", "review_latency",
    "threshold_from_env", "export_csv", "_fetch", "init_db", "sync_one", "run_hook",
    "cleanup_cache", "max_items", "list_tags", "commits_between", "load_config",
    "PR_STALE_DAYS", "NOTES_MAX", "NOTES_WEBHOOK", "post-sync", ".release-notes.json",
    "T000/B000", "hooks.example.com",
]


def guard_targets() -> list[pathlib.Path]:
    files = sorted((LOOP / "targets").glob("*.diff")) + sorted((LOOP / "targets").glob("meta-*.json"))
    files += [LOOP / "targets/src/sandbox/release_notes.py", LOOP / "expected-rules.json"]
    files += sorted((LOOP / "scripts").glob("*.py"))
    files += [KIT / ".github/scripts/deepseek_review.py", KIT / ".github/scripts/locate.py",
              KIT / "prompts/review-rubric.md"]
    files += sorted((KIT / "prompts/rules").glob("*.md"))
    return files


def digest(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    if sys.argv[1:] == ["--snapshot"]:
        if SNAP.exists():
            sys.exit("快照已經存在，不覆寫（loop 期間 Guard target 不可改）")
        SNAP.write_text("".join(f"{digest(p)}  {p.relative_to(KIT)}\n" for p in guard_targets()),
                        encoding="utf-8")
        print(f"快照：{len(guard_targets())} 個檔")
        return

    text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    fails = []
    if META.search(text):
        fails.append(f"元評論標記：{META.search(text).group(0)}")
    fails += [f"輸出格式少了欄位 \"{k}\"" for k in SCHEMA_KEYS if f'"{k}"' not in text]
    fails += [f"含標的專屬字串：{t}" for t in TARGET_TOKENS if t in text]
    snap = {line.split("  ", 1)[1]: line.split("  ", 1)[0]
            for line in SNAP.read_text(encoding="utf-8").splitlines() if line.strip()}
    for p in guard_targets():
        rel = str(p.relative_to(KIT))
        if snap.get(rel) != digest(p):
            fails.append(f"Guard target 被改或是新檔：{rel}")
    for rel in set(snap) - {str(p.relative_to(KIT)) for p in guard_targets()}:
        fails.append(f"Guard target 不見了：{rel}")
    if fails:
        print("GUARD FAIL\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("GUARD PASS")


if __name__ == "__main__":
    main()
