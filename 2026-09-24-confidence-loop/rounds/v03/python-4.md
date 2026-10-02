<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell 注入（archive 使用 shell=True 且拼接 repo 參數）、以及資源管理（export_csv 未使用 with）。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們可能導致靜默失敗或命令執行。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且拼接 repo 參數，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 轉換環境變數為整數時未處理 ValueError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 pr 字典包含 additions、changed_files、title 鍵，若缺失會拋出 KeyError | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:32` | collect_authors 未處理 _fetch 回傳 None 或缺少 user 鍵的情況 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作字典，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 或 `pr["additions"]` 會拋出 `TypeError`，且原始錯誤被隱藏，難以除錯。

建議：讓 `_fetch` 在失敗時拋出例外，或回傳明確的錯誤值，並在呼叫端處理。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且拼接 repo 參數，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 參數（來自命令列參數）。攻擊者可以傳入如 `repo; rm -rf /` 的值，導致任意命令執行。

建議：避免使用 `shell=True`，改用參數列表形式，並將 `repo` 作為參數傳遞。

**判斷依據**：diff 第 88 行：`shell=True` 且 f-string 包含 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。如果這個函式被多次呼叫（例如在同一個 process 中處理多個 repo），`seen` 會累積之前呼叫的作者，導致結果不正確。

建議：改用 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 28 行：參數預設值為 `[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close`，但若在寫入過程中發生例外（例如磁碟滿、權限問題），檔案不會被關閉，造成資源洩漏。

建議：使用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 79-83 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 轉換環境變數為整數時未處理 ValueError</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 `int`，若該變數不是有效整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式崩潰。

建議：使用 try/except 捕捉轉換錯誤，或提供預設值。

**判斷依據**：diff 第 43 行：`int(raw)` 無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 字典包含 additions、changed_files、title 鍵，若缺失會拋出 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 `_fetch` 回傳的資料可能不完整（例如 API 回應缺少這些欄位），導致 `KeyError`。

建議：使用 `pr.get()` 並提供預設值，或驗證資料結構。

**判斷依據**：diff 第 50-55 行：直接索引字典。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:32</code> collect_authors 未處理 _fetch 回傳 None 或缺少 user 鍵的情況</summary>

`collect_authors` 中 `pr["user"]["login"]` 若 `_fetch` 回傳 `None` 或 `pr` 缺少 `user` 鍵，會拋出 `TypeError` 或 `KeyError`。這與 `_fetch` 的錯誤處理有關，但即使 `_fetch` 正常，API 回應也可能缺少 `user` 欄位。

建議：在使用前檢查 `pr` 是否為 None 以及 `user` 鍵是否存在。

**判斷依據**：diff 第 31 行：直接存取巢狀鍵。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3355 (cache hit 256) ｜ completion tokens 1780 ｜ PR #12</sub>