<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要改進 Unix 憑證信任流程：檢查 SSL_CERT_DIR 是否已包含憑證目錄，並調整事件來源訊息與監聽器設定。主要風險在於路徑比較邏輯可能因大小寫或符號連結而誤判，以及事件監聽器在非 verbose 模式下可能導致過多輸出。建議修正路徑比較方式並確認事件層級設定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能誤判 | 0.80 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 事件可能導致過多輸出 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | catch 區塊過於寬鬆，可能隱藏非預期的例外 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能誤判</summary>

在 Linux 檔案系統中，路徑是區分大小寫的。使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能導致錯誤判斷憑證目錄已存在於 SSL_CERT_DIR 中，但實際上因大小寫不同而未被包含。建議改用 `StringComparison.Ordinal` 或 `StringComparison.Ordinal` 搭配 `Path.GetFullPath` 的標準化結果。

**判斷依據**：diff 中新增的程式碼使用 `StringComparison.OrdinalIgnoreCase` 進行路徑比較，但 Linux 路徑區分大小寫，可能導致誤判。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 事件可能導致過多輸出</summary>

在非 verbose 模式下，`listener.EnableEvents(CertificateManager.Log, EventLevel.LogAlways)` 會啟用所有 LogAlways 等級的事件，可能導致不必要的輸出。建議確認是否有需要僅在 verbose 模式下顯示的事件，或調整事件等級。

**判斷依據**：diff 中新增的 else 區塊使用 LogAlways 等級，可能輸出過多資訊。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> catch 區塊過於寬鬆，可能隱藏非預期的例外</summary>

`catch` 區塊捕獲所有例外並忽略，可能隱藏非預期的錯誤（例如權限不足或 I/O 錯誤）。建議至少記錄例外或僅捕獲預期的例外類型（如 `IOException`、`UnauthorizedAccessException`）。

**判斷依據**：diff 中新增的 catch 區塊未指定例外類型，且未記錄任何資訊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5645 (cache hit 5632) ｜ completion tokens 741 ｜ PR #3</sub>