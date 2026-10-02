<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的本機主機名稱，並更新相關設定檔與測試。主要風險在於 smtplib 建構子呼叫方式改變，可能影響 TLS 模式下的行為，且 local_hostname 參數傳遞方式需確認與 Python 版本相容。整體變更範圍小，但需驗證 SMTP 連線在各種 TLS 設定下的正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP 類別選擇邏輯可能改變非 TLS 與 TLS 模式的行為 | 0.80 |
| ⚠️ | Major | `api/libs/smtp.py:28` | local_hostname 參數傳遞空字串可能導致 SMTP 連線失敗 | 0.70 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 可能被最佳化移除 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP 類別選擇邏輯可能改變非 TLS 與 TLS 模式的行為</summary>

原本程式碼根據 use_tls 和 opportunistic_tls 明確選擇 SMTP 或 SMTP_SSL，並在 opportunistic TLS 時先建立 SMTP 再呼叫 starttls。新程式碼使用三元運算子選擇類別，但條件 `(self.use_tls and not self.opportunistic_tls)` 在 use_tls=False 時會選擇 SMTP（正確），但在 use_tls=True 且 opportunistic_tls=True 時也會選擇 SMTP（正確），然而在 use_tls=True 且 opportunistic_tls=False 時選擇 SMTP_SSL（正確）。看似等價，但需注意原本在非 TLS 模式下（use_tls=False）直接建立 SMTP，新程式碼也相同。然而，原本在 opportunistic TLS 模式下，先建立 SMTP 後呼叫 ehlo(self.server)，新程式碼改為 ehlo(local_host)，其中 local_host 可能為空字串，這可能導致 HELO 命令使用空字串而非伺服器位址，違反 SMTP 規範。建議確認 local_host 為空時應回退為 self.server。

**判斷依據**：diff 中原本的 if-else 分支被替換為三元運算子，且 ehlo 呼叫從 self.server 改為 local_host。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> local_hostname 參數傳遞空字串可能導致 SMTP 連線失敗</summary>

程式碼使用 `local_host or None` 將空字串轉為 None，但 smtplib.SMTP 的 local_hostname 參數若為 None，會使用 socket.getfqdn() 取得本機主機名稱。若設定 SMTP_LOCAL_HOSTNAME 為空字串，原本意圖可能是使用預設值，但傳遞 None 會觸發 getfqdn()，可能導致 DNS 查詢延遲或失敗。建議明確處理空字串，例如直接傳遞 local_host（若為空字串則由 smtplib 自行處理）或設定為 None 前先檢查。

**判斷依據**：diff 中新增 local_hostname 參數，並使用 `local_host or None`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 可能被最佳化移除</summary>

新增的 `assert smtp is not None` 在 Python 最佳化模式（-O）下會被移除，且此處 smtp 必定不為 None，因為建構子已指派。此 assert 無實際作用，建議移除。

**判斷依據**：diff 中新增 assert 陳述式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4936 (cache hit 4864) ｜ completion tokens 1015 ｜ PR #6</sub>