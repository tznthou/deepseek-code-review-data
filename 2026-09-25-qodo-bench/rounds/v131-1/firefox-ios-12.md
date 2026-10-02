<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了兩個 WebKit 的 mock 類別（MockWKFrameInfo、MockWKSecurityOrigin），改以新增的 WebKitTestHelpers 來取得真實的 WKFrameInfo 與 WKSecurityOrigin。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時；此外，testRequestMediaCaptureSuccess 中的 expectation 使用方式有誤，可能造成測試永遠等待。建議先修正 expectation 邏輯，並評估是否可改用更穩定的方式取得測試所需的物件。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待</summary>

在 testRequestMediaCaptureSuccess 中，原本的 expectation 是在 decisionHandler 內 fulfill，但修改後 decisionHandler 不再 fulfill，而是在呼叫 subject.webView 後直接呼叫 expectation.fulfill()。這會導致 expectation 在 decisionHandler 被呼叫前就 fulfill，使得 wait(for:) 立即返回，無法驗證 decisionHandler 是否真的被呼叫。若 decisionHandler 未被呼叫，測試仍會通過，失去測試意義。建議將 expectation.fulfill() 移回 decisionHandler 內。

**判斷依據**：diff 中 testRequestMediaCaptureSuccess 的 decisionHandler 已移除 expectation.fulfill()，並在 wait 後直接呼叫 expectation.fulfill()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時</summary>

captureFrameAndOrigin 會建立真實的 WKWebView 並載入 https://example.com。這使得測試依賴外部網路連線與 WebKit 的實際行為，可能因網路延遲、離線環境或 WebKit 內部變更而失敗或逾時。建議改用 local test server 或注入 mock 的 navigation delegate 來提供所需的 WKFrameInfo 與 WKSecurityOrigin，以提升測試穩定性。

**判斷依據**：diff 中新增的 WebKitTestHelpers 使用真實 URL 載入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤</summary>

XCTWaiter.wait 的回傳值未被檢查，若等待逾時，函式會回傳 nil，但呼叫端僅以 XCTFail 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果，並在逾時時提供更明確的錯誤訊息。

**判斷依據**：diff 中新增的程式碼未使用 waiter 結果。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3973 (cache hit 1408) ｜ completion tokens 863 ｜ PR #12</sub>