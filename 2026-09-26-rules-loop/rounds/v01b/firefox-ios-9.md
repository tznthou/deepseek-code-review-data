<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除 QR code 相關功能，包含快捷動作、路由、Redux 狀態、遙測與測試。整體移除範圍完整，但其中混入了三處與 QR code 無關的邏輯變更，可能造成行為回歸：ToolbarMiddleware 的 cancelEditMode 條件反轉、readerModeState 的 isEnabled 判斷反轉，以及 BrowserViewControllerState 中 displayView 的 case 名稱變更。這些變更缺乏測試與說明，風險較高，建議拆分或補充驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件反轉可能導致 URL 遺失 | 0.90 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 的 isEnabled 判斷反轉 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566` | displayView 改為 .readerModeLongPressAction 可能造成顯示錯誤 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9` | [R11] gleanWrapper 屬性從 private 改為 internal 可能違反封裝 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件反轉可能導致 URL 遺失</summary>

原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓非網頁但為 reader mode 的 URL 也被保留，或網頁但非 reader mode 的 URL 被設為 nil，與原意相反。例如：一般網頁（isWebPage=true, isReaderModeURL=false）原本會保留 URL，現在會被設為 nil，導致取消編輯時網址列被清空。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，邏輯完全反轉，且無相關測試更新。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 的 isEnabled 判斷反轉</summary>

原本 `case .available: true`，現在改為 `case .available: false`，且 default 從 false 改為 true。這會讓 reader mode 按鈕的啟用狀態完全相反：當 reader mode 可用時按鈕被視為停用，不可用時反而被視為啟用，直接影響使用者操作與遙測數據。

**判斷依據**：diff 中兩行布林值對調，且註解仍寫「will be enabled after action gets executed」，與新值矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566</code> displayView 改為 .readerModeLongPressAction 可能造成顯示錯誤</summary>

原本 `displayView: .readerMode`，現在改為 `.readerModeLongPressAction`。若此 case 是用於一般 reader mode 顯示，改名可能導致對應的 view 無法正確呈現，或與其他狀態混淆。需確認此處是否為筆誤，或是否有對應的 enum case 定義。

**判斷依據**：diff 中此行由 `.readerMode` 改為 `.readerModeLongPressAction`，且無其他相關變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9</code> [R11] gleanWrapper 屬性從 private 改為 internal 可能違反封裝</summary>

原本 `private let gleanWrapper: GleanWrapper`，現在改為 `let gleanWrapper: GleanWrapper`（internal）。若無外部使用需求，應維持 private 以符合最小權限原則。

**判斷依據**：diff 中移除了 private 修飾詞，且未見其他檔案使用此屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10422 (cache hit 10368) ｜ completion tokens 1029 ｜ PR #9</sub>