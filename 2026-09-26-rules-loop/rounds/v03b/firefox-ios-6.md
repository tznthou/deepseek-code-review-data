<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將多個測試類別的 setUp/tearDown 改為 async 版本，並為部分 UI 相關測試類別加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。整體改動方向正確，但存在一個重大問題：NotificationManagerTests 中將 XCTest 斷言改為 Swift 標準庫的 assert，這會導致測試在 release 建置中失效，且無法正確回報失敗。此外，部分測試類別未加上 @MainActor，可能違反專案規範 R09。建議優先修正 assert 的使用，並全面檢查 UI 相關測試類別的 @MainActor 標註。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 assert 取代 XCTest 斷言，導致測試失效 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/RatingPromptManagerTests.swift:22` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/HistoryPanelTests.swift:11` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuConfigurationUtilityTests.swift:17` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuCoordinatorTests.swift:11` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuMiddlewareTests.swift:15` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyCoordinatorTests.swift:15` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyMiddlewareTests.swift:15` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/OnboardingTests/IntroViewControllerTests.swift:11` | [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 assert 取代 XCTest 斷言，導致測試失效</summary>

在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 的斷言被改為 Swift 標準庫的 `assert`。`assert` 在 release 建置（預設的測試建置）中會被編譯器移除，因此這些斷言不會被執行，測試將永遠通過，無法驗證行為。此外，`assert` 失敗時會直接 crash，而不是像 XCTest 斷言那樣記錄失敗並繼續執行。

**失敗情境**：當 `requestAuthorization` 的實作錯誤，導致 completion 中的 `granted` 為 false 或 `center.requestAuthorizationWasCalled` 為 false 時，測試仍會通過，無法捕捉到回歸。

**建議修法**：改回使用 XCTest 的斷言，例如 `XCTAssertTrue(granted)` 和 `XCTAssertTrue(center?.requestAuthorizationWasCalled ?? false)`。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，並將 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `FxAWebViewModelTests` 涉及 UI 相關的 ViewModel 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API（例如 `FxAWebViewModel` 的初始化或方法）時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`，如同其他 UI 相關測試類別（例如 `StoriesFeedDiffableDataSourceTests`）的做法。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別（如 `StoriesFeedDiffableDataSourceTests`）已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/RatingPromptManagerTests.swift:22</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `RatingPromptManagerTests` 涉及 UI 相關的 RatingPromptManager 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/HistoryPanelTests.swift:11</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `HistoryPanelTests` 涉及 UI 相關的 HistoryPanel 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuConfigurationUtilityTests.swift:17</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `MainMenuConfigurationUtilityTests` 涉及 UI 相關的 MainMenu 配置測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuCoordinatorTests.swift:11</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `MainMenuCoordinatorTests` 涉及 UI 相關的 Coordinator 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuMiddlewareTests.swift:15</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `MainMenuMiddlewareTests` 涉及 UI 相關的 Middleware 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyCoordinatorTests.swift:15</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `MicrosurveyCoordinatorTests` 涉及 UI 相關的 Coordinator 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyMiddlewareTests.swift:15</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `MicrosurveyMiddlewareIntegrationTests` 涉及 UI 相關的 Middleware 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/OnboardingTests/IntroViewControllerTests.swift:11</code> [R09] 測試類別未標註 @MainActor，可能導致 UI 操作在背景執行</summary>

此測試類別 `IntroViewControllerTests` 涉及 UI 相關的 ViewController 測試，但未加上 `@MainActor` 標註。在 Swift 6 的嚴格 concurrency 檢查下，若測試中觸及 UI 或 main actor 隔離的程式碼，可能會導致編譯錯誤或執行時 crash。

**失敗情境**：當測試方法中呼叫需要 main actor 的 API 時，若測試類別未標註 `@MainActor`，編譯器可能報錯，或測試在背景執行緒執行導致非預期行為。

**建議修法**：在類別宣告前加上 `@MainActor`。

**判斷依據**：diff 中此類別未加上 `@MainActor`，而其他類似測試類別已加上。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10011 (cache hit 9984) ｜ completion tokens 3288 ｜ PR #6</sub>