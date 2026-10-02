<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，會從 git log 整理兩個 tag 之間的 commit，並將結果貼到團隊頻道的 webhook。整體結構清楚，但存在幾個需要修正的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的退出碼，當 repo 路徑錯誤或 tag 不存在時會靜默失敗，導致後續程式碼在空資料上執行並可能誤報成功。此外，`max_items()` 對負數或零的 NOTES_MAX 沒有防護，會造成切片結果為空或全部納入，與預期不符。webhook URL 未驗證 scheme，可能被用於 SSRF。最後，`load_config` 對 JSON 型別沒有驗證，若設定檔內容不是物件，後續 `.get()` 會拋出 AttributeError。建議優先修正 `commits_between` 的錯誤處理，並對 NOTES_MAX 加上下限檢查。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查退出碼，可能導致靜默失敗 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:41` | NOTES_MAX 未限制下限，負數或零會造成非預期行為 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:109` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | 設定檔 JSON 型別未驗證，可能導致 AttributeError | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查退出碼，可能導致靜默失敗</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `repo` 路徑不存在、不是 git repo，或 `prev`/`tag` 不存在，`git log` 會以非零退出碼結束，但程式會繼續執行，將 `proc.stdout`（可能是空字串或錯誤訊息）當成正常輸出處理。這會導致後續 `group` 收到空列表或無法解析的內容，最終可能發送錯誤的 release notes 或誤報成功。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並拋出例外或記錄錯誤。

**判斷依據**：diff 中 `commits_between` 函式內，`subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `proc.returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:41</code> NOTES_MAX 未限制下限，負數或零會造成非預期行為</summary>

`max_items()` 將環境變數 NOTES_MAX 轉為整數後直接回傳，沒有檢查是否為正數。若使用者設定 NOTES_MAX=0 或負數，`commits[: max_items()]` 會得到空列表或全部元素（負索引切片），導致 release notes 內容不正確。

建議：在轉換後檢查數值是否大於 0，否則回傳預設值或記錄警告。

**判斷依據**：diff 中 `max_items()` 函式只處理了 ValueError，未對轉換後的整數做範圍檢查。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:109</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 函式直接使用環境變數 NOTES_WEBHOOK 作為 URL，未檢查其 scheme 是否為 http/https。攻擊者若能控制環境變數（例如透過 CI 設定），可將 URL 設為 `file:///etc/passwd` 或內網位址，造成資訊洩漏或 SSRF。

建議：在 `main` 中取得 URL 後，檢查是否以 `http://` 或 `https://` 開頭，否則拒絕執行。

**判斷依據**：diff 中 `main` 函式僅檢查 NOTES_WEBHOOK 是否存在，未驗證其 scheme。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> 設定檔 JSON 型別未驗證，可能導致 AttributeError</summary>

`load_config` 回傳 `json.load` 的結果，但未檢查其是否為 dict。若 `.release-notes.json` 內容是陣列或字串，後續 `cfg.get('title', ...)` 會拋出 AttributeError，導致程式崩潰。

建議：在 `load_config` 中檢查回傳值是否為 dict，若不是則拋出錯誤或回傳空 dict。

**判斷依據**：diff 中 `load_config` 直接回傳 `json.load` 的結果，未做型別檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1302 ｜ PR #14</sub>