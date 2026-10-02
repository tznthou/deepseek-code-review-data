<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo extension 遷移至 Swift 6，主要變更包括移除 StrictConcurrency 相關的 experimental feature flags、將測試從 async 改為同步、在必要處加上 @Sendable 與 nonisolated(unsafe)，以及調整 Xcode 專案的 SWIFT_VERSION。整體風險中等，需特別注意測試同步化後可能造成的執行緒阻塞、@Sendable 閉包的正確性，以及移除 concurrency flags 後是否遺留未處理的資料隔離問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 測試從 async 改為同步可能導致主執行緒阻塞 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:29` | 移除 expectation 可能導致測試無法驗證非同步行為 | 0.70 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | 額外的 closure 包裝可能造成 retain cycle | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 測試從 async 改為同步可能導致主執行緒阻塞</summary>

原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 的測試改為 `wait(for: [exp], timeout: 2.0)`，但 `startMockImageServer` 已不再是 async，且測試方法也移除了 `async`。這可能導致測試在主執行緒上同步等待非同步 callback，若 callback 需要在主執行緒執行，可能造成死鎖或測試逾時。建議確認 GCDWebServer 的 callback 執行緒，或保留 async 測試寫法。

**判斷依據**：diff 中移除了 `async` 關鍵字，並將 `await fulfillment` 改為 `wait(for:)`，但 `startMockImageServer` 仍可能涉及非同步行為。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:29</code> 移除 expectation 可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，原本有 expectation 等待 decision handler 被呼叫，但修改後移除了 expectation 與 wait，僅直接呼叫 `subject.requestMediaCapturePermission(decisionHandler: decisionHandler)`。若該方法為非同步，測試可能在 callback 執行前就結束，導致斷言未被執行。建議保留 expectation 或改用 async 測試。

**判斷依據**：diff 中移除了 `let expectation = expectation(...)` 與 `wait(for: [expectation])`，但未確認方法是否同步。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將 `static let generator` 標記為 `nonisolated(unsafe)` 以繞過 Swift 6 的 concurrency 檢查，但註解指出 ContentBlockerGenerator 並非 thread safe。若此 static property 被多個執行緒同時存取，可能導致資料競爭。建議改為使用 actor 或確保所有存取都在同一執行緒。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)`，且註解明確指出 thread safety 問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> 額外的 closure 包裝可能造成 retain cycle</summary>

新增的 `wrappedAction` 閉包捕獲了 `moreButtonAction`，但未使用 `[weak self]` 或 `[weak moreButtonAction]`。若 `moreButtonAction` 持有 self，可能造成 retain cycle。建議確認閉包的生命週期，或使用 weak 捕獲。

**判斷依據**：diff 中新增了 wrappedAction，但未見 weak 捕獲。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10279 (cache hit 10240) ｜ completion tokens 1080 ｜ PR #10</sub>