<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入風險（archive 函式）、以及資源未正確釋放（export_csv 未使用 with）。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理 int() 轉換失敗 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式假設 pr 字典一定有 additions、changed_files、title 鍵 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 函式中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。這會導致呼叫端（如 `collect_authors` 和 `main` 中的 `pr["user"]["login"]`）在 `_fetch` 回傳 `None` 時拋出 `TypeError` 或 `KeyError`，且沒有明確的錯誤訊息。

建議：
- 至少記錄例外並重新拋出，或回傳一個明確的錯誤值。
- 使用 `raise ... from err` 保留原始追蹤資訊。
- 考慮使用 `urllib.error.HTTPError` 來處理特定的 HTTP 狀態碼。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path`，這兩個參數來自命令列參數或內部變數。如果 `repo` 包含惡意內容（例如 `; rm -rf /`），就可能執行任意指令。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 如果必須使用 shell，請對輸入進行嚴格的驗證或轉義。

**判斷依據**：diff 第 72 行：`shell=True` 且指令字串由 f-string 組成，包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，會在多次呼叫之間共用同一個 list。這可能導致非預期的行為，例如第二次呼叫時會包含第一次的結果。

建議：將預設值改為 `None`，並在函式內初始化為空 list：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 29 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，但如果在寫入過程中發生例外，檔案可能不會被關閉。

建議：使用 `with open(path, "w") as f:` 來確保檔案總是被關閉。

**判斷依據**：diff 第 64-68 行：手動 open/close，沒有使用 with。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理 int() 轉換失敗</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，如果該值不是有效的整數（例如 "abc"），會拋出 `ValueError` 且沒有處理。

建議：使用 try/except 捕捉轉換錯誤，並提供預設值或明確的錯誤訊息。

**判斷依據**：diff 第 51 行：`int(raw)` 沒有例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式假設 pr 字典一定有 additions、changed_files、title 鍵</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，如果 API 回應缺少這些鍵（例如權限不足或 API 變更），會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 56-61 行：直接使用鍵存取，沒有檢查鍵是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 3200) ｜ completion tokens 1622 ｜ PR #12</sub>