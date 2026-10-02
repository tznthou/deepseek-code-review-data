<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設參數（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確釋放。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設參數，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:83` | main 中重複呼叫 _fetch 造成不必要的 API 請求 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，且未處理寫入錯誤 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式在失敗時回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，且沒有提供任何錯誤訊息。

**失敗情境**：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]` 會拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

**建議**：移除 `try/except`，讓例外自然傳播；或至少記錄錯誤並重新拋出，例如：
```python
except Exception as e:
    print(f"Failed to fetch {path}: {e}", file=sys.stderr)
    raise
```

**判斷依據**：diff 第 24-25 行：`except:` 後直接 `pass`，且函式沒有回傳任何值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可以注入額外的 shell 指令。

**失敗情境**：若使用者執行 `python pr_stats.py 'repo; rm -rf /' 1`，`repo` 的值為 `repo; rm -rf /`，最終執行的指令會是 `tar czf /tmp/pr-stats-repo; rm -rf /.tgz /tmp/pr-stats-repo; rm -rf / && gh repo view repo; rm -rf /`，導致任意指令執行。

**建議**：避免使用 `shell=True`，改用參數列表傳遞，例如：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])
```
或至少對輸入進行嚴格的驗證與轉義。

**判斷依據**：diff 第 70 行：`shell=True` 且 f-string 包含外部輸入 `repo` 和 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設參數，跨呼叫累積資料</summary>

`collect_authors` 的 `seen=[]` 是可變預設參數，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留下來，造成結果不正確。

**失敗情境**：第一次呼叫 `collect_authors('repo', [1,2])` 回傳 `['alice', 'bob']`；第二次呼叫 `collect_authors('repo', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

**建議**：改用 `None` 作為預設值，在函式內建立新 list：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:83</code> main 中重複呼叫 _fetch 造成不必要的 API 請求</summary>

`main` 先呼叫 `collect_authors` 取得作者列表，然後在迴圈中再次呼叫 `_fetch` 取得每個 PR 的詳細資料。這導致每個 PR 被請求兩次，增加 API 呼叫次數與執行時間。

**失敗情境**：若處理大量 PR，會觸發 GitHub API 的 rate limit，導致程式失敗。

**建議**：在 `collect_authors` 中同時回傳 PR 資料，或在 `main` 中只呼叫一次 `_fetch` 並重複使用結果。

**判斷依據**：diff 第 74-80 行：`collect_authors` 內部呼叫 `_fetch`，之後迴圈又再次呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，且未處理寫入錯誤</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。此外，寫入錯誤不會被處理，程式可能靜默失敗。

**失敗情境**：當磁碟空間不足時，`f.write` 拋出 `OSError`，但檔案未被關閉，且程式繼續執行，可能導致後續 `archive` 使用不完整的檔案。

**建議**：使用 `with open(path, "w") as f:` 確保檔案正確關閉，並考慮處理寫入例外。

**判斷依據**：diff 第 82-86 行：手動 open/close，無例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若該值不是合法整數（例如 `abc`），會拋出 `ValueError`，導致程式崩潰。

**失敗情境**：使用者設定 `PR_STALE_DAYS=abc` 時，程式在啟動時即失敗。

**建議**：捕捉 `ValueError` 並提供預設值或錯誤訊息，例如：
```python
try:
    days = int(raw)
except ValueError:
    days = 7
```

**判斷依據**：diff 第 38-40 行：直接 `int(raw)` 無例外處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 2072 ｜ PR #12</sub>