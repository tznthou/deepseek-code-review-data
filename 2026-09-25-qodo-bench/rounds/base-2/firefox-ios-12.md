<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過實際載入 https://example.com 來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴真實網路與 WebKit 內部行為，可能導致測試不穩定（flaky）或離線環境失敗。此外，helper 中的 XCTestExpectation 使用方式有誤，可能造成測試永遠等待或提前結束。建議先修正 expectation 的建立與等待邏輯，並考慮以注入或更輕量的方式取得測試所需物件。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | 測試中的 expectation 未正確等待，可能導致測試永遠掛起 | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與外部服務，可能導致不穩定或離線失敗 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 強制解包 URL 可能導致測試崩潰 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束</summary>

在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 39 行顯示 `let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`，且 `FakeWKNavigationDelegate` 在 `decidePolicyFor` 中呼叫 `expect.fulfill()`。在 `WKUIHandlerTests.swift` 的修改中，測試方法建立了 expectation 但未等待，直接呼叫 `wait(for: [expectation])`，這會導致測試永遠等待。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> 測試中的 expectation 未正確等待，可能導致測試永遠掛起</summary>

在 `testRequestMediaCaptureSuccess` 中，建立了 `expectation` 並在 decisionHandler 中呼叫 `expectation.fulfill()`，但之後直接呼叫 `wait(for: [expectation])`，而沒有使用 `waitForExpectations(timeout:)`。這會導致測試永遠等待，因為 `wait(for:)` 是 XCTestCase 的方法，它會等待所有傳入的 expectation 被 fulfill，但這裡的 expectation 從未被 fulfill（因為 decisionHandler 可能不會被呼叫，或者呼叫時機不正確）。

建議：使用 `waitForExpectations(timeout: 5.0)` 來等待，並確保 decisionHandler 一定會被呼叫。

**判斷依據**：diff 中 `WKUIHandlerTests.swift` 第 41 行顯示 `wait(for: [expectation])`，且上方 decisionHandler 中有 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與外部服務，可能導致不穩定或離線失敗</summary>

`captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試無法取得 frame 與 origin，進而失敗。此外，即使網路可用，外部服務的回應時間與內容可能變動，造成測試不穩定。

建議：使用本地測試伺服器或注入 mock 的 `WKNavigationAction` 來提供 frame 與 origin，避免依賴外部網路。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 44 行顯示 `webView.load(URLRequest(url: url))`，且呼叫處傳入 `URL(string: "https://example.com")!`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 強制解包 URL 可能導致測試崩潰</summary>

在呼叫 `WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!)` 時，使用了強制解包。雖然 URL 字串是硬編碼且有效，但若未來修改為變數，可能引入崩潰風險。建議使用 `guard let url = URL(string: ...) else { XCTFail(); return }` 來處理。

**判斷依據**：diff 中 `WKUIHandlerTests.swift` 第 38 行顯示 `URL(string: "https://example.com")!`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4009 (cache hit 3968) ｜ completion tokens 1462 ｜ PR #12</sub>