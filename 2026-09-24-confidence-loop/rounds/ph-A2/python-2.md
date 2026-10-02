<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell 注入（archive 使用 shell=True 且拼接 repo）、以及資源管理（export_csv 未使用 with）。此外，review_latency 依賴未提供的 timeline 欄位，可能導致 KeyError。建議優先修正安全性與正確性問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | 例外被完全吞掉，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令字串包含外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設參數 seen=[] 導致跨呼叫累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 依賴不存在的 timeline 欄位，可能引發 KeyError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> 例外被完全吞掉，導致後續程式碼在資料缺失時崩潰</summary>

_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx 狀態碼或 JSON 解析失敗時，函式會回傳 None。呼叫端（collect_authors 和 main）直接對回傳值進行索引或屬性存取，例如 pr["user"]["login"]，會引發 TypeError 或 KeyError，且錯誤訊息不明確。

建議：至少記錄例外（logging.exception），或重新拋出，讓呼叫端能處理。若希望函式回傳 None，呼叫端應檢查 None 並提供明確錯誤訊息。

**判斷依據**：diff 第 24-25 行顯示 except: pass，且後續 collect_authors 與 main 直接使用 pr["user"]["login"] 等索引。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令字串包含外部輸入，存在命令注入風險</summary>

archive 函式使用 subprocess.run 搭配 shell=True，且指令字串中包含 repo 參數（來自命令列）。攻擊者可提供惡意 repo 值（例如 `; rm -rf /`）來執行任意命令。

建議：避免使用 shell=True，改用參數列表形式，並將 repo 作為參數傳遞。若必須使用 shell，請對 repo 進行嚴格驗證或使用 shlex.quote。

**判斷依據**：diff 第 61 行顯示 shell=True 且 f-string 包含 repo。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設參數 seen=[] 導致跨呼叫累積</summary>

collect_authors 的 seen 參數預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若多次呼叫 collect_authors 而未傳入 seen，結果會累積先前呼叫的作者，導致資料污染。

建議：使用 None 作為預設值，並在函式內初始化為空串列。

**判斷依據**：diff 第 28 行顯示 seen=[]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，例外時可能洩漏資源</summary>

export_csv 使用 open 和 close 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限問題），檔案不會被關閉，造成資源洩漏。

建議：使用 with open(path, "w") as f: 確保檔案在離開區塊時關閉。

**判斷依據**：diff 第 55-59 行顯示手動 open/close。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 依賴不存在的 timeline 欄位，可能引發 KeyError</summary>

review_latency 使用 pr.get("timeline", [])，但 GitHub Pull Request API 的回應中沒有 timeline 欄位（timeline 是另一個 API 端點）。因此 events 永遠為空，函式回傳 0，無法計算實際延遲。若未來 API 變更，可能導致 KeyError。

建議：確認正確的 API 端點或欄位，或明確處理缺失情況。

**判斷依據**：diff 第 35 行顯示 pr.get("timeline", [])。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

threshold_from_env 使用 int(raw) 轉換環境變數 PR_STALE_DAYS，若使用者設定非數字字串（例如 "abc"），會拋出 ValueError 且未處理，導致程式崩潰。

建議：捕捉 ValueError 並提供有意義的錯誤訊息，或使用預設值。

**判斷依據**：diff 第 44 行顯示 int(raw)。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1456 ｜ PR #12</sub>