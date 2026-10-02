<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 抓取兩個 tag 之間的 commit，分類後貼到 webhook。主要風險在於 `commits_between` 沒有檢查 git 指令的失敗，以及 `prev` 的計算在 tag 是第一個時會出錯。另外，`max_items` 對負數或非整數的處理可能造成非預期行為。整體而言，程式碼結構清楚，但需要修正上述問題以確保穩健性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查，可能回報成功但沒有內容 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個 tag 時，prev 會取到錯誤的 tag | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:40` | NOTES_MAX 為負數或零時，max_items 回傳非預期值 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，可能回報成功但沒有內容</summary>

`subprocess.run` 沒有設定 `check=True`，當 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗時，`proc.returncode` 非零，但程式仍會繼續執行，最後可能回傳空列表並視為成功。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式內呼叫 `subprocess.run` 但沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個 tag 時，prev 會取到錯誤的 tag</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，`tags.index(tag)` 為 0，`-1` 會取到最後一個 tag，導致 `git log` 範圍錯誤。應檢查 index 是否為 0，若是則可能沒有前一個 tag，需處理此情況（例如從 repo 初始 commit 開始）。

**判斷依據**：diff 中 `main` 函式內直接使用 `tags.index(tag) - 1`，未檢查是否為 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:40</code> NOTES_MAX 為負數或零時，max_items 回傳非預期值</summary>

`max_items` 直接將環境變數轉為整數，若設定為負數或零，`commits[: max_items()]` 會得到空列表或全部元素（負數切片），可能非使用者預期。建議限制最小值為 1 或驗證範圍。

**判斷依據**：diff 中 `max_items` 函式僅處理 ValueError，未檢查數值範圍。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 822 ｜ PR #14</sub>