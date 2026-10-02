<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要移除 QR code 相關功能，包括快捷動作、路由、工具列按鈕、遙測與測試。整體移除範圍完整，但其中包含兩處與 QR code 無關的邏輯變更（ToolbarMiddleware.swift 中的布林條件反轉），可能引入回歸。建議先確認這兩處變更的意圖與正確性。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | 布林條件反轉可能導致取消編輯時 URL 處理錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | Reader Mode 啟用狀態判斷反轉可能導致遙測錯誤 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> 布林條件反轉可能導致取消編輯時 URL 處理錯誤</summary>

在 `cancelEditMode(windowUUID:)` 中，原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓「非網頁但為 Reader Mode URL」的 URL 也被保留，可能導致取消編輯時工具列顯示錯誤的 URL。請確認此變更是否為預期行為，若非預期請還原。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，邏輯完全相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> Reader Mode 啟用狀態判斷反轉可能導致遙測錯誤</summary>

在 `readerModeButtonTapped` 相關邏輯中，原本 `case .available: true` 改為 `false`，`default: false` 改為 `true`。這會使遙測記錄的 `isEnabled` 值與實際狀態相反，影響數據準確性。請確認此變更是否為預期行為，若非預期請還原。

**判斷依據**：diff 中兩行布林值對調。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10412 (cache hit 10368) ｜ completion tokens 565 ｜ PR #9</sub>