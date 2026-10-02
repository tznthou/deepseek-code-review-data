<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試改為同步、標註 @Sendable 與 nonisolated(unsafe)。整體方向合理，但部分測試的同步化可能導致測試提前結束或無法驗證非同步行為，且移除 @MainActor 可能引入執行緒安全問題。建議先修正測試同步化的問題，並確認 GCDWebServer 的執行緒需求。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27` | 移除 expectation 可能導致測試提前結束 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化崩潰 | 0.70 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試提前結束 | 0.70 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27</code> 移除 expectation 可能導致測試提前結束</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `expectation` 等待非同步下載完成，但現在移除了 `exp.fulfill()` 與 `await fulfillment`，且測試方法改為同步。這可能導致測試在非同步回呼執行前就結束，無法驗證下載結果，甚至可能造成測試通過但實際上未測試到任何內容。建議保留 expectation 或改用 async/await 等待非同步操作完成。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")`、`exp.fulfill()` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且方法簽名從 `async` 改為同步。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化崩潰</summary>

原本 `startMockImageServer` 標註為 `@MainActor`，並有註解說明 GCDWebServer 必須在主執行緒初始化。移除後，若測試在背景執行緒呼叫此方法，可能導致崩潰或未定義行為。建議保留 @MainActor 或確保呼叫端在主執行緒執行。

**判斷依據**：diff 中移除了 `@MainActor` 屬性與相關註解。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試提前結束</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待 decision handler 被呼叫，但現在移除了 `expectation.fulfill()` 與 `wait(for:)`。這可能導致測試在 handler 執行前就結束，無法驗證決策結果。建議保留 expectation 或改用 async/await。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")`、`expectation.fulfill()` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

使用 `nonisolated(unsafe)` 標註靜態屬性，表示開發者已確認其執行緒安全性，但若 `ContentBlockerGenerator` 並非執行緒安全，可能導致資料競爭。建議確認該類別的執行緒安全性，或改用其他同步機制。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6914 (cache hit 6912) ｜ completion tokens 1146 ｜ PR #10</sub>