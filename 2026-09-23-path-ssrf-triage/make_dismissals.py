"""產生 27 筆 won't fix 的 dismiss request body, 並檢查 GitHub 的 280 字元上限。

用法: python3 make_dismissals.py  → 寫出 dismiss/<n>.json, 印出每筆長度
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ARGV_RULES_DIR = (
    "rules_dir 來自 --rules-dir：04 裡是 workflow 寫死的 .kit/prompts/rules，本機是 review-local.sh "
    "的 $SCRIPT_DIR/prompts/rules。diff 只決定從 RULE_MAP 挑哪個常數檔名，不進路徑字串。"
    "設值的人本來就有同等權限，不構成威脅。"
)
LOAD_TEXT = (
    "load_text 的路徑來自 --diff／--meta／--rubric／--rules-dir：04 裡前兩個是寫死的 in/pr.diff、"
    "in/meta.json，--rubric 是 caller 的 rubric-path input 或 kit 內建檔；本機是操作者自己。"
    "artifact 內容只被讀、不組路徑。⚠️ 共用 helper：日後把不受信任的資料當路徑傳進來要重新評估。"
)
ARGV_OUT = (
    "輸出路徑來自 --out／--findings-out：04 裡是 workflow 寫死的 review.md、findings.json，"
    "本機是 review-local.sh 的 $TMPDIR 路徑。設值的人本來就有同等權限，不構成威脅。"
)
STEP_SUMMARY = (
    "GITHUB_STEP_SUMMARY 由 Actions runner 設定，PR 作者與 caller 都碰不到；本機沒設就不寫。"
)
BASE_URL_REVIEW = (
    "URL 來自 --base-url／DEEPSEEK_BASE_URL，預設寫死 api.deepseek.com。04 兩者都沒設"
    "（reusable 不繼承 caller 的 env），固定走預設值；本機是操作者自己。能改這個值的人本來就拿得到 key。"
)
POST_REVIEW = (
    "路徑來自 --review／--findings／--diff：04 裡是 workflow 寫死的 review.md、findings.json、"
    "in/pr.diff。findings.json 的內容（模型輸出）只被解析，其中的 path 只當 API 參數貼留言，不拿來開檔。"
    "設值的人本來就有同等權限。"
)
DSH = (
    "本機專用工具，沒有任何 workflow 呼叫它。--app 是操作者自己指定的 app 路徑"
    "（預設 /Applications/Cherry Studio.app），自己對自己做 path injection 不構成威脅。"
)
DSH_ASAR = DSH + "另一段路徑來自已安裝 app 的 asar header——能竄改它的人已經能在這台機器上執行程式。"
EVAL_CACHE = (
    "快取路徑來自環境變數 AACR_CACHE，預設 tools/eval/dataset.json。eval-filter.yml 沒設它、走預設值，"
    "本機是操作者自己。資料集的欄位不進檔案路徑。"
)
EVAL_OUT = (
    "輸出路徑來自環境變數 EVAL_SET_OUT，預設 tools/eval/eval_set.json。eval-filter.yml 沒設它、走預設值，"
    "本機是操作者自己。資料集的欄位不進檔案路徑。"
)
EVAL_PROMPT = (
    "--filter-prompt 在 eval-filter.yml 來自 workflow_dispatch input：能觸發 dispatch 的人要有 write 權限，"
    "本來就能直接改 workflow；本機是操作者自己。不構成權限提升。"
)
EVAL_ARGV = (
    "--eval-set／--out 在 eval-filter.yml 沒有傳，走 tools/eval/ 下的預設路徑；本機是操作者自己。"
    "設值的人本來就有同等權限，不構成威脅。"
)
BASE_URL_EVAL = (
    "BASE_URL 來自環境變數 DEEPSEEK_BASE_URL，預設寫死 api.deepseek.com；eval-filter.yml 沒設它，"
    "本機是操作者自己。能改這個值的人本來就拿得到 key。"
)

COMMENTS = {
    27: ARGV_RULES_DIR,
    28: LOAD_TEXT, 29: LOAD_TEXT,
    30: ARGV_OUT, 31: ARGV_OUT, 32: ARGV_OUT, 33: ARGV_OUT,
    34: STEP_SUMMARY,
    40: BASE_URL_REVIEW,
    35: POST_REVIEW, 36: POST_REVIEW, 37: POST_REVIEW, 38: POST_REVIEW,
    17: DSH, 18: DSH, 19: DSH_ASAR, 20: DSH, 22: DSH,
    14: EVAL_CACHE, 15: EVAL_CACHE, 16: EVAL_CACHE,
    21: EVAL_OUT,
    23: EVAL_PROMPT,
    24: EVAL_ARGV, 26: EVAL_ARGV,
    25: STEP_SUMMARY,
    39: BASE_URL_EVAL,
}


def main():
    out_dir = os.path.join(HERE, "dismiss")
    os.makedirs(out_dir, exist_ok=True)
    worst = 0
    for num in sorted(COMMENTS):
        comment = COMMENTS[num]
        worst = max(worst, len(comment))
        body = {"state": "dismissed", "dismissed_reason": "won't fix", "dismissed_comment": comment}
        with open(os.path.join(out_dir, f"{num}.json"), "w", encoding="utf-8") as fh:
            json.dump(body, fh, ensure_ascii=False)
        flag = "OK " if len(comment) <= 280 else "TOO LONG"
        print(f"#{num:<3} {len(comment):>3} {flag}")
    print(f"alerts: {len(COMMENTS)}  longest: {worst}")


if __name__ == "__main__":
    main()
