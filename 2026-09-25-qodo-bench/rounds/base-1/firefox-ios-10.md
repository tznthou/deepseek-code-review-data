<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo extension 遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試改為同步、標註 @Sendable 與 nonisolated(unsafe)。整體方向合理，但部分測試的同步化可能導致測試提前結束或無法正確等待非同步完成，且移除 @MainActor 可能引入執行緒安全問題。建議優先修正測試同步化與 GCDWebServer 執行緒問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27` | 測試改為同步後未等待非同步完成，可能導致測試提前結束或無法驗證結果 | 0.90 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 測試未等待非同步決策處理器，可能導致測試提前結束 | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒而崩潰 | 0.80 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27</code> 測試改為同步後未等待非同步完成，可能導致測試提前結束或無法驗證結果</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，移除了 `await fulfillment(of: [exp], timeout: 2.0)`，且未使用 `wait(for:timeout:)`。`downloadImage` 的回呼是非同步的，測試方法現在是同步的，因此測試會在回呼執行前就返回，導致測試永遠通過（即使回呼中有 XCTFail 也不會被執行）。建議保留 expectation 並使用 `wait(for:timeout:)` 等待。

**判斷依據**：diff 中移除了 `await fulfillment(of: [exp], timeout: 2.0)`，且未加入 `wait(for:timeout:)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 測試未等待非同步決策處理器，可能導致測試提前結束</summary>

在 `testRequestMediaCaptureSuccess` 中，移除了 expectation 的建立與 `wait(for:)`，但 `requestMediaCapturePermission` 可能非同步呼叫決策處理器。測試方法現在是同步的，可能在處理器執行前就返回，導致斷言未被執行。建議保留 expectation 並等待。

**判斷依據**：diff 中移除了 expectation 與 wait，且未加入其他等待機制。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒而崩潰</summary>

原本 `startMockImageServer` 標註為 `@MainActor`，註解說明 GCDWebServer 必須在主執行緒初始化。移除後，若測試在背景執行緒呼叫此方法，可能導致崩潰。建議保留 @MainActor 或確保呼叫端在主執行緒。

**判斷依據**：diff 中移除了 `@MainActor` 標註及相關註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

`nonisolated(unsafe)` 標註表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 實例並非執行緒安全，可能導致資料競爭。建議確認其內部狀態或改為隔離。

**判斷依據**：diff 中新增 `nonisolated(unsafe)`，並有註解說明非執行緒安全。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6914 (cache hit 1536) ｜ completion tokens 988 ｜ PR #10</sub>