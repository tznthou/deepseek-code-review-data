<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的本機主機名稱。主要變更在 api/libs/smtp.py 重構連線建立邏輯，並更新相關設定檔與測試。主要風險在於重構後對 smtplib 的呼叫方式可能與原本行為不一致，且 local_hostname 參數傳遞方式可能導致非預期行為。建議先確認 SMTP 連線建立邏輯的正確性，特別是 opportunistic TLS 與 local_hostname 的互動。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP 連線建立邏輯重構可能改變行為 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:28` | local_hostname 參數傳遞空字串可能導致非預期行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP 連線建立邏輯重構可能改變行為</summary>

原本的程式碼根據 use_tls 和 opportunistic_tls 的組合，明確選擇建立 SMTP_SSL 或 SMTP 連線，並在 opportunistic TLS 模式下先建立 SMTP 連線再呼叫 starttls。重構後使用三元運算子選擇類別，但條件 `(self.use_tls and not self.opportunistic_tls)` 只涵蓋了原本的 `use_tls=True, opportunistic_tls=False` 情況；當 `use_tls=False` 時，原本會建立 SMTP 連線，現在也會建立 SMTP 連線，但原本的程式碼在 `use_tls=False` 時不會呼叫 `ehlo` 或 `starttls`，而新程式碼在 `use_tls=False` 時也不會呼叫，這部分行為一致。然而，當 `use_tls=True, opportunistic_tls=True` 時，新程式碼會建立 SMTP 連線並呼叫 `ehlo(local_host)`、`starttls()`、`ehlo(local_host)`，但原本的程式碼在這種情況下會先建立 SMTP 連線，然後呼叫 `ehlo(self.server)`、`starttls()`、`ehlo(self.server)`。新程式碼將 `ehlo` 的參數改為 `local_host`，這可能改變 HELO/EHLO 命令中傳送的網域名稱，若 `local_host` 為空字串，則可能導致 SMTP 伺服器拒絕連線。建議確認此行為變更是否符合預期，並確保 `local_host` 在未設定時使用預設值（例如 `self.server`）。

**判斷依據**：diff 中顯示原本的程式碼在 opportunistic TLS 模式下使用 `smtp.ehlo(self.server)`，而新程式碼使用 `smtp.ehlo(local_host)`，且 `local_host` 來自 `dify_config.SMTP_LOCAL_HOSTNAME or ""`，若未設定則為空字串，可能導致 HELO/EHLO 命令不正確。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:28</code> local_hostname 參數傳遞空字串可能導致非預期行為</summary>

在建立 SMTP 連線時，傳入 `local_hostname=local_host or None`。若 `local_host` 為空字串，則傳入 `None`，這會讓 smtplib 使用預設的本機主機名稱。但原本的程式碼並未傳入 `local_hostname` 參數，因此行為可能相同。然而，在 opportunistic TLS 模式下，`ehlo(local_host)` 直接使用 `local_host`，若為空字串，則可能傳送空字串作為 HELO/EHLO 參數，這可能導致某些 SMTP 伺服器拒絕連線。建議在未設定 `SMTP_LOCAL_HOSTNAME` 時，使用 `self.server` 作為 HELO/EHLO 參數，或明確處理空字串的情況。

**判斷依據**：diff 中顯示 `local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`，且 `ehlo(local_host)` 直接使用該變數，未處理空字串。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6434 (cache hit 6400) ｜ completion tokens 1224 ｜ PR #6</sub>