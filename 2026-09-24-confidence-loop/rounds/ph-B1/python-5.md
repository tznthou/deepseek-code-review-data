<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 腳本。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及缺少輸入驗證。最該先修的是 _fetch 的例外處理和 archive 的 shell 指令，因為它們可能導致靜默失敗或安全漏洞。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序，可能拋出 KeyError 或 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 未處理環境變數轉型失敗 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:48` | _to_epoch 使用 fromisoformat 可能無法解析 GitHub 的時間格式 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 假設 PR 物件一定有 additions、changed_files、title 欄位 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得函式回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError` 或 `KeyError`，且錯誤訊息不明確。

失敗情境：當 GitHub API 回傳 404（PR 不存在）或網路逾時，`_fetch` 回傳 `None`，`main` 中的 `pr["user"]` 會拋出 `TypeError: 'NoneType' object is not subscriptable`，程式直接崩潰。

建議：不要吞掉例外，讓錯誤向上傳播，或在 `_fetch` 內處理並拋出明確的例外；若需回傳 `None`，呼叫端必須檢查。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors`（第 29 行）和 `main`（第 66 行）被直接使用。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令包含外部輸入，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 參數（來自命令列參數）。攻擊者可注入額外 shell 指令，例如 `repo` 設為 `foo; rm -rf /`，導致任意指令執行。

失敗情境：使用者執行 `python3 pr_stats.py 'repo; malicious_command' 1`，`repo` 中的分號會讓 shell 執行後續指令。

建議：避免使用 `shell=True`，改用參數列表形式，例如 `subprocess.run(["tar", "czf", f"{path}.tgz", path])`，並分開處理 `gh` 指令。

**判斷依據**：diff 第 57 行：`shell=True` 且 f-string 包含 `repo`，而 `repo` 來自 `sys.argv[1]`（第 62 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時，先前呼叫的作者會被保留下來，造成結果不正確。

失敗情境：若在同一個程序內呼叫 `collect_authors` 兩次（例如測試或迴圈），第二次呼叫的 `seen` 會包含第一次的結果，導致作者清單重複。

建議：改用 `seen=None`，在函式內初始化為空 list。

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值，且函式內對 `seen` 進行 `append` 修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序，可能拋出 KeyError 或 IndexError</summary>

`review_latency` 直接存取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但 `events` 可能為空（已檢查）或事件物件缺少 `created_at` 欄位（未檢查）。此外，GitHub API 的 timeline 事件不一定按時間排序，若未排序，計算出的 latency 可能為負值。

失敗情境：若某個 timeline 事件沒有 `created_at` 欄位（例如某些事件類型），會拋出 `KeyError`。

建議：先驗證事件結構，或使用 `events[0].get("created_at")` 並處理缺失；若需正確 latency，應先依時間排序。

**判斷依據**：diff 第 34-35 行：直接使用索引和鍵存取，未做防禦性檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理環境變數轉型失敗</summary>

`threshold_from_env` 直接對環境變數 `PR_STALE_DAYS` 執行 `int(raw)`，若該變數不是有效整數（例如設為 `abc`），會拋出 `ValueError` 導致程式崩潰。

失敗情境：使用者誤設 `PR_STALE_DAYS=seven`，程式在啟動時即失敗。

建議：使用 `try/except` 捕捉轉型錯誤，並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 43 行：`int(raw)` 未包在例外處理中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:48</code> _to_epoch 使用 fromisoformat 可能無法解析 GitHub 的時間格式</summary>

`_to_epoch` 使用 `datetime.datetime.fromisoformat` 解析時間字串，但 GitHub API 回傳的時間格式為 ISO 8601，例如 `2023-01-01T12:00:00Z`，Python 3.10 及以下版本的 `fromisoformat` 不支援 `Z` 後綴，會拋出 `ValueError`。

失敗情境：在 Python 3.9 環境中執行，遇到 `Z` 結尾的時間字串會崩潰。

建議：使用 `datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")` 或先替換 `Z` 為 `+00:00`（目前程式碼有做 `replace`，但 `fromisoformat` 在舊版仍可能不支援）。

**判斷依據**：diff 第 39 行：依賴 `fromisoformat` 的行為，但未考慮版本相容性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 PR 物件一定有 additions、changed_files、title 欄位</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但若 `_fetch` 回傳的資料不完整（例如 API 回應缺少這些欄位），會拋出 `KeyError`。

失敗情境：GitHub API 在某些情況下可能不包含 `additions` 或 `changed_files`（例如權限不足或 API 版本變更），導致程式崩潰。

建議：使用 `pr.get("additions", 0)` 等方式提供預設值，或先驗證欄位存在。

**判斷依據**：diff 第 50-53 行：直接使用鍵存取，未做防禦。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，造成資源洩漏。

失敗情境：寫入時發生 `OSError`，程式終止但檔案仍保持開啟，可能導致後續操作失敗或資料不完整。

建議：改用 `with open(path, "w") as f:` 確保檔案自動關閉。

**判斷依據**：diff 第 55-59 行：手動 open/close，無例外處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 0) ｜ completion tokens 2526 ｜ PR #12</sub>