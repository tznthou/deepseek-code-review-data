<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除 QR code 相關功能，包含快捷動作、路由、Redux 狀態、工具列按鈕、Telemetry 與測試。整體移除範圍完整，但包含兩處與 QR code 無關的邏輯變更，可能引入回歸：ToolbarMiddleware 中 cancelEditMode 的條件由 AND 改為 OR，以及 readerModeState 的布林值反轉。建議將這兩項變更拆分至獨立 PR，並補充對應測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件變更可能導致非網頁 URL 被傳遞 | 0.90 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 布林值反轉可能導致錯誤的遙測事件 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件變更缺乏測試覆蓋 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 布林值反轉缺乏測試覆蓋 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] gleanWrapper 屬性存取控制從 private 改為 internal | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件變更可能導致非網頁 URL 被傳遞</summary>

原本條件為 `currentURL.isWebPage() && !currentURL.isReaderModeURL`，表示只有當 URL 是網頁且非閱讀模式時才保留 URL。修改後變成 `currentURL.isWebPage() || currentURL.isReaderModeURL`，這會讓任何網頁 URL（包括閱讀模式）或任何閱讀模式 URL（即使不是網頁）都被保留。這可能導致非網頁 URL（如 `about:blank` 或 `file://`）被傳遞給 `ToolbarAction`，進而影響取消編輯時的行為。

**失敗情境**：當使用者在網址列編輯一個非網頁 URL（例如 `about:config`）並取消編輯時，原本會將 URL 設為 nil，但修改後會保留該 URL，可能導致工具列顯示錯誤的 URL 或觸發非預期的導航。

**建議**：若此變更為刻意修正，請提供對應的測試案例；否則應還原為原本的 AND 條件。

**判斷依據**：diff 中此行由 `url = (currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil` 改為 `url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`，邏輯運算子與條件完全相反。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 布林值反轉可能導致錯誤的遙測事件</summary>

原本 `isReaderModeEnabled` 在 `.available` 時為 `true`，其他情況為 `false`。修改後變成 `.available` 時為 `false`，其他情況為 `true`。這會讓遙測事件記錄錯誤的啟用狀態，影響數據分析。

**失敗情境**：當閱讀模式可用時，使用者點擊閱讀模式按鈕，遙測會記錄 `isEnabled: false`，與實際行為相反。

**建議**：若此變更為刻意修正，請提供對應的測試案例；否則應還原為原本的邏輯。

**判斷依據**：diff 中原本為 `case .available: true` 與 `default: false`，修改後完全反轉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件變更缺乏測試覆蓋</summary>

此邏輯變更未包含任何對應的單元測試。`ToolbarMiddlewareTests` 中沒有針對 `cancelEditMode` 的測試案例，無法驗證新邏輯的正確性。

**建議**：新增測試案例，涵蓋 `isWebPage` 與 `isReaderModeURL` 的各種組合，確保行為符合預期。

**判斷依據**：diff 中僅修改了實作，未見任何測試檔案變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 布林值反轉缺乏測試覆蓋</summary>

此邏輯變更未包含任何對應的單元測試。`ToolbarMiddlewareTests` 中沒有針對 `readerModeButtonTapped` 遙測事件的測試案例，無法驗證新邏輯的正確性。

**建議**：新增測試案例，驗證不同 `readerModeState` 下遙測事件的正確性。

**判斷依據**：diff 中僅修改了實作，未見任何測試檔案變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] gleanWrapper 屬性存取控制從 private 改為 internal</summary>

原本 `private let gleanWrapper: GleanWrapper` 改為 `let gleanWrapper: GleanWrapper`，擴大了屬性的可見範圍。若無外部使用需求，建議保持 `private` 以符合資訊隱藏原則。

**判斷依據**：diff 中此行由 `private let gleanWrapper: GleanWrapper` 改為 `let gleanWrapper: GleanWrapper`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10374 (cache hit 10368) ｜ completion tokens 1456 ｜ PR #9</sub>