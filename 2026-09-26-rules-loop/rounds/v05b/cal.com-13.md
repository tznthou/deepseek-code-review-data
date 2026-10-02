<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並新增對應的 DI 模組與 token。主要風險在於 DI 模組的 token 設定不一致，可能導致容器解析失敗；此外，測試改用全域容器取得服務，可能造成測試間狀態污染。整體架構方向合理，但需修正 token 設定與測試隔離問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 設定錯誤，導致 DI 容器無法解析 | 0.95 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82` | 測試使用全域 DI 容器，可能造成測試間狀態污染 | 0.80 |
| ⚠️ | Major | `packages/features/di/modules/FeatureOptInService.ts:19` | FeatureOptInService 模組的 token 設定可能不一致 | 0.75 |
| 🔸 | Minor | `packages/features/di/tokens.ts:39` | DI_TOKENS 合併可能造成 Symbol 重複 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 設定錯誤，導致 DI 容器無法解析</summary>

在 `FeaturesRepository.ts` 中，`moduleLoader` 的 `token` 被設定為 `moduleToken`（`FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`），但 `bindModuleToClassOnToken` 綁定的是 `token`（`FLAGS_DI_TOKENS.FEATURES_REPOSITORY`）。這會導致 `getFeaturesRepository()` 嘗試以 `moduleToken` 從容器取得實例時失敗，因為容器中註冊的是 `token`。

**失敗情境**：呼叫 `getFeaturesRepository()` 時，`container.get(moduleToken)` 會拋出「找不到綁定」的錯誤。

**建議修法**：將 `moduleLoader.token` 改為 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），與其他模組的慣例一致。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 第 20 行 `token: moduleToken`，但第 12 行 `bindModuleToClassOnToken` 使用的 `token` 是 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82</code> 測試使用全域 DI 容器，可能造成測試間狀態污染</summary>

測試中改用 `getFeaturesRepository()` 與 `getFeatureOptInService()`，這兩個函式每次呼叫都會建立新的容器，但測試內並未在 `afterEach` 中清理或重置容器。若測試之間共享全域狀態（例如 Prisma 連線或快取），可能導致測試互相影響。

**失敗情境**：若某個測試修改了全域的 Prisma 實例或容器快取，後續測試可能讀到髒資料。

**建議修法**：在 `afterEach` 中呼叫容器清理方法（如果有的話），或改為在 `setup` 中建立容器並在測試結束後銷毀。

**判斷依據**：diff 中第 82-83 行改為呼叫全域容器取得服務，但未見對應的清理邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/modules/FeatureOptInService.ts:19</code> FeatureOptInService 模組的 token 設定可能不一致</summary>

`FeatureOptInService.ts` 中，`moduleLoader.token` 設定為 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`，但 `bindModuleToClassOnToken` 綁定的 `token` 也是同一個。這與 `FeaturesRepository.ts` 的錯誤不同，但需確認 `getFeatureOptInService()` 是否使用正確的 token 取得實例。

**失敗情境**：若 `getFeatureOptInService()` 使用 `moduleToken` 取得實例，則會失敗；若使用 `token` 則正常。目前 `getFeatureOptInService()` 使用 `featureOptInServiceModuleLoader.token`，而該 token 是 `FEATURE_OPT_IN_SERVICE`，因此可能正確。但需確認 `bindModuleToClassOnToken` 的實作是否會將 `token` 註冊到容器中。

**判斷依據**：diff 中新增的 `FeatureOptInService.ts` 第 18-21 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/tokens.ts:39</code> DI_TOKENS 合併可能造成 Symbol 重複</summary>

在 `DI_TOKENS` 中合併 `FLAGS_DI_TOKENS` 與 `FEATURE_OPT_IN_DI_TOKENS`，但原本的 `FEATURES_REPOSITORY` 與 `FEATURES_REPOSITORY_MODULE` 被移除。若其他程式碼仍直接引用 `DI_TOKENS.FEATURES_REPOSITORY`，會導致 undefined。需確認所有引用都已更新。

**判斷依據**：diff 中 `packages/features/di/tokens.ts` 第 39-40 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7833 (cache hit 7808) ｜ completion tokens 1351 ｜ PR #13</sub>