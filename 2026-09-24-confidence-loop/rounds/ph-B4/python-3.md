<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確釋放。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們可能導致資料不正確或安全性問題。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:25` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 假設 pr 一定有 additions、changed_files、title 鍵，可能 KeyError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且每個事件都有 created_at | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:21` | Authorization header 直接使用環境變數，若未設定會 KeyError | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:25</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且不回報任何錯誤。這使得呼叫端無法得知失敗，後續程式碼（如 `pr["user"]["login"]`）在 `pr` 為 `None` 或缺少鍵時會拋出未處理的例外，造成程式崩潰。

建議：
- 至少記錄錯誤並重新拋出，或回傳一個明確的錯誤值。
- 使用 `raise` 保留原始例外，或改用 `except Exception as e: raise RuntimeError(...) from e`。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。

**判斷依據**：diff 第 25-26 行：`except:` 後直接 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令字串由外部輸入拼接，存在指令注入風險</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path`，這兩個參數來自命令列參數或程式內部，但 `repo` 是使用者輸入（`sys.argv[1]`）。攻擊者可以注入額外的 shell 指令，例如 `repo` 設為 `foo; rm -rf /`。

建議：避免使用 `shell=True`，改用參數列表形式：
```python
subprocess.run(["tar", "czf", f"{path}.tgz", path])
subprocess.run(["gh", "repo", "view", repo])
```
或至少對輸入進行嚴格的驗證與轉義。

**判斷依據**：diff 第 70 行：`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 是可變預設值，在函式定義時建立一次，之後每次呼叫都會共用同一個 list。這會導致多次呼叫時作者名單不斷累積，而不是每次重新開始。

建議：改用 `seen=None`，並在函式內初始化：
```python
def collect_authors(repo, numbers, seen=None):
    if seen is None:
        seen = []
    ...
```

**判斷依據**：diff 第 30 行：參數預設值為 `[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，例外時可能洩漏檔案描述子</summary>

`export_csv` 使用 `open` 和 `close`，但沒有使用 `with` 語句。如果在寫入過程中發生例外（例如磁碟滿、權限錯誤），檔案不會被關閉，造成資源洩漏。

建議：改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 62-66 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的 ValueError</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，如果該值不是合法整數（例如 "abc" 或空字串），會拋出 `ValueError`，導致程式崩潰。

建議：捕捉 `ValueError` 並回傳預設值，或記錄警告。

**判斷依據**：diff 第 45-46 行：直接 `int(raw)` 無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 假設 pr 一定有 additions、changed_files、title 鍵，可能 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，但 `_fetch` 回傳的 JSON 可能缺少這些鍵（例如 API 回應格式變更或部分 PR 資料不完整），導致 `KeyError`。

建議：使用 `pr.get("additions", 0)` 等方式，或先驗證資料結構。

**判斷依據**：diff 第 50-55 行：直接索引字典。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且每個事件都有 created_at</summary>

`review_latency` 在 `events` 非空時直接取 `events[0]["created_at"]` 和 `events[-1]["created_at"]`，但事件物件可能缺少 `created_at` 鍵，或 `events` 為空（已處理），但若 `events` 為空則回傳 0，可能掩蓋真實延遲。此外，若 `created_at` 格式不正確，`_to_epoch` 會拋出例外。

建議：檢查鍵是否存在，並處理時間解析錯誤。

**判斷依據**：diff 第 36-37 行：直接索引事件列表。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:21</code> Authorization header 直接使用環境變數，若未設定會 KeyError</summary>

`_fetch` 使用 `os.environ["GITHUB_TOKEN"]`，如果環境變數未設定，會拋出 `KeyError`，且沒有提供明確的錯誤訊息。

建議：使用 `os.environ.get("GITHUB_TOKEN")` 並檢查是否為 `None`，或提供預設值。

**判斷依據**：diff 第 22 行：直接索引環境變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 2128 ｜ PR #12</sub>