<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於：錯誤處理幾乎完全缺失（_fetch 吞掉所有例外、archive 使用 shell=True 且未檢查回傳值）、可變預設值 collect_authors 的 seen=[] 會跨呼叫累積、CSV 輸出未處理欄位中的逗號或換行、以及 review_latency 對空 timeline 的處理不正確。最該先修的是 _fetch 的錯誤處理與 archive 的 shell 注入風險。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | review_latency 對空 timeline 的處理不正確 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:72` | export_csv 未處理欄位中的逗號或換行，可能產生格式錯誤的 CSV | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 未處理 PR_STALE_DAYS 轉型失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr.get(...)`，若 `_fetch` 回傳 `None`，會拋出 `TypeError` 或 `AttributeError`，且沒有提供任何錯誤訊息。

失敗情境：GitHub API 暫時無法連線、token 無效、或 PR 編號不存在時，程式會以難以理解的 traceback 結束，使用者無法得知真正原因。

建議：讓 `_fetch` 在失敗時拋出明確的例外（例如 `raise RuntimeError(f"Failed to fetch {path}: {e}")`），或回傳一個可辨識的錯誤物件，並在呼叫端檢查。

**判斷依據**：diff 第 25 行：`except:` 後只有 `pass`，且函式沒有回傳任何值，隱含回傳 `None`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令包含外部輸入，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`。其中 `path` 和 `repo` 來自命令列參數，攻擊者可注入額外 shell 指令。例如 `repo` 設為 `x; rm -rf /` 或 `path` 設為 `x; curl evil.com`，會導致任意命令執行。

失敗情境：使用者執行 `python3 pr_stats.py '; rm -rf ~' 1`，會刪除家目錄。

建議：改用參數列表形式，避免 shell 解析：`subprocess.run(["tar", "czf", f"{path}.tgz", path])` 和 `subprocess.run(["gh", "repo", "view", repo])`，或至少對輸入做嚴格驗證。

**判斷依據**：diff 第 78 行：`shell=True` 且 f-string 包含 `path` 和 `repo`，這兩個變數來自 `sys.argv`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的 `seen` 參數預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，因此多次呼叫會共用同一個列表，導致結果累積。

失敗情境：第一次呼叫 `collect_authors('repo', [1,2])` 回傳 `['alice', 'bob']`，第二次呼叫 `collect_authors('repo', [3])` 會回傳 `['alice', 'bob', 'carol']`，而不是預期的 `['carol']`。

建議：將預設值改為 `None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 29 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> review_latency 對空 timeline 的處理不正確</summary>

`review_latency` 在 `events` 為空時回傳 0，但這會與「真正的 latency 為 0」混淆。此外，`events` 來自 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 欄位，因此 `events` 永遠是空列表，導致 latency 永遠為 0。

失敗情境：即使 PR 有 review 活動，只要 `_fetch` 沒有特別要求 timeline，`review_latency` 就會回傳 0，使指標失去意義。

建議：確認 API 回應是否包含 timeline，若無則需額外請求；若確實可能為空，應回傳 `None` 或拋出例外，而不是 0。

**判斷依據**：diff 第 35-37 行：`pr.get("timeline", [])` 預設空列表，且空列表時回傳 0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:72</code> export_csv 未處理欄位中的逗號或換行，可能產生格式錯誤的 CSV</summary>

`export_csv` 直接使用 f-string 寫入 `author`、`latency`、`kind`，未對欄位值做 CSV 跳脫。若 `author` 包含逗號或換行（GitHub 使用者名稱可能包含逗號？），會破壞 CSV 結構。

失敗情境：若 `author` 為 `"Doe, John"`，輸出會變成 `Doe, John,123,normal`，導致解析錯誤。

建議：使用 `csv` 模組的 `writer` 來正確處理跳脫。

**判斷依據**：diff 第 72 行：直接以 f-string 寫入，未使用 csv 模組。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理 PR_STALE_DAYS 轉型失敗</summary>

`threshold_from_env` 直接 `int(raw)`，若環境變數不是整數（例如 `PR_STALE_DAYS=abc`），會拋出 `ValueError` 且沒有提供有意義的錯誤訊息。

失敗情境：使用者誤設 `PR_STALE_DAYS=seven`，程式會以 traceback 結束。

建議：捕捉 `ValueError` 並提供明確錯誤，或使用預設值。

**判斷依據**：diff 第 44 行：`int(raw)` 未包在 try-except 中。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 0) ｜ completion tokens 1924 ｜ PR #12</sub>