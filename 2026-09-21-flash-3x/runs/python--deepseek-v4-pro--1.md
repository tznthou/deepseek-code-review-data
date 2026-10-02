<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的 Python 工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen 參數）、shell 注入（archive 使用 shell=True 且拼接 repo）、以及資源管理（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議優先修正。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且拼接 repo，存在命令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 假設 timeline 存在且非空，可能拋出例外 | 0.85 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能洩漏資源 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 PR 一定有 additions 和 changed_files 鍵 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉型失敗 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:81` | main 未驗證命令列參數，可能導致 IndexError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 函式中的 `except: pass` 會捕捉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不記錄或重新拋出。這使得呼叫端無法得知失敗，後續程式碼（如 `pr["user"]["login"]`）在 `pr` 為 `None` 或缺少鍵時會拋出 `TypeError` 或 `KeyError`，造成程式崩潰。建議至少記錄錯誤並重新拋出，或讓函式回傳 `None` 並在呼叫端檢查。

**判斷依據**：diff 第 24-25 行：`except:` 後僅有 `pass`，且函式無回傳值，呼叫端未檢查。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且拼接 repo，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 變數（來自命令列參數）。攻擊者可提供如 `repo='x; rm -rf /'` 的輸入來執行任意命令。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 72 行：`shell=True` 且 f-string 包含 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的 `seen` 參數預設為空串列，這是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若多次呼叫此函式，作者名單會不斷累積，導致結果不正確。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 29 行：`seen=[]` 為可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 假設 timeline 存在且非空，可能拋出例外</summary>

`review_latency` 直接存取 `pr["timeline"]`，但 GitHub API 的回應中可能沒有 `timeline` 鍵（例如未請求該欄位），導致 `KeyError`。此外，若 `timeline` 為空，函式回傳 0，但呼叫端可能未預期此情況。建議使用 `pr.get("timeline", [])` 並處理空串列。

**判斷依據**：diff 第 34-38 行：`pr.get` 已處理缺失鍵，但後續 `events[0]` 和 `events[-1]` 在空串列時會拋出 `IndexError`，但此處有 `if not events` 保護，故風險較低。然而，若 `timeline` 存在但元素缺少 `created_at`，仍會拋出 `KeyError`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能洩漏資源</summary>

`export_csv` 直接使用 `open` 和 `close`，若在寫入過程中發生例外，檔案可能未關閉。建議使用 `with open(path, 'w') as f:` 來確保資源釋放。

**判斷依據**：diff 第 66-70 行：未使用 context manager。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 一定有 additions 和 changed_files 鍵</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 API 回應可能缺少這些鍵（例如權限不足或欄位未包含），導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式。

**判斷依據**：diff 第 51-53 行：直接索引字典。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉型失敗</summary>

`threshold_from_env` 直接將環境變數 `PR_STALE_DAYS` 轉為整數，若值不是有效整數（如 "abc"），會拋出 `ValueError` 導致程式終止。建議捕捉例外並回退到預設值或提供明確錯誤訊息。

**判斷依據**：diff 第 45 行：`int(raw)` 未包在 try-except 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:81</code> main 未驗證命令列參數，可能導致 IndexError</summary>

`main` 直接使用 `sys.argv[1]` 和 `sys.argv[2:]`，若使用者未提供足夠參數，會拋出 `IndexError`。建議檢查參數數量並提供使用說明。

**判斷依據**：diff 第 82-83 行：未檢查 `len(sys.argv)`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3228 (cache hit 1408) ｜ completion tokens 1891</sub>