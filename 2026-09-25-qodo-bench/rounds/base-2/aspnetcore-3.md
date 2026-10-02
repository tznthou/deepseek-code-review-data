<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 調整了 Unix 憑證信任流程：當 SSL_CERT_DIR 已包含目標目錄時不再回報失敗，並新增對應事件與訊息；同時將事件監聽器移至條件外，確保 LogAlways 事件在非 verbose 模式下也能輸出。主要風險在於路徑比較邏輯可能因符號連結或大小寫敏感檔案系統而誤判，以及事件監聽器生命週期變更可能影響其他輸出。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | SSL_CERT_DIR 路徑比較可能因符號連結或大小寫敏感檔案系統而誤判 | 0.80 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:379` | catch 區塊過於寬鬆，可能隱藏非預期錯誤 | 0.70 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:127` | 事件監聽器生命週期變更可能影響其他輸出 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> SSL_CERT_DIR 路徑比較可能因符號連結或大小寫敏感檔案系統而誤判</summary>

使用 `Path.GetFullPath` 進行字串比較，但未解析符號連結。若 `SSL_CERT_DIR` 中的路徑包含符號連結，或檔案系統大小寫敏感（如 Linux），可能導致已包含的目錄被誤判為未包含，進而錯誤地設定 `sawTrustFailure = true`。建議使用 `Path.GetFullPath` 後再以 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `LinkTarget` 來處理符號連結，或改用 `Path.TrimEndingDirectorySeparator` 後進行 Ordinal 比較（Linux 上大小寫敏感）。

**判斷依據**：diff 中新增的 `isCertDirIncluded` 判斷使用 `StringComparison.OrdinalIgnoreCase`，在 Linux 上大小寫敏感，且未解析符號連結。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:379</code> catch 區塊過於寬鬆，可能隱藏非預期錯誤</summary>

`catch` 區塊捕獲所有例外並回傳 false，可能隱藏非預期的錯誤（如 `Path.GetFullPath` 因權限不足拋出 `SecurityException`）。建議至少記錄例外或僅捕獲預期的例外類型（如 `ArgumentException`、`NotSupportedException`）。

**判斷依據**：diff 中新增的 catch 區塊未指定例外類型，且未記錄任何資訊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:127</code> 事件監聽器生命週期變更可能影響其他輸出</summary>

將 `ReporterEventListener` 的建立移至條件外，並在非 verbose 模式下啟用 `LogAlways` 等級。這可能導致原本僅在 verbose 模式下輸出的 `LogAlways` 事件（如 `UnixSuggestSettingEnvironmentVariable`）現在也會在一般模式輸出，可能造成非預期的輸出變化。建議確認所有 `LogAlways` 事件是否都適合在非 verbose 模式顯示。

**判斷依據**：diff 中將 listener 建立移至條件外，並新增 else 分支啟用 LogAlways。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3460 (cache hit 3456) ｜ completion tokens 904 ｜ PR #3</sub>