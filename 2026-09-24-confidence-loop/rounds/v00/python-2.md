<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險集中在錯誤處理與安全性：`_fetch` 吞掉所有例外且回傳 None，後續直接取值會造成未處理的例外；`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險；`collect_authors` 使用可變預設值 `seen=[]`，跨呼叫會累積資料；`threshold_from_env` 對環境變數做 `int()` 轉換但未處理無效輸入。建議先修復這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | `_fetch` 吞掉所有例外且回傳 None，後續直接取值會導致未處理的例外 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | `collect_authors` 使用可變預設值 `seen=[]`，跨呼叫會累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | `threshold_from_env` 對環境變數做 `int()` 轉換但未處理無效輸入 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | `export_csv` 未使用 `with` 開啟檔案，例外時可能洩漏檔案控制代碼 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> `_fetch` 吞掉所有例外且回傳 None，後續直接取值會導致未處理的例外</summary>

`_fetch` 的 `except:` 區塊只有 `pass`，當請求失敗（例如網路錯誤、API 回傳非 2xx、JSON 解析失敗）時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr.get(...)`，會拋出 `TypeError` 或 `AttributeError`，導致程式崩潰。建議：讓 `_fetch` 在失敗時拋出例外（或回傳明確的錯誤物件），並在呼叫端處理；至少應記錄錯誤並中止，而不是靜默吞掉。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有其他回傳值，失敗時回傳 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（使用者可控）。攻擊者可注入額外命令，例如 `repo` 設為 `foo; rm -rf /`，導致任意命令執行。建議：改用參數列表形式（`subprocess.run(["tar", "czf", f"{path}.tgz", path])`），並避免使用 `shell=True`；若必須使用 shell，應對輸入進行嚴格驗證或轉義。

**判斷依據**：diff 第 74 行：`subprocess.run` 的指令字串由 f-string 組成，包含外部輸入 `repo` 和 `path`，且 `shell=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> `collect_authors` 使用可變預設值 `seen=[]`，跨呼叫會累積資料</summary>

`collect_authors` 的參數 `seen` 預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，之後每次呼叫都會共用同一個列表物件。如果呼叫者未傳入 `seen`，多次呼叫會不斷累積作者，導致結果不正確。建議：將預設值改為 `None`，並在函式內初始化為空列表。

**判斷依據**：diff 第 28 行：函式簽名使用可變預設值 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> `threshold_from_env` 對環境變數做 `int()` 轉換但未處理無效輸入</summary>

`threshold_from_env` 讀取環境變數 `PR_STALE_DAYS` 並直接 `int(raw)`，若該變數不是有效整數（例如設為 `abc`），會拋出 `ValueError` 導致程式崩潰。建議：使用 `try/except` 捕捉轉換錯誤，並提供合理的預設值或錯誤訊息。

**判斷依據**：diff 第 42 行：`int(raw)` 沒有例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> `export_csv` 未使用 `with` 開啟檔案，例外時可能洩漏檔案控制代碼</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限問題），檔案不會被關閉，可能造成資源洩漏。建議改用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 58-62 行：手動開啟和關閉檔案，沒有使用 `with`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 1408) ｜ completion tokens 1418 ｜ PR #12</sub>