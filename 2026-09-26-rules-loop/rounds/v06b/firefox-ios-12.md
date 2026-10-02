<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入 https://example.com 來取得，以解決 Xcode 26.2 上的測試失敗。主要風險在於測試現在依賴外部網路與 WebKit 的非同步行為，可能導致測試不穩定或離線環境失敗。此外，WebKitTestHelpers 中的 XCTWaiter 結果未被檢查，且測試中 expectation 的 fulfill 時機有誤，可能造成誤判。建議先修正測試的同步邏輯，並考慮使用更穩定的方式取得 frame/origin。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | 測試 expectation 在 decisionHandler 外被 fulfill，可能導致測試提前通過 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter 的結果未被檢查，可能導致測試在超時後仍繼續執行 | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴外部網路與真實 WebKit 行為，可能導致不穩定 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未實作所有必要的 WKNavigationDelegate 方法 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> 測試 expectation 在 decisionHandler 外被 fulfill，可能導致測試提前通過</summary>

在 `testRequestMediaCaptureSuccess` 中，原本的 `expectation.fulfill()` 被移出 decisionHandler，改在 `wait(for:)` 之後呼叫。這使得測試不再等待 decisionHandler 被呼叫，即使 `subject.webView` 從未呼叫 decisionHandler，測試也會通過。這會讓測試失去驗證功能，可能隱藏回歸。

建議將 `expectation.fulfill()` 移回 decisionHandler 內，並移除 `wait` 之後的 fulfill。

**判斷依據**：diff 中顯示原本在 decisionHandler 內的 `expectation.fulfill()` 被刪除，並在 `wait(for:)` 之後新增 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter 的結果未被檢查，可能導致測試在超時後仍繼續執行</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值被忽略。如果等待超時（例如網路問題或 WebKit 未觸發 delegate），`capturedFrame` 和 `capturedOrigin` 可能為 nil，但函式仍會回傳 nil，呼叫端會以 `XCTFail` 處理。然而，若 delegate 在超時後才被呼叫，可能造成非預期的狀態。建議檢查 waiter 結果，若為 `.timedOut` 則直接回傳 nil 或記錄錯誤。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 43 行呼叫 `XCTWaiter.wait` 但未使用回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴外部網路與真實 WebKit 行為，可能導致不穩定</summary>

`captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 或離線環境中，此請求可能失敗或超時，導致測試不穩定。此外，WebKit 的導航行為可能因系統版本而異，增加測試的脆弱性。建議考慮使用 local HTML 或 data URL 來避免外部依賴，或使用其他方式建立所需的 frame/origin。

**判斷依據**：diff 中新增的 `WebKitTestHelpers.swift` 第 38 行載入外部 URL。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未實作所有必要的 WKNavigationDelegate 方法</summary>

`FakeWKNavigationDelegate` 僅實作 `decidePolicyFor`，但未實作其他 delegate 方法（如 `didFinish`、`didFail`）。在某些情況下，WebKit 可能要求 delegate 處理其他回呼，若未實作可能導致行為未定義或錯誤。建議至少實作 `didFail` 以處理載入失敗，並在失敗時 fulfill expectation 以避免測試卡住。

**判斷依據**：diff 中新增的 `FakeWKNavigationDelegate` 類別僅包含一個 delegate 方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6058 (cache hit 6016) ｜ completion tokens 1192 ｜ PR #12</sub>