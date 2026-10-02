<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入網頁來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或逾時；此外，testRequestMediaCaptureSuccess 中的 expectation 使用方式有誤，可能造成測試永遠等待。建議先修正 expectation 邏輯，並考慮以更穩定的方式取得測試所需的 frame 與 origin。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter.wait 的結果未被檢查，可能掩蓋逾時錯誤 | 0.75 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未處理其他 navigation delegate 方法，可能導致行為不完整 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待</summary>

在 testRequestMediaCaptureSuccess 中，原本的 expectation 是在 decisionHandler 內被 fulfill，但修改後 decisionHandler 不再 fulfill expectation，而是在呼叫 webView 方法後直接呼叫 expectation.fulfill()。這會導致 expectation 在 decisionHandler 被呼叫前就被 fulfill，使得 wait(for:) 立即返回，但 decisionHandler 可能尚未執行，造成測試邏輯錯誤。更嚴重的是，如果 decisionHandler 從未被呼叫，測試也不會失敗，因為 expectation 已經被 fulfill。建議將 expectation.fulfill() 移回 decisionHandler 內。

**判斷依據**：diff 中顯示 decisionHandler 內已移除 expectation.fulfill()，且在 wait(for:) 之後才呼叫 expectation.fulfill()。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時</summary>

captureFrameAndOrigin 方法會實際載入一個 URL（目前為 https://example.com），這使得測試依賴網路連線與 WebKit 的實際行為。在 CI 環境中，網路可能不可用或速度緩慢，導致測試逾時或失敗。此外，載入真實網頁可能觸發額外的網路請求或內容處理，增加測試的不確定性。建議考慮使用本地 HTML 或 data URL 來避免外部依賴，或使用其他方式建立所需的 WKFrameInfo 與 WKSecurityOrigin。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 使用 webView.load(URLRequest(url: url)) 載入真實 URL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter.wait 的結果未被檢查，可能掩蓋逾時錯誤</summary>

在 captureFrameAndOrigin 中，呼叫 XCTWaiter.wait(for:timeout:) 後未檢查其回傳值。如果等待逾時，方法會直接回傳 nil，但測試中會以 XCTFail 處理 nil 回傳，因此仍會失敗。然而，未檢查 waiter 結果可能導致在非預期情況下（例如 expectation 被 fulfill 但 capturedFrame 或 capturedOrigin 為 nil）無法提供明確的錯誤訊息。建議檢查 waiter 結果並在逾時或失敗時提供更詳細的診斷資訊。

**判斷依據**：diff 中新增的程式碼未使用 waiter 變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未處理其他 navigation delegate 方法，可能導致行為不完整</summary>

FakeWKNavigationDelegate 僅實作了 decidePolicyFor navigationAction，但未實作其他 WKNavigationDelegate 方法。在實際載入網頁時，WebKit 可能會呼叫其他 delegate 方法（例如 didStartProvisionalNavigation、didFinishNavigation 等），若未實作可能不會有直接影響，但若未來測試需要驗證這些行為，則需要擴充。目前影響不大，但建議考慮使用更完整的 mock 或明確標註僅用於特定情境。

**判斷依據**：diff 中新增的 FakeWKNavigationDelegate 僅實作一個 delegate 方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4869 (cache hit 4864) ｜ completion tokens 1438 ｜ PR #12</sub>