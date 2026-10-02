<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入（archive 函式）、以及資源未正確關閉（export_csv 未使用 with）。最該先修的是 archive 的 shell 指令注入與 _fetch 的錯誤吞掉，因為它們可能造成安全問題或讓使用者誤判結果。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 搭配外部輸入可能造成指令注入 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:22` | _fetch 吞掉所有例外，導致後續程式碼可能因 None 而崩潰 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 會跨呼叫累積資料 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能造成資源洩漏 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:37` | review_latency 假設 events 存在且非空，但 PR 物件可能沒有 timeline 鍵 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理的例外 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 搭配外部輸入可能造成指令注入</summary>

`archive` 函式使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 與 `path` 參數。`repo` 來自命令列參數（`sys.argv[1]`），攻擊者可注入額外 shell 指令，例如 `repo = "x; rm -rf /"`。建議改用參數陣列並避免 `shell=True`，或至少對輸入做嚴格驗證。

**判斷依據**：diff 第 104 行：`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自 `sys.argv[1]`（第 96 行），未經驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:22</code> _fetch 吞掉所有例外，導致後續程式碼可能因 None 而崩潰</summary>

`_fetch` 的 `except:` 區塊只有 `pass`，沒有記錄或重新拋出。當網路錯誤或 API 回傳非 2xx 時，函式會回傳 `None`。呼叫端（如 `collect_authors` 第 31 行、`main` 第 99 行）直接使用回傳值，會導致 `TypeError` 或 `AttributeError`。建議至少記錄錯誤並拋出例外，或讓呼叫端檢查回傳值。

**判斷依據**：diff 第 22-23 行：`except:` 後只有 `pass`，且 `_fetch` 的回傳值在 `collect_authors` 和 `main` 中被直接使用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 會跨呼叫累積資料</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list。若函式被多次呼叫，結果會累積，造成非預期行為。建議改為 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 28 行：`def collect_authors(repo, numbers, seen=[]):`，且函式內有 `seen.append(...)`（第 31 行）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能造成資源洩漏</summary>

`export_csv` 使用 `open` 但未使用 `with`，若寫入過程發生例外，檔案不會被關閉。建議改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 88 行：`f = open(path, "w")`，且後續寫入與關閉未包在 try/finally 或 with 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:37</code> review_latency 假設 events 存在且非空，但 PR 物件可能沒有 timeline 鍵</summary>

`review_latency` 使用 `pr.get("timeline", [])`，但 GitHub API 的 PR 物件通常不包含 `timeline` 鍵，因此 `events` 會是空 list，函式回傳 0。這可能不是預期行為。建議確認 API 回應結構或改用其他方式取得時間資料。

**判斷依據**：diff 第 34 行：`events = pr.get("timeline", [])`，但 GitHub PR API 回應中沒有 `timeline` 欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理的例外</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 轉為整數，若值不是有效整數會拋出 `ValueError`，導致程式崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 48 行：`return {"days": int(raw)}`，且 `raw` 來自環境變數，未驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1451 ｜ PR #12</sub>