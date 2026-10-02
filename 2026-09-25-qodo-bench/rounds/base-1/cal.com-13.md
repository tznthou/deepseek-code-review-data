<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為依賴注入（DI）模式，新增容器與模組載入器，並更新相關 import 與測試。主要風險在於 DI token 的合併可能造成 Symbol 重複或型別衝突，以及容器建立方式可能導致每個請求都建立新實例，影響效能與狀態一致性。建議先確認 token 合併的相容性與容器生命週期。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/di/tokens.ts:39` | DI token 合併可能造成 Symbol 重複或型別衝突 | 0.80 |
| ⚠️ | Major | `packages/features/di/containers/FeatureOptInService.ts:6` | 每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題 | 0.75 |
| ⚠️ | Major | `packages/features/di/containers/FeaturesRepository.ts:4` | 每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題 | 0.75 |
| 🔸 | Minor | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader 的 token 可能與綁定 token 不一致 | 0.60 |
| 🔸 | Minor | `packages/features/di/modules/FeatureOptInService.ts:19` | moduleLoader 的 token 可能與綁定 token 不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/tokens.ts:39</code> DI token 合併可能造成 Symbol 重複或型別衝突</summary>

在 `DI_TOKENS` 物件中，原本的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE` 被移除，改為展開 `FLAGS_DI_TOKENS` 和 `FEATURE_OPT_IN_DI_TOKENS`。如果這兩個新 token 物件中的 Symbol 名稱與其他已存在的 token 重複，會導致依賴注入容器中的綁定衝突，可能造成錯誤的實例被注入。建議確認所有 Symbol 名稱在全域是唯一的，或考慮使用命名空間前綴。

**判斷依據**：diff 中刪除了原本的 FEATURES_REPOSITORY 相關 token，並展開新的 token 物件。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeatureOptInService.ts:6</code> 每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題</summary>

`getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

**判斷依據**：diff 中新增的容器建立邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeaturesRepository.ts:4</code> 每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題</summary>

`getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

**判斷依據**：diff 中新增的容器建立邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader 的 token 可能與綁定 token 不一致</summary>

在 `moduleLoader` 中，`token` 被設定為 `moduleToken`，但 `bindModuleToClassOnToken` 的 `token` 參數是 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。這可能導致使用 `moduleLoader.token` 來取得實例時，實際上是取得模組 token 而非服務 token，造成型別或實例錯誤。建議確認 `moduleLoader.token` 應該回傳服務 token 還是模組 token，並保持一致性。

**判斷依據**：diff 中 moduleLoader 的 token 設定。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/modules/FeatureOptInService.ts:19</code> moduleLoader 的 token 可能與綁定 token 不一致</summary>

在 `moduleLoader` 中，`token` 被設定為 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`，但 `bindModuleToClassOnToken` 的 `token` 參數也是同一個。這可能導致使用 `moduleLoader.token` 來取得實例時，實際上是取得服務 token 而非模組 token，造成型別或實例錯誤。建議確認 `moduleLoader.token` 應該回傳服務 token 還是模組 token，並保持一致性。

**判斷依據**：diff 中 moduleLoader 的 token 設定。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6425 (cache hit 1536) ｜ completion tokens 1357 ｜ PR #13</sub>