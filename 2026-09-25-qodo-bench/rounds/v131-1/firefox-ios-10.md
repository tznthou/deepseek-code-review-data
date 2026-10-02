<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括：移除 StrictConcurrency 等實驗性旗標、將測試從 async 改為同步、為閉包加上 @Sendable、以及使用 nonisolated(unsafe) 處理全域變數。整體風險中等，需注意測試同步化可能導致的執行緒問題，以及 nonisolated(unsafe) 的潛在資料競爭。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 測試方法從 async 改為同步可能導致執行緒阻塞或逾時 | 0.80 |
| ⚠️ | Major | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏資料競爭 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試無法驗證非同步行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 測試方法從 async 改為同步可能導致執行緒阻塞或逾時</summary>

原本的 async 測試方法使用 `await fulfillment(of:timeout:)` 等待非同步完成，現在改為同步方法並使用 `wait(for:timeout:)`。然而，`startMockImageServer` 原本標記為 `@MainActor`，現在移除了該標記，且測試方法本身未標註 `@MainActor`。若 `startMockImageServer` 內部需要在主執行緒執行（例如 GCDWebServer 初始化），在同步測試方法中直接呼叫可能導致主執行緒阻塞或崩潰。建議確認 GCDWebServer 的執行緒需求，或將測試方法標註為 `@MainActor` 並使用 `wait(for:timeout:)` 的正確變體。

**判斷依據**：diff 中移除了 `async` 關鍵字，並將 `await fulfillment` 改為 `wait(for:)`；同時移除了 `startMockImageServer` 的 `@MainActor` 標記。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏資料競爭</summary>

`generator` 被標註為 `nonisolated(unsafe) static let`，這表示編譯器不會檢查其執行緒安全性。如果 `ContentBlockerGenerator` 實例不是執行緒安全的，多個執行緒同時存取可能導致資料競爭。建議確認 `ContentBlockerGenerator` 是否為 Sendable，或改用其他隔離機制（如 actor 或鎖）。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)` 修飾詞，並附有註解「ContentBlockerGenerator is not thread safe」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待 decision handler 被呼叫，現在移除了 expectation 和 `wait`，只留下閉包內的斷言。如果 decision handler 是非同步呼叫，測試可能在斷言執行前就結束，導致測試無法有效驗證。建議保留 expectation 或改用其他同步等待機制。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: ...)` 和 `wait(for: [expectation])`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6878 (cache hit 1408) ｜ completion tokens 910 ｜ PR #10</sub>