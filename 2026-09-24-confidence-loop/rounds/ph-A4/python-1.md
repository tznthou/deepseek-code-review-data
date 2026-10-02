<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未使用 with）。此外，review_latency 依賴不存在的 timeline 欄位，可能導致 KeyError。建議優先修正這些問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:22` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設參數 seen=[] 導致跨呼叫共用狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 使用不存在的 timeline 欄位，可能拋出 KeyError | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr["additions"] 等鍵，可能因鍵不存在而拋出 KeyError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:83` | main 中重複呼叫 _fetch 取得相同 PR 資料，造成不必要的 API 請求 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:22</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 為 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息。

建議：
- 至少記錄錯誤（使用 `logging`）並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 避免使用裸 `except:`，改為捕捉具體例外（如 `urllib.error.URLError`, `json.JSONDecodeError`）。

**判斷依據**：diff 第 22-23 行：`except:` 後直接 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中的 `repo` 來自命令列參數，攻擊者可注入任意 shell 指令（例如 `repo = "x; rm -rf /"`）。此外，`path` 也可能包含特殊字元。

建議：避免使用 `shell=True`，改用參數列表形式，並分開執行 `tar` 和 `gh` 指令。

**判斷依據**：diff 第 63 行：`shell=True` 且 f-string 包含外部輸入 `repo` 和 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設參數 seen=[] 導致跨呼叫共用狀態</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值。Python 在函式定義時只建立一次該 list，因此多次呼叫會共用同一個 list，導致結果累積且難以預測。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 26 行：`seen=[]` 是可變預設參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 使用不存在的 timeline 欄位，可能拋出 KeyError</summary>

`pr.get("timeline", [])` 嘗試取得 `timeline` 欄位，但 GitHub Pull Request API 的回應中並無此欄位（需另外請求 timeline 端點）。因此 `events` 永遠是空 list，`review_latency` 永遠回傳 0。若未來 API 變更或誤用，可能導致 `KeyError`。

建議：確認正確的資料來源，或移除該函式。

**判斷依據**：diff 第 31 行：`pr.get("timeline", [])` 中的 `timeline` 並非標準 PR 物件欄位。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`int(raw)` 直接轉換環境變數 `PR_STALE_DAYS` 的值，若該值不是合法整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式崩潰。

建議：使用 try/except 捕捉轉換錯誤，或提供預設值。

**判斷依據**：diff 第 47 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr["additions"] 等鍵，可能因鍵不存在而拋出 KeyError</summary>

`pr["additions"]`、`pr["changed_files"]`、`pr["title"]` 直接使用索引存取，若 API 回應缺少這些欄位（例如權限不足或 API 變更），會拋出 `KeyError`。

建議：使用 `.get()` 並提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 51 行：直接索引存取 `pr["additions"]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`open(path, "w")` 沒有使用 `with` 語句，若寫入過程中發生例外，檔案不會被正確關閉，可能導致資料遺失或檔案鎖定。

建議：改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 58 行：`open` 未搭配 `with`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:83</code> main 中重複呼叫 _fetch 取得相同 PR 資料，造成不必要的 API 請求</summary>

`collect_authors` 和後續的迴圈都對每個 PR 呼叫 `_fetch`，導致每個 PR 被請求兩次。這不僅浪費 API 配額，也可能因速率限制而失敗。

建議：先一次取得所有 PR 資料，再分別計算作者和指標。

**判斷依據**：diff 第 72 行和 76-77 行：重複的 `_fetch` 呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1961 ｜ PR #12</sub>