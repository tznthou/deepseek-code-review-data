<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外、archive 使用 shell=True 且未檢查回傳值）、可變預設值（collect_authors 的 seen=[]）、以及資源管理（export_csv 未使用 with）。此外，classify 對 title.startswith('fix') 的判斷可能誤分類，且 review_latency 依賴 timeline 欄位但 API 預設不回傳。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:26` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，例外時可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 依賴 timeline 欄位，但 GitHub API 預設不回傳，導致延遲永遠為 0 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:63` | classify 使用 title.startswith('fix') 可能誤分類（如 'fixed'、'fixer'） | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:26</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except:` 區塊只有 `pass`，沒有記錄或重新拋出。當網路錯誤、API 回傳非 2xx、或 JSON 解析失敗時，函式會回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr.get(...)`，若 `pr` 為 `None` 會拋出 `TypeError` 或 `AttributeError`，且原始錯誤被隱藏，難以除錯。

**失敗情境**：GitHub API 暫時性故障（如 503）或 token 無效時，`_fetch` 回傳 `None`，`collect_authors` 在 `seen.append(pr["user"]["login"])` 處拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

**建議**：至少記錄例外並重新拋出，或讓 `_fetch` 拋出明確的例外，由呼叫端處理。例如：
```python
except Exception as e:
    raise RuntimeError(f"Failed to fetch {path}: {e}") from e
```

**判斷依據**：diff 第 26-27 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 31 行）和 `main`（第 75 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 參數，該參數來自命令列輸入（`sys.argv[1]`），完全由使用者控制。攻擊者可注入任意 shell 指令，例如傳入 `repo` 為 `foo; rm -rf /` 或 `$(malicious)`。

**失敗情境**：使用者執行 `python3 pr_stats.py 'repo; touch /tmp/pwned' 1`，`archive` 會執行 `tar czf /tmp/pr-stats-repo; touch /tmp/pwned.tgz ...`，導致任意指令執行。

**建議**：避免使用 `shell=True`，改用參數列表傳遞，並驗證 `repo` 格式。例如：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path], check=True)
subprocess.run(["gh", "repo", "view", repo], check=True)
```

**判斷依據**：diff 第 65 行：`subprocess.run` 使用 `shell=True`，且 f-string 包含 `repo`（來自 `sys.argv[1]`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若函式被多次呼叫（例如在同一個程序內處理多個 repo），`seen` 會不斷累積先前呼叫的作者，導致結果錯誤。

**失敗情境**：第一次呼叫 `collect_authors('repo1', [1,2])` 回傳 `['alice', 'bob']`；第二次呼叫 `collect_authors('repo2', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

**建議**：改用 `None` 作為預設值，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 29 行：函式定義使用可變預設值 `seen=[]`，且函式內對 `seen` 進行 `append` 修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 開啟檔案，但沒有使用 `with` 或 `try/finally` 確保關閉。若在寫入過程中發生例外（例如磁碟滿、權限不足），檔案控制代碼不會被關閉，可能導致資源洩漏或資料不完整。

**失敗情境**：寫入時發生 `OSError`，程式終止，檔案可能未完整寫入且控制代碼未釋放。

**建議**：使用 `with open(path, "w") as f:` 自動管理資源。

**判斷依據**：diff 第 58-62 行：手動 `open` 和 `close`，沒有例外安全。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 依賴 timeline 欄位，但 GitHub API 預設不回傳，導致延遲永遠為 0</summary>

`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub Pull Request API 的回應中並無 `timeline` 欄位（需另外請求 timeline 端點）。因此 `events` 永遠是空列表，函式回傳 0，指標失去意義。

**失敗情境**：所有 PR 的 latency 都顯示為 0，無法反映實際審查時間。

**建議**：若要取得 timeline，需額外呼叫 `/repos/{repo}/issues/{n}/timeline` 或使用 GraphQL；或改用其他可用欄位（如 `created_at` 與 `closed_at`）。

**判斷依據**：diff 第 43 行：`pr.get("timeline", [])`，但 `_fetch` 只請求 `/repos/{repo}/pulls/{n}`，該端點回應不含 `timeline`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:63</code> classify 使用 title.startswith('fix') 可能誤分類（如 'fixed'、'fixer'）</summary>

`classify` 判斷 `pr["title"].startswith("fix")`，這會將標題開頭為 'fixed'、'fixer'、'fixing' 等字詞的 PR 也歸類為 'fix'，可能不是預期行為。

**失敗情境**：標題為 "Fixed typo in README" 的 PR 會被分類為 'fix'，但若預期只有 'fix' 開頭才算，則結果不正確。

**建議**：使用更精確的判斷，例如 `pr["title"].lower().startswith("fix ")` 或正則表達式。

**判斷依據**：diff 第 70 行：`startswith("fix")` 未考慮單詞邊界。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 2233 ｜ PR #12</sub>