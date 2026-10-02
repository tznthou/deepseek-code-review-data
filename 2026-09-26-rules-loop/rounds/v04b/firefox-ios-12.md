<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入 https://example.com 來取得。此舉可解決 Xcode 26.2 的相容性問題，但引入了對外部網路的依賴，可能導致測試不穩定或離線環境失敗。此外，測試程式碼中 expectation 的 fulfill 時機有誤，可能造成測試永遠等待或提前結束。建議先修正 expectation 邏輯，並考慮以本地 HTML 或更可靠的方式取得 frame/origin。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待或提前結束 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴外部網路，可能導致不穩定或離線失敗 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | 未處理 XCTWaiter 結果，可能掩蓋逾時錯誤 | 0.75 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5` | 缺少 MPL 標頭 | 0.90 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標記為 final | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待或提前結束</summary>

在 `testRequestMediaCaptureSuccess` 中，`expectation` 原本應在 `decisionHandler` 內被 fulfill，但現在被移到 `wait(for:)` 之後。這會造成 `wait(for:)` 永遠等待直到 timeout，因為 `expectation` 在等待前從未被 fulfill。此外，在 `wait(for:)` 之後才呼叫 `expectation.fulfill()` 是無效的，因為 expectation 已經因為 timeout 而失敗。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除 `wait(for:)` 之後的呼叫。

**判斷依據**：diff 中顯示原本在 decisionHandler 內的 `expectation.fulfill()` 被移除，並在 `wait(for:)` 之後新增了一行 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴外部網路，可能導致不穩定或離線失敗</summary>

`captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 或離線環境中，此請求可能失敗或逾時，導致測試不穩定。建議改用本地 HTML 字串或 `about:blank` 來觸發 navigation，以取得 frame 和 origin，避免外部依賴。

**判斷依據**：helper 中直接載入傳入的 URL，而測試中傳入的是 `https://example.com`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> 未處理 XCTWaiter 結果，可能掩蓋逾時錯誤</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值未被檢查。如果等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中會以 `XCTFail` 處理。然而，若 waiter 因其他原因失敗（例如中斷），也可能回傳 nil，導致誤判。建議檢查 waiter 結果並在非 `.completed` 時提供更明確的錯誤訊息。

**判斷依據**：helper 中未使用 waiter 的結果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5</code> 缺少 MPL 標頭</summary>

新檔案 `WebKitTestHelpers.swift` 未包含 Mozilla Public License 標頭。根據專案規範 R01，所有 Swift 檔案必須包含 MPL 標頭。

**判斷依據**：檔案開頭直接是 import，沒有 license header。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標記為 final</summary>

此類別僅用於測試，且不應被繼承。根據專案規範 R12，應標記為 `final` 以提升效能並防止意外繼承。

**判斷依據**：類別宣告缺少 `final` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4856 (cache hit 4736) ｜ completion tokens 1183 ｜ PR #12</sub>