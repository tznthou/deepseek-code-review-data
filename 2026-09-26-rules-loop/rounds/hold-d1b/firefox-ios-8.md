<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies() 標記為 @MainActor 且改為 async 呼叫，以符合 Swift 6 的 concurrency 要求。整體改動方向正確，但部分測試類別在改為 async setUp 後，其內部的 bootstrapDependencies() 呼叫未加上 await，可能導致編譯錯誤。此外，刪除 TestSetup.swift 及調整專案檔的變更需確認無其他引用。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:16` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:16` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:15` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuViewControllerTests.swift:16` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyViewControllerTests.swift:16` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/NativeErrorPage/NativeErrorPageViewControllerTests.swift:16` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Sharing/URLActivityItemProviderTests.swift:16` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/WindowManagerTests.swift:18` | [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await | 0.95 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:16</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:16</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:15</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/MainMenu/MainMenuViewControllerTests.swift:16</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Microsurvey/MicrosurveyViewControllerTests.swift:16</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/NativeErrorPage/NativeErrorPageViewControllerTests.swift:16</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Sharing/URLActivityItemProviderTests.swift:16</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/WindowManagerTests.swift:18</code> [R06] 在 async setUp 中呼叫 @MainActor async 方法未加 await</summary>

`DependencyHelperMock().bootstrapDependencies(injectedTabManager: tabManager)` 現在是 @MainActor async 方法，但在 async setUp 中呼叫時未加上 `await`，會導致編譯錯誤。

建議改為 `await DependencyHelperMock().bootstrapDependencies(injectedTabManager: tabManager)`。

**判斷依據**：diff 中此檔案 setUp 改為 async throws，但該行未加 await，而 DependencyHelperMock.swift 中該方法已標註 @MainActor 且為 async。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23685 (cache hit 23680) ｜ completion tokens 2344 ｜ PR #8</sub>