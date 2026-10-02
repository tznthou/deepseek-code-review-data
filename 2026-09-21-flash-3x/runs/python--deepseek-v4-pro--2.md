<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個從 GitHub API 撈取 PR 資料並計算維護指標的 Python 腳本。主要風險在於安全性與穩健性：`_fetch` 函式吞掉所有例外且未檢查回應狀態，可能導致後續程式碼因缺少欄位而崩潰；`archive` 函式使用 `shell=True` 且拼接外部輸入，存在命令注入風險；此外還有可變預設值、資源未妥善管理等問題。建議先修正安全性與錯誤處理，再考慮合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | `_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 `seen=[]` 導致跨呼叫共用狀態 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | `export_csv` 未使用 `with` 管理檔案資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | `threshold_from_env` 未處理環境變數轉換失敗 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | `classify` 假設 PR 一定有 `additions` 和 `changed_files` 欄位 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:37` | `review_latency` 假設 `timeline` 事件存在且非空 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> `_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼</summary>

`_fetch` 函式使用裸 `except: pass` 吞掉所有例外，包括網路錯誤、JSON 解析錯誤等。此外，它未檢查 HTTP 回應狀態碼，若 API 回傳 404 或 401，`json.loads` 仍會嘗試解析錯誤頁面，可能拋出例外而被吞掉，導致函式回傳 `None`。後續程式碼（如 `pr["user"]["login"]`）會因 `pr` 為 `None` 而拋出 `TypeError`，造成程式崩潰。建議：明確捕捉 `urllib.error.URLError` 和 `json.JSONDecodeError`，並檢查 `resp.status`，若非 2xx 則拋出例外或記錄錯誤。

**判斷依據**：diff 第 22 行：`except:` 與 `pass`，且未檢查 `resp.status`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 參數（來自命令列參數）與 `path`（來自內部變數，但可能受環境影響）。攻擊者可提供惡意的 `repo` 值（例如 `; rm -rf /`）來執行任意命令。建議改用參數列表形式並移除 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 76 行：`shell=True` 且 f-string 包含 `repo` 變數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 `seen=[]` 導致跨呼叫共用狀態</summary>

`collect_authors` 函式的 `seen` 參數預設為空列表，這是一個可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，導致非預期行為。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 31 行：`seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> `export_csv` 未使用 `with` 管理檔案資源</summary>

`export_csv` 函式直接使用 `open` 和 `close`，若在寫入過程中發生例外，檔案可能未正確關閉，導致資源洩漏。建議改用 `with open(path, "w") as f:` 來確保檔案總會被關閉。

**判斷依據**：diff 第 78-82 行：手動 `open` 與 `close`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> `threshold_from_env` 未處理環境變數轉換失敗</summary>

`threshold_from_env` 函式直接使用 `int(raw)` 轉換環境變數 `PR_STALE_DAYS`，若該變數不是有效整數（例如設為 `abc`），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 49 行：`int(raw)` 未包在 try-except 中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> `classify` 假設 PR 一定有 `additions` 和 `changed_files` 欄位</summary>

`classify` 函式直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能因權限或 API 版本而缺少這些欄位，導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 54 行：直接索引 `pr["additions"]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:37</code> `review_latency` 假設 `timeline` 事件存在且非空</summary>

`review_latency` 函式使用 `pr.get("timeline", [])` 取得事件列表，但若 `timeline` 欄位存在但為 `None`，則 `if not events` 會通過（因為 `None` 為假），但後續 `events[0]` 會拋出 `TypeError`。建議檢查 `events` 是否為列表且非空。

**判斷依據**：diff 第 40-43 行：`events` 可能為 `None`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3228 (cache hit 3200) ｜ completion tokens 1723</sub>