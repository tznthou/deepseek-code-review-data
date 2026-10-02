<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 dotnet-dev-certs 在 Unix 平台上的信任流程：當 SSL_CERT_DIR 已設定時，會檢查是否已包含憑證目錄，並據此輸出對應訊息；同時將 EventSource 的監聽改為預設啟用 LogAlways 層級，以確保訊息總會顯示。主要風險在於 SSL_CERT_DIR 解析邏輯的潛在例外、路徑比較的語意問題，以及 EventSource 監聽器未釋放可能造成的資源洩漏。建議先修正路徑解析與比較邏輯，並確認監聽器生命週期。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外 | 0.80 |
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確 | 0.75 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:364` | SSL_CERT_DIR 解析時未處理空目錄項目 | 0.70 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:127` | ReporterEventListener 未釋放可能造成資源洩漏 | 0.70 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | EventSource 監聽器預設啟用 LogAlways 可能影響效能 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外</summary>

在解析現有 SSL_CERT_DIR 時，程式碼對每個目錄呼叫 `Path.GetFullPath(dir)`，但僅以 `catch` 捕捉例外並回傳 false。然而，`Path.GetFullPath` 可能因無效路徑字元、過長路徑或權限問題擲回 `ArgumentException`、`PathTooLongException`、`SecurityException` 等。若例外發生，該目錄會被忽略，可能導致誤判憑證目錄已存在或未存在。建議明確捕捉特定例外並記錄，或先驗證路徑格式。

**判斷依據**：diff 中新增的程式碼片段：`try { return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); } catch { return false; }`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確</summary>

Unix 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，可能將不同大小寫的目錄視為相同，導致誤判。例如 `/home/user/.dotnet/corefx/cryptography/x509stores/ca` 與 `/HOME/USER/.DOTNET/...` 會被視為相同，但實際上可能指向不同位置。建議在 Unix 上使用 `StringComparison.Ordinal`，或根據作業系統選擇比較方式。

**判斷依據**：diff 中新增的程式碼片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:364</code> SSL_CERT_DIR 解析時未處理空目錄項目</summary>

程式碼使用 `existingSslCertDir.Split(Path.PathSeparator)` 分割環境變數，但未移除空字串項目。若 SSL_CERT_DIR 包含連續分隔符（如 `dir1::dir2`），會產生空字串，後續 `string.IsNullOrWhiteSpace(dir)` 檢查會將其忽略，但可能導致其他邏輯問題。建議使用 `StringSplitOptions.RemoveEmptyEntries` 分割。

**判斷依據**：diff 中新增的程式碼片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:127</code> ReporterEventListener 未釋放可能造成資源洩漏</summary>

在 `OnExecute` 中建立了 `ReporterEventListener` 實例，但未在結束時呼叫 `Dispose`。`EventListener` 實作 `IDisposable`，若未釋放可能導致事件監聽器持續存在，造成記憶體或資源洩漏。建議使用 `using` 陳述式或明確呼叫 `Dispose`。

**判斷依據**：diff 中新增的程式碼片段：`var listener = new ReporterEventListener(reporter);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> EventSource 監聽器預設啟用 LogAlways 可能影響效能</summary>

在非 verbose 模式下，程式碼現在會以 `EventLevel.LogAlways` 啟用事件監聽器，這可能導致大量事件被處理，影響效能。雖然 `LogAlways` 層級的事件通常較少，但若未來新增更多此層級事件，可能造成不必要的負擔。建議確認此變更的必要性，或考慮使用更精確的過濾條件。

**判斷依據**：diff 中新增的程式碼片段：`listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12176 (cache hit 1536) ｜ completion tokens 1369 ｜ PR #3</sub>