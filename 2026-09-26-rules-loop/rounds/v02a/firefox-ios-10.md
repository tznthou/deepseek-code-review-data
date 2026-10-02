<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo extension 遷移至 Swift 6，主要變更包括移除實驗性 concurrency flags、調整測試以符合 Swift 6 的同步/非同步規則、以及為 ShareTo 設定 SWIFT_VERSION = 6.0。整體風險在於移除 StrictConcurrency 等 flags 後，可能隱藏了原本被檢查的 concurrency 問題；此外，測試中將 async 改為 sync 並使用 wait(for:) 可能導致測試不穩定或無法正確驗證非同步行為。建議優先確認測試變更的正確性，並確保所有 concurrency 相關的程式碼在 Swift 6 模式下仍能安全運作。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 測試從 async 改為 sync 可能導致非同步行為未被正確等待 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:70` | 使用 wait(for:) 可能導致測試不穩定或死鎖 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試未驗證非同步行為 | 0.70 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | 使用 nonisolated(unsafe) 可能隱藏 concurrency 問題 | 0.60 |
| 🔸 | Minor | `BrowserKit/Package.swift:1` | 移除 StrictConcurrency 等 flags 可能降低 concurrency 檢查 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 測試從 async 改為 sync 可能導致非同步行為未被正確等待</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `await fulfillment(of: [exp], timeout: 2.0)` 等待非同步 callback，現在移除了 expectation 與等待，直接呼叫 `siteDownloader.downloadImage` 後測試方法即結束。這可能導致測試在非同步 callback 執行前就返回，使得斷言永遠不會被執行，測試形同虛設。

建議：保留 expectation 並使用 `wait(for:timeout:)` 或將測試方法維持 async 並使用 `await fulfillment`，以確保非同步操作完成後再進行驗證。

**判斷依據**：diff 中移除了 `let exp = expectation(...)` 與 `await fulfillment(of: [exp], timeout: 2.0)`，且測試方法從 `async` 改為 sync。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:70</code> 使用 wait(for:) 可能導致測試不穩定或死鎖</summary>

在 `testDownloadingSVGImage_withKingfisherProcessor_forSpecialSVGCase` 中，將 `await fulfillment` 改為 `wait(for: [exp], timeout: 2.0)`。若 `downloadImage` 的 callback 是在 main thread 執行，而測試也在 main thread 等待，可能造成死鎖。此外，若 callback 未在 timeout 內觸發，測試會失敗，但原本的 async 寫法可能更安全。

建議：確認 callback 的執行緒，若可能跨執行緒，應使用 `await fulfillment` 或將測試方法標記為 `@MainActor` 並使用 `wait`。

**判斷依據**：diff 中將 `await fulfillment(of: [exp], timeout: 2.0)` 改為 `wait(for: [exp], timeout: 2.0)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試未驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中，原本有 expectation 等待 decision handler 被呼叫，現在移除了 expectation 與 `wait(for:)`，僅直接呼叫 `subject.requestMediaCapturePermission`。這可能導致測試在 handler 執行前就結束，無法驗證 decision 是否正確。

建議：保留 expectation 並使用 `wait(for:timeout:)` 或將測試方法改為 async 並使用 `await fulfillment`。

**判斷依據**：diff 中移除了 `let expectation = expectation(...)` 與 `wait(for: [expectation])`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> 使用 nonisolated(unsafe) 可能隱藏 concurrency 問題</summary>

將 `static let generator` 加上 `nonisolated(unsafe)` 以繞過 Swift 6 的 concurrency 檢查。雖然註解說明 ContentBlockerGenerator 不是 thread safe，但此舉可能讓潛在的資料競爭在未來被忽略。建議確認 generator 的使用情境是否真的安全，或考慮將其改為 actor 或使用鎖保護。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)` 修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Package.swift:1</code> 移除 StrictConcurrency 等 flags 可能降低 concurrency 檢查</summary>

此 PR 移除了多個 target 中的 `.enableExperimentalFeature("StrictConcurrency")` 等 flags。雖然 Swift 6 預設啟用 strict concurrency，但移除這些 flags 可能導致某些程式碼在遷移過程中未被嚴格檢查，增加潛在的 concurrency bug 風險。建議確認所有程式碼已在 Swift 6 模式下通過編譯且無警告。

**判斷依據**：diff 中大量移除了 `.enableExperimentalFeature("StrictConcurrency")` 等設定。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8973 (cache hit 1536) ｜ completion tokens 1450 ｜ PR #10</sub>