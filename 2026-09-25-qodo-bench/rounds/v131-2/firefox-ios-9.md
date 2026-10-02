<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除 QR code 相關功能，包含快捷動作、路由、UI 顯示、遙測事件與測試。整體移除範圍完整，但發現兩處邏輯變更可能引入 bug：`cancelEditMode` 的條件判斷反轉，以及 `readerModeState` 的遙測旗標邏輯顛倒。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件判斷反轉，導致 URL 處理錯誤 | 0.95 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 遙測旗標邏輯顛倒 | 0.90 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件判斷反轉，導致 URL 處理錯誤</summary>

原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，表示只有當 URL 是網頁且不是閱讀模式時才保留 URL。修改後變成 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`，這會讓任何網頁 URL 或閱讀模式 URL 都被保留，包括非網頁的 URL（例如 `about:blank`）也會被保留，可能導致取消編輯時 URL 欄位顯示不正確的內容。

建議改回原本的邏輯，或確認此變更是否為有意為之。

**判斷依據**：diff 中此行由 `&& !` 改為 `||`，邏輯完全相反。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 遙測旗標邏輯顛倒</summary>

原本 `case .available: true` 表示當閱讀模式可用時，遙測事件記錄 `isEnabled = true`。修改後變成 `case .available: false`，而 `default: true`，這會導致當閱讀模式可用時記錄為未啟用，反之亦然，造成遙測數據錯誤。

建議改回原本的邏輯，或確認此變更是否為有意為之。

**判斷依據**：diff 中將 `true` 改為 `false`，`false` 改為 `true`，註解未變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8327 (cache hit 8320) ｜ completion tokens 620 ｜ PR #9</sub>