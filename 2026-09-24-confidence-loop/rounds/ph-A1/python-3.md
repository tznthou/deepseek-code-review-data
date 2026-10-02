<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外、export_csv 未使用 with、archive 使用 shell=True 且指令由外部輸入拼接）、可變預設值（collect_authors 的 seen=[]）、以及 review_latency 對空 timeline 的處理不正確。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:38` | review_latency 對空 timeline 回傳 0，可能誤導為無延遲 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 與 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 會拋出 `TypeError`，且錯誤訊息不明確。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 若允許回傳 `None`，呼叫端需檢查並處理。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 30 行）與 `main`（第 69 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在命令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 與 `repo` 來自命令列參數（`sys.argv`），攻擊者可注入額外指令。例如 `repo` 設為 `x; rm -rf /` 會執行任意命令。

建議：
- 避免使用 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 與 `subprocess.run(["gh", "repo", "view", repo])`。
- 若必須使用 shell，需對輸入進行嚴格驗證或轉義。

**判斷依據**：diff 第 82 行：`shell=True` 且 f-string 包含 `path` 與 `repo`，兩者皆來自使用者輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值為可變的 list，會在多次呼叫間共用。若呼叫者未傳入 `seen`，第二次呼叫會包含第一次的結果，導致資料污染。

建議：
- 改用 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 28 行：可變預設值 `seen=[]`，且函式內對其進行 `append` 操作（第 30 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:38</code> review_latency 對空 timeline 回傳 0，可能誤導為無延遲</summary>

`review_latency` 在 `events` 為空時回傳 `0`，但這可能表示資料缺失或 PR 尚未有任何事件，而非真正的零延遲。呼叫端（`main`）將此值寫入 CSV，可能造成錯誤的統計。

建議：
- 回傳 `None` 或拋出例外，讓呼叫端處理。
- 或記錄警告並回傳一個明確的無效值（如 -1）。

**判斷依據**：diff 第 34-35 行：空 `events` 時回傳 `0`，但 `0` 是有效的延遲值，無法區分。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼</summary>

`export_csv` 使用 `open` 與 `close`，但若 `write` 拋出例外（例如磁碟滿），`close` 不會被執行，導致檔案控制代碼洩漏。

建議：
- 使用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 75-79 行：手動 `open`/`close`，無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`threshold_from_env` 中 `int(raw)` 若環境變數 `PR_STALE_DAYS` 不是有效整數，會拋出 `ValueError`，導致程式崩潰。

建議：
- 使用 `try/except` 處理轉換失敗，或提供預設值。

**判斷依據**：diff 第 44 行：直接 `int(raw)`，無例外處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1679 ｜ PR #12</sub>