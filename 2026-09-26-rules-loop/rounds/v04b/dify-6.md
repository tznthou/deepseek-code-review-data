<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱。主要風險在於 smtp.py 中重構後的 SMTP 連線建立邏輯：使用三元運算子選擇 SMTP 類別並傳入 local_hostname，但 local_host 可能為空字串，導致傳入空字串而非 None，可能影響 smtplib 行為。此外，assert smtp is not None 在型別檢查後是多餘的，且若未來建構子回傳 None 會造成 AssertionError。整體而言，功能合理，但需修正 local_host 的處理方式。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | local_hostname 可能傳入空字串而非 None | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 為多餘且可能造成意外錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> local_hostname 可能傳入空字串而非 None</summary>

在 `send` 方法中，`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""` 會將 None 轉為空字串。接著在建構 SMTP 物件時傳入 `local_hostname=local_host or None`，若 local_host 為空字串，則 `local_host or None` 會是 None，因此實際上不會傳入空字串。但後續的 `smtp.ehlo(local_host)` 在 opportunistic TLS 模式下會傳入空字串，可能導致 HELO/EHLO 命令使用空字串作為主機名稱，某些 SMTP 伺服器可能拒絕。建議將 local_host 保留為 None 或直接使用設定值，並在呼叫 ehlo 時傳入 None 或有效主機名稱。

**判斷依據**：diff 中新增的程式碼：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""` 和 `smtp.ehlo(local_host)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 為多餘且可能造成意外錯誤</summary>

在建構 SMTP 物件後，新增了 `assert smtp is not None`。由於 smtp 的型別已標註為 `smtplib.SMTP | None`，且建構子正常情況下不會回傳 None，此 assert 是多餘的。若未來建構子因某些原因回傳 None，assert 會拋出 AssertionError，但這並非預期的錯誤處理方式。建議移除 assert，或改為明確的錯誤處理。

**判斷依據**：diff 中新增的 `assert smtp is not None`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6175 (cache hit 6144) ｜ completion tokens 738 ｜ PR #6</sub>