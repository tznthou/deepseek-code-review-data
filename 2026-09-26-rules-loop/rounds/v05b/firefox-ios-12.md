<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過實際載入 https://example.com 來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致不穩定或失敗；此外，helper 中未使用 XCTWaiter 的結果、測試中 expectation 的 fulfill 時機有誤，以及部分程式碼違反專案規範（如缺少 MARK 註解、未使用 @MainActor）。建議先修正測試邏輯與網路依賴問題，再考慮合併。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 測試依賴真實網路與外部服務，可能導致不穩定或失敗 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | 未檢查 XCTWaiter 結果，可能誤判成功 | 0.90 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束 | 0.85 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12` | [R03] 缺少 MARK 註解來組織程式碼區段 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12` | [R09] UI 相關程式碼未標註 @MainActor | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12` | [R14] 公開 API 缺少文件註解 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 測試依賴真實網路與外部服務，可能導致不穩定或失敗</summary>

`WebKitTestHelpers.captureFrameAndOrigin` 會實際載入 `https://example.com`，這使得測試依賴外部網路連線與 WebKit 的實際行為。在 CI 環境中若無網路或 example.com 無法存取，測試將失敗；此外，載入真實網頁可能引入非確定性（如載入時間、內容變動），導致測試不穩定。建議改為使用本機測試伺服器或注入 mock 的 navigation action，避免外部依賴。

**判斷依據**：diff 中新增了對 `WebKitTestHelpers.captureFrameAndOrigin` 的呼叫，且 helper 內部使用 `webView.load(URLRequest(url: url))` 載入真實 URL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> 未檢查 XCTWaiter 結果，可能誤判成功</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值未被檢查。若等待逾時，`delegate.capturedFrame` 與 `capturedOrigin` 可能為 nil，但函式仍會回傳 nil，導致呼叫端 `XCTFail`。然而，若等待因其他原因（如中斷）提前結束，也可能回傳非 `.completed` 的結果，此時應視為失敗。建議檢查 waiter 結果，若不是 `.completed` 則直接回傳 nil 或拋出錯誤。

**判斷依據**：diff 中新增了 `let waiter = XCTWaiter.wait(...)`，但未使用回傳值。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束</summary>

在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致測試在呼叫 `subject.webView(...)` 後立即 fulfill expectation，而 `decisionHandler` 可能尚未被呼叫，使得 `XCTAssertEqual` 可能未被執行。應將 `expectation.fulfill()` 移回 `decisionHandler` 內，確保斷言有被執行。

**判斷依據**：diff 中顯示原本在 decisionHandler 內的 `expectation.fulfill()` 被移出，並在 `wait(for:)` 後呼叫。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12</code> [R03] 缺少 MARK 註解來組織程式碼區段</summary>

此檔案包含多個邏輯區塊（如 FakeWKNavigationDelegate、captureFrameAndOrigin），但未使用 `// MARK:` 註解來分隔。根據專案規範 R03，應使用 MARK 註解來組織程式碼，提升可讀性。

**判斷依據**：diff 中新增的檔案沒有 MARK 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12</code> [R09] UI 相關程式碼未標註 @MainActor</summary>

此 helper 涉及 WKWebView 的操作，屬於 UI 相關程式碼，但未標註 `@MainActor`。根據專案規範 R09，UI 相關程式碼應標註 `@MainActor` 以確保執行緒安全。

**判斷依據**：diff 中新增的類別未標註 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12</code> [R14] 公開 API 缺少文件註解</summary>

`WebKitTestHelpers` 及其方法 `captureFrameAndOrigin` 是公開的（internal），但缺少文件註解。根據專案規範 R14，公開 API 應有 `///` 文件註解。

**判斷依據**：diff 中新增的類別和方法沒有文件註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6020 (cache hit 6016) ｜ completion tokens 1451 ｜ PR #12</sub>