<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險集中在錯誤處理、安全性與資源管理：`_fetch` 吞掉所有例外且回傳 `None`，後續直接取值會造成未處理的例外；`archive` 使用 `shell=True` 且指令由外部輸入拼接，存在命令注入風險；`export_csv` 未使用 `with` 管理檔案；`collect_authors` 使用可變預設值且未回傳新串列。建議先修補這些問題再合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | `_fetch` 吞掉所有例外且回傳 `None`，導致後續程式碼崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | `archive` 使用 `shell=True` 且指令由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | `export_csv` 未使用 `with` 管理檔案，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | `collect_authors` 使用可變預設值 `seen=[]`，跨呼叫共用狀態 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:32` | `collect_authors` 直接修改傳入的 `seen` 並回傳，可能造成非預期副作用 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | `threshold_from_env` 的 `default` 參數為可變預設值，且未處理轉換失敗 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | `classify` 依賴 `pr` 中的鍵，若 API 回傳缺少欄位會拋出 `KeyError` | 0.60 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | `review_latency` 假設 `events` 非空且元素有 `created_at`，可能拋出例外 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> `_fetch` 吞掉所有例外且回傳 `None`，導致後續程式碼崩潰</summary>

`_fetch` 的 `except` 區塊只有 `pass`，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx、JSON 解析失敗或 `GITHUB_TOKEN` 未設定時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，導致程式崩潰且沒有有用的錯誤訊息。

建議：在 `except` 中記錄錯誤並重新拋出，或讓 `_fetch` 回傳明確的錯誤值，並在呼叫端檢查。

**判斷依據**：diff 第 25-26 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> `archive` 使用 `shell=True` 且指令由外部輸入拼接，存在命令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。`repo` 來自命令列參數，攻擊者可注入額外指令，例如 `repo = "x; rm -rf /"`，導致任意命令執行。

建議：改用參數列表形式並移除 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 88 行：`subprocess.run` 使用 `shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> `export_csv` 未使用 `with` 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 開啟檔案後手動 `close`，但若寫入過程拋出例外（例如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。

建議：使用 `with open(path, "w") as f:` 確保檔案關閉。

**判斷依據**：diff 第 82-86 行：手動開啟與關閉檔案，沒有 `with` 或 `try/finally`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> `collect_authors` 使用可變預設值 `seen=[]`，跨呼叫共用狀態</summary>

`collect_authors` 的參數 `seen` 預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，導致作者清單不正確。

建議：改用 `seen=None`，並在函式內初始化為空串列。

**判斷依據**：diff 第 29 行：`seen=[]` 為可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:32</code> `collect_authors` 直接修改傳入的 `seen` 並回傳，可能造成非預期副作用</summary>

`collect_authors` 對傳入的 `seen` 串列進行 `append`，並回傳同一個串列。若呼叫者傳入自己的串列，該串列會被修改，可能造成非預期副作用。

建議：在函式內建立新串列，或複製傳入的串列後再修改。

**判斷依據**：diff 第 34-35 行：直接修改參數並回傳。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> `threshold_from_env` 的 `default` 參數為可變預設值，且未處理轉換失敗</summary>

`threshold_from_env` 的 `default` 參數預設為 `{"days": 7}`，是可變字典。雖然函式內未修改 `default`，但若未來修改可能引入共用狀態問題。此外，`int(raw)` 轉換環境變數時若值不是整數會拋出 `ValueError`，導致程式崩潰。

建議：改用 `default=None` 並在函式內設定預設值，並捕捉 `ValueError` 或提供明確錯誤訊息。

**判斷依據**：diff 第 48-51 行：可變預設值與未處理的 `int()` 轉換。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> `classify` 依賴 `pr` 中的鍵，若 API 回傳缺少欄位會拋出 `KeyError`</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]` 和 `pr["title"]`。若 GitHub API 回傳的 JSON 缺少這些欄位（例如 API 變更或權限不足），會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證資料結構。

**判斷依據**：diff 第 55-59 行：直接使用鍵存取。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> `review_latency` 假設 `events` 非空且元素有 `created_at`，可能拋出例外</summary>

`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 鍵，會拋出 `KeyError`。此外，`events` 可能不是串列（例如 API 回傳 `None`），`events[0]` 會拋出 `TypeError`。

建議：檢查 `events` 型別與元素結構，或使用 `events[0].get("created_at")`。

**判斷依據**：diff 第 40-41 行：直接索引與鍵存取。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 2183 ｜ PR #12</sub>