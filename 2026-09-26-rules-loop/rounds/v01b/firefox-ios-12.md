<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 移除了兩個 WebKit mock 類別，改以新的 WebKitTestHelpers 透過真實 WKWebView 載入 https://example.com 來取得 WKFrameInfo 與 WKSecurityOrigin。主要風險在於測試現在依賴外部網路與 WebKit 內部行為，可能導致測試不穩定或逾時；此外，測試方法中 expectation 的 fulfill 時機有誤，可能造成測試永遠等待或提前結束。建議先修正 expectation 邏輯，並考慮以本地 HTML 或資料 URL 取代外部請求。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41` | 測試依賴外部網路，可能導致不穩定或失敗 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter 結果未檢查，可能掩蓋逾時錯誤 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5` | [R01] 新檔案缺少 Mozilla Public License 標頭 | 0.90 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標記為 final | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待</summary>

在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `subject.webView(...)` 呼叫之後，而不是在 `decisionHandler` 閉包內。這會導致 expectation 在 decisionHandler 被呼叫前就 fulfill，使得 `wait(for:)` 可能立即返回，但決策處理器尚未執行，斷言可能未被執行。更糟的是，如果 decisionHandler 從未被呼叫，測試也不會失敗，因為 expectation 已經被 fulfill。應將 `expectation.fulfill()` 移回 `decisionHandler` 閉包內，與其他測試方法一致。

**判斷依據**：diff 中 `testRequestMediaCaptureSuccess` 的 decisionHandler 閉包內已移除 `expectation.fulfill()`，但在 `wait(for:)` 之後新增了一行 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41</code> 測試依賴外部網路，可能導致不穩定或失敗</summary>

`captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試不穩定。建議改用本地 HTML 內容（例如 `loadHTMLString`）或資料 URL，以消除對外部網路的依賴。

**判斷依據**：diff 中新增的 helper 方法直接載入傳入的 URL，而測試中傳入的是 `https://example.com`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter 結果未檢查，可能掩蓋逾時錯誤</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，方法仍會繼續執行並嘗試從 delegate 取得 capturedFrame 和 capturedOrigin，若為 nil 則回傳 nil。這可能導致測試在逾時後才失敗，且錯誤訊息不夠明確。建議檢查 waiter 結果，若為 `.timedOut` 則直接 `XCTFail` 並回傳 nil。

**判斷依據**：diff 中新增的 helper 方法呼叫 `XCTWaiter.wait` 但未使用其回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:5</code> [R01] 新檔案缺少 Mozilla Public License 標頭</summary>

新增的 `WebKitTestHelpers.swift` 檔案開頭沒有包含 Mozilla Public License v2.0 標頭。根據專案規範 R01，所有 Swift 檔案必須包含標準 MPL 標頭。請在檔案最上方加入：
```
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
```

**判斷依據**：diff 中新增檔案的前兩行是 import 陳述式，沒有 license header。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標記為 final</summary>

根據專案規範 R12，不應被繼承的類別應標記為 `final`。此處 `FakeWKNavigationDelegate` 是測試輔助類別，沒有繼承需求，建議加上 `final`。

**判斷依據**：diff 中新增的類別宣告缺少 `final` 修飾詞。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6068 (cache hit 6016) ｜ completion tokens 1391 ｜ PR #12</sub>