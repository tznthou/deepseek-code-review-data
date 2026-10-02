<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過實際載入網頁來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時。此外，測試中 expectation 的使用方式有誤，可能造成誤判。建議先修正測試邏輯，並考慮更穩定的取得方式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:40` | 測試中 expectation 使用錯誤，可能導致測試永遠通過或逾時 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路，可能導致不穩定或失敗 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | 未處理逾時情況，可能導致測試失敗但無明確訊息 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:35` | FakeWKNavigationDelegate 未保留 webView 強參考，可能導致提前釋放 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:40</code> 測試中 expectation 使用錯誤，可能導致測試永遠通過或逾時</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 閉包內沒有呼叫 `expectation.fulfill()`，而是在 `wait(for:)` 之後才呼叫。這會導致 `wait(for:)` 等待 expectation 直到逾時，測試必定失敗（或花費大量時間）。應將 `expectation.fulfill()` 移回閉包內。

**判斷依據**：diff 中 `decisionHandler` 閉包內沒有 `expectation.fulfill()`，且 `expectation.fulfill()` 被移到 `wait(for:)` 之後。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路，可能導致不穩定或失敗</summary>

`captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入真實網頁（例如 `https://example.com`）。這使得測試依賴外部網路連線，在無網路或網路不穩的 CI 環境中可能失敗或逾時。建議改用本地 HTML 字串或 mock 網路回應，以確保測試的可靠性。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 30 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> 未處理逾時情況，可能導致測試失敗但無明確訊息</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值未被檢查。若逾時，`capturedFrame` 或 `capturedOrigin` 可能為 nil，函式回傳 nil，呼叫端會執行 `XCTFail`。但若 waiter 回傳非 `.completed`（例如 `.timedOut`），應提供更明確的錯誤訊息。建議檢查 waiter 結果並記錄。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 34-38 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:35</code> FakeWKNavigationDelegate 未保留 webView 強參考，可能導致提前釋放</summary>

`captureFrameAndOrigin` 中建立的 `webView` 是區域變數，且 delegate 未持有 webView 的強參考。在非同步載入期間，webView 可能被釋放，導致 delegate 方法不會被呼叫。建議將 webView 儲存在 delegate 中或使用靜態變數延長生命週期。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 15-19 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3973 (cache hit 3968) ｜ completion tokens 1173 ｜ PR #12</sub>