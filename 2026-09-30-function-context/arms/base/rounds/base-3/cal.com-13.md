<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為依賴注入（DI）容器管理，並新增對應的容器與模組。主要風險在於 DI token 的合併方式可能造成 Symbol 重複或型別衝突，以及新容器每次呼叫都建立新實例可能影響效能與狀態一致性。整體結構合理，但需確認 token 命名空間與容器生命週期。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/di/tokens.ts:39` | DI token 合併可能造成 Symbol 重複或型別衝突 | 0.80 |
| 🔸 | Minor | `packages/features/di/containers/FeatureOptInService.ts:6` | 每次呼叫 getFeatureOptInService 都建立新容器與新服務實例 | 0.70 |
| 🔸 | Minor | `packages/features/di/containers/FeaturesRepository.ts:4` | 每次呼叫 getFeaturesRepository 都建立新容器與新 repository 實例 | 0.70 |
| 🔸 | Minor | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 使用 moduleToken 而非 token | 0.60 |
| 🔹 | Nit | `packages/features/feature-opt-in/services/IFeatureOptInService.ts:11` | 多餘的空白 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/tokens.ts:39</code> DI token 合併可能造成 Symbol 重複或型別衝突</summary>

在 `DI_TOKENS` 物件中使用 spread 運算子合併 `FLAGS_DI_TOKENS` 與 `FEATURE_OPT_IN_DI_TOKENS`，若這些 token 物件中有相同的鍵名，後者會覆蓋前者，導致 token 不一致。此外，原本的 `FEATURES_REPOSITORY` 與 `FEATURES_REPOSITORY_MODULE` 被移除，改由 `FLAGS_DI_TOKENS` 提供，但若其他程式碼仍直接引用 `DI_TOKENS.FEATURES_REPOSITORY`，將導致 undefined。建議明確列出所有 token，或使用 `Object.freeze` 與型別檢查確保唯一性。

**判斷依據**：diff 中刪除了原本的 `FEATURES_REPOSITORY` 與 `FEATURES_REPOSITORY_MODULE`，並新增 spread 合併。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/containers/FeatureOptInService.ts:6</code> 每次呼叫 getFeatureOptInService 都建立新容器與新服務實例</summary>

`getFeatureOptInService` 每次呼叫都會建立新的 DI 容器並載入模組，這可能導致效能浪費，且若服務內部有狀態（例如快取），狀態不會被共享。建議考慮使用單例模式或模組層級的容器快取。

**判斷依據**：diff 中新增的容器函式，每次呼叫都建立新容器。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/containers/FeaturesRepository.ts:4</code> 每次呼叫 getFeaturesRepository 都建立新容器與新 repository 實例</summary>

與 `getFeatureOptInService` 相同，每次呼叫都建立新容器，可能造成不必要的資源消耗。若 repository 無狀態則影響較小，但仍建議考慮快取。

**判斷依據**：diff 中新增的容器函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 使用 moduleToken 而非 token</summary>

在 `moduleLoader` 物件中，`token` 屬性被設定為 `moduleToken`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`），而其他模組通常使用 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`）。這可能導致使用 `moduleLoader.token` 取得服務時型別不符或找不到綁定。請確認此處是否應為 `token` 而非 `moduleToken`。

**判斷依據**：diff 中新增的 moduleLoader，token 使用 moduleToken。

</details>

<details><summary>🔹 <b>Nit</b> — <code>packages/features/feature-opt-in/services/IFeatureOptInService.ts:11</code> 多餘的空白</summary>

在 `orgAutoOptIn: boolean;` 後面有多餘的空白，雖然不影響功能，但建議移除。

**判斷依據**：diff 中新增的介面定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6425 (cache hit 6400) ｜ completion tokens 1234 ｜ PR #13</sub>