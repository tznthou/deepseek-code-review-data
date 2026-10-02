<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在移除 QR code 相關功能，包含快捷動作、路由、工具列按鈕、遙測與測試。整體移除範圍完整，但其中混入了三處與 QR code 無關的邏輯變更，可能引入回歸。最需要優先確認的是 BrowserViewControllerState.swift 中 displayView 的變更，以及 ToolbarMiddleware.swift 中兩處布林邏輯的反轉，這些變更缺乏測試且可能影響現有功能。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | [R02] 錯誤的 displayView 變更可能導致錯誤的畫面顯示 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | [R02] 布林邏輯反轉可能導致取消編輯時 URL 處理錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | [R02] 布林邏輯反轉可能導致 Reader Mode 遙測事件錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] gleanWrapper 屬性存取控制從 private 改為 internal | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> [R02] 錯誤的 displayView 變更可能導致錯誤的畫面顯示</summary>

此變更將 `displayView` 從 `.readerMode` 改為 `.readerModeLongPressAction`，但該方法（`handleShowReaderModeAction`）的意圖是顯示 Reader Mode，而非長按動作。這可能導致使用者點擊 Reader Mode 按鈕時，畫面顯示錯誤的視圖。建議確認此變更是否為誤植，若非誤植則需補充說明與測試。

**判斷依據**：diff 中此行由 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`，且該方法名稱與上下文均指向 Reader Mode 顯示。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> [R02] 布林邏輯反轉可能導致取消編輯時 URL 處理錯誤</summary>

原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會使得當 URL 是 Reader Mode 頁面時，`url` 不會被設為 nil，可能導致取消編輯後工具列仍顯示 Reader Mode URL，或影響後續行為。請確認此變更的意圖，並補充測試。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，邏輯完全相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> [R02] 布林邏輯反轉可能導致 Reader Mode 遙測事件錯誤</summary>

原本 `case .available: true` 改為 `false`，`default: false` 改為 `true`。這會使得當 Reader Mode 狀態為 `.available` 時，遙測事件記錄為未啟用，反之亦然。這可能導致遙測數據不準確，影響產品決策。請確認此變更的意圖，並補充測試。

**判斷依據**：diff 中兩行布林值被反轉。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] gleanWrapper 屬性存取控制從 private 改為 internal</summary>

`gleanWrapper` 屬性從 `private let` 改為 `let`（internal），這擴大了其可見性。若無外部使用需求，建議維持 `private` 以遵循最小權限原則。

**判斷依據**：diff 中此行由 `private let gleanWrapper: GleanWrapper` 改為 `let gleanWrapper: GleanWrapper`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10374 (cache hit 8320) ｜ completion tokens 1027 ｜ PR #9</sub>