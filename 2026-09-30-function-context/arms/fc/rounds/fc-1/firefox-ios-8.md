<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 主要將測試中的 `setUp`/`tearDown` 改為 async 版本，並將 `DependencyHelperMock.bootstrapDependencies()` 標記為 `@MainActor` 後以 `await` 呼叫。整體方向合理，但部分測試類別在 async `setUp` 中呼叫 `bootstrapDependencies()` 時未加 `await`，可能導致編譯錯誤或執行緒問題。此外，`DependencyHelperMock` 的 `reset()` 未標記 `@MainActor`，但多數 `tearDown` 已改為 async 且未 await，可能造成 main actor 隔離不一致。建議修正這些遺漏。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19` | async setUp 中呼叫 @MainActor 方法缺少 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:14` | async setUp 中呼叫 @MainActor 方法缺少 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:16` | async setUp 中呼叫 @MainActor 方法缺少 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:14` | async setUp 中呼叫 @MainActor 方法缺少 await | 0.95 |
| 🛑 | Blocker | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14` | async setUp 中呼叫 @MainActor 方法缺少 await | 0.95 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:25` | tearDown 中呼叫 reset 未 await | 0.85 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:18` | tearDown 中呼叫 reset 未 await | 0.85 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:23` | tearDown 中呼叫 reset 未 await | 0.85 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:17` | tearDown 中呼叫 reset 未 await | 0.85 |
| ⚠️ | Major | `firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:18` | tearDown 中呼叫 reset 未 await | 0.85 |

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19</code> async setUp 中呼叫 @MainActor 方法缺少 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 已標記為 `@MainActor`，但在 async `setUp` 中呼叫時未加上 `await`。這會導致編譯錯誤，因為從非隔離的 async 函式呼叫 main actor 方法必須 await。

**判斷依據**：diff 中該行未變更，但 `DependencyHelperMock.bootstrapDependencies` 已加上 `@MainActor`，且此處 `setUp` 已改為 `async throws`，因此需要 `await`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:14</code> async setUp 中呼叫 @MainActor 方法缺少 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 已標記為 `@MainActor`，但在 async `setUp` 中呼叫時未加上 `await`。這會導致編譯錯誤。

**判斷依據**：diff 中該行未變更，但 `DependencyHelperMock.bootstrapDependencies` 已加上 `@MainActor`，且此處 `setUp` 已改為 `async throws`，因此需要 `await`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:16</code> async setUp 中呼叫 @MainActor 方法缺少 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 已標記為 `@MainActor`，但在 async `setUp` 中呼叫時未加上 `await`。這會導致編譯錯誤。

**判斷依據**：diff 中該行未變更，但 `DependencyHelperMock.bootstrapDependencies` 已加上 `@MainActor`，且此處 `setUp` 已改為 `async throws`，因此需要 `await`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:14</code> async setUp 中呼叫 @MainActor 方法缺少 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 已標記為 `@MainActor`，但在 async `setUp` 中呼叫時未加上 `await`。這會導致編譯錯誤。

**判斷依據**：diff 中該行未變更，但 `DependencyHelperMock.bootstrapDependencies` 已加上 `@MainActor`，且此處 `setUp` 已改為 `async throws`，因此需要 `await`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:14</code> async setUp 中呼叫 @MainActor 方法缺少 await</summary>

`DependencyHelperMock().bootstrapDependencies()` 已標記為 `@MainActor`，但在 async `setUp` 中呼叫時未加上 `await`。這會導致編譯錯誤。

**判斷依據**：diff 中該行未變更，但 `DependencyHelperMock.bootstrapDependencies` 已加上 `@MainActor`，且此處 `setUp` 已改為 `async throws`，因此需要 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:25</code> tearDown 中呼叫 reset 未 await</summary>

`DependencyHelperMock().reset()` 未標記為 `@MainActor`，但 `tearDown` 已改為 async 且未 await。若 `reset` 未來改為 main actor 隔離，此處將需要 await。目前可能無編譯錯誤，但建議統一加上 `await` 以符合 async 慣例。

**判斷依據**：diff 中 `tearDown` 改為 async，但 `reset()` 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/Launch/LaunchTypeTests.swift:18</code> tearDown 中呼叫 reset 未 await</summary>

`DependencyHelperMock().reset()` 未標記為 `@MainActor`，但 `tearDown` 已改為 async 且未 await。若 `reset` 未來改為 main actor 隔離，此處將需要 await。目前可能無編譯錯誤，但建議統一加上 `await` 以符合 async 慣例。

**判斷依據**：diff 中 `tearDown` 改為 async，但 `reset()` 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CreditCard/CreditCardSettingsViewControllerTests.swift:23</code> tearDown 中呼叫 reset 未 await</summary>

`DependencyHelperMock().reset()` 未標記為 `@MainActor`，但 `tearDown` 已改為 async 且未 await。若 `reset` 未來改為 main actor 隔離，此處將需要 await。目前可能無編譯錯誤，但建議統一加上 `await` 以符合 async 慣例。

**判斷依據**：diff 中 `tearDown` 改為 async，但 `reset()` 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/CustomSearchEnginesTest.swift:17</code> tearDown 中呼叫 reset 未 await</summary>

`DependencyHelperMock().reset()` 未標記為 `@MainActor`，但 `tearDown` 已改為 async 且未 await。若 `reset` 未來改為 main actor 隔離，此處將需要 await。目前可能無編譯錯誤，但建議統一加上 `await` 以符合 async 慣例。

**判斷依據**：diff 中 `tearDown` 改為 async，但 `reset()` 呼叫未加 await。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/firefox-ios-tests/Tests/ClientTests/DownloadProgressManagerTests.swift:18</code> tearDown 中呼叫 reset 未 await</summary>

`DependencyHelperMock().reset()` 未標記為 `@MainActor`，但 `tearDown` 已改為 async 且未 await。若 `reset` 未來改為 main actor 隔離，此處將需要 await。目前可能無編譯錯誤，但建議統一加上 `await` 以符合 async 慣例。

**判斷依據**：diff 中 `tearDown` 改為 async，但 `reset()` 呼叫未加 await。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 87953 (cache hit 1536) ｜ completion tokens 2290 ｜ PR #8</sub>