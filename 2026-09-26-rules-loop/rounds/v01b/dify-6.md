<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並更新相關測試與環境變數範例。主要風險在於 SMTP 連線建立邏輯的重構：原本依 TLS 模式分支建立連線，現在改為單一三元運算式，並在 opportunistic TLS 模式下呼叫 ehlo 時傳入 local_host 而非原本的 server 位址，可能改變行為。此外，local_hostname 參數傳入空字串時的行為需確認，且測試僅驗證參數存在，未涵蓋實際值。整體而言，功能合理，但需確認重構後的行為一致性與空值處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | 重構後 SMTP 連線建立邏輯可能改變行為 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:28` | local_hostname 傳入空字串可能導致 SMTP 連線失敗 | 0.60 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試僅驗證 local_hostname 參數存在，未驗證實際值 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> 重構後 SMTP 連線建立邏輯可能改變行為</summary>

原本程式碼依 `use_tls` 與 `opportunistic_tls` 的組合，分別建立 `SMTP` 或 `SMTP_SSL` 實例，並在 opportunistic TLS 模式下先以 `self.server` 作為 HELO 參數呼叫 `ehlo`。重構後，所有模式都使用同一個三元運算式建立連線，且 opportunistic TLS 模式下改以 `local_host`（可能為空字串）呼叫 `ehlo`。這可能導致：
1. 當 `SMTP_LOCAL_HOSTNAME` 未設定時，`local_host` 為空字串，傳入 `ehlo` 可能導致某些 SMTP 伺服器拒絕連線（原本是傳入 `self.server`）。
2. 三元運算式在 `use_tls=True` 且 `opportunistic_tls=False` 時會建立 `SMTP_SSL`，但原本的程式碼在 `use_tls=True` 且 `opportunistic_tls=True` 時會先建立 `SMTP` 再升級，現在則直接建立 `SMTP`（因為條件 `self.use_tls and not self.opportunistic_tls` 為 False），行為一致。
建議：保留原本的分支邏輯，僅在需要時傳入 `local_hostname`，並確認 `ehlo` 的參數應為有效主機名稱或保留原本的 `self.server`。

**判斷依據**：diff 中原本的 if-else 分支被替換為單一三元運算式，且 opportunistic TLS 分支的 ehlo 參數從 self.server 改為 local_host。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:28</code> local_hostname 傳入空字串可能導致 SMTP 連線失敗</summary>

當 `SMTP_LOCAL_HOSTNAME` 未設定時，`local_host` 為空字串，但程式碼使用 `local_host or None` 將空字串轉為 `None`，因此 `local_hostname` 參數會是 `None`，這與原本未傳入該參數的行為相同（smtplib 預設使用 socket.getfqdn()）。然而，在 opportunistic TLS 模式下，`ehlo(local_host)` 直接傳入空字串，可能導致某些 SMTP 伺服器拒絕。建議在呼叫 `ehlo` 時也使用 `local_host or None` 或保留原本的 `self.server`。

**判斷依據**：diff 中新增的 `local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""` 以及後續的 `smtp.ehlo(local_host)` 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試僅驗證 local_hostname 參數存在，未驗證實際值</summary>

測試中將 `local_hostname` 的期望值改為 `ANY`，這使得測試無法驗證傳入的值是否正確（例如是否為設定的主機名稱或 None）。建議增加測試案例，明確驗證當 `SMTP_LOCAL_HOSTNAME` 設定時，傳入的值為該設定值；未設定時，傳入的值為 None 或預設行為。

**判斷依據**：diff 中測試斷言從原本不檢查 local_hostname 改為使用 ANY，未驗證實際值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7614 (cache hit 7552) ｜ completion tokens 1261 ｜ PR #6</sub>