<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入 https://example.com 來取得，以解決 Xcode 26.2 上的測試失敗。主要風險在於測試現在依賴真實網路與 WebKit 內部行為，可能導致不穩定或逾時。此外，WebKitTestHelpers 中的 XCTestExpectation 使用方式有誤，可能造成測試永遠等待。建議先修正 expectation 的建立與 fulfill 時機，並考慮使用更穩定的方式取得測試所需的 frame 與 origin。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTestExpectation 使用錯誤，可能導致測試永遠等待 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路，可能導致不穩定或逾時 | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:41` | 測試中的 expectation 可能永遠不會被 fulfill | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | 未處理 XCTWaiter 結果，可能導致測試誤判 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:14` | [R11] 屬性缺少明確的存取控制 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5` | [R01] 缺少 Mozilla Public License Header | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTestExpectation 使用錯誤，可能導致測試永遠等待</summary>

在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後傳入 delegate，但 delegate 在 `decidePolicyFor` 中呼叫 `expect.fulfill()`。然而，`XCTWaiter.wait(for:timeout:)` 會等待 expectation 被 fulfill 或逾時。此處的 expectation 是在 helper 函式內建立，但測試方法中也建立了自己的 expectation 並呼叫 `wait(for:)`。這可能導致測試中的 expectation 永遠不會被 fulfill，因為 helper 內部的 expectation 已經被 fulfill，但測試中的 expectation 沒有被 fulfill。此外，在 `testRequestMediaCaptureSuccess` 中，測試在呼叫 `subject.webView` 後才呼叫 `expectation.fulfill()`，但 `decisionHandler` 內沒有 fulfill，這會造成測試永遠等待。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 43 行，以及 WKUIHandlerTests.swift 中測試方法的 expectation 使用方式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路，可能導致不穩定或逾時</summary>

`captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或速度慢，導致測試逾時或失敗。建議使用本地 HTML 或 data URL 來避免外部依賴。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 44 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:41</code> 測試中的 expectation 可能永遠不會被 fulfill</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView` 後才呼叫。這可能導致 `wait(for:)` 永遠等待，因為 expectation 在等待開始前就被 fulfill 了。正確做法是在 `decisionHandler` 內 fulfill。

**判斷依據**：diff 中 WKUIHandlerTests.swift 第 41 行附近的變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> 未處理 XCTWaiter 結果，可能導致測試誤判</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值未被檢查。如果等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，但函式仍會回傳 nil，測試會失敗。然而，如果等待結果是 `.incorrectOrder` 或其他狀態，可能會有非預期的行為。建議檢查 waiter 結果並記錄錯誤。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 45 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:14</code> [R11] 屬性缺少明確的存取控制</summary>

`FakeWKNavigationDelegate` 中的 `expect`、`capturedFrame`、`capturedOrigin` 屬性沒有明確的存取控制修飾詞。根據規範 R11，應明確標示為 `private` 或 `internal`。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 16-18 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5</code> [R01] 缺少 Mozilla Public License Header</summary>

新增的 WebKitTestHelpers.swift 檔案開頭沒有包含 Mozilla Public License v2.0 header。根據規範 R01，所有 Swift 檔案都必須包含此 header。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 1 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6020 (cache hit 3968) ｜ completion tokens 1473 ｜ PR #12</sub>