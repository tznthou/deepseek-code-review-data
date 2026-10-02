<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的退出碼，當 repo 路徑錯誤或 tag 不存在時，程式會繼續用空的 stdout 往下走，最後可能貼出空公告；其次是 `prev` 的取得方式在 tag 是第一個 tag 時會拋出 IndexError；另外 `max_items` 對負數或零沒有防護，可能造成切片行為不如預期。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 失敗時未檢查退出碼，可能貼出空公告 | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 是第一個 tag 時會拋出 IndexError | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:34` | NOTES_MAX 為負數或零時切片行為異常 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查退出碼，可能貼出空公告</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。當 `repo` 路徑不存在、不是 git repo，或 `prev`/`tag` 不存在時，`git log` 會以非零退出碼結束，但程式會繼續執行，`proc.stdout` 會是空字串，最後 `commits` 為空 list。接著 `main` 會因為 `if not commits` 而直接回傳 0，不會貼出任何東西，但也不會回報錯誤，使用者會以為成功。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 是第一個 tag 時會拋出 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 會是 0，`0 - 1` 變成 -1，`tags[-1]` 會取到最後一個 tag，而不是報錯。這會導致 release notes 的範圍錯誤（從最後一個 tag 到第一個 tag）。

建議：檢查 `tags.index(tag) == 0` 時，提示使用者這是第一個 tag，沒有前一個 tag 可以比較。

**判斷依據**：diff 中 `main` 函式的這一行，沒有處理 `tag` 是第一個 tag 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:34</code> NOTES_MAX 為負數或零時切片行為異常</summary>

`max_items` 只處理了非整數的情況，沒有檢查負數或零。如果使用者設定 `NOTES_MAX=-1`，`commits[: -1]` 會回傳除了最後一個 commit 以外的所有 commit；如果設定 `NOTES_MAX=0`，會回傳空 list，導致公告沒有內容。

建議：在 `max_items` 中檢查 `value <= 0` 時回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有處理負數或零。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1033 ｜ PR #14</sub>