<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的 Python 腳本。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源管理（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議優先修正。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能導致資源洩漏 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉型失敗 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 PR 一定有 additions 和 changed_files 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 函式中的 `except: pass` 會捕捉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不記錄任何資訊。當 API 呼叫失敗時，函式回傳 `None`，而呼叫端（如 `collect_authors` 和 `main`）直接存取 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，導致程式崩潰。建議至少記錄錯誤並重新拋出，或讓呼叫端檢查回傳值。

**判斷依據**：diff 第 24 行：`except:` 後接 `pass`，且無任何 logging 或 raise。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。這些參數來自命令列參數（`sys.argv`），攻擊者可注入額外指令，例如 `repo` 設為 `foo; rm -rf /`。建議改用參數列表形式，避免使用 shell，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 70 行：`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

函式 `collect_authors` 的參數 `seen=[]` 使用可變預設值，該 list 在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留，造成結果不正確。建議改為 `seen=None`，並在函式內初始化為空 list。

**判斷依據**：diff 第 28 行：`seen=[]` 為可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 開啟檔案，但未使用 `with` 語句，若寫入過程中發生例外，檔案不會被正確關閉。建議改用 `with open(path, "w") as f:` 來確保資源釋放。

**判斷依據**：diff 第 62-66 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉型失敗</summary>

`threshold_from_env` 直接使用 `int(raw)` 轉換環境變數 `PR_STALE_DAYS`，若該變數不是有效整數（例如設為 "abc"），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 45 行：`int(raw)` 無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 一定有 additions 和 changed_files 欄位</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能因權限或 API 版本而缺少這些欄位，導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 50-51 行：直接索引字典。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3355 (cache hit 256) ｜ completion tokens 1424 ｜ PR #12</sub>