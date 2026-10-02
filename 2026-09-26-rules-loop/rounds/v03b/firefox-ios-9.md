<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除 QR code 掃描功能相關程式碼，包含快捷鍵、路由、Redux 狀態、Telemetry 與測試。整體移除範圍完整，但其中包含三處與 QR code 無關的邏輯變更，可能為誤植或意外修改，需特別確認。此外，移除功能後可能殘留未使用的程式碼或設定，建議一併清理。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 值從 .readerMode 改為 .readerModeLongPressAction，與 QR code 移除無關 | 0.95 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | 布林條件從 && 改為 \|\|，可能改變取消編輯時 URL 的處理邏輯 | 0.95 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | isReaderModeEnabled 的布林值反轉，可能導致 telemetry 記錄錯誤 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | gleanWrapper 屬性從 private 改為 internal，可能違反封裝原則 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Configuration/version.xcconfig:1` | APP_VERSION 從 147.1 升為 147.2，與 QR code 移除無關 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 值從 .readerMode 改為 .readerModeLongPressAction，與 QR code 移除無關</summary>

此變更將 `displayView` 從 `.readerMode` 改為 `.readerModeLongPressAction`，但此 PR 目的為移除 QR code 相關程式碼，此變更與目的無關。若為誤植，可能導致 reader mode 顯示錯誤；若為有意修改，應在 PR 描述中說明。

**判斷依據**：diff 中此行由 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`，且前後文皆為 QR code 移除，無相關性。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> 布林條件從 && 改為 ||，可能改變取消編輯時 URL 的處理邏輯</summary>

此變更將 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)` 改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`，與 QR code 移除無關。此邏輯變更可能影響取消編輯時 URL 的保留與否，進而影響使用者體驗。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，且前後文皆為 QR code 移除，無相關性。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> isReaderModeEnabled 的布林值反轉，可能導致 telemetry 記錄錯誤</summary>

此變更將 `case .available: true` 改為 `false`，`default: false` 改為 `true`，與 QR code 移除無關。此變更可能導致 reader mode 按鈕的 telemetry 記錄錯誤，影響數據分析。

**判斷依據**：diff 中此兩行由 `true` 改為 `false`、`false` 改為 `true`，且前後文皆為 QR code 移除，無相關性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> gleanWrapper 屬性從 private 改為 internal，可能違反封裝原則</summary>

此變更將 `private let gleanWrapper` 改為 `let gleanWrapper`，使其成為 internal，可能違反 [R11] 的封裝原則。若無外部使用需求，應保持 private。

**判斷依據**：diff 中此行由 `private let gleanWrapper` 改為 `let gleanWrapper`，且無其他程式碼使用此屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Configuration/version.xcconfig:1</code> APP_VERSION 從 147.1 升為 147.2，與 QR code 移除無關</summary>

此變更將版本號從 147.1 改為 147.2，但 PR 目的為移除 QR code 功能，版本號變更可能為誤植或應在獨立 PR 中處理。

**判斷依據**：diff 中此行由 `147.1` 改為 `147.2`，且無其他版本相關變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10432 (cache hit 10368) ｜ completion tokens 1188 ｜ PR #9</sub>