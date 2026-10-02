<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理兩個 tag 之間的 commit，並將結果貼到團隊頻道的 webhook。整體結構清楚，但存在幾個值得注意的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的執行結果，失敗時會靜默產生空列表，導致後續流程誤判；其次是 `prev` 的取得方式在 tag 是第一個版本時會拋出 `IndexError`；另外 `max_items()` 對負數或零的處理可能造成非預期行為。建議先修正這些正確性問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能靜默產生空列表 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | `max_items()` 未處理負數或零，可能導致非預期行為 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:96` | `post` 函式只捕捉 `URLError`，其他例外可能導致程式崩潰 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能靜默產生空列表</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 git 本身出錯而失敗，`proc.stdout` 會是空字串，函式會回傳空列表，導致 `main` 誤以為「沒有新 commit」而回傳 0，實際上根本沒有成功取得任何資料。建議加上 `check=True` 或明確檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

**判斷依據**：diff 第 55-58 行，`subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，未檢查 `returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，`prev = tags[tags.index(tag) - 1]` 會拋出 IndexError</summary>

如果使用者指定的 tag 是 `list_tags` 回傳列表中的第一個元素（例如 repo 只有一個 tag，或該 tag 是最早的版本），`tags.index(tag)` 會是 0，`tags[0 - 1]` 會拋出 `IndexError`，程式直接崩潰。建議在取 `prev` 前檢查 `tags.index(tag) == 0`，並給出明確錯誤訊息或改用其他方式處理（例如從 repo 初始 commit 開始）。

**判斷依據**：diff 第 94 行，直接對 `tags.index(tag) - 1` 取值，未處理 index 為 0 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> `max_items()` 未處理負數或零，可能導致非預期行為</summary>

`max_items()` 將環境變數 `NOTES_MAX` 轉為整數後直接回傳，沒有檢查是否為正數。如果使用者設定 `NOTES_MAX=-1` 或 `NOTES_MAX=0`，`commits[: max_items()]` 會分別取得空列表或全部 commit（因為 `commits[:-1]` 會排除最後一個，`commits[:0]` 會是空列表），與預期的「限制數量」不符。建議在轉換後檢查數值是否大於 0，否則回傳預設值或拋出錯誤。

**判斷依據**：diff 第 39-43 行，`int(raw)` 成功後直接回傳，未驗證數值範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:96</code> `post` 函式只捕捉 `URLError`，其他例外可能導致程式崩潰</summary>

`urllib.request.urlopen` 除了 `URLError` 之外，還可能拋出 `ValueError`（例如 URL 格式錯誤）、`TimeoutError`（在 Python 3.10+ 中 timeout 會拋出 `TimeoutError`，它是 `URLError` 的子類別，但某些情況可能不是）或 `http.client.HTTPException`。目前只捕捉 `URLError`，其他例外會讓程式直接崩潰。建議捕捉更廣泛的例外（例如 `Exception`）或至少加上 `except Exception as e` 並記錄錯誤。

**判斷依據**：diff 第 79-81 行，只捕捉 `URLError`，未涵蓋所有可能的例外。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3631 (cache hit 3584) ｜ completion tokens 1317 ｜ PR #14</sub>