<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 沒有檢查 `git log` 的退出碼，可能把錯誤訊息當成 commit 處理；`list_tags` 在找不到符合條件的 tag 時會讓 `main` 因 `IndexError` 崩潰；`max_items` 對負數或非整數的環境變數處理不完整。建議先修正這三個正確性問題，再考慮合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 未檢查 git log 的退出碼，可能把錯誤訊息當成 commit | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 找不到符合條件的 tag 時會因 IndexError 崩潰 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:38` | NOTES_MAX 為負數或非整數時處理不完整 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 未檢查 git log 的退出碼，可能把錯誤訊息當成 commit</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串或錯誤訊息（stderr 不會被擷取），函式會回傳空列表或把錯誤訊息當成 commit 解析。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 找不到符合條件的 tag 時會因 IndexError 崩潰</summary>

`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 且格式正確的 tag）。在 `main` 中，`tags.index(tag)` 會拋出 `ValueError`，但即使 tag 存在於列表中，若它是第一個元素，`tags[tags.index(tag) - 1]` 會取到 `tags[-1]`（最後一個元素），而不是前一個 tag。建議在 `list_tags` 後檢查列表是否為空，並明確處理 tag 是第一個元素的情況。

**判斷依據**：diff 中 `prev = tags[tags.index(tag) - 1]` 沒有考慮 `tags` 為空或 `tag` 是第一個元素的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:38</code> NOTES_MAX 為負數或非整數時處理不完整</summary>

`max_items` 只處理了 `ValueError`，但 `int(raw)` 也可能拋出 `TypeError`（如果 `raw` 是 `None` 以外的非字串型別，但環境變數一定是字串，所以實際上不會）。另外，如果 `NOTES_MAX` 是負數，`commits[: max_items()]` 會取到空列表，導致公告沒有內容。建議加上範圍檢查，例如 `max(0, int(raw))` 或明確拒絕負數。

**判斷依據**：diff 中 `max_items` 沒有處理負數或非整數輸入，且 `commits[: max_items()]` 可能因負數而得到空列表。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3863 (cache hit 3840) ｜ completion tokens 987 ｜ PR #14</sub>