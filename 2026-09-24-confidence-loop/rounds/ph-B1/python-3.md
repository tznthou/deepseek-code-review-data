<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive）、以及缺少輸入驗證（classify 直接存取 pr['additions'] 等鍵）。最該先修的是 _fetch 的例外處理與 archive 的 shell=True，因為它們會造成靜默失敗或安全漏洞。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr['additions'] 等鍵，若 API 回應缺少欄位會拋出 KeyError | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int(raw) 未處理轉換失敗，可能導致程式崩潰 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。呼叫端（`collect_authors` 和 `main`）直接使用回傳值，若 `_fetch` 回傳 `None`，後續 `pr["user"]["login"]` 會拋出 `TypeError`，且沒有上下文可除錯。

具體失敗情境：GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`collect_authors` 執行 `pr["user"]` 時拋出 `TypeError: 'NoneType' object is not subscriptable`。

建議：至少記錄例外並重新拋出，或讓 `_fetch` 在失敗時拋出明確的例外，由呼叫端處理。

**判斷依據**：diff 第 25 行 `except: pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 30 行）和 `main`（第 75 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，其中 `repo` 來自命令列參數（使用者可控），`path` 來自 `out`（由 `repo` 衍生）。攻擊者可注入任意 shell 指令。

具體攻擊情境：執行 `python3 pr_stats.py '$(rm -rf /)' 1`，`repo` 的值會被展開，導致惡意指令執行。

建議：改用 `subprocess.run` 的參數列表形式（`shell=False`），並將 `gh repo view` 分開呼叫，避免 shell 解讀。

**判斷依據**：diff 第 67 行，`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。若此函式被多次呼叫（例如在同一個行程中處理多個 repo），先前呼叫的結果會殘留，導致作者清單不正確。

具體失敗情境：第一次呼叫 `collect_authors('repo1', [1,2])` 回傳 `['alice', 'bob']`，第二次呼叫 `collect_authors('repo2', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是 `['carol']`。

建議：將預設值改為 `None`，在函式內初始化為空 list。

**判斷依據**：diff 第 29 行，函式定義使用可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr['additions'] 等鍵，若 API 回應缺少欄位會拋出 KeyError</summary>

`classify` 假設 `pr` 字典一定包含 `additions`、`changed_files`、`title` 等鍵。但 GitHub API 的回應可能因權限、API 版本或 PR 狀態而缺少這些欄位（例如 draft PR 可能沒有 `additions`）。

具體失敗情境：若 `_fetch` 回傳的 JSON 缺少 `additions`（例如 API 變更或權限不足），`pr["additions"]` 會拋出 `KeyError`，程式終止。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 52 行，直接使用 `pr["additions"]`，未檢查鍵是否存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int(raw) 未處理轉換失敗，可能導致程式崩潰</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若使用者設定非數字字串（例如 `abc`），會拋出 `ValueError`，程式終止。

具體失敗情境：`PR_STALE_DAYS=abc python3 pr_stats.py repo 1` 會拋出 `ValueError: invalid literal for int() with base 10: 'abc'`。

建議：捕捉 `ValueError` 並提供有意義的錯誤訊息，或使用預設值。

**判斷依據**：diff 第 44 行，直接轉換環境變數為整數，未處理例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若 `f.write` 拋出例外（例如磁碟滿），檔案不會被關閉，造成資源洩漏。

建議：改用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 60-64 行，手動開啟與關閉檔案，未使用 context manager。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 0) ｜ completion tokens 1853 ｜ PR #12</sub>