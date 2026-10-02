<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入網頁來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致測試不穩定或逾時。此外，helper 中的 XCTWaiter 使用方式有誤，且部分測試的 expectation 處理邏輯有缺陷。建議先修正這些問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter 使用方式錯誤，導致測試必定逾時 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | 未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗 | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34` | expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路，可能不穩定 | 0.75 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23` | FakeWKNavigationDelegate 未處理非 targetFrame 的情況 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter 使用方式錯誤，導致測試必定逾時</summary>

`XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 38 行使用了 `XCTWaiter.wait`，但該方法會阻塞執行緒，而 WebKit 的 delegate 回呼需要 RunLoop 處理，因此會造成死鎖。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> 未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗</summary>

`XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

**判斷依據**：diff 中第 39 行未使用 waiter 結果，且後續直接檢查 capturedFrame 和 capturedOrigin 是否為 nil。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34</code> expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束</summary>

在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致 `wait(for:)` 永遠等不到 expectation 被 fulfill，直到逾時。

應將 `expectation.fulfill()` 移回 `decisionHandler` 內，與其他測試保持一致。

**判斷依據**：diff 中第 34-35 行顯示 `expectation.fulfill()` 在 `wait` 之後，而其他測試（如 `testRequestMediaCaptureIsActiveFalse`）則在 `decisionHandler` 內 fulfill。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路，可能不穩定</summary>

`captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或不穩定，導致測試逾時或失敗。

建議改用本地 HTML 字串或 `data:` URL 來避免外部依賴，或使用 `WKWebView` 的 `loadHTMLString` 方法。

**判斷依據**：diff 中第 44 行使用 `URLRequest(url: url)`，而呼叫端傳入的是 `https://example.com`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23</code> FakeWKNavigationDelegate 未處理非 targetFrame 的情況</summary>

`decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

**判斷依據**：diff 中第 17-19 行直接使用 targetFrame，未檢查 nil。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4869 (cache hit 1536) ｜ completion tokens 1397 ｜ PR #12</sub>