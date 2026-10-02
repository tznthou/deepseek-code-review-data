<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並新增對應的模組與容器。主要風險在於 DI token 的合併可能造成 Symbol 重複或型別衝突，以及容器建立方式可能導致每次呼叫都建立新實例，影響效能與狀態一致性。建議先確認 token 合併的影響，並考慮將容器改為單例。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/di/tokens.ts:39` | DI token 合併可能造成 Symbol 重複或型別衝突 | 0.80 |
| ⚠️ | Major | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader 的 token 可能設定錯誤 | 0.75 |
| 🔸 | Minor | `packages/features/di/containers/FeatureOptInService.ts:6` | 每次呼叫都建立新容器，可能造成效能與狀態問題 | 0.70 |
| 🔸 | Minor | `packages/features/di/containers/FeaturesRepository.ts:4` | 每次呼叫都建立新容器，可能造成效能與狀態問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/tokens.ts:39</code> DI token 合併可能造成 Symbol 重複或型別衝突</summary>

在 `DI_TOKENS` 物件中直接展開 `FLAGS_DI_TOKENS` 與 `FEATURE_OPT_IN_DI_TOKENS`，若這些 token 物件中有與現有 `DI_TOKENS` 相同的 key，後面的展開會覆蓋前面的值，導致 token 不一致。此外，`Symbol` 的描述字串可能重複，但 Symbol 本身是唯一的，因此不會造成實際衝突，但可能造成除錯困難。建議明確列出需要的 token，或使用 `Object.assign` 並檢查衝突。

**判斷依據**：diff 中新增了 `...FLAGS_DI_TOKENS` 與 `...FEATURE_OPT_IN_DI_TOKENS`，且刪除了原本的 `FEATURES_REPOSITORY` 與 `FEATURES_REPOSITORY_MODULE`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader 的 token 可能設定錯誤</summary>

`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`，但其他模組（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token。這可能導致容器在取得服務時使用錯誤的 token。請確認 `moduleLoader.token` 應該是要回傳哪一個 token。

**判斷依據**：在 `FeatureOptInService.ts` 中，`moduleLoader.token` 是 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`，而此處是 `moduleToken`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/containers/FeatureOptInService.ts:6</code> 每次呼叫都建立新容器，可能造成效能與狀態問題</summary>

`getFeatureOptInService()` 每次呼叫都會建立新的容器並載入模組，這可能導致不必要的效能開銷，且若服務內部有狀態（例如快取），每次取得都會是全新的實例。建議考慮使用單例模式或模組層級的容器。

**判斷依據**：diff 中新增的容器函式每次呼叫都建立新容器。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/containers/FeaturesRepository.ts:4</code> 每次呼叫都建立新容器，可能造成效能與狀態問題</summary>

`getFeaturesRepository()` 每次呼叫都會建立新的容器並載入模組，這可能導致不必要的效能開銷，且若 repository 內部有狀態（例如快取），每次取得都會是全新的實例。建議考慮使用單例模式或模組層級的容器。

**判斷依據**：diff 中新增的容器函式每次呼叫都建立新容器。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6425 (cache hit 6400) ｜ completion tokens 1106 ｜ PR #13</sub>