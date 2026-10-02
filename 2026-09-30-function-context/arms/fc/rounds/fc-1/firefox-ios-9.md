<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除 QR code 相關功能，包含 UI 進入點、路由、Redux action、Telemetry 與測試。整體移除範圍完整，但發現兩處與 QR code 無關的邏輯變更，可能引入回歸：ToolbarMiddleware 中 cancelEditMode 的條件反轉，以及 readerModeState 的 isEnabled 判斷反轉。此外，移除 Glean metrics 定義後，若仍有程式碼引用將導致編譯失敗，需確認已完全清除。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件反轉可能導致編輯模式無法正確取消 | 0.95 |
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | readerModeState 的 isEnabled 判斷反轉可能導致錯誤的遙測事件 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Glean/probes/metrics.yaml:1530` | 移除 Glean metrics 定義後可能殘留引用導致編譯失敗 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Telemetry/TelemetryWrapper.swift:825` | 移除 QR code 遙測事件後可能殘留引用 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件反轉可能導致編輯模式無法正確取消</summary>

原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓一般網頁（非 Reader Mode）也被視為有效 URL，導致 `url` 被設為非 nil，進而影響取消編輯時的行為。例如，使用者在一般網頁編輯網址列後取消編輯，原本應清空網址列，現在卻可能保留原網址，造成使用者困惑。建議確認此變更是否為 QR code 移除的一部分，若非必要請回復原狀。

**判斷依據**：diff 中此行由 `url = (currentURL.isWebPage() && !currentURL.isReaderModeURL) ? url : nil` 改為 `url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`，邏輯完全相反。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> readerModeState 的 isEnabled 判斷反轉可能導致錯誤的遙測事件</summary>

原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會讓 `readerModeButtonTapped` 的 `isEnabled` 參數傳入相反的值，導致遙測數據錯誤。例如，當 Reader Mode 可用時，原本應記錄為 enabled，現在卻記錄為 disabled。請確認此變更是否為預期行為，若非必要請回復。

**判斷依據**：diff 中此段由 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Glean/probes/metrics.yaml:1530</code> 移除 Glean metrics 定義後可能殘留引用導致編譯失敗</summary>

此 PR 移除了 `qr_code` 和 `toolbar.qr_scan_button_tapped` 的 metrics 定義，但若程式碼中仍有任何地方引用 `GleanMetrics.QrCode.scanned` 或 `GleanMetrics.Toolbar.qrScanButtonTapped`，將導致編譯錯誤。請確認已搜尋整個程式碼庫，確保沒有殘留引用。

**判斷依據**：diff 中移除了 `qr_code` 區塊，但未提供其他檔案中是否已移除所有引用。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Telemetry/TelemetryWrapper.swift:825</code> 移除 QR code 遙測事件後可能殘留引用</summary>

移除了 `case (.action, .scan, .qrCodeText, _, _)` 和 `case (.action, .scan, .qrCodeURL, _, _)` 的處理，但若其他程式碼仍呼叫 `TelemetryWrapper.recordEvent` 並傳入 `.qrCodeText` 或 `.qrCodeURL`，將導致執行時錯誤或未預期的行為。請確認所有呼叫點已移除。

**判斷依據**：diff 中移除了此 case，但未提供其他檔案中是否已移除所有呼叫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8363 (cache hit 8320) ｜ completion tokens 1182 ｜ PR #9</sub>