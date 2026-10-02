<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將測試類別的 setUp/tearDown 改為 async 版本，並將 DependencyHelperMock.bootstrapDependencies 標記為 @MainActor，以符合 Swift 6 的 concurrency 要求。整體改動方向正確，但部分測試類別在改為 async setUp 後，未對呼叫的 bootstrapDependencies 加上 await，可能導致編譯錯誤或執行緒不安全。此外，刪除 TestSetup.swift 後，需確認無其他程式碼依賴該類別。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | [R09] 未 await @MainActor 方法 bootstrapDependencies | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28` | [R09] 未 await @MainActor 方法 reset | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14` | [R09] 未 await @MainActor 方法 bootstrapDependencies | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:18` | [R09] 未 await @MainActor 方法 reset | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:16` | [R09] 未 await @MainActor 方法 bootstrapDependencies | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:20` | [R09] 未 await @MainActor 方法 reset | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:16` | [R09] 未 await @MainActor 方法 bootstrapDependencies | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:21` | [R09] 未 await @MainActor 方法 reset | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:15` | [R09] 未 await @MainActor 方法 bootstrapDependencies | 0.90 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:20` | [R09] 未 await @MainActor 方法 reset | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> [R09] 未 await @MainActor 方法 bootstrapDependencies</summary>

在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時，該方法已標記為 @MainActor，但此處未加上 `await`。這會導致編譯錯誤，因為從非隔離的 async 函式呼叫 @MainActor 方法必須使用 await。建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock.swift 中該方法已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28</code> [R09] 未 await @MainActor 方法 reset</summary>

在 async tearDown 中呼叫 `DependencyHelperMock().reset()` 時，該方法可能也標記為 @MainActor（需確認），但此處未加上 `await`。若 reset 為 @MainActor，則會導致編譯錯誤。建議加上 `await`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock 類別可能已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14</code> [R09] 未 await @MainActor 方法 bootstrapDependencies</summary>

在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時，該方法已標記為 @MainActor，但此處未加上 `await`。這會導致編譯錯誤。建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock.swift 中該方法已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:18</code> [R09] 未 await @MainActor 方法 reset</summary>

在 async tearDown 中呼叫 `DependencyHelperMock().reset()` 時，該方法可能也標記為 @MainActor（需確認），但此處未加上 `await`。若 reset 為 @MainActor，則會導致編譯錯誤。建議加上 `await`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock 類別可能已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:16</code> [R09] 未 await @MainActor 方法 bootstrapDependencies</summary>

在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時，該方法已標記為 @MainActor，但此處未加上 `await`。這會導致編譯錯誤。建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock.swift 中該方法已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/Homepage/PrivateHomepageViewControllerTests.swift:20</code> [R09] 未 await @MainActor 方法 reset</summary>

在 async tearDown 中呼叫 `DependencyHelperMock().reset()` 時，該方法可能也標記為 @MainActor（需確認），但此處未加上 `await`。若 reset 為 @MainActor，則會導致編譯錯誤。建議加上 `await`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock 類別可能已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:16</code> [R09] 未 await @MainActor 方法 bootstrapDependencies</summary>

在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時，該方法已標記為 @MainActor，但此處未加上 `await`。這會導致編譯錯誤。建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock.swift 中該方法已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/DownloadsPanelTests.swift:21</code> [R09] 未 await @MainActor 方法 reset</summary>

在 async tearDown 中呼叫 `DependencyHelperMock().reset()` 時，該方法可能也標記為 @MainActor（需確認），但此處未加上 `await`。若 reset 為 @MainActor，則會導致編譯錯誤。建議加上 `await`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock 類別可能已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:15</code> [R09] 未 await @MainActor 方法 bootstrapDependencies</summary>

在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時，該方法已標記為 @MainActor，但此處未加上 `await`。這會導致編譯錯誤。建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock.swift 中該方法已標記 @MainActor。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/ReadingListPanelTests.swift:20</code> [R09] 未 await @MainActor 方法 reset</summary>

在 async tearDown 中呼叫 `DependencyHelperMock().reset()` 時，該方法可能也標記為 @MainActor（需確認），但此處未加上 `await`。若 reset 為 @MainActor，則會導致編譯錯誤。建議加上 `await`。

**判斷依據**：diff 中該行未加上 await，而 DependencyHelperMock 類別可能已標記 @MainActor。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 23685 (cache hit 23552) ｜ completion tokens 2144 ｜ PR #8</sub>