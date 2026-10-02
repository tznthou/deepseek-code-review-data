<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增一個從 GitHub API 撈取 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及缺少輸入驗證。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們可能造成靜默失敗或命令注入。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:26` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at，可能拋出例外 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理 int() 轉換失敗，可能導致程式崩潰 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 pr 有 additions、changed_files、title 鍵，可能 KeyError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能洩漏資源 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:83` | main 中重複呼叫 _fetch 取得相同 PR 資料，造成不必要的 API 請求 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:26</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 與 `main`）直接使用回傳值當作 dict 存取，例如 `pr["user"]["login"]`，當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，且原始錯誤被隱藏，難以除錯。

建議：
- 至少記錄錯誤（`logging.exception`）並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼（`resp.status`）並處理非 200 的情況。
- 避免使用裸 `except:`，改為捕捉具體例外（`urllib.error.URLError`, `json.JSONDecodeError` 等）。

**判斷依據**：diff 第 26 行：`except:` 後只有 `pass`，且函式無回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 與 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外 shell 指令，例如 `repo = "x; rm -rf /"`。

建議：
- 避免使用 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若需執行 `gh repo view`，也應分開呼叫並使用參數列表。
- 若必須使用 shell，請對輸入進行嚴格驗證或使用 `shlex.quote`。

**判斷依據**：diff 第 71 行：`shell=True` 且 f-string 包含 `repo` 與 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是 Python 的可變預設值，只會在函式定義時建立一次。每次呼叫若未傳入 `seen`，都會共用同一個 list，導致多次呼叫時作者名單不斷累積，且可能包含前一次呼叫的結果。

建議：改為 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 31 行：參數預設值為 `[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at，可能拋出例外</summary>

`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但第一個元素缺少 `created_at` 鍵，則會拋出 `KeyError`。此外，`pr.get("timeline", [])` 可能回傳 `None`（若 API 回傳 `timeline: null`），此時 `if not events` 會通過（`None` 為 falsy），但後續 `events[0]` 會拋出 `TypeError`。

建議：
- 檢查 `events` 是否為 list 且非空，並確認每個元素都有 `created_at`。
- 使用 `events[0].get("created_at")` 並處理缺失值。

**判斷依據**：diff 第 44-45 行：直接索引 events 並存取鍵。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理 int() 轉換失敗，可能導致程式崩潰</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若該值不是合法整數（例如 "abc" 或空字串），會拋出 `ValueError` 且未捕捉，導致程式終止。

建議：使用 try/except 捕捉 `ValueError`，並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 50 行：`int(raw)` 無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 有 additions、changed_files、title 鍵，可能 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但若 API 回傳的 PR 物件缺少這些鍵（例如某些事件或權限不足），會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證必要欄位。

**判斷依據**：diff 第 58-61 行：直接索引字典。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 與 `close`，但若寫入過程中發生例外（例如磁碟滿），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 66-70 行：手動 open/close。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:83</code> main 中重複呼叫 _fetch 取得相同 PR 資料，造成不必要的 API 請求</summary>

`main` 先呼叫 `collect_authors` 取得作者（內部對每個 PR 呼叫 `_fetch`），然後又在迴圈中再次對每個 PR 呼叫 `_fetch` 取得完整資料。這會造成每個 PR 被請求兩次，增加 API 負擔與執行時間。建議只請求一次並重用資料。

**判斷依據**：diff 第 82-86 行：兩次迴圈呼叫 _fetch。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 2228 ｜ PR #12</sub>