<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險集中在錯誤處理與安全性：`_fetch` 吞掉所有例外且不回報，會讓後續程式碼在資料缺失時直接崩潰；`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險；`collect_authors` 使用可變預設值參數，跨呼叫會累積資料。此外，`review_latency` 依賴不存在的 `timeline` 欄位，可能永遠回傳 0。建議先修補安全性與錯誤處理，再考慮合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | `_fetch` 吞掉所有例外且不回報，導致後續程式碼在資料缺失時直接崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | `collect_authors` 使用可變預設值參數，跨呼叫會累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:37` | `review_latency` 依賴不存在的 `timeline` 欄位，可能永遠回傳 0 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:51` | `threshold_from_env` 的預設參數為可變字典，且未處理轉換例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | `export_csv` 未使用 `with` 管理檔案，且未處理寫入例外 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:23` | `_fetch` 未檢查 HTTP 狀態碼，非 2xx 回應會被當成成功處理 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> `_fetch` 吞掉所有例外且不回報，導致後續程式碼在資料缺失時直接崩潰</summary>

`_fetch` 的 `except:` 區塊只有 `pass`，沒有記錄或重新拋出。當網路錯誤、API 回傳非 200、JSON 解析失敗或 `GITHUB_TOKEN` 未設定時，函式會回傳 `None`。呼叫端（`collect_authors`、`main`）直接對回傳值做 `pr["user"]` 或 `pr["additions"]` 等操作，會拋出 `TypeError` 或 `KeyError`，且錯誤訊息不明確。

**失敗情境**：
- 未設定 `GITHUB_TOKEN` 環境變數時，`os.environ["GITHUB_TOKEN"]` 會拋出 `KeyError`，但被 `except` 捕捉後回傳 `None`，後續 `pr["user"]` 拋出 `TypeError`。
- API 回傳 404（PR 不存在）時，`urlopen` 拋出 `HTTPError`，同樣被吞掉，後續程式碼崩潰。

**建議**：
- 至少記錄例外（`logging.exception`）並重新拋出，或讓函式回傳明確的錯誤結果。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 使用 `raise ... from err` 保留原始追蹤資訊。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，且函式沒有其他回傳值，呼叫端直接使用回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 和 `repo` 來自命令列參數（`sys.argv`），未經任何驗證或轉義。攻擊者可注入額外命令，例如 `repo` 設為 `x; rm -rf /`，導致任意命令執行。

**失敗情境**：
- 使用者執行 `python3 pr_stats.py 'x; curl http://evil' 1`，`repo` 中的分號會讓 shell 執行 `curl`。
- `path` 若包含空格或特殊字元，也會造成非預期行為。

**建議**：
- 避免使用 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若需要執行多個命令，分開呼叫 `subprocess.run`。
- 對外部輸入進行驗證（例如只允許 `owner/repo` 格式）。

**判斷依據**：diff 第 84 行：`shell=True` 且 f-string 包含 `path` 和 `repo`，兩者皆來自使用者輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> `collect_authors` 使用可變預設值參數，跨呼叫會累積資料</summary>

`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 的預設值是空列表，但 Python 的預設參數在函式定義時只建立一次，之後每次呼叫都會共用同一個列表物件。若呼叫者未傳入 `seen`，多次呼叫會累積先前呼叫的結果，導致資料污染。

**失敗情境**：
- 第一次呼叫 `collect_authors("repo", [1])` 回傳 `["alice"]`。
- 第二次呼叫 `collect_authors("repo", [2])` 會回傳 `["alice", "bob"]`，而不是 `["bob"]`。

**建議**：
- 使用 `None` 作為預設值，並在函式內初始化：`def collect_authors(repo, numbers, seen=None):`，然後 `if seen is None: seen = []`。

**判斷依據**：diff 第 28 行：函式定義使用可變預設值 `[]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:37</code> `review_latency` 依賴不存在的 `timeline` 欄位，可能永遠回傳 0</summary>

`events = pr.get("timeline", [])` 嘗試從 PR 物件取得 `timeline` 欄位，但 GitHub API 的 PR 物件通常不包含 `timeline`（需要另外請求 timeline API）。因此 `events` 幾乎總是空列表，函式回傳 0，導致延遲指標失效。

**失敗情境**：
- 對任何 PR 呼叫 `review_latency`，都會得到 0，即使實際上有 review 活動。

**建議**：
- 確認 API 回應是否包含 `timeline`，若無，需另外呼叫 timeline API 或改用其他欄位（如 `created_at` 與 `updated_at`）。
- 若 `timeline` 不存在，應拋出錯誤或記錄警告，而不是靜默回傳 0。

**判斷依據**：diff 第 34 行：使用 `pr.get("timeline", [])`，但 GitHub PR 物件通常無此欄位。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:51</code> `threshold_from_env` 的預設參數為可變字典，且未處理轉換例外</summary>

`def threshold_from_env(default={"days": 7}):` 使用可變字典作為預設值，雖然函式內未修改 `default`，但若未來修改會造成跨呼叫污染。此外，`int(raw)` 轉換環境變數時未處理 `ValueError`，若 `PR_STALE_DAYS` 設為非數字字串，程式會崩潰。

**失敗情境**：
- 使用者設定 `PR_STALE_DAYS=abc`，`int(raw)` 拋出 `ValueError`，程式終止。

**建議**：
- 使用 `None` 作為預設值，並在函式內設定：`def threshold_from_env(default=None):`，然後 `if default is None: default = {"days": 7}`。
- 捕捉 `ValueError` 並提供有意義的錯誤訊息，或使用 `int(raw)` 前先驗證。

**判斷依據**：diff 第 44 行：可變預設值，且第 47 行 `int(raw)` 未處理例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> `export_csv` 未使用 `with` 管理檔案，且未處理寫入例外</summary>

`f = open(path, "w")` 後直接寫入，若寫入過程拋出例外（如磁碟滿、權限不足），檔案不會被關閉，造成資源洩漏。此外，CSV 欄位未做跳脫，若 `author` 或 `kind` 包含逗號或換行，會破壞 CSV 格式。

**失敗情境**：
- 寫入時發生例外，檔案控制代碼未關閉，可能導致後續操作失敗或資料不完整。
- `author` 為 `"Doe, John"` 時，CSV 解析會錯位。

**建議**：
- 使用 `with open(path, "w") as f:` 確保檔案關閉。
- 使用 `csv` 模組的 `writer` 來正確處理跳脫。

**判斷依據**：diff 第 74 行：直接 `open` 而無 `with`，且後續手動寫入 CSV。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:23</code> `_fetch` 未檢查 HTTP 狀態碼，非 2xx 回應會被當成成功處理</summary>

`urllib.request.urlopen` 在 HTTP 錯誤（如 404、500）時會拋出 `HTTPError`，但此處被 `except` 捕捉後回傳 `None`，呼叫端無法區分錯誤類型。若 API 回傳 401（token 無效），程式會繼續執行並在後續崩潰。

**失敗情境**：
- token 過期時，API 回傳 401，`_fetch` 回傳 `None`，`main` 中 `pr["user"]` 拋出 `TypeError`。

**建議**：
- 在 `urlopen` 後檢查 `resp.status`，非 2xx 時拋出例外或回傳錯誤。

**判斷依據**：diff 第 20-22 行：未檢查 `resp.status`，且例外處理不當。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 2686 ｜ PR #12</sub>