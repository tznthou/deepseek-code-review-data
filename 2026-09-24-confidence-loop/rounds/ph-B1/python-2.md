<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 腳本。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未使用 with）。此外，classify 對 additions 的型別假設、threshold_from_env 的 int 轉換未處理例外、review_latency 對空 events 的處理等都可能造成執行期錯誤。最該先修的是 _fetch 的錯誤處理和 archive 的指令注入。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設參數 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int 轉換未處理例外，可能導致程式崩潰 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 pr["additions"] 和 pr["changed_files"] 為數字，可能因型別錯誤而崩潰 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:38` | review_latency 對空 events 回傳 0，可能誤導指標 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。建議至少記錄例外並重新拋出，或回傳明確的錯誤物件，並在呼叫端處理。

**判斷依據**：diff 第 24 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值被直接使用（例如 `collect_authors` 第 29 行 `pr["user"]["login"]`）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，這些值來自命令列參數或檔案路徑，可能包含惡意 shell 指令。攻擊者可透過控制 `repo` 參數注入任意指令。建議改用參數列表形式，避免 shell 解析，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 74 行：`shell=True` 且 f-string 包含外部輸入 `repo` 和 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設參數 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的 `seen` 參數預設為空 list，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫多次，前一次的結果會殘留，導致後續呼叫的 `seen` 包含先前資料。建議改為 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值，且函式內有 `seen.append(...)` 修改它。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（如磁碟滿、權限問題），檔案不會被關閉，造成資源洩漏。建議使用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 70-74 行：手動 open/close，無 with 或 try/finally。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int 轉換未處理例外，可能導致程式崩潰</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 int，若該值不是合法整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式終止。建議使用 try/except 或先驗證輸入。

**判斷依據**：diff 第 45 行：`int(raw)` 無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr["additions"] 和 pr["changed_files"] 為數字，可能因型別錯誤而崩潰</summary>

`classify` 直接比較 `pr["additions"] > 500` 和 `pr["changed_files"] > 20`，但 GitHub API 回傳的這些欄位可能是字串或缺失，導致 TypeError 或 KeyError。建議先驗證型別或使用 `int()` 轉換並處理例外。

**判斷依據**：diff 第 51-53 行：直接比較，無型別檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:38</code> review_latency 對空 events 回傳 0，可能誤導指標</summary>

`review_latency` 在 `events` 為空時回傳 0，但 0 可能被解讀為「零延遲」，而實際上可能是資料缺失。建議回傳 None 或拋出例外，讓呼叫端處理。

**判斷依據**：diff 第 35-36 行：空 events 回傳 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 0) ｜ completion tokens 1716 ｜ PR #12</sub>