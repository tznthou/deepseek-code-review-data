<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並透過 webhook 發布。主要風險在於：`commits_between` 未檢查 git 指令的失敗，可能導致後續程式在錯誤資料上執行；`max_items` 未處理負數或零，可能造成輸出異常；`post` 函式未驗證 URL scheme，可能被用於 SSRF；此外，`group` 函式對 commit subject 的解析可能因格式不符而誤分類。建議優先修正 git 指令的錯誤處理與 URL 驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查，可能導致後續處理錯誤資料 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:31` | NOTES_MAX 未驗證範圍，負數或零可能造成非預期行為 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:74` | commit subject 解析可能因格式不符而誤分類 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，可能導致後續處理錯誤資料</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 損壞、權限不足或 tag 不存在而失敗，`proc.stdout` 可能為空或包含錯誤訊息，函式仍會回傳空列表或解析出錯誤的 commit。後續 `main` 會將空列表視為「沒有新 commit」而回傳 0，或將錯誤訊息當成 commit 處理。建議加上 `check=True` 或檢查 `returncode`，並在失敗時拋出例外或回傳明確錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且未設定 `check=True`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:31</code> NOTES_MAX 未驗證範圍，負數或零可能造成非預期行為</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數，`commits[: max_items()]` 會回傳空列表，導致輸出空白；若設定為 0，同樣回傳空列表。建議在轉換後檢查 `value > 0`，否則回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items` 僅處理 `ValueError`，未檢查轉換後的值是否為正整數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 函式直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，未驗證其 scheme 是否為 `https`。攻擊者若控制環境變數，可將其設為 `file:///etc/passwd` 或內網位址，導致讀取任意檔案或掃描內網。建議在 `main` 中檢查 URL 是否以 `https://` 開頭，否則拒絕執行。

**判斷依據**：diff 中 `post` 函式未對 `url` 進行 scheme 驗證，直接傳給 `urllib.request.Request`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:74</code> commit subject 解析可能因格式不符而誤分類</summary>

`group` 函式以 `subject.split(":", 1)[0]` 作為分類依據，若 commit subject 不含冒號，則整個 subject 會被當成 prefix，並歸入 `other`。這可能導致大量 commit 被錯誤分類，影響 release notes 的可讀性。建議僅在 prefix 符合已知標籤時才使用，否則一律歸入 `other`。

**判斷依據**：diff 中 `group` 函式未檢查 prefix 是否為有效標籤，直接使用 `subject.split(":", 1)[0]`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3917 (cache hit 3840) ｜ completion tokens 1197 ｜ PR #14</sub>