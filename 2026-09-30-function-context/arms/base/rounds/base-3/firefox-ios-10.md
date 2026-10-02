<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 BrowserKit 套件與 ShareTo 擴充功能遷移至 Swift 6，主要變更包括：移除 StrictConcurrency 等實驗性旗標、將測試從 async 改為同步、為靜態屬性加上 nonisolated(unsafe)、以及為閉包加上 @Sendable 標註。整體風險中等，需注意測試同步化可能導致的執行緒問題，以及 nonisolated(unsafe) 的濫用。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12` | 測試從 async 改為同步可能導致執行緒阻塞或逾時 | 0.80 |
| ⚠️ | Major | `BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208` | 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全 | 0.70 |
| 🔸 | Minor | `BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6` | nonisolated(unsafe) 可能隱藏執行緒安全問題 | 0.60 |
| 🔸 | Minor | `BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38` | 移除 expectation 可能導致測試無法驗證非同步行為 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12</code> 測試從 async 改為同步可能導致執行緒阻塞或逾時</summary>

原本使用 `await fulfillment(of:timeout:)` 等待非同步 callback，現在改為同步的 `wait(for:timeout:)`。若 callback 在背景執行緒執行，`wait(for:timeout:)` 會阻塞主執行緒，可能導致測試逾時或死鎖。建議保留 async 版本，或確認 callback 執行緒與測試執行緒的關係。

**判斷依據**：diff 中移除了 `async` 關鍵字，並將 `await fulfillment` 改為 `wait(for:timeout:)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:208</code> 移除 @MainActor 可能導致 GCDWebServer 初始化執行緒不安全</summary>

原本 `startMockImageServer` 有 `@MainActor` 標註，確保 GCDWebServer 在主執行緒初始化。移除後，若測試在背景執行緒呼叫此方法，可能導致崩潰或未定義行為。建議保留 @MainActor，或確認所有呼叫點都在主執行緒。

**判斷依據**：diff 中移除了 `@MainActor` 標註。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6</code> nonisolated(unsafe) 可能隱藏執行緒安全問題</summary>

使用 `nonisolated(unsafe)` 來繞過 Swift 6 的嚴格並發檢查，但若 `ContentBlockerGenerator` 真的非執行緒安全，此標註只是暫時壓制問題。建議確認其執行緒安全性，或改用其他並發安全機制。

**判斷依據**：diff 中新增了 `nonisolated(unsafe)`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38</code> 移除 expectation 可能導致測試無法驗證非同步行為</summary>

在 `testRequestMediaCaptureSuccess` 中移除了 expectation 和 wait，若 `requestMediaCapturePermission` 是非同步的，測試可能在 callback 執行前就結束，導致斷言未執行。建議保留 expectation 或改用 async 測試。

**判斷依據**：diff 中移除了 expectation 的建立與 wait。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6914 (cache hit 6912) ｜ completion tokens 925 ｜ PR #10</sub>