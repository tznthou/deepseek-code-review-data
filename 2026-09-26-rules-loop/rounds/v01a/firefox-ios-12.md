<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入網頁來取得，以解決 Xcode 26.2 上測試失敗的問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時；此外，測試程式碼中出現重複的 expectation.fulfill() 呼叫，可能造成 XCTest 錯誤。建議先修正測試邏輯，並考慮使用更輕量的方式取得 frame 與 origin。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | 重複呼叫 expectation.fulfill() 可能導致測試失敗 | 0.90 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與 WebKit 行為，可能不穩定 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | 未檢查 XCTWaiter 結果，可能誤判成功 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標記為 final | 0.60 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12` | 缺少 MARK 註解組織程式碼區段 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> 重複呼叫 expectation.fulfill() 可能導致測試失敗</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內已呼叫 `expectation.fulfill()`，但測試方法結尾又再次呼叫 `expectation.fulfill()`。這會造成 expectation 被 fulfill 兩次，XCTest 會拋出錯誤（「API violation - multiple calls made to -[XCTestExpectation fulfill]」）。

建議移除測試方法結尾的 `expectation.fulfill()`，只保留 `decisionHandler` 內的呼叫。

**判斷依據**：diff 中新增的 `expectation.fulfill()` 位於 `wait(for:)` 之後，而 `decisionHandler` 內已有 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與 WebKit 行為，可能不穩定</summary>

`captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這使得測試依賴外部網路連線與 WebKit 的實際行為。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。

建議改用 `WKWebView` 載入本地 HTML 或使用 `about:blank`，或考慮使用其他方式建立 `WKFrameInfo` 與 `WKSecurityOrigin`（例如透過 `WKWebView` 的 `loadHTMLString`）。

**判斷依據**：diff 中新增的 `webView.load(URLRequest(url: url))` 使用外部 URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> 未檢查 XCTWaiter 結果，可能誤判成功</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值未被檢查。若等待逾時，`delegate.capturedFrame` 與 `capturedOrigin` 可能為 nil，但函式仍會回傳 nil，導致測試失敗。建議檢查 waiter 結果，並在逾時或失敗時提供更明確的錯誤訊息。

**判斷依據**：diff 中新增的 `XCTWaiter.wait` 呼叫未使用回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標記為 final</summary>

根據專案規範 R12，不應被繼承的類別應標記為 `final`。`FakeWKNavigationDelegate` 是測試輔助類別，不應被繼承，建議加上 `final`。

**判斷依據**：diff 中新增的類別宣告缺少 `final`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12</code> 缺少 MARK 註解組織程式碼區段</summary>

根據專案規範 R03，程式碼應使用 MARK 註解組織邏輯區段。此檔案包含類別與靜態方法，但未使用 MARK 分隔，建議加入 `// MARK: -` 來提升可讀性。

**判斷依據**：diff 中新增的類別未使用 MARK 註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6068 (cache hit 3968) ｜ completion tokens 1199 ｜ PR #12</sub>