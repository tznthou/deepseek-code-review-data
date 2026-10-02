<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的小工具。主要風險在於：例外處理不當（_fetch 吞掉所有錯誤）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源管理（export_csv 未使用 with）。建議先修正這些問題再合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 pr 一定有 additions 和 changed_files 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict 存取，若 `_fetch` 失敗，會拋出 `TypeError` 或 `KeyError`，且沒有原始錯誤資訊。

建議：
- 至少記錄錯誤（`logging.exception`）並重新拋出或回傳 None，讓呼叫端處理。
- 檢查 HTTP 狀態碼（`resp.status`），非 2xx 時拋出例外。
- 避免裸 `except:`，改為捕捉具體例外（`urllib.error.URLError`, `json.JSONDecodeError`）。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，這些值來自命令列參數（`sys.argv`），攻擊者可注入任意 shell 指令。例如 `repo` 設為 `x; rm -rf /` 會導致嚴重後果。

建議：
- 避免 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若需執行 `gh`，也應使用參數列表並分開呼叫。
- 驗證 `repo` 格式（例如只允許 `owner/repo` 字元）。

**判斷依據**：diff 第 72 行：`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積</summary>

`collect_authors` 的 `seen` 參數預設為空 list，這是可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會將作者加到同一個 list，導致結果累積。

建議：改為 `seen=None`，在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程拋出例外（例如磁碟滿），檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 63-67 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若值不是整數（例如 "abc"），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 44 行：`int(raw)` 無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 一定有 additions 和 changed_files 欄位</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 GitHub API 的回應可能缺少這些欄位（例如某些事件或權限不足），導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 50-52 行：直接索引字典。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1561 ｜ PR #12</sub>