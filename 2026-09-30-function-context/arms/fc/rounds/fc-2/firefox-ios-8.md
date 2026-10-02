<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將測試中的 `DependencyHelperMock.bootstrapDependencies()` 改為 async/await 呼叫，並將 `setUp`/`tearDown` 改為 async 版本，以配合 Swift 6 的 concurrency 變更。整體風險在於 `bootstrapDependencies` 現在標記為 `@MainActor`，但部分測試類別未標記 `@MainActor`，可能導致編譯錯誤或執行緒問題。此外，刪除 `TestSetup.swift` 及專案檔調整應無功能影響。建議先確認所有呼叫點都正確處理 actor isolation。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11` | bootstrapDependencies 標記 @MainActor 但呼叫端可能未隔離 | 0.80 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:12` | setUp 改為 async 但未標記 @MainActor | 0.60 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/StartAtHome/StartAtHomeHelperTests.swift:21` | 重複呼叫 bootstrapDependencies 已移除但可能殘留 | 0.50 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Sharing/URLActivityItemProviderTests.swift:20` | 新增 tearDown 但未呼叫 super.tearDown 於最後 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11</code> bootstrapDependencies 標記 @MainActor 但呼叫端可能未隔離</summary>

`bootstrapDependencies` 現在標記為 `@MainActor`，但許多測試類別（如 `LaunchTypeTests`、`CustomSearchEnginesTest` 等）本身未標記 `@MainActor`，且其 `setUp` 方法也未標記。在 Swift 6 嚴格 concurrency 下，從非隔離的 async 方法呼叫 `@MainActor` 方法需要 `await`，但若呼叫端未在 MainActor 上，可能導致編譯錯誤或執行緒不安全。建議確認所有呼叫點都正確處理 actor isolation，或考慮將 `bootstrapDependencies` 改為 nonisolated 並在內部處理 main thread 切換。

**判斷依據**：diff 中 `DependencyHelperMock.swift` 新增 `@MainActor` 屬性，且多個測試檔案將 `DependencyHelperMock().bootstrapDependencies()` 改為 `await DependencyHelperMock().bootstrapDependencies()`，但測試類別本身未標記 `@MainActor`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:12</code> setUp 改為 async 但未標記 @MainActor</summary>

`setUp` 改為 `async throws` 並呼叫 `await DependencyHelperMock().bootstrapDependencies()`，但 `LaunchTypeTests` 類別未標記 `@MainActor`。若 `bootstrapDependencies` 為 `@MainActor`，此處 await 可能需要在 MainActor 上執行，否則可能導致執行緒問題。建議確認 XCTest 的 async setUp 是否自動在 MainActor 上執行，或明確標記。

**判斷依據**：diff 中 `LaunchTypeTests.swift` 的 setUp 改為 async 並 await bootstrapDependencies，但類別宣告為 `final class LaunchTypeTests: XCTestCase` 無 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/StartAtHome/StartAtHomeHelperTests.swift:21</code> 重複呼叫 bootstrapDependencies 已移除但可能殘留</summary>

原本 setUp 中有兩次 `DependencyHelperMock().bootstrapDependencies()`，現在只保留一次並加上 await。但需確認是否所有測試都依賴於兩次呼叫（例如重置狀態），若移除可能影響測試隔離。建議檢查測試是否仍通過。

**判斷依據**：diff 中 `StartAtHomeHelperTests.swift` 原本有兩行 bootstrapDependencies，現在只剩一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Sharing/URLActivityItemProviderTests.swift:20</code> 新增 tearDown 但未呼叫 super.tearDown 於最後</summary>

新增的 `tearDown` 中先呼叫 `DependencyHelperMock().reset()` 再 `try await super.tearDown()`，順序可能影響其他資源釋放。建議確認 XCTest 的 tearDown 順序慣例。

**判斷依據**：diff 中 `URLActivityItemProviderTests.swift` 新增 tearDown 方法。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 87953 (cache hit 87936) ｜ completion tokens 1191 ｜ PR #8</sub>