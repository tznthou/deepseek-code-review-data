<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 Swift 版本從 5.0 升級至 6.0，並在多個檔案中調整了閉包與協定的並發標註（如 @MainActor、@Sendable）。主要風險在於 LaunchCoordinator 中將原本的 @MainActor 閉包改為包在 Task 中執行，可能導致非預期的執行緒切換與行為改變；另外部分閉包標註不一致可能造成編譯錯誤或執行期問題。建議優先確認 LaunchCoordinator 的變更是否會影響 UI 操作與狀態管理。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | 將 @MainActor 閉包包在 Task 中可能造成非預期執行緒切換 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:98` | WKUIDelegate 方法中的 completionHandler 標註不一致可能導致編譯錯誤 | 0.75 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79` | handleJavaScriptAlert 的 spamCallback 標註變更可能導致執行緒問題 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:315` | 部分閉包標註 @Sendable 但未確認所有使用情境 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192` | 移除 UX struct 並硬編碼按鈕尺寸可能降低可維護性 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> 將 @MainActor 閉包包在 Task 中可能造成非預期執行緒切換</summary>

原本 `onActionTap` 閉包標註為 `@MainActor`，直接呼叫 `onboardingService.handleAction`。修改後將呼叫包在 `Task { ... }` 中，但 `Task` 預設會繼承當前 actor context，若呼叫端已在 MainActor 上，則仍會在 MainActor 執行；然而若呼叫端不在 MainActor，則會切換到背景執行緒，可能導致 UI 操作或狀態更新不在主執行緒。建議明確使用 `Task { @MainActor in ... }` 或保留原本的直接呼叫。

**判斷依據**：diff 中原本的 `onActionTap: { @MainActor [weak self] action, cardName, completion in ... }` 被改為 `onActionTap: { [weak self] action, cardName, completion in ... }`，並在內部使用 `Task { ... }`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:98</code> WKUIDelegate 方法中的 completionHandler 標註不一致可能導致編譯錯誤</summary>

在 `BrowserViewController+WebViewDelegates.swift` 中，多個 WKUIDelegate 方法的 `completionHandler` 參數被加上 `@Sendable`，但對應的 `BrowserWebUIDelegate.swift` 中相同方法的 `completionHandler` 卻移除了 `@Sendable`。這可能導致協定遵循不一致，造成編譯錯誤。請確認所有實作與協定定義的標註一致。

**判斷依據**：diff 中 `BrowserViewController+WebViewDelegates.swift` 將 `completionHandler` 改為 `@escaping @MainActor @Sendable`，而 `BrowserWebUIDelegate.swift` 則將原本的 `@escaping @MainActor @Sendable` 改為 `@escaping @MainActor`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79</code> handleJavaScriptAlert 的 spamCallback 標註變更可能導致執行緒問題</summary>

`handleJavaScriptAlert` 的 `spamCallback` 參數從 `@escaping () -> Void` 改為 `@escaping @MainActor @Sendable () -> Void`。此方法內部在 `handleSpammedJSAlert` 中使用 `DispatchQueue.main.asyncAfter` 呼叫 callback，若 callback 被標註為 `@MainActor`，則在非主執行緒呼叫可能導致編譯錯誤或執行期崩潰。請確認所有呼叫點皆在主執行緒。

**判斷依據**：diff 中 `handleJavaScriptAlert` 的參數類型變更，且 `handleSpammedJSAlert` 內使用 `DispatchQueue.main.asyncAfter` 呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:315</code> 部分閉包標註 @Sendable 但未確認所有使用情境</summary>

多個方法（如 `addOpenInNewTab`、`addOpenInNewPrivateTab`）的閉包參數被加上 `@Sendable`，但這些閉包可能捕獲非 Sendable 的狀態（如 `self`），可能導致 Swift 6 的嚴格並發檢查錯誤。建議逐一確認閉包內捕獲的物件是否為 Sendable，或考慮使用 `@unchecked Sendable` 包裝。

**判斷依據**：diff 中多處將閉包參數加上 `@Sendable`，但未見對應的 Sendable 確認。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192</code> 移除 UX struct 並硬編碼按鈕尺寸可能降低可維護性</summary>

原本的 `UX.buttonSize` 常數被移除，改為直接使用數值 `40`。雖然不影響功能，但若未來需要調整尺寸，需修改多處。建議保留常數或使用有意義的命名。

**判斷依據**：diff 中刪除了 `struct UX` 並將 `UX.buttonSize` 替換為 `40`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 33731 (cache hit 1536) ｜ completion tokens 1512 ｜ PR #3</sub>