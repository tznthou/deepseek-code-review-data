<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並更新相關測試與設定檔。主要風險在於 smtplib 建構子參數傳遞方式：當 local_host 為空字串時，程式碼傳入 None 而非省略參數，可能導致與舊版 smtplib 不相容或行為不一致。此外，assert 敘述在最佳化模式下會被移除，不應作為控制流程使用。整體而言，功能方向合理，但需修正上述問題以確保相容性與穩健性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | smtplib 建構子 local_hostname 參數傳遞 None 可能導致不相容 | 0.80 |
| 🔸 | Minor | `api/libs/smtp.py:32` | 使用 assert 進行控制流程可能被最佳化移除 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> smtplib 建構子 local_hostname 參數傳遞 None 可能導致不相容</summary>

當 SMTP_LOCAL_HOSTNAME 未設定時，local_host 為空字串，程式碼傳入 local_hostname=None。然而，smtplib.SMTP 的建構子中 local_hostname 參數預設為 None，但若明確傳入 None，在某些 Python 版本或實作中可能被視為有效值，導致 socket.getfqdn() 未被呼叫，而直接使用 None 作為 HELO 主機名稱，造成 SMTP 伺服器拒絕連線。建議改為僅在 local_host 非空時才傳入 local_hostname 參數，或使用條件式展開參數。

**判斷依據**：diff 中新增的建構子呼叫明確傳入 local_hostname=local_host or None，而 local_host 可能為空字串，導致傳入 None。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> 使用 assert 進行控制流程可能被最佳化移除</summary>

assert smtp is not None 用於確保 smtp 不為 None，但在 Python 以 -O 參數執行時，assert 敘述會被移除，失去保護效果。此外，assert 不應用於控制流程，應改用 if smtp is None: raise ... 的方式。

**判斷依據**：diff 中新增 assert smtp is not None，但 smtp 在建構後不可能為 None，此 assert 僅為型別檢查用途，不應依賴。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6175 (cache hit 4096) ｜ completion tokens 677 ｜ PR #6</sub>