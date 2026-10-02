<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修改了 Unix 憑證信任流程，新增對 SSL_CERT_DIR 已存在時的檢查與對應事件，並調整事件監聽器以在非 verbose 模式下仍顯示 LogAlways 訊息。主要風險在於路徑比較邏輯可能因大小寫敏感或符號連結而誤判，以及事件監聽器在非 verbose 模式下可能收到過多訊息。整體方向合理，但需修正比較邏輯並考慮監聽器效能。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能誤判 | 0.80 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下監聽 LogAlways 可能導致過多輸出 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較未解析符號連結，可能導致重複加入 | 0.60 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/CertificateManager.cs:1315` | 新增事件未遵循既有命名模式 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能誤判</summary>

在 Linux 上檔案路徑是大小寫敏感的，使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能導致將不同目錄視為相同，或反之。例如 `/Certs` 與 `/certs` 會被視為相同，但實際上是不同目錄。建議改用 `StringComparison.Ordinal`（或 `StringComparison.OrdinalIgnoreCase` 僅在 Windows 上使用）。

**判斷依據**：diff 中新增的這行使用了 OrdinalIgnoreCase，而此程式碼執行於 Unix 環境（檔案路徑大小寫敏感）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下監聽 LogAlways 可能導致過多輸出</summary>

在非 verbose 模式下啟用 `EventLevel.LogAlways` 會讓所有 LogAlways 事件都輸出，可能包含大量訊息，影響效能與使用者體驗。建議確認 LogAlways 事件的數量與內容是否適合在一般模式顯示，或考慮使用更精確的過濾。

**判斷依據**：diff 中新增的 else 分支啟用了 LogAlways 等級。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較未解析符號連結，可能導致重複加入</summary>

若 SSL_CERT_DIR 中的目錄是符號連結指向 certDir，`Path.GetFullPath` 不會解析符號連結，因此比較會失敗，導致重複建議加入。建議使用 `Path.GetFullPath` 後再透過 `FileInfo.ResolveLinkTarget` 或 `realpath` 解析真實路徑。

**判斷依據**：程式碼僅使用 Path.GetFullPath，未處理符號連結。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1315</code> 新增事件未遵循既有命名模式</summary>

新增的事件方法名稱 `UnixOpenSslCertificateDirectoryAlreadyConfigured` 與 `UnixSuggestAppendingToEnvironmentVariable` 與既有事件命名風格（如 `UnixSuggestSettingEnvironmentVariable`）略有差異，但尚可接受。

**判斷依據**：diff 中新增的事件方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4410 (cache hit 3456) ｜ completion tokens 932 ｜ PR #3</sub>