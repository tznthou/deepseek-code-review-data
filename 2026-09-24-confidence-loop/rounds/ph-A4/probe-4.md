<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一支 release notes 產生器，從 git log 整理 commit 並透過 webhook 發布。主要風險在於：`commits_between` 未檢查 `git log` 的失敗（可能導致後續 IndexError）、`max_items` 未處理負數或零、`post` 未驗證 URL scheme、以及 `load_config` 未限制設定檔大小。建議先修正 `commits_between` 的錯誤處理與 `max_items` 的輸入驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | `git log` 失敗時未檢查回傳碼，可能導致後續 IndexError | 0.80 |
| ⚠️ | Major | `sandbox/release_notes.py:34` | `max_items` 未處理負數或零，可能導致空公告或錯誤 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:91` | `post` 未驗證 URL scheme，可能誤用非 HTTP(S) 協定 | 0.60 |
| 🔸 | Minor | `sandbox/release_notes.py:30` | `load_config` 未限制設定檔大小，可能讀入超大檔案 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> `git log` 失敗時未檢查回傳碼，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有 `check=True`，若 `git log` 因 repo 損毀或權限問題失敗，`proc.stdout` 會是空字串，`commits` 會是空 list。接著在 `main` 中 `latest = commits[0][0]` 會拋出 `IndexError`，程式直接 crash。建議加上 `check=True` 或檢查 `proc.returncode` 並回報錯誤。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且 `main` 中 `latest = commits[0][0]` 假設 `commits` 非空。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:34</code> `max_items` 未處理負數或零，可能導致空公告或錯誤</summary>

`max_items` 將環境變數 `NOTES_MAX` 轉為整數，但未檢查是否為正數。若設為負數，`commits[: max_items()]` 會變成 `commits[:-1]`（少最後一筆）；若設為 0，會得到空 list，導致 `latest = commits[0][0]` 拋出 IndexError。建議驗證數值為正整數，否則回退預設值。

**判斷依據**：diff 中 `max_items` 只處理 ValueError，未處理負數或零。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:91</code> `post` 未驗證 URL scheme，可能誤用非 HTTP(S) 協定</summary>

`post` 直接將 `url` 傳給 `urllib.request.Request`，若環境變數 `NOTES_WEBHOOK` 設為 `file://` 或 `ftp://` 等非 HTTP(S) scheme，程式會嘗試以該協定連線，可能造成非預期行為或安全風險。建議檢查 `urlparse(url).scheme` 是否為 `http` 或 `https`。

**判斷依據**：diff 中 `post` 未對 URL scheme 做任何驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:30</code> `load_config` 未限制設定檔大小，可能讀入超大檔案</summary>

`load_config` 直接 `json.load(fh)`，若 `.release-notes.json` 被意外放入超大檔案，可能耗盡記憶體。建議在讀取前檢查檔案大小或限制讀取位元組數。

**判斷依據**：diff 中 `load_config` 未對檔案大小做任何限制。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1107 ｜ PR #14</sub>