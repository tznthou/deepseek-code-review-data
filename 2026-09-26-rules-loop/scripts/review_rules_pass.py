#!/usr/bin/env python3
"""D1 的第二次呼叫：v01 的規範呈現，後面再接一段「這一次 review 的範圍」。其餘跟 v01 完全一樣。

review_with_rules.py 是 loop 凍結的 Guard target，這裡只 import 它：用它的 patch_template 把
「規範 ＋ 範圍說明」當成一整段插進 kit 的 USER_TEMPLATE。順序：metadata → diff → 規範（含標編號那句）
→ 範圍說明 → kit 依檔案型態附加的補充規則。到 diff 為止跟一般 pass 逐字相同，吃得到快取。
範圍說明只講分工（資訊），不寫「確定才報」這類要求自我約束的話（render.py 開頭註解：實測無效）。

用法同 review_with_rules.py：review_rules_pass.py --rules-config <設定.json> --repo <repo 名> <kit 參數…>
"""
import argparse
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
import render  # noqa: E402
import review_with_rules as rwr  # noqa: E402

dr = rwr.dr
SCOPE = ("## 這一次 review 的範圍\n\n"
         "這一次只檢查上面的 repo 規範：找出這次改動違反了哪幾條。一般的程式問題由另一次 review 負責。\n")


def compose(block: str) -> str:
    """規範那段接範圍說明。dryrun_d1.py 的探針會換掉這個函式，驗證檢查抓得到放錯、漏放。"""
    return block + "\n" + SCOPE


def main() -> int:
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--rules-config", required=True)
    ap.add_argument("--repo", required=True)
    ours, rest = ap.parse_known_args()
    cfg = render.check(json.loads(pathlib.Path(ours.rules_config).read_text(encoding="utf-8")))
    block, ids = render.render(ours.repo, cfg)
    text = compose(block)
    dr.USER_TEMPLATE = rwr.patch_template(text, cfg["placement"])
    dr.log(f"[info] repo 規範＋範圍說明：repo={ours.repo}、{len(ids)} 條、{len(text)} 字元、placement={cfg['placement']}、"
           f"sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]}")
    sys.argv = [dr.__file__] + rest
    return dr.main()


if __name__ == "__main__":
    sys.exit(main())
