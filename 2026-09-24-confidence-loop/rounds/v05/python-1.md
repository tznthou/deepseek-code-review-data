<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、安全性（shell=True 的指令注入、token 可能外洩）、以及可變預設值導致的狀態累積。建議先修復 _fetch 的錯誤處理與 archive 的 shell 注入問題，再考慮合併。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:26` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值，導致跨呼叫累積作者 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有 created_at 欄位 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的預設值為可變 dict，且 int() 轉換可能失敗 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 PR 物件有 additions、changed_files、title 欄位 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:77` | archive 的 tar 指令可能因路徑包含空格或特殊字元而失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:26</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若為 `None` 會拋出 `TypeError`，若為空 dict 則會拋出 `KeyError`。例如：網路中斷時，`pr["user"]["login"]` 會因為 `pr` 是 `None` 而崩潰。建議：讓 `_fetch` 在失敗時拋出例外，或回傳明確的錯誤值，並在呼叫端處理。

**判斷依據**：diff 第 26 行：`except: pass` 吞掉所有例外，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 參數（來自命令列參數）。攻擊者可提供惡意的 repo 名稱（例如 `foo; rm -rf /`）來執行任意指令。建議：改用參數列表形式（`subprocess.run(["tar", "czf", ...])`），或對輸入進行嚴格驗證。

**判斷依據**：diff 第 69 行：`shell=True` 且 f-string 包含 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值，導致跨呼叫累積作者</summary>

`collect_authors` 的 `seen` 參數預設為 `[]`，這是一個可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會將作者附加到同一個 list，導致結果累積。例如：第一次呼叫後 `seen` 包含 A，第二次呼叫會包含 A 和 B。建議：將預設值改為 `None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 31 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有 created_at 欄位</summary>

`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理），但事件物件可能缺少 `created_at` 欄位（例如某些事件類型），導致 `KeyError`。建議：使用 `.get("created_at")` 並處理缺失值。

**判斷依據**：diff 第 38-39 行：直接索引事件物件的 `created_at`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的預設值為可變 dict，且 int() 轉換可能失敗</summary>

`threshold_from_env` 的 `default` 參數預設為 `{"days": 7}`，這是一個可變 dict，但函式內沒有修改它，所以不會造成跨呼叫污染（此點不報）。然而，`int(raw)` 若環境變數不是有效整數會拋出 `ValueError`，導致程式崩潰。建議：捕捉 `ValueError` 並提供有意義的錯誤訊息。

**判斷依據**：diff 第 46 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 物件有 additions、changed_files、title 欄位</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 GitHub API 的回應可能缺少這些欄位（例如某些事件或權限不足），導致 `KeyError`。建議：使用 `.get()` 並提供預設值。

**判斷依據**：diff 第 51-54 行：直接索引可能不存在的鍵。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程中發生例外，檔案不會被關閉。建議：使用 `with open(path, "w") as f:` 來確保資源釋放。

**判斷依據**：diff 第 59-63 行：手動開啟和關閉檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:77</code> archive 的 tar 指令可能因路徑包含空格或特殊字元而失敗</summary>

`archive` 使用 f-string 將 `path` 直接嵌入 shell 指令，若 `path` 包含空格或特殊字元（例如 `/tmp/pr-stats-my repo.csv`），指令會解析錯誤。建議：使用參數列表形式，或對路徑進行轉義。

**判斷依據**：diff 第 69 行：路徑未轉義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1937 ｜ PR #12</sub>