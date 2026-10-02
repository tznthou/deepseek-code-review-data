<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 SMTP_LOCAL_HOSTNAME 設定，允許覆寫 SMTP HELO/EHLO 使用的主機名稱。主要風險在於 smtp.py 中重構後的連線建立邏輯：使用三元運算子選擇 SMTP 類別時，將 local_hostname 參數傳給所有類別，但 SMTP_SSL 的建構子可能不接受該參數（需確認 Python 版本），且 local_host 為空字串時會傳入空字串而非 None，可能導致 smtplib 內部行為異常。此外，opportunistic TLS 模式下，ehlo 呼叫改為傳入 local_host，但若 local_host 為空字串，可能導致 EHLO 命令格式錯誤。建議修正參數傳遞方式，並確保空值時使用 None。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `api/libs/smtp.py:28` | SMTP_SSL 建構子可能不支援 local_hostname 參數 | 0.80 |
| ⚠️ | Major | `api/libs/smtp.py:25` | local_host 為空字串時傳入空字串而非 None | 0.70 |
| 🔸 | Minor | `api/libs/smtp.py:32` | assert smtp is not None 為冗餘且可能被最佳化移除 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:28</code> SMTP_SSL 建構子可能不支援 local_hostname 參數</summary>

在 Python 3.10 及更早版本中，smtplib.SMTP_SSL 的 __init__ 方法簽名為 (host='', port=0, local_hostname=None, keyfile=None, certfile=None, timeout=..., ...)，實際上接受 local_hostname 參數。但需確認專案使用的 Python 版本是否支援。若版本過舊，可能導致 TypeError。建議檢查 Python 版本，或改用條件式分別建立 SMTP 與 SMTP_SSL 實例，避免將 local_hostname 傳給不支援的類別。

**判斷依據**：diff 中新增的這行使用三元運算子選擇 SMTP_SSL 或 SMTP，並傳入 local_hostname 參數。若 SMTP_SSL 不支援該參數，將拋出 TypeError。

</details>

<details><summary>⚠️ <b>Major</b> — <code>api/libs/smtp.py:25</code> local_host 為空字串時傳入空字串而非 None</summary>

local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""，若設定為空字串，則 local_host 為空字串。在建構 SMTP 時傳入 local_hostname=local_host or None，但 local_host 為空字串時，local_host or None 會得到 None，因此實際上傳入 None，這部分正確。但後續 opportunistic TLS 模式中，smtp.ehlo(local_host) 會傳入空字串，可能導致 EHLO 命令格式錯誤。建議在呼叫 ehlo 時也使用 local_host or None，或確保 local_host 不為空字串。

**判斷依據**：diff 中 opportunistic TLS 分支的 ehlo 呼叫改為傳入 local_host，若 local_host 為空字串，smtplib 可能發出 'EHLO ' 而非 'EHLO [預設主機名稱]'，導致伺服器拒絕。

</details>

<details><summary>🔸 <b>Minor</b> — <code>api/libs/smtp.py:32</code> assert smtp is not None 為冗餘且可能被最佳化移除</summary>

assert smtp is not None 在建立 SMTP 實例後立即執行，但該實例必定非 None，因此 assert 永遠為真。若使用 python -O 執行，assert 會被移除，不影響功能。此 assert 無實際作用，建議移除。

**判斷依據**：diff 中新增的 assert 語句，但 smtp 剛被賦值為 SMTP 或 SMTP_SSL 實例，不可能為 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4900 (cache hit 1408) ｜ completion tokens 1026 ｜ PR #6</sub>