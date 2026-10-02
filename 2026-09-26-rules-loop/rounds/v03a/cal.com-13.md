<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並新增對應的 DI 模組與 token。主要風險在於 DI 模組的 token 設定不一致，可能導致容器解析失敗；此外，新模組的 token 來源與既有慣例不同，需確認是否為刻意設計。整體結構尚可，但建議先修正 token 設定問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | DI 模組的 token 設定錯誤，可能導致容器解析失敗 | 0.95 |
| ⚠️ | Major | `packages/features/di/modules/FeatureOptInService.ts:8` | DI 模組的 token 來源不一致，可能造成混淆 | 0.80 |
| 🔸 | Minor | `packages/features/di/modules/FeaturesRepository.ts:8` | 模組 token 與服務 token 的命名可能造成混淆 | 0.70 |
| 🔸 | Minor | `packages/features/di/tokens.ts:39` | DI token 合併方式可能導致意外覆蓋 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> DI 模組的 token 設定錯誤，可能導致容器解析失敗</summary>

在 `moduleLoader` 中，`token` 被設定為 `moduleToken`，但 `moduleToken` 是模組載入用的 token，而非服務本身的 token。這會導致使用 `featuresRepositoryModuleLoader.token` 來解析服務時，實際取得的 token 是模組 token，可能造成型別不符或解析失敗。

建議將 `token` 改為服務本身的 token（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），並確認 `moduleToken` 僅用於 `loadModule` 的 `container.load`。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 第 19 行將 `token` 設為 `moduleToken`，而其他模組（如 `FeatureOptInService.ts`）的 `token` 是服務 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/modules/FeatureOptInService.ts:8</code> DI 模組的 token 來源不一致，可能造成混淆</summary>

`FeatureOptInService` 模組使用 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE` 作為 token，但 `FeaturesRepository` 模組使用 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。兩者皆為新建立的 token 群組，但命名與來源不同，可能導致維護上的混淆。

建議統一 token 的來源，或確認此設計是否有特殊考量。

**判斷依據**：diff 中新增的 `FeatureOptInService.ts` 第 8 行使用 `FEATURE_OPT_IN_DI_TOKENS`，而 `FeaturesRepository.ts` 使用 `FLAGS_DI_TOKENS`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/modules/FeaturesRepository.ts:8</code> 模組 token 與服務 token 的命名可能造成混淆</summary>

`FLAGS_DI_TOKENS` 中同時定義了 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE`，但在 `moduleLoader` 中將 `token` 設為 `moduleToken`，這可能讓使用 `moduleLoader.token` 的程式碼誤以為取得的是服務 token。

建議在 `moduleLoader` 中明確區分服務 token 與模組 token，或提供獨立的屬性。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 第 8-9 行定義了兩個 token，但後續使用可能混淆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/tokens.ts:39</code> DI token 合併方式可能導致意外覆蓋</summary>

在 `DI_TOKENS` 中使用 spread 運算子合併 `FLAGS_DI_TOKENS` 和 `FEATURE_OPT_IN_DI_TOKENS`，若未來有相同名稱的 token，後者會覆蓋前者。目前沒有衝突，但建議改用明確的巢狀結構或命名空間來避免潛在問題。

**判斷依據**：diff 中 `tokens.ts` 第 39-40 行使用 spread 合併，可能造成覆蓋。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7874 (cache hit 6400) ｜ completion tokens 1156 ｜ PR #13</sub>