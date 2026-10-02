<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未使用 with）。此外，classify 對缺少欄位的 PR 可能拋出 KeyError，threshold_from_env 對無效輸入會拋出 ValueError。建議先修正安全性與正確性問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:23` | 錯誤被完全吞掉，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入造成命令注入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設參數 seen=[] 導致跨呼叫累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 對缺少 additions 或 changed_files 的 PR 拋出 KeyError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:42` | threshold_from_env 對無效環境變數拋出未處理的 ValueError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:23</code> 錯誤被完全吞掉，導致後續程式碼在資料缺失時崩潰</summary>

_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回傳非 JSON、或 HTTP 錯誤狀態碼（如 404）發生時，_fetch 會回傳 None。呼叫端（collect_authors 和 main 中的迴圈）直接對回傳值進行索引（pr["user"]["login"]）或屬性存取，將導致 TypeError 或 AttributeError，且原始錯誤被隱藏，難以除錯。

建議：至少記錄例外（logging.exception），或重新拋出；若需回傳 None，呼叫端應檢查並處理。

**判斷依據**：diff 第 23-24 行：except: pass

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入造成命令注入</summary>

archive 函式使用 subprocess.run 並設定 shell=True，且命令字串包含 repo 變數（來自命令列參數）和 path（由 repo 衍生）。攻擊者可提供如 '; rm -rf /' 的 repo 值，導致任意命令執行。

建議：避免 shell=True，改用參數列表形式，例如 subprocess.run(['tar', 'czf', f'{path}.tgz', path])，並分開執行 gh 命令。

**判斷依據**：diff 第 67 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設參數 seen=[] 導致跨呼叫累積</summary>

collect_authors 的 seen 參數預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 seen，每次呼叫都會將作者附加到同一個串列，導致結果累積。例如連續呼叫 collect_authors(repo, [1]) 和 collect_authors(repo, [2])，第二次會回傳包含第一次作者的串列。

建議：使用 seen=None 並在函式內初始化為空串列。

**判斷依據**：diff 第 28 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，可能洩漏資源</summary>

export_csv 使用 open 開啟檔案，但未使用 with 或 try/finally 確保關閉。若寫入過程中發生例外（如磁碟滿、權限錯誤），檔案控制代碼不會被關閉，可能導致資源洩漏或資料不完整。

建議：使用 with open(path, 'w') as f: 並在區塊內寫入。

**判斷依據**：diff 第 59-63 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 對缺少 additions 或 changed_files 的 PR 拋出 KeyError</summary>

classify 直接存取 pr["additions"] 和 pr["changed_files"]，但 GitHub API 回傳的 PR 物件不一定包含這些欄位（例如某些事件或權限不足時）。若欄位缺失，會拋出 KeyError 導致程式終止。

建議：使用 pr.get("additions", 0) 和 pr.get("changed_files", 0) 提供預設值。

**判斷依據**：diff 第 73-75 行

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:42</code> threshold_from_env 對無效環境變數拋出未處理的 ValueError</summary>

threshold_from_env 將環境變數 PR_STALE_DAYS 轉為整數，若值不是有效整數（如 'abc'），int() 會拋出 ValueError，導致程式崩潰。建議捕捉例外並回退到預設值或提供明確錯誤訊息。

**判斷依據**：diff 第 42-43 行

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 0) ｜ completion tokens 1472 ｜ PR #12</sub>