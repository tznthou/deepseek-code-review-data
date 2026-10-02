<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並將相關 token 移至各自 feature 的 di/tokens.ts。整體方向合理，但存在一個 blocker：FeaturesRepository 的 moduleLoader token 設定錯誤，導致 getFeaturesRepository() 無法取得實例。此外，DI 容器每次呼叫都新建，可能造成資源浪費與狀態不一致，建議改為 singleton。另有介面型別匯入不一致、測試未使用 DI 等 minor 問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader token 設定錯誤，導致 getFeaturesRepository() 無法取得實例 | 0.95 |
| ⚠️ | Major | `packages/features/di/containers/FeatureOptInService.ts:6` | 每次呼叫 getFeatureOptInService() 都建立新的 DI 容器，可能造成資源浪費與狀態不一致 | 0.80 |
| ⚠️ | Major | `packages/features/di/containers/FeaturesRepository.ts:4` | 每次呼叫 getFeaturesRepository() 都建立新的 DI 容器，可能造成資源浪費與狀態不一致 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82` | 整合測試未使用 DI 容器，而是直接呼叫 getFeatureOptInService() 與 getFeaturesRepository() | 0.70 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/IFeatureOptInService.ts:1` | 介面檔案匯入型別不一致：FeatureState 從 config 匯入，但 FeatureId 從 config 匯入 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader token 設定錯誤，導致 getFeaturesRepository() 無法取得實例</summary>

在 `FeaturesRepository.ts` 中，`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`（`FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`），但 `getFeaturesRepository()` 使用 `featuresRepositoryModuleLoader.token` 來取得實例。這會導致 `container.get()` 使用錯誤的 token，無法取得綁定的 `FeaturesRepository` 實例，造成 runtime error。

建議將 `moduleLoader` 的 `token` 改為 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），與其他 module 的慣例一致。

**判斷依據**：diff 中新增的 `packages/features/di/modules/FeaturesRepository.ts` 第 20-23 行，`token: moduleToken`；而 `packages/features/di/containers/FeaturesRepository.ts` 第 7 行使用 `featuresRepositoryModuleLoader.token` 來取得實例。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeatureOptInService.ts:6</code> 每次呼叫 getFeatureOptInService() 都建立新的 DI 容器，可能造成資源浪費與狀態不一致</summary>

`getFeatureOptInService()` 每次呼叫都會建立新的 `createContainer()` 並載入模組。若此函式被頻繁呼叫（例如每個 request），會重複建立容器與實例，可能導致效能問題，且若模組內有狀態（如快取），狀態不會共享。

建議將容器建立改為 singleton 模式，或使用全域共用的容器。

**判斷依據**：diff 中新增的 `packages/features/di/containers/FeatureOptInService.ts` 第 6-9 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeaturesRepository.ts:4</code> 每次呼叫 getFeaturesRepository() 都建立新的 DI 容器，可能造成資源浪費與狀態不一致</summary>

`getFeaturesRepository()` 每次呼叫都會建立新的 `createContainer()` 並載入模組。若此函式被頻繁呼叫，會重複建立容器與實例，可能導致效能問題，且若模組內有狀態（如快取），狀態不會共享。

建議將容器建立改為 singleton 模式，或使用全域共用的容器。

**判斷依據**：diff 中新增的 `packages/features/di/containers/FeaturesRepository.ts` 第 5-8 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82</code> 整合測試未使用 DI 容器，而是直接呼叫 getFeatureOptInService() 與 getFeaturesRepository()</summary>

測試中直接呼叫 `getFeatureOptInService()` 與 `getFeaturesRepository()`，這會建立新的 DI 容器，而非使用測試環境中可能已設定的容器。這可能導致測試與實際應用程式使用不同的依賴設定，降低測試的可靠性。

建議在測試中注入 mock 或使用測試專用的 DI 容器。

**判斷依據**：diff 中 `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts` 第 82-83 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/IFeatureOptInService.ts:1</code> 介面檔案匯入型別不一致：FeatureState 從 config 匯入，但 FeatureId 從 config 匯入</summary>

在 `IFeatureOptInService.ts` 中，`FeatureState` 從 `@calcom/features/flags/config` 匯入，但 `FeatureId` 也從同一處匯入。然而，在 `FeatureOptInService.ts` 中，`FeatureId` 是從 `@calcom/features/flags/config` 匯入，而 `FeatureState` 是從 `@calcom/features/flags/config` 匯入。這可能導致型別不一致或循環依賴。

建議確認型別來源，並統一匯入路徑。

**判斷依據**：diff 中新增的 `packages/features/feature-opt-in/services/IFeatureOptInService.ts` 第 1 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7049 (cache hit 6400) ｜ completion tokens 1565 ｜ PR #13</sub>