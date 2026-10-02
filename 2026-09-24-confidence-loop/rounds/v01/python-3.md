<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、安全性（shell=True 的指令注入、CSV 注入）、以及可變預設值導致的狀態污染。最該先修的是 _fetch 的例外處理和 archive 的 shell 指令，因為它們可能造成誤導性的輸出或執行任意指令。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰或產生錯誤結果 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序，可能導致錯誤延遲計算 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 使用可變預設值 default={"days": 7}，可能被意外修改 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未處理 CSV 注入，且未使用 with 管理檔案 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 未處理無效的整數輸入 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 pr 包含 additions 和 changed_files 欄位，可能因 API 回應缺失而崩潰 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰或產生錯誤結果</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，導致程式崩潰。此外，若 API 回傳錯誤（如 404），程式不會有明確的錯誤訊息，使用者難以除錯。

建議：
- 移除 `try/except`，讓例外自然傳播，或至少記錄錯誤並重新拋出。
- 若需處理特定例外（如 `urllib.error.HTTPError`），應針對性捕捉並提供有意義的錯誤訊息。

**判斷依據**：diff 第 24-28 行顯示 `_fetch` 的 `except: pass`，且呼叫端（第 31、59 行）直接使用回傳值，未檢查是否為 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外指令，例如 `repo = "x; rm -rf /"`，導致任意指令執行。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`。
- 若必須使用 shell，應對輸入進行嚴格驗證或使用 `shlex.quote`。

**判斷依據**：diff 第 76 行顯示 `shell=True` 且指令包含外部輸入 `repo` 和 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若呼叫多次，前一次的結果會殘留，導致後續呼叫的結果包含先前 PR 的作者，造成資料污染。

建議：
- 將預設值改為 `None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 31 行顯示可變預設值 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序，可能導致錯誤延遲計算</summary>

`review_latency` 直接取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空 list（已處理）或事件未按時間排序。若事件順序混亂，計算出的延遲可能為負值或錯誤。此外，若 `created_at` 欄位缺失或格式不符，`_to_epoch` 會拋出例外。

建議：
- 確認 API 回傳的 timeline 是否保證有序，否則應先排序。
- 對 `created_at` 的解析加入錯誤處理。

**判斷依據**：diff 第 42-43 行直接使用索引存取，未檢查事件順序或欄位存在性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 使用可變預設值 default={"days": 7}，可能被意外修改</summary>

`threshold_from_env` 的參數 `default={"days": 7}` 是可變預設值，若函式內修改了 `default`（目前沒有），會影響後續呼叫。雖然目前程式碼未修改，但這是潛在風險，且不符合最佳實踐。

建議：
- 將預設值改為 `None`，並在函式內設定：`if default is None: default = {"days": 7}`。

**判斷依據**：diff 第 50 行顯示可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未處理 CSV 注入，且未使用 with 管理檔案</summary>

`export_csv` 直接將 `r['author']` 等值寫入 CSV，若值包含逗號、換行或公式（如 `=cmd|' /C calc'!A0`），可能破壞 CSV 格式或在試算表軟體中觸發公式注入。此外，檔案開啟未使用 `with`，若寫入過程拋出例外，檔案可能未關閉。

建議：
- 使用 `csv` 模組並設定 `quoting=csv.QUOTE_ALL` 來正確處理特殊字元。
- 使用 `with open(path, 'w', newline='') as f:` 確保檔案關閉。

**判斷依據**：diff 第 68-72 行顯示手動拼接 CSV 且未使用 with。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理無效的整數輸入</summary>

`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為 `int`，若值不是有效整數（如 "abc"），會拋出 `ValueError` 導致程式崩潰。

建議：
- 使用 `try/except` 捕捉轉換錯誤，並提供預設值或錯誤訊息。

**判斷依據**：diff 第 54 行顯示直接 `int(raw)` 轉換。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 包含 additions 和 changed_files 欄位，可能因 API 回應缺失而崩潰</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，若 API 回應中缺少這些欄位（例如權限不足或 API 版本變更），會拋出 `KeyError`。

建議：
- 使用 `pr.get("additions", 0)` 和 `pr.get("changed_files", 0)` 提供預設值。

**判斷依據**：diff 第 59-60 行直接使用鍵值存取。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3409 (cache hit 640) ｜ completion tokens 2302 ｜ PR #12</sub>