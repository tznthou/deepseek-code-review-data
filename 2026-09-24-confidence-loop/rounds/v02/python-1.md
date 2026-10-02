<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源管理（export_csv 未使用 with）。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們可能導致工具靜默失敗或執行任意指令。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的例外 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 pr 一定有 additions、changed_files、title 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 是 `None` 而拋出 `TypeError`，且沒有提供任何錯誤訊息，讓使用者難以除錯。

建議：
- 至少記錄例外（例如 `logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 考慮使用 `requests` 函式庫，它會自動拋出 HTTP 錯誤。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path` 參數。這些參數來自命令列參數（`repo`）和內部產生的路徑（`path`），但 `repo` 完全由使用者控制。攻擊者可以提供類似 `foo; rm -rf /` 的 repo 名稱，導致任意指令執行。

建議：
- 避免使用 `shell=True`，改用參數列表：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`。
- 如果必須使用 shell，請對參數進行嚴格的驗證或轉義。

**判斷依據**：diff 第 78 行：`shell=True` 且 f-string 包含外部輸入 `repo`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，會在函式定義時建立一次，並在所有呼叫之間共用。如果呼叫者沒有傳入 `seen`，每次呼叫都會將作者加到同一個 list 中，導致結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，如果 `f.write` 拋出例外（例如磁碟已滿），`f.close()` 不會被執行，導致檔案控制代碼洩漏。

建議：使用 `with open(path, "w") as f:` 來自動關閉檔案。

**判斷依據**：diff 第 71-75 行：手動 open/close，沒有 with。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的例外</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，如果該值不是合法整數（例如 "abc"），會拋出 `ValueError`，導致程式崩潰。

建議：捕捉 `ValueError` 並提供預設值或錯誤訊息。

**判斷依據**：diff 第 44 行：`int(raw)` 沒有例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 一定有 additions、changed_files、title 欄位</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但這些欄位可能不存在（例如 API 回應格式變更或某些 PR 缺少這些資料）。如果缺少，會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 50-55 行：直接使用鍵存取，沒有檢查鍵是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 0) ｜ completion tokens 1698 ｜ PR #12</sub>