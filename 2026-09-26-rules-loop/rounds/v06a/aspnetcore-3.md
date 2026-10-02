<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要調整 Unix 憑證信任流程：當 SSL_CERT_DIR 已包含目標目錄時不再重複提示，並新增對應事件與訊息；同時將 NssDb 改為傳統建構函式以符合命名慣例。主要風險在於路徑比較邏輯可能因符號連結或大小寫敏感檔案系統而誤判，以及事件監聽器在非 verbose 模式下可能收到過多 LogAlways 事件。建議先修正路徑正規化與事件層級設定。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較未處理符號連結，可能誤判 SSL_CERT_DIR 已包含憑證目錄 | 0.80 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 事件，可能導致過多輸出 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase，在大小寫敏感的 Unix 檔案系統可能誤判 | 0.60 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1314` | 新增事件未使用正確的 EventLevel，可能影響輸出 | 0.50 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:365` | 捕捉所有例外可能隱藏路徑解析錯誤 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較未處理符號連結，可能誤判 SSL_CERT_DIR 已包含憑證目錄</summary>

在檢查 SSL_CERT_DIR 是否已包含憑證目錄時，使用 `Path.GetFullPath` 進行字串比較。若 SSL_CERT_DIR 中的路徑包含符號連結（例如 `/var/run/secrets/ssl` 連結到 `/etc/ssl/certs`），而 `prettyCertDir` 是實際路徑，則 `Path.GetFullPath` 不會解析符號連結，導致比較失敗，誤判為未包含。建議使用 `Path.GetFullPath` 後再透過 `Path.GetRelativePath` 或 `FileSystemInfo.ResolveLinkTarget` 解析符號連結後比較，或改用 `Path.GetFullPath` 搭配 `Path.TrimEndingDirectorySeparator` 並考慮使用 `Path.GetRelativePath` 判斷是否相同。

**判斷依據**：diff 中新增的比較邏輯僅使用 `Path.GetFullPath`，未解析符號連結。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 事件，可能導致過多輸出</summary>

原本僅在 verbose 模式啟用事件監聽，現在非 verbose 模式也啟用 `EventLevel.LogAlways`。這會讓所有 LogAlways 層級的事件（包括新加入的 `UnixSuggestAppendingToEnvironmentVariable`）在一般執行時輸出，可能造成不必要的訊息干擾。建議確認這些 LogAlways 事件是否真的需要在非 verbose 模式顯示，或改用更低的層級（如 Informational）。

**判斷依據**：diff 中新增的 else 分支啟用 LogAlways。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase，在大小寫敏感的 Unix 檔案系統可能誤判</summary>

Unix 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑。若 SSL_CERT_DIR 中包含大小寫不同但指向不同目錄的路徑（例如 `/etc/ssl/certs` 與 `/etc/SSL/Certs`），則可能誤判為相同。建議在 Unix 平台使用 `StringComparison.Ordinal`，或根據作業系統選擇比較方式。

**判斷依據**：diff 中新增的比較邏輯使用 `OrdinalIgnoreCase`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1314</code> 新增事件未使用正確的 EventLevel，可能影響輸出</summary>

新增的 `UnixOpenSslCertificateDirectoryAlreadyConfigured` 事件使用 `EventLevel.Verbose`，但此事件代表「已正確設定」，可能不需要在 verbose 模式才顯示。若使用者未加 `--verbose`，將看不到此確認訊息。建議評估是否應改為 `EventLevel.Informational` 或 `LogAlways`。

**判斷依據**：diff 中新增的事件定義。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:365</code> 捕捉所有例外可能隱藏路徑解析錯誤</summary>

在比較路徑時使用 `catch { return false; }` 捕捉所有例外，包括 `Path.GetFullPath` 可能拋出的 `ArgumentException`、`SecurityException` 等。這可能隱藏潛在的程式錯誤或環境問題。建議至少記錄例外或僅捕捉預期的例外類型（如 `ArgumentException`）。

**判斷依據**：diff 中新增的 catch 區塊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5635 (cache hit 3456) ｜ completion tokens 1307 ｜ PR #3</sub>