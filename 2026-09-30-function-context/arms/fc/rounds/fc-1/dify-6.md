<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的本機主機名稱，並在 SMTPClient 中傳遞該值。主要風險在於 SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性；此外，當設定為空字串時，local_hostname 會傳入 None，可能導致非預期的連線行為。建議將設定值注入 SMTPClient 建構子，並確保空字串時不傳遞 local_hostname 參數。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:25` | SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:28` | 當 SMTP_LOCAL_HOSTNAME 為空字串時，local_hostname 傳入 None 可能導致非預期行為 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:25</code> SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性</summary>

SMTPClient 在建構時直接從全域 dify_config 讀取 SMTP_LOCAL_HOSTNAME，這使得 SMTPClient 與全域設定耦合，難以在測試中隔離或在不同設定下重用。建議將 local_hostname 作為建構子參數傳入，由呼叫端負責提供設定值。

**判斷依據**：diff 中新增 `from configs import dify_config` 並在建構子中使用 `dify_config.SMTP_LOCAL_HOSTNAME`，直接讀取全域設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:28</code> 當 SMTP_LOCAL_HOSTNAME 為空字串時，local_hostname 傳入 None 可能導致非預期行為</summary>

程式碼使用 `local_host or None`，若設定為空字串，則傳入 None。smtplib 在建構時若 local_hostname 為 None，會自動使用 socket.getfqdn()，這可能與預期不符（預期不覆寫時應使用預設行為，但 None 可能觸發不同的行為）。建議明確處理空字串，例如僅在設定非空時才傳遞 local_hostname 參數。

**判斷依據**：diff 中 `local_hostname=local_host or None`，當 local_host 為空字串時傳入 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6434 (cache hit 1536) ｜ completion tokens 650 ｜ PR #6</sub>