<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並透過 webhook 發佈。主要風險在於：`commits_between` 未檢查 git 指令失敗，可能導致後續處理空輸出或錯誤資料；`max_items` 未限制負數，可能造成切片邏輯錯誤；`post` 未驗證 webhook URL 的 scheme，可能被用於 SSRF。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查，可能導致後續處理空輸出或錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:40` | NOTES_MAX 未限制為正整數，負數可能造成切片邏輯錯誤 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:118` | tag 列表為空時索引錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，可能導致後續處理空輸出或錯誤資料</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑無效、權限不足、或 `prev..tag` 範圍不存在），`proc.stdout` 可能為空字串或包含錯誤訊息，但函式仍會回傳空列表或解析錯誤的內容。後續 `main` 會將空列表視為「沒有新 commit」而回傳 0，或將錯誤訊息當成 commit 處理。

建議：加上 `check=True` 或檢查 `proc.returncode != 0` 時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `subprocess.run` 未設定 `check=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:40</code> NOTES_MAX 未限制為正整數，負數可能造成切片邏輯錯誤</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未驗證其值是否為正數。若設定為負數（例如 `-1`），`commits[: max_items()]` 會變成 `commits[:-1]`，導致最後一個 commit 被排除，且不會有任何警告。

建議：檢查 `max_items` 回傳值，若小於 1 則使用預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 僅處理 `ValueError`，未檢查轉換後的值是否為正數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，未驗證其 scheme 是否為 `https` 或 `http`。攻擊者若控制環境變數，可將其設為 `file:///etc/passwd` 或內網位址，導致程式讀取任意檔案或掃描內網。

建議：檢查 URL 的 scheme 必須為 `https`（或明確允許的 scheme），並考慮限制目標網域。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 參數，未進行任何 scheme 或網域驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:118</code> tag 列表為空時索引錯誤</summary>

`list_tags` 回傳的列表可能為空（例如 repo 中沒有任何符合 `v*` 的 tag）。在 `main` 中，`tags.index(tag)` 會拋出 `ValueError`，但若 `tag` 不在列表中，程式會先檢查 `if tag not in tags` 並回傳錯誤，因此不會執行到 `tags.index(tag)`。然而，若 `tags` 為空且 `tag` 不在其中，`if tag not in tags` 為真，程式會回傳 2，不會有問題。但若 `tags` 為空且 `tag` 恰好為空字串（不可能，因為前面已驗證格式），所以此情境不會發生。因此此問題可能不存在，但建議仍檢查 `tags` 是否為空，避免未來修改時引入錯誤。

**判斷依據**：diff 中 `main` 函式在 `tag not in tags` 檢查後直接使用 `tags.index(tag)`，但未檢查 `tags` 是否為空。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3917 (cache hit 1664) ｜ completion tokens 1302 ｜ PR #14</sub>