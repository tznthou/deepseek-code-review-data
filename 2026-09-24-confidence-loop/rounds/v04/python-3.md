<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確關閉（export_csv）。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | 例外被吞掉，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:38` | review_latency 對空事件列表回傳 0，可能誤導 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> 例外被吞掉，導致後續程式碼在資料缺失時崩潰</summary>

_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx 狀態碼、或 JSON 解析失敗時，函式會回傳 None。呼叫端（collect_authors 和 main）直接使用回傳值，例如 pr["user"]["login"]，會導致 TypeError 或 KeyError，且沒有明確的錯誤訊息。

建議：
- 至少記錄例外（logging.exception）並重新拋出，或回傳一個明確的錯誤物件。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 在呼叫端處理 None 的情況。

**判斷依據**：diff 第 24 行：`except:` 後接 `pass`，且函式無回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入，存在指令注入風險</summary>

archive 函式使用 subprocess.run 並設定 shell=True，且指令字串包含 repo 和 path 參數。repo 來自命令列參數（使用者可控），若包含特殊字元（如分號、管道、反引號），可注入任意指令。

建議：避免使用 shell=True，改用參數列表形式，例如：
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])

**判斷依據**：diff 第 75 行：`shell=True` 且指令字串由外部輸入拼接。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫累積</summary>

collect_authors 函式的參數 seen 預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。雖然目前程式碼中只呼叫一次，但若未來重複呼叫，會累積先前結果，造成非預期行為。

建議：將預設值改為 None，並在函式內初始化為空串列。

**判斷依據**：diff 第 28 行：`seen=[]` 為可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，可能洩漏資源</summary>

export_csv 函式使用 open 開啟檔案，但未使用 with 或 try/finally 確保關閉。若寫入過程中發生例外，檔案可能未關閉，造成資源洩漏。

建議：使用 with open(path, "w") as f: 來管理檔案。

**判斷依據**：diff 第 71-74 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

threshold_from_env 函式將環境變數 PR_STALE_DAYS 轉換為整數，但未處理 ValueError。若使用者設定非數字值，程式會崩潰。

建議：使用 try/except 捕捉轉換錯誤，並提供有意義的錯誤訊息或回退到預設值。

**判斷依據**：diff 第 40 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:38</code> review_latency 對空事件列表回傳 0，可能誤導</summary>

review_latency 函式在 events 為空時回傳 0，這可能被解讀為「零延遲」，但實際上可能是資料缺失。建議回傳 None 或拋出例外，讓呼叫端處理。

**判斷依據**：diff 第 33-34 行：空列表回傳 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 3200) ｜ completion tokens 1429 ｜ PR #12</sub>