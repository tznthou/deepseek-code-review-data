<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並引入對應的介面與模組。主要風險在於 DI 模組的 token 設定不一致，可能導致執行時期解析失敗；此外，測試中直接使用容器取得的服務，可能因快取或狀態共享造成測試隔離問題。建議先修正 token 設定並確認測試的獨立性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 設定為 moduleToken 而非 token，可能導致容器解析失敗 | 0.95 |
| ⚠️ | Major | `packages/features/di/modules/FeatureOptInService.ts:19` | moduleLoader.token 設定為服務 token 而非模組 token，可能導致依賴解析不一致 | 0.80 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82` | 測試中直接使用容器取得的服務，可能因快取或狀態共享導致測試隔離問題 | 0.75 |
| 🔸 | Minor | `packages/features/di/tokens.ts:39` | DI_TOKENS 中展開 FLAGS_DI_TOKENS 和 FEATURE_OPT_IN_DI_TOKENS 可能造成 token 衝突 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 設定為 moduleToken 而非 token，可能導致容器解析失敗</summary>

在 `FeaturesRepository.ts` 中，`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`），但其他模組（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token（`FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`）。這可能導致依賴此模組的容器在解析 `FeaturesRepository` 時，使用錯誤的 token 而找不到綁定，進而拋出錯誤。

**失敗情境**：當 `FeatureOptInService` 模組載入時，它依賴 `featuresRepositoryModuleLoader`，而該 loader 的 `token` 是 `moduleToken`。若容器在解析依賴時使用 `moduleLoader.token` 來查找綁定，則會找不到以 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY` 為 token 的綁定，導致解析失敗。

**建議**：將 `moduleLoader.token` 改為 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），與其他模組保持一致。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 第 19-22 行顯示 `token: moduleToken`，而 `FeatureOptInService.ts` 第 20-23 行顯示 `token` 為服務 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/modules/FeatureOptInService.ts:19</code> moduleLoader.token 設定為服務 token 而非模組 token，可能導致依賴解析不一致</summary>

在 `FeatureOptInService.ts` 中，`moduleLoader.token` 被設定為 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`（服務 token），但其他模組（如 `FeaturesRepository.ts`）的 `moduleLoader.token` 是設定為模組 token。這可能導致容器在載入模組時，使用錯誤的 token 進行綁定或解析，造成依賴注入失敗。

**失敗情境**：當容器載入 `FeatureOptInService` 模組時，它會使用 `moduleLoader.token` 來註冊模組。若容器預期 `moduleLoader.token` 是模組 token，但實際上是服務 token，則後續解析服務時可能找不到正確的綁定。

**建議**：確認 `moduleLoader.token` 的語意。若它代表模組的 token，應改為 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE_MODULE`；若代表服務 token，則需確保所有模組一致。

**判斷依據**：diff 中新增的 `FeatureOptInService.ts` 第 20-23 行顯示 `token` 為 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`，而 `FeaturesRepository.ts` 使用 `moduleToken`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82</code> 測試中直接使用容器取得的服務，可能因快取或狀態共享導致測試隔離問題</summary>

在測試的 `setup()` 函式中，`featuresRepository` 和 `service` 改為透過 `getFeaturesRepository()` 和 `getFeatureOptInService()` 取得。這些函式每次呼叫都會建立新的容器，但若底層的 `FeaturesRepository` 或 `FeatureOptInService` 內部有靜態狀態或快取，可能會在不同測試之間共享，導致測試互相影響。

**失敗情境**：若 `FeaturesRepository` 內部有快取（例如 `getAllFeatures()` 的結果），且快取未在測試間清除，則一個測試建立的 feature 可能被另一個測試看到，造成非預期的行為。

**建議**：確認 `FeaturesRepository` 和 `FeatureOptInService` 是否為無狀態，或確保每個測試使用獨立的實例。若有必要，可在測試中手動建立實例，或提供重置快取的方法。

**判斷依據**：diff 中測試檔案第 31-32 行顯示改用容器取得服務，而原本是直接 `new`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/tokens.ts:39</code> DI_TOKENS 中展開 FLAGS_DI_TOKENS 和 FEATURE_OPT_IN_DI_TOKENS 可能造成 token 衝突</summary>

在 `DI_TOKENS` 物件中，原本的 `FEATURES_REPOSITORY` 和 `FEATURES_REPOSITORY_MODULE` 被移除，改為展開 `FLAGS_DI_TOKENS` 和 `FEATURE_OPT_IN_DI_TOKENS`。這可能導致與其他展開的 token 物件（如 `BOOKING_AUDIT_DI_TOKENS`）中的同名屬性衝突，後展開的會覆蓋先前的。

**失敗情境**：若 `FLAGS_DI_TOKENS` 或 `FEATURE_OPT_IN_DI_TOKENS` 中的 token 名稱與其他展開物件中的名稱相同，則會發生覆蓋，導致某些模組使用錯誤的 token。

**建議**：確認所有展開的 token 物件中的屬性名稱都是唯一的，或考慮使用更明確的命名空間。

**判斷依據**：diff 中 `tokens.ts` 第 13-14 行顯示展開兩個新的 token 物件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9824 (cache hit 9728) ｜ completion tokens 1676 ｜ PR #13</sub>