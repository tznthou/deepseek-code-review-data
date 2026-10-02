<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、安全性（shell=True 的指令注入、token 可能外洩）、以及可變預設值導致的狀態污染。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們可能造成靜默失敗或遠端程式碼執行。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致靜默失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態污染 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 的預設值為可變字典，且未處理轉換錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能洩漏資源 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:21` | Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致靜默失敗</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），呼叫端無法得知失敗，後續程式碼會繼續執行並可能因資料缺失而崩潰。例如：若 API 回傳 404，`json.loads` 會拋出例外，但被吞掉後 `_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]` 會拋出 `TypeError`。建議至少記錄錯誤並重新拋出，或讓呼叫端處理。

**判斷依據**：diff 第 25 行：`except:` 後只有 `pass`，且 `_fetch` 被多處呼叫（`collect_authors`、`main`），其回傳值被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令包含外部輸入，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo`（來自命令列參數）與 `path`（由 repo 衍生）。攻擊者可提供如 `repo = "x; rm -rf /"` 的輸入，導致任意指令執行。建議改用參數列表形式（`subprocess.run([...])`）並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 73 行：`subprocess.run` 使用 `shell=True`，且 f-string 中包含 `repo` 與 `path`，兩者皆來自外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態污染</summary>

`collect_authors` 的 `seen` 參數預設為空列表，這是可變物件，會在多次呼叫間共享。若呼叫者未傳入 `seen`，每次呼叫都會將作者附加到同一個列表，導致結果累積。例如：第一次呼叫後 `seen` 包含 A，第二次呼叫（未傳入）會從 A 開始附加，回傳錯誤結果。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 20 行：`seen=[]` 為可變預設值，且函式內有 `seen.append(...)` 修改該列表。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 的預設值為可變字典，且未處理轉換錯誤</summary>

`threshold_from_env` 的 `default` 參數預設為 `{"days": 7}`，是可變字典。雖然目前函式未修改它，但若未來修改會造成跨呼叫污染。此外，`int(raw)` 若環境變數不是數字會拋出 `ValueError`，導致程式崩潰。建議使用不可變預設值（如 `None`）並處理轉換例外。

**判斷依據**：diff 第 44 行：可變預設值，且 `int(raw)` 未包在 try/except 中。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若 `f.write` 拋出例外（如磁碟滿），檔案不會被關閉。建議使用 `with open(...) as f:` 確保資源釋放。

**判斷依據**：diff 第 76-80 行：手動 open/close，無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:21</code> Authorization header 直接使用環境變數，可能因缺失而拋出 KeyError</summary>

`_fetch` 使用 `os.environ["GITHUB_TOKEN"]`，若環境變數未設定會拋出 `KeyError`，且此例外會被 `except: pass` 吞掉，導致靜默失敗。建議使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 None。

**判斷依據**：diff 第 22 行：直接索引環境變數，且位於 try 區塊外（但被外層 except 捕獲）。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 0) ｜ completion tokens 1539 ｜ PR #12</sub>