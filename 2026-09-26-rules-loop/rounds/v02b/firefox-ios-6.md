<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個測試類別從同步 setUp/tearDown 遷移至 async 版本，並加上 @MainActor 標註，以符合 Swift 6 的 concurrency 要求。整體改動方向正確，但 NotificationManagerTests 中將 XCTest 斷言改為 Swift assert 會導致測試失效，且部分測試類別未加上 @MainActor 可能導致執行緒安全問題。建議先修正 NotificationManagerTests 的斷言，並確認所有涉及 UI 的測試類別都有 @MainActor。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27` | 使用 Swift assert 取代 XCTest 斷言，導致測試失效 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.80 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/RatingPromptManagerTests.swift:22` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/HistoryPanelTests.swift:11` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuConfigurationUtilityTests.swift:17` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuCoordinatorTests.swift:11` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuMiddlewareTests.swift:15` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyCoordinatorTests.swift:15` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyMiddlewareTests.swift:15` | 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27</code> 使用 Swift assert 取代 XCTest 斷言，導致測試失效</summary>

在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，但此 PR 將其改為 Swift 標準庫的 `assert`。`assert` 在 release 建置中會被編譯器移除，且不會回報給 XCTest 框架，因此測試將永遠通過，無法驗證實際行為。應改回 `XCTAssertTrue` 或使用其他 XCTest 斷言。

**判斷依據**：diff 中將 `XCTAssertTrue(granted)` 改為 `assert(granted, ...)`，並將 `XCTAssertTrue(self.center.requestAuthorizationWasCalled)` 改為 `assert(center?.requestAuthorizationWasCalled ?? false, ...)`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 UIViewController（SyncContentSettingsViewController），但未加上 @MainActor。在 Swift 6 嚴格 concurrency 下，從非主執行緒存取 UI 物件可能導致 runtime crash 或資料競爭。建議在類別宣告加上 @MainActor，或確認所有 UI 操作都在主執行緒。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別（如 StoriesFeedDiffableDataSourceTests）有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/FxAWebViewModelTests.swift:14</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 FxAWebViewModel，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/RatingPromptManagerTests.swift:22</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 RatingPromptManager，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/HistoryPanelTests.swift:11</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 HistoryPanel，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuConfigurationUtilityTests.swift:17</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 MainMenuConfigurationUtility，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuCoordinatorTests.swift:11</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 MainMenuCoordinator，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuMiddlewareTests.swift:15</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 MainMenuMiddleware，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyCoordinatorTests.swift:15</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 MicrosurveyCoordinator，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyMiddlewareTests.swift:15</code> 測試類別未加上 @MainActor，可能導致 UI 操作在背景執行緒執行</summary>

此測試類別涉及 MicrosurveyMiddleware，可能包含 UI 相關邏輯，但未加上 @MainActor。建議確認是否需要加上 @MainActor 以確保執行緒安全。

**判斷依據**：diff 中此類別未加上 @MainActor，而其他 UI 測試類別有加上。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10001 (cache hit 9984) ｜ completion tokens 2112 ｜ PR #6</sub>