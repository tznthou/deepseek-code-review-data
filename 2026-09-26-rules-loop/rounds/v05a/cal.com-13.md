<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器建立，並新增對應的 module 與 container。主要風險在於 DI token 的合併方式可能造成 Symbol 重複定義，以及 moduleLoader 的 token 欄位可能誤植為 moduleToken，導致容器解析失敗。建議先修正這兩個問題再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/tokens.ts:39` | DI token 合併可能造成 Symbol 重複定義 | 0.95 |
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader 的 token 欄位誤植為 moduleToken | 0.90 |
| ⚠️ | Major | `packages/features/di/containers/FeatureOptInService.ts:6` | 每次呼叫 getFeatureOptInService 都會建立新的容器 | 0.80 |
| ⚠️ | Major | `packages/features/di/containers/FeaturesRepository.ts:4` | 每次呼叫 getFeaturesRepository 都會建立新的容器 | 0.80 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/IFeatureOptInService.ts:11` | 多餘的空白字元 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/tokens.ts:39</code> DI token 合併可能造成 Symbol 重複定義</summary>

在 `DI_TOKENS` 物件中，使用 spread 運算子將 `FLAGS_DI_TOKENS` 與 `FEATURE_OPT_IN_DI_TOKENS` 合併，但這兩個物件中的 Symbol 名稱可能與原本的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE` 重複。原本的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE` 已被刪除，但若其他程式碼仍依賴這些 Symbol，會導致解析失敗。此外，`FLAGS_DI_TOKENS` 中的 Symbol 名稱與原本相同，但 Symbol 本身是新的，因此任何使用舊 Symbol 的地方都會失效。建議確認所有使用舊 Symbol 的地方都已更新，或保留舊 Symbol 作為別名。

**判斷依據**：diff 中刪除了原本的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE`，並新增了 `...FLAGS_DI_TOKENS` 和 `...FEATURE_OPT_IN_DI_TOKENS`。由於 Symbol 是唯一的，即使名稱相同，新的 Symbol 也不同於舊的，因此任何使用舊 Symbol 的程式碼都會失效。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader 的 token 欄位誤植為 moduleToken</summary>

在 `moduleLoader` 物件中，`token` 屬性被設定為 `moduleToken`，但根據其他 module 的慣例，`token` 應該是用於解析實例的 token（即 `FEATURES_REPOSITORY`），而不是 module token。這會導致使用 `moduleLoader.token` 來取得實例時，實際拿到的是 module token，造成型別不符或解析失敗。建議將 `token` 改為 `token`（即 `FEATURES_REPOSITORY`）。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 檔案，`moduleLoader` 的 `token` 欄位被設定為 `moduleToken`，而其他 module（如 `FeatureOptInService.ts`）的 `moduleLoader` 的 `token` 欄位是設定為 `token`（即實例 token）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeatureOptInService.ts:6</code> 每次呼叫 getFeatureOptInService 都會建立新的容器</summary>

`getFeatureOptInService` 函式每次呼叫都會建立一個新的容器並載入 module，這可能導致效能問題，且若 module 內有狀態，會產生不一致。建議考慮使用單例模式或快取容器，避免重複建立。

**判斷依據**：diff 中新增的 `FeatureOptInService.ts` 容器檔案，函式內每次都建立新容器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeaturesRepository.ts:4</code> 每次呼叫 getFeaturesRepository 都會建立新的容器</summary>

`getFeaturesRepository` 函式每次呼叫都會建立一個新的容器並載入 module，這可能導致效能問題，且若 module 內有狀態，會產生不一致。建議考慮使用單例模式或快取容器，避免重複建立。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 容器檔案，函式內每次都建立新容器。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/IFeatureOptInService.ts:11</code> 多餘的空白字元</summary>

在 `orgAutoOptIn: boolean;` 後面有多餘的空白字元，可能違反格式規範（R03）。建議移除多餘空白。

**判斷依據**：diff 中新增的 `IFeatureOptInService.ts` 檔案，該行末尾有三個空格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7833 (cache hit 6400) ｜ completion tokens 1415 ｜ PR #13</sub>