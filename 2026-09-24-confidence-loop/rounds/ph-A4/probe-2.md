<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於 `commits_between` 沒有檢查子程序失敗、`prev` 的計算在只有一個 tag 時會出錯、`NOTES_MAX` 沒有下限、webhook URL 未驗證 scheme，以及 `post` 沒有處理 HTTP 錯誤狀態碼。建議優先修正 `commits_between` 的錯誤處理與 `prev` 的邊界條件。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `commits_between` 未檢查子程序失敗，可能回傳空列表並誤導流程 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個符合條件的 tag 時，`prev` 會取到 `tags[-1]` 造成錯誤 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | `NOTES_MAX` 沒有下限，可能導致負數或零造成意外行為 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期協定 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:96` | `post` 未處理 HTTP 錯誤狀態碼，可能誤報成功 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `commits_between` 未檢查子程序失敗，可能回傳空列表並誤導流程</summary>

`subprocess.run` 沒有設定 `check=True`，當 `git log` 失敗（例如 repo 路徑無效、git 不在 PATH、或 `prev..tag` 不是有效範圍）時，`proc.returncode` 非零但程式不會拋出例外。`proc.stdout` 可能為空字串，導致函式回傳空列表，`main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並記錄錯誤後回傳非零。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且回傳值 `proc` 的 `returncode` 未被檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個符合條件的 tag 時，`prev` 會取到 `tags[-1]` 造成錯誤</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag) - 1` 會是 `-1`，因此 `prev` 會變成最後一個 tag（即 `tag` 本身），導致 `prev..tag` 是空範圍，`commits_between` 回傳空列表，程式印出「之間沒有新 commit」並回傳 0。

建議：檢查 `tags.index(tag) == 0` 時，記錄錯誤並回傳非零，或改用 `tags[tags.index(tag) - 1] if tags.index(tag) > 0 else None` 並處理 `None`。

**判斷依據**：diff 中 `prev` 的計算沒有處理 `tag` 是第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> `NOTES_MAX` 沒有下限，可能導致負數或零造成意外行為</summary>

`max_items()` 將環境變數轉成整數，但沒有檢查是否為正數。若使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空列表或全部元素（負索引切片），導致公告內容不正確。

建議：在轉換後檢查 `value < 1` 時記錄警告並使用預設值。

**判斷依據**：diff 中 `max_items()` 只處理了 `ValueError`，沒有檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期協定</summary>

`post` 直接將 `url` 傳給 `urllib.request.Request`，沒有檢查 scheme 是否為 `http` 或 `https`。若環境變數被設為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或傳送資料到非預期的位置。

建議：在 `main` 中驗證 `url` 的 scheme 為 `http` 或 `https`，否則回傳錯誤。

**判斷依據**：diff 中 `url` 直接來自環境變數，未經 scheme 驗證即用於 `urllib.request.Request`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:96</code> `post` 未處理 HTTP 錯誤狀態碼，可能誤報成功</summary>

`post` 只檢查 `200 <= resp.status < 300`，但 `urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 404、500）時會拋出 `urllib.error.HTTPError`，而 `HTTPError` 是 `URLError` 的子類別，因此會被 `except urllib.error.URLError` 捕捉並記錄錯誤，但函式回傳 `False`，`main` 會回傳 1。這部分行為正確，但若 webhook 端回傳 3xx 重定向，`urlopen` 會自動跟隨，最終可能得到 2xx 或拋出例外。整體而言，錯誤處理尚可，但建議明確捕捉 `HTTPError` 以提供更精確的錯誤訊息。

**判斷依據**：diff 中 `post` 的例外處理只捕捉 `URLError`，未區分 `HTTPError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1623 ｜ PR #14</sub>