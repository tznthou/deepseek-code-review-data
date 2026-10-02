<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入網頁來取得，以解決 Xcode 26.2 上測試失敗的問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時；此外，測試程式碼中 expectation 的使用方式有誤，可能造成誤判。建議先修正 expectation 邏輯，並考慮以注入方式提供測試資料以提升穩定性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:48` | expectation 使用錯誤可能導致測試誤判 | 0.90 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路可能導致不穩定 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter 等待結果未檢查 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標示為 final | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:48</code> expectation 使用錯誤可能導致測試誤判</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在 `wait(for:)` 之後才呼叫。這會造成即使 decision handler 從未被呼叫，測試仍可能通過（因為 expectation 在等待後被手動 fulfill）。建議將 `expectation.fulfill()` 移回 decision handler 內，並移除等待後的呼叫。

**判斷依據**：diff 中 `testRequestMediaCaptureSuccess` 的 decisionHandler 內沒有 fulfill，且等待後才 fulfill。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路可能導致不穩定</summary>

`captureFrameAndOrigin` 會實際載入 `https://example.com`，這需要網路連線且依賴外部服務。在 CI 或無網路環境下可能失敗或逾時，造成測試不穩定。建議改用本地測試伺服器或注入假的 navigation action 來取得 frame 與 origin。

**判斷依據**：diff 中新增的 helper 直接呼叫 `webView.load` 載入外部 URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter 等待結果未檢查</summary>

`XCTWaiter.wait` 的回傳值未被檢查，若等待逾時，仍可能回傳 nil 並讓測試失敗，但錯誤訊息不夠明確。建議檢查 waiter 結果，並在逾時或失敗時提供更清楚的診斷。

**判斷依據**：diff 中未使用 waiter 回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標示為 final</summary>

此類別僅供測試使用，且無需繼承，建議加上 `final` 以符合專案慣例（R12）。

**判斷依據**：diff 中新增的類別未標示 final。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6058 (cache hit 3968) ｜ completion tokens 972 ｜ PR #12</sub>