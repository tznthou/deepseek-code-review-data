<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於 `commits_between` 沒有檢查 `git log` 的失敗，可能把錯誤輸出當成正常結果；`list_tags` 在 tag 清單為空時會因索引 -1 而取到錯誤的 prev；`max_items` 對負數或超大值沒有防護；webhook URL 未驗證 scheme 可能造成 SSRF；以及 `post` 只處理 `URLError`，HTTP 錯誤狀態碼不會被記錄。建議先修正 `commits_between` 的錯誤處理與 `list_tags` 的邊界條件。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能把錯誤輸出當成正常結果 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | `list_tags` 回傳空列表時，`tags.index(tag) - 1` 會取到最後一個元素 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | `max_items` 未限制 `NOTES_MAX` 的範圍，可能導致記憶體耗盡或負數切片 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:96` | `post` 只捕捉 `URLError`，HTTP 錯誤狀態碼不會被記錄 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能把錯誤輸出當成正常結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 `prev..tag` 範圍無效而失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True` 或檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 第 55-58 行：`subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> `list_tags` 回傳空列表時，`tags.index(tag) - 1` 會取到最後一個元素</summary>

在 `main` 中，`prev = tags[tags.index(tag) - 1]`。如果 `tags` 是空列表（例如 repo 沒有任何符合 `v*` 的 tag），`tags.index(tag)` 會拋出 `ValueError`，但更隱晦的是如果 `tags` 非空但 `tag` 不在其中，`tags.index(tag)` 也會拋出 `ValueError`，這部分已有檢查。然而，如果 `tags` 只有一個元素且就是 `tag`，`tags.index(tag) - 1` 會是 `-1`，取到最後一個元素（即 `tag` 本身），導致 `prev` 等於 `tag`，`git log prev..tag` 會是空範圍。建議在取 `prev` 前檢查 `tags.index(tag) > 0`，否則回報錯誤。

**判斷依據**：diff 第 48 行：`prev = tags[tags.index(tag) - 1]`，未處理 `tags` 只有一個元素或 `tag` 是第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> `max_items` 未限制 `NOTES_MAX` 的範圍，可能導致記憶體耗盡或負數切片</summary>

`max_items` 直接將環境變數轉為整數，沒有檢查是否為負數或過大。若 `NOTES_MAX` 設為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，意外排除最後 n 筆；若設為極大值，可能嘗試處理大量 commit 造成記憶體壓力。建議加上範圍檢查（例如 1 到某個合理上限）。

**判斷依據**：diff 第 38-40 行：`int(raw)` 沒有範圍驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.urlopen`，沒有檢查 scheme 是否為 `https` 或 `http`。攻擊者若控制環境變數，可指定 `file://` 等 scheme 讀取本機檔案或觸發其他內部請求。建議驗證 URL 的 scheme 與 host。

**判斷依據**：diff 第 91 行：`url` 來自環境變數，未經 scheme 驗證即用於 `urllib.request.Request`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:96</code> `post` 只捕捉 `URLError`，HTTP 錯誤狀態碼不會被記錄</summary>

`urllib.request.urlopen` 在 HTTP 錯誤狀態碼（如 404、500）時會拋出 `urllib.error.HTTPError`，它是 `URLError` 的子類別，所以會被捕捉並記錄。但若伺服器回傳 3xx 重定向，`urlopen` 會自動跟隨，最終可能得到 200 或拋出錯誤。若回傳 4xx/5xx，`HTTPError` 會被捕捉，但 `post` 回傳 `False`，呼叫端會回傳 1，但沒有記錄具體的 HTTP 狀態碼。建議在 `except` 中檢查 `e.code` 並記錄。

**判斷依據**：diff 第 95-97 行：捕捉 `URLError` 但未記錄 HTTP 狀態碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1593 ｜ PR #14</sub>