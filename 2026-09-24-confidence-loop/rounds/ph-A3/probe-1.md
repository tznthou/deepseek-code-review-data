<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於 `commits_between` 沒有檢查 git 指令的失敗（例如 repo 路徑錯誤或 tag 不存在時會回傳空字串，導致後續邏輯誤判），以及 `prev` 的取得在 tag 是第一個 tag 時會拋出 IndexError。此外，`max_items()` 對負數或零沒有防護，可能造成切片行為不如預期。建議先修正這些錯誤處理路徑。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致誤判為無 commit | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個 tag 時，prev 取得會拋出 IndexError | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | max_items() 未處理負數或零，可能造成切片行為異常 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致誤判為無 commit</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空 list，而 `main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式沒有檢查 `proc.returncode`，且 `subprocess.run` 未設 `check=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個 tag 時，prev 取得會拋出 IndexError</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，索引會變成 -1，取到最後一個 tag，而不是報錯。這可能導致錯誤的 commit 範圍。建議檢查 `tags.index(tag) == 0` 的情況，並給出明確的錯誤訊息。

**判斷依據**：diff 中該行直接使用 `tags.index(tag) - 1`，沒有處理 index 為 0 的邊界。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> max_items() 未處理負數或零，可能造成切片行為異常</summary>

`max_items()` 將環境變數 `NOTES_MAX` 轉成整數，但沒有檢查是否為正數。如果設定為負數或零，`commits[: max_items()]` 會得到空 list 或意外的結果。建議加上檢查，若小於 1 則使用預設值或報錯。

**判斷依據**：diff 中 `max_items()` 只處理了 ValueError，沒有檢查數值範圍。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 894 ｜ PR #14</sub>