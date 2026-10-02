<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 移除 QR code 相關功能，包含 UI 動作、路由、遙測與測試，並調整版本號。主要風險在於 ToolbarMiddleware 中兩處邏輯變更：cancelEditMode 的條件從 AND 改為 OR，以及 readerModeState 的 isEnabled 判斷反轉，可能影響網址列編輯取消與閱讀模式按鈕的遙測正確性。建議確認這些變更是否為移除 QR code 時的必要調整，並補齊對應測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件變更可能導致非網頁 URL 被保留 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 的 isEnabled 判斷反轉可能導致遙測錯誤 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件變更可能導致非網頁 URL 被保留</summary>

原本條件為 `currentURL.isWebPage() && !currentURL.isReaderModeURL`，現在改為 `currentURL.isWebPage() || currentURL.isReaderModeURL`。這會讓非網頁但為閱讀模式 URL 的網址在取消編輯時被保留，可能導致網址列顯示不正確的內容。請確認此變更是否為移除 QR code 時的必要調整，若非必要請還原。

**判斷依據**：diff 中此行由 `&&` 改為 `||`，且 `!` 被移除。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 的 isEnabled 判斷反轉可能導致遙測錯誤</summary>

原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會讓閱讀模式按鈕的遙測事件記錄相反的啟用狀態，影響數據分析。請確認此變更是否為移除 QR code 時的必要調整，若非必要請還原。

**判斷依據**：diff 中兩行註解與布林值同時反轉。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8363 (cache hit 8320) ｜ completion tokens 589 ｜ PR #9</sub>