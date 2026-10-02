<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，並透過 webhook 貼到團隊頻道。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的退出碼，當 repo 路徑錯誤或 tag 不存在時會靜默產生空結果；其次是 `prev` 的取得方式在 tag 是第一個版本時會拋出 IndexError；另外 `max_items()` 沒有處理負數或零，可能導致輸出空白公告。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 失敗時未檢查退出碼，可能靜默產生空結果 | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，`prev` 會拋出 IndexError | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | `max_items()` 未處理負數或零，可能導致空白公告 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查退出碼，可能靜默產生空結果</summary>

`subprocess.run` 沒有設定 `check=True`，當 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗時，`proc.returncode` 非零，但程式碼完全沒有檢查，會繼續處理空的 `stdout`，最後回報成功並可能貼出空白公告。

建議：加上 `check=True`，或在執行後檢查 `proc.returncode != 0` 並記錄錯誤後返回非零退出碼。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，`prev` 會拋出 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是拋出錯誤。這會導致錯誤的 commit 範圍，甚至可能讓 `git log` 失敗。

建議：先檢查 `tags.index(tag) == 0`，若是第一個 tag，則記錄錯誤並返回非零退出碼，或改用 `git log tag` 來取得該 tag 的所有 commit。

**判斷依據**：diff 中 `main()` 函式在取得 `prev` 時直接使用 `tags.index(tag) - 1`，沒有處理 `tag` 是第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> `max_items()` 未處理負數或零，可能導致空白公告</summary>

`max_items()` 只處理了非整數輸入，但若 `NOTES_MAX` 設為負數或零，`commits[: max_items()]` 會得到空列表，導致 `render` 產生只有標題的公告，並可能貼出空白內容。

建議：在 `max_items()` 中檢查數值是否大於 0，否則回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items()` 函式只處理 `ValueError`，沒有檢查轉換後的整數是否為正數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 966 ｜ PR #14</sub>