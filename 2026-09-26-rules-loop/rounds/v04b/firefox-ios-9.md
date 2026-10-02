<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 旨在移除 QR code 相關功能，包含快捷動作、路由、工具列按鈕、遙測與測試。整體移除範圍完整，但包含三處與 QR code 無關的邏輯變更，可能引入回歸：ToolbarMiddleware 中 cancelEditMode 的條件反轉、readerModeState 的布林值反轉，以及 BrowserViewControllerState 中 displayView 的變更。這些變更缺乏測試與說明，風險較高，建議分離或補充驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件反轉可能導致網址列內容被錯誤清除 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 布林值反轉可能導致遙測資料錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 變更可能導致錯誤的畫面顯示 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | gleanWrapper 屬性存取控制放寬可能違反封裝原則 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件反轉可能導致網址列內容被錯誤清除</summary>

原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，修改後變成 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓非網頁但為 Reader Mode 的 URL（例如 `about:reader?url=...`）也被保留，而原本應被清除。若使用者正在編輯網址列且目前頁面為 Reader Mode，取消編輯時網址列可能殘留舊內容，造成顯示錯誤。建議確認此變更意圖，若非必要請還原。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，且無相關測試或說明。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 布林值反轉可能導致遙測資料錯誤</summary>

原本 `case .available: true` 改為 `false`，`default: false` 改為 `true`。這會讓 `isReaderModeEnabled` 的語意完全相反，影響 `readerModeButtonTapped` 遙測事件的正確性。若此變更非預期，應還原；若為修正，需補充測試驗證。

**判斷依據**：diff 中兩行布林值對調，且無相關測試。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 變更可能導致錯誤的畫面顯示</summary>

原本 `displayView: .readerMode` 改為 `.readerModeLongPressAction`。此變更與 QR code 移除無關，可能影響 Reader Mode 長按行為的畫面呈現。若為誤植，請還原；若為修正，請補充說明與測試。

**判斷依據**：diff 中此行由 `.readerMode` 改為 `.readerModeLongPressAction`，且無相關說明。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> gleanWrapper 屬性存取控制放寬可能違反封裝原則</summary>

原本 `private let gleanWrapper` 改為 `let gleanWrapper`，使外部可存取此屬性。若無必要，建議維持 `private` 以符合資訊隱藏原則（R11）。

**判斷依據**：diff 中移除了 `private` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9210 (cache hit 9088) ｜ completion tokens 987 ｜ PR #9</sub>