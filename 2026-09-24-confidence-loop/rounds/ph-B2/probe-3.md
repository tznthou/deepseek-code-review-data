<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗（可能回傳空列表而誤判為無 commit）、`list_tags` 在只有一個 tag 時會因 `tags.index(tag) - 1` 變成 -1 而取到最後一個 tag、`max_items` 未處理負數或零值、`post` 未驗證 URL scheme、以及 `load_config` 未限制設定檔大小。整體結構清晰，但上述問題可能導致錯誤的公告內容或維運困擾。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能誤判為無 commit | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個 tag 時會取到錯誤的 prev tag | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | NOTES_MAX 未處理負數或零值 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能造成 SSRF 或誤用 | 0.60 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | 設定檔讀取未限制大小，可能造成記憶體耗盡 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能誤判為無 commit</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有 `check=True`，如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.returncode` 非零但程式不會拋出例外，`proc.stdout` 可能為空，導致函式回傳空列表。呼叫端 `main` 看到空列表會印出「沒有新 commit」並回傳 0，但實際上可能是錯誤。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時記錄錯誤並回傳非零。

**判斷依據**：diff 中 `commits_between` 的 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個 tag 時會取到錯誤的 prev tag</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是列表第一個元素時，`tags.index(tag)` 為 0，`-1` 會取到最後一個 tag，而不是沒有前一個 tag。這會導致 release notes 包含從最後一個 tag 到目前 tag 的所有 commit，內容錯誤。建議檢查 `tags.index(tag) == 0` 並處理（例如回報錯誤或使用 repo 初始 commit）。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未處理 index 為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> NOTES_MAX 未處理負數或零值</summary>

`max_items` 將環境變數轉為整數後直接回傳，若設定為負數或 0，`commits[: max_items()]` 會得到空列表或全部 commit（負數切片會從尾端取），可能造成非預期行為。建議限制最小值為 1 或驗證範圍。

**判斷依據**：diff 中 `max_items` 只處理 ValueError，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能造成 SSRF 或誤用</summary>

`post` 直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，未檢查是否為 http/https。若誤設為 `file://` 或其他 scheme，可能讀取本機檔案或造成非預期行為。建議驗證 URL scheme 為 http 或 https。

**判斷依據**：diff 中 `post` 函式直接將 `url` 傳給 `urllib.request.Request`，無任何 scheme 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> 設定檔讀取未限制大小，可能造成記憶體耗盡</summary>

`load_config` 直接 `json.load(fh)`，若 `.release-notes.json` 非常大（例如誤放大型檔案），可能耗盡記憶體。建議限制檔案大小或使用串流解析。

**判斷依據**：diff 中 `load_config` 無檔案大小限制。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1289 ｜ PR #14</sub>