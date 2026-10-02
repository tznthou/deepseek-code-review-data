<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在改善 dotnet-dev-certs 在 Unix 上對 SSL_CERT_DIR 環境變數的處理：當變數已包含憑證目錄時不再重複提示，並調整事件來源的訊息與日誌層級。主要風險在於路徑比較邏輯可能因符號連結或大小寫敏感度而誤判，以及事件監聽器在非 verbose 模式下可能收到過多事件。整體方向合理，但需修正路徑正規化與事件過濾。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:365` | 路徑比較未解析符號連結，可能誤判憑證目錄已存在 | 0.80 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較使用 OrdinalIgnoreCase，在 Linux 上可能誤判 | 0.70 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 可能導致過多輸出 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:365</code> 路徑比較未解析符號連結，可能誤判憑證目錄已存在</summary>

在檢查 SSL_CERT_DIR 是否已包含憑證目錄時，使用 `Path.GetFullPath` 進行正規化，但未解析符號連結。若使用者以符號連結路徑加入 SSL_CERT_DIR，而實際憑證目錄路徑不同，則比較會失敗，導致重複提示或誤判為未設定。建議使用 `FileSystemInfo.ResolveLinkTarget` 或 `Path.GetFullPath` 後再解析符號連結，或改用 `Path.GetRelativePath` 比較。

**判斷依據**：diff 中新增的程式碼使用 `Path.GetFullPath` 進行比較，但未處理符號連結。Unix 系統上使用者常以符號連結設定環境變數，可能導致誤判。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較使用 OrdinalIgnoreCase，在 Linux 上可能誤判</summary>

Linux 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，可能將不同大小寫的目錄視為相同，導致誤判。建議在 Unix 上使用 `StringComparison.Ordinal`，或根據作業系統選擇比較方式。

**判斷依據**：diff 中新增的程式碼使用 `OrdinalIgnoreCase`，但 Unix 路徑區分大小寫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 可能導致過多輸出</summary>

在非 verbose 模式下，將事件監聽器設為 `EventLevel.LogAlways`，這會接收所有 LogAlways 層級的事件。若事件來源有大量 LogAlways 事件，可能造成不必要的輸出或效能影響。建議確認 LogAlways 事件的數量與必要性，或考慮使用更精確的過濾。

**判斷依據**：diff 中新增的 else 區塊將事件層級設為 LogAlways，可能導致非 verbose 模式下輸出過多。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3424 (cache hit 3328) ｜ completion tokens 933 ｜ PR #3</sub>