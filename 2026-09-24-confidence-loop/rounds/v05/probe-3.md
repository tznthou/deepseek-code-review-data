<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發布。主要風險在於錯誤處理不完整（例如 commits_between 未檢查 git 指令失敗、post 未處理 HTTP 錯誤狀態碼）、輸入驗證不足（NOTES_MAX 可為負數或零、tag 格式驗證可能與實際 tag 不符），以及潛在的資源管理問題（subprocess 未使用 with）。建議優先修正錯誤處理與輸入驗證，以確保工具在異常狀況下能正確回報而非靜默失敗。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | commits_between 未檢查 git log 的執行結果 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:96` | post 未處理非 2xx 的 HTTP 回應狀態碼 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | NOTES_MAX 未限制為正整數 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:50` | list_tags 使用 check=True 但未處理可能的例外 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:58` | subprocess 未使用 with 管理資源 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> commits_between 未檢查 git log 的執行結果</summary>

`subprocess.run` 未設定 `check=True`，且回傳的 `proc.returncode` 未被檢查。若 `git log` 因 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空字串，導致函式回傳空列表，後續流程會誤以為沒有 commit 而正常結束（回傳 0）。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:96</code> post 未處理非 2xx 的 HTTP 回應狀態碼</summary>

`urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 4xx、5xx）時會拋出 `urllib.error.HTTPError`，但此處只捕捉 `URLError`，因此 HTTP 錯誤會被視為未處理例外而導致程式崩潰。建議捕捉 `HTTPError` 並記錄狀態碼，或改用 `urllib.request.urlopen` 的 `context` 參數來處理。

**判斷依據**：diff 中 `except` 只捕捉 `URLError`，但 `urlopen` 在 HTTP 錯誤時會拋出 `HTTPError`（其為 `URLError` 的子類別，但若未捕捉會向上傳播）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> NOTES_MAX 未限制為正整數</summary>

`max_items()` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為 0 或負數，`commits[: max_items()]` 會得到空列表或錯誤切片，導致公告內容不完整或程式出錯。建議驗證數值必須大於 0，否則回退到預設值。

**判斷依據**：diff 中 `int(raw)` 成功後直接回傳，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:50</code> list_tags 使用 check=True 但未處理可能的例外</summary>

`subprocess.run` 設定 `check=True`，若 `git tag` 失敗會拋出 `CalledProcessError`，但呼叫端 `main()` 未捕捉此例外，導致程式直接崩潰並顯示 traceback。建議在 `main()` 中捕捉並轉換為使用者友善的錯誤訊息。

**判斷依據**：diff 中 `check=True` 會拋出例外，但 `main()` 未處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:58</code> subprocess 未使用 with 管理資源</summary>

`subprocess.run` 內部會建立 pipe 並等待子程序，雖然通常會自動清理，但若發生例外（如 `CalledProcessError`）可能導致資源洩漏。建議使用 `with subprocess.Popen(...) as proc:` 或確保在 `finally` 中關閉。

**判斷依據**：diff 中直接呼叫 `subprocess.run` 而未使用 `with` 或 `try/finally`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1407 ｜ PR #14</sub>