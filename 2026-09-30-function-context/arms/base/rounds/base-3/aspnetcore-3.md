<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要修正 dotnet-dev-certs 在 Unix 上對 SSL_CERT_DIR 的處理：當環境變數已存在時，檢查是否已包含憑證目錄，並提供更精確的建議訊息；同時調整事件監聽器以確保 LogAlways 等級的訊息總會顯示。整體方向合理，但存在一些潛在問題：路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能不正確、例外處理過於寬鬆、以及事件監聽器在非 verbose 模式下可能導致過多輸出。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判 | 0.80 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:378` | 過度寬泛的例外處理可能隱藏真實錯誤 | 0.60 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 可能導致過多輸出 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判</summary>

在 Linux 上，檔案路徑是區分大小寫的。使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能將不同目錄視為相同（例如 `/Certs` 與 `/certs`），導致錯誤地認為憑證目錄已存在於 SSL_CERT_DIR 中，進而跳過必要的設定。建議在 Unix 平台上使用 `StringComparison.Ordinal`，或根據作業系統動態選擇比較方式。

**判斷依據**：diff 中新增的程式碼使用了 `StringComparison.OrdinalIgnoreCase`，而此程式碼位於 Unix 專用的 `UnixCertificateManager.cs` 中。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:378</code> 過度寬泛的例外處理可能隱藏真實錯誤</summary>

在解析 SSL_CERT_DIR 中的每個目錄時，使用 `catch` 捕捉所有例外並忽略，可能掩蓋了非預期的錯誤（例如 `Path.GetFullPath` 因權限不足或路徑格式錯誤而拋出的例外）。建議至少記錄例外資訊，或僅捕捉預期的例外類型（如 `ArgumentException`、`NotSupportedException`、`PathTooLongException`）。

**判斷依據**：diff 中新增的 catch 區塊沒有指定例外類型，且註解表示忽略所有例外。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 可能導致過多輸出</summary>

在非 verbose 模式下，將事件監聽器設為 `EventLevel.LogAlways` 會顯示所有 LogAlways 等級的事件。這可能包括原本設計為僅在 verbose 模式顯示的訊息，導致輸出過於冗長。建議確認所有 LogAlways 事件是否都適合在一般模式下顯示，或考慮使用更精確的過濾。

**判斷依據**：diff 中新增了 else 分支，在非 verbose 模式下啟用 LogAlways 等級的事件監聽。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3460 (cache hit 3456) ｜ completion tokens 838 ｜ PR #3</sub>