<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器腳本，從 git tag 之間收集 commit、分類後貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗（可能導致後續處理空輸出或錯誤資料）、`group` 函式對 commit subject 的解析可能因格式不符而誤分類、`max_items` 對負數或過大值未設限、以及 webhook URL 未驗證 scheme 可能造成 SSRF。最該先修的是 `commits_between` 的錯誤處理，因為它會直接影響輸出內容的正確性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `commits_between` 未檢查 `git log` 的失敗 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:74` | `group` 函式對 commit subject 的解析可能誤分類 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:37` | `max_items` 未限制負數或過大值 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能造成 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `commits_between` 未檢查 `git log` 的失敗</summary>

`subprocess.run` 沒有設定 `check=True`，且回傳的 `proc.returncode` 未被檢查。如果 `git log` 因為 repo 損壞、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式會回傳空 list，導致後續流程誤以為沒有 commit 而正常結束（回傳 0）。建議加上 `check=True` 或檢查 `proc.returncode`，並在失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:74</code> `group` 函式對 commit subject 的解析可能誤分類</summary>

`group` 函式以 `subject.split(":", 1)[0]` 作為分類依據，但若 commit subject 不含冒號，`prefix` 會是整個 subject，可能不屬於任何已知分類而被歸為 `other`。這可能導致分類不準確，但影響有限。建議先檢查是否包含冒號，或使用更嚴謹的解析方式。

**判斷依據**：diff 中 `group` 函式的解析邏輯未處理無冒號的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:37</code> `max_items` 未限制負數或過大值</summary>

`max_items` 直接將環境變數轉為整數，未檢查是否為負數或過大。若 `NOTES_MAX` 設為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，導致輸出錯誤；若設為極大值，可能造成記憶體問題。建議加上範圍檢查（例如 1 到某個上限）。

**判斷依據**：diff 中 `max_items` 函式只處理 ValueError，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能造成 SSRF</summary>

`post` 函式直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，未驗證其 scheme 是否為 http/https。若攻擊者能控制該環境變數（例如在 CI 環境中），可能誘使腳本向內部服務發送請求。建議檢查 URL 的 scheme 並限制為 http/https。

**判斷依據**：diff 中 `post` 函式未對 URL 進行任何驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3917 (cache hit 3840) ｜ completion tokens 1082 ｜ PR #14</sub>