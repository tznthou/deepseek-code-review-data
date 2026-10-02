#!/usr/bin/env python3
"""把 repo 規範附進 user message，其餘照原樣跑 kit 的 deepseek_review.py。

kit 的檔案一行都不改：這裡 import 它，只換掉 USER_TEMPLATE 這個模組層常數，main() 執行時用的就是新的。
system prompt（rubric）、依檔案型態附加的補充規則、禁用詞掃描、API 呼叫、輸出格式，全部走 kit 原本的 code。

用法：review_with_rules.py --rules-config <設定.json> --repo <repo 名> <deepseek_review.py 原本的參數…>
"""
import argparse
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
from common import KIT  # noqa: E402

sys.path.insert(0, str(KIT / ".github/scripts"))
import deepseek_review as dr  # noqa: E402
import render  # noqa: E402

ORIGINAL_TEMPLATE = dr.USER_TEMPLATE
DIFF_HEADING = "## Unified diff"


def patch_template(block: str, placement: str) -> str:
    """回傳插好規範的新 template。block 裡的大括號要跳脫，因為 kit 用 str.format 填 template。"""
    esc = block.replace("{", "{{").replace("}", "}}")
    tpl = ORIGINAL_TEMPLATE
    if placement == "after_diff":
        # 接在 diff 後面：前綴（system + metadata + diff）不變，吃得到 context caching。
        # 依檔案型態附加的補充規則仍由 kit 接在最後面。
        return tpl.rstrip("\n") + "\n\n" + esc
    i = tpl.index(DIFF_HEADING)
    return tpl[:i] + esc + "\n" + tpl[i:]


def main() -> int:
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--rules-config", required=True)
    ap.add_argument("--repo", required=True)
    ours, rest = ap.parse_known_args()
    cfg = render.check(json.loads(pathlib.Path(ours.rules_config).read_text(encoding="utf-8")))
    block, ids = render.render(ours.repo, cfg)
    dr.USER_TEMPLATE = patch_template(block, cfg["placement"])
    dr.log(f"[info] repo 規範：repo={ours.repo}、{len(ids)} 條、{len(block)} 字元、placement={cfg['placement']}、"
           f"sha256={hashlib.sha256(block.encode('utf-8')).hexdigest()[:12]}")
    sys.argv = [dr.__file__] + rest
    return dr.main()


if __name__ == "__main__":
    sys.exit(main())
