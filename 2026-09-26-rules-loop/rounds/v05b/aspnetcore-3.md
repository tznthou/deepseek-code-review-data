<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Unix 憑證信任流程：當 SSL_CERT_DIR 已包含目標目錄時不再重複提示，並新增對應事件與訊息格式。主要風險在於路徑比較邏輯（大小寫不敏感、例外吞掉）可能誤判，以及 EventSource 事件 ID 與訊息格式的相容性。另有一處 NssDb 類別改寫為傳統建構子，違反 R11 主要建構子規範。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 可能誤判 | 0.80 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:994` | [R11] NssDb 類別未使用主要建構子 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:377` | catch 區塊吞掉所有例外，可能隱藏路徑處理錯誤 | 0.60 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1314` | EventSource 事件 ID 113 與 114 可能與既有事件衝突 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 可能誤判</summary>

在 Unix 系統上，路徑大小寫敏感。使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能將不同目錄視為相同，導致誤判憑證目錄已存在於 SSL_CERT_DIR 中，進而跳過必要的環境變數設定提示。建議改用 `StringComparison.Ordinal`（或 `StringComparison.OrdinalIgnoreCase` 僅在 Windows 上使用）。

**判斷依據**：diff 中新增的比較邏輯使用 OrdinalIgnoreCase，而此程式碼路徑主要針對 Unix（檔案位於 UnixCertificateManager.cs）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:994</code> [R11] NssDb 類別未使用主要建構子</summary>

此類別原本使用主要建構子（`private sealed class NssDb(string path, bool isFirefox)`），但被改寫為傳統建構子與欄位指派。根據規範 R11，簡單的建構子指派應使用主要建構子語法。建議改回主要建構子形式。

**判斷依據**：diff 中將原本的主要建構子改為傳統建構子，違反 R11。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:377</code> catch 區塊吞掉所有例外，可能隱藏路徑處理錯誤</summary>

`catch` 區塊未指定例外類型，會吞掉所有例外（包括非預期的 `OutOfMemoryException` 等）。雖然目的是忽略無效目錄，但過度寬鬆的例外處理可能掩蓋真正的錯誤。建議至少記錄或限定捕捉 `IOException`、`UnauthorizedAccessException` 等預期例外。

**判斷依據**：diff 中新增的 try-catch 區塊，catch 未指定例外類型。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1314</code> EventSource 事件 ID 113 與 114 可能與既有事件衝突</summary>

新增事件 ID 113 與 114，需確認未與其他事件 ID 重複。若重複可能導致事件追蹤混淆。建議檢查整個 EventSource 類別中所有事件 ID 的唯一性。

**判斷依據**：diff 中新增事件 ID 113 與 114，未提供全域唯一性檢查。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5579 (cache hit 5504) ｜ completion tokens 1193 ｜ PR #3</sub>