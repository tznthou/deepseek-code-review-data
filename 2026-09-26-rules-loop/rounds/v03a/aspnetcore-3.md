<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要修改 dotnet-dev-certs 工具在 Unix 上處理 SSL_CERT_DIR 環境變數的邏輯，新增檢查是否已包含憑證目錄，並調整事件來源訊息與事件監聽器設定。整體方向合理，但存在幾個問題：事件監聽器在非 verbose 模式下使用 LogAlways 等級，可能導致過多輸出；新增的檢查邏輯中，路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確；此外，NssDb 類別從主要建構函式改為傳統建構函式，違反專案規範 R11。建議修正這些問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 可能導致過多輸出 | 0.80 |
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | Unix 路徑比較使用 OrdinalIgnoreCase 可能不正確 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:994` | [R11] NssDb 類別未使用主要建構函式 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 可能導致過多輸出</summary>

在非 verbose 模式下，程式碼將事件監聽器設定為 `EventLevel.LogAlways`，這會導致所有標記為 LogAlways 的事件（包括資訊性訊息）都被輸出。原本的設計是僅在 verbose 模式下才顯示這些訊息（如 diff 中移除的註解所述）。這可能造成使用者執行一般命令時看到不必要的輸出，影響使用者體驗。建議改為僅在 verbose 模式下啟用事件監聽器，或使用更嚴格的等級（如 Warning）。

**判斷依據**：diff 中新增的 else 區塊：`else { listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); }`，且移除了原本的註解「Note that dotnet-dev-certs won't display any of these, regardless of level, unless --verbose is passed.」

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> Unix 路徑比較使用 OrdinalIgnoreCase 可能不正確</summary>

在檢查 SSL_CERT_DIR 是否已包含憑證目錄時，程式碼使用 `StringComparison.OrdinalIgnoreCase` 進行路徑比較。然而，Unix 檔案系統是區分大小寫的，使用忽略大小寫的比較可能導致誤判（例如將 `/path/MyCerts` 視為等同於 `/path/mycerts`）。這可能導致工具錯誤地認為憑證目錄已存在，而實際上並未包含。建議改用 `StringComparison.Ordinal` 進行比較。

**判斷依據**：diff 中新增的程式碼：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:994</code> [R11] NssDb 類別未使用主要建構函式</summary>

NssDb 類別原本使用 C# 12 的主要建構函式（primary constructor）語法，但此 PR 將其改為傳統的建構函式與欄位指派。這違反了專案規範 R11（Use Primary Constructor Syntax Where Appropriate），因為此類別符合簡單的建構函式到欄位指派模式。建議改回主要建構函式語法。

**判斷依據**：diff 中將原本的 `private sealed class NssDb(string path, bool isFirefox)` 改為傳統建構函式，違反 R11。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5655 (cache hit 3456) ｜ completion tokens 1023 ｜ PR #3</sub>