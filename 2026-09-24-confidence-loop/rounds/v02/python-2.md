<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell=True 的指令注入（archive 函式）、以及資源管理（export_csv 未使用 with）。此外，classify 函式直接存取 pr['additions'] 等鍵，若 API 回應缺少這些欄位會拋出 KeyError。建議優先修正安全性與錯誤處理問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:20` | 例外被吞掉，導致後續程式碼在資料缺失時崩潰 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設參數 seen=[] 導致跨呼叫狀態累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，例外時可能外洩資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取可能不存在的鍵 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 參數（來自命令列參數）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`，導致任意指令執行。

建議改為不使用 shell，直接傳遞參數清單：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])
```

**判斷依據**：diff 第 60 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自 `sys.argv[1]`，未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:20</code> 例外被吞掉，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 函式在 `try` 區塊中捕捉所有例外後僅執行 `pass`，沒有記錄或重新拋出。當 API 請求失敗（例如網路錯誤、token 無效、PR 不存在）時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，例如 `pr["user"]["login"]`，會拋出 `TypeError`。

建議至少記錄錯誤並拋出例外，或讓呼叫端檢查回傳值。

**判斷依據**：diff 第 20-21 行：`except:` 後僅有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 27 行）和 `main`（第 72 行）被直接使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設參數 seen=[] 導致跨呼叫狀態累積</summary>

`collect_authors` 的 `seen` 參數預設為空串列，這是可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會將作者加到同一個串列中，造成結果不正確。

建議改為 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 25 行：`def collect_authors(repo, numbers, seen=[]):`，且函式內有 `seen.append(...)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，例外時可能外洩資源</summary>

`export_csv` 使用 `open` 開啟檔案，但沒有使用 `with` 或 `try/finally` 確保關閉。若寫入過程中發生例外，檔案控制代碼不會被釋放。

建議改為：
```python
with open(path, "w") as f:
    ...
```

**判斷依據**：diff 第 55 行：`f = open(path, "w")`，且後續沒有 `with` 或 `finally`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取可能不存在的鍵</summary>

`classify` 函式直接使用 `pr["additions"]`、`pr["changed_files"]` 和 `pr["title"]`。GitHub API 的回應不一定包含這些欄位（例如某些事件或權限不足時），會拋出 `KeyError`。

建議使用 `.get()` 並提供預設值，或先驗證鍵是否存在。

**判斷依據**：diff 第 41 行：`if pr["additions"] > 500:`，且 `pr` 來自 `_fetch` 的回傳值，可能為 `None` 或缺少鍵。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

`threshold_from_env` 中 `int(raw)` 可能拋出 `ValueError`，若環境變數 `PR_STALE_DAYS` 不是有效整數，程式會崩潰。

建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 35 行：`return {"days": int(raw)}`，且 `raw` 來自環境變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 0) ｜ completion tokens 1572 ｜ PR #12</sub>