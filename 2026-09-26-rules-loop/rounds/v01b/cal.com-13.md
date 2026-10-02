<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並新增對應的 DI 模組與容器。主要風險在於 DI 模組的 token 設定不一致，可能導致執行時期解析失敗；此外，測試改用全域容器取得服務，可能造成測試間的狀態污染。建議先修正 token 設定並確認測試隔離性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 設定錯誤，導致 DI 解析失敗 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82` | 測試使用全域 DI 容器可能造成狀態污染 | 0.80 |
| 🔸 | Minor | `packages/features/di/modules/FeatureOptInService.ts:11` | DI 模組依賴的 token 可能不一致 | 0.70 |
| 🔸 | Minor | `packages/features/di/tokens.ts:39` | DI_TOKENS 合併可能造成 Symbol 重複或衝突 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 設定錯誤，導致 DI 解析失敗</summary>

`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`（`FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`），但其他模組的慣例是設定為實際綁定的 token（`FLAGS_DI_TOKENS.FEATURES_REPOSITORY`）。這會導致依賴此模組的程式碼（例如 `FeatureOptInService` 模組）在解析 `featuresRepositoryModuleLoader.token` 時取得錯誤的 token，進而無法從容器中取得 `FeaturesRepository` 實例，造成執行時期錯誤。

建議將 `token` 改為 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。

**判斷依據**：diff 中新增的 `packages/features/di/modules/FeaturesRepository.ts` 第 19 行 `token: moduleToken`，而 `moduleToken` 定義為 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`。對比同 PR 中 `FeatureOptInService.ts` 模組的 `moduleLoader.token` 設定為 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`（實際 token），以及舊版 `Features.ts` 中 `moduleLoader.token` 設定為 `DI_TOKENS.FEATURES_REPOSITORY`，可確認此處應為實際 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82</code> 測試使用全域 DI 容器可能造成狀態污染</summary>

測試中改用 `getFeaturesRepository()` 和 `getFeatureOptInService()`，這兩個函式每次呼叫都會建立新的容器，但 `FeatureOptInService` 可能內部持有狀態（例如快取），且測試之間可能共享相同的全域模組狀態。若測試並行執行或依賴特定狀態，可能導致測試不穩定或互相影響。

建議確認 `FeatureOptInService` 是否為無狀態，或改為在每個測試中建立獨立的服務實例，並確保容器不會被重複使用。

**判斷依據**：diff 中 `FeatureOptInService.integration-test.ts` 第 82 行改為使用 `getFeaturesRepository()` 和 `getFeatureOptInService()`，這兩個函式來自 `packages/features/di/containers/`，其內部會建立新的容器，但未提供清理機制。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/modules/FeatureOptInService.ts:11</code> DI 模組依賴的 token 可能不一致</summary>

`FeatureOptInService` 模組依賴 `featuresRepositoryModuleLoader`，但 `featuresRepositoryModuleLoader` 的 `token` 屬性目前設定為 `moduleToken`（`FEATURES_REPOSITORY_MODULE`），而非實際的 `FEATURES_REPOSITORY` token。這可能導致依賴解析時無法正確取得 `FeaturesRepository` 實例。

建議確認 `featuresRepositoryModuleLoader` 的 `token` 設定是否正確，並確保所有依賴模組的 token 一致。

**判斷依據**：diff 中 `FeatureOptInService.ts` 第 14 行使用 `dep: featuresRepositoryModuleLoader`，而 `featuresRepositoryModuleLoader` 來自 `./FeaturesRepository`，其 `token` 屬性在該檔案中設定為 `moduleToken`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/tokens.ts:39</code> DI_TOKENS 合併可能造成 Symbol 重複或衝突</summary>

`DI_TOKENS` 物件使用 spread 運算子合併 `FLAGS_DI_TOKENS` 和 `FEATURE_OPT_IN_DI_TOKENS`，但原有的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE` 已被移除。若其他程式碼仍直接引用 `DI_TOKENS.FEATURES_REPOSITORY`，將導致 undefined。

建議搜尋程式碼中是否仍有直接使用 `DI_TOKENS.FEATURES_REPOSITORY` 的地方，並確認合併後的 token 不會與其他 token 衝突。

**判斷依據**：diff 中 `packages/features/di/tokens.ts` 第 39 行移除了原有的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE`，改為合併 `FLAGS_DI_TOKENS` 和 `FEATURE_OPT_IN_DI_TOKENS`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7864 (cache hit 7808) ｜ completion tokens 1474 ｜ PR #13</sub>