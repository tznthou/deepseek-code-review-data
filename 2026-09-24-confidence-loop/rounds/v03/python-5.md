<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算統計的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確關閉。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們可能導致靜默失敗或安全問題。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致靜默失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令包含外部輸入，存在指令注入風險 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 跨呼叫共用 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:32` | 直接存取 pr["user"]["login"] 可能因鍵不存在而崩潰 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:40` | review_latency 假設 events 非空且元素有 created_at | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:59` | classify 直接存取 pr["additions"] 等鍵可能 KeyError | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 開啟檔案，可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 的 int(raw) 可能拋出 ValueError | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:83` | main 中重複呼叫 _fetch 且未檢查回傳值 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致靜默失敗</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使得呼叫端無法得知失敗，後續程式碼可能因 `pr` 為 `None` 或缺少鍵而崩潰，或產生錯誤的統計結果。

建議：至少記錄錯誤並重新拋出，或回傳一個明確的錯誤值，讓呼叫端處理。

**判斷依據**：diff 第 24-25 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令包含外部輸入，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串包含 `repo` 和 `path`，這些值來自命令列參數或計算結果，攻擊者可注入額外指令。

建議：避免 `shell=True`，改用參數列表，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 67 行：shell=True 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 跨呼叫共用</summary>

`collect_authors` 的 `seen` 參數預設為空 list，這是可變預設值，會在所有呼叫之間共用。如果多次呼叫此函式且未傳入 `seen`，結果會累積，導致作者清單包含先前呼叫的結果。

建議：使用 `seen=None` 並在函式內初始化。

**判斷依據**：diff 第 29 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:32</code> 直接存取 pr["user"]["login"] 可能因鍵不存在而崩潰</summary>

`_fetch` 回傳的 JSON 可能缺少 `user` 或 `login` 鍵（例如 API 錯誤或 PR 資料不完整），直接使用 `pr["user"]["login"]` 會拋出 `KeyError`。

建議：使用 `.get()` 或先驗證結構。

**判斷依據**：diff 第 31 行：直接索引巢狀鍵。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:40</code> review_latency 假設 events 非空且元素有 created_at</summary>

`review_latency` 中，如果 `events` 為空，函式回傳 0，但若 `events` 非空但元素缺少 `created_at` 鍵，則會拋出 `KeyError`。此外，`events` 的順序可能不是按時間排序，直接取第一個和最後一個可能不準確。

建議：驗證每個事件的 `created_at` 存在，並考慮排序。

**判斷依據**：diff 第 36-37 行：直接索引 events 並存取 created_at。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:59</code> classify 直接存取 pr["additions"] 等鍵可能 KeyError</summary>

`classify` 假設 `pr` 字典包含 `additions`、`changed_files`、`title` 鍵，但 API 回應可能缺少這些鍵（例如某些 PR 類型），導致 `KeyError`。

建議：使用 `.get()` 並提供預設值。

**判斷依據**：diff 第 55 行：直接索引 pr["additions"]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 開啟檔案，可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程中發生例外，檔案不會被關閉。

建議：使用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 62 行：手動 open/close。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 的 int(raw) 可能拋出 ValueError</summary>

`threshold_from_env` 將環境變數 `PR_STALE_DAYS` 直接轉為 int，若該值不是有效整數，會拋出 `ValueError` 且未處理。

建議：捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 43 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:83</code> main 中重複呼叫 _fetch 且未檢查回傳值</summary>

`main` 中先呼叫 `collect_authors` 取得作者，然後在迴圈中再次呼叫 `_fetch` 取得 PR 資料，造成重複請求。且 `_fetch` 可能回傳 `None`（因為例外被吞掉），後續程式碼會因 `pr["user"]` 等鍵而崩潰。

建議：只呼叫一次 `_fetch` 並重用結果，並檢查回傳值。

**判斷依據**：diff 第 70-78 行：重複 fetch 且未檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3355 (cache hit 256) ｜ completion tokens 1918 ｜ PR #12</sub>