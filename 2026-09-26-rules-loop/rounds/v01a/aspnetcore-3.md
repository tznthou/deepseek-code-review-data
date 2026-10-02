<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 Unix 憑證信任流程，新增檢查 SSL_CERT_DIR 是否已包含憑證目錄的邏輯，並調整事件來源訊息與事件監聽設定。主要風險在於路徑比較邏輯可能因符號連結或大小寫敏感度而誤判，且新增的 LogAlways 事件在非 verbose 模式下可能造成過多輸出。建議先修正路徑正規化與事件層級設定。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較未處理符號連結，可能誤判 SSL_CERT_DIR 已包含憑證目錄 | 0.80 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式啟用 LogAlways 事件，可能輸出過多訊息 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase，在 Linux 上可能誤判 | 0.60 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1315` | 新增事件未遵循既有命名模式 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較未處理符號連結，可能誤判 SSL_CERT_DIR 已包含憑證目錄</summary>

在檢查 SSL_CERT_DIR 是否已包含憑證目錄時，使用 `Path.GetFullPath` 進行正規化，但未解析符號連結。若 SSL_CERT_DIR 中的路徑或 `prettyCertDir` 包含符號連結，可能導致路徑字串不同但實際指向相同目錄，造成誤判為未包含，進而重複輸出建議訊息或錯誤設定 `sawTrustFailure`。建議使用 `Path.GetFullPath` 後再透過 `Path.GetRelativePath` 或比較 `FileSystemInfo.ResolveLinkTarget` 來處理符號連結。

**判斷依據**：diff 中新增的 `isCertDirIncluded` 判斷邏輯使用 `Path.GetFullPath` 比較，未處理符號連結。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式啟用 LogAlways 事件，可能輸出過多訊息</summary>

在非 verbose 模式下，將事件監聽層級設為 `EventLevel.LogAlways`，這會讓所有標記為 `LogAlways` 的事件（包括新加入的 `UnixSuggestAppendingToEnvironmentVariable`）在一般執行時輸出。這可能導致使用者看到不必要的建議訊息，與原本「除非 --verbose 否則不顯示」的設計意圖相違背。建議改為 `EventLevel.Warning` 或僅在需要時啟用特定事件。

**判斷依據**：diff 中新增的 else 分支將事件層級設為 LogAlways，且 CertificateManagerEventSource 中有多個 LogAlways 事件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase，在 Linux 上可能誤判</summary>

Linux 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，可能將不同大小寫的目錄視為相同，導致誤判 SSL_CERT_DIR 已包含憑證目錄。建議在 Unix 平台上使用 `StringComparison.Ordinal`。

**判斷依據**：diff 中新增的比較使用 `OrdinalIgnoreCase`，未考慮平台差異。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1315</code> 新增事件未遵循既有命名模式</summary>

新增的事件方法 `UnixOpenSslCertificateDirectoryAlreadyConfigured` 和 `UnixSuggestAppendingToEnvironmentVariable` 命名與既有事件（如 `UnixSuggestSettingEnvironmentVariable`）不一致，缺少 `Unix` 前綴或動詞形式不統一。建議調整命名以維持一致性。

**判斷依據**：diff 中新增的事件方法命名與既有事件風格不符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5645 (cache hit 3456) ｜ completion tokens 1058 ｜ PR #3</sub>