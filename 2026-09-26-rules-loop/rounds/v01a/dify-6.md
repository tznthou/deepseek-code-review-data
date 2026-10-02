<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並在 SMTPClient 中傳遞該參數。主要風險在於 local_host 變數可能為空字串，導致 smtplib 使用空字串作為 local_hostname，可能造成 SMTP 伺服器拒絕連線或行為異常。此外，測試僅驗證參數存在（ANY），未驗證實際傳遞的值，且缺少對新設定的測試。建議修正空字串處理並補強測試。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | local_host 為空字串時可能導致 SMTP 連線失敗 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:31` | ehlo 呼叫傳入空字串可能導致錯誤 | 0.70 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試僅驗證 local_hostname 參數存在，未驗證其值 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> local_host 為空字串時可能導致 SMTP 連線失敗</summary>

當 SMTP_LOCAL_HOSTNAME 未設定時，local_host 為空字串 ""，但程式碼將 local_hostname 設為 local_host or None，因此會傳入空字串而非 None。smtplib 在建構時若 local_hostname 為空字串，可能導致 HELO/EHLO 命令使用空字串，某些 SMTP 伺服器會拒絕此類連線。建議改為：local_hostname=local_host if local_host else None，或直接使用 local_host or None（但需確認 smtplib 對空字串的處理）。

**判斷依據**：diff 中新增的 local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""，以及 local_hostname=local_host or None。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:31</code> ehlo 呼叫傳入空字串可能導致錯誤</summary>

在 opportunistic TLS 模式下，smtp.ehlo(local_host) 會將 local_host 作為參數傳入，若 local_host 為空字串，可能導致 EHLO 命令格式錯誤。建議改為 smtp.ehlo(local_host or None) 或僅在 local_host 非空時傳入。

**判斷依據**：diff 中新增的兩行 ehlo 呼叫，local_host 可能為空字串。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試僅驗證 local_hostname 參數存在，未驗證其值</summary>

測試使用 ANY 來匹配 local_hostname，無法驗證實際傳入的值是否正確。建議增加測試案例，明確設定 SMTP_LOCAL_HOSTNAME 並驗證傳入的值。

**判斷依據**：diff 中測試斷言使用 ANY。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7614 (cache hit 1536) ｜ completion tokens 844 ｜ PR #6</sub>