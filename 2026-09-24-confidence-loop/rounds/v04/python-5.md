<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確關閉。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們可能導致資料不正確或安全問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉換失敗 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 pr 一定有 additions 和 changed_files 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 函式中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（如 `collect_authors` 和 `main` 中的 `pr["user"]["login"]`）會因為 `None` 而拋出 `TypeError`，且錯誤訊息不明確。

建議：
- 至少記錄例外（使用 `logging` 模組）。
- 重新拋出例外或讓呼叫端處理。
- 避免使用裸 `except:`，改為捕捉特定例外（如 `urllib.error.URLError`、`json.JSONDecodeError`）。

**判斷依據**：diff 第 24 行：`except:` 後直接 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，這些值來自命令列參數（`repo`）或由 `repo` 衍生（`path`）。攻擊者可以注入額外的 shell 指令，例如 `repo` 設為 `foo; rm -rf /`。

建議：
- 避免使用 `shell=True`，改用參數列表傳遞：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])
```
- 如果必須使用 shell，請對輸入進行嚴格的驗證或轉義。

**判斷依據**：diff 第 76 行：`shell=True` 且指令字串由外部輸入拼接。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，會在函式定義時建立一次，並在所有呼叫之間共用。如果呼叫多次，前一次的結果會殘留在 `seen` 中，導致後續呼叫的結果不正確。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 29 行：參數 `seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，如果在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，造成資源洩漏。

建議：使用 `with` 語句：
```python
with open(path, "w") as f:
    f.write(...)
```

**判斷依據**：diff 第 68-72 行：手動開啟和關閉檔案，沒有使用 `with`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉換失敗</summary>

`threshold_from_env` 直接使用 `int(raw)` 轉換環境變數 `PR_STALE_DAYS`，如果該變數不是有效的整數（例如設為 `abc`），會拋出 `ValueError` 且程式終止。

建議：捕捉 `ValueError` 並提供預設值或明確的錯誤訊息。

**判斷依據**：diff 第 44 行：`int(raw)` 沒有例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 一定有 additions 和 changed_files 欄位</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，如果 API 回應中缺少這些欄位（例如權限不足或 API 變更），會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 和 `pr.get("changed_files", 0)` 提供預設值。

**判斷依據**：diff 第 50-52 行：直接使用鍵值存取，沒有預設值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 3200) ｜ completion tokens 1645 ｜ PR #12</sub>