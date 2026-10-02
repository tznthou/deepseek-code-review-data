<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，會從 git log 收集兩個 tag 之間的 commit，分類後貼到團隊頻道的 webhook。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，當 repo 路徑無效或 git 指令失敗時，程式會靜默地產生空的 commit 清單，導致後續流程誤判為「沒有新 commit」而回報成功。另外，`list_tags` 在 tag 清單只有一個元素時會發生索引錯誤，且 `max_items` 對負數或零的輸入沒有防護，可能造成輸出內容不完整。建議先修正這些正確性問題，再考慮合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 執行失敗時未檢查，導致靜默失敗 | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 清單只有一個元素時會 IndexError | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:34` | NOTES_MAX 未處理負數或零 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 執行失敗時未檢查，導致靜默失敗</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `repo` 路徑不存在、不是 git repository，或 `git log` 因其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空 list。呼叫端 `main` 會將空 list 解讀為「沒有新 commit」並回傳 0（成功），但實際上根本沒有取得任何資料。

**失敗情境**：使用者提供錯誤的 repo 路徑，程式會印出「之間沒有新 commit」並以 exit code 0 結束，讓 CI 或排程誤以為成功。

**建議**：在 `subprocess.run` 加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 清單只有一個元素時會 IndexError</summary>

`list_tags` 回傳符合 `TAG_RE` 的 tag 清單。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 假設 `tag` 在清單中且前面還有更早的 tag。如果 repo 只有一個符合條件的 tag（例如剛建立第一個 release），`tags.index(tag)` 會是 0，`tags[-1]` 會取到最後一個元素（也就是自己），導致 `prev` 等於 `tag`，`git log prev..tag` 會是空範圍，產生錯誤的結果。

**失敗情境**：在只有一個 tag 的 repo 上執行，程式會將該 tag 同時當作 prev 和 tag，導致 commit 清單為空，或產生非預期的輸出。

**建議**：在取 `prev` 前檢查 `tags.index(tag) > 0`，否則回報錯誤或改用其他方式決定起始點。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，未檢查邊界。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:34</code> NOTES_MAX 未處理負數或零</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但沒有檢查是否為正數。如果設定為 `0` 或負數，`commits[: max_items()]` 會產生空清單或錯誤的切片，導致輸出內容不完整或程式出錯。

**失敗情境**：使用者誤設 `NOTES_MAX=0`，程式會產生空的 release notes，但仍回報成功。

**建議**：在轉換後檢查數值是否大於 0，否則使用預設值或回報錯誤。

**判斷依據**：diff 中 `max_items` 只處理了 ValueError，未檢查數值範圍。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1196 ｜ PR #14</sub>