<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要修正 dotnet-dev-certs 在 Unix 上對 SSL_CERT_DIR 環境變數的處理：當變數已存在時，檢查是否已包含憑證目錄，並提供更精確的訊息。整體邏輯合理，但存在一些潛在問題：路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能不正確；例外處理過於寬鬆可能隱藏錯誤；新增事件方法缺少 XML 文件註解（違反 R07）；以及 NssDb 類別改寫可能違反 R11（應使用 primary constructor）。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判 | 0.80 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1314` | [R07] 新增的 public 事件方法缺少 XML 文件註解 | 0.90 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 過於寬泛的例外處理可能隱藏錯誤 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:994` | [R11] NssDb 類別應使用 primary constructor | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判</summary>

在 Linux 上檔案路徑是區分大小寫的，使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能錯誤地認為兩個不同大小寫的目錄是相同的。例如 `/home/user/.dotnet/corefx/cryptography/x509stores/my` 和 `/home/user/.dotnet/corefx/cryptography/x509stores/My` 會被視為相同，但實際上是不同目錄。建議使用 `StringComparison.Ordinal`（或 `StringComparison.OrdinalIgnoreCase` 僅在 Windows 上）。

**判斷依據**：diff 中新增的這一行使用了 OrdinalIgnoreCase，而此程式碼在 Unix 平台上執行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1314</code> [R07] 新增的 public 事件方法缺少 XML 文件註解</summary>

新增的 `UnixOpenSslCertificateDirectoryAlreadyConfigured` 和 `UnixSuggestAppendingToEnvironmentVariable` 是 public 方法，但沒有 XML 文件註解。根據規範 R07，所有 public API 都應該有 XML 文件註解。

**判斷依據**：diff 中新增的這兩個方法沒有 XML 文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 過於寬泛的例外處理可能隱藏錯誤</summary>

在解析 SSL_CERT_DIR 中的每個目錄時，使用 `catch` 捕獲所有例外並忽略。這可能隱藏了非預期的錯誤，例如 `Path.GetFullPath` 可能拋出的 `ArgumentException`、`NotSupportedException`、`PathTooLongException` 等。建議至少記錄這些例外，或僅捕獲預期的例外類型。

**判斷依據**：diff 中新增的 catch 區塊沒有指定例外類型，且註解表明忽略所有例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:994</code> [R11] NssDb 類別應使用 primary constructor</summary>

NssDb 類別從 primary constructor 改為傳統建構函式，但根據規範 R11，簡單的依賴注入場景應使用 primary constructor。此類別只有兩個唯讀屬性，適合使用 primary constructor。

**判斷依據**：diff 中將原本的 primary constructor 改為傳統建構函式，違反 R11。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4410 (cache hit 4352) ｜ completion tokens 1116 ｜ PR #3</sub>