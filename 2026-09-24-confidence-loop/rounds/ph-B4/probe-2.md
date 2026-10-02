<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查子程序失敗，可能導致後續索引錯誤；`list_tags` 在 tag 不存在時會拋出未處理的例外；`max_items` 對負數或零值未做驗證；以及 webhook URL 未驗證 scheme 可能造成 SSRF。建議先修正這些正確性與安全性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 子程序失敗未檢查，可能導致後續 IndexError | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:50` | list_tags 未處理子程序失敗，可能拋出未捕捉例外 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:36` | max_items 未驗證負數或零值 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能造成 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 子程序失敗未檢查，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 `git log` 因 repo 路徑無效、tag 不存在或權限問題失敗，`proc.stdout` 可能為空字串，後續 `commits[0][0]` 會拋出 `IndexError`。建議加上 `check=True` 或檢查 `proc.returncode` 並處理錯誤。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，而 `main` 中 `latest = commits[0][0]` 假設 `commits` 非空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:50</code> list_tags 未處理子程序失敗，可能拋出未捕捉例外</summary>

`list_tags` 使用 `check=True`，若 `git tag` 失敗（例如 repo 路徑不存在）會拋出 `subprocess.CalledProcessError`，但 `main` 中未捕捉，導致程式直接崩潰。建議在 `main` 中捕捉此例外並回傳錯誤碼，或改用 `check=False` 並檢查回傳值。

**判斷依據**：diff 中 `list_tags` 使用 `check=True`，而 `main` 呼叫 `list_tags(repo)` 時未包在 try/except 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:36</code> max_items 未驗證負數或零值</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會產生空列表或意外結果。建議驗證值必須大於 0，否則回退到預設值。

**判斷依據**：diff 中 `max_items` 僅處理 ValueError，未檢查數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能造成 SSRF</summary>

`post` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，未驗證 scheme 是否為 http/https。若攻擊者能控制環境變數，可能誘使程式向內部服務發送請求（SSRF）。建議檢查 URL 的 scheme 並限制為 http/https。

**判斷依據**：diff 中 `post` 未對 `url` 進行 scheme 驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1108 ｜ PR #14</sub>