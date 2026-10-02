<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。整體結構清楚，但存在幾個值得注意的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的退出碼，可能把錯誤輸出當成正常結果；其次是 `prev` 的取得方式在 tag 是第一個版本時會拋出 IndexError；另外 `NOTES_MAX` 的解析沒有處理負數或零，可能導致公告內容不完整。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:40` | `NOTES_MAX` 未處理負數或零，可能導致公告內容不完整 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 來解析。建議加上 `check=True`，或至少檢查 `proc.returncode != 0` 時記錄錯誤並回傳空列表。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError</summary>

如果使用者指定的 tag 是 `tags` 列表中的第一個元素（例如 repo 只有一個 tag），`tags.index(tag) - 1` 會是 -1，`tags[-1]` 會取到最後一個 tag，而不是拋出錯誤。這會導致 `prev` 指向錯誤的 tag，產生錯誤的 commit 範圍。建議在 `tags.index(tag) == 0` 時顯示錯誤訊息並回傳非零退出碼。

**判斷依據**：diff 中這一行直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:40</code> `NOTES_MAX` 未處理負數或零，可能導致公告內容不完整</summary>

`max_items()` 將 `NOTES_MAX` 轉成整數後直接回傳，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=0` 或負數，`commits[: max_items()]` 會是空列表或錯誤切片，導致公告沒有內容或拋出例外。建議在轉換後檢查數值是否大於 0，否則使用預設值。

**判斷依據**：diff 中 `max_items()` 只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 948 ｜ PR #14</sub>