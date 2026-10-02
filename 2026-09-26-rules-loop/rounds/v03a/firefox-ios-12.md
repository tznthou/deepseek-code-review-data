<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將原本以 mock 方式建立的 WKFrameInfo 與 WKSecurityOrigin 改為透過真實 WKWebView 載入 example.com 來取得，以解決 Xcode 26.2 的測試相容性問題。主要風險在於測試現在依賴網路與 WebKit 內部行為，可能導致不穩定或逾時；此外，測試程式碼中出現重複的 expectation.fulfill() 呼叫，可能造成 XCTest 錯誤。建議先修正 expectation 重複 fulfill 的問題，並評估是否可改用更穩定的方式取得測試所需的 frame 與 origin。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53` | 重複呼叫 expectation.fulfill() 可能導致測試失敗 | 0.90 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與 WebKit 內部行為，可能不穩定 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44` | XCTWaiter.wait 的結果未檢查，可能掩蓋逾時 | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12` | [R03] 缺少 MARK 註解來組織程式碼區段 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53</code> 重複呼叫 expectation.fulfill() 可能導致測試失敗</summary>

在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內已呼叫 `expectation.fulfill()`，但測試結尾又再次呼叫 `expectation.fulfill()`。XCTest 的 expectation 只能 fulfill 一次，重複呼叫會導致 API 違規錯誤（通常會 crash 或測試失敗）。請移除多餘的 `expectation.fulfill()`。

**判斷依據**：diff 中新增了 `expectation.fulfill()` 於 `wait(for:)` 之後，而 `decisionHandler` 內已有 `expectation.fulfill()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與 WebKit 內部行為，可能不穩定</summary>

`captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這使得測試依賴外部網路連線與 WebKit 的實際導航行為。在 CI 環境中若無網路或 example.com 無法存取，測試將逾時失敗；且 WebKit 的內部實作可能隨版本變動，導致測試脆弱。建議改以注入 mock 的方式提供 `WKFrameInfo` 與 `WKSecurityOrigin`，或使用其他不需真實載入的替代方案。

**判斷依據**：diff 中新增了 `webView.load(URLRequest(url: url))`，且 helper 的註解說明其依賴真實載入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44</code> XCTWaiter.wait 的結果未檢查，可能掩蓋逾時</summary>

`XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 與 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試端僅以 `XCTFail` 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果並在逾時情況下提供更明確的錯誤訊息。

**判斷依據**：diff 中新增了 `let waiter = XCTWaiter.wait(...)`，但未使用回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:12</code> [R03] 缺少 MARK 註解來組織程式碼區段</summary>

新檔案 `WebKitTestHelpers.swift` 包含多個邏輯區塊（如 helper class、static method），但未使用 `// MARK:` 註解來分隔。根據專案規範 R03，應使用 MARK 註解來組織程式碼，提升可讀性。

**判斷依據**：整個新檔案未見任何 `// MARK:` 註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6078 (cache hit 3968) ｜ completion tokens 1058 ｜ PR #12</sub>