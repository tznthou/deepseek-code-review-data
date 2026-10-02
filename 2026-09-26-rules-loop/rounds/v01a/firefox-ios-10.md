<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試從 async 改為同步、調整 @Sendable 標註，以及為 ContentBlockerGenerator 加上 nonisolated(unsafe)。整體方向合理，但部分測試改動可能導致測試失去等待非同步完成的機制，且移除 @MainActor 可能違反專案規範並引入執行緒安全風險。建議優先確認測試同步化後的正確性，並重新評估 @MainActor 移除的必要性。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 測試移除 expectation 等待，可能導致測試提前結束而無法驗證非同步結果 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | [R09] 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒，違反專案規範 | 0.75 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 測試移除 expectation 等待，可能導致測試提前結束而無法驗證非同步結果 | 0.70 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | 新增 wrappedAction 可能造成不必要的閉包包裝，且未明確標註 @Sendable | 0.60 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 測試移除 expectation 等待，可能導致測試提前結束而無法驗證非同步結果</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 等待非同步下載完成，但此次修改移除了 expectation 的建立與等待，且方法改為同步。`downloadImage` 的回呼是非同步的，若測試方法同步返回，測試會在回呼執行前結束，導致斷言永遠不會被執行，測試形同虛設。建議保留 expectation 並使用 `wait(for:timeout:)` 等待，或將方法改回 async 並使用 `await fulfillment`。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且方法簽名從 `async` 改為同步。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> [R09] 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒，違反專案規範</summary>

原本 `startMockImageServer` 標註為 `@MainActor`，並有註解說明 GCDWebServer 必須在主執行緒初始化。此次修改移除了 `@MainActor`，且呼叫端也從 `await` 改為同步呼叫。若測試方法不在主執行緒執行，可能導致 GCDWebServer 初始化失敗或當機。專案規範 R09 要求 UI 相關程式碼需標註 @MainActor，此處雖非 UI，但涉及主執行緒限制的第三方元件，建議保留 @MainActor 或明確確保在主執行緒呼叫。

**判斷依據**：diff 中移除了 `@MainActor` 標註與相關註解，且呼叫端不再使用 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 測試移除 expectation 等待，可能導致測試提前結束而無法驗證非同步結果</summary>

在 `testRequestMediaCaptureSuccess` 中，原本建立 expectation 並在 decisionHandler 中 fulfill，最後使用 `wait(for: [expectation])` 等待。此次修改移除了 expectation 的建立與等待，且 decisionHandler 改為 @Sendable 閉包。若 `requestMediaCapturePermission` 是非同步呼叫，測試可能在 decisionHandler 執行前就結束，導致斷言未被執行。建議保留 expectation 並使用 `wait(for:timeout:)`。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> 新增 wrappedAction 可能造成不必要的閉包包裝，且未明確標註 @Sendable</summary>

在 `configure` 方法中，原本直接將 `moreButtonAction` 傳給 `ActionButtonViewModel`，現在改為建立 `wrappedAction` 閉包，在其中呼叫 `moreButtonAction?(button)`。此包裝似乎只是為了滿足型別需求，但若 `moreButtonAction` 本身已是 @Sendable @MainActor，直接傳遞即可，無需額外包裝。此外，`wrappedAction` 未標註 @Sendable，可能導致編譯器警告或錯誤。建議確認是否真的需要包裝，或直接調整參數型別。

**判斷依據**：diff 中新增了 wrappedAction 閉包，並將其傳給 touchUpAction。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將 `generator` 標註為 `nonisolated(unsafe)` 並加上註解說明 ContentBlockerGenerator 不是 thread safe。此舉雖然能通過編譯，但若未來有其他執行緒同時存取此靜態屬性，可能導致資料競爭。建議評估是否可改為其他隔離方式，或確保所有存取都在同一執行緒。

**判斷依據**：diff 中新增了 nonisolated(unsafe) 標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8973 (cache hit 1536) ｜ completion tokens 1528 ｜ PR #10</sub>