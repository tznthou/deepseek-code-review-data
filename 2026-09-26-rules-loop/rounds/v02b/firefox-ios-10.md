<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除實驗性 concurrency 旗標、將測試方法從 async 改為同步、在必要處加上 @Sendable 或 nonisolated(unsafe) 標註，並將 ShareTo 的 SWIFT_VERSION 設為 6.0。整體方向合理，但需注意測試中移除 expectation 可能導致測試提前結束而無法驗證非同步行為，以及 nonisolated(unsafe) 的使用是否確實安全。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 移除 expectation 可能導致測試提前結束，無法驗證非同步結果 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試提前結束，無法驗證 decisionHandler 被呼叫 | 0.80 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 移除 expectation 可能導致測試提前結束，無法驗證非同步結果</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `expectation` 與 `await fulfillment` 等待非同步下載完成，但此次修改移除了 expectation 的建立與等待，且方法不再是 async。這可能導致測試在非同步 callback 執行前就結束，使得斷言永遠不會被執行，測試失去驗證效果。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或將方法改回 async 並使用 `await fulfillment`。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且方法簽名從 `async` 改為同步。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試提前結束，無法驗證 decisionHandler 被呼叫</summary>

在 `testRequestMediaCaptureSuccess` 中，原本建立 expectation 並在 decisionHandler 中 fulfill，最後以 `wait(for:)` 等待。此次修改移除了 expectation 的建立與等待，且 decisionHandler 僅包含斷言。這可能導致測試在非同步呼叫 decisionHandler 前就結束，使得斷言不會被執行。

建議：保留 expectation 並使用 `wait(for:timeout:)`，或改為 async 測試並使用 `await fulfillment`。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將 `static let generator` 標註為 `nonisolated(unsafe)` 以繞過 Swift 6 的 concurrency 檢查，但註解指出 `ContentBlockerGenerator` 並非執行緒安全。若此 generator 可能被多個執行緒同時使用，可能導致資料競爭。建議確認使用情境是否真的安全，或考慮將 generator 改為 actor 或使用鎖保護。

**判斷依據**：diff 中新增 `nonisolated(unsafe)` 並加上註解 `// FXIOS-14548 ContentBlockerGenerator is not thread safe`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8973 (cache hit 8960) ｜ completion tokens 1074 ｜ PR #10</sub>