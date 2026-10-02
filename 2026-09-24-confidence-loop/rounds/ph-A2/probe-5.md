<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並透過 webhook 發布。主要風險在於：`commits_between` 未檢查 `git log` 的退出碼，可能把錯誤輸出當成正常結果；`list_tags` 在 tag 不存在時會因 `tags.index(tag)` 拋出 `ValueError` 而直接崩潰；`max_items` 對負數或零沒有防護，可能導致公告內容為空或行為異常。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | `tags.index(tag)` 在 tag 不存在時拋出 `ValueError`，導致程式崩潰 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | `max_items` 未處理負數或零，可能導致公告內容為空 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查退出碼，可能把錯誤輸出當成正常結果</summary>

`subprocess.run` 沒有設定 `check=True`，當 `git log` 因為 repo 路徑錯誤、tag 不存在或權限問題失敗時，`proc.returncode` 非零，但程式仍會繼續解析 `proc.stdout`（可能是空字串或錯誤訊息），導致後續流程在錯誤的基礎上執行。建議加上 `check=True`，或明確檢查 `proc.returncode` 並在非零時拋出例外或回傳空列表。

**判斷依據**：diff 中 `commits_between` 函式的 `subprocess.run` 呼叫沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> `tags.index(tag)` 在 tag 不存在時拋出 `ValueError`，導致程式崩潰</summary>

`main` 中先檢查 `if tag not in tags`，但 `tags` 是 `list_tags` 回傳的列表，而 `list_tags` 只回傳符合 `TAG_RE` 的 tag。如果使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為真，程式會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，如果 `list_tags` 因為某些原因回傳的列表不包含該 tag（例如 tag 名稱大小寫不同），則 `tags.index(tag)` 會拋出 `ValueError`。建議使用更安全的方式取得前一個 tag，例如 `prev = tags[tags.index(tag) - 1] if tag in tags else None`，或直接使用 `try/except` 處理。

**判斷依據**：diff 中 `main` 函式在 `if tag not in tags` 檢查後直接使用 `tags.index(tag)`，但 `tags` 的內容可能因 `list_tags` 的過濾條件而與預期不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> `max_items` 未處理負數或零，可能導致公告內容為空</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但沒有檢查是否為正數。如果設定為 `0` 或負數，`commits[: max_items()]` 會得到空列表或錯誤切片，導致公告內容為空或行為異常。建議加上驗證，例如 `if value < 1: return DEFAULT_MAX`。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，未檢查轉換後的整數是否為正數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1054 ｜ PR #14</sub>