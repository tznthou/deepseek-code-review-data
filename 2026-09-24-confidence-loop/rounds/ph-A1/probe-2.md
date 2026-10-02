<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並透過 webhook 發佈。主要風險在於 `commits_between` 未檢查 git 指令失敗，可能導致後續處理空輸出或錯誤資料；`max_items` 未限制 NOTES_MAX 為正整數，負值或零會造成切片異常；`post` 未驗證 webhook URL 的 scheme，可能被用於 SSRF。建議優先修正這些問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致後續處理空輸出 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:43` | NOTES_MAX 未限制為正整數，負值或零會造成切片異常 | 0.75 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:94` | webhook 回應狀態碼檢查可能不完整 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致後續處理空輸出</summary>

`commits_between` 呼叫 `subprocess.run` 時未設定 `check=True`，也未檢查 `proc.returncode`。若 git 指令失敗（例如 repo 路徑錯誤、權限不足），`proc.stdout` 可能為空字串，函式會回傳空 list，後續 `main` 會印出「沒有新 commit」並回傳 0，但實際上並未成功取得 commit 清單。建議加上 `check=True` 或檢查 `proc.returncode`，失敗時拋出例外或回傳錯誤碼。

**判斷依據**：diff 中 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:43</code> NOTES_MAX 未限制為正整數，負值或零會造成切片異常</summary>

`max_items` 將環境變數 NOTES_MAX 轉為整數後直接回傳，未檢查是否為正數。若設定為負數或零，`commits[: max_items()]` 會產生空 list 或錯誤切片（負數切片會從尾端取，可能導致非預期行為）。建議驗證數值必須大於 0，否則使用預設值。

**判斷依據**：diff 中 `int(raw)` 成功後直接回傳，沒有檢查是否為正數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 直接使用環境變數 NOTES_WEBHOOK 作為 URL，未檢查其 scheme 是否為 http/https。攻擊者若控制環境變數，可指定 `file://` 或 `gopher://` 等 scheme，導致任意檔案讀取或內網請求。建議驗證 URL 的 scheme 必須是 http 或 https。

**判斷依據**：diff 中 `url` 來自環境變數，未經 scheme 驗證即傳入 `urllib.request.Request`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:94</code> webhook 回應狀態碼檢查可能不完整</summary>

`post` 檢查 `200 <= resp.status < 300`，但某些 webhook 服務可能回傳 204 No Content 或其他 2xx 狀態碼，此處已涵蓋。然而，若服務回傳 3xx 重定向，`urllib` 預設會自動跟隨，可能導致非預期行為。建議明確處理重定向或停用自動跟隨。

**判斷依據**：diff 中未處理 3xx 狀態碼，且 `urlopen` 預設會跟隨重定向。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1126 ｜ PR #14</sub>