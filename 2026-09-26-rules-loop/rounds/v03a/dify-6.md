<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並更新相關測試與環境變數範例。主要風險在於 smtplib 建構子參數傳遞方式：當 local_hostname 為空字串時，程式碼傳入 None 而非省略參數，可能導致與預設行為不一致；此外，opportunistic TLS 模式下 ehlo 呼叫未傳入 local_hostname，可能使覆寫失效。建議修正參數傳遞邏輯並補充測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP 建構子 local_hostname 參數傳遞可能導致非預期行為 | 0.80 |
| ⚠️ | Major | `api/libs/smtp.py:30` | Opportunistic TLS 模式下 ehlo 未使用 local_hostname | 0.70 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 為多餘且可能誤導 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP 建構子 local_hostname 參數傳遞可能導致非預期行為</summary>

當 SMTP_LOCAL_HOSTNAME 未設定時，local_host 為空字串，程式碼傳入 `local_hostname=local_host or None`，即傳入 None。然而，smtplib.SMTP 的 local_hostname 參數預設為 None，但若明確傳入 None，可能與省略參數的行為不同（例如某些實作會將 None 視為 'localhost' 或觸發 socket.getfqdn() 以外的邏輯）。建議改為僅在 local_host 非空時才傳入該參數，例如使用條件式建構或 **kwargs。

**判斷依據**：diff 中新增的建構子呼叫明確傳入 local_hostname=local_host or None，而原本的呼叫未傳入該參數，可能改變預設行為。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:30</code> Opportunistic TLS 模式下 ehlo 未使用 local_hostname</summary>

在 opportunistic TLS 分支中，`smtp.ehlo(local_host)` 傳入的是 local_host（可能為空字串），而非建構子使用的 local_hostname 值。若 SMTP_LOCAL_HOSTNAME 設定為非空，此處應傳入該值以確保 HELO/EHLO 使用覆寫的主機名稱；若未設定，傳入空字串可能導致伺服器拒絕。建議改為傳入 `local_host or None` 或與建構子一致的邏輯。

**判斷依據**：diff 中新增的 ehlo 呼叫使用 local_host 變數，而該變數可能為空字串，與建構子傳入的 local_hostname 不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 為多餘且可能誤導</summary>

在建構子呼叫後立即斷言 smtp 不為 None，但建構子正常情況下不會回傳 None，此斷言無實際作用，且若未來建構子可能回傳 None，此處應有更明確的錯誤處理。建議移除或改為明確的例外處理。

**判斷依據**：diff 中新增的 assert 陳述式，但 smtp 型別已標註為 smtplib.SMTP | None，且建構子不會回傳 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7624 (cache hit 4096) ｜ completion tokens 933 ｜ PR #6</sub>