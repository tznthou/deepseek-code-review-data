<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 指令注入、token 可能外洩）、以及可變預設值導致的狀態累積。建議先修正 _fetch 的例外處理與 archive 的 shell 用法，再考慮其他問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且參數未驗證，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值，導致跨呼叫累積作者 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 使用可變預設值，且未處理轉換例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式對缺失鍵的處理不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。建議至少記錄錯誤並重新拋出，或讓呼叫端處理 `None`。

**判斷依據**：diff 第 24 行顯示 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors` 和 `main` 中被直接使用（如 `pr["user"]["login"]`）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且參數未驗證，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。這些參數來自命令列輸入（`repo` 來自 `sys.argv[1]`，`path` 來自 `out` 變數，而 `out` 包含 `repo`），攻擊者可注入任意 shell 指令。例如 `repo` 設為 `foo; rm -rf /` 會導致嚴重後果。建議改用參數列表形式（`subprocess.run([...])`）並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 68 行顯示 `shell=True` 且指令字串由外部輸入拼接。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值，導致跨呼叫累積作者</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會累積作者而不會重置。這會導致多次呼叫時結果不正確（例如第二次呼叫會包含第一次的作者）。建議改為 `seen=None` 並在函式內初始化為空列表。

**判斷依據**：diff 第 22 行顯示可變預設值 `seen=[]`，且函式內對 `seen` 進行 `append` 操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 使用可變預設值，且未處理轉換例外</summary>

`threshold_from_env` 的參數 `default={"days": 7}` 使用可變預設值，雖然函式內未修改該字典，但若未來修改可能導致問題。此外，`int(raw)` 可能拋出 `ValueError`（例如環境變數設為非數字），導致程式崩潰。建議改用不可變預設值（如 `None`）並處理轉換例外。

**判斷依據**：diff 第 38 行顯示可變預設值，且第 40 行 `int(raw)` 未處理例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若寫入過程中發生例外（如磁碟滿），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 來確保資源釋放。

**判斷依據**：diff 第 62-66 行顯示手動開啟和關閉檔案，沒有使用 `with`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式對缺失鍵的處理不完整</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]` 和 `pr["title"]`，若 API 回應缺少這些鍵（例如權限不足或 API 變更），會拋出 `KeyError`。建議使用 `.get()` 方法並提供預設值，或先驗證鍵是否存在。

**判斷依據**：diff 第 52-56 行顯示直接存取鍵，未處理缺失情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1563 ｜ PR #12</sub>