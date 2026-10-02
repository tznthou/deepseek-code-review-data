<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 git 指令的失敗回傳碼，可能導致後續在空列表上取 `commits[0]` 而崩潰；`max_items` 對負數或零沒有下限保護，可能造成切片行為異常；webhook URL 未驗證 scheme，可能被用於 SSRF。建議先修正這三個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，後續會因空列表而崩潰 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:45` | NOTES_MAX 可設為負數或零，導致切片行為異常 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，後續會因空列表而崩潰</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空列表。接著在 `main` 中 `commits[0][0]` 會拋出 `IndexError`，程式直接崩潰。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並回報錯誤。

**判斷依據**：diff 中 `commits_between` 的 `subprocess.run` 沒有 `check=True`，且回傳值未檢查；`main` 中 `latest = commits[0][0]` 直接對空列表取索引。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:45</code> NOTES_MAX 可設為負數或零，導致切片行為異常</summary>

`max_items` 只驗證 `NOTES_MAX` 是否為整數，沒有檢查是否大於 0。若設為負數，`commits[: max_items()]` 會變成 `commits[:-n]`，意外排除最後 n 筆 commit；若設為 0，則會回傳空列表，但 `main` 中仍會嘗試取 `commits[0]` 而崩潰。建議在轉換後檢查 `value > 0`，否則回退到預設值。

**判斷依據**：diff 中 `max_items` 只處理 `ValueError`，未檢查數值範圍；`main` 中 `commits[: max_items()]` 直接使用該值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.urlopen`，沒有檢查 URL 的 scheme。攻擊者若能控制環境變數（例如在 CI 中注入），可指定 `file:///etc/passwd` 或 `http://169.254.169.254/...` 等 URL，導致任意檔案讀取或內部網路掃描。建議限制 scheme 為 `https`（或至少 `http`/`https`），並考慮阻擋內網位址。

**判斷依據**：diff 中 `post` 函式直接使用傳入的 `url`，未做任何驗證；`main` 中 `url` 來自環境變數 `NOTES_WEBHOOK`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1036 ｜ PR #14</sub>