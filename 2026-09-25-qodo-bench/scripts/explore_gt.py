#!/usr/bin/env python3
"""摸清 Qodo GT 的語意：start_line 是哪一側的行號？片段落在 + 行、context 行、還是 - 行？

只讀本地檔案，不呼叫任何 API。
"""
import collections
import json
import pathlib
import re
import sys

EXP = pathlib.Path(__file__).resolve().parents[1]
KIT = EXP.parents[2]
sys.path.insert(0, str(KIT / ".github/scripts"))
import locate  # noqa: E402

HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
GIT = re.compile(r"^diff --git a/(.+?) b/(.+)$")


def parse(diff: str):
    """回傳 {path: {"new": {line: text}, "old": {line: text}, "kind_new": {line: '+'|' '}}}"""
    files = {}
    cur = None
    o = n = 0
    for raw in diff.splitlines():
        m = GIT.match(raw)
        if m:
            cur = files.setdefault(m.group(2), {"new": {}, "old": {}, "kind_new": {}})
            continue
        if cur is None or raw.startswith(("+++ ", "--- ")):
            continue
        h = HUNK.match(raw)
        if h:
            o, n = int(h.group(1)), int(h.group(2))
            continue
        if raw.startswith("+"):
            cur["new"][n] = raw[1:]; cur["kind_new"][n] = "+"; n += 1
        elif raw.startswith("-"):
            cur["old"][o] = raw[1:]; o += 1
        elif raw.startswith(" "):
            cur["new"][n] = raw[1:]; cur["kind_new"][n] = " "
            cur["old"][o] = raw[1:]; o += 1; n += 1
    return files


def first_line(snippet: str) -> str:
    for ln in snippet.splitlines():
        s = locate.normalize_ws(ln)
        if len(s) >= locate.MIN_SNIPPET_LEN:
            return s
    return ""


def main() -> None:
    rows = [json.loads(l) for l in (EXP / "data/bench.jsonl").read_text().splitlines() if l.strip()]
    stats = collections.Counter()
    examples = collections.defaultdict(list)
    for r in rows:
        parts = r["pr_url_to_review"].rstrip("/").split("/")
        key = f"{parts[-3]}-{parts[-1]}"
        diff = (EXP / "prs" / key / "pr.diff").read_text(encoding="utf-8")
        files = parse(diff)
        for i, g in enumerate(r["issues"]):
            fl = first_line(g.get("problematic_code_snippet") or "")
            path = g.get("file_path")
            kind = "rule" if (g.get("rule_name") or "").strip() else "func"
            f = files.get(path) if path else None
            # 1) 路徑在不在 diff 裡
            if path and f is None:
                stats[(kind, "路徑不在 diff")] += 1
                examples["路徑不在 diff"].append((key, path))
                continue
            if not path:
                stats[(kind, "沒有 file_path")] += 1
            # 2) 片段首行在哪一側
            where = []
            cands = [f] if f else list(files.values())
            for ff in cands:
                if any(fl and fl in locate.normalize_ws(t) for ln, t in ff["new"].items() if ff["kind_new"][ln] == "+"):
                    where.append("+")
                if any(fl and fl in locate.normalize_ws(t) for ln, t in ff["new"].items() if ff["kind_new"][ln] == " "):
                    where.append("ctx")
                if any(fl and fl in locate.normalize_ws(t) for t in ff["old"].values()):
                    where.append("-")
            w = "+".join(sorted(set(where))) if where else ("片段太短" if not fl else "找不到")
            stats[(kind, f"片段在 {w}")] += 1
            # 3) start_line 對得上哪一側
            sl = g.get("start_line")
            if f and isinstance(sl, int) and fl:
                new_ok = fl in locate.normalize_ws(f["new"].get(sl, ""))
                old_ok = fl in locate.normalize_ws(f["old"].get(sl, ""))
                near_new = any(fl in locate.normalize_ws(f["new"].get(x, "")) for x in range(sl - 3, sl + 4))
                stats[("行號", "start_line=新檔同行" if new_ok else "start_line=舊檔同行" if old_ok
                       else "新檔±3 內" if near_new else "對不上")] += 1
    for k, v in sorted(stats.items()):
        print(f"{k[0]:<5} {k[1]:<24} {v}")
    print("例：", examples["路徑不在 diff"][:5])


if __name__ == "__main__":
    main()
