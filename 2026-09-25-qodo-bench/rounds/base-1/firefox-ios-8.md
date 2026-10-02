<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將大量測試類別的 setUp/tearDown 改為 async throws，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫，以符合 Swift 6 的 concurrency 規範。主要風險在於部分測試類別未標記 @MainActor，卻在非主執行緒的 async setUp 中呼叫 @MainActor 方法，可能導致執行緒安全問題或測試不穩定。另外，部分 tearDown 中呼叫 DependencyHelperMock().reset() 未加 await，若 reset 也是 @MainActor 隔離，可能造成編譯錯誤或 runtime 問題。整體改動方向正確，但需確保所有呼叫點都正確處理 actor 隔離。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:12` | 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:17` | 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:14` | 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:12` | 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:12` | 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28` | tearDown 中呼叫 @MainActor 方法可能導致執行緒問題 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:21` | tearDown 中呼叫 @MainActor 方法可能導致執行緒問題 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:17` | tearDown 中呼叫 @MainActor 方法可能導致執行緒問題 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:17` | tearDown 中呼叫 @MainActor 方法可能導致執行緒問題 | 0.70 |
| 🔸 | Minor | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11` | bootstrapDependencies 標記為 @MainActor 但未處理非主執行緒呼叫 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:12</code> 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`LaunchTypeTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `await DependencyHelperMock().bootstrapDependencies()`。由於 `bootstrapDependencies` 被標記為 `@MainActor`，此呼叫會在主執行緒上執行，但測試類別本身可能在其他執行緒上運行，這可能導致資料競爭或非預期的行為。建議將測試類別標記為 `@MainActor`，或確保 `bootstrapDependencies` 的呼叫在正確的 actor 隔離下進行。

**判斷依據**：diff 中 `LaunchTypeTests` 類別未標記 `@MainActor`，但 `bootstrapDependencies` 在 `DependencyHelperMock.swift` 中被標記為 `@MainActor`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:17</code> 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 `await`，但該方法現在是 async 且 @MainActor）。這可能導致編譯錯誤或執行緒問題。建議將測試類別標記為 `@MainActor`，並確保呼叫方式正確。

**判斷依據**：diff 中 `LaunchScreenViewModelTests` 類別未標記 `@MainActor`，且 `bootstrapDependencies` 呼叫未加 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:14</code> 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`CreditCardSettingsViewControllerTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `await DependencyHelperMock().bootstrapDependencies()`。這可能導致執行緒問題。建議將測試類別標記為 `@MainActor`。

**判斷依據**：diff 中 `CreditCardSettingsViewControllerTests` 類別未標記 `@MainActor`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:12</code> 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`CustomSearchEnginesTest` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `await DependencyHelperMock().bootstrapDependencies()`。這可能導致執行緒問題。建議將測試類別標記為 `@MainActor`。

**判斷依據**：diff 中 `CustomSearchEnginesTest` 類別未標記 `@MainActor`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:12</code> 非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`DownloadProgressManagerTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 `await`，但該方法現在是 async 且 @MainActor）。這可能導致編譯錯誤或執行緒問題。建議將測試類別標記為 `@MainActor`，並確保呼叫方式正確。

**判斷依據**：diff 中 `DownloadProgressManagerTests` 類別未標記 `@MainActor`，且 `bootstrapDependencies` 呼叫未加 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28</code> tearDown 中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`tearDown` 中呼叫 `DependencyHelperMock().reset()` 未加 `await`，但 `reset` 可能也是 @MainActor 隔離。若測試類別未標記 @MainActor，可能導致編譯錯誤或執行緒問題。建議檢查 `reset` 的隔離屬性，並在必要時加上 `await` 或將類別標記為 @MainActor。

**判斷依據**：diff 中 `tearDown` 內呼叫 `DependencyHelperMock().reset()` 未加 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:21</code> tearDown 中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`tearDown` 中呼叫 `DependencyHelperMock().reset()` 未加 `await`，可能導致編譯錯誤或執行緒問題。建議檢查 `reset` 的隔離屬性，並在必要時加上 `await` 或將類別標記為 @MainActor。

**判斷依據**：diff 中 `tearDown` 內呼叫 `DependencyHelperMock().reset()` 未加 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:17</code> tearDown 中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`tearDown` 中呼叫 `AppContainer.shared.reset()` 未加 `await`，可能導致編譯錯誤或執行緒問題。建議檢查 `reset` 的隔離屬性，並在必要時加上 `await` 或將類別標記為 @MainActor。

**判斷依據**：diff 中 `tearDown` 內呼叫 `AppContainer.shared.reset()` 未加 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:17</code> tearDown 中呼叫 @MainActor 方法可能導致執行緒問題</summary>

`tearDown` 中呼叫 `DependencyHelperMock().reset()` 未加 `await`，可能導致編譯錯誤或執行緒問題。建議檢查 `reset` 的隔離屬性，並在必要時加上 `await` 或將類別標記為 @MainActor。

**判斷依據**：diff 中 `tearDown` 內呼叫 `DependencyHelperMock().reset()` 未加 `await`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11</code> bootstrapDependencies 標記為 @MainActor 但未處理非主執行緒呼叫</summary>

`bootstrapDependencies` 被標記為 `@MainActor`，但方法內部仍有 `DispatchQueue.main.sync` 的舊程式碼被移除，改為直接在主執行緒上執行。這可能導致在非主執行緒呼叫時發生問題。建議確認所有呼叫點都在主執行緒上，或保留適當的執行緒處理。

**判斷依據**：diff 中 `bootstrapDependencies` 被標記為 `@MainActor`，但移除了原有的 `Thread.isMainThread` 和 `DispatchQueue.main.sync` 處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 21589 (cache hit 1536) ｜ completion tokens 2723 ｜ PR #8</sub>