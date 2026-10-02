<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將專案與多個 target 的 Swift 版本升級至 6.0，並為多個閉包加上 @MainActor 與 @Sendable 標註以符合嚴格並發檢查。主要風險在於大量閉包標註變更可能導致呼叫端型別不符而編譯失敗，且部分標註（如 @Sendable）可能過度限制，造成不必要的編譯錯誤。建議先確認所有呼叫端已同步更新，並評估 @Sendable 的必要性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271` | onActionTap 閉包內使用 Task 可能造成執行緒跳脫 | 0.80 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79` | spamCallback 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:98` | completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:113` | completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:130` | completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:156` | completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:187` | decisionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:315` | addTab 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:708` | decisionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |
| ⚠️ | Major | `firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1056` | completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271</code> onActionTap 閉包內使用 Task 可能造成執行緒跳脫</summary>

原本 onActionTap 閉包標註為 @MainActor，直接呼叫 onboardingService.handleAction。修改後移除 @MainActor 標註，並在閉包內建立 Task 來執行 handleAction。這可能導致 handleAction 在非主執行緒執行，若其內部有 UI 操作或依賴主執行緒的邏輯，將造成執行緒安全問題。建議確認 handleAction 是否為 @MainActor 或內部有主執行緒保護，否則應保留 @MainActor 標註並直接呼叫。

**判斷依據**：diff 中 onActionTap 閉包從 @MainActor 改為無標註，並新增 Task 包裹呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:79</code> spamCallback 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

spamCallback 參數新增 @Sendable 標註，但呼叫端 handleSpammedJSAlert 的實作可能未標註 @Sendable，導致編譯失敗。需確認所有傳入的閉包皆符合 @Sendable 要求，或考慮移除不必要的 @Sendable。

**判斷依據**：diff 中 spamCallback 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:98</code> completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

多個 WKUIDelegate 方法的 completionHandler 參數新增 @Sendable 標註，但這些方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中多處 completionHandler 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:113</code> completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

多個 WKUIDelegate 方法的 completionHandler 參數新增 @Sendable 標註，但這些方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中多處 completionHandler 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:130</code> completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

多個 WKUIDelegate 方法的 completionHandler 參數新增 @Sendable 標註，但這些方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中多處 completionHandler 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:156</code> completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

多個 WKUIDelegate 方法的 completionHandler 參數新增 @Sendable 標註，但這些方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中多處 completionHandler 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:187</code> decisionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

decisionHandler 參數新增 @Sendable 標註，但此方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中 decisionHandler 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:315</code> addTab 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

addTab 參數新增 @Sendable 標註，但呼叫端可能傳入未標註 @Sendable 的閉包，導致編譯失敗。需確認所有呼叫端皆符合 @Sendable 要求。

**判斷依據**：diff 中 addTab 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:708</code> decisionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

decisionHandler 參數新增 @Sendable 標註，但此方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中 decisionHandler 參數型別新增 @Sendable。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1056</code> completionHandler 標註 @Sendable 可能導致呼叫端編譯錯誤</summary>

completionHandler 參數新增 @Sendable 標註，但此方法由系統呼叫，傳入的閉包可能未標註 @Sendable，導致編譯失敗。需確認所有實作皆符合 @Sendable 要求。

**判斷依據**：diff 中 completionHandler 參數型別新增 @Sendable。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8598 (cache hit 8576) ｜ completion tokens 2228 ｜ PR #3</sub>