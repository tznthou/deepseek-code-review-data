<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確關閉。最該先修的是 _fetch 的錯誤處理與 archive 的 shell=True，因為它們可能導致靜默失敗或安全問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致呼叫端在失敗時仍繼續執行 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int(raw) 未處理轉換失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr["additions"] 等鍵，若 API 回應缺少欄位會拋出 KeyError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at，可能拋出例外 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致呼叫端在失敗時仍繼續執行</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得呼叫端在 API 失敗時仍拿到 `None` 並繼續執行，後續程式碼會因為 `None` 而拋出 `TypeError` 或 `KeyError`，且沒有留下任何錯誤訊息。

建議：
- 至少記錄錯誤（例如 `logging.exception`）並重新拋出，或回傳一個明確的錯誤值。
- 不要使用裸 `except:`，應捕捉具體例外（如 `urllib.error.URLError`, `json.JSONDecodeError`）。

**判斷依據**：diff 第 24 行：`except:` 後直接 `pass`，且 `_fetch` 被 `collect_authors` 和 `main` 呼叫，其回傳值被直接使用（如 `pr["user"]["login"]`）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中的 `path` 和 `repo` 來自命令列參數，攻擊者可注入額外指令（例如 `repo` 設為 `x; rm -rf /`）。此外，`path` 可能包含空格或特殊字元，導致指令執行錯誤。

建議：
- 避免使用 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`。
- 若必須使用 shell，請對參數進行嚴格的驗證或轉義。

**判斷依據**：diff 第 72 行：`shell=True` 且 f-string 包含 `path` 和 `repo`，這兩個值來自 `sys.argv`，完全由使用者控制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`seen=[]` 是 Python 的可變預設值，只會在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫 `collect_authors` 時，先前呼叫的結果會殘留在 `seen` 中，造成資料污染。

建議：改用 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值，且函式內有 `seen.append(...)` 修改該 list。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close`，但若在寫入過程中發生例外（例如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。

建議：使用 `with open(path, "w") as f:` 來確保檔案總會被關閉。

**判斷依據**：diff 第 76-80 行：手動 `open`/`close`，沒有 `with` 或 `try/finally`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int(raw) 未處理轉換失敗</summary>

`int(raw)` 若 `raw` 不是合法整數（例如使用者設定 `PR_STALE_DAYS=abc`），會拋出 `ValueError` 且沒有被捕捉，導致程式崩潰。

建議：使用 `try/except` 處理轉換失敗，或提供預設值。

**判斷依據**：diff 第 40 行：`int(raw)` 直接轉換環境變數字串，沒有錯誤處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr["additions"] 等鍵，若 API 回應缺少欄位會拋出 KeyError</summary>

`classify` 假設 `pr` 字典一定包含 `additions`、`changed_files`、`title` 等鍵。但 GitHub API 的回應可能因權限或版本不同而缺少這些欄位，導致 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 45-50 行：直接使用 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，沒有防禦性檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at，可能拋出例外</summary>

`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但第一個或最後一個元素缺少 `created_at` 鍵，會拋出 `KeyError`。此外，`_to_epoch` 對時間格式有嚴格要求，若 API 回傳格式變更可能失敗。

建議：使用 `events[0].get("created_at")` 並處理缺失情況。

**判斷依據**：diff 第 55-56 行：直接存取 `created_at`，沒有檢查鍵是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1991 ｜ PR #12</sub>