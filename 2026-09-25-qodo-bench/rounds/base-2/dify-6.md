<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的本機主機名稱，並重構 SMTPClient 的連線建立邏輯。主要風險在於重構後的連線建立方式可能改變原本的行為，尤其是 opportunistic TLS 模式下原本會先以非 SSL 連線再升級，現在改為直接建立連線後再呼叫 starttls，需確認 smtplib 的實作是否相容。另外，local_hostname 參數傳遞空字串或 None 的行為需驗證，避免造成連線失敗。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | 重構後 opportunistic TLS 連線建立方式可能與原本不同 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 可能不是必要的 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> 重構後 opportunistic TLS 連線建立方式可能與原本不同</summary>

原本在 opportunistic TLS 模式下，會先建立非 SSL 的 SMTP 連線，然後呼叫 ehlo、starttls、再 ehlo。重構後，連線建立改為根據條件選擇 SMTP_SSL 或 SMTP，但 opportunistic TLS 模式仍使用 SMTP（非 SSL），因此行為看似相同。然而，原本的程式碼在建立 SMTP 連線時沒有傳入 local_hostname，而新程式碼傳入了 local_hostname（可能為空字串或 None）。如果 local_hostname 為空字串，smtplib 可能將其視為有效的主機名稱，導致 HELO/EHLO 命令使用空字串，可能被伺服器拒絕。建議確認 smtplib 對空字串的處理，並考慮在 local_hostname 為空時不傳遞該參數。

**判斷依據**：diff 中新增的連線建立程式碼，使用 local_hostname=local_host or None，但 local_host 可能為空字串，導致傳入空字串而非 None。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 可能不是必要的</summary>

新增的 assert smtp is not None 在連線建立後立即執行，但 smtp 變數在 try 區塊內被賦值，且型別標註為 smtplib.SMTP | None。由於連線建立函式不會回傳 None，此 assert 可能永遠不會觸發，但若未來修改導致可能為 None，assert 在最佳化模式下會被移除，無法提供保護。建議移除或改為明確的型別檢查。

**判斷依據**：diff 中新增的 assert 陳述式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4936 (cache hit 4864) ｜ completion tokens 731 ｜ PR #6</sub>