<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試改為同步、調整 @Sendable 標註，以及將 ShareTo 的 SWIFT_VERSION 設為 6.0。整體風險在於移除實驗性旗標後可能暴露新的並行錯誤，且部分測試改為同步後可能因非同步行為而失敗。最需要先確認的是 MainContentBlockerGenerator 的 nonisolated(unsafe) 使用是否合理，以及測試中移除 @MainActor 是否會導致 GCDWebServer 初始化問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化崩潰 | 0.70 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 測試改為同步可能導致非同步回呼未被等待 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 移除 expectation 可能導致測試無法驗證非同步行為 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | wrappedAction 可能造成不必要的閉包包裝 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將 `generator` 標記為 `nonisolated(unsafe)` 會繞過 Swift 6 的並行檢查，但註解指出 `ContentBlockerGenerator` 並非執行緒安全。若此靜態屬性被多個執行緒同時存取，可能導致資料競爭或未定義行為。建議確認此 generator 是否真的只會在單一執行緒使用，或考慮將其改為 actor 或使用鎖保護。

**判斷依據**：diff 中新增 `nonisolated(unsafe)` 並移除原本的 `static let`，且註解明確指出 `ContentBlockerGenerator is not thread safe`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化崩潰</summary>

原本 `startMockImageServer` 標記為 `@MainActor`，註解說明 GCDWebServer 必須在主執行緒初始化。移除後，若測試在非主執行緒呼叫此方法，可能導致崩潰。建議保留 `@MainActor` 或確保測試方法在主執行緒執行。

**判斷依據**：diff 中移除了 `@MainActor` 標註及相關註解。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 測試改為同步可能導致非同步回呼未被等待</summary>

多個測試方法從 `async` 改為同步，並將 `await fulfillment` 改為 `wait(for:)`。但 `downloadImage` 的回呼可能是非同步的，若在 `wait` 之前回呼尚未執行，測試可能提前結束或失敗。建議確認 `downloadImage` 是否保證同步呼叫回呼，或保留非同步等待。

**判斷依據**：diff 中多處將 `await fulfillment(of: [exp], timeout: 2.0)` 改為 `wait(for: [exp], timeout: 2.0)`，且移除 `async` 關鍵字。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 移除 expectation 可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，移除了 expectation 的建立與等待，僅留下 assertion。若 `requestMediaCapturePermission` 是非同步呼叫，測試可能在 assertion 執行前就結束，導致測試失效。建議保留 expectation 或確認該方法為同步。

**判斷依據**：diff 中移除了 `let expectation = expectation(...)` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> wrappedAction 可能造成不必要的閉包包裝</summary>

新增的 `wrappedAction` 只是單純呼叫 `moreButtonAction`，沒有額外邏輯，可能只是為了滿足型別檢查。若 `ActionButtonViewModel` 的 `touchUpAction` 型別已相容，此包裝可能多餘。建議確認是否可直接傳遞 `moreButtonAction`。

**判斷依據**：diff 中新增 wrappedAction 並在 touchUpAction 使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8983 (cache hit 6784) ｜ completion tokens 1246 ｜ PR #10</sub>