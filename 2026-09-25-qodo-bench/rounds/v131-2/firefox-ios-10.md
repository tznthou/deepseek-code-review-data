<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括：移除 StrictConcurrency 等實驗性旗標、將測試方法從 async 改為同步、在必要處加上 @Sendable 與 nonisolated(unsafe) 標註。整體風險集中在測試程式碼的同步化可能導致測試不穩定或失效，以及 nonisolated(unsafe) 的使用可能隱藏執行緒安全問題。建議優先確認測試等待機制是否正確，並評估 ContentBlockerGenerator 的執行緒安全性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 非同步測試改為同步後可能無法等待完成 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:67` | 非同步測試改為同步後可能無法等待完成 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試無法驗證非同步行為 | 0.80 |
| ⚠️ | Major | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 非同步測試改為同步後可能無法等待完成</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 等待非同步完成，但改為同步後移除了 expectation 的建立與等待。`downloadImage` 的回呼是非同步的，若測試方法同步返回，測試會在回呼執行前結束，導致斷言永遠不會被執行，測試可能誤判為通過或直接崩潰。建議保留 expectation 並使用 `wait(for:timeout:)` 等待，或將測試方法改回 async 並使用 `await fulfillment`。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且方法簽名從 `async` 改為同步。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:67</code> 非同步測試改為同步後可能無法等待完成</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forSpecialSVGCase` 中，雖然保留了 expectation 並改用 `wait(for:timeout:)`，但 `startMockImageServer` 原本是 async 且標註 @MainActor，現在改為同步且移除 @MainActor。若 GCDWebServer 的初始化必須在主執行緒，此變更可能導致測試在背景執行緒執行時崩潰。建議確認 GCDWebServer 的執行緒需求，必要時保留 @MainActor 或將測試方法標註 @MainActor。

**判斷依據**：diff 中 `startMockImageServer` 的 @MainActor 標註被移除，且呼叫方式從 `try? await` 改為 `try?`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，原本建立 expectation 並在 decisionHandler 中 fulfill，最後使用 `wait(for:)` 等待。但 diff 移除了 expectation 的建立與等待，只留下 decisionHandler 中的斷言。由於 `requestMediaCapturePermission` 可能非同步呼叫 decisionHandler，測試方法同步返回後斷言可能尚未執行，導致測試無法驗證行為。建議保留 expectation 並使用 `wait(for:timeout:)`。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 與 `wait(for: [expectation])`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將 `static let generator` 標註為 `nonisolated(unsafe)` 表示開發者宣稱此屬性安全，但註解指出 `ContentBlockerGenerator` 並非執行緒安全。若多個執行緒同時存取此屬性，可能導致資料競爭或未定義行為。建議確認此屬性的存取情境，若確實只在單一執行緒使用，可考慮改用 `@MainActor` 或將 generator 改為執行緒安全實作。

**判斷依據**：diff 中新增 `nonisolated(unsafe)` 並加上註解 `// FXIOS-14548 ContentBlockerGenerator is not thread safe`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6878 (cache hit 6784) ｜ completion tokens 1358 ｜ PR #10</sub>