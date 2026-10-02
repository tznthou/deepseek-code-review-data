<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確關閉（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議先修正 blocker 等級的指令注入與錯誤吞掉問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:23` | 錯誤被吞掉，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配使用者輸入，可能造成指令注入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫共用狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，可能造成資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式可能因缺少鍵而拋出 KeyError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:23</code> 錯誤被吞掉，導致後續程式碼在資料缺失時崩潰</summary>

_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。這會使得當 API 請求失敗（例如網路錯誤、認證失敗、回應非 JSON）時，函式回傳 None。呼叫端（如 collect_authors 和 main 中的迴圈）直接使用回傳值進行索引（pr["user"]），會引發 TypeError 或 KeyError，且錯誤訊息不明確。

建議：至少記錄例外（logging.exception），或重新拋出，讓呼叫端能處理。

**判斷依據**：diff 第 23-24 行：except: pass

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配使用者輸入，可能造成指令注入</summary>

archive 函式使用 subprocess.run 搭配 shell=True，且指令字串包含 repo 參數（來自命令列輸入）。攻擊者可注入額外指令，例如 repo 值為 "x; rm -rf /" 時，會執行任意指令。

建議：避免使用 shell=True，改用參數清單傳遞，或使用 shlex.quote 正確跳脫。

**判斷依據**：diff 第 48 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫共用狀態</summary>

collect_authors 函式的 seen 參數預設值為空串列，這在 Python 中只會建立一次，並在所有呼叫之間共用。如果呼叫者未傳入 seen，多次呼叫會累積先前呼叫的結果，導致 authors 清單包含重複或非預期的資料。

建議：將預設值改為 None，並在函式內初始化為空串列。

**判斷依據**：diff 第 28 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，可能造成資源洩漏</summary>

export_csv 函式使用 open 開啟檔案，但未使用 with 或 try/finally 確保關閉。若寫入過程發生例外，檔案控制代碼不會被釋放，可能導致資源洩漏。

建議：改用 with open(path, "w") as f: 寫入。

**判斷依據**：diff 第 43-47 行

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

threshold_from_env 函式將環境變數 PR_STALE_DAYS 轉換為整數，但未處理 ValueError。若使用者設定非數字值（例如 "abc"），程式會崩潰。

建議：使用 try/except 捕捉轉換錯誤，並提供預設值或錯誤訊息。

**判斷依據**：diff 第 52 行

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式可能因缺少鍵而拋出 KeyError</summary>

classify 函式直接存取 pr["additions"]、pr["changed_files"]、pr["title"]，但未檢查這些鍵是否存在。若 API 回應缺少這些欄位（例如權限不足或 API 變更），會拋出 KeyError。

建議：使用 .get() 方法並提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 55-60 行

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 3200) ｜ completion tokens 1394 ｜ PR #12</sub>