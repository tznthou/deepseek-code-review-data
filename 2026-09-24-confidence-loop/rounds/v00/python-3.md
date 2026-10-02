<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive 函式）、以及資源管理（export_csv 未使用 with）。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int(raw) 未處理轉換失敗 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:63` | classify 使用 startswith("fix") 可能誤判標題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except:` 捕捉所有例外後僅 `pass`，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx、或 JSON 解析失敗時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr.get(...)`，若 `pr` 為 `None` 會拋出 `TypeError` 或 `AttributeError`，導致程式崩潰。建議至少記錄錯誤並重新拋出，或讓呼叫端檢查 `None`。

**判斷依據**：diff 第 24-25 行：`except:` 後僅 `pass`，且呼叫端未檢查回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（外部輸入）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`。建議改用參數列表形式並移除 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 62 行：`shell=True` 且 f-string 包含外部輸入 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態</summary>

`collect_authors` 的參數 `seen=[]` 在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若多次呼叫此函式，作者名單會不斷累積，導致結果不正確。建議改為 `seen=None`，在函式內初始化為空 list。

**判斷依據**：diff 第 29 行：`seen=[]` 為可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若寫入過程中發生例外（例如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。建議改用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 56-60 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int(raw) 未處理轉換失敗</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 `int`，若該值不是合法整數（例如 "abc"），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 38 行：`int(raw)` 未處理例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:63</code> classify 使用 startswith("fix") 可能誤判標題</summary>

`classify` 以 `pr["title"].startswith("fix")` 判斷是否為 fix PR，但標題可能以 "fix" 開頭但非修復（例如 "fixed typo in docs"），或大小寫不同（"Fix"）。建議使用更精確的判斷，例如正規表示式或檢查標籤。

**判斷依據**：diff 第 44 行：`startswith("fix")` 過於寬鬆。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 1408) ｜ completion tokens 1435 ｜ PR #12</sub>