<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的 Python 工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源管理（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議先修正 blocker 級別的指令注入與錯誤吞掉問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | 錯誤被吞掉，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配使用者輸入，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫共用狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，可能造成資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序，可能導致錯誤結果 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉型失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> 錯誤被吞掉，導致後續程式碼在資料缺失時崩潰</summary>

_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。當網路錯誤、API 回應非 JSON、或回應缺少預期欄位時，函式會回傳 None。呼叫端（如 collect_authors 和 main 中的 pr['user']['login']）會因為 None 而拋出 TypeError，且原始錯誤被隱藏，難以除錯。

建議：至少記錄例外（logging.exception），或重新拋出，讓呼叫端能處理。

**判斷依據**：diff 第 24 行顯示 except: pass，且 _fetch 的回傳值被直接用於索引（如 pr['user']['login']），若 _fetch 回傳 None 會導致 TypeError。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配使用者輸入，存在指令注入風險</summary>

archive 函式使用 subprocess.run 搭配 shell=True，且指令字串包含 repo 和 path 參數。repo 來自命令列參數（sys.argv[1]），攻擊者可注入額外 shell 指令，例如 repo 值為 '; rm -rf / #' 時，會執行任意指令。

建議：避免 shell=True，改用參數清單傳遞，或使用 shlex.quote 正確跳脫。

**判斷依據**：diff 第 57 行顯示 shell=True 且 f-string 包含 repo 變數，該變數來自使用者輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫共用狀態</summary>

collect_authors 的參數 seen 預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 seen，多次呼叫會累積先前結果，導致 authors 清單包含重複或非本次 PR 的作者。

建議：將預設值改為 None，並在函式內初始化為空串列。

**判斷依據**：diff 第 28 行顯示 seen=[]，且函式內使用 seen.append 修改該串列。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，可能造成資源洩漏</summary>

export_csv 使用 open 和 close 手動管理檔案，若寫入過程拋出例外（例如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。

建議：改用 with open(path, 'w') as f: 確保檔案正確關閉。

**判斷依據**：diff 第 52-55 行顯示手動 open/close，沒有使用 with。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序，可能導致錯誤結果</summary>

review_latency 直接取 events[0] 和 events[-1] 的 created_at，但未檢查 events 是否為空（已檢查）或事件是否依時間排序。GitHub API 的 timeline 可能未排序，或事件缺少 created_at 欄位，導致計算錯誤或 KeyError。

建議：驗證事件結構，或明確排序後再取首尾。

**判斷依據**：diff 第 34-35 行直接索引 events，未檢查事件內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉型失敗</summary>

threshold_from_env 將環境變數 PR_STALE_DAYS 直接轉為 int，若值不是數字（例如 'abc'）會拋出 ValueError，導致程式崩潰。

建議：捕捉 ValueError 並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 40 行顯示 int(raw) 未處理轉換例外。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 1408) ｜ completion tokens 1453 ｜ PR #12</sub>