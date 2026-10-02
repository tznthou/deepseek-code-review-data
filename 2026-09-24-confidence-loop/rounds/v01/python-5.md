<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 的指令注入、token 可能外洩）、以及可變預設值導致的狀態污染。最該先修的是 _fetch 的例外處理和 archive 的 shell 指令，因為它們可能造成資料不正確或安全漏洞。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr 的鍵，若鍵不存在會拋出 KeyError | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能外洩資源 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:21` | Authorization header 直接使用環境變數，若未設定會拋出 KeyError | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，且沒有提供任何錯誤訊息。建議：移除 `try/except`，讓例外向上傳播；或至少記錄錯誤並重新拋出。

**判斷依據**：diff 第 20-24 行顯示 `_fetch` 的 `except: pass`，而 `collect_authors`（第 28 行）和 `main`（第 71 行）直接使用回傳值，沒有檢查是否為 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外指令，例如 `repo = "x; rm -rf /"`。建議：改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 62 行顯示 `shell=True` 且指令字串由外部輸入拼接。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的預設參數 `seen=[]` 在函式定義時建立一次，之後每次呼叫都會共用同一個 list。如果函式被多次呼叫（例如在同一個程序內處理多個 repo），先前呼叫的結果會殘留，導致作者清單不正確。建議：改用 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 28 行顯示可變預設值 `seen=[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> threshold_from_env 的預設值為可變 dict，且 int() 轉換可能拋出例外</summary>

`threshold_from_env` 的預設參數 `default={"days": 7}` 是可變 dict，雖然函式內沒有修改它，但若未來修改可能造成跨呼叫污染。此外，`int(raw)` 若環境變數不是整數會拋出 `ValueError`，導致程式崩潰。建議：改用不可變預設值（如 `None`）並處理轉換例外。

**判斷依據**：diff 第 45-48 行顯示可變預設值和未處理的 `int()` 轉換。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr 的鍵，若鍵不存在會拋出 KeyError</summary>

`classify` 假設 `pr` 字典一定有 `additions`、`changed_files`、`title` 鍵。但 `_fetch` 可能回傳 `None` 或 API 回應缺少這些欄位（例如權限不足或 API 變更），導致程式崩潰。建議：使用 `.get()` 並提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 54-58 行顯示直接存取鍵，而 `_fetch` 可能回傳 `None`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能外洩資源</summary>

`export_csv` 使用 `open()` 和 `close()` 手動管理檔案，若寫入過程中拋出例外（例如磁碟滿），檔案不會被關閉。建議：改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 66-70 行顯示手動檔案管理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:21</code> Authorization header 直接使用環境變數，若未設定會拋出 KeyError</summary>

`_fetch` 使用 `os.environ["GITHUB_TOKEN"]`，若環境變數未設定會拋出 `KeyError`，且沒有提供友善的錯誤訊息。建議：使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 `None`。

**判斷依據**：diff 第 21 行顯示直接存取環境變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3409 (cache hit 640) ｜ completion tokens 1821 ｜ PR #12</sub>