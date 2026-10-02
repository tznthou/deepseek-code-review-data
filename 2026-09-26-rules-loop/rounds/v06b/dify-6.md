<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並更新相關測試與環境變數範例。主要風險在於 smtplib 的 local_hostname 參數若傳入空字串可能導致 SMTP 連線失敗，且設定值未做格式驗證。建議修正空字串處理並考慮增加驗證。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP_LOCAL_HOSTNAME 為空字串時可能導致連線失敗 | 0.80 |
| 🔸 | Minor | `api/configs/feature/__init__.py:952` | SMTP_LOCAL_HOSTNAME 未驗證格式 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP_LOCAL_HOSTNAME 為空字串時可能導致連線失敗</summary>

當 SMTP_LOCAL_HOSTNAME 未設定時，local_host 為空字串，但程式碼將 local_host or None 傳給 smtplib.SMTP 的 local_hostname 參數。若 local_host 為空字串，則傳入 None，smtplib 會使用 socket.getfqdn() 取得本機主機名稱，這可能不是預期行為。建議直接傳入 local_host（空字串時 smtplib 會自動處理），或明確設定為 None。

**判斷依據**：diff 中新增的 local_hostname=local_host or None，當 local_host 為空字串時會傳 None，可能導致非預期行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/configs/feature/__init__.py:952</code> SMTP_LOCAL_HOSTNAME 未驗證格式</summary>

SMTP_LOCAL_HOSTNAME 直接從環境變數讀取，未驗證是否為合法主機名稱。若設定為無效值（如包含空格或特殊字元），可能導致 SMTP 連線失敗或錯誤。建議在設定層級增加驗證（例如使用 Pydantic 的欄位驗證）。

**判斷依據**：新增的設定欄位沒有驗證規則。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7604 (cache hit 7552) ｜ completion tokens 639 ｜ PR #6</sub>