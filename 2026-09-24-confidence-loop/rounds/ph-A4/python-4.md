<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 指令注入、token 可能外洩）、以及可變預設值導致的狀態累積。最該先修的是 _fetch 的例外處理和 archive 的 shell 指令。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配使用者輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:21` | 環境變數 GITHUB_TOKEN 未檢查存在性，可能導致 KeyError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式依賴可能不存在的鍵 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能洩漏資源 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式回傳 `None`。呼叫端（如 `collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，且沒有提供任何錯誤上下文。

具體失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 在 `pr["user"]` 處拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

建議：讓例外向上傳播，或至少記錄錯誤並回傳一個明確的錯誤值，並在呼叫端檢查。

**判斷依據**：diff 第 25 行 `except: pass`，且呼叫端如第 31 行 `pr["user"]["login"]` 未檢查 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配使用者輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 且 `shell=True`，指令字串包含 `repo` 變數（來自命令列參數）。攻擊者可以注入額外指令，例如 `repo` 設為 `foo; rm -rf /`，導致任意指令執行。

具體失敗情境：使用者執行 `python3 pr_stats.py '; rm -rf /' 1`，`repo` 值被拼入 shell 指令，造成嚴重破壞。

建議：改用參數列表形式，避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 68 行，`repo` 來自 `sys.argv[1]`（第 72 行），未經驗證直接拼入 shell 指令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態累積</summary>

`collect_authors` 的 `seen` 參數預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，因此多次呼叫會共用同一個列表，導致作者名單不斷累積。

具體失敗情境：第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`，第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`，而不是預期的 `['bob']`。

建議：將預設值改為 `None`，並在函式內初始化為空列表。

**判斷依據**：diff 第 29 行，`seen=[]` 為可變預設值，且函式內對 `seen` 進行 `append` 操作（第 31 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:21</code> 環境變數 GITHUB_TOKEN 未檢查存在性，可能導致 KeyError</summary>

`_fetch` 直接使用 `os.environ["GITHUB_TOKEN"]`，如果環境變數未設定，會拋出 `KeyError`，且沒有提供友善的錯誤訊息。

具體失敗情境：使用者未設定 `GITHUB_TOKEN` 就執行程式，程式在第一次呼叫 `_fetch` 時崩潰。

建議：使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 `None`，或提供預設值。

**判斷依據**：diff 第 21 行，直接存取環境變數，未處理缺失情況。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為整數，若該值不是合法整數（例如 "abc"），會拋出 `ValueError`，導致程式崩潰。

具體失敗情境：使用者設定 `PR_STALE_DAYS=abc`，程式在呼叫 `threshold_from_env` 時崩潰。

建議：使用 `try/except` 處理轉換失敗，或提供預設值。

**判斷依據**：diff 第 44 行，`int(raw)` 未處理轉換例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式依賴可能不存在的鍵</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 `_fetch` 回傳的資料可能缺少這些鍵（例如 API 回應格式變更或部分 PR 資料不完整），導致 `KeyError`。

具體失敗情境：GitHub API 回傳的 PR 物件缺少 `additions` 欄位（例如某些事件類型），程式在 `classify` 中拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證資料結構。

**判斷依據**：diff 第 54 行，直接存取鍵，未檢查存在性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿），檔案不會被關閉，造成資源洩漏。

具體失敗情境：寫入 CSV 時發生 I/O 錯誤，檔案控制代碼未釋放，可能導致後續操作失敗。

建議：改用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 61-65 行，未使用 context manager。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2022 ｜ PR #12</sub>