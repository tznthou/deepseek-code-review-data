<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，讓使用者可覆寫 SMTP HELO/EHLO 使用的本機主機名稱。主要變更在 api/libs/smtp.py，將原本依 TLS 模式分支建立 SMTP 連線的邏輯改為單一三元運算式，並傳入 local_hostname 參數。整體風險中等：主要疑慮是重構後的連線建立邏輯與原本行為是否完全等價，以及 local_hostname 參數在未設定時傳入 None 是否會影響 smtplib 的預設行為。測試已更新以匹配新的呼叫簽章，但未新增針對 local_hostname 實際傳遞值的測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | 重構後的 SMTP 連線建立邏輯可能與原本行為不一致 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 可能造成非預期錯誤 | 0.70 |
| 🔸 | Minor | `api/libs/smtp.py:30` | ehlo 呼叫使用 local_host 變數可能傳入空字串 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試僅驗證 local_hostname 參數存在，未驗證實際傳遞值 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> 重構後的 SMTP 連線建立邏輯可能與原本行為不一致</summary>

原本程式碼在 `use_tls=True` 且 `opportunistic_tls=False` 時使用 `smtplib.SMTP_SSL`，否則使用 `smtplib.SMTP`。重構後的三元運算式 `(smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)` 在邏輯上等價，但需確認 `smtplib.SMTP` 和 `smtplib.SMTP_SSL` 的建構子都接受 `local_hostname` 參數，且傳入 `None` 時行為與未傳入相同。若 `local_hostname=None` 會導致 smtplib 使用空字串而非預設值，可能造成 HELO/EHLO 失敗。建議查閱 smtplib 文件或實際測試確認。

**判斷依據**：diff 中原本的 if-else 分支被替換為三元運算式，且新增了 local_hostname 參數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 可能造成非預期錯誤</summary>

新增的 `assert smtp is not None` 在正常情況下不會觸發，但若未來建構子拋出例外或回傳 None（不太可能），會導致 AssertionError。此 assert 似乎只是為了滿足型別檢查，但可能掩蓋真正的錯誤。建議移除或改用更明確的錯誤處理。

**判斷依據**：diff 中新增了 assert 陳述式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:30</code> ehlo 呼叫使用 local_host 變數可能傳入空字串</summary>

在 opportunistic TLS 模式下，`smtp.ehlo(local_host)` 和 `smtp.ehlo(local_host)` 使用 `local_host` 變數，該變數在未設定 SMTP_LOCAL_HOSTNAME 時為空字串。原本程式碼使用 `self.server` 作為 HELO 名稱，現在改為空字串可能導致某些 SMTP 伺服器拒絕連線。建議在未設定時使用預設值（例如 `self.server` 或讓 smtplib 自行決定）。

**判斷依據**：diff 中原本的 `smtp.ehlo(self.server)` 被改為 `smtp.ehlo(local_host)`，且 `local_host` 可能為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試僅驗證 local_hostname 參數存在，未驗證實際傳遞值</summary>

測試中將 `assert_called_once_with` 的 `local_hostname` 參數改為 `ANY`，這表示測試只確認有傳入該參數，但未驗證其值是否正確。建議增加測試案例，分別驗證設定 SMTP_LOCAL_HOSTNAME 與未設定時的行為。

**判斷依據**：diff 中測試斷言從原本的精確比對改為使用 ANY。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7534 (cache hit 4096) ｜ completion tokens 1219 ｜ PR #6</sub>