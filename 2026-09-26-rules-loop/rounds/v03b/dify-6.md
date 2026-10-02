<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並在 SMTPClient 中傳遞 local_hostname 參數。主要風險在於 smtplib 的 local_hostname 參數不接受空字串，程式碼以 `local_host or None` 處理，但測試僅驗證 ANY，未涵蓋實際值。此外，`assert smtp is not None` 在最佳化模式下會被移除，且 SMTP_SSL 不應呼叫 ehlo。整體改動方向合理，但需修正上述問題並補強測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP_SSL 不應呼叫 ehlo，可能導致非預期行為 | 0.90 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert 在最佳化模式下會被移除，不應作為必要檢查 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:25` | local_hostname 傳遞空字串可能導致 smtplib 錯誤 | 0.70 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試僅驗證 local_hostname 為 ANY，未驗證實際值 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP_SSL 不應呼叫 ehlo，可能導致非預期行為</summary>

在 `self.use_tls and not self.opportunistic_tls` 時使用 `smtplib.SMTP_SSL`，但後續的 `if self.use_tls and self.opportunistic_tls:` 條件不會執行，因此不會呼叫 ehlo。然而，若未來條件變更或誤用，SMTP_SSL 的 ehlo 呼叫可能導致錯誤。建議明確區分 SMTP 與 SMTP_SSL 的初始化流程，避免依賴條件判斷。

**判斷依據**：diff 中新增的 SMTP_SSL 實例化後，緊接著的條件判斷僅在 opportunistic_tls 為真時呼叫 ehlo，因此 SMTP_SSL 不會呼叫 ehlo。但若未來修改條件，可能誤用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert 在最佳化模式下會被移除，不應作為必要檢查</summary>

`assert smtp is not None` 在 Python 以 `-O` 執行時會被移除，無法保證 smtp 不為 None。雖然目前 smtp 必定有值，但此 assert 無實際作用，建議移除或改用明確的例外處理。

**判斷依據**：diff 中新增的 assert 語句，在最佳化模式下會被跳過。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:25</code> local_hostname 傳遞空字串可能導致 smtplib 錯誤</summary>

`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""` 將 None 轉為空字串，但 smtplib 的 local_hostname 參數不接受空字串，會拋出 ValueError。雖然後續以 `local_host or None` 傳遞，但若設定為空字串，仍可能觸發錯誤。建議直接使用 `dify_config.SMTP_LOCAL_HOSTNAME`，並在傳遞前檢查。

**判斷依據**：diff 中將設定值轉為空字串，但 smtplib 不接受空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試僅驗證 local_hostname 為 ANY，未驗證實際值</summary>

測試使用 `ANY` 驗證 local_hostname，未確認是否正確傳遞設定值。建議增加測試案例，驗證當 SMTP_LOCAL_HOSTNAME 設定時，傳遞的值正確；未設定時，傳遞 None。

**判斷依據**：diff 中測試斷言使用 ANY，未驗證實際值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7624 (cache hit 7552) ｜ completion tokens 1064 ｜ PR #6</sub>