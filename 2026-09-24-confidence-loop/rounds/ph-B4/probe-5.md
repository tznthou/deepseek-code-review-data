<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查子程序失敗，可能導致後續索引錯誤；`list_tags` 在找不到符合條件的 tag 時會拋出未處理的例外；`max_items` 對負數或過大值無防護；webhook URL 未驗證 scheme，可能被用於 SSRF。建議先修正這些正確性與安全性問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | 子程序失敗未檢查，可能導致後續 IndexError | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:50` | list_tags 在無符合 tag 時拋出未處理例外 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:35` | max_items 未限制負數或過大值 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> 子程序失敗未檢查，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑無效、權限不足），`proc.stdout` 可能為空字串，但函式仍回傳空 list，後續 `main` 中 `commits[0][0]` 會拋出 `IndexError`。建議加上 `check=True` 或檢查 `returncode`，並在失敗時記錄錯誤並回傳非零狀態。

**判斷依據**：diff 中 `commits_between` 函式未檢查 `proc.returncode`，且 `main` 中 `latest = commits[0][0]` 假設 `commits` 非空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:50</code> list_tags 在無符合 tag 時拋出未處理例外</summary>

`list_tags` 使用 `subprocess.run` 且設定 `check=True`，若 repo 中沒有符合 `v*` 的 tag，`git tag --list v*` 會回傳空輸出且 exit code 0，但若 git 指令本身失敗（例如 repo 不存在），會拋出 `CalledProcessError`，而 `main` 未捕捉，導致程式直接崩潰。建議在 `main` 中捕捉此例外並回傳錯誤訊息。

**判斷依據**：diff 中 `list_tags` 使用 `check=True`，但 `main` 呼叫 `list_tags` 時未包在 try/except 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:35</code> max_items 未限制負數或過大值</summary>

`max_items` 從環境變數 `NOTES_MAX` 讀取整數，但未檢查範圍。若設定為負數，`commits[: max_items()]` 會回傳空 list，導致後續 `commits[0][0]` 出錯；若設定為極大值，可能造成記憶體壓力。建議限制在合理範圍（例如 1 到 1000）。

**判斷依據**：diff 中 `max_items` 僅轉換為 int，未做範圍檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，未檢查 scheme 是否為 http/https。若攻擊者能控制環境變數，可指定 `file://` 或 `gopher://` 等 scheme，造成 SSRF 或資訊洩漏。建議驗證 URL 的 scheme 必須是 http 或 https。

**判斷依據**：diff 中 `post` 未對 `url` 做任何驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1182 ｜ PR #14</sub>