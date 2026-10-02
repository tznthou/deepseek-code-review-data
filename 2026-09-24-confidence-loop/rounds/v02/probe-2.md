<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的退出碼，可能把錯誤輸出當成正常結果；`list_tags` 在只有一個 tag 時會因索引 -1 而選到錯誤的 prev；`max_items` 對負數或零沒有下限，可能產生空公告；`post` 未驗證 URL scheme，可能被用於 SSRF。建議先修正這些正確性與安全性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個 tag 時，prev 會取到最後一個 tag 而非前一個版本 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | NOTES_MAX 設為負數或零時，會產生空公告或錯誤 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有傳入 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True`，或明確檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 中 `commits_between` 的 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個 tag 時，prev 會取到最後一個 tag 而非前一個版本</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是列表第一個元素時，索引 -1 會取到最後一個 tag，導致 `commits_between` 的範圍錯誤。例如 repo 只有 `v1.0.0` 一個 tag 時，`prev` 會是 `v1.0.0` 本身，`git log v1.0.0..v1.0.0` 會回傳空。建議在 `tags.index(tag) == 0` 時改用其他方式決定 prev（例如第一個 commit 或直接報錯）。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，沒有檢查 `tag` 是否為第一個元素。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> NOTES_MAX 設為負數或零時，會產生空公告或錯誤</summary>

`max_items` 只處理了非整數的情況，但沒有檢查 `int(raw)` 是否為正數。如果 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空列表，`render` 會產生只有標題的公告；如果 `NOTES_MAX=-1`，切片會取到倒數第一個元素，行為怪異。建議加上 `if n <= 0: return DEFAULT_MAX` 之類的檢查。

**判斷依據**：diff 中 `max_items` 只處理 `ValueError`，沒有檢查轉換後的整數是否大於 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，沒有檢查 scheme 是否為 `http` 或 `https`。如果攻擊者能控制 `NOTES_WEBHOOK` 環境變數（例如 CI 環境），可以指定 `file:///etc/passwd` 或 `gopher://` 等 scheme，造成資訊洩漏或 SSRF。建議在 `post` 開頭加上 `if not url.startswith(('http://', 'https://')): raise ValueError(...)`。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 建立 Request，沒有檢查 scheme。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1251 ｜ PR #14</sub>