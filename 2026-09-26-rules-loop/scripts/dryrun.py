#!/usr/bin/env python3
"""$0 檢查：照 runner 的組法把 prompt 組出來，在送出前攔下，逐項驗證。

攔法：把 kit 模組裡的 chat_completion 換成「記下 payload 就丟例外」。main() 本來就會接住 API 的例外、
回傳 1，所以什麼都不會送出去。DEEPSEEK_API_KEY 只填假值，讓 main() 走得到組 prompt 那一段。
帶規範的走 review_with_rules.main()（跟 runner 同一條 CLI 路徑），不帶的直接走 kit 的 main()。
"""
import contextlib
import io
import json
import os
import pathlib
import re
import sys
import tempfile

sys.dont_write_bytecode = True
from common import KIT, QODO, pr_repo, split_prs  # noqa: E402
import render  # noqa: E402
import review_with_rules as rwr  # noqa: E402

dr = rwr.dr
RUBRIC = KIT / "prompts/review-rubric.md"
FILETYPE_HEADING = "## 這次改動涉及的檔案型態"
CAPTURED: dict = {}
CONFIGS = [
    {"placement": "after_diff", "fields": "full", "format": "list", "header": "h1"},
    {"placement": "before_diff", "fields": "title_objective", "format": "json", "header": "h3"},
    {"placement": "after_diff", "fields": "title", "format": "sections", "header": "h2"},
]


class Captured(Exception):
    pass


def fake_chat(base_url, api_key, payload, timeout, retries):  # noqa: ARG001
    CAPTURED["payload"] = payload
    raise Captured("dry run：到這裡就停，不送出")


def build(pr: str, cfg: dict | None) -> tuple[str, str]:
    dr.chat_completion = fake_chat
    dr.USER_TEMPLATE = rwr.ORIGINAL_TEMPLATE
    os.environ["DEEPSEEK_API_KEY"] = "sk-dryrun-placeholder-never-sent"
    os.environ.pop("REVIEW_BLOCKED_TERMS", None)
    with tempfile.TemporaryDirectory() as td, contextlib.redirect_stderr(io.StringIO()):
        kit_args = ["--diff", str(QODO / "prs" / pr / "pr.diff"), "--meta", str(QODO / "prs" / pr / "meta.json"),
                    "--rubric", str(RUBRIC), "--out", f"{td}/o.md", "--findings-out", f"{td}/o.json",
                    "--rules-dir", str(KIT / "prompts/rules")]
        if cfg:
            cfg_path = pathlib.Path(td) / "cfg.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            sys.argv = ["review_with_rules.py", "--rules-config", str(cfg_path), "--repo", pr_repo(pr)] + kit_args
            rwr.main()
        else:
            sys.argv = [dr.__file__] + kit_args
            dr.main()
    msgs = CAPTURED.pop("payload")["messages"]
    return msgs[0]["content"], msgs[1]["content"]


def squash(s: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def main() -> int:
    def paths(pr: str) -> list[str]:
        return re.findall(r"^diff --git a/.+ b/(.+)$", (QODO / "prs" / pr / "pr.diff").read_text(encoding="utf-8"), re.M)

    def wants_filetype(pr: str) -> bool:
        return any(re.search(pat, p) for pat, _ in dr.RULE_MAP for p in paths(pr))

    tune = split_prs("tune")
    picks = [next(p for p in tune if wants_filetype(p)), next(p for p in tune if not wants_filetype(p))]
    rubric_text = dr.load_text(str(RUBRIC))
    fails = 0
    for pr in picks:
        sys0, user0 = build(pr, None)
        for cfg in CONFIGS:
            sys1, user1 = build(pr, cfg)
            block, ids = render.render(pr_repo(pr), cfg)
            pos = user1.find(block)
            diff_start = user1.find("```diff\n")
            diff_end = user1.find("\n```", diff_start + 8)
            placed = (pos > diff_end) if cfg["placement"] == "after_diff" else (0 <= pos < user1.find("## Unified diff"))
            checks = [
                ("system prompt 沒變，就是 rubric 原文", sys1 == sys0 == rubric_text),
                ("規範整段逐字出現在 user message", pos >= 0),
                (f"位置正確（{cfg['placement']}）", placed),
                ("拿掉規範後，跟不附規範的 prompt 一模一樣", squash(user1.replace(block, "")) == squash(user0)),
                ("依檔案型態的補充規則照舊", (FILETYPE_HEADING in user1) == (FILETYPE_HEADING in user0) == wants_filetype(pr)),
                # 編號的寫法依格式而定：list／sections 是 [R01]，json 是 "id": "R01"；每一條都要在
                ("引用編號的要求在，每一條規則的編號也都在", render.CITE in user1 and all(
                    (f'"id": "{rid}"' if cfg["format"] == "json" else f"[{rid}]") in user1 for rid in ids)),
            ]
            if cfg["format"] == "json":
                # 從規範那一段開始找：user message 裡第一個 ```json 是 PR metadata，不是規則
                m = re.search(r"```json\n(.*?)\n```", user1[pos:], re.S) if pos >= 0 else None
                try:
                    parsed = json.loads(m.group(1)) if m else None
                except json.JSONDecodeError:
                    parsed = None
                checks.append(("JSON 整段解析得回來（大括號沒被 str.format 吃掉）",
                               isinstance(parsed, list) and [x["id"] for x in parsed] == list(ids)))
            bad = [name for name, ok in checks if not ok]
            fails += len(bad)
            print(f"{'PASS' if not bad else 'FAIL'} {pr:<14} {cfg['placement']:<11} {cfg['fields']:<15} "
                  f"{cfg['format']:<8} {cfg['header']}｜{len(ids)} 條、多 {len(user1) - len(user0)} 字元"
                  + (f"｜失敗：{bad}" if bad else ""))
    print(f"\n檢查的 PR：{picks}（第一個會觸發依檔案型態的補充規則，第二個不會）")
    print("全部通過" if not fails else f"{fails} 項失敗")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
