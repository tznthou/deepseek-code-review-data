<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並新增對應的 DI 模組與 token。主要風險在於 DI 模組的 token 設定不一致，可能導致執行時期解析失敗；此外，部分檔案命名與專案規範 R01 不符，且測試改用全域容器可能造成測試隔離問題。建議先修正 token 設定與命名問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 設定為 moduleToken 而非 token，導致容器解析失敗 | 0.95 |
| 🛑 | Blocker | `packages/features/di/modules/FeatureOptInService.ts:19` | moduleLoader.token 設定為 token 而非 moduleToken，可能導致容器解析失敗 | 0.90 |
| ⚠️ | Major | `packages/features/di/modules/FeaturesRepository.ts:2` | [R01] 檔案名稱與類別名稱不符，違反命名慣例 | 0.80 |
| ⚠️ | Major | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82` | 測試改用全域容器取得服務，可能造成測試隔離問題 | 0.75 |
| 🔸 | Minor | `packages/features/di/tokens.ts:39` | 使用 spread 運算子合併 token 物件，可能造成屬性覆蓋或型別混淆 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 設定為 moduleToken 而非 token，導致容器解析失敗</summary>

在 `moduleLoader` 中，`token` 屬性被設定為 `moduleToken`，但 `bindModuleToClassOnToken` 綁定的是 `token`（`FLAGS_DI_TOKENS.FEATURES_REPOSITORY`）。這會造成 `getFeaturesRepository()` 中 `container.get(featuresRepositoryModuleLoader.token)` 嘗試以 `moduleToken` 取得實例，但容器中註冊的 key 是 `token`，導致解析失敗。

**失敗情境**：呼叫 `getFeaturesRepository()` 時，會拋出「找不到對應 token」的錯誤。

**建議**：將 `moduleLoader.token` 改為 `token`。

**判斷依據**：diff 中新增的 `packages/features/di/modules/FeaturesRepository.ts` 第 18 行明確將 `token` 設為 `moduleToken`，而 `bindModuleToClassOnToken` 使用的 `token` 是 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeatureOptInService.ts:19</code> moduleLoader.token 設定為 token 而非 moduleToken，可能導致容器解析失敗</summary>

在 `moduleLoader` 中，`token` 屬性被設定為 `token`（`FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`），但 `bindModuleToClassOnToken` 綁定的是 `token`，而 `moduleToken` 用於載入模組。這與其他模組的慣例不一致（例如 `FeaturesRepository` 的 `moduleLoader.token` 是 `moduleToken`）。雖然 `getFeatureOptInService()` 使用 `featureOptInServiceModuleLoader.token` 來取得服務，但若其他程式碼嘗試以 `moduleToken` 載入模組，可能會失敗。

**失敗情境**：若有程式碼依賴 `moduleToken` 來載入此模組，會因為 `moduleLoader.token` 不是 `moduleToken` 而無法正確載入。

**建議**：將 `moduleLoader.token` 改為 `moduleToken`，並確認 `getFeatureOptInService()` 使用正確的 token 取得服務。

**判斷依據**：diff 中新增的 `packages/features/di/modules/FeatureOptInService.ts` 第 20 行將 `token` 設為 `token`，而 `bindModuleToClassOnToken` 的 `moduleToken` 是 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE_MODULE`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/modules/FeaturesRepository.ts:2</code> [R01] 檔案名稱與類別名稱不符，違反命名慣例</summary>

專案規範 R01 要求 repository 檔案名稱應為 `Prisma<Entity>Repository.ts`，但此檔案命名為 `FeaturesRepository.ts`，且匯出的類別為 `FeaturesRepository`。這可能導致不一致性，並影響自動化工具或開發者搜尋。

**建議**：將檔案重新命名為 `PrismaFeaturesRepository.ts`，並相應調整匯入路徑。

**判斷依據**：diff 中新增的 `packages/features/di/modules/FeaturesRepository.ts` 第 1 行匯入了 `FeaturesRepository`，但檔案名稱未遵循 `Prisma<Entity>Repository` 模式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82</code> 測試改用全域容器取得服務，可能造成測試隔離問題</summary>

原本測試直接建立 `FeaturesRepository` 和 `FeatureOptInService`，現在改為使用 `getFeaturesRepository()` 和 `getFeatureOptInService()`。這些函式會建立新的容器並載入模組，但若模組內部有共享狀態（例如 Prisma client），可能導致測試之間的資料污染。此外，若容器建立成本高，可能拖慢測試。

**失敗情境**：若多個測試同時執行，且容器內的服務具有可變狀態，可能互相影響。

**建議**：考慮在測試中使用獨立的容器實例，或確保容器內的服務是無狀態的。

**判斷依據**：diff 中 `FeatureOptInService.integration-test.ts` 第 82 行改為使用全域容器取得服務，取代原本的直接實例化。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/di/tokens.ts:39</code> 使用 spread 運算子合併 token 物件，可能造成屬性覆蓋或型別混淆</summary>

在 `DI_TOKENS` 中使用 `...FLAGS_DI_TOKENS` 和 `...FEATURE_OPT_IN_DI_TOKENS` 來合併 token。如果未來這些 token 物件有重複的屬性名稱，後面的 spread 會覆蓋前面的，可能導致非預期的行為。此外，這也可能讓型別推斷變得複雜。

**建議**：考慮使用 `Object.assign` 或明確列出所有 token，以增加可讀性和安全性。

**判斷依據**：diff 中 `packages/features/di/tokens.ts` 第 39 行使用 spread 運算子合併 token 物件。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7874 (cache hit 7808) ｜ completion tokens 1686 ｜ PR #13</sub>