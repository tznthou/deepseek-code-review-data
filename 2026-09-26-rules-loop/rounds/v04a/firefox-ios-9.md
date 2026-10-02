<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在移除 QR code 相關功能，包含快捷動作、路由、狀態管理、遙測與測試。整體移除範圍完整，但包含兩處與 QR code 無關的邏輯變更，可能引入回歸。最需要優先確認的是 ToolbarMiddleware 中 cancelEditMode 與 readerModeState 的條件反轉，以及 BrowserViewControllerState 中 displayView 的變更。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件反轉可能導致 URL 遺失 | 0.90 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 條件反轉可能導致遙測錯誤 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 變更可能導致錯誤畫面顯示 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] gleanWrapper 屬性存取控制變更 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件反轉可能導致 URL 遺失</summary>

原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓非網頁但為 Reader Mode 的 URL（例如 `about:reader?url=...`）也被保留，而原本應被清除。這可能導致取消編輯時 URL 欄顯示錯誤內容。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，邏輯完全相反。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 條件反轉可能導致遙測錯誤</summary>

原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會使遙測事件中的 `isEnabled` 值完全相反，影響數據準確性。

**判斷依據**：diff 中兩行條件值互換。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 變更可能導致錯誤畫面顯示</summary>

原本 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`。此變更與 QR code 移除無關，可能影響長按閱讀模式按鈕時顯示的畫面，需確認是否為預期行為。

**判斷依據**：diff 中此行由 `.readerMode` 改為 `.readerModeLongPressAction`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] gleanWrapper 屬性存取控制變更</summary>

`gleanWrapper` 從 `private let` 改為 `let`（internal）。若無外部使用需求，建議維持 `private` 以符合資訊隱藏原則。

**判斷依據**：diff 中此行由 `private let` 改為 `let`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9210 (cache hit 8320) ｜ completion tokens 876 ｜ PR #9</sub>