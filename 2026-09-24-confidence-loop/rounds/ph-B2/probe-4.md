<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗回傳碼，可能導致後續程式碼在空列表上執行並拋出未處理的例外；`max_items` 未處理負數或零，可能造成切片行為異常；`post` 函式未檢查 HTTP 狀態碼，可能將失敗視為成功；此外，`load_config` 的 JSON 解析錯誤處理可能造成程式提前終止。整體而言，程式碼結構清晰，但錯誤處理與輸入驗證需要加強。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 的失敗回傳碼 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:42` | max_items 未處理負數或零 | 0.75 |
| ⚠️ | Major | `sandbox/release_notes.py:94` | post 函式未檢查 HTTP 狀態碼 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:34` | load_config 的 JSON 解析錯誤處理可能造成程式提前終止 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 的失敗回傳碼</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，後續 `main` 中的 `commits[0][0]` 會拋出 `IndexError`，導致程式崩潰。建議加上 `check=True` 或檢查 `proc.returncode` 並處理錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `main` 中直接使用 `commits[0][0]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:42</code> max_items 未處理負數或零</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會產生空列表或意外結果（負數切片會從尾端取元素），可能導致公告內容不正確。建議驗證數值必須大於 0，否則使用預設值。

**判斷依據**：diff 中 `max_items` 函式僅處理 `ValueError`，未檢查數值範圍。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:94</code> post 函式未檢查 HTTP 狀態碼</summary>

`post` 函式在 `urlopen` 成功後僅回傳 `200 <= resp.status < 300`，但未處理其他狀態碼（如 4xx、5xx）。若 webhook 回傳 404 或 500，函式會回傳 `False`，但呼叫端 `main` 會回傳 1，導致程式被視為失敗。建議明確處理非 2xx 狀態碼，記錄錯誤並回傳 `False`。

**判斷依據**：diff 中 `post` 函式僅回傳布林值，未區分不同錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:34</code> load_config 的 JSON 解析錯誤處理可能造成程式提前終止</summary>

`load_config` 在 JSON 解析失敗時直接 `raise SystemExit`，這會讓整個程式終止，即使設定檔是選配的。若設定檔損壞，使用者可能無法產生 release notes。建議改為記錄警告並回傳空字典，或讓呼叫端決定是否終止。

**判斷依據**：diff 中 `load_config` 的例外處理直接終止程式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1147 ｜ PR #14</sub>