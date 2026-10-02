# CodeQL path-injection 25 / full-ssrf 2 的分流 — 2026-09-23

> 判準與逐筆預期在 `triage-criteria.md`, 定稿 07:46:06Z, **讀 SARIF flow 與 code 之前**。
> 標的: main `ff63650`, analysis `1823093375`。

## 結論: 27 筆全部 won't fix, 0 筆成立

SARIF 的 27 條 flow, **source 全是 argv (`parse_args()`) 或環境變數**, 沒有一條從檔案內容起跳。
CodeQL 只畫得出它建模的 source, 所以另外逐行看了每個 sink 組路徑時有沒有混進它沒追的資料:

| 群組 | alert | sink 的值從哪來 | 誰設的 |
|---|---|---|---|
| `deepseek_review.py` argv | #27 #28 #29 #30 #31 #32 #33 | `--diff` `--meta` `--rubric` `--rules-dir` `--out` `--findings-out` | `04`: workflow 字面值 (`in/pr.diff` 等), `--rubric` = caller 的 `rubric-path` 或 kit 內建; 本機: `review-local.sh` 的 `$TMPDIR`/`$SCRIPT_DIR` |
| step summary | #34 #25 | `GITHUB_STEP_SUMMARY` | Actions runner |
| base URL (ssrf) | #40 #39 | `--base-url` / `DEEPSEEK_BASE_URL` | `04` 與 `eval-filter.yml` 都沒設 → 寫死的預設值 (reusable 不繼承 caller 的 env); 本機: 操作者 |
| `post_review.py` argv | #35 #36 #37 #38 | `--review` `--findings` `--diff` | `04`: workflow 字面值 |
| `check-dsh-version.py` | #17 #18 #19 #20 #22 | `--app` (+ #19 的 asar header 檔名) | 本機操作者; **沒有任何 workflow 呼叫它** |
| `build_eval_set.py` | #14 #15 #16 #21 | `AACR_CACHE` / `EVAL_SET_OUT` | `eval-filter.yml` 沒設 → 預設路徑; 本機: 操作者 |
| `eval_filter.py` argv | #23 #24 #26 | `--filter-prompt` `--eval-set` `--out` | `--filter-prompt` = `workflow_dispatch` input (要 write 權限); 其餘沒傳 → 預設 |

**不受信任的資料只被當內容讀**: artifact 的 diff / `meta.json` 讀進來送 API; `findings.json` (模型輸出) 被解析, 其中的 `path` 只當 API 參數貼留言;
diff 只決定從 `RULE_MAP` 挑哪個**常數**檔名 (`deepseek_review.py:154`), 不進路徑字串。

## 預期 vs 實際

| | 預期 | 實際 |
|---|---|---|
| won't fix | ≥ 21 | **27** |
| 成立候選 | 0–6, 三處 | **0** |
| `deepseek_review.py:142-164` | 不確定 (diff 內容 → 規則檔路徑?) | diff 只選常數檔名 |
| `post_review.py:196-197` | 不確定 (模型輸出的 path → 開檔?) | `--diff` 是字面值 `in/pr.diff`; 模型的 path 只當 API 參數 |
| `build_eval_set.py:148` | **可能成立** (資料集欄位 → 路徑?) | **預期錯**: `EVAL_SET_OUT` 環境變數, 資料集欄位不進檔案路徑 |
| #34 / #25 | argv 輸出路徑 | `GITHUB_STEP_SUMMARY` (同屬信任來源, 來源猜錯) |

⚠️ 「27 條 flow 沒有一條從檔案內容起跳」分不出是「Python 的 local threat model 沒把讀檔當 source」還是「本來就沒有這種 flow」。**這份資料不支持任一方向**, 不要引用成「CodeQL 不追讀檔」。

## dismiss

- reason 一律 `won't fix` (不選 false positive: local threat model 是我們自己開的, CodeQL 的資料流陳述是對的, 只是設值的人本來就有同等權限)
- 理由原文: `make_dismissals.py` → `dismiss/<n>.json` (最長 199 字元, 上限 280); 涵蓋的編號與 open alert 清單逐筆比對過 (27/27)
- 為什麼 dismiss 而不是留著: open 回到 0, 下一筆新的才會顯眼。留著 27 筆, 第 28 筆來了沒有人會看到 (#19 之後 1.5 天沒人發現就是這個形狀)

## 執行結果 (2026-09-23, 時間皆 UTC)

- **dismiss**: 08:01:41–08:02:10, 27 筆全部 `won't fix`。事後查: open 0、`won't fix` 27、`dismissed_comment` 與 `dismiss/<n>.json` 逐字相符 27/27
- **PR #29** merge 08:12 → main `f45fa47`: README §8 那句「27 筆的汙染源是 workflow 寫死的 argv」改寫成實際結果, CHANGELOG `[Unreleased]` 補一條。CI 全綠, AI review 0 筆
- **merge 後複驗**: main 兩次 CodeQL 分析 (`f45fa47` 08:12:57、`12bc089` 08:15:09) results_count 都是 30 (= 本批 27 + #41/#42/#44), open 0 → **dismiss 狀態在新分析上有延續**
- 同一批 `04` (真 key) 是 `v1.3.1` 第一次在真 API 上跑 (`HEAD is now at ff63650`), findings=0 → `locate.py` 的新 code 沒走到

## 範圍外的觀察 (記下, 沒有動)

1. **dismiss 是以 sink 為單位**。日後若有新的不受信任來源流進同一個 sink (尤其共用 helper `load_text`, #28/#29), 會沿用已 dismiss 的 alert 還是跳新的 —— **未驗證**。所以 #28/#29 的理由裡寫明了前提
2. `build_eval_set.py` 把資料集的 `pr_url` 切成 `repo`/`num` 塞進 `gh api repos/{repo}/pulls/{num}` (list 參數, 不經 shell)。不是檔案路徑、不是這批 alert。最壞是用操作者的 token GET 另一個 GitHub API endpoint, 回應只有長得像 diff 的部分會被留下 → 實質丟棄。資料集 URL 是 `resolve/main` (可變)。影響可忽略
3. `reusable-ai-review-post.yml:211-213` 把 `inputs.min-severity` 等值直接內插進 run block, 而上一個 step 的註解寫「值一律走 env」。值是 caller 自己給的 (`min-severity` 是 string, 另兩個 number), 不跨權限邊界 → **不是漏洞, 是與自己的規則不一致**

## 檔案

| 檔 | 內容 |
|---|---|
| `triage-criteria.md` | 判準 + 逐筆預期, 定稿 07:46:06Z |
| `analysis-1823093375.sarif` | main `ff63650` 的完整 SARIF (30 results = open 27 + 已 dismiss 3) |
| `alerts-open.tsv` | 27 筆 open alert (number / rule / path / line) |
| `flows.py` → `flows.txt` | 每筆 alert 的 source → sink 攤平 |
| `make_dismissals.py` → `dismiss/` | 27 份 dismiss request body |
