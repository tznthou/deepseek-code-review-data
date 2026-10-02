<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的 Python 腳本。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、以及 shell=True 的指令注入風險（archive 函式）。此外，資源管理（export_csv 未使用 with）和環境變數解析（threshold_from_env 未處理轉換失敗）也需要改善。最優先應修復 _fetch 的錯誤吞掉和 archive 的 shell 注入。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | 例外被吞掉且函式可能回傳 None | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入造成指令注入 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設參數 seen=[] 導致跨呼叫共用狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，例外時可能外洩 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式依賴可能不存在的鍵 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> 例外被吞掉且函式可能回傳 None</summary>

_fetch 函式在 try 區塊中捕捉所有例外後僅執行 pass，沒有記錄或重新拋出。這會導致呼叫端在 API 請求失敗時收到 None，後續程式碼（如 pr["user"]）將拋出 TypeError，且難以除錯。建議至少記錄錯誤並重新拋出，或讓函式回傳明確的錯誤值並由呼叫端處理。

**判斷依據**：diff 第 24-25 行顯示 except: pass，且 _fetch 的回傳值在 collect_authors 和 main 中被直接使用（如 pr["user"]["login"]）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入造成指令注入</summary>

archive 函式使用 subprocess.run 搭配 shell=True，且指令字串包含 repo 和 path 參數。repo 來自命令列參數，攻擊者可注入額外指令（例如 repo 值為 "x; rm -rf /"）。建議改用參數列表形式並避免 shell=True，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 78 行顯示 shell=True 且 f-string 包含外部輸入 repo 和 path。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設參數 seen=[] 導致跨呼叫共用狀態</summary>

collect_authors 的 seen 參數預設為空串列，這是可變物件，會在多次呼叫間共用。若呼叫者未傳入 seen，則每次呼叫都會累積到同一個串列，造成結果不正確。建議改為 seen=None，並在函式內初始化為 []。

**判斷依據**：diff 第 28 行顯示 seen=[]，且函式內有 seen.append(...)，會修改該預設串列。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，例外時可能外洩</summary>

export_csv 使用 open 和 close 手動管理檔案，若寫入過程拋出例外，檔案不會被關閉。建議改用 with open(...) as f: 確保資源釋放。

**判斷依據**：diff 第 70-74 行顯示 open 和 close 未使用 with。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

threshold_from_env 中 int(raw) 可能拋出 ValueError，導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 44 行顯示 int(raw) 未包在 try 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式依賴可能不存在的鍵</summary>

classify 直接存取 pr["additions"]、pr["changed_files"]、pr["title"]，若 API 回應缺少這些鍵（例如權限不足或欄位變更），會拋出 KeyError。建議使用 .get() 並提供預設值。

**判斷依據**：diff 第 50-55 行顯示直接索引存取。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3355 (cache hit 256) ｜ completion tokens 1344 ｜ PR #12</sub>