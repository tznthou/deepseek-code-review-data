<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 刪除了無法在 Xcode 26.2 下正常運作的 MockWKFrameInfo 與 MockWKSecurityOrigin，改以 WebKitTestHelpers 透過真實 WKWebView 導航來取得 WKFrameInfo 與 WKSecurityOrigin。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時；此外，testRequestMediaCaptureSuccess 中的 expectation 使用方式有誤，可能造成測試永遠等待或提前通過。建議修正 expectation 邏輯，並考慮使用本地 HTML 或攔截請求來避免外部依賴。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴外部網路可能導致不穩定 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter.wait 的結果未檢查 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23` | FakeWKNavigationDelegate 可能無法捕捉 targetFrame | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤</summary>

在 testRequestMediaCaptureSuccess 中，decisionHandler 閉包內沒有呼叫 expectation.fulfill()，而是在呼叫 subject.webView(...) 之後直接呼叫 expectation.fulfill()。這會導致測試在 decisionHandler 被呼叫前就完成等待，無法驗證 decisionHandler 是否被呼叫及其內容。若 decisionHandler 從未被呼叫，測試仍會通過，失去測試意義。

建議將 expectation.fulfill() 移回 decisionHandler 閉包內，並移除多餘的 expectation.fulfill()。

**判斷依據**：diff 中新增的 testRequestMediaCaptureSuccess 顯示 decisionHandler 內沒有 expectation.fulfill()，且在 wait 之後才呼叫 expectation.fulfill()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴外部網路可能導致不穩定</summary>

captureFrameAndOrigin 使用真實的 WKWebView 載入 https://example.com，這需要網路連線。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。建議改用本地 HTML 字串或攔截請求的方式，避免外部依賴。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 37 行載入外部 URL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter.wait 的結果未檢查</summary>

XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 40-44 行未檢查 waiter 結果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23</code> FakeWKNavigationDelegate 可能無法捕捉 targetFrame</summary>

在 decidePolicyFor navigationAction 中，navigationAction.targetFrame 可能為 nil（例如新視窗或某些重定向），此時 capturedFrame 為 nil，導致測試失敗。建議處理 targetFrame 為 nil 的情況，或使用其他 delegate 方法。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 15-17 行直接使用 targetFrame，未檢查 nil。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4009 (cache hit 3968) ｜ completion tokens 1163 ｜ PR #12</sub>