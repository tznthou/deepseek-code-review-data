<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並貼到團隊頻道的 webhook。主要風險在於 `commits_between` 沒有檢查子程序失敗，可能導致後續程式碼在錯誤的資料上執行；另外 `list_tags` 在沒有符合條件的 tag 時會拋出未處理的例外。整體結構清楚，但錯誤處理需要加強。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 子程序失敗時未檢查回傳碼，可能導致後續處理錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:109` | webhook URL 未驗證 scheme，可能造成 SSRF 或非預期請求 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 子程序失敗時未檢查回傳碼，可能導致後續處理錯誤資料</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、tag 不存在或其他原因失敗，`proc.stdout` 會是空字串，函式會回傳空列表，呼叫端會誤以為沒有 commit 而正常結束（回傳 0）。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式沒有檢查 `proc.returncode`，且 `main` 中 `if not commits:` 會將空列表視為正常情況回傳 0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> list_tags 在沒有符合條件的 tag 時會拋出未處理的 IndexError</summary>

`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 且通過 `TAG_RE` 的 tag）。在 `main` 中，`prev = tags[tags.index(tag) - 1]` 會先執行 `tags.index(tag)`，若 `tag` 不在列表中會拋出 `ValueError`，但若列表為空且 `tag` 不在其中，`tags.index(tag)` 同樣拋出 `ValueError`，這部分已有處理。然而，若 `tag` 是列表中的第一個元素，`tags.index(tag) - 1` 會是 -1，`tags[-1]` 會取到最後一個元素，這可能不是預期的「前一個 tag」。建議在 `main` 中檢查 `tags.index(tag) == 0` 的情況，並明確處理沒有前一個 tag 的狀況。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1` 作為索引，沒有檢查是否為 0。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:109</code> webhook URL 未驗證 scheme，可能造成 SSRF 或非預期請求</summary>

`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.urlopen`，沒有驗證 scheme 是否為 http/https。如果使用者誤設為 `file://` 或其他 scheme，可能導致讀取本地檔案或發出非預期請求。建議檢查 URL 的 scheme 是否為 `http` 或 `https`。

**判斷依據**：diff 中 `main` 函式取得 `NOTES_WEBHOOK` 後直接傳給 `post`，而 `post` 中直接使用 `urllib.request.urlopen`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 988 ｜ PR #14</sub>