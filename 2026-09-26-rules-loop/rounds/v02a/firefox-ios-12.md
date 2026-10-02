<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了兩個 WebKit mock 類別，改用真實的 WKWebView 導航來取得 WKFrameInfo 與 WKSecurityOrigin，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時；此外，測試中 expectation 的使用方式有誤，可能造成誤判。建議先修正 expectation 邏輯，並考慮以更可控的方式取得測試資料。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 測試中 expectation 使用錯誤，可能導致測試永遠等待或提前通過 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter.wait 的結果未檢查，可能掩蓋逾時錯誤 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標記為 final，可能被意外繼承 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 測試中 expectation 使用錯誤，可能導致測試永遠等待或提前通過</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內不再呼叫 `expectation.fulfill()`，而是在 `wait(for:)` 之後才呼叫。這會造成 `wait(for:)` 等待的 expectation 永遠不會被 fulfill，導致測試逾時失敗。此外，`wait(for:)` 之後的 `expectation.fulfill()` 是多餘的，且可能掩蓋非同步完成的問題。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除 `wait(for:)` 之後的呼叫。

**判斷依據**：diff 中 `decisionHandler` 閉包內沒有 `expectation.fulfill()`，且 `wait(for:)` 之後才呼叫 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時</summary>

`captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對網路連線和 WebKit 內部實作的依賴。在 CI 環境中，網路可能不可用或速度緩慢，導致測試逾時或失敗。此外，WebKit 的導航行為可能因版本而異，降低測試的可靠性。

建議考慮使用更可控的方式取得 `WKFrameInfo` 和 `WKSecurityOrigin`，例如使用 `WKWebView` 的 `loadHTMLString` 搭配自訂 scheme，或使用其他 mock 策略。

**判斷依據**：diff 中新增的 `WebKitTestHelpers` 使用 `webView.load(URLRequest(url: url))` 載入真實 URL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter.wait 的結果未檢查，可能掩蓋逾時錯誤</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）未被檢查。如果等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中會以 `XCTFail` 處理。然而，未檢查結果可能導致測試在逾時後仍繼續執行，浪費時間。

建議檢查 `waiter` 的結果，若為 `.timedOut` 則直接回傳 nil 或觸發失敗。

**判斷依據**：diff 中 `let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)` 未使用回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標記為 final，可能被意外繼承</summary>

`FakeWKNavigationDelegate` 是一個測試輔助類別，不應被繼承。根據專案規範 R12，應標記為 `final`。

**判斷依據**：diff 中 `class FakeWKNavigationDelegate` 缺少 `final` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6068 (cache hit 1536) ｜ completion tokens 1227 ｜ PR #12</sub>