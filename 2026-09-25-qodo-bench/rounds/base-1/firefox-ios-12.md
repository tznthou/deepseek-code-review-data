<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入 https://example.com 來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴外部網路與 WebKit 的非同步行為，可能導致測試不穩定或逾時；此外，testRequestMediaCaptureSuccess 中的 expectation 使用方式有誤，可能造成測試永遠等待或提前通過。建議先修正 expectation 邏輯，並考慮以更可靠的方式取得測試所需的 frame 與 origin。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | expectation 使用錯誤導致測試可能永遠等待或提前通過 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41` | 測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤 | 0.75 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23` | FakeWKNavigationDelegate 可能無法捕捉到 targetFrame | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> expectation 使用錯誤導致測試可能永遠等待或提前通過</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

**判斷依據**：diff 中新增的 `expectation.fulfill()` 位於 `wait(for:)` 之後，且 `decisionHandler` 內沒有 fulfill。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41</code> 測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定</summary>

`captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

**判斷依據**：diff 中新增的 `webView.load(URLRequest(url: url))` 使用外部 URL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

**判斷依據**：diff 中新增的 `XCTWaiter.wait` 呼叫未檢查回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23</code> FakeWKNavigationDelegate 可能無法捕捉到 targetFrame</summary>

在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

**判斷依據**：diff 中新增的程式碼直接使用 `targetFrame`，未處理 nil 情況。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4009 (cache hit 1536) ｜ completion tokens 1357 ｜ PR #12</sub>