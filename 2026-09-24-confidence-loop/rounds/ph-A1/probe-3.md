<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並透過 webhook 發佈。主要風險在於錯誤處理不完整（git 指令失敗時未檢查、webhook 回應未讀取）、輸入驗證不足（NOTES_MAX 可為負數、tag 清單可能為空），以及安全疑慮（webhook URL 未驗證 scheme）。建議先修正這些問題再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:50` | git tag 指令失敗時未檢查回傳碼 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 指令失敗時未檢查回傳碼 | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:94` | webhook 回應未讀取可能導致連線無法重用 | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:36` | NOTES_MAX 可設為負數導致切片錯誤 | 0.75 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | tag 清單可能為空導致 IndexError | 0.70 |
| ⚠️ | Major | `sandbox/release_notes.py:109` | webhook URL 未驗證 scheme 可能導致 SSRF | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:104` | 設定檔載入可能拋出未處理的例外 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:50</code> git tag 指令失敗時未檢查回傳碼</summary>

`list_tags` 使用 `subprocess.run` 但未設定 `check=True`，也未檢查 `returncode`。若 repo 路徑無效或 git 執行失敗，程式會繼續執行並可能產生錯誤結果。建議加上 `check=True` 或明確檢查 `returncode`。

**判斷依據**：diff 中 `list_tags` 的 subprocess.run 呼叫沒有 check=True，且未檢查 returncode。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 指令失敗時未檢查回傳碼</summary>

`commits_between` 使用 `subprocess.run` 但未設定 `check=True`，也未檢查 `returncode`。若 git 執行失敗，`proc.stdout` 可能為空，導致後續處理錯誤。建議加上 `check=True` 或明確檢查 `returncode`。

**判斷依據**：diff 中 `commits_between` 的 subprocess.run 呼叫沒有 check=True，且未檢查 returncode。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:94</code> webhook 回應未讀取可能導致連線無法重用</summary>

`post` 函式中，`urlopen` 的回應物件未讀取內容。若伺服器回傳大量資料，可能導致連線無法重用或資源洩漏。建議讀取回應內容（例如 `resp.read()`）或使用 `contextlib.closing`。

**判斷依據**：diff 中 `post` 函式的 `urlopen` 回應未讀取。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:36</code> NOTES_MAX 可設為負數導致切片錯誤</summary>

`max_items` 直接將環境變數轉為整數，未驗證是否為正數。若設定為負數，`commits[: max_items()]` 會產生錯誤切片（例如 `[:-1]` 會排除最後一個元素）。建議檢查數值範圍，例如 `if n < 1: return DEFAULT_MAX`。

**判斷依據**：diff 中 `max_items` 未檢查轉換後的整數是否為正數。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> tag 清單可能為空導致 IndexError</summary>

`main` 中 `prev = tags[tags.index(tag) - 1]` 假設 `tags` 至少有一個元素。若 `list_tags` 回傳空清單（例如 repo 中沒有符合的 tag），`tags.index(tag)` 會拋出 `ValueError`，但若 `tag` 存在於空清單中不可能，因此實際上會先觸發 `ValueError`。但若 `tags` 只有一個元素且 `tag` 是第一個，`tags.index(tag) - 1` 會是 -1，導致 `prev` 為最後一個元素，可能不是預期的前一個 tag。建議檢查 `tags.index(tag) > 0`。

**判斷依據**：diff 中 `main` 函式直接使用 `tags.index(tag) - 1`，未檢查索引是否大於 0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:109</code> webhook URL 未驗證 scheme 可能導致 SSRF</summary>

`NOTES_WEBHOOK` 環境變數直接傳給 `urllib.request.Request`，未驗證 scheme。若攻擊者控制環境變數，可指定 `file://` 等 scheme 讀取本機檔案。建議驗證 URL 的 scheme 為 `http` 或 `https`。

**判斷依據**：diff 中 `main` 函式直接使用環境變數作為 URL，未驗證 scheme。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:104</code> 設定檔載入可能拋出未處理的例外</summary>

`load_config` 只處理 `FileNotFoundError` 和 `json.JSONDecodeError`，但若檔案權限不足或讀取時發生其他 I/O 錯誤，程式會崩潰。建議捕捉 `OSError` 或更廣泛的例外並記錄。

**判斷依據**：diff 中 `load_config` 的例外處理僅限於 `FileNotFoundError` 和 `json.JSONDecodeError`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1751 ｜ PR #14</sub>