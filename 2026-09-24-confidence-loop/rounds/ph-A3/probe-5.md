<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

這個 PR 新增了一個 release notes 產生器，從 git log 整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 git 指令的失敗（可能導致後續索引錯誤）、`prev` 的計算在 tag 是第一個版本時會出錯、`NOTES_MAX` 未限制上限可能造成記憶體問題、以及 webhook URL 未驗證 scheme 可能被用於 SSRF。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能導致後續 IndexError | 0.95 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 當 tag 是第一個版本時，prev 會取到錯誤的 tag | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:91` | webhook URL 未驗證 scheme，可能被用於 SSRF | 0.85 |
| ⚠️ | Major | `sandbox/release_notes.py:36` | NOTES_MAX 未限制上限，可能導致記憶體耗盡 | 0.80 |
| 🔸 | Minor | `sandbox/release_notes.py:64` | git log 輸出解析脆弱，可能誤判 commit subject | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能導致後續 IndexError</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有設定 `check=True`，也沒有檢查 `proc.returncode`。如果 `git log` 因為 repo 路徑錯誤、權限不足或 tag 不存在而失敗，`proc.stdout` 會是空字串，`commits` 會是空 list。接著在 `main` 中 `latest = commits[0][0]` 會拋出 `IndexError`，程式直接 crash。

建議：加上 `check=True`，或在呼叫後檢查 `proc.returncode != 0` 並記錄錯誤後回傳空 list 或拋出例外。

**判斷依據**：diff 中 `commits_between` 函式沒有 `check=True`，且 `main` 中直接使用 `commits[0][0]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 當 tag 是第一個版本時，prev 會取到錯誤的 tag</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，會取到 `tags[-1]`（最後一個 tag），而不是沒有前一個版本。這會導致 `commits_between` 使用錯誤的範圍，產生不正確的 release notes。

建議：檢查 `tags.index(tag) == 0` 的情況，並處理沒有前一個 tag 的邏輯（例如從 repo 初始 commit 開始）。

**判斷依據**：diff 中 `main` 函式直接計算 `prev`，沒有檢查 index 是否為 0。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:91</code> webhook URL 未驗證 scheme，可能被用於 SSRF</summary>

`post` 函式直接使用 `urllib.request.urlopen` 開啟使用者提供的 URL（來自環境變數 `NOTES_WEBHOOK`）。如果攻擊者能控制環境變數（例如在 CI 中），可以指定 `file://` 或 `ftp://` 等 scheme，讀取本機檔案或進行其他攻擊。

建議：驗證 URL 的 scheme 必須是 `http` 或 `https`，並考慮使用 `urllib.parse.urlparse` 檢查。

**判斷依據**：diff 中 `post` 函式沒有對 URL 做任何驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:36</code> NOTES_MAX 未限制上限，可能導致記憶體耗盡</summary>

`max_items` 從環境變數讀取整數，但沒有檢查上限。如果使用者設定一個極大的值（例如 `NOTES_MAX=999999999`），`commits[: max_items()]` 會嘗試建立一個巨大的 list，可能耗盡記憶體。

建議：設定一個合理的上限（例如 1000），並在超過時記錄警告或直接截斷。

**判斷依據**：diff 中 `max_items` 函式沒有對回傳值做上限檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:64</code> git log 輸出解析脆弱，可能誤判 commit subject</summary>

`commits_between` 使用 `line.split(" ", 1)` 來分割 sha 和 subject，但 git log 的 `%h %s` 格式中，subject 可能包含多個空格，這部分沒問題。然而，如果 commit subject 本身以空格開頭（不太可能），或者 git 輸出格式因設定而改變，解析就會出錯。另外，`if " " not in line: continue` 會跳過沒有空格的列，但 git log 的輸出通常都有空格，所以這個檢查可能永遠不會觸發。

建議：使用更嚴謹的解析方式，例如用 `--format=%h%x09%s` 並以 tab 分割。

**判斷依據**：diff 中 `commits_between` 的解析邏輯。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1464 ｜ PR #14</sub>