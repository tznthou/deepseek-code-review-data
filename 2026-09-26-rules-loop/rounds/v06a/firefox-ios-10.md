<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除實驗性並發功能旗標、將 swift-tools-version 提升至 6.2、調整測試以使用同步等待、以及為特定屬性加上 nonisolated(unsafe) 或 @Sendable 標註。整體方向合理，但需注意：移除 @MainActor 於 startMockImageServer 可能導致 GCDWebServer 初始化執行緒問題；移除測試中的 expectation 可能造成測試提前結束或無法驗證非同步行為；以及移除 MPL 標頭違反專案規範。建議修正上述問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | [R09] 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27` | 移除 expectation 可能導致測試提前結束或無法驗證非同步結果 | 0.75 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:1` | [R01] 移除 Mozilla Public License 標頭 | 0.90 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42` | 移除 expectation 可能導致測試無法驗證決策處理器被呼叫 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> [R09] 移除 @MainActor 可能導致 GCDWebServer 初始化於背景執行緒</summary>

原本的註解明確指出 GCDWebServer 必須在主執行緒初始化，否則可能崩潰。移除 @MainActor 後，若測試在背景執行緒呼叫 startMockImageServer，可能導致當機。建議保留 @MainActor 或確保呼叫端在主執行緒。

**判斷依據**：diff 中移除了 @MainActor 與相關註解，且函式內建立 GCDWebServer 實例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27</code> 移除 expectation 可能導致測試提前結束或無法驗證非同步結果</summary>

在 testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase 中，移除了 expectation 與 await fulfillment，但 downloadImage 的回呼是非同步的。若測試方法在回呼執行前就返回，測試將提前結束且無法驗證結果。建議保留 expectation 或改用 async 測試。

**判斷依據**：diff 中移除了 exp 的建立與 await fulfillment，但未改為 async 等待。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:1</code> [R01] 移除 Mozilla Public License 標頭</summary>

檔案開頭的 MPL 標頭被移除，違反專案規範 R01。請保留標準授權標頭。

**判斷依據**：diff 顯示原本的 MPL 標頭被刪除，且未新增替代。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42</code> 移除 expectation 可能導致測試無法驗證決策處理器被呼叫</summary>

在 testRequestMediaCaptureSuccess 中，移除了 expectation 與 wait，但決策處理器可能非同步呼叫。若未等待，測試可能無法驗證 XCTAssertEqual 是否執行。建議保留等待機制。

**判斷依據**：diff 移除了 expectation 的建立與 wait(for:)，且未改為 async 測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8963 (cache hit 6912) ｜ completion tokens 914 ｜ PR #10</sub>