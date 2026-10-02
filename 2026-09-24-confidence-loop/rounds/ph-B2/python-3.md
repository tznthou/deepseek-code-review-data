<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未用 with 管理。最該先修的是 _fetch 的錯誤處理和 archive 的 shell=True，因為它們可能導致資料不正確或安全問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:22` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理 int() 轉換失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr["additions"] 等鍵，若 API 回應缺少欄位會拋出 KeyError | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且第一個事件是 created_at | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:48` | _to_epoch 使用 fromisoformat 可能無法解析所有 ISO 格式 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:22</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict 存取，例如 `pr["user"]["login"]`，當 `_fetch` 回傳 `None` 時會拋出 `TypeError`。此外，`urlopen` 在 HTTP 錯誤（如 404）時會拋出 `HTTPError`，也被吞掉。建議：讓 `_fetch` 重新拋出例外，或回傳明確的錯誤值並在呼叫端檢查。

**判斷依據**：diff 第 22-23 行：`except: pass`，且 `_fetch` 的回傳值在 `collect_authors` 和 `main` 中被直接當作 dict 使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串包含外部輸入，存在指令注入風險</summary>

`archive` 使用 `subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `path` 和 `repo` 來自命令列參數，攻擊者可注入額外指令。例如 `repo` 設為 `x; rm -rf /` 會執行任意指令。建議改用 `subprocess.run` 的 list 形式，避免 shell，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 72 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是 mutable default argument，每次呼叫都會共用同一個 list。如果函式被多次呼叫（例如在同一個 process 中處理多個 repo），`seen` 會累積前一次呼叫的結果，導致資料污染。建議改為 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 27 行：`def collect_authors(repo, numbers, seen=[]):`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但沒有 `try/finally` 或 `with`。如果寫入過程中發生例外（例如磁碟滿），檔案不會被關閉，造成資源洩漏。建議改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 63-67 行：`f = open(path, "w")` 和 `f.close()` 沒有例外保護。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理 int() 轉換失敗</summary>

`threshold_from_env` 直接 `int(raw)`，如果環境變數 `PR_STALE_DAYS` 不是有效整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 49 行：`return {"days": int(raw)}`

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr["additions"] 等鍵，若 API 回應缺少欄位會拋出 KeyError</summary>

`classify` 假設 `pr` 一定有 `additions`、`changed_files`、`title` 等鍵。但 GitHub API 的回應可能因權限或版本不同而缺少這些欄位，導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 55-60 行：直接使用 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且第一個事件是 created_at</summary>

`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]`，但若第一個事件沒有 `created_at` 欄位（例如某些事件型別），會拋出 `KeyError`。建議檢查事件型別或使用 `get`。

**判斷依據**：diff 第 34-35 行：`first = events[0]["created_at"]` 和 `last = events[-1]["created_at"]`

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:48</code> _to_epoch 使用 fromisoformat 可能無法解析所有 ISO 格式</summary>

`_to_epoch` 使用 `datetime.datetime.fromisoformat`，但 GitHub API 的時間格式可能包含微秒或時區偏移，某些 Python 版本可能無法解析。建議使用更寬容的解析方式，如 `dateutil.parser`。

**判斷依據**：diff 第 40 行：`datetime.datetime.fromisoformat`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1983 ｜ PR #12</sub>