<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了 QR code 掃描功能相關的程式碼，包括快捷動作、路由、Redux 狀態、Telemetry 與測試。整體移除範圍完整，但其中包含兩處與 QR code 無關的邏輯變更，可能引入回歸風險，需特別確認。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | 錯誤的 displayView 指派：應為 .readerMode 而非 .readerModeLongPressAction | 0.95 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | 取消編輯模式的 URL 判斷邏輯反轉，可能導致網址列內容錯誤 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | Reader Mode 按鈕啟用狀態的判斷邏輯反轉，可能導致 Telemetry 回報錯誤 | 0.85 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] `gleanWrapper` 屬性從 `private` 改為 `internal`，可能違反封裝原則 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> 錯誤的 displayView 指派：應為 .readerMode 而非 .readerModeLongPressAction</summary>

在 `handleShowReaderModeAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這會導致當使用者點擊網址列的 Reader Mode 按鈕時，畫面顯示錯誤的視圖（長按選單而非 Reader Mode 內容），造成功能失效。

**失敗情境**：使用者瀏覽支援 Reader Mode 的網頁，點擊網址列的 Reader Mode 圖示，預期進入閱讀模式，但實際會顯示長按動作選單。

**建議修法**：將該行改回 `displayView: .readerMode`。

**判斷依據**：diff 中此行由 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`，且該函式為 `handleShowReaderModeAction`，應對應 `.readerMode`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> 取消編輯模式的 URL 判斷邏輯反轉，可能導致網址列內容錯誤</summary>

在 `cancelEditMode` 中，原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil`，意即只有當 URL 是網頁且不是 Reader Mode URL 時才保留 URL。此 PR 將其改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`，邏輯完全相反。

**失敗情境**：當使用者在編輯網址列時，若目前頁面是 Reader Mode，原本會清空網址列（因為 Reader Mode URL 不應顯示），但修改後會保留 Reader Mode URL，導致網址列顯示不正確的 URL。反之，若目前頁面不是網頁（例如 about:blank），原本會清空，但修改後會保留該 URL，可能造成非預期的網址顯示。

**建議修法**：恢復原本的邏輯 `(currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil`。

**判斷依據**：diff 中此行由 `url = (currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil` 改為 `url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`，邏輯運算子與否定條件均被修改。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> Reader Mode 按鈕啟用狀態的判斷邏輯反轉，可能導致 Telemetry 回報錯誤</summary>

在 `readerModeButtonTapped` 的 Telemetry 記錄中，原本的 `isReaderModeEnabled` 判斷為：當 `readerModeState` 為 `.available` 時為 `true`（表示按鈕將被啟用），其他狀態為 `false`。此 PR 將其改為 `.available` 時為 `false`，其他狀態為 `true`，邏輯完全相反。

**失敗情境**：當 Reader Mode 可用時，使用者點擊按鈕，Telemetry 會記錄 `isEnabled: false`，但實際上按鈕是啟用的，導致資料錯誤。反之，當 Reader Mode 不可用時，會記錄 `isEnabled: true`。

**建議修法**：恢復原本的邏輯：`case .available: true; default: false`。

**判斷依據**：diff 中此段由 `case .available: true // will be enabled after action gets executed` 和 `default: false` 改為 `case .available: false` 和 `default: true`，註解仍保留但邏輯已反轉。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] `gleanWrapper` 屬性從 `private` 改為 `internal`，可能違反封裝原則</summary>

`gleanWrapper` 屬性原本為 `private let`，此 PR 將其改為 `let`（預設為 internal）。這使得該屬性在模組內可被外部存取，違反了最小權限原則。

**建議修法**：若無外部使用需求，應恢復為 `private let`。

**判斷依據**：diff 中此行由 `private let gleanWrapper: GleanWrapper` 改為 `let gleanWrapper: GleanWrapper`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10422 (cache hit 8320) ｜ completion tokens 1416 ｜ PR #9</sub>