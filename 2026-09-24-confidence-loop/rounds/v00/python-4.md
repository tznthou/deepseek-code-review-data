<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈取 PR 資料並計算統計的小工具。主要風險集中在錯誤處理不當（_fetch 吞掉所有例外）、安全性問題（shell=True 指令注入、token 可能外洩）、以及可變預設值導致的狀態污染。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，否則工具在實際使用中容易出現難以除錯的失敗或安全漏洞。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，呼叫端無法得知失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態累積 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int() 轉換可能拋出未處理例外 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，可能洩漏資源 | 0.75 |
| ⚠️ | Major | `sandbox/pr_stats.py:81` | main 中未檢查命令列參數數量，可能 IndexError | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:63` | classify 中 title.startswith("fix") 可能誤判 | 0.65 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，呼叫端無法得知失敗</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包含網路錯誤、HTTP 錯誤、JSON 解析錯誤），導致呼叫端拿到 `None` 或繼續執行，後續程式碼可能因為 `pr` 為 `None` 而拋出 `TypeError`，且錯誤被隱藏，難以除錯。

建議：
- 至少記錄例外（`logging.exception`）或重新拋出。
- 檢查 HTTP 狀態碼，非 2xx 時拋出例外。
- 讓呼叫端處理錯誤，而不是靜默失敗。

**判斷依據**：diff 第 24 行：`except:` 後直接 `pass`，且 `_fetch` 被 `collect_authors` 和 `main` 呼叫，其回傳值被直接使用（如 `pr["user"]["login"]`）。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令包含外部輸入，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo`（來自命令列參數）與 `path`（由 repo 衍生）。攻擊者可注入額外指令，例如 `repo` 設為 `x; rm -rf /`。

建議：
- 避免 `shell=True`，改用參數列表形式：`subprocess.run(["tar", "czf", f"{path}.tgz", path])`。
- 若需使用 shell，務必驗證輸入或使用 `shlex.quote`。

**判斷依據**：diff 第 68 行：`repo` 來自 `sys.argv[1]`，未經驗證直接嵌入 shell 指令。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態累積</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會累積作者，且不會清空。若多次呼叫此函式，結果會包含先前呼叫的作者，造成資料污染。

建議：改為 `seen=None`，並在函式內初始化：`if seen is None: seen = []`。

**判斷依據**：diff 第 28 行：`seen=[]` 為可變預設值，且函式內對其進行 `append` 操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at</summary>

`review_latency` 在 `events` 為空時回傳 0，但若 `events` 非空但元素缺少 `created_at` 鍵，會拋出 `KeyError`。此外，若 `events` 只有一個元素，`first` 和 `last` 相同，回傳 0，可能無法反映真實延遲。

建議：檢查 `events` 是否為空，並確認每個事件都有 `created_at`，或使用更精確的計算方式。

**判斷依據**：diff 第 34-35 行：直接存取 `events[0]` 和 `events[-1]`，未檢查鍵是否存在。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int() 轉換可能拋出未處理例外</summary>

`threshold_from_env` 從環境變數 `PR_STALE_DAYS` 讀取值並直接 `int(raw)`，若值不是整數（例如 `abc`），會拋出 `ValueError`，導致程式崩潰。

建議：使用 `try/except` 處理轉換失敗，或提供預設值。

**判斷依據**：diff 第 42 行：`int(raw)` 未處理例外。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程中發生例外，檔案不會被關閉。建議使用 `with open(path, "w") as f:` 確保資源釋放。

**判斷依據**：diff 第 58-62 行：手動開啟與關閉檔案，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:81</code> main 中未檢查命令列參數數量，可能 IndexError</summary>

`main` 直接使用 `sys.argv[1]` 和 `sys.argv[2:]`，若使用者未提供足夠參數，會拋出 `IndexError`。建議檢查參數數量並顯示用法。

**判斷依據**：diff 第 72-73 行：直接索引 `sys.argv`，未檢查長度。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:63</code> classify 中 title.startswith("fix") 可能誤判</summary>

`classify` 使用 `pr["title"].startswith("fix")` 判斷是否為 fix，但大小寫敏感且可能誤判（例如 "fixed" 或 "Fix"）。建議使用正規表示式或忽略大小寫。

**判斷依據**：diff 第 53 行：`startswith("fix")` 未考慮大小寫變體。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3243 (cache hit 1408) ｜ completion tokens 1923 ｜ PR #12</sub>