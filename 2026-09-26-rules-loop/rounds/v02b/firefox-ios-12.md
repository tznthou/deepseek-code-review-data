<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了無法在 Xcode 26.2 下使用的 WebKit mock（MockWKFrameInfo、MockWKSecurityOrigin），改以 WebKitTestHelpers 透過真實 WKWebView 載入來取得 WKFrameInfo 與 WKSecurityOrigin。主要風險在於測試現在依賴真實網路與 WebKit 內部行為，可能導致不穩定或逾時；此外，testRequestMediaCaptureSuccess 中的 expectation 處理有邏輯錯誤，可能造成測試永遠等待。建議先修正 expectation 邏輯，並評估網路依賴對 CI 的影響。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:41` | testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤，可能導致測試永遠等待 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與 WebKit 內部行為，可能導致不穩定或逾時 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter.wait 的結果未檢查，可能掩蓋逾時錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:41</code> testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤，可能導致測試永遠等待</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 閉包內不再呼叫 `expectation.fulfill()`，而是在 `wait(for:)` 之後才呼叫 `expectation.fulfill()`。這會造成 `wait(for:)` 等待的 expectation 永遠不會被滿足，測試將在 timeout 後失敗。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 閉包內，並移除 `wait(for:)` 之後的呼叫。

**判斷依據**：diff 中顯示原本的 `expectation.fulfill()` 被從 decisionHandler 中移除，並在 wait 之後呼叫，這會導致 wait 永遠等待。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與 WebKit 內部行為，可能導致不穩定或逾時</summary>

`captureFrameAndOrigin` 會載入真實的 `https://example.com`，這使得測試依賴外部網路連線。在 CI 環境中若無網路或網路不穩定，測試將逾時失敗。此外，WebKit 的內部行為可能因版本而異，導致取得的 frame/origin 不符合預期。

建議改為使用本地 HTML 字串或 data URL 來避免外部依賴，或使用 mock 方式（若可行）來隔離測試。

**判斷依據**：diff 中新增的 helper 使用 `webView.load(URLRequest(url: url))` 載入外部 URL，且測試中傳入 `https://example.com`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter.wait 的結果未檢查，可能掩蓋逾時錯誤</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值未被檢查。若等待逾時，函式仍會回傳 nil，但測試可能無法明確指出是逾時還是其他原因。建議檢查回傳值，並在逾時情況下提供更明確的錯誤訊息。

**判斷依據**：diff 中新增的 helper 未使用 waiter 的結果。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6068 (cache hit 6016) ｜ completion tokens 965 ｜ PR #12</sub>