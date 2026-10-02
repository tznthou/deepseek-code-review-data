<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確關閉（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議優先修正。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int(raw) 未處理轉換失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 pr 一定有 additions、changed_files、title 欄位 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（如 `collect_authors` 和 `main`）直接使用回傳值，例如 `pr["user"]["login"]`，當 `pr` 為 `None` 時會拋出 `TypeError`，造成程式崩潰。建議至少記錄錯誤並重新拋出，或讓呼叫端檢查回傳值。

**判斷依據**：diff 第 24 行 `except: pass` 吞掉所有例外，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 74 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（外部輸入）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`，導致任意指令執行。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 80 行使用 `shell=True` 且 f-string 包含外部輸入 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，會在多次呼叫間共用同一個 list。如果這個函式被呼叫多次（例如在同一個程序內處理多個 repo），作者名單會不斷累積，導致結果不正確。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 28 行定義了可變預設值 `seen=[]`，且函式內對其進行 `append` 操作（第 30 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限問題），檔案不會被關閉，造成資源洩漏。建議使用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 62-66 行顯示手動開啟和關閉檔案，沒有使用 context manager。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int(raw) 未處理轉換失敗</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若該值不是有效整數（例如 "abc"），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 44 行直接轉換環境變數為整數，沒有錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 一定有 additions、changed_files、title 欄位</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 `_fetch` 可能回傳 `None` 或 API 回應缺少這些欄位（例如權限不足或 API 變更），導致 `KeyError` 或 `TypeError`。建議先驗證資料結構或使用 `.get()` 提供預設值。

**判斷依據**：diff 第 50-55 行直接存取字典鍵，沒有檢查鍵是否存在。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at</summary>

`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但若事件物件缺少 `created_at` 欄位（例如 API 回應格式變更），會拋出 `KeyError`。建議使用 `.get()` 或驗證結構。

**判斷依據**：diff 第 35-36 行直接存取鍵，沒有防禦性檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1754 ｜ PR #12</sub>