<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入 https://example.com 來取得，以解決 Xcode 26.2 上測試失敗的問題。主要風險在於測試現在依賴外部網路與 WebKit 內部行為，可能導致測試不穩定或逾時；此外，helper 中的 XCTestExpectation 使用方式與既有測試結構有重複 fulfill 的疑慮。建議先確認測試在無網路環境下的行為，並修正 expectation 的處理。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴外部網路可能導致不穩定 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | expectation 重複 fulfill 可能導致測試失敗 | 0.75 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23` | FakeWKNavigationDelegate 未處理非目標 frame 的 navigationAction | 0.60 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標記為 final | 0.50 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5` | 缺少 MARK 註解組織程式碼區段 | 0.40 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴外部網路可能導致不穩定</summary>

`captureFrameAndOrigin` 會載入 `https://example.com`，若測試環境無網路或 DNS 解析失敗，`XCTWaiter.wait` 將等待至 timeout（3 秒）後回傳 nil，導致測試失敗。這使得測試結果受外部因素影響，降低可靠性。建議改為載入本地測試資源（如 `about:blank` 或內嵌 HTML），或使用 URLProtocol mock 來攔截請求。

**判斷依據**：diff 中新增的 helper 直接使用 `webView.load(URLRequest(url: url))`，且呼叫端傳入 `URL(string: "https://example.com")!`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> expectation 重複 fulfill 可能導致測試失敗</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內已呼叫 `expectation.fulfill()`，但測試結尾又呼叫一次 `expectation.fulfill()`。若 decisionHandler 被呼叫，expectation 會被 fulfill 兩次，可能導致 XCTest 拋出錯誤（「API violation - multiple calls made to -[XCTestExpectation fulfill]」）。建議移除多餘的 fulfill。

**判斷依據**：diff 中新增了 `expectation.fulfill()` 於 `wait(for:)` 之後，而 decisionHandler 內已有 `expectation.fulfill()`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23</code> FakeWKNavigationDelegate 未處理非目標 frame 的 navigationAction</summary>

`decidePolicyFor` 中直接將 `navigationAction.targetFrame` 指派給 `capturedFrame`，但若 navigationAction 的 targetFrame 為 nil（例如新視窗或下載），`capturedFrame` 會是 nil，導致 helper 回傳 nil。建議檢查 targetFrame 是否存在，或改為使用 `sourceFrame`。

**判斷依據**：diff 中新增的 delegate 方法直接使用 targetFrame，未做 nil 檢查。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標記為 final</summary>

此類別僅供測試輔助使用，且無需被繼承，建議加上 `final` 以符合專案規範 [R12]。

**判斷依據**：diff 中新增的 class 未標記 final。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5</code> 缺少 MARK 註解組織程式碼區段</summary>

此檔案包含多個邏輯區塊（helper class、delegate class、static method），但未使用 `// MARK:` 分隔，違反專案規範 [R03]。建議加入 MARK 註解以提升可讀性。

**判斷依據**：diff 中新增的檔案未見任何 MARK 註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6078 (cache hit 6016) ｜ completion tokens 1157 ｜ PR #12</sub>