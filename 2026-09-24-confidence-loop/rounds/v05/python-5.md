<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及資源未正確釋放（export_csv 未使用 with）。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們會直接影響工具的正確性與安全性。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，例外時可能未關閉 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的例外 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 對 pr 欄位存取可能因缺失鍵而拋出 KeyError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，當 `_fetch` 失敗時會得到 `None`，接著存取 `pr["user"]` 或 `pr["additions"]` 會拋出 `TypeError`，造成程式崩潰。

**失敗情境**：網路中斷、API 回傳 404（PR 不存在）、token 無效、回應不是合法 JSON 時，程式會以未處理的例外結束。

**建議**：
- 讓 `_fetch` 在失敗時拋出例外（不要 `pass`），或回傳一個明確的錯誤值，並在呼叫端檢查。
- 至少記錄錯誤訊息（例如 `logging.exception`）以便除錯。
- 考慮使用 `raise ... from err` 保留原始例外資訊。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，沒有回傳值或重新拋出。呼叫端如第 29 行 `pr = _fetch(...)` 後直接 `pr["user"]`，若 `_fetch` 回傳 `None` 會拋出 `TypeError`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令包含外部輸入，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串由 `path` 和 `repo` 拼接而成。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可以注入額外指令。

**失敗情境**：若使用者執行 `python pr_stats.py 'repo; rm -rf /' 1`，`repo` 中的分號會讓 shell 執行 `rm -rf /`。

**建議**：
- 避免使用 `shell=True`，改用參數列表傳遞：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])
```
- 若必須使用 shell，請對輸入進行嚴格的驗證或轉義。

**判斷依據**：diff 第 72 行：`shell=True` 且 f-string 包含 `repo`（來自 `sys.argv[1]`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫累積</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，該 list 在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留，造成結果不正確。

**失敗情境**：若在同一個程序內呼叫 `collect_authors` 兩次（例如處理多個 repo），第二次呼叫的結果會包含第一次的作者。

**建議**：改用 `None` 作為預設值，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值，且函式內有 `seen.append(...)` 修改該 list。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，例外時可能未關閉</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，可能造成資源洩漏或資料不完整。

**建議**：使用 `with` 陳述式：
```python
with open(path, "w") as f:
    f.write(...)
```

**判斷依據**：diff 第 64-68 行：手動 `open` 和 `close`，沒有 `with` 或 `try/finally`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的例外</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若該值不是合法整數（例如 "abc" 或空字串），會拋出 `ValueError`，導致程式崩潰。

**失敗情境**：使用者設定 `PR_STALE_DAYS=abc` 時，程式會以未處理的例外結束。

**建議**：捕捉 `ValueError` 並提供預設值或錯誤訊息：
```python
try:
    days = int(raw)
except ValueError:
    days = 7  # 或記錄警告
```

**判斷依據**：diff 第 48 行：`int(raw)` 沒有例外處理，`raw` 來自環境變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 對 pr 欄位存取可能因缺失鍵而拋出 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 GitHub API 的回應可能因權限或 PR 類型而缺少這些欄位（例如某些事件可能沒有 `additions`）。若鍵不存在，會拋出 `KeyError`。

**建議**：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 53-58 行：直接使用 `pr[...]` 存取，沒有檢查鍵是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2005 ｜ PR #12</sub>