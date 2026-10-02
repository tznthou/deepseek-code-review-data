<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫。主要風險在於部分測試類別未標記 @MainActor，卻在 async setUp 中呼叫 @MainActor 方法，可能導致編譯錯誤或執行緒問題；另外部分 tearDown 未呼叫 super.tearDown()，可能造成資源未正確釋放。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11` | bootstrapDependencies 標記 @MainActor 但未標記 async，呼叫端需 await | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:14` | 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:18` | tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29` | tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:16` | 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:23` | tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:14` | 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:18` | tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14` | 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11</code> bootstrapDependencies 標記 @MainActor 但未標記 async，呼叫端需 await</summary>

`bootstrapDependencies` 被標記為 `@MainActor`，但未標記為 `async`。在 Swift 中，從非 async 上下文呼叫 @MainActor 方法需要 await，但從 async 上下文呼叫則不需要。然而，此方法內部有同步的 MainActor 隔離操作，若從非 MainActor 執行緒呼叫會導致執行緒不安全。建議將方法標記為 `async`，或確保所有呼叫端都在 MainActor 上。

**判斷依據**：diff 中新增 @MainActor 屬性，但方法簽名未加 async。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:14</code> 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤</summary>

`LaunchTypeTests` 類別未標記 `@MainActor`，但其 `setUp` 方法中呼叫了 `await DependencyHelperMock().bootstrapDependencies()`，而 `bootstrapDependencies` 已標記為 `@MainActor`。在 Swift 6 嚴格並發檢查下，這可能導致編譯錯誤或執行緒不安全。建議將測試類別標記為 `@MainActor`，或確保呼叫發生在 MainActor 上。

**判斷依據**：diff 中 LaunchTypeTests.swift 的 setUp 改為 async 並呼叫 await DependencyHelperMock().bootstrapDependencies()，但類別宣告 `final class LaunchTypeTests: XCTestCase` 沒有 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:18</code> tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor</summary>

`tearDown` 中呼叫 `DependencyHelperMock().reset()`，該方法可能也是 @MainActor（需確認），但類別未標記 @MainActor，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤</summary>

`LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 方法中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 await，但方法已改為 async @MainActor），可能導致編譯錯誤。

**判斷依據**：diff 中 setUp 改為 async throws，但呼叫 bootstrapDependencies 未加 await，且類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29</code> tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor</summary>

`tearDown` 中呼叫 `AppContainer.shared.reset()`，該方法可能也是 @MainActor，但類別未標記 @MainActor，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:16</code> 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤</summary>

`CreditCardSettingsViewControllerTests` 類別未標記 `@MainActor`，但其 `setUp` 方法中呼叫了 `await DependencyHelperMock().bootstrapDependencies()`，可能導致編譯錯誤。

**判斷依據**：diff 中 setUp 改為 async throws 並呼叫 await bootstrapDependencies，但類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:23</code> tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor</summary>

`tearDown` 中呼叫 `DependencyHelperMock().reset()`，該方法可能也是 @MainActor，但類別未標記 @MainActor，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:14</code> 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤</summary>

`CustomSearchEnginesTest` 類別未標記 `@MainActor`，但其 `setUp` 方法中呼叫了 `await DependencyHelperMock().bootstrapDependencies()`，可能導致編譯錯誤。

**判斷依據**：diff 中 setUp 改為 async throws 並呼叫 await bootstrapDependencies，但類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:18</code> tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor</summary>

`tearDown` 中呼叫 `AppContainer.shared.reset()`，該方法可能也是 @MainActor，但類別未標記 @MainActor，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但類別未標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14</code> 非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤</summary>

`DownloadProgressManagerTests` 類別標記為 `@MainActor`，但其 `setUp` 方法中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 await），但方法已改為 async @MainActor，可能導致編譯錯誤。

**判斷依據**：diff 中 setUp 改為 async throws，但呼叫 bootstrapDependencies 未加 await，且類別已標記 @MainActor。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 21589 (cache hit 21504) ｜ completion tokens 2174 ｜ PR #8</sub>