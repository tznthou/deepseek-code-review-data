<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險集中在錯誤處理（_fetch 吞掉所有例外）、安全性（shell=True 指令注入、token 可能外洩）、以及可變預設值（collect_authors 的 seen=[]）導致的跨呼叫污染。建議先修 _fetch 的例外處理與 archive 的 shell 指令，再處理其他問題。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，呼叫端會拿到 None 並在後續崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:21` | GITHUB_TOKEN 可能因例外而外洩至 stderr | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 timeline 事件存在且有序，可能回傳錯誤結果 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，呼叫端會拿到 None 並在後續崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），且函式沒有回傳值，導致呼叫端（`collect_authors`、`main`）拿到 `None` 後嘗試以 `pr["user"]` 或 `pr["additions"]` 存取，觸發 `TypeError`。

失敗情境：網路逾時、GitHub API 回 404、回應不是合法 JSON 時，程式會以難以理解的 `TypeError` 崩潰，且沒有留下任何錯誤訊息。

建議：
- 捕捉具體例外（`urllib.error.URLError`、`json.JSONDecodeError` 等），記錄錯誤並重新拋出或回傳明確的錯誤值。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 不要使用裸 `except:`。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 與 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外 shell 指令。

失敗情境：執行 `python3 pr_stats.py 'repo; rm -rf /' 1` 時，`repo` 中的分號會讓 shell 執行 `rm -rf /`。

建議：
- 改用 `subprocess.run` 的參數列表形式，避免 `shell=True`。
- 若必須使用 shell，請對所有外部輸入進行嚴格的驗證與轉義。

**判斷依據**：diff 第 76 行：`shell=True` 且 f-string 包含 `repo`（來自 `sys.argv[1]`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的 `seen` 參數預設為空列表，但 Python 的可變預設值只會在函式定義時建立一次，之後每次呼叫都會共用同一個列表物件。

失敗情境：第一次呼叫 `collect_authors('repo', [1])` 回傳 `['alice']`；第二次呼叫 `collect_authors('repo', [2])` 會回傳 `['alice', 'bob']`，而不是預期的 `['bob']`。

建議：將預設值改為 `None`，在函式內判斷並建立新列表：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 28 行：參數 `seen=[]` 為可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:21</code> GITHUB_TOKEN 可能因例外而外洩至 stderr</summary>

`_fetch` 使用 `os.environ["GITHUB_TOKEN"]` 取得 token，若環境變數未設定會拋出 `KeyError`，且該例外會被 `except: pass` 吞掉，但 Python 預設的例外處理會將 traceback 輸出到 stderr，其中可能包含 token 值（若 token 出現在錯誤訊息中）。

失敗情境：未設定 `GITHUB_TOKEN` 時，程式會印出包含 `KeyError: 'GITHUB_TOKEN'` 的 traceback，但不會洩漏 token 本身；然而若 token 值本身包含特殊字元導致其他例外，traceback 可能包含 token。

建議：使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 `None`，若未設定則印出明確錯誤訊息並退出。

**判斷依據**：diff 第 20 行：直接使用 `os.environ["GITHUB_TOKEN"]`，未處理 KeyError。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 timeline 事件存在且有序，可能回傳錯誤結果</summary>

`review_latency` 直接取 `events[0]` 和 `events[-1]`，但 `pr.get("timeline", [])` 可能回傳空列表（已處理），但若事件順序不是時間遞增（例如 GitHub API 可能依其他方式排序），計算出的 latency 可能為負值或錯誤。

失敗情境：若 timeline 事件順序為 `[{"created_at": "2023-01-02"}, {"created_at": "2023-01-01"}]`，則 latency 為負數。

建議：先依 `created_at` 排序，或明確使用最早和最晚的事件。

**判斷依據**：diff 第 34-35 行：直接取第一個和最後一個事件，未排序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 `int`，若使用者設定非數字字串（例如 `"abc"`），會拋出 `ValueError` 且未被捕捉，導致程式崩潰。

失敗情境：`PR_STALE_DAYS=abc python3 pr_stats.py repo 1` 會以 traceback 結束。

建議：捕捉 `ValueError` 並提供有意義的錯誤訊息，或使用預設值。

**判斷依據**：diff 第 42 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案控制代碼</summary>

`export_csv` 使用 `open` 和 `close`，但若 `f.write` 拋出例外（例如磁碟已滿），`f.close()` 不會被執行，導致檔案控制代碼洩漏。

失敗情境：寫入過程中發生 I/O 錯誤時，程式會留下未關閉的檔案。

建議：使用 `with open(path, "w") as f:` 確保檔案總會被關閉。

**判斷依據**：diff 第 70-74 行：手動 open/close，無例外處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2186 ｜ PR #12</sub>