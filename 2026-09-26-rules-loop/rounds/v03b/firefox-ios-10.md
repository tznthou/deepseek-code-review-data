<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括移除 StrictConcurrency 等實驗性旗標、將套件工具版本提升至 6.2、調整測試以符合 Swift 6 的並發要求，以及為 ShareTo 建置設定 SWIFT_VERSION = 6.0。整體方向正確，但需注意幾個風險：移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全；測試中移除 expectation 可能造成測試提前結束而漏測；使用 nonisolated(unsafe) 雖有註解但應確認其必要性。建議修正上述問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27` | 移除 expectation 可能導致測試提前結束而漏測 | 0.75 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏並發問題 | 0.60 |
| 🔸 | Minor | `firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106` | wrappedAction 可能造成不必要的閉包包裝 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全</summary>

原本的註解指出 GCDWebServer 必須在主執行緒初始化，因此將 startMockImageServer 標記為 @MainActor。此 PR 移除了該標記，且呼叫端也改為同步呼叫（不再使用 await），這可能導致測試在背景執行緒執行時，GCDWebServer 初始化失敗或崩潰。

建議：保留 @MainActor 標記，或確保測試方法本身在主執行緒執行（例如使用 @MainActor 標記測試方法）。

**判斷依據**：diff 中移除了 @MainActor 註解與標記，且呼叫端從 `try? await startMockImageServer` 改為 `try? startMockImageServer`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27</code> 移除 expectation 可能導致測試提前結束而漏測</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 expectation 等待非同步下載完成，但此 PR 移除了 expectation 的建立與等待。由於 `downloadImage` 是非同步回呼，測試方法可能在回呼執行前就返回，導致測試永遠通過但實際上未驗證任何內容。

建議：保留 expectation 並使用 `wait(for:timeout:)` 等待，或將測試方法改為 async 並使用 `await` 等待非同步結果。

**判斷依據**：diff 中移除了 `let exp = expectation(description: "Image download and parse")` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且未加入其他等待機制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏並發問題</summary>

將 `generator` 標記為 `nonisolated(unsafe)` 以繞過 Swift 6 的並發檢查，但此舉可能隱藏潛在的資料競爭。雖然有註解說明 ContentBlockerGenerator 不是執行緒安全的，但應確認此靜態屬性是否真的只會在單一執行緒存取，或考慮將其改為 actor 或使用鎖保護。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)` 修飾詞，並加上註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106</code> wrappedAction 可能造成不必要的閉包包裝</summary>

新增的 `wrappedAction` 閉包僅是轉呼叫 `moreButtonAction`，沒有額外邏輯。這可能是為了滿足 Swift 6 的 @Sendable 要求，但應確認是否真的需要此包裝，或可直接將 `moreButtonAction` 標記為 @Sendable。

**判斷依據**：diff 中新增了 wrappedAction 閉包，並將其傳遞給 ActionButtonViewModel。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8983 (cache hit 8960) ｜ completion tokens 1160 ｜ PR #10</sub>