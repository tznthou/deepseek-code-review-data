<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要修正 dotnet-dev-certs 在 Unix 上對 SSL_CERT_DIR 環境變數的處理：當變數已存在時，檢查是否已包含憑證目錄，並提供更精確的建議訊息；同時調整事件監聽器，使 LogAlways 等級的事件在非 verbose 模式下也能輸出。整體方向合理，但存在一些正確性與可維護性問題：路徑比較時未正規化尾端分隔符可能導致誤判；事件 ID 113 的訊息格式與參數順序不一致；事件監聽器在非 verbose 模式下可能輸出過多資訊；以及 NssDb 類別改寫為傳統屬性後，未使用自動實作屬性，可能違反專案慣例。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:375` | 路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含 | 0.80 |
| ⚠️ | Major | `src/Shared/CertificateGeneration/CertificateManager.cs:1314` | 事件 113 的訊息格式與參數順序不一致 | 0.75 |
| 🔸 | Minor | `src/Tools/dotnet-dev-certs/src/Program.cs:134` | 非 verbose 模式下啟用 LogAlways 可能輸出過多資訊 | 0.70 |
| 🔸 | Minor | `src/Shared/CertificateGeneration/UnixCertificateManager.cs:994` | NssDb 類別改寫為傳統屬性，可能違反專案慣例 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:375</code> 路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含</summary>

在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

**判斷依據**：diff 中新增的比較邏輯直接使用 `Path.GetFullPath` 的結果進行字串比較，未處理尾端分隔符。

</details>

<details><summary>⚠️ <b>Major</b> — <code>src/Shared/CertificateGeneration/CertificateManager.cs:1314</code> 事件 113 的訊息格式與參數順序不一致</summary>

事件 113 的 Message 為 "The certificate directory '{0}' is already included in the {1} environment variable."，但 `WriteEvent` 的參數順序是 `(certDir, envVarName)`，這與訊息中的佔位符順序相符。然而，事件 114 的 Message 為 "For OpenSSL trust to take effect, '{0}' must be listed in the {1} environment variable. For example, `export {1}=\"{0}:${1}\"`."，其 `WriteEvent` 參數順序也是 `(certDir, envVarName)`，但訊息中第二個佔位符 `{1}` 被用於 `export` 指令的變數名稱，這可能造成混淆。此外，事件 110 的訊息已改為使用 `{2}` 作為環境變數名稱，但事件 114 仍使用 `{1}`，不一致。

**建議**：統一事件訊息中的佔位符順序，並確保與 `WriteEvent` 參數順序一致。

**判斷依據**：diff 中新增的事件定義，事件 114 的訊息格式與事件 110 不一致，且佔位符使用可能造成混淆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Tools/dotnet-dev-certs/src/Program.cs:134</code> 非 verbose 模式下啟用 LogAlways 可能輸出過多資訊</summary>

原本只有在 verbose 模式才會啟用事件監聽器，現在非 verbose 模式也會啟用並設定為 `EventLevel.LogAlways`。這可能導致原本只在 verbose 下顯示的 LogAlways 事件（如事件 110、114）在一般執行時也輸出，造成資訊過載。需確認這是否為預期行為。

**判斷依據**：diff 中新增的 else 區塊，將事件監聽器啟用並設定為 LogAlways。

</details>

<details><summary>🔸 <b>Minor</b> — <code>src/Shared/CertificateGeneration/UnixCertificateManager.cs:994</code> NssDb 類別改寫為傳統屬性，可能違反專案慣例</summary>

原本的 `NssDb` 使用 primary constructor 與自動實作屬性，現在改為傳統的唯讀屬性與建構子。若專案中普遍使用 primary constructor 或自動實作屬性，此改動可能降低一致性。建議確認專案慣例，若無特殊原因，可保留原本寫法。

**判斷依據**：diff 中將原本使用 primary constructor 的類別改為傳統寫法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3460 (cache hit 1536) ｜ completion tokens 1544 ｜ PR #3</sub>