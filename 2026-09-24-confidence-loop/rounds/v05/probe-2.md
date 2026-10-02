<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 git 指令的失敗、`list_tags` 在只有一個 tag 時會 IndexError、`max_items` 對負數或零沒有防護、以及 webhook URL 未驗證 scheme。建議先修正這些正確性與安全性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能產生不完整的 release notes | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個符合條件的 tag 時會 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | NOTES_MAX 設為負數或零時會產生空公告或錯誤 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期請求 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能產生不完整的 release notes</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，導致後續流程誤以為沒有 commit 而直接回傳 0。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 中 `commits_between` 的 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個符合條件的 tag 時會 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tags` 只有一個元素且該元素就是 `tag` 時，`tags.index(tag)` 回傳 0，`0 - 1` 變成 -1，`tags[-1]` 會取到同一個 tag，導致 `prev == tag`，`git log prev..tag` 會是空範圍。如果 `tags` 是空 list（但前面已檢查 `tag in tags`，所以不會是空），但只有一個 tag 時會發生。建議在只有一個 tag 時明確處理，例如回傳錯誤或改用 `--max-count` 等方式。

**判斷依據**：diff 中 `prev = tags[tags.index(tag) - 1]` 沒有檢查 `tags.index(tag)` 是否為 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> NOTES_MAX 設為負數或零時會產生空公告或錯誤</summary>

`max_items()` 只檢查 `int(raw)` 是否拋出 `ValueError`，但沒有檢查轉換後的值是否為正整數。如果 `NOTES_MAX=0`，`commits[:0]` 會是空 list，`group` 會回傳空 sections，`render` 會產生只有標題的公告。如果 `NOTES_MAX=-1`，`commits[:-1]` 會排除最後一個 commit，可能不是預期行為。建議加上 `if n <= 0: log(...); return DEFAULT_MAX` 或類似防護。

**判斷依據**：diff 中 `max_items` 只處理 `ValueError`，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期請求</summary>

`post` 直接使用 `urllib.request.urlopen(req)`，沒有檢查 URL 的 scheme 是否為 `https` 或 `http`。如果環境變數 `NOTES_WEBHOOK` 被設為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或傳送資料到非預期的位置。建議在 `main` 中驗證 URL 的 scheme 和 host，或至少限制為 `https`。

**判斷依據**：diff 中 `post` 未對 `url` 做任何驗證，直接傳給 `urlopen`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1287 ｜ PR #14</sub>