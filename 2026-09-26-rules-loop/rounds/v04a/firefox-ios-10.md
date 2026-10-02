<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將測試從 async 改為同步、以及調整 @Sendable 標註。整體方向合理，但存在一個 blocker：測試方法改為同步後，非同步的圖片下載完成回呼可能永遠不會被等待，導致測試提前結束而無法驗證結果。此外，移除 @MainActor 標註可能導致 GCDWebServer 初始化執行緒問題，需要確認。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 同步測試方法未等待非同步下載完成，測試可能提前結束 | 0.95 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 測試方法未等待非同步決策處理器呼叫 | 0.85 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒問題 | 0.80 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | 不必要的 wrappedAction 閉包可能造成多餘的間接層 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 同步測試方法未等待非同步下載完成，測試可能提前結束</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 等待非同步下載完成，但改為同步方法後，移除了 expectation 的建立與等待。`downloadImage` 的回呼是非同步的，測試方法會立即返回，導致 XCTest 可能認為測試已完成，而回呼中的斷言可能永遠不會被執行，或測試在回呼前就結束。這會造成測試無法驗證下載結果，甚至可能導致測試通過但實際上未測試任何內容。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或將測試方法改回 async 並使用 `await fulfillment`。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 和 `await fulfillment(of: [exp], timeout: 2.0)`，且方法簽名從 `async` 改為同步。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 測試方法未等待非同步決策處理器呼叫</summary>

在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待決策處理器被呼叫，但改動後移除了 expectation 的建立與等待。`requestMediaCapturePermission` 可能非同步呼叫決策處理器，測試方法會立即返回，導致斷言可能不會被執行。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或確認該方法為同步呼叫。

**判斷依據**：diff 中移除了 `let expectation = expectation(description: "Wait for the decision handler to be called")` 和 `wait(for: [expectation])`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒問題</summary>

原本 `startMockImageServer` 標註為 `@MainActor`，並有註解說明 GCDWebServer 必須在主執行緒初始化。移除後，該方法可能從背景執行緒呼叫，導致 GCDWebServer 初始化失敗或崩潰。雖然測試方法目前是同步的，但 XCTest 可能在背景執行緒執行測試，因此風險仍然存在。

建議：確認 GCDWebServer 是否真的需要主執行緒，若需要則保留 @MainActor 並將測試方法標註為 @MainActor，或使用其他方式確保主執行緒執行。

**判斷依據**：diff 中移除了 `@MainActor` 標註及相關註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> 不必要的 wrappedAction 閉包可能造成多餘的間接層</summary>

新增的 `wrappedAction` 閉包僅呼叫 `moreButtonAction?(button)`，沒有額外邏輯，可能只是為了滿足型別檢查。這增加了程式碼複雜度，且可能影響效能（雖然微小）。

建議：確認是否可以直接傳遞 `moreButtonAction`，若型別匹配則移除 wrappedAction。

**判斷依據**：diff 中新增了 wrappedAction 閉包，並將其傳遞給 ActionButtonViewModel。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7761 (cache hit 6912) ｜ completion tokens 1216 ｜ PR #10</sub>