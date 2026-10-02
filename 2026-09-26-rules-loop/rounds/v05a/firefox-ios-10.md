<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，移除實驗性 concurrency 旗標並調整測試以符合 Swift 6 的嚴格並行檢查。主要風險在於測試中移除 async/await 與 expectation 等待，可能導致測試提前結束或無法驗證非同步行為；此外，移除 @MainActor 於 GCDWebServer 初始化可能導致執行緒問題。建議優先修正測試同步問題，並確認 GCDWebServer 的執行緒安全性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26` | 測試方法移除 async 與 expectation 等待，導致非同步驗證失效 | 0.95 |
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:67` | 測試方法移除 async 但未正確等待非同步完成 | 0.95 |
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:98` | 測試方法移除 async 但未正確等待非同步完成 | 0.95 |
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:125` | 測試方法移除 async 但未正確等待非同步完成 | 0.95 |
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:149` | 測試方法移除 async 但未正確等待非同步完成 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 移除 expectation 等待可能導致測試無法驗證非同步行為 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 移除 expectation 等待可能導致測試無法驗證非同步行為 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 移除 expectation 等待可能導致測試無法驗證非同步行為 | 0.80 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:26</code> 測試方法移除 async 與 expectation 等待，導致非同步驗證失效</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 等待非同步下載完成，但現在移除了 expectation 的建立與等待，且方法不再是 async。這使得測試方法在啟動下載後立即返回，無法驗證下載結果，且 XCTest 可能因測試結束而取消進行中的非同步工作，導致測試無法真正驗證功能。

建議：保留 expectation 並使用 `wait(for:timeout:)` 同步等待，或將方法維持 async 並使用 `await fulfillment(of:timeout:)`。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 和 `await fulfillment(of: [exp], timeout: 2.0)`，且方法簽名從 `async` 改為非 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:67</code> 測試方法移除 async 但未正確等待非同步完成</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forSpecialSVGCase` 中，方法不再是 async，但內部仍使用 `wait(for: [exp], timeout: 2.0)` 等待 expectation。然而，expectation 的建立與 fulfill 邏輯可能不完整：diff 中未顯示 `exp` 的建立，但原本應有 `let exp = expectation(description: ...)`。若未建立 expectation，`wait(for:)` 會崩潰或無效。此外，移除 async 後，`startMockImageServer` 改為同步呼叫，但該方法可能仍需要主執行緒，需確認。

建議：確保 expectation 正確建立並在回呼中 fulfill，且使用 `wait(for:timeout:)` 等待。

**判斷依據**：diff 中將 `await fulfillment(of: [exp], timeout: 2.0)` 改為 `wait(for: [exp], timeout: 2.0)`，但未顯示 `exp` 的建立，且方法不再是 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:98</code> 測試方法移除 async 但未正確等待非同步完成</summary>

在 `testDownloadingICOImage_withKingfisherProcessor` 中，方法不再是 async，但使用 `wait(for: [exp], timeout: 2.0)` 等待 expectation。與前一個測試相同，需確認 `exp` 是否正確建立並在回呼中 fulfill。若未建立，測試會失敗或崩潰。

建議：確保 expectation 正確建立並在回呼中 fulfill，且使用 `wait(for:timeout:)` 等待。

**判斷依據**：diff 中將 `await fulfillment(of: [exp], timeout: 2.0)` 改為 `wait(for: [exp], timeout: 2.0)`，且方法不再是 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:125</code> 測試方法移除 async 但未正確等待非同步完成</summary>

在 `testDownloadingGarbageData_withKingfisherProcessor` 中，方法不再是 async，但使用 `wait(for: [exp], timeout: 2.0)` 等待 expectation。需確認 `exp` 是否正確建立並在回呼中 fulfill。若未建立，測試會失敗或崩潰。

建議：確保 expectation 正確建立並在回呼中 fulfill，且使用 `wait(for:timeout:)` 等待。

**判斷依據**：diff 中將 `await fulfillment(of: [exp], timeout: 2.0)` 改為 `wait(for: [exp], timeout: 2.0)`，且方法不再是 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:149</code> 測試方法移除 async 但未正確等待非同步完成</summary>

在 `testDownloadingEmptyImage_withKingfisherProcessor` 中，方法不再是 async，但使用 `wait(for: [exp], timeout: 2.0)` 等待 expectation。需確認 `exp` 是否正確建立並在回呼中 fulfill。若未建立，測試會失敗或崩潰。

建議：確保 expectation 正確建立並在回呼中 fulfill，且使用 `wait(for:timeout:)` 等待。

**判斷依據**：diff 中將 `await fulfillment(of: [exp], timeout: 2.0)` 改為 `wait(for: [exp], timeout: 2.0)`，且方法不再是 async。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全</summary>

原本 `startMockImageServer` 標記為 `@MainActor`，並有註解說明 GCDWebServer 必須在主執行緒初始化。現在移除了 `@MainActor`，若測試在背景執行緒呼叫此方法，可能導致崩潰或未定義行為。

建議：保留 `@MainActor`，或確保呼叫端在主執行緒執行。

**判斷依據**：diff 中移除了 `@MainActor` 註解及相關說明。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 移除 expectation 等待可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待 decision handler 被呼叫，但現在移除了 expectation 的建立與 `wait(for:)`。這使得測試在呼叫 `requestMediaCapturePermission` 後立即返回，無法驗證 decision handler 是否被正確呼叫。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或將方法改為 async 並使用 `await fulfillment(of:timeout:)`。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 和 `wait(for: [expectation])`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 移除 expectation 等待可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureIsActiveFalse` 中，原本使用 expectation 等待 decision handler 被呼叫，但現在移除了 expectation 的建立與 `wait(for:)`。這使得測試在呼叫 `requestMediaCapturePermission` 後立即返回，無法驗證 decision handler 是否被正確呼叫。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或將方法改為 async 並使用 `await fulfillment(of:timeout:)`。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 和 `wait(for: [expectation])`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 移除 expectation 等待可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureIsActiveFalse` 的第二個測試案例中，原本使用 expectation 等待 decision handler 被呼叫，但現在移除了 expectation 的建立與 `wait(for:)`。這使得測試在呼叫 `requestMediaCapturePermission` 後立即返回，無法驗證 decision handler 是否被正確呼叫。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或將方法改為 async 並使用 `await fulfillment(of:timeout:)`。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 和 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

將 `generator` 標記為 `nonisolated(unsafe)` 表示開發者已知其非執行緒安全，但這可能導致未來誤用。建議考慮將 `ContentBlockerGenerator` 改為執行緒安全，或提供同步機制。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8925 (cache hit 6912) ｜ completion tokens 2779 ｜ PR #10</sub>