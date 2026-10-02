<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 腳本。主要風險在於：錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及缺少輸入驗證（環境變數轉型、API 回應欄位）。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們可能導致靜默失敗或任意命令執行。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 將環境變數直接轉型為 int，未處理轉換失敗 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr["additions"] 等欄位，未處理缺失鍵 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，例外時可能洩漏資源 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at，未處理空列表或缺失欄位 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回傳任何值。呼叫端（`collect_authors` 和 `main`）直接使用回傳值當作 dict 存取 `pr["user"]["login"]` 等欄位，若 `_fetch` 回傳 `None` 或非 dict，會拋出 `TypeError` 或 `KeyError`，且沒有上下文可除錯。

具體失敗情境：GitHub API 回傳 404（PR 不存在）或 401（token 無效）時，`urlopen` 會拋出 `HTTPError`，被 `except` 吞掉，`_fetch` 回傳 `None`，接著 `pr["user"]` 就會拋出 `TypeError: 'NoneType' object is not subscriptable`。

建議：至少記錄錯誤並重新拋出，或回傳明確的錯誤物件；並在呼叫端檢查回傳值。

**判斷依據**：diff 第 25-26 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串中拼接了 `path` 和 `repo`。這兩個參數來自命令列參數（`repo`）或由 `repo` 衍生（`path`），攻擊者可注入額外 shell 命令。

具體攻擊情境：執行 `python pr_stats.py '$(rm -rf /)' 1` 時，`repo` 的值會被 shell 展開，導致任意命令執行。

建議：改用 `subprocess.run` 的 list 形式，避免 `shell=True`；或使用 `shlex.quote` 對參數進行轉義。

**判斷依據**：diff 第 73 行：`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態</summary>

`collect_authors` 的參數 `seen=[]` 是 Python 的可變預設值，只會在函式定義時建立一次。每次呼叫若未傳入 `seen`，都會共用同一個 list，導致作者名單跨呼叫累積。

具體失敗情境：第一次呼叫 `collect_authors(repo, [1,2])` 回傳 `['alice', 'bob']`；第二次呼叫 `collect_authors(repo, [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

建議：改用 `seen=None`，在函式內判斷 `if seen is None: seen = []`。

**判斷依據**：diff 第 29 行：參數預設值為 `[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 將環境變數直接轉型為 int，未處理轉換失敗</summary>

`threshold_from_env` 讀取環境變數 `PR_STALE_DAYS` 並直接 `int(raw)`。若該變數不是合法整數（例如設為 `abc` 或空字串），會拋出 `ValueError`，導致程式崩潰。

具體失敗情境：使用者設定 `PR_STALE_DAYS=seven` 時，程式在啟動階段就崩潰。

建議：使用 `try/except` 捕捉 `ValueError`，並提供有意義的錯誤訊息或回退到預設值。

**判斷依據**：diff 第 42 行：`int(raw)` 沒有例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr["additions"] 等欄位，未處理缺失鍵</summary>

`classify` 假設 `pr` 字典一定包含 `additions`、`changed_files`、`title` 等鍵。但 GitHub API 的回應可能因權限或 API 版本而缺少這些欄位（例如使用精簡版 PR 物件時）。

具體失敗情境：若 API 回傳的 PR 物件沒有 `additions` 欄位，`pr["additions"]` 會拋出 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 48 行：直接以鍵值存取，未使用 `.get()` 或檢查存在性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案。若在寫入過程中發生例外（例如磁碟滿、權限不足），`f.close()` 不會被執行，導致檔案控制代碼洩漏。

建議：改用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 58-62 行：手動 open/close，無例外保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at，未處理空列表或缺失欄位</summary>

`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 欄位（例如 API 回應格式變更），`events[0]["created_at"]` 會拋出 `KeyError`。

建議：使用 `events[0].get("created_at")` 並檢查是否為 None。

**判斷依據**：diff 第 36-37 行：直接以鍵值存取，未使用 `.get()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 2061 ｜ PR #12</sub>