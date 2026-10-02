<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個從 GitHub API 撈 PR 資料並計算指標的小工具。主要風險在於錯誤處理不當（_fetch 吞掉所有例外）、可變預設值（collect_authors 的 seen=[]）、shell=True 的指令注入、以及資源未用 with 管理。最該先修的是 _fetch 的例外處理與 archive 的 shell 指令，因為它們可能導致靜默失敗或安全問題。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/pr_stats.py:24` | _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰 | 0.95 |
| ⚠️ | Major | `sandbox/pr_stats.py:29` | collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態 | 0.90 |
| ⚠️ | Major | `sandbox/pr_stats.py:77` | archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險 | 0.85 |
| ⚠️ | Major | `sandbox/pr_stats.py:69` | export_csv 未使用 with 管理檔案，例外時可能洩漏資源 | 0.80 |
| ⚠️ | Major | `sandbox/pr_stats.py:54` | threshold_from_env 未處理 int() 轉換失敗 | 0.75 |
| 🔸 | Minor | `sandbox/pr_stats.py:59` | classify 未處理 pr 缺少 additions 或 changed_files 鍵的情況 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/pr_stats.py:24</code> _fetch 吞掉所有例外，導致後續程式碼在資料缺失時崩潰</summary>

`_fetch` 的 `except: pass` 會吞掉所有例外（包括網路錯誤、HTTP 錯誤、JSON 解析錯誤），然後回傳 `None`。呼叫端（`collect_authors` 和 `main`）直接對回傳值做 `pr["user"]["login"]` 或 `pr["additions"]`，會拋出 `TypeError: 'NoneType' object is not subscriptable`。這會讓工具在 API 失敗時直接崩潰，且沒有錯誤訊息。建議：讓例外向上傳播，或在 `_fetch` 內記錄錯誤並拋出明確的例外，或回傳一個可辨識的錯誤物件。

**判斷依據**：diff 第 24 行 `except: pass`，且呼叫端（第 28、47 行）直接使用回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:29</code> collect_authors 使用可變預設值 seen=[]，跨呼叫累積狀態</summary>

`collect_authors` 的 `seen=[]` 是可變預設值，會在多次呼叫間共用同一個 list。雖然目前程式只呼叫一次，但這是一個常見的陷阱，未來若重複呼叫會導致結果累積。建議改為 `seen=None`，在函式內初始化為空 list。

**判斷依據**：diff 第 27 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:77</code> archive 使用 shell=True 且指令由外部輸入拼接，存在指令注入風險</summary>

`subprocess.run(f"tar czf {path}.tgz {path} && gh repo view {repo}", shell=True)` 中，`path` 和 `repo` 來自命令列參數，攻擊者可注入額外指令（例如 `repo` 設為 `x; rm -rf /`）。即使目前是內部工具，仍應避免 `shell=True`。建議改用 `subprocess.run` 的參數列表形式，並分開執行 `tar` 和 `gh`。

**判斷依據**：diff 第 65 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:69</code> export_csv 未使用 with 管理檔案，例外時可能洩漏資源</summary>

`export_csv` 使用 `open` 和 `close`，但若 `write` 拋出例外（例如磁碟滿），檔案不會被關閉。建議改用 `with open(path, "w") as f:`。

**判斷依據**：diff 第 58-62 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/pr_stats.py:54</code> threshold_from_env 未處理 int() 轉換失敗</summary>

`int(raw)` 若環境變數 `PR_STALE_DAYS` 不是有效整數（例如 "abc"），會拋出 `ValueError` 且未處理，導致程式崩潰。建議捕捉例外並提供預設值或明確錯誤訊息。

**判斷依據**：diff 第 36 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/pr_stats.py:59</code> classify 未處理 pr 缺少 additions 或 changed_files 鍵的情況</summary>

`pr["additions"]` 和 `pr["changed_files"]` 直接取值，若 API 回應缺少這些鍵（例如權限不足或 API 變更），會拋出 `KeyError`。建議使用 `pr.get("additions", 0)` 等方式。

**判斷依據**：diff 第 42-43 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3279 (cache hit 3200) ｜ completion tokens 1385 ｜ PR #12</sub>