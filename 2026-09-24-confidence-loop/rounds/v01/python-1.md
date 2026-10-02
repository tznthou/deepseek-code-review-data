<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於：錯誤處理幾乎全面失效（_fetch 吞掉所有例外、archive 使用 shell=True 且未檢查回傳值）、可變預設值 seen=[] 造成跨呼叫污染、以及 export_csv 未使用 with 管理檔案資源。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，呼叫端無法得知失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且未檢查回傳值，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 造成跨呼叫污染 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理無效的環境變數值 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 對 pr 欄位存取可能因缺失鍵而崩潰 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，呼叫端無法得知失敗</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），導致呼叫端拿到 `None` 或未定義的 `pr`，後續程式碼會因 `pr["user"]` 拋出 `TypeError` 或 `KeyError`。例如：GitHub API 回傳 404 時，`urlopen` 會拋出 `HTTPError`，但被 `pass` 吞掉，`_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]` 就會崩潰。建議：至少記錄錯誤並重新拋出，或回傳明確的錯誤值，讓呼叫端能處理。

**判斷依據**：diff 第 24 行顯示 `except:` 後只有 `pass`，且 `_fetch` 的呼叫端（如 `collect_authors` 第 28 行）直接使用回傳值，沒有檢查是否為 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且未檢查回傳值，存在命令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 使用 `shell=True` 且字串由外部輸入（`repo` 和 `path`）拼接，攻擊者可注入額外命令。例如：`repo` 為 `x; rm -rf /` 時，會執行 `tar ... && gh repo view x; rm -rf /`。此外，未檢查 `subprocess.run` 的回傳值，即使 `tar` 或 `gh` 失敗，程式仍會繼續執行並回報成功。建議：改用參數列表形式（`shell=False`）並檢查回傳值，或使用 `shlex.quote` 進行轉義。

**判斷依據**：diff 第 72 行顯示 `shell=True` 且 f-string 包含 `repo` 和 `path`，這些值來自命令列參數，未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 造成跨呼叫污染</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，會在多次呼叫間共用同一個 list。如果呼叫者沒有傳入 `seen`，每次呼叫都會把新作者附加到同一個 list 上，導致結果累積。例如：第一次呼叫 `collect_authors(repo, [1])` 回傳 `['alice']`，第二次呼叫 `collect_authors(repo, [2])` 會回傳 `['alice', 'bob']` 而不是 `['bob']`。建議改用 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 30 行顯示 `seen=[]`，且函式內有 `seen.append(...)`，會修改該 list。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，造成資源洩漏。建議改用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 65-69 行顯示手動 `open`/`close`，沒有使用 `with`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理無效的環境變數值</summary>

`threshold_from_env` 直接 `int(raw)`，若環境變數 `PR_STALE_DAYS` 不是有效整數（例如 `abc`），會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 48 行顯示 `int(raw)` 沒有 try/except 保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 對 pr 欄位存取可能因缺失鍵而崩潰</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，若 API 回傳的 JSON 缺少這些鍵（例如 API 版本變更或部分 PR 沒有這些欄位），會拋出 `KeyError`。建議使用 `.get()` 或先驗證資料結構。

**判斷依據**：diff 第 53-58 行顯示直接使用 `pr[...]` 存取，沒有防禦性檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3409 (cache hit 640) ｜ completion tokens 1695 ｜ PR #12</sub>