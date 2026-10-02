<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並重構 SMTPClient 的連線建立邏輯。主要風險在於重構後的連線建立邏輯是否正確處理各種 TLS 模式，以及 local_hostname 參數的傳遞方式。此外，測試斷言使用 ANY 可能降低測試精確度。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | 重構後的 SMTP 連線建立邏輯可能改變行為 | 0.80 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試斷言使用 ANY 降低精確度 | 0.70 |
| 🔸 | Minor | `api/libs/smtp.py:28` | local_hostname 參數傳遞空字串可能導致錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> 重構後的 SMTP 連線建立邏輯可能改變行為</summary>

原本的程式碼針對三種模式（TLS、opportunistic TLS、無 TLS）分別建立不同的 SMTP 物件，並在 opportunistic TLS 模式下先建立 SMTP 再呼叫 ehlo 和 starttls。重構後使用三元運算子選擇 SMTP_SSL 或 SMTP，並統一傳入 local_hostname 參數。然而，在 opportunistic TLS 模式下，原本的程式碼是先建立 SMTP 物件，再呼叫 ehlo(self.server)，而新程式碼改為 smtp.ehlo(local_host)，其中 local_host 可能為空字串（若未設定 SMTP_LOCAL_HOSTNAME）。這可能導致 HELO/EHLO 命令使用空字串作為主機名稱，與原本使用伺服器位址的行為不同，可能導致某些 SMTP 伺服器拒絕連線。建議在 local_host 為空時，仍使用 self.server 作為 ehlo 參數。

**判斷依據**：diff 中顯示原本的 smtp.ehlo(self.server) 被改為 smtp.ehlo(local_host)，而 local_host 可能為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試斷言使用 ANY 降低精確度</summary>

測試中將原本的 assert_called_once_with 改為使用 ANY 來匹配 local_hostname 參數，這使得測試無法驗證 local_hostname 是否正確傳遞。建議使用具體的值（例如 None 或預期的 local_hostname）來確保行為正確。

**判斷依據**：diff 中顯示測試斷言從原本的精確匹配改為使用 ANY。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:28</code> local_hostname 參數傳遞空字串可能導致錯誤</summary>

在建立 SMTP 物件時，使用 local_hostname=local_host or None，若 local_host 為空字串，則傳入 None。這可能導致 smtplib 使用預設的 local_hostname（即 socket.getfqdn()），與原本行為一致。但若使用者設定 SMTP_LOCAL_HOSTNAME 為空字串，可能期望使用空字串作為 HELO 名稱，但實際上會使用預設值。建議明確處理空字串的情況，或使用更明確的邏輯。

**判斷依據**：diff 中顯示 local_hostname=local_host or None，當 local_host 為空字串時會傳入 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7615 (cache hit 7552) ｜ completion tokens 1036 ｜ PR #6</sub>