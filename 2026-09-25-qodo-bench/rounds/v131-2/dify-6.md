<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的本機主機名稱，並更新相關設定檔與測試。主要風險在於 smtp.py 中 local_host 的處理：當設定為空字串時，會將 local_hostname 設為 None，可能導致 smtplib 使用 socket.getfqdn() 的結果，而非原本的 server 參數，造成行為改變。此外，assert smtp is not None 在 production 中可能被停用，且若建構子拋出例外，smtp 變數可能未定義，導致後續錯誤。建議修正 local_host 的預設值處理，並移除不必要的 assert。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | local_hostname 設為 None 可能導致非預期的 HELO 名稱 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 可能被停用且無助於錯誤處理 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> local_hostname 設為 None 可能導致非預期的 HELO 名稱</summary>

當 SMTP_LOCAL_HOSTNAME 未設定或為空字串時，local_host 為空字串，傳入 local_hostname 的參數為 None。這會使 smtplib 在建構時使用 socket.getfqdn() 的結果作為 local_hostname，而非原本的 server 參數。這可能導致 HELO/EHLO 命令使用不同的主機名稱，進而影響郵件伺服器的接受度。建議改為：若 local_host 為空，則傳入 self.server 或省略 local_hostname 參數。

**判斷依據**：diff 中新增的程式碼將 local_hostname 設為 local_host or None，而 local_host 來自 dify_config.SMTP_LOCAL_HOSTNAME，預設為 None，因此當未設定時會傳入 None。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 可能被停用且無助於錯誤處理</summary>

assert smtp is not None 在 Python 最佳化模式（-O）下會被移除，且此處 smtp 必定不為 None（因為建構子成功回傳），因此 assert 沒有實際作用。若建構子拋出例外，smtp 變數可能未定義，後續的 smtp.ehlo 會導致 UnboundLocalError。建議移除 assert，並確保例外處理能正確關閉連線。

**判斷依據**：diff 中新增 assert smtp is not None，但 smtp 在建構成功後必定非 None，且若建構失敗，程式會拋出例外，不會執行到 assert。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4900 (cache hit 4864) ｜ completion tokens 738 ｜ PR #6</sub>