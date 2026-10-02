<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell 注入（archive 使用 shell=True 且拼接 repo）、以及資源未正確關閉（export_csv 未使用 with）。這些問題可能導致資料不正確、安全漏洞或資源洩漏，建議優先修正。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | 例外被吞掉且回傳 None，導致後續程式碼崩潰 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令字串由外部輸入拼接，存在命令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，可能導致資源洩漏 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 函式假設 pr 包含 additions 和 changed_files 鍵 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且包含 created_at | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> 例外被吞掉且回傳 None，導致後續程式碼崩潰</summary>

`_fetch` 函式中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），且函式沒有回傳值，隱含回傳 `None`。呼叫端（如 `collect_authors` 和 `main`）直接對回傳值做 `pr["user"]` 或 `pr["additions"]`，當 `_fetch` 失敗時會拋出 `TypeError: 'NoneType' object is not subscriptable`，且沒有提供任何錯誤訊息，難以除錯。建議：捕捉具體例外並記錄錯誤，或重新拋出；若需回傳 None，呼叫端應檢查。

**判斷依據**：diff 第 24 行 `except: pass`，且函式無回傳值。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令字串由外部輸入拼接，存在命令注入風險</summary>

`archive` 函式使用 `subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)`，其中 `repo` 來自命令列參數（外部輸入），攻擊者可注入額外命令，例如 `repo = "x; rm -rf /"`。此外，`path` 也可能包含特殊字元。建議改用參數列表形式並避免 shell=True，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 73 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫累積</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list，導致多次呼叫時作者列表會累積，造成結果不正確。例如第一次呼叫後 seen 包含 ['alice']，第二次呼叫會從 ['alice'] 開始，最終回傳包含重複作者的列表。建議改為 `seen=None`，在函式內初始化為空 list。

**判斷依據**：diff 第 28 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，可能導致資源洩漏</summary>

`export_csv` 使用 `open` 和 `close` 手動管理檔案，若在寫入過程中發生例外（例如磁碟滿、權限問題），檔案不會被關閉，造成資源洩漏。建議改用 `with open(path, "w") as f:` 確保檔案正確關閉。

**判斷依據**：diff 第 66-70 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

`threshold_from_env` 中 `int(raw)` 可能拋出 `ValueError`（例如環境變數設為非數字字串），導致程式崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 44 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 函式假設 pr 包含 additions 和 changed_files 鍵</summary>

`classify` 直接存取 `pr["additions"]` 和 `pr["changed_files"]`，但 `_fetch` 回傳的 JSON 可能不包含這些鍵（例如 API 回應格式變更或錯誤），導致 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式提供預設值。

**判斷依據**：diff 第 50-52 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且包含 created_at</summary>

`review_latency` 中若 `events` 為空列表，函式回傳 0，但若 events 非空但元素缺少 `created_at` 鍵，會拋出 `KeyError`。建議使用 `events[0].get("created_at")` 並處理缺失情況。

**判斷依據**：diff 第 36-37 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 0) ｜ completion tokens 1597 ｜ PR #12</sub>