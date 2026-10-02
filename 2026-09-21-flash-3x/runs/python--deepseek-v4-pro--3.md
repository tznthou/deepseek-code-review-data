<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了一個從 GitHub API 撈取 PR 資料並計算維護指標的 Python 腳本。主要風險在於安全性與穩健性：`_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼，可能導致後續程式碼因資料缺失而崩潰；`archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險；`collect_authors` 使用可變預設參數，可能造成跨呼叫的狀態污染；此外，檔案處理未使用 `with`，且環境變數轉換未處理例外。建議優先修復安全與錯誤處理問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:22` | `_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | `collect_authors` 使用可變預設參數 `seen=[]` | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | `export_csv` 未使用 `with` 開啟檔案，可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | `threshold_from_env` 未處理環境變數轉換例外 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:37` | `review_latency` 假設 `timeline` 欄位存在且非空 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:22</code> `_fetch` 吞掉所有例外且未檢查 HTTP 狀態碼</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、JSON 解析錯誤），且未檢查 HTTP 狀態碼（例如 404、401）。這會導致呼叫端在 API 失敗時拿到 `None`，後續程式碼（如 `pr["user"]["login"]`）會拋出 `TypeError` 或 `KeyError`，造成程式崩潰。建議：明確捕捉 `urllib.error.URLError` 和 `json.JSONDecodeError`，並檢查 `resp.status`，若非 2xx 則拋出例外或記錄錯誤。

**判斷依據**：diff 第 22 行：`except:` 後直接 `pass`，且未檢查 `resp.status`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> `archive` 使用 `shell=True` 且拼接外部輸入，存在命令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 和 `repo` 來自命令列參數，攻擊者可注入額外命令（例如 `repo` 設為 `x; rm -rf /`）。即使 `path` 是內部產生的，`repo` 仍完全由使用者控制。建議：改用參數列表形式（`subprocess.run(["tar", "czf", f"{path}.tgz", path])`），並分開執行 `gh` 命令，避免 `shell=True`。

**判斷依據**：diff 第 72 行：`shell=True` 且 f-string 包含 `repo`（來自 `sys.argv[1]`）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> `collect_authors` 使用可變預設參數 `seen=[]`</summary>

`def collect_authors(repo, numbers, seen=[]):` 中，`seen` 預設為空列表，但列表是可變物件，會在函式定義時建立一次並在所有呼叫間共用。若呼叫者未傳入 `seen`，多次呼叫會累積先前結果，導致資料污染。建議改為 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 27 行：可變預設參數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> `export_csv` 未使用 `with` 開啟檔案，可能洩漏資源</summary>

`f = open(path, "w")` 後手動 `f.close()`，若寫入過程拋出例外（例如磁碟滿、權限不足），檔案控制代碼不會被關閉，造成資源洩漏。建議使用 `with open(path, "w") as f:` 確保自動關閉。

**判斷依據**：diff 第 64-68 行：手動開啟與關閉檔案。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> `threshold_from_env` 未處理環境變數轉換例外</summary>

`int(raw)` 可能拋出 `ValueError`（例如 `PR_STALE_DAYS=abc`），導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 48 行：直接 `int(raw)` 未捕捉例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:37</code> `review_latency` 假設 `timeline` 欄位存在且非空</summary>

`events = pr.get("timeline", [])` 若 `timeline` 不存在會回傳空列表，但後續 `events[0]` 和 `events[-1]` 在空列表時會拋出 `IndexError`。雖然目前有 `if not events: return 0` 保護，但若 `timeline` 存在但為空列表，仍會觸發。建議明確檢查 `if not events: return 0` 已足夠，但需確保 `timeline` 鍵存在時一定是列表。

**判斷依據**：diff 第 31-35 行：`events` 可能為空列表，但 `if not events` 已處理，此處為低風險。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3228 (cache hit 3200) ｜ completion tokens 1613</sub>