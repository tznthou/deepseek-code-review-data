<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外、collect_authors 的預設參數可變）、安全性問題（shell=True 的指令注入、token 可能外洩）、以及資源管理（export_csv 未使用 with）。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 指令注入。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，呼叫端無法得知失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值，跨呼叫累積結果 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:21` | GITHUB_TOKEN 可能未設定，導致 KeyError | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的例外 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，呼叫端無法得知失敗</summary>

`_fetch` 的 `except:` 區塊只有 `pass`，任何網路錯誤、HTTP 錯誤、JSON 解析錯誤都會被吞掉，函式回傳 `None`。後續程式碼（如 `collect_authors` 中的 `pr["user"]["login"]`）會因為 `pr` 是 `None` 而拋出 `TypeError`，但真正的錯誤原因已被隱藏。

失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 嘗試存取 `None["user"]` 導致 `TypeError`，使用者只看到無意義的錯誤，無法得知是 API 失敗。

建議：不要捕捉所有例外，或至少記錄錯誤並重新拋出。例如：
```python
except Exception as e:
    raise RuntimeError(f"Failed to fetch {path}: {e}") from e
```

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳任何錯誤指示。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，這兩個參數來自命令列參數（`sys.argv`），屬於外部輸入。攻擊者可以注入額外的 shell 指令。

失敗情境：如果使用者執行 `python3 pr_stats.py 'repo; rm -rf /' 1`，`repo` 的值會讓指令變成 `tar czf /tmp/pr-stats-repo; rm -rf /.tgz /tmp/pr-stats-repo; rm -rf / && gh repo view repo; rm -rf /`，導致任意指令執行。

建議：避免使用 `shell=True`，改用參數列表傳遞，並分開執行 `tar` 和 `gh`：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path], check=True)
subprocess.run(["gh", "repo", "view", repo], check=True)
```

**判斷依據**：diff 第 61 行：`shell=True` 且 f-string 包含外部輸入 `repo` 和 `path`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值，跨呼叫累積結果</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，每次呼叫都會共用同一個 list。如果這個函式被多次呼叫（例如在同一個行程中處理多個 repo），結果會累積，導致資料污染。

失敗情境：第一次呼叫 `collect_authors('repo1', [1,2])` 回傳 `['user1','user2']`，第二次呼叫 `collect_authors('repo2', [3])` 會回傳 `['user1','user2','user3']`，而不是只有 `['user3']`。

建議：使用 `None` 作為預設值，在函式內建立新的 list：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：參數 `seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，如果在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，造成資源洩漏。

失敗情境：當 `f.write` 拋出例外（如 `OSError`），函式會直接中斷，檔案控制代碼沒有被釋放，可能導致後續操作失敗或檔案鎖定。

建議：使用 `with` 陳述式：
```python
with open(path, "w") as f:
    f.write(...)
```

**判斷依據**：diff 第 55-59 行：手動 `open`/`close`，沒有 `with` 或 `try/finally`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:21</code> GITHUB_TOKEN 可能未設定，導致 KeyError</summary>

`_fetch` 直接使用 `os.environ["GITHUB_TOKEN"]`，如果環境變數未設定，會拋出 `KeyError`，且沒有提供任何有用的錯誤訊息。

失敗情境：使用者未設定 `GITHUB_TOKEN` 時，程式在第一次呼叫 `_fetch` 時崩潰，只顯示 `KeyError: 'GITHUB_TOKEN'`，無法得知需要設定 token。

建議：在程式啟動時檢查，或提供預設值與明確錯誤：
```python
token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN environment variable is required")
```

**判斷依據**：diff 第 22 行：直接存取 `os.environ["GITHUB_TOKEN"]`，沒有檢查存在性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的例外</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉成 `int`，如果該值不是合法整數（例如 "abc"），會拋出 `ValueError`，導致程式崩潰。

失敗情境：使用者設定 `PR_STALE_DAYS=abc`，程式在呼叫 `threshold_from_env` 時拋出 `ValueError`，沒有提供任何錯誤訊息。

建議：捕捉轉換例外並提供明確錯誤，或使用預設值：
```python
try:
    days = int(raw)
except ValueError:
    raise ValueError(f"Invalid PR_STALE_DAYS: {raw}") from None
```

**判斷依據**：diff 第 44 行：`int(raw)` 沒有處理轉換失敗。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2033 ｜ PR #12</sub>