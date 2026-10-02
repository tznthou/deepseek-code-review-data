<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗回傳碼，可能導致空結果被誤判為無 commit；`list_tags` 在 tag 不存在時會因 `tags.index(tag)` 拋出 `ValueError` 而崩潰；`max_items` 對負數或零值未做下限處理，可能造成切片行為異常。此外，`post` 函式未驗證 webhook URL 的 scheme，存在 SSRF 風險。整體而言，程式碼結構清晰，但上述問題可能導致錯誤的輸出或安全疑慮，建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能誤判為無 commit | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | `tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError` | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | `max_items` 未處理負數或零值，可能導致切片行為異常 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | `post` 函式未驗證 webhook URL 的 scheme，存在 SSRF 風險 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能誤判為無 commit</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list，導致主流程印出「之間沒有新 commit」並回傳 0，但實際上是錯誤。建議加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `subprocess.run` 未設 `check=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> `tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError`</summary>

`main` 中先檢查 `if tag not in tags`，但 `tags` 是 `list_tags` 回傳的 list，而 `list_tags` 只回傳符合 `TAG_RE` 的 tag。若使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為 True，會先印出錯誤並 return 2，不會執行到 `tags.index(tag)`。但若 `list_tags` 因某些原因回傳的 list 不包含該 tag（例如 tag 名稱符合 regex 但實際不存在），則 `tags.index(tag)` 會拋出 `ValueError`，導致程式崩潰。建議使用 `try/except` 或先檢查 `tag in tags` 再取 index。

**判斷依據**：diff 中 `main` 函式在 `if tag not in tags` 檢查後直接使用 `tags.index(tag)`，但未處理 `ValueError`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> `max_items` 未處理負數或零值，可能導致切片行為異常</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未檢查是否為正數。若設定為負數，`commits[: max_items()]` 會回傳空 list（因為負索引切片會從尾端取，但這裡是負數會導致空結果），若為 0 則回傳空 list，可能造成公告內容空白。建議加上下限檢查，例如 `max(1, int(raw))` 或明確拒絕非正整數。

**判斷依據**：diff 中 `max_items` 函式僅處理 `ValueError`，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> `post` 函式未驗證 webhook URL 的 scheme，存在 SSRF 風險</summary>

`post` 直接使用 `urllib.request.urlopen` 開啟使用者提供的 URL（來自環境變數 `NOTES_WEBHOOK`）。若攻擊者能控制該環境變數，可指定 `file://` 或 `gopher://` 等 scheme 來讀取本機檔案或進行內網探測。建議限制 scheme 為 `http` 或 `https`，並可考慮驗證主機名稱。

**判斷依據**：diff 中 `post` 函式未對 `url` 進行 scheme 檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1320 ｜ PR #14</sub>