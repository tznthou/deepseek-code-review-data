<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 Unix 憑證信任流程，使其在 SSL_CERT_DIR 已設定時能正確偵測並提供建議，同時調整事件來源訊息與事件監聽器設定。主要風險在於路徑比較邏輯可能因符號連結或相對路徑而誤判，以及事件監聽器在非 verbose 模式下可能遺漏 LogAlways 事件。建議先修正路徑正規化與事件監聽器設定。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較未解析符號連結可能導致誤判 | 0.80 |
| ⚠️ | Major | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下可能遺漏 LogAlways 事件 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較忽略大小寫可能不適用於所有 Unix 檔案系統 | 0.60 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1320` | 事件訊息中的環境變數名稱未正確引用 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較未解析符號連結可能導致誤判</summary>

在比較 `existingSslCertDir` 中的目錄與 `certDirFullPath` 時，使用 `Path.GetFullPath` 進行正規化，但未解析符號連結。若 `SSL_CERT_DIR` 中的路徑包含符號連結，或 `certDir` 本身是符號連結，可能導致路徑字串不同而誤判為未包含，進而重複建議設定環境變數。建議使用 `Path.GetFullPath` 後再透過 `FileSystemInfo.ResolveLinkTarget` 或 `Path.GetFullPath(new DirectoryInfo(path).FullName)` 等方式解析符號連結，或改用 `Path.GetRelativePath` 比較。

**判斷依據**：diff 中新增的 `isCertDirIncluded` 判斷使用 `Path.GetFullPath` 比較路徑，未處理符號連結。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下可能遺漏 LogAlways 事件</summary>

在非 verbose 模式下，事件監聽器僅啟用 `EventLevel.LogAlways`，但 `CertificateManager.Log` 的事件來源可能使用 `EventLevel.Informational` 或更低等級的事件。若這些事件未標記為 `LogAlways`，則不會被輸出，導致使用者看不到重要訊息。建議確認所有需要顯示的事件等級均為 `LogAlways`，或改為啟用 `EventLevel.Informational`。

**判斷依據**：diff 中新增的 else 分支僅啟用 LogAlways 等級。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較忽略大小寫可能不適用於所有 Unix 檔案系統</summary>

使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，但 Unix 檔案系統通常區分大小寫。若 `SSL_CERT_DIR` 中的路徑大小寫與實際目錄不同，可能誤判為已包含。建議使用 `StringComparison.Ordinal` 以符合 Unix 慣例。

**判斷依據**：diff 中新增的比較使用 `OrdinalIgnoreCase`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1320</code> 事件訊息中的環境變數名稱未正確引用</summary>

在 `UnixSuggestAppendingToEnvironmentVariable` 事件中，訊息範例使用 `export {1}="{0}:${1}"`，但 `{1}` 是環境變數名稱，若名稱包含特殊字元（如空格），可能導致 shell 指令錯誤。建議使用單引號或跳脫。

**判斷依據**：diff 中新增的事件方法，其 Message 屬性包含 `export {1}="{0}:${1}"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5635 (cache hit 5632) ｜ completion tokens 1050 ｜ PR #3</sub>