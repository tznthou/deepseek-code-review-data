<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未使用 with）。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們可能導致工具在實際使用中靜默失敗或造成安全問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:26` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設參數 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉型失敗 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:26</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。建議：至少記錄例外並重新拋出，或回傳一個明確的錯誤物件，讓呼叫端能處理。

**判斷依據**：diff 第 26 行：`except: pass` 吞掉所有例外，且函式沒有回傳值，導致呼叫端無法區分成功與失敗。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串包含外部輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含了 `repo` 和 `path` 參數。這些參數來自命令列參數（`repo`）或由程式內部產生（`path`），但 `repo` 是使用者可控的。攻擊者可以提供類似 `foo; rm -rf /` 的 repo 名稱，導致任意指令執行。建議改用參數列表形式（`shell=False`）並分開傳遞參數，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 72 行：`shell=True` 且 f-string 包含 `repo` 變數，該變數來自 `sys.argv[1]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設參數 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的預設參數 `seen=[]` 在函式定義時建立一次，之後每次呼叫都會共用同一個 list。如果這個函式被多次呼叫（例如在同一個程序內處理多個 repo），作者名單會不斷累積，導致結果錯誤。建議改為 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 31 行：`seen=[]` 是可變預設參數，且函式內會對其進行 `append` 操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，但如果在寫入過程中發生例外（例如磁碟滿、權限問題），`close` 不會被執行，導致檔案控制代碼洩漏。建議使用 `with open(path, "w") as f:` 來確保檔案總會被關閉。

**判斷依據**：diff 第 66-70 行：手動 open/close，沒有使用 with 或 try/finally。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉型失敗</summary>

`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為 `int`，如果該變數不是有效整數（例如設為 "abc"），會拋出 `ValueError` 且沒有提供任何錯誤訊息。建議使用 try/except 捕捉轉換錯誤，並提供有意義的錯誤訊息或回退到預設值。

**判斷依據**：diff 第 48 行：`int(raw)` 沒有錯誤處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序</summary>

`review_latency` 直接取 `events[0]` 和 `events[-1]`，但沒有檢查 `events` 是否為空（雖然有 `if not events` 的檢查，但若 `events` 為 `None` 會拋出 `TypeError`）。此外，它假設事件按時間排序，但 GitHub API 的回傳順序可能不保證。建議明確處理 `None` 情況，並考慮對事件按時間排序後再計算。

**判斷依據**：diff 第 40-41 行：直接索引 events，未處理 None 或順序問題。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1576 ｜ PR #12</sub>