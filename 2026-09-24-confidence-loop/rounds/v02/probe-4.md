<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了一個 release notes 產生器，會從 git 歷史整理 commit 並貼到 webhook。主要風險在於：`commits_between` 未檢查 `git log` 的失敗、`prev` 的取得在只有一個 tag 時會出錯、`max_items` 未限制負數、webhook URL 未驗證 scheme、以及 `group` 對 commit subject 的解析可能誤分類。最該先修的是 `commits_between` 的錯誤處理與 `prev` 的邊界條件。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `sandbox/release_notes.py:58` | git log 失敗時未檢查回傳碼，可能回報成功但沒有內容 | 0.90 |
| ⚠️ | Major | `sandbox/release_notes.py:118` | 只有一個符合條件的 tag 時，`prev` 會取到 `tags[-1]` 造成錯誤 | 0.85 |
| 🔸 | Minor | `sandbox/release_notes.py:43` | `max_items` 未限制負數，可能導致切片行為異常 | 0.70 |
| 🔸 | Minor | `sandbox/release_notes.py:94` | webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期協定 | 0.60 |
| 🔸 | Minor | `sandbox/release_notes.py:74` | commit subject 的 prefix 解析可能誤分類 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:58</code> git log 失敗時未檢查回傳碼，可能回報成功但沒有內容</summary>

`commits_between` 呼叫 `subprocess.run` 時沒有 `check=True`，且未檢查 `proc.returncode`。如果 `git log` 因為 repo 損毀、權限不足或 `prev`/`tag` 不存在而失敗，`proc.stdout` 會是空字串，函式回傳空 list，`main` 會印出「之間沒有新 commit」並回傳 0，讓使用者誤以為成功。

建議：加上 `check=True`，或明確檢查 `proc.returncode != 0` 並拋出例外或回傳錯誤。

**判斷依據**：diff 第 51-54 行顯示 `subprocess.run` 沒有 `check=True`，且後續直接使用 `proc.stdout`，沒有檢查 `returncode`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>sandbox/release_notes.py:118</code> 只有一個符合條件的 tag 時，`prev` 會取到 `tags[-1]` 造成錯誤</summary>

`prev = tags[tags.index(tag) - 1]` 在 `tag` 是 `tags` 的第一個元素時，會取到 `tags[-1]`（最後一個 tag），而不是更早的 commit。這會讓 `git log prev..tag` 的範圍完全錯誤，可能包含大量不相關的 commit 或根本沒有 commit。

建議：檢查 `tags.index(tag) == 0` 的情況，並決定要如何處理（例如從 repo 的第一個 commit 開始，或直接報錯）。

**判斷依據**：diff 第 105 行，`tags.index(tag)` 可能為 0，此時 `-1` 會指向最後一個元素。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:43</code> `max_items` 未限制負數，可能導致切片行為異常</summary>

`max_items` 直接將環境變數轉成整數，沒有檢查是否為負數。若 `NOTES_MAX=-1`，`commits[: -1]` 會回傳除了最後一個以外的所有 commit，而不是全部或報錯。這可能不是使用者預期的行為。

建議：檢查數值是否為正整數，否則使用預設值或報錯。

**判斷依據**：diff 第 39 行，`int(raw)` 沒有驗證範圍。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:94</code> webhook URL 未驗證 scheme，可能被用於 SSRF 或非預期協定</summary>

`post` 直接使用 `urllib.request.urlopen` 開啟 `url`，沒有檢查 scheme 是否為 `http` 或 `https`。如果環境變數被設為 `file:///etc/passwd` 或 `ftp://...`，程式會嘗試讀取或連線到非預期的資源。雖然環境變數通常由部署者控制，但這仍是一個潛在的安全風險。

建議：在 `main` 中驗證 `url` 的 scheme 為 `http` 或 `https`。

**判斷依據**：diff 第 93 行，`urlopen` 接受任意 scheme。

</details>

<details><summary>🔸 <b>Minor</b> — <code>sandbox/release_notes.py:74</code> commit subject 的 prefix 解析可能誤分類</summary>

`group` 使用 `subject.split(":", 1)[0]` 作為分類依據，但若 commit subject 本身包含冒號（例如 `fix: handle: edge case`），prefix 會是 `fix`，仍能正確分類；但若 subject 開頭不是 `feat:` 或 `fix:`，就會被歸為 `other`。這可能不是問題，但若團隊使用其他 prefix（如 `docs:`、`chore:`），這些 commit 會被歸為「其他」，可能不符合預期。

建議：確認團隊的 commit 慣例，或考慮更彈性的分類方式。

**判斷依據**：diff 第 61 行，只處理 `feat` 和 `fix`，其他都歸為 `other`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3787 (cache hit 3712) ｜ completion tokens 1434 ｜ PR #14</sub>