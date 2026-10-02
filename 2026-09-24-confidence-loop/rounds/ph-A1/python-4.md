<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 且指令由外部輸入拼接）、以及可變預設值（seen=[]）可能造成跨呼叫污染。此外，資源管理（export_csv 未使用 with）和輸入驗證（環境變數轉型）也需要改善。最優先應修復 _fetch 的例外處理與 archive 的 shell 注入風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫污染 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，例外時可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉型未處理例外，可能導致程式崩潰 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 PR 一定有 additions 和 changed_files 欄位 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續的 `pr["user"]["login"]` 或 `pr["additions"]` 會拋出 `TypeError`，且原始錯誤被隱藏，難以除錯。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 若預期可能失敗，讓 `_fetch` 回傳 `None` 並在呼叫端檢查。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 72 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令由外部輸入拼接，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（`sys.argv[1]`），完全由使用者控制。攻擊者可注入額外命令，例如 `repo` 設為 `x; rm -rf /`，導致任意命令執行。

建議：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若必須使用 shell，請對輸入進行嚴格驗證或使用 `shlex.quote`。

**判斷依據**：diff 第 61 行：`subprocess.run` 使用 `shell=True`，且 f-string 中包含 `repo`（來自 `sys.argv[1]`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫污染</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值。若呼叫者未傳入 `seen`，則每次呼叫都會共用同一個 list，導致結果累積。例如連續呼叫 `collect_authors(repo, [1])` 和 `collect_authors(repo, [2])`，第二次呼叫會回傳 `[author1, author2]` 而非 `[author2]`。

建議：將預設值改為 `None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：參數 `seen=[]` 為可變預設值，且函式內對其進行 `append` 操作（第 30 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若在寫入過程中發生例外（例如磁碟滿、權限不足），`close` 不會被執行，導致檔案控制代碼洩漏。

建議：使用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 55-59 行：手動 `open`/`close`，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉型未處理例外，可能導致程式崩潰</summary>

`threshold_from_env` 中 `int(raw)` 若 `raw` 不是有效整數（例如使用者設定 `PR_STALE_DAYS=abc`），會拋出 `ValueError` 且未被捕捉，導致程式終止。

建議：捕捉 `ValueError` 並提供有意義的錯誤訊息，或使用預設值。

**判斷依據**：diff 第 45 行：`int(raw)` 直接轉換環境變數，無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 一定有 additions 和 changed_files 欄位</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但若 API 回應缺少這些欄位（例如權限不足或 API 變更），會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 和 `pr.get("changed_files", 0)` 提供預設值。

**判斷依據**：diff 第 50-52 行：直接使用鍵值存取，無預設值或檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1763 ｜ PR #12</sub>