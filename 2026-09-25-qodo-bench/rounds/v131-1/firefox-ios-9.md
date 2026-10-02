<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除 QR code 相關功能，包含 UI 入口、路由、遙測與測試，並調整版本號。主要風險在於兩處邏輯變更：`cancelEditMode` 的條件從 `&&` 改為 `||`，以及 reader mode 狀態的布林值對調，可能影響網址列編輯取消與 reader mode 按鈕的遙測行為。此外，移除 QR code 遙測定義可能導致其他模組引用時編譯失敗，需確認無殘留引用。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485` | cancelEditMode 條件變更可能導致非網頁 URL 被錯誤保留 | 0.90 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524` | reader mode 狀態布林值對調可能造成遙測數據錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Glean/probes/metrics.yaml:1530` | 移除 QR code 遙測定義可能導致其他模組編譯失敗 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Glean/probes/toolbar.yaml:24` | 移除 toolbar 遙測定義可能導致其他模組編譯失敗 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485</code> cancelEditMode 條件變更可能導致非網頁 URL 被錯誤保留</summary>

原本條件 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)` 改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓 reader mode URL 也被保留，但 reader mode URL 並非一般網頁，可能導致取消編輯時網址列顯示 reader mode 的內部 URL，而非使用者預期的內容。建議確認此變更是否為預期行為，若非必要請回復原條件。

**判斷依據**：diff 中此行由 `&&` 改為 `||`，且無相關說明。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524</code> reader mode 狀態布林值對調可能造成遙測數據錯誤</summary>

原本 `case .available: true` 改為 `false`，`default: false` 改為 `true`。這會使 `isReaderModeEnabled` 的語意相反，導致 `readerModeButtonTapped` 遙測事件記錄錯誤的啟用狀態。若此變更非預期，請修正；若為預期，請確認遙測定義是否需同步調整。

**判斷依據**：diff 中布林值對調，且註解未更新。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Glean/probes/metrics.yaml:1530</code> 移除 QR code 遙測定義可能導致其他模組編譯失敗</summary>

移除了 `qr_code` 區塊，但若其他程式碼仍引用 `GleanMetrics.QrCode`，將導致編譯錯誤。請確認所有引用已一併移除（例如 `TelemetryWrapper.swift` 中的 `GleanMetrics.QrCode.scanned.add()` 已移除，但需檢查是否有其他檔案）。

**判斷依據**：diff 中刪除了整個 `qr_code` 區塊。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Glean/probes/toolbar.yaml:24</code> 移除 toolbar 遙測定義可能導致其他模組編譯失敗</summary>

移除了 `qr_scan_button_tapped` 事件定義，若其他程式碼仍引用 `GleanMetrics.Toolbar.qrScanButtonTapped`，將導致編譯錯誤。請確認所有引用已移除（例如 `ToolbarTelemetry.swift` 中的 `qrCodeButtonTapped` 已移除，但需檢查其他檔案）。

**判斷依據**：diff 中刪除了整個 `qr_scan_button_tapped` 區塊。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8327 (cache hit 1408) ｜ completion tokens 1306 ｜ PR #9</sub>