<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算指標的 Python 小工具。主要風險在於：錯誤處理幾乎全面失效（_fetch 吞掉所有例外、裸 except）、shell=True 的指令注入、可變預設值、以及多處未處理的邊界條件。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:22` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令字串包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 `seen=[]` 導致跨呼叫累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 假設 timeline 存在且非空，但 API 回應可能不含該欄位 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換未處理例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr["additions"] 等鍵，未處理缺失 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:77` | archive 中的 tar 指令未處理路徑中的特殊字元 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:75` | main 中重複呼叫 _fetch，且未檢查回傳值 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:22` | 裸 except 會捕捉 KeyboardInterrupt 和 SystemExit | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:22</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式可能回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，當 `_fetch` 回傳 `None` 時會拋出 `TypeError`，且沒有提供任何錯誤訊息。

具體失敗情境：當 GitHub API 回傳 404（例如 PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`main` 中的 `pr["user"]["login"]` 會拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰且沒有 log。

建議：在 `_fetch` 中不要吞掉例外，或至少記錄錯誤並重新拋出；或者讓呼叫端檢查回傳值是否為 `None`。

**判斷依據**：diff 第 22-23 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 27 行）和 `main`（第 75 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令字串包含外部輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中直接拼接了 `repo` 和 `path`。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可以注入額外的 shell 指令。

具體攻擊情境：執行 `python3 pr_stats.py 'repo; rm -rf /' 1`，`repo` 的值為 `repo; rm -rf /`，拼接後的指令為 `tar czf /tmp/pr-stats-repo; rm -rf /.tgz /tmp/pr-stats-repo; rm -rf / && gh repo view repo; rm -rf /`，導致任意指令執行。

建議：使用參數列表形式呼叫 `subprocess.run`，避免 `shell=True`；或對輸入進行嚴格的驗證與轉義。

**判斷依據**：diff 第 61 行：`subprocess.run` 使用 `shell=True`，且 f-string 中包含 `repo`（來自 `sys.argv[1]`）和 `path`（來自 `out`，但 `out` 由 `repo` 衍生）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 `seen=[]` 導致跨呼叫累積</summary>

`collect_authors` 的參數 `seen` 預設為空列表，這是一個可變預設值。每次呼叫時若未傳入 `seen`，會共用同一個列表物件，導致多次呼叫的結果累積。

具體情境：第一次呼叫 `collect_authors(repo, [1])` 回傳 `['user1']`；第二次呼叫 `collect_authors(repo, [2])` 會回傳 `['user1', 'user2']`，而不是預期的 `['user2']`。

建議：將預設值改為 `None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 26 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行了 `append` 操作（第 28 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 假設 timeline 存在且非空，但 API 回應可能不含該欄位</summary>

`review_latency` 直接使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位（需要另外請求 timeline API）。因此 `events` 會是空列表，函式回傳 0，導致延遲指標失真。

具體情境：`_fetch` 回傳的 PR JSON 沒有 `timeline` 鍵，`events` 為空，函式回傳 0，所有 PR 的延遲都顯示為 0。

建議：確認 API 回應結構，或另外請求 timeline 資料；若無法取得，應回傳 `None` 或拋出明確錯誤。

**判斷依據**：diff 第 31 行：`pr.get("timeline", [])` 預設為空列表，但 GitHub PR API 回應中沒有 `timeline` 欄位。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換未處理例外</summary>

`threshold_from_env` 中 `int(raw)` 直接轉換環境變數 `PR_STALE_DAYS` 的值，若該值不是合法整數（例如 `abc`），會拋出 `ValueError`，導致程式崩潰。

具體情境：使用者設定 `PR_STALE_DAYS=abc`，程式在 `threshold_from_env` 中拋出 `ValueError`，且沒有提供任何錯誤訊息。

建議：使用 try-except 處理轉換失敗，或提供預設值。

**判斷依據**：diff 第 39 行：`int(raw)` 直接轉換，未處理 `ValueError`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr["additions"] 等鍵，未處理缺失</summary>

`classify` 直接使用 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，若 API 回應缺少這些鍵（例如權限不足或 API 變更），會拋出 `KeyError`。

具體情境：GitHub API 回應中缺少 `additions` 欄位（例如某些事件類型），`classify` 拋出 `KeyError`，程式崩潰。

建議：使用 `.get()` 並提供預設值，或先驗證回應結構。

**判斷依據**：diff 第 44 行：直接使用 `pr["additions"]`，未檢查鍵是否存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。

具體情境：寫入 CSV 時發生 `OSError`，檔案控制代碼未關閉，可能導致後續操作失敗或檔案鎖定。

建議：使用 `with open(path, "w") as f:` 確保檔案總是被關閉。

**判斷依據**：diff 第 52 行：`open` 未搭配 `with`，且後續有 `f.write` 和 `f.close`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:77</code> archive 中的 tar 指令未處理路徑中的特殊字元</summary>

`archive` 使用 `tar czf {path}.tgz {path}`，其中 `path` 來自 `out`（由 `repo` 衍生）。若 `repo` 包含空格或特殊字元（例如 `;`、`&`），可能導致指令執行錯誤或注入。

具體情境：`repo` 為 `my repo`，`path` 為 `/tmp/pr-stats-my repo.csv`，指令變成 `tar czf /tmp/pr-stats-my repo.csv.tgz /tmp/pr-stats-my repo.csv`，tar 會將 `repo.csv.tgz` 和 `repo.csv` 視為兩個檔案，導致錯誤。

建議：使用 `subprocess.run` 的參數列表形式，避免 shell 解析；或對路徑進行轉義。

**判斷依據**：diff 第 61 行：`path` 和 `repo` 直接拼接進 shell 指令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:75</code> main 中重複呼叫 _fetch，且未檢查回傳值</summary>

`main` 在迴圈中對每個 PR 呼叫 `_fetch`，但 `_fetch` 可能回傳 `None`（因為吞掉例外），導致後續 `pr["user"]["login"]` 拋出 `TypeError`。此外，`collect_authors` 已經呼叫過一次 `_fetch`，這裡又重複呼叫，造成不必要的 API 請求。

具體情境：某個 PR 的 API 請求失敗，`_fetch` 回傳 `None`，`main` 中的 `pr["user"]["login"]` 拋出 `TypeError`。

建議：在 `_fetch` 中處理錯誤並拋出例外，或在 `main` 中檢查回傳值；同時考慮重用 `collect_authors` 的結果，避免重複請求。

**判斷依據**：diff 第 75 行：`_fetch` 的回傳值未檢查，且 `_fetch` 可能回傳 `None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:22</code> 裸 except 會捕捉 KeyboardInterrupt 和 SystemExit</summary>

`_fetch` 中的 `except:` 是裸 except，會捕捉所有例外，包括 `KeyboardInterrupt` 和 `SystemExit`，這可能導致程式無法被使用者中斷。

具體情境：使用者在程式執行時按下 Ctrl+C，`KeyboardInterrupt` 被捕捉並忽略，程式繼續執行。

建議：至少改為 `except Exception:`，或更精確地捕捉特定例外。

**判斷依據**：diff 第 22 行：裸 `except:`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3409 (cache hit 640) ｜ completion tokens 3028 ｜ PR #12</sub>