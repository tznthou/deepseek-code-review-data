<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未使用 with）。此外，環境變數轉換未處理例外、CSV 輸出未跳脫、以及 review_latency 依賴不存在的 timeline 欄位，都可能導致執行期錯誤或資料不正確。建議優先修正安全性與錯誤處理問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:22` | 例外被吞掉且回傳 None，導致後續程式碼崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 `seen=[]` 導致跨呼叫狀態污染 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換未處理例外，可能導致程式崩潰 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:72` | CSV 輸出未跳脫，可能導致格式錯誤或注入 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 依賴不存在的 timeline 欄位，可能回傳 0 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 函式對 additions 和 changed_files 的判斷可能不完整 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:22</code> 例外被吞掉且回傳 None，導致後續程式碼崩潰</summary>

`_fetch` 函式中的 `except:` 區塊只有 `pass`，沒有記錄錯誤或重新拋出。當 API 請求失敗（例如網路問題、HTTP 錯誤、JSON 解析失敗）時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，例如 `pr["user"]["login"]`，會引發 `TypeError`。這使得錯誤難以診斷，且程式會在非預期處崩潰。

建議：
- 至少記錄錯誤（使用 `logging` 模組）並重新拋出例外，或回傳一個明確的錯誤值。
- 避免使用裸 `except:`，應捕捉具體例外（如 `urllib.error.URLError`, `json.JSONDecodeError`）。

**判斷依據**：diff 第 22-23 行：`except:` 後只有 `pass`，且函式沒有其他回傳值，隱含回傳 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 並設定 `shell=True`，且指令字串中包含 `repo` 和 `path` 變數。這些變數來自命令列參數（`repo`）和內部產生的路徑（`path`），但 `repo` 完全由使用者控制。攻擊者可以提供惡意的 `repo` 值，例如 `"; rm -rf / #"`，導致任意指令執行。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`。
- 如果必須使用 shell，請對所有外部輸入進行嚴格的驗證和轉義。

**判斷依據**：diff 第 67 行：`shell=True` 且 f-string 包含外部輸入 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 `seen=[]` 導致跨呼叫狀態污染</summary>

`collect_authors` 的參數 `seen` 預設為空列表，這是一個可變物件。在 Python 中，預設值只會在函式定義時建立一次，之後每次呼叫都會共用同一個列表。如果呼叫者沒有傳入 `seen`，則每次呼叫都會將作者名稱累加到同一個列表中，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 27 行：參數 `seen=[]` 使用可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，可能導致資源洩漏</summary>

`export_csv` 函式使用 `open` 開啟檔案，但沒有使用 `with` 語句。如果在寫入過程中發生例外（例如磁碟已滿、權限錯誤），檔案不會被正確關閉，可能導致資料遺失或檔案鎖定。

建議：使用 `with open(path, "w") as f:` 來確保檔案總會被關閉。

**判斷依據**：diff 第 61-65 行：手動 `open` 和 `close`，沒有例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換未處理例外，可能導致程式崩潰</summary>

`threshold_from_env` 函式直接使用 `int(raw)` 將環境變數 `PR_STALE_DAYS` 轉換為整數。如果該變數不是有效的整數（例如設定為 "abc"），會拋出 `ValueError`，導致程式終止。

建議：使用 try-except 捕捉轉換錯誤，並提供合理的預設值或錯誤訊息。

**判斷依據**：diff 第 38 行：`int(raw)` 沒有例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:72</code> CSV 輸出未跳脫，可能導致格式錯誤或注入</summary>

`export_csv` 直接使用 f-string 將 `author`、`latency`、`kind` 寫入 CSV 檔案。如果 `author` 包含逗號、換行或引號，會破壞 CSV 格式。此外，如果這些值來自外部（例如 GitHub 使用者名稱），可能包含惡意內容，在後續處理（如用試算表開啟）時造成風險。

建議：使用 `csv` 模組的 `writer` 來正確處理跳脫。

**判斷依據**：diff 第 63 行：直接字串拼接，未使用 csv 模組。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 依賴不存在的 timeline 欄位，可能回傳 0</summary>

`review_latency` 函式使用 `pr.get("timeline", [])` 取得事件列表。但 GitHub API 的 Pull Request 物件通常不包含 `timeline` 欄位（需要另外請求 timeline 端點）。因此 `events` 會是空列表，函式回傳 0，導致延遲計算不正確。

建議：確認 API 回應結構，或另外請求 timeline 資料。

**判斷依據**：diff 第 33 行：`pr.get("timeline", [])` 可能永遠為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 函式對 additions 和 changed_files 的判斷可能不完整</summary>

`classify` 函式先檢查 `additions > 500` 回傳 "large"，再檢查 `changed_files > 20` 回傳 "wide"。如果一個 PR 同時滿足兩個條件，只會回傳 "large"，可能不是預期的分類。此外，`title.startswith("fix")` 是大小寫敏感的，可能漏掉 "Fix" 開頭的標題。

建議：確認分類優先順序是否符合需求，並考慮使用不區分大小寫的比對。

**判斷依據**：diff 第 45-50 行：條件判斷順序和大小寫敏感。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3355 (cache hit 256) ｜ completion tokens 2265 ｜ PR #12</sub>