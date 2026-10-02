<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱，並更新相關測試與設定檔。主要風險在於 smtplib 的 local_hostname 參數若傳入空字串可能導致連線失敗，且測試僅驗證參數存在而未驗證實際值，可能掩蓋回歸。建議修正空字串處理並強化測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP_LOCAL_HOSTNAME 為空字串時可能導致連線失敗 | 0.80 |
| 🔸 | Minor | `api/tests/unit_tests/libs/test_smtp_client.py:20` | 測試僅驗證 local_hostname 參數存在，未驗證實際值 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP_LOCAL_HOSTNAME 為空字串時可能導致連線失敗</summary>

當 SMTP_LOCAL_HOSTNAME 未設定時，dify_config.SMTP_LOCAL_HOSTNAME 為 None，local_host 為空字串。程式碼將 local_hostname 設為空字串或 None 傳給 smtplib.SMTP。smtplib 在 local_hostname 為空字串時可能將其視為無效主機名稱，導致連線失敗或 HELO 命令錯誤。建議在 local_host 為空時不要傳遞 local_hostname 參數，或明確傳入 None。

**判斷依據**：diff 中新增的程式碼使用 local_host or None，當 local_host 為空字串時會傳入 None，但 smtplib 對 None 的處理可能與預期不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/tests/unit_tests/libs/test_smtp_client.py:20</code> 測試僅驗證 local_hostname 參數存在，未驗證實際值</summary>

測試使用 ANY 來匹配 local_hostname 參數，僅確認參數被傳遞，但未驗證其值是否正確。這可能掩蓋 local_hostname 設定錯誤的問題。建議增加測試案例，驗證當 SMTP_LOCAL_HOSTNAME 設定時，傳入的值正確；未設定時，傳入 None 或不傳遞。

**判斷依據**：diff 中測試斷言使用 ANY，未檢查實際值。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7534 (cache hit 7424) ｜ completion tokens 651 ｜ PR #6</sub>