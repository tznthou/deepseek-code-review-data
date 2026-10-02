<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險在於安全性（shell=True 的指令注入、token 可能外洩）、錯誤處理（_fetch 吞掉所有例外、collect_authors 的可變預設值）以及資源管理（export_csv 未使用 with）。最該先修的是 archive 函式中的 shell 指令注入與 _fetch 的例外處理。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入造成指令注入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:22` | _fetch 吞掉所有例外且回傳 None | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 造成跨呼叫狀態污染 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案資源 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 未處理 int 轉換失敗 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 對缺失欄位可能拋出 KeyError | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入造成指令注入</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 與 `path` 變數。`repo` 來自命令列參數，攻擊者可注入任意 shell 指令，例如 `python3 pr_stats.py 'repo; rm -rf /' 1`。建議改用參數陣列並移除 `shell=True`，或對輸入做嚴格驗證。

**判斷依據**：diff 第 77 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自 `sys.argv[1]`，未經任何消毒。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:22</code> _fetch 吞掉所有例外且回傳 None</summary>

`_fetch` 的 `except` 區塊只有 `pass`，任何網路錯誤、HTTP 錯誤、JSON 解析錯誤都會被吞掉，函式回傳 `None`。後續程式碼直接對回傳值做 `pr["user"]` 等操作，會拋出 `TypeError`。建議至少記錄錯誤並重新拋出，或回傳明確的錯誤物件。

**判斷依據**：diff 第 22-23 行：`except:` 後只有 `pass`，且函式沒有其他回傳路徑。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 造成跨呼叫狀態污染</summary>

`collect_authors` 的 `seen` 參數預設為空串列，這是可變物件，會在多次呼叫間共用。若呼叫者未傳入 `seen`，每次呼叫都會累積之前的結果，導致資料錯誤。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 28 行：`def collect_authors(repo, numbers, seen=[]):`，且函式內對 `seen` 進行 `append` 修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案資源</summary>

`export_csv` 直接使用 `open` 和 `close`，若寫入過程拋出例外，檔案不會被關閉，可能造成資源洩漏或資料不完整。建議改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 61-65 行：手動開啟與關閉檔案，沒有例外保護。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理 int 轉換失敗</summary>

`threshold_from_env` 直接對環境變數 `PR_STALE_DAYS` 做 `int(raw)`，若使用者設定非數字字串，會拋出 `ValueError` 導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 44 行：`return {"days": int(raw)}`，無任何例外處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 對缺失欄位可能拋出 KeyError</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，若 API 回傳的 JSON 缺少這些欄位（例如權限不足或 API 變更），會拋出 `KeyError`。建議使用 `.get()` 並提供預設值。

**判斷依據**：diff 第 50-55 行：直接使用鍵值存取，無防護。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 1408) ｜ completion tokens 1434 ｜ PR #12</sub>