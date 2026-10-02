<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 刪除了兩個 mock 類別（MockWKFrameInfo、MockWKSecurityOrigin），改以 WebKitTestHelpers 在真實 WKWebView 中取得 WKFrameInfo 與 WKSecurityOrigin，並更新三個測試方法。主要風險在於測試現在依賴真實網路與 WebKit 行為，可能導致測試不穩定或失敗；此外，helper 中的 XCTestExpectation 使用方式有誤，可能造成測試永遠等待或提前通過。建議修正 expectation 的建立與等待邏輯，並考慮使用 local HTML 或 data URL 以避免外部網路依賴。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:36` | XCTestExpectation 使用錯誤導致測試可能永遠等待或提前通過 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42` | 測試依賴真實網路與外部服務，可能導致不穩定或失敗 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:41` | 測試中 expectation 的 fulfill 時機可能不正確 | 0.80 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13` | FakeWKNavigationDelegate 未標記為 final | 0.70 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:1` | 缺少 MARK 註解組織程式碼區段 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:36</code> XCTestExpectation 使用錯誤導致測試可能永遠等待或提前通過</summary>

在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後傳入 delegate，但 delegate 在 `decidePolicyFor` 中呼叫 `expect.fulfill()`。然而，`XCTWaiter.wait(for:timeout:)` 是在建立 expectation 之後才呼叫，且 expectation 並未與任何測試案例綁定。這可能導致兩種問題：
1. 如果 `decidePolicyFor` 在 `wait` 之前被呼叫（例如 WebKit 同步處理），則 `fulfill()` 會發生在 expectation 尚未被等待時，之後 `wait` 將永遠等待直到 timeout。
2. 如果測試案例本身也有其他 expectation，此 expectation 未正確關聯可能導致測試提前結束或無法正確等待。
建議改為在測試案例中建立 expectation，並將 fulfillment 邏輯直接放在測試的 decision handler 中，或使用 `XCTWaiter` 搭配 `expectation(description:)` 並確保在呼叫 `wait` 前 expectation 尚未被 fulfill。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 42 行附近，`XCTestExpectation` 的建立與 `XCTWaiter.wait` 的使用方式不符合 XCTest 的典型模式，且 delegate 中的 `fulfill()` 可能在 `wait` 之前被呼叫。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42</code> 測試依賴真實網路與外部服務，可能導致不穩定或失敗</summary>

`captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入真實 URL（如 `https://example.com`）。這使得測試依賴網路連線與外部服務可用性，可能因網路延遲、防火牆或服務變更而失敗。建議改用 local HTML 字串或 data URL 來觸發 navigation，以確保測試的獨立性與穩定性。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 38 行，直接載入外部 URL。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:41</code> 測試中 expectation 的 fulfill 時機可能不正確</summary>

在 `testRequestMediaCaptureSuccess` 中，原本的 decision handler 內會呼叫 `expectation.fulfill()`，但修改後 decision handler 不再 fulfill，而是在呼叫 `subject.webView` 之後才呼叫 `expectation.fulfill()`。這可能導致測試在 decision handler 尚未被呼叫時就提前通過，或因為 expectation 未被正確等待而失敗。建議將 `expectation.fulfill()` 保留在 decision handler 內，以確保測試等待非同步回呼完成。

**判斷依據**：diff 中 WKUIHandlerTests.swift 第 41 行附近，decision handler 不再 fulfill expectation，而是在 wait 之後才 fulfill。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:13</code> FakeWKNavigationDelegate 未標記為 final</summary>

根據專案規範 R12，不應被繼承的類別應標記為 final。`FakeWKNavigationDelegate` 是一個測試輔助類別，沒有繼承需求，建議加上 `final` 修飾詞。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 第 12 行，類別宣告缺少 final。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:1</code> 缺少 MARK 註解組織程式碼區段</summary>

根據專案規範 R03，程式碼區段應使用 MARK 註解組織。此檔案包含多個邏輯區塊（helper class、delegate class），建議加上 MARK 註解以提升可讀性。

**判斷依據**：diff 中新增的 WebKitTestHelpers.swift 開頭，未見 MARK 註解。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4856 (cache hit 3968) ｜ completion tokens 1623 ｜ PR #12</sub>