<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正了 dotnet-dev-certs 在 Unix 上處理 SSL_CERT_DIR 環境變數的邏輯，並新增事件來源方法以提供更精確的訊息。主要變更包括：檢查現有 SSL_CERT_DIR 是否已包含憑證目錄、新增兩個事件方法、調整事件監聽器的啟用方式，以及將 NssDb 類別改為傳統建構函式。整體而言，變更方向合理，但存在一些潛在問題：路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能不正確、事件監聽器在非 verbose 模式下啟用 LogAlways 可能導致過多輸出、以及 NssDb 類別的改寫違反了專案規範 R11（應使用 primary constructor）。建議修正這些問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判 | 0.80 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:994` | [R11] NssDb 類別應使用 primary constructor 而非傳統建構函式 | 0.90 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 可能導致過多輸出 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判</summary>

在檢查 SSL_CERT_DIR 是否已包含憑證目錄時，使用 `StringComparison.OrdinalIgnoreCase` 進行路徑比較。在 Linux 上，檔案路徑是區分大小寫的，因此若 SSL_CERT_DIR 中包含大小寫不同的相同路徑（例如 `/home/user/.dotnet/corefx/cryptography/x509stores/my` 與 `/home/user/.dotnet/corefx/cryptography/x509stores/My`），此比較會錯誤地視為相同，導致程式誤判憑證目錄已存在，而略過必要的設定。建議改用 `StringComparison.Ordinal` 以符合 Unix 檔案系統的語意。

**判斷依據**：diff 中新增的程式碼片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:994</code> [R11] NssDb 類別應使用 primary constructor 而非傳統建構函式</summary>

此變更將原本使用 primary constructor 的 `NssDb` 類別改為傳統建構函式，違反了專案規範 R11（Use Primary Constructor Syntax Where Appropriate）。該類別僅有簡單的參數指派，符合 primary constructor 的使用情境。建議改回 primary constructor 寫法以維持一致性。

**判斷依據**：diff 中將原本的 `private sealed class NssDb(string path, bool isFirefox)` 改為傳統建構函式寫法。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 可能導致過多輸出</summary>

原本只有在 verbose 模式下才啟用事件監聽器，現在改為非 verbose 模式下也啟用，且等級為 `EventLevel.LogAlways`。這可能導致在一般使用情境下輸出過多訊息，影響使用者體驗。建議確認這些 LogAlways 事件是否真的需要在非 verbose 模式下顯示，或考慮使用較低的等級（如 Informational）。

**判斷依據**：diff 中新增的程式碼片段：`listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways);`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5645 (cache hit 5632) ｜ completion tokens 1013 ｜ PR #3</sub>