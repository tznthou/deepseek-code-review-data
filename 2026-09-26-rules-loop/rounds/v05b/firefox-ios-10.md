<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、調整測試以使用同步等待、以及為部分閉包加上 @Sendable 標註。整體風險在於移除 @MainActor 標註可能導致 UI 執行緒安全問題，以及測試中移除 expectation 可能造成測試提前結束而無法驗證非同步行為。建議優先確認 startMockImageServer 的執行緒安全性，並確保測試仍能正確等待非同步完成。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | [R09] 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 移除 expectation 可能導致測試未等待非同步完成即結束 | 0.75 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試未等待決策處理器呼叫 | 0.70 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | 閉包包裝可能造成不必要的 @MainActor 隔離 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> [R09] 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒</summary>

原本 `startMockImageServer` 標註為 `@MainActor`，並有註解說明 GCDWebServer 必須在主執行緒初始化以避免當機。此 PR 移除了該標註，若測試在背景執行緒呼叫此方法，可能導致當機或非預期行為。建議保留 `@MainActor` 或改用其他方式確保主執行緒執行。

**判斷依據**：diff 中移除了 `@MainActor` 標註及相關註解，且方法內建立 `GCDWebServer()` 實例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 移除 expectation 可能導致測試未等待非同步完成即結束</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 expectation 等待非同步下載完成，但此 PR 移除了 expectation 的建立與等待。若 `downloadImage` 為非同步，測試可能在回呼執行前就結束，導致斷言未被執行或測試誤判為通過。建議保留 expectation 或改用 async/await 等待。

**判斷依據**：diff 中移除了 `let exp = expectation(...)` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且未見其他等待機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試未等待決策處理器呼叫</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待決策處理器被呼叫，但此 PR 移除了 expectation 的建立與等待。若 `requestMediaCapturePermission` 為非同步，測試可能在處理器執行前就結束，導致斷言未被執行。建議保留等待機制。

**判斷依據**：diff 中移除了 `let expectation = expectation(...)` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將靜態屬性標註為 `nonisolated(unsafe)` 表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 並非執行緒安全，可能導致資料競爭。建議確認其實作是否真的安全，或改用其他隔離方式。

**判斷依據**：diff 中新增 `nonisolated(unsafe)` 並有註解說明非執行緒安全。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> 閉包包裝可能造成不必要的 @MainActor 隔離</summary>

新增的 `wrappedAction` 閉包標註為 `@MainActor`，但僅呼叫 `moreButtonAction`，若 `moreButtonAction` 本身已為 `@MainActor`，此包裝可能多餘。建議確認是否可直接傳遞原始閉包。

**判斷依據**：diff 中新增 wrappedAction 並傳遞給 ActionButtonViewModel。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8925 (cache hit 8832) ｜ completion tokens 1286 ｜ PR #10</sub>