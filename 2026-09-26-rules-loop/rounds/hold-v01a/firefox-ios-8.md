<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將大量測試類別的 setUp/tearDown 改為 async throws，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async，以解決 Swift 6 遷移中的警告。主要風險在於部分測試類別未正確 await 此 async 呼叫，可能導致測試不穩定或失敗；另外刪除 TestSetup.swift 及調整專案檔可能影響測試建置。整體方向正確，但需修正遺漏的 await 及確認專案檔變更的完整性。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:16` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:16` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:15` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuViewControllerTests.swift:16` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyViewControllerTests.swift:16` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/NativeErrorPage/NativeErrorPageViewControllerTests.swift:16` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/WindowManagerTests.swift:18` | bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗 | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:34` | tearDown() 中呼叫 super.tearDown() 可能需在最後執行 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 18 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 13 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:16</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 15 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:16</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 14 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:15</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 14 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuViewControllerTests.swift:16</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 15 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyViewControllerTests.swift:16</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 15 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/NativeErrorPage/NativeErrorPageViewControllerTests.swift:16</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案第 15 行新增的 `DependencyHelperMock().bootstrapDependencies()` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/WindowManagerTests.swift:18</code> bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗</summary>

在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies(injectedTabManager: tabManager)` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies(injectedTabManager: tabManager)`。

**判斷依據**：diff 中此檔案第 17 行新增的 `DependencyHelperMock().bootstrapDependencies(injectedTabManager: tabManager)` 未加 `await`，而其他檔案多已改為 `await DependencyHelperMock().bootstrapDependencies()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:34</code> tearDown() 中呼叫 super.tearDown() 可能需在最後執行</summary>

在 `tearDown() async throws` 中，`try await super.tearDown()` 被放在最後，但通常應先呼叫 super 再進行清理，以確保父類別狀態正確。請確認此順序是否會影響測試隔離。

**判斷依據**：diff 中此檔案第 28 行新增的 `try await super.tearDown()` 位於方法最後，與其他檔案常見的順序不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23648 (cache hit 21504) ｜ completion tokens 2523 ｜ PR #8</sub>