<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除 QR code 相關功能，包括快捷動作、路由、工具列按鈕、遙測事件與測試。整體移除範圍完整，但包含兩處與 QR code 無關的邏輯變更：`BrowserViewControllerState.swift` 中 displayView 從 `.readerMode` 改為 `.readerModeLongPressAction`，以及 `ToolbarMiddleware.swift` 中布林條件與 reader mode 狀態的變更。這些變更缺乏說明，且可能引入行為差異，建議分離或補充說明。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 從 .readerMode 改為 .readerModeLongPressAction 可能導致錯誤的畫面顯示 | 0.90 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 中的 URL 條件邏輯反轉可能導致編輯取消時 URL 遺失 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | reader mode 狀態的布林值反轉可能導致遙測記錄錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] gleanWrapper 屬性從 private 改為 internal 可能違反封裝原則 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 從 .readerMode 改為 .readerModeLongPressAction 可能導致錯誤的畫面顯示</summary>

在 `handleShowReaderModeAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這會導致當使用者點擊 reader mode 按鈕時，顯示的畫面變成 long press action 的畫面，而非 reader mode 畫面。

**失敗情境**：使用者點擊網址列的 reader mode 按鈕，預期進入 reader mode，但實際會顯示 long press action 的選單或畫面，造成功能錯誤。

**建議**：確認此變更是否為筆誤，應保留 `.readerMode`。

**判斷依據**：diff 中該行由 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`，且此變更與 QR code 移除無關。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 中的 URL 條件邏輯反轉可能導致編輯取消時 URL 遺失</summary>

在 `cancelEditMode` 方法中，原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，但此 PR 將其改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會導致當 URL 是 reader mode URL 或不是網頁時，仍會保留 URL，可能造成取消編輯後網址列顯示錯誤的 URL。

**失敗情境**：使用者在 reader mode 下編輯網址列，然後取消編輯，網址列可能顯示 reader mode 的 URL 而非原始網頁 URL。

**建議**：確認此變更是否為筆誤，應保留原始邏輯。

**判斷依據**：diff 中該行由 `url = (currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil` 改為 `url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`，且此變更與 QR code 移除無關。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> reader mode 狀態的布林值反轉可能導致遙測記錄錯誤</summary>

在 `readerModeButtonTapped` 相關的遙測記錄中，原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會導致當 reader mode 可用時，記錄的 `isEnabled` 為 false，反之亦然，造成遙測數據不正確。

**失敗情境**：使用者點擊 reader mode 按鈕，遙測記錄的 `isEnabled` 值與實際狀態相反，影響數據分析。

**建議**：確認此變更是否為筆誤，應保留原始邏輯。

**判斷依據**：diff 中該 switch 的兩個 case 回傳值被互換，且此變更與 QR code 移除無關。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] gleanWrapper 屬性從 private 改為 internal 可能違反封裝原則</summary>

`gleanWrapper` 屬性原本為 `private`，此 PR 將其改為 `let`（internal）。這會讓外部程式碼可以直接存取此屬性，違反資訊隱藏原則。

**建議**：除非有明確需求，否則應保留 `private`。

**判斷依據**：diff 中該行由 `private let gleanWrapper: GleanWrapper` 改為 `let gleanWrapper: GleanWrapper`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10422 (cache hit 1536) ｜ completion tokens 1293 ｜ PR #9</sub>