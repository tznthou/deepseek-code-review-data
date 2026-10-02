<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並重構 SMTPClient.send 以支援此功能。主要風險在於重構後的連線建立邏輯：原本依 TLS 模式分支建立不同 SMTP 類別，現在改為單一三元運算式，可能改變行為（例如原本非 TLS 模式會建立 SMTP，現在若 use_tls 為 False 且 opportunistic_tls 為 True 仍會建立 SMTP，但原本會建立 SMTP_SSL？需確認）。此外，local_hostname 參數傳遞方式可能導致 smtplib 使用空字串而非 None，需驗證是否影響預設行為。測試僅驗證呼叫參數包含 local_hostname=ANY，未驗證實際傳遞的值。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | 重構後 SMTP 連線建立邏輯可能改變行為 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:25` | local_hostname 參數可能傳遞空字串而非 None | 0.60 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 可能造成非預期錯誤 | 0.50 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試僅驗證 local_hostname 參數存在，未驗證實際值 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> 重構後 SMTP 連線建立邏輯可能改變行為</summary>

原本程式碼依 use_tls 和 opportunistic_tls 的組合明確分支：
- use_tls=True, opportunistic_tls=True → smtplib.SMTP
- use_tls=True, opportunistic_tls=False → smtplib.SMTP_SSL
- use_tls=False → smtplib.SMTP

新程式碼使用三元運算式：
```python
smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)(...)
```
此運算式在 use_tls=False 且 opportunistic_tls=True 時會選擇 smtplib.SMTP，與原本相同；但在 use_tls=False 且 opportunistic_tls=False 時也會選擇 smtplib.SMTP，與原本相同。然而，原本在 use_tls=True 且 opportunistic_tls=False 時會建立 SMTP_SSL，新程式碼也相同。因此主要分支行為似乎一致，但需注意原本在 use_tls=True 且 opportunistic_tls=True 時會先建立 SMTP 再呼叫 ehlo 和 starttls，新程式碼也相同。不過，原本在 use_tls=False 時不會呼叫 ehlo，新程式碼也不會。因此行為可能一致，但重構增加了複雜度，且未涵蓋所有可能組合的測試。建議確認所有 TLS 模式組合的測試覆蓋。

**判斷依據**：diff 中原本的分支被替換為單一三元運算式，且後續的 ehlo/starttls 呼叫僅在 use_tls and opportunistic_tls 條件下執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:25</code> local_hostname 參數可能傳遞空字串而非 None</summary>

程式碼使用 `local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`，然後在建構 SMTP 時傳入 `local_hostname=local_host or None`。若設定值為空字串，則 `local_host` 為空字串，`local_host or None` 會得到 None，因此實際上傳遞 None。但若設定值為空白字串（例如 " "），則 `local_host` 為 " "，`local_host or None` 會得到 " "，可能導致 smtplib 使用空白字串作為 local_hostname，而非預設行為。建議明確處理空白字串，或直接使用 `dify_config.SMTP_LOCAL_HOSTNAME` 而不做 `or ""` 轉換。

**判斷依據**：diff 中新增此行，且後續使用 `local_host or None` 作為參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 可能造成非預期錯誤</summary>

新增 `assert smtp is not None` 用於型別檢查，但若 smtp 因某些原因為 None（例如建構子拋出例外），assert 會引發 AssertionError，可能掩蓋原始錯誤。建議使用更明確的錯誤處理或型別檢查。

**判斷依據**：diff 中新增此行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試僅驗證 local_hostname 參數存在，未驗證實際值</summary>

測試使用 `local_hostname=ANY` 驗證呼叫，未驗證傳遞的實際值是否正確（例如當設定 SMTP_LOCAL_HOSTNAME 時應傳遞該值，未設定時應傳遞 None）。建議增加測試案例驗證不同設定下的行為。

**判斷依據**：diff 中測試斷言從原本不包含 local_hostname 改為包含 ANY。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7615 (cache hit 1536) ｜ completion tokens 1372 ｜ PR #6</sub>