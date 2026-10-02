<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除 QR code 相關功能，包含 UI 動作、路由、遙測與測試。整體移除範圍完整，但其中混入了三處與 QR code 無關的邏輯變更，可能造成行為回歸，需要特別確認。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 從 .readerMode 改為 .readerModeLongPressAction，可能顯示錯誤畫面 | 0.95 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 中的 URL 判斷條件由 AND 改為 OR，可能導致非預期行為 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | isReaderModeEnabled 的布林值邏輯反轉，可能導致遙測資料錯誤 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 從 .readerMode 改為 .readerModeLongPressAction，可能顯示錯誤畫面</summary>

在 `handleShowReaderModeLongPressAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這會導致長按閱讀模式按鈕時，畫面顯示錯誤的視圖（可能是長按選單而非閱讀模式）。請確認此變更是否為預期行為，若非預期請還原。

**判斷依據**：diff 中該行由 `displayView: .readerMode` 改為 `displayView: .readerModeLongPressAction`，且此變更與 QR code 移除無關。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 中的 URL 判斷條件由 AND 改為 OR，可能導致非預期行為</summary>

在 `cancelEditMode` 中，原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓閱讀模式 URL 也被視為有效 URL 而保留，可能導致取消編輯時 URL 欄顯示閱讀模式 URL，而非預期的空白或一般 URL。請確認此變更是否為預期行為。

**判斷依據**：diff 中該行由 `&&` 改為 `||`，且此變更與 QR code 移除無關。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> isReaderModeEnabled 的布林值邏輯反轉，可能導致遙測資料錯誤</summary>

原本 `case .available: true` 與 `default: false`，現在改為 `case .available: false` 與 `default: true`。這會讓閱讀模式按鈕的遙測事件記錄錯誤的啟用狀態，影響數據分析。請確認此變更是否為預期行為。

**判斷依據**：diff 中該 switch 的兩個分支回傳值被反轉，且此變更與 QR code 移除無關。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8363 (cache hit 8320) ｜ completion tokens 807 ｜ PR #9</sub>