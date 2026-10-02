<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，從 git log 收集 commit 並發送到 webhook。整體結構清晰，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 git 指令的失敗，可能導致後續程式碼在錯誤的資料上執行；另外 `max_items` 沒有處理負數或零，可能造成輸出異常；`post` 函式沒有驗證 URL scheme，可能被用於 SSRF。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 失敗時未檢查，可能導致錯誤的 release notes | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:31` | NOTES_MAX 未處理負數或零，可能導致輸出異常 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.75 |
| 🔸 | Minor | `sandbox/release_notes.py:94` | webhook 回應狀態碼判斷可能不正確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查，可能導致錯誤的 release notes</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查回傳碼。如果 git 指令失敗（例如 repo 路徑錯誤、權限不足、或 git 本身出錯），`proc.stdout` 可能是空字串或錯誤訊息，但函式仍會回傳空列表或解析錯誤的內容。這會讓後續流程在錯誤的基礎上繼續執行，產生不正確的 release notes 或誤導使用者。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式內的 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:31</code> NOTES_MAX 未處理負數或零，可能導致輸出異常</summary>

`max_items` 從環境變數讀取整數，但沒有驗證範圍。如果設定為負數或零，`commits[: max_items()]` 會產生空列表或錯誤的切片，導致 release notes 內容不完整或程式出錯。

建議：檢查數值是否為正整數，否則使用預設值或回報錯誤。

**判斷依據**：diff 中 `max_items` 函式只處理了 `ValueError`，沒有檢查轉換後的數值是否合理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 函式直接使用環境變數 `NOTES_WEBHOOK` 作為 URL，沒有驗證 scheme 是否為 http 或 https。攻擊者若能控制環境變數，可能指定 `file://` 或 `gopher://` 等 scheme，導致任意檔案讀取或內網請求。

建議：檢查 URL 的 scheme 是否為 `http` 或 `https`，否則拒絕執行。

**判斷依據**：diff 中 `post` 函式直接使用 `url` 參數，沒有進行 scheme 驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:94</code> webhook 回應狀態碼判斷可能不正確</summary>

`post` 函式檢查 `200 <= resp.status < 300` 來判斷成功，但有些 webhook 服務可能回傳 204 No Content 或其他 2xx 狀態碼，這部分沒問題。然而，如果服務回傳 3xx 重定向，`urllib` 會自動跟隨，最終狀態碼可能是 2xx，但這可能不是預期的行為。另外，如果服務回傳 4xx 或 5xx，函式會回傳 False，但沒有記錄回應內容，不利於除錯。

建議：考慮記錄回應狀態碼和內容，以便診斷問題。

**判斷依據**：diff 中 `post` 函式只回傳布林值，沒有記錄失敗時的詳細資訊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3917 (cache hit 3840) ｜ completion tokens 1215 ｜ PR #14</sub>