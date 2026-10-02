#!/usr/bin/env python3
"""D1 的 $0 檢查：v01 與 D1 的 prompt 各組一次，在送出前攔下，驗證兩者只差「範圍說明」那一段。

攔法同 dryrun.py：chat_completion 換成記下 payload 就丟例外，main() 會接住、回傳 1，什麼都不送出。
v01 走 review_with_rules.main()、D1 走 review_rules_pass.main()，跟 runner 同一條 CLI 路徑。
探針（每次都跑）：把 compose 換成「漏掉範圍說明」與「範圍說明放在規範前面」，對應的檢查必須 FAIL，
否則代表檢查本身抓不到錯，正常版的 PASS 也不算數。
"""
import contextlib
import io
import json
import os
import re
import sys
import tempfile

sys.dont_write_bytecode = True
from common import KIT, LOOP, QODO, pr_repo, split_prs  # noqa: E402
import render  # noqa: E402
import review_rules_pass as rrp  # noqa: E402

rwr = rrp.rwr
dr = rrp.dr
RUBRIC = KIT / "prompts/review-rubric.md"
CFG_PATH = LOOP / "iterations/v01.json"
FILETYPE_HEADING = "## 這次改動涉及的檔案型態"
CAPTURED: dict = {}
REAL_COMPOSE = rrp.compose
PROBES = {
    "漏掉範圍說明": (lambda block: block, "範圍說明逐字出現剛好一次"),
    "範圍說明放在規範前面": (lambda block: rrp.SCOPE + "\n" + block, "範圍說明在規範（含標編號那句）後面"),
}


class Captured(Exception):
    pass


def fake_chat(base_url, api_key, payload, timeout, retries):  # noqa: ARG001
    CAPTURED["payload"] = payload
    raise Captured("dry run：到這裡就停，不送出")


def build(pr: str, entry) -> tuple[str, str]:
    dr.chat_completion = fake_chat
    dr.USER_TEMPLATE = rwr.ORIGINAL_TEMPLATE
    os.environ["DEEPSEEK_API_KEY"] = "sk-dryrun-placeholder-never-sent"
    os.environ.pop("REVIEW_BLOCKED_TERMS", None)
    with tempfile.TemporaryDirectory() as td, contextlib.redirect_stderr(io.StringIO()):
        sys.argv = ["dryrun", "--rules-config", str(CFG_PATH), "--repo", pr_repo(pr),
                    "--diff", str(QODO / "prs" / pr / "pr.diff"), "--meta", str(QODO / "prs" / pr / "meta.json"),
                    "--rubric", str(RUBRIC), "--out", f"{td}/o.md", "--findings-out", f"{td}/o.json",
                    "--rules-dir", str(KIT / "prompts/rules")]
        entry()
    msgs = CAPTURED.pop("payload")["messages"]
    return msgs[0]["content"], msgs[1]["content"]


def squash(s: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def wants_filetype(pr: str) -> bool:
    paths = re.findall(r"^diff --git a/.+ b/(.+)$", (QODO / "prs" / pr / "pr.diff").read_text(encoding="utf-8"), re.M)
    return any(re.search(pat, p) for pat, _ in dr.RULE_MAP for p in paths)


def checks(pr: str, rubric_text: str) -> list[tuple[str, bool]]:
    sys0, user0 = build(pr, rwr.main)
    sys1, user1 = build(pr, rrp.main)
    block, _ids = render.render(pr_repo(pr), json.loads(CFG_PATH.read_text(encoding="utf-8")))
    b0, b1, s, ft = user0.find(block), user1.find(block), user1.find(rrp.SCOPE), user1.find(FILETYPE_HEADING)
    return [
        ("system prompt 沒變，就是 rubric 原文", sys1 == sys0 == rubric_text),
        ("v01 與 D1 都有整段規範", b0 >= 0 and b1 >= 0),
        ("範圍說明逐字出現剛好一次", user1.count(rrp.SCOPE) == 1),
        ("範圍說明在規範（含標編號那句）後面", b1 >= 0 and s >= b1 + len(block)),
        ("範圍說明在依檔案型態的補充規則前面", ft < 0 or 0 <= s < ft),
        ("規範之前（metadata＋diff）跟 v01 逐字相同", b0 >= 0 and b1 >= 0 and user1[:b1] == user0[:b0]),
        ("拿掉範圍說明後，跟 v01 的 prompt 一模一樣", squash(user1.replace(rrp.SCOPE, "")) == squash(user0)),
        ("依檔案型態的補充規則照舊", (FILETYPE_HEADING in user1) == (FILETYPE_HEADING in user0) == wants_filetype(pr)),
    ]


def main() -> int:
    pool = split_prs("holdout") + split_prs("tune")
    picks = [p for p in (next((p for p in pool if wants_filetype(p)), None),
                         next((p for p in split_prs("holdout") if not wants_filetype(p)), None)) if p]
    rubric_text = dr.load_text(str(RUBRIC))
    bad_total = 0

    rrp.compose = REAL_COMPOSE
    for pr in picks:
        res = checks(pr, rubric_text)
        bad = [n for n, ok in res if not ok]
        bad_total += len(bad)
        print(f"{'PASS' if not bad else 'FAIL'} {pr:<16} 補充規則={'有' if wants_filetype(pr) else '無'}"
              + (f"｜失敗：{bad}" if bad else f"｜{len(res)} 項全過"))

    probe_ok = True
    for name, (fake, must_fail) in PROBES.items():
        rrp.compose = fake
        res = dict(checks(picks[-1], rubric_text))
        caught = not res[must_fail]
        probe_ok &= caught
        print(f"探針「{name}」：「{must_fail}」{'有抓到（FAIL）' if caught else '沒抓到——檢查本身有問題'}"
              f"｜其他 FAIL：{[n for n, ok in res.items() if not ok and n != must_fail]}")
    rrp.compose = REAL_COMPOSE

    print(f"\n檢查的 PR：{picks}")
    ok = not bad_total and probe_ok
    print("全部通過，探針也都抓到" if ok else f"正常版 {bad_total} 項失敗；探針{'正常' if probe_ok else '沒抓到'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
