<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 且指令由外部輸入拼接、token 可能外洩）、以及可變預設值與資源管理缺陷。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入風險。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫共用狀態 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:21` | GITHUB_TOKEN 可能因例外而外洩 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理例外 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（如 `collect_authors` 和 `main` 中的 `pr = _fetch(...)`）直接使用回傳值，當 `_fetch` 失敗時會得到 `None`，接著存取 `pr["user"]` 或 `pr["additions"]` 會拋出 `TypeError`，且原始錯誤被隱藏，難以除錯。

建議：讓 `_fetch` 在失敗時拋出例外，或回傳明確的錯誤值並由呼叫端檢查。

**判斷依據**：diff 第 24 行：`except: pass` 且函式沒有回傳值。呼叫端如第 30 行 `pr["user"]["login"]` 直接使用回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令由外部輸入拼接，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 參數（來自命令列參數）與 `path`（由 repo 衍生）。攻擊者可提供惡意 repo 名稱（例如 `foo; rm -rf /`）來執行任意命令。

建議：避免使用 `shell=True`，改用參數列表形式，並將 `gh repo view` 分開執行。

**判斷依據**：diff 第 62 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自 `sys.argv[1]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫共用狀態</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會累積到同一個 list，導致結果不正確。例如連續呼叫兩次，第二次會包含第一次的作者。

建議：改用 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 28 行：`def collect_authors(repo, numbers, seen=[]):`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程拋出例外（例如磁碟滿），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 58-62 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:21</code> GITHUB_TOKEN 可能因例外而外洩</summary>

`_fetch` 在建立請求時直接從環境變數讀取 token，若後續發生例外（例如網路錯誤），traceback 可能包含請求物件，進而洩漏 token。此外，若 token 無效，錯誤訊息可能包含 token。建議在錯誤處理中避免輸出請求內容，或使用更安全的方式傳遞憑證。

**判斷依據**：diff 第 20 行：直接將 token 加入 header，且後續例外處理不當。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序</summary>

`review_latency` 直接取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理），但若 timeline 存在但為空（例如 `[]`），則會拋出 IndexError。此外，事件順序未保證按時間排序，可能導致負數延遲。建議檢查空 list 並排序事件。

**判斷依據**：diff 第 36-37 行：直接索引 events，未檢查空 list 或排序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理例外</summary>

`int(raw)` 若環境變數 `PR_STALE_DAYS` 不是有效整數，會拋出 ValueError，導致程式崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 44 行：`int(raw)` 無例外處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 0) ｜ completion tokens 1680 ｜ PR #12</sub>