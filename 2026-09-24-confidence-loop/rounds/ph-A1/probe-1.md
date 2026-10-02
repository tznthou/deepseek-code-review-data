<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，從 git log 整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。主要風險在於：`commits_between` 未檢查 `git log` 的 return code，可能把錯誤輸出當成正常結果；`list_tags` 在 tag 是第一個版本時會因 `tags.index(tag) - 1` 變成 -1 而取到最後一個 tag；`max_items` 對負數或零沒有防護，可能導致公告內容為空或行為怪異。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 的 return code，可能把錯誤輸出當成正常結果 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，prev 會取到最後一個 tag | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:39` | NOTES_MAX 設為負數或零時沒有防護 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 的 return code，可能把錯誤輸出當成正常結果</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串或錯誤訊息，函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，prev 會取到最後一個 tag</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`0 - 1` 等於 -1，Python 會取到最後一個元素。這會導致 release notes 涵蓋從最後一個 tag 到第一個 tag 的所有 commit，而不是空範圍。建議在 `tags.index(tag) == 0` 時處理為沒有前一個 tag 的情況（例如回傳空列表或提示錯誤）。

**判斷依據**：diff 中 `main` 函式內 `prev = tags[tags.index(tag) - 1]`，沒有檢查 `tags.index(tag)` 是否為 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:39</code> NOTES_MAX 設為負數或零時沒有防護</summary>

`max_items` 直接將環境變數轉為整數，沒有檢查是否為正數。如果 `NOTES_MAX` 設為負數，`commits[: max_items()]` 會取到空列表或部分列表；設為 0 也會得到空列表。建議限制最小值為 1，或在使用前檢查。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 924 ｜ PR #14</sub>