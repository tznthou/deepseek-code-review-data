<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在移除 QR code 相關功能，包含快捷動作、路由、工具列按鈕、遙測與測試。主要風險在於兩處邏輯變更：`cancelEditMode` 中 URL 判斷條件的反轉，以及 `readerModeState` 對應布林值的反轉，可能導致非預期的行為。此外，`ToolbarTelemetry` 的 `gleanWrapper` 屬性從 `private` 改為 `internal`，違反最小權限原則。整體而言，移除 QR code 的程式碼看似完整，但邏輯變更需謹慎驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 中 URL 判斷條件反轉可能導致非預期行為 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 對應布林值反轉可能導致遙測錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] gleanWrapper 屬性不應從 private 改為 internal | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 中 URL 判斷條件反轉可能導致非預期行為</summary>

原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`。這會讓 reader mode URL 也被保留，可能導致取消編輯時 URL 欄顯示 reader mode 的 URL，而非一般網頁 URL。請確認此變更是否為預期行為，並補充測試。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，邏輯完全相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 對應布林值反轉可能導致遙測錯誤</summary>

原本 `case .available: true` 改為 `false`，`default: false` 改為 `true`。這會讓 `isReaderModeEnabled` 的遙測值與實際狀態相反，可能誤導分析。請確認此變更是否為預期，並修正或補充說明。

**判斷依據**：diff 中兩行布林值對調。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] gleanWrapper 屬性不應從 private 改為 internal</summary>

`gleanWrapper` 原本為 `private let`，現在改為 `let`（internal）。此屬性僅供內部使用，應維持 `private` 以符合最小權限原則。

**判斷依據**：diff 中移除了 `private` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10412 (cache hit 8320) ｜ completion tokens 769 ｜ PR #9</sub>