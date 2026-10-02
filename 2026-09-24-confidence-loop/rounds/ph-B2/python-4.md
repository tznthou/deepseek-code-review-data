<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的 Python 腳本。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未正確釋放。最該先修的是 _fetch 的例外處理與 archive 的 shell 注入，因為它們可能導致靜默失敗或任意指令執行。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致靜默失敗 | 0.95 |
| 🛑 | Blocker | `sandbox/pr_stats.py:77` | shell=True 且指令字串包含外部輸入，存在指令注入風險 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | 可變預設值 seen=[] 導致跨呼叫狀態累積 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | 檔案未使用 with 開啟，例外時可能洩漏資源 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | 環境變數轉換為整數未處理例外 | 0.80 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 依賴可能不存在的鍵 | 0.70 |
| 🔸 | Minor | `sandbox/pr_stats.py:38` | review_latency 對空 timeline 回傳 0 可能誤導 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致靜默失敗</summary>

`_fetch` 中的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），使呼叫端無法得知失敗，後續程式碼會因 `pr` 為 `None` 而拋出 `TypeError` 或 `KeyError`。例如：當 GitHub API 回傳 404 或網路中斷時，`_fetch` 回傳 `None`，`collect_authors` 中的 `pr["user"]["login"]` 會拋出 `TypeError`。建議至少記錄錯誤並重新拋出，或讓呼叫端處理 `None`。

**判斷依據**：diff 第 24 行：`except:` 後只有 `pass`，沒有記錄或重新拋出。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:77</code> shell=True 且指令字串包含外部輸入，存在指令注入風險</summary>

`archive` 使用 `subprocess.run` 搭配 `shell=True`，且指令字串中包含 `repo` 和 `path`，這些值來自命令列參數或環境，攻擊者可注入額外指令。例如：`repo` 設為 `foo; rm -rf /` 時，會執行任意指令。建議改用參數列表形式並避免 `shell=True`，或對輸入進行嚴格驗證。

**判斷依據**：diff 第 63 行：`shell=True` 且 f-string 包含外部輸入。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> 可變預設值 seen=[] 導致跨呼叫狀態累積</summary>

`collect_authors` 的參數 `seen=[]` 使用可變預設值，每次呼叫都會共用同一個 list。若多次呼叫此函式，作者名稱會不斷累積，造成結果錯誤。例如：第一次呼叫後 `seen` 包含 ['alice']，第二次呼叫時會從 ['alice'] 開始，最後回傳 ['alice', 'bob'] 而非 ['bob']。建議改為 `seen=None`，並在函式內初始化。

**判斷依據**：diff 第 28 行：`seen=[]` 是可變預設值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> 檔案未使用 with 開啟，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若寫入過程中發生例外（如磁碟滿），檔案不會被關閉。建議使用 `with open(path, 'w') as f:` 確保資源釋放。

**判斷依據**：diff 第 57-61 行：手動 open/close，無例外處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> 環境變數轉換為整數未處理例外</summary>

`threshold_from_env` 中 `int(raw)` 可能拋出 `ValueError`，若環境變數 `PR_STALE_DAYS` 不是有效整數，程式會崩潰。建議捕捉例外並提供預設值或錯誤訊息。

**判斷依據**：diff 第 42 行：`int(raw)` 未處理轉換失敗。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 依賴可能不存在的鍵</summary>

`classify` 直接存取 `pr["additions"]`、`pr["changed_files"]`、`pr["title"]`，若 API 回應缺少這些鍵（例如權限不足或欄位變更），會拋出 `KeyError`。建議使用 `.get()` 並提供預設值。

**判斷依據**：diff 第 46-51 行：直接索引字典。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:38</code> review_latency 對空 timeline 回傳 0 可能誤導</summary>

當 `events` 為空時回傳 0，但 0 可能被解讀為「無延遲」，與實際情況（無資料）混淆。建議回傳 `None` 或拋出例外，讓呼叫端處理。

**判斷依據**：diff 第 34-35 行：空列表回傳 0。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3123 (cache hit 3072) ｜ completion tokens 1623 ｜ PR #12</sub>