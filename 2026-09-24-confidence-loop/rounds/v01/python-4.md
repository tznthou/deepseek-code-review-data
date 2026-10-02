<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 且未驗證輸入）、以及可變預設值參數。建議先修正這些問題再合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:22` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令包含外部輸入，可能導致命令注入 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值參數 seen=[] 可能導致跨呼叫累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 的預設值為可變字典，可能被意外修改 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式可能因缺少鍵而拋出 KeyError | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:37` | review_latency 假設 timeline 存在且非空，可能導致錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | 環境變數轉換為整數時未處理 ValueError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:22</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式可能回傳 `None`。呼叫端（`collect_authors` 和 `main` 中的迴圈）直接使用回傳值，例如 `pr["user"]["login"]`，當 `pr` 為 `None` 時會拋出 `TypeError`，造成程式崩潰。建議：讓例外向上傳播，或回傳明確的錯誤值並在呼叫端檢查。

**判斷依據**：diff 第 22 行顯示 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 27 行）和 `main`（第 77 行）中被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令包含外部輸入，可能導致命令注入</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path` 參數。`repo` 來自命令列參數，攻擊者可注入額外指令，例如 `repo = "x; rm -rf /"`。建議改用參數列表形式，並避免使用 `shell=True`。

**判斷依據**：diff 第 88 行顯示 `shell=True` 且指令由 f-string 組成，其中 `repo` 來自 `sys.argv[1]`（第 72 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值參數 seen=[] 可能導致跨呼叫累積</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list。如果函式被多次呼叫（例如在測試或迴圈中），結果會累積，導致非預期行為。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 27 行顯示 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 的預設值為可變字典，可能被意外修改</summary>

`threshold_from_env` 的參數 `default={"days": 7}` 是可變字典，若函式內部修改該字典（目前沒有），會影響後續呼叫。即使目前未修改，仍建議改為 `None` 並在函式內設定預設值，以避免未來修改時引入 bug。

**判斷依據**：diff 第 46 行顯示 `default={"days": 7}`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若寫入過程中發生例外，檔案不會被關閉。建議使用 `with open(path, "w") as f:` 來確保資源釋放。

**判斷依據**：diff 第 62-66 行顯示手動開啟和關閉檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式可能因缺少鍵而拋出 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]` 和 `pr["title"]`，但 GitHub API 的回應可能缺少這些欄位（例如某些事件類型）。建議使用 `pr.get(...)` 並提供預設值。

**判斷依據**：diff 第 55-60 行顯示直接使用鍵存取。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:37</code> review_latency 假設 timeline 存在且非空，可能導致錯誤</summary>

`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位，因此 `events` 會是空列表，函式回傳 0。這可能不是預期行為，建議確認 API 回應結構或改用其他端點取得時間線。

**判斷依據**：diff 第 34-36 行顯示對 `timeline` 的處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數時未處理 ValueError</summary>

`threshold_from_env` 中 `int(raw)` 可能拋出 `ValueError`，若環境變數 `PR_STALE_DAYS` 不是有效整數，程式會崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 50 行顯示 `int(raw)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3409 (cache hit 640) ｜ completion tokens 1800 ｜ PR #12</sub>