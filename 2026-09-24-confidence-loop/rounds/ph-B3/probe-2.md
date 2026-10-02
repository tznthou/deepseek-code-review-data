<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗，可能導致後續在空列表上取 `commits[0]` 而崩潰；`list_tags` 在 tag 不存在時會因 `tags.index(tag)` 拋出 `ValueError`；`max_items` 對負數或非整數輸入的處理不完整；`post` 未驗證 URL scheme，可能被用於 SSRF。整體程式結構清楚，但錯誤處理需要加強。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能導致後續崩潰 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | `tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError` | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | `max_items` 未處理負數或非整數輸入 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | `post` 未驗證 URL scheme，可能被用於 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能導致後續崩潰</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 `prev..tag` 範圍無效而失敗，`proc.stdout` 會是空字串，函式回傳空列表。接著在 `main` 中 `commits[0]` 會拋出 `IndexError`，程式以 traceback 結束。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並回報錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `main` 中 `latest = commits[0][0]` 假設列表非空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> `tags.index(tag)` 在 tag 不存在時拋出未處理的 `ValueError`</summary>

`main` 中先檢查 `if tag not in tags`，但 `tags` 來自 `list_tags`，該函式只回傳符合 `TAG_RE` 的 tag。如果使用者輸入的 tag 格式正確但不在 repo 中（例如 `v9.9.9`），`tag not in tags` 為真，程式會印出錯誤並回傳 2，不會執行到 `tags.index(tag)`。然而，如果 `list_tags` 因為某種原因回傳的列表不包含該 tag（例如 tag 名稱大小寫不同），`tags.index(tag)` 仍可能拋出 `ValueError`。建議使用 `try/except` 或先取得 index 再檢查。

**判斷依據**：diff 中 `main` 函式在 `if tag not in tags` 之後直接呼叫 `tags.index(tag)`，未處理可能的 `ValueError`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> `max_items` 未處理負數或非整數輸入</summary>

`max_items` 將 `NOTES_MAX` 轉為整數，但未檢查是否為負數。若設定為負數，`commits[: max_items()]` 會變成 `commits[:-1]`，導致最後一個 commit 被排除。此外，若輸入為浮點數字串（如 `"3.5"`），`int()` 會拋出 `ValueError`，目前有處理，但負數未處理。建議加上 `if value < 0: return DEFAULT_MAX` 或類似檢查。

**判斷依據**：diff 中 `max_items` 函式只處理 `ValueError`，未檢查負數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> `post` 未驗證 URL scheme，可能被用於 SSRF</summary>

`post` 直接使用 `NOTES_WEBHOOK` 環境變數作為 URL，未檢查 scheme 是否為 `https`。如果攻擊者能控制環境變數（例如在 CI 中注入），可能導致請求發送到內部服務（如 `http://169.254.169.254/...`）。建議驗證 URL 的 scheme 和 host，或至少限制為 `https`。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 參數，未做任何驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1290 ｜ PR #14</sub>