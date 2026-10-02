<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱。主要風險在於 smtplib 建構子參數傳遞方式：當 local_hostname 為空字串時，會傳入空字串而非 None，可能導致 SMTP 連線失敗。此外，assert 敘述在最佳化模式下會被移除，不應作為執行時期檢查。建議修正參數傳遞邏輯並移除 assert。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | local_hostname 參數可能傳入空字串而非 None | 0.85 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert 不應作為執行時期檢查 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> local_hostname 參數可能傳入空字串而非 None</summary>

在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

**判斷依據**：diff 中新增的程式碼使用 `local_host or None`，但 `local_host` 來自 `dify_config.SMTP_LOCAL_HOSTNAME or ""`，若設定為空字串，則 `local_host` 為空字串，`local_host or None` 會得到 `None`，因此實際上不會傳入空字串。但若設定值為空白字元（如空格），則 `local_host` 為空白字串，`local_host or None` 會得到空白字串，可能導致問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert 不應作為執行時期檢查</summary>

`assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

**判斷依據**：diff 中新增 `assert smtp is not None`，但 smtp 剛被賦值，不可能為 None，且 assert 可能被最佳化移除。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4936 (cache hit 1536) ｜ completion tokens 718 ｜ PR #6</sub>