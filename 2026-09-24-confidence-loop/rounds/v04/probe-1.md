<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並透過 webhook 發佈。整體結構清楚，但存在幾個值得注意的問題：最嚴重的是 `commits_between` 沒有檢查 `git log` 的退出碼，可能導致在 tag 不存在時仍回報成功；其次是 `max_items()` 對負數或非整數輸入的處理不一致；另外 `post()` 的錯誤處理可能洩漏 webhook URL。建議先修正 `commits_between` 的錯誤處理，再考慮其他項目。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查退出碼，可能導致誤報成功 | 0.90 |
| 🔸 | Minor | `sandbox/release_notes.py:35` | `max_items()` 未處理負數或非整數輸入，可能導致意外行為 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:97` | 錯誤訊息可能洩漏 webhook URL | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查退出碼，可能導致誤報成功</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `prev` 或 `tag` 不存在，`git log` 會回傳非零退出碼並在 stderr 輸出錯誤，但函式仍會回傳空列表，讓主流程誤以為沒有 commit 而回報成功。建議加上 `check=True` 或明確檢查 `proc.returncode`，並在失敗時拋出例外或回傳錯誤。

**判斷依據**：diff 中 `commits_between` 函式沒有處理 `subprocess.run` 的錯誤，且 `main` 中呼叫後直接檢查 `if not commits`，未考慮 git 失敗的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:35</code> `max_items()` 未處理負數或非整數輸入，可能導致意外行為</summary>

`max_items()` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為負數。若設為負數，`commits[: max_items()]` 會切片到倒數第 N 個元素，可能遺漏大部分 commit。建議驗證數值為正整數，否則回退到預設值。

**判斷依據**：diff 中 `max_items()` 只處理了 `ValueError`，未檢查轉換後的數值是否合理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:97</code> 錯誤訊息可能洩漏 webhook URL</summary>

`post()` 在 `URLError` 的錯誤訊息中直接印出 `url`，而 webhook URL 通常包含 secret token，可能意外洩漏到 log 中。建議在錯誤訊息中隱藏 URL 或僅顯示 host。

**判斷依據**：diff 中 `post()` 的錯誤處理直接將 `url` 寫入 log。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3751 (cache hit 3712) ｜ completion tokens 874 ｜ PR #14</sub>