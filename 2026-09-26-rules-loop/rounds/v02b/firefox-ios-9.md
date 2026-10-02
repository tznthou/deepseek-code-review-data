<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要移除 QR code 相關功能，包含路由、快捷動作、工具列按鈕、Telemetry 與測試。移除範圍完整，但同時修改了兩處與 QR code 無關的邏輯（cancelEditMode 的條件判斷、readerModeState 的 isEnabled 判斷），且未附帶任何測試或說明，風險較高。建議先確認這兩處變更是否為誤植，並補上對應測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件判斷邏輯反轉，可能導致編輯模式取消時 URL 處理錯誤 | 0.95 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 的 isEnabled 判斷邏輯反轉，可能導致 Telemetry 記錄錯誤 | 0.95 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件判斷邏輯反轉，可能導致編輯模式取消時 URL 處理錯誤</summary>

在 `cancelEditMode` 中，原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓所有網頁 URL 或 Reader Mode URL 都被保留，而其他 URL（例如 about:blank、file://）則會被設為 nil。這與原本意圖（僅保留一般網頁且非 Reader Mode 的 URL）完全相反。

**失敗情境**：當使用者在編輯模式中取消編輯時，若目前頁面是 Reader Mode，原本會將 URL 設為 nil（可能觸發重新載入或顯示原始頁面），現在卻會保留 Reader Mode URL，可能導致後續行為異常。

**建議**：若此變更為誤植，請還原為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`；若為刻意修改，請提供對應的測試與說明。

**判斷依據**：diff 中此行由 `url = (currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil` 改為 `url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`，邏輯完全相反。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 的 isEnabled 判斷邏輯反轉，可能導致 Telemetry 記錄錯誤</summary>

在 `readerModeButtonTapped` 的 Telemetry 記錄中，原本 `case .available: true` 表示 Reader Mode 可用時 isEnabled 為 true，現在改為 `case .available: false`，且 `default: true`。這會讓所有非 available 狀態（例如 .unavailable、.active）都被記錄為 isEnabled = true，而 available 狀態反而記錄為 false。

**失敗情境**：當使用者點擊 Reader Mode 按鈕時，若目前狀態為 available（即將啟用），Telemetry 會記錄 isEnabled = false，與實際行為不符，影響數據分析。

**建議**：若此變更為誤植，請還原為 `case .available: true` 與 `default: false`；若為刻意修改，請提供對應的測試與說明。

**判斷依據**：diff 中原本為 `case .available: true` 與 `default: false`，現在改為 `case .available: false` 與 `default: true`，邏輯完全相反。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10422 (cache hit 10368) ｜ completion tokens 894 ｜ PR #9</sub>