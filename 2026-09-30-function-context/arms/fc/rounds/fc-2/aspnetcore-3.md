<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 dotnet-dev-certs 在 Unix 上的 SSL_CERT_DIR 環境變數處理邏輯，並新增事件來源方法與調整事件監聽設定。主要風險在於環境變數解析的例外處理、路徑比較的正確性，以及事件監聽設定變更可能影響輸出。建議優先確認 SSL_CERT_DIR 解析邏輯與事件監聽的相容性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外 | 0.80 |
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確 | 0.75 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:408` | sawTrustFailure 變數在後續邏輯中可能被覆寫 | 0.70 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:127` | 事件監聽設定變更可能影響非 verbose 模式的輸出 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外</summary>

在解析現有 SSL_CERT_DIR 時，程式碼呼叫 `Path.GetFullPath(dir)` 來正規化路徑。如果環境變數中包含無效路徑（例如包含非法字元或格式錯誤），`Path.GetFullPath` 可能擲回 `ArgumentException`、`NotSupportedException` 或 `PathTooLongException`。雖然外層有 try-catch 捕捉，但 catch 區塊僅回傳 false，會將該目錄視為未包含，可能導致後續錯誤建議使用者附加目錄，或誤判為未設定。建議明確捕捉特定例外並記錄，或使用更安全的比較方式（例如僅比較字串，不進行完整路徑解析）。

**判斷依據**：diff 中新增的程式碼片段：`try { return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); } catch { return false; }`

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確</summary>

在 Unix 系統上，檔案路徑是區分大小寫的。程式碼使用 `StringComparison.OrdinalIgnoreCase` 比較 `Path.GetFullPath(dir)` 與 `certDirFullPath`，這可能導致大小寫不同的路徑被誤判為相同，進而跳過必要的環境變數設定建議。例如，若 SSL_CERT_DIR 包含 `/home/user/.dotnet/corefx/cryptography/x509stores/my`，而實際目錄為 `/home/user/.dotnet/corefx/cryptography/x509stores/My`，兩者會被視為相同，但實際上 OpenSSL 可能無法找到憑證。建議在 Unix 上使用區分大小寫的比較（`StringComparison.Ordinal`），或根據平台調整。

**判斷依據**：diff 中新增的程式碼片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:408</code> sawTrustFailure 變數在後續邏輯中可能被覆寫</summary>

在 `TrustCertificateCore` 方法中，`sawTrustFailure` 原本用於追蹤信任過程中的失敗。新增的程式碼在 OpenSSL 信任成功後，根據 SSL_CERT_DIR 的狀態設定 `sawTrustFailure = !hasValidSslCertDir;`，這會覆寫先前可能設定的 `sawTrustFailure` 值。如果先前已有其他信任失敗（例如 NSS 資料庫失敗），此覆寫可能導致最終回傳的 `TrustLevel` 不正確。建議使用獨立的變數來追蹤 SSL_CERT_DIR 的狀態，或合併邏輯時謹慎處理。

**判斷依據**：diff 中新增的程式碼片段：`sawTrustFailure = !hasValidSslCertDir;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:127</code> 事件監聽設定變更可能影響非 verbose 模式的輸出</summary>

原本只有在 verbose 模式才啟用事件監聽，現在改為一律建立 `ReporterEventListener` 並在非 verbose 模式啟用 `EventLevel.LogAlways`。這可能導致原本不會顯示的 LogAlways 事件（例如 `UnixSuggestSettingEnvironmentVariable`）在非 verbose 模式下輸出，改變使用者體驗。若這是預期行為，則需確認所有 LogAlways 事件都適合在一般模式顯示；若不是，則應調整事件等級或條件。

**判斷依據**：diff 中新增的程式碼片段：`var listener = new ReporterEventListener(reporter);` 與 `else { listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); }`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12176 (cache hit 12160) ｜ completion tokens 1327 ｜ PR #3</sub>