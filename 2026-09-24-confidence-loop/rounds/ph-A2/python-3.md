<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、以及 shell=True 的指令注入（archive）。此外，review_latency 的計算邏輯可能不正確，且 classify 對缺少欄位的 PR 會拋出 KeyError。建議先修正安全性與正確性問題再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | 例外被完全吞掉，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | `shell=True` 搭配使用者輸入，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 `seen=[]` 導致跨呼叫累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | `classify` 對缺少欄位的 PR 會拋出 KeyError | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | `review_latency` 計算邏輯可能不正確 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | 檔案開啟未使用 `with`，可能導致資源洩漏 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> 例外被完全吞掉，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。當 API 呼叫失敗時，函式回傳 `None`，而呼叫端（如 `collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，導致程式崩潰且難以除錯。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 或讓 `_fetch` 在失敗時拋出明確的例外，由呼叫端處理。
- 避免使用裸 `except:`，改為捕捉具體例外（如 `urllib.error.URLError`, `json.JSONDecodeError`）。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 72 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> `shell=True` 搭配使用者輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 且 `shell=True`，指令字串中包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（`sys.argv[1]`），屬於外部輸入。攻擊者可注入額外指令，例如 `repo` 設為 `foo; rm -rf /`，導致任意指令執行。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若必須使用 shell，請對輸入進行嚴格驗證或使用 `shlex.quote`。

**判斷依據**：diff 第 82 行：`shell=True` 且指令字串由 `repo`（來自 `sys.argv[1]`）和 `path` 拼接。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 `seen=[]` 導致跨呼叫累積</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值。在 Python 中，預設值只會在函式定義時建立一次，之後每次呼叫若未提供 `seen` 參數，都會共用同一個 list。這會導致多次呼叫 `collect_authors` 時，作者名單會不斷累積，而不是每次重新開始。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 操作（第 30 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> `classify` 對缺少欄位的 PR 會拋出 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`。若 API 回應缺少這些欄位（例如權限不足或 API 版本變更），會拋出 `KeyError` 導致程式崩潰。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證欄位存在。

**判斷依據**：diff 第 56 行：直接存取 `pr["additions"]`，未檢查鍵是否存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> `review_latency` 計算邏輯可能不正確</summary>

`review_latency` 從 `pr.get("timeline", [])` 取得事件列表，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位（需要另外請求 timeline API）。因此 `events` 會是空列表，函式回傳 0，導致延遲指標永遠為 0。

建議：確認 API 回應是否包含 timeline，若無則需額外請求或改用其他欄位（如 `created_at` 和 `updated_at`）。

**判斷依據**：diff 第 34 行：`pr.get("timeline", [])` 但 GitHub PR API 回應中沒有 `timeline` 欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> 檔案開啟未使用 `with`，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close`，但若在寫入過程中發生例外（例如磁碟滿），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 63 行：`f = open(path, "w")` 後未使用 `with`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

`threshold_from_env` 中 `int(raw)` 可能拋出 `ValueError` 若環境變數不是有效整數。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 45 行：`int(raw)` 未處理轉換失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1879 ｜ PR #12</sub>