<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫。主要風險在於部分測試類別未加上 @MainActor 標註，但呼叫了 @MainActor 方法，可能導致編譯錯誤或執行緒問題；另外部分 tearDown 中 DependencyHelperMock().reset() 未加 await，若 reset 也是 @MainActor 則可能遺漏。整體改動方向合理，但需確保所有呼叫點都正確處理 async 與 actor isolation。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:14` | setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:16` | setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:14` | setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14` | setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:18` | tearDown 中呼叫 DependencyHelperMock().reset() 未加 await | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29` | tearDown 中呼叫 AppContainer.shared.reset() 可能需 await | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:23` | tearDown 中呼叫 DependencyHelperMock().reset() 未加 await | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:18` | tearDown 中呼叫 AppContainer.shared.reset() 可能需 await | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:18` | tearDown 中呼叫 DependencyHelperMock().reset() 未加 await | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:14</code> setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor 方法，但 `LaunchTypeTests` 類別本身沒有標註 @MainActor。在 Swift 6 嚴格並發檢查下，從非隔離的 async 方法呼叫 @MainActor 方法需要 await，但此處已加上 await，理論上可行；然而若測試方法本身在非主執行緒執行，可能導致後續操作不在主執行緒。建議確認測試類別是否需要標註 @MainActor，或確保所有相關操作都在主執行緒。

**判斷依據**：diff 中 setUp 改為 async throws，並呼叫 await DependencyHelperMock().bootstrapDependencies()，但類別宣告 `final class LaunchTypeTests: XCTestCase` 沒有 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor 方法，但 `LaunchScreenViewModelTests` 類別沒有標註 @MainActor。此處未加 await（diff 中仍為 `DependencyHelperMock().bootstrapDependencies()`），在 Swift 6 下可能導致編譯錯誤。

**判斷依據**：diff 中 setUp 改為 async throws，但 bootstrapDependencies 呼叫未加 await，且類別未標註 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:16</code> setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor 方法，但 `CreditCardSettingsViewControllerTests` 類別沒有標註 @MainActor。此處已加 await，但若測試方法在非主執行緒執行，可能導致後續操作不在主執行緒。

**判斷依據**：diff 中 setUp 改為 async throws，並呼叫 await DependencyHelperMock().bootstrapDependencies()，但類別宣告 `final class CreditCardSettingsViewControllerTests: XCTestCase` 沒有 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:14</code> setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor 方法，但 `CustomSearchEnginesTest` 類別沒有標註 @MainActor。此處已加 await，但若測試方法在非主執行緒執行，可能導致後續操作不在主執行緒。

**判斷依據**：diff 中 setUp 改為 async throws，並呼叫 await DependencyHelperMock().bootstrapDependencies()，但類別宣告 `class CustomSearchEnginesTest: XCTestCase` 沒有 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14</code> setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor 方法，但 `DownloadProgressManagerTests` 類別沒有標註 @MainActor。此處未加 await（diff 中仍為 `DependencyHelperMock().bootstrapDependencies()`），在 Swift 6 下可能導致編譯錯誤。

**判斷依據**：diff 中 setUp 改為 async throws，但 bootstrapDependencies 呼叫未加 await，且類別未標註 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:18</code> tearDown 中呼叫 DependencyHelperMock().reset() 未加 await</summary>

`DependencyHelperMock().reset()` 可能也是 @MainActor 方法（需確認），若為 @MainActor 且 tearDown 為 async，則應加上 await。目前 diff 中未加 await，可能導致編譯錯誤或執行緒問題。

**判斷依據**：diff 中 tearDown 改為 async throws，但 reset() 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29</code> tearDown 中呼叫 AppContainer.shared.reset() 可能需 await</summary>

`AppContainer.shared.reset()` 若為 @MainActor 方法，在 async tearDown 中應加上 await。目前未加，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但 reset() 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:23</code> tearDown 中呼叫 DependencyHelperMock().reset() 未加 await</summary>

`DependencyHelperMock().reset()` 可能也是 @MainActor 方法，若為 @MainActor 且 tearDown 為 async，則應加上 await。目前未加，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但 reset() 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:18</code> tearDown 中呼叫 AppContainer.shared.reset() 可能需 await</summary>

`AppContainer.shared.reset()` 若為 @MainActor 方法，在 async tearDown 中應加上 await。目前未加，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但 reset() 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:18</code> tearDown 中呼叫 DependencyHelperMock().reset() 未加 await</summary>

`DependencyHelperMock().reset()` 可能也是 @MainActor 方法，若為 @MainActor 且 tearDown 為 async，則應加上 await。目前未加，可能導致編譯錯誤。

**判斷依據**：diff 中 tearDown 改為 async throws，但 reset() 呼叫未加 await。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 21589 (cache hit 21504) ｜ completion tokens 2234 ｜ PR #8</sub>