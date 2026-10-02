<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除 QR code 相關功能，包含快捷動作、路由、工具列按鈕、遙測與測試。整體移除範圍完整，但其中混入了三處與 QR code 無關的邏輯變更，可能造成行為回歸，需要特別確認。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 從 .readerMode 改為 .readerModeLongPressAction 可能造成錯誤畫面顯示 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 中的 URL 判斷邏輯反轉，可能導致編輯模式取消時 URL 遺失 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | isReaderModeEnabled 的布林值反轉，可能導致遙測記錄錯誤 | 0.90 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | gleanWrapper 屬性從 private 改為 internal，可能破壞封裝 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 從 .readerMode 改為 .readerModeLongPressAction 可能造成錯誤畫面顯示</summary>

在 `handleShowReaderModeLongPressAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這可能導致長按閱讀模式按鈕時顯示錯誤的畫面，或造成狀態不一致。請確認此變更是否為筆誤，若不是，請提供對應的測試與說明。

**判斷依據**：diff 中該行由 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`，且此變更與 QR code 移除無關。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 中的 URL 判斷邏輯反轉，可能導致編輯模式取消時 URL 遺失</summary>

原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓非網頁 URL（例如 about:blank）或閱讀模式 URL 也被保留，可能導致取消編輯時工具列顯示錯誤的 URL。請確認此變更的意圖，並補充測試。

**判斷依據**：diff 中該行由 `&& !` 改為 `||`，邏輯完全相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> isReaderModeEnabled 的布林值反轉，可能導致遙測記錄錯誤</summary>

原本 `case .available: true`、`default: false`，現在改為 `case .available: false`、`default: true`。這會讓閱讀模式按鈕的遙測事件記錄錯誤的啟用狀態。請確認此變更是否為筆誤，若不是，請提供對應的測試與說明。

**判斷依據**：diff 中布林值被反轉，且註解未更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> gleanWrapper 屬性從 private 改為 internal，可能破壞封裝</summary>

將 `private let gleanWrapper` 改為 `let gleanWrapper` 會讓外部可以存取此屬性，可能不是必要的變更。如果只是為了測試，建議使用其他方式（例如依賴注入或測試專用的 init）。

**判斷依據**：diff 中移除了 `private` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8363 (cache hit 1536) ｜ completion tokens 958 ｜ PR #9</sub>