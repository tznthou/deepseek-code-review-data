<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為依賴注入（DI）模式，新增對應的 DI 模組與容器，並更新相關引用。整體方向合理，但存在兩個主要風險：FeaturesRepository 模組的 token 設定錯誤，可能導致 DI 解析失敗；以及 DI 容器在每次呼叫時重新建立，可能造成資源浪費與狀態不一致。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 設定錯誤，導致 DI 解析失敗 | 0.95 |
| ⚠️ | Major | `packages/features/di/containers/FeatureOptInService.ts:6` | 每次呼叫都建立新的 DI 容器，可能造成資源浪費與狀態不一致 | 0.80 |
| ⚠️ | Major | `packages/features/di/containers/FeaturesRepository.ts:4` | 每次呼叫都建立新的 DI 容器，可能造成資源浪費與狀態不一致 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 設定錯誤，導致 DI 解析失敗</summary>

在 `moduleLoader` 物件中，`token` 屬性被設定為 `moduleToken`，但其他模組（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token（例如 `FEATURE_OPT_IN_DI_TOKENS.FEATURE_OPT_IN_SERVICE`）。這會導致當其他模組依賴 `featuresRepositoryModuleLoader` 時，使用 `featuresRepositoryModuleLoader.token` 取得的 token 是模組 token 而非服務 token，造成 DI 容器無法正確解析 `FeaturesRepository` 實例。

**失敗情境**：任何使用 `featuresRepositoryModuleLoader` 作為依賴的模組（例如 `FeatureOptInService`）在載入時，會嘗試以 `FEATURES_REPOSITORY_MODULE` token 取得 `FeaturesRepository`，但該 token 並未綁定到類別，導致解析失敗並拋出錯誤。

**建議修法**：將 `moduleLoader` 的 `token` 屬性改為 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），與其他模組保持一致。

**判斷依據**：diff 中新增的 `packages/features/di/modules/FeaturesRepository.ts` 第 21 行明確設定 `token: moduleToken`，而對照 `packages/features/di/modules/FeatureOptInService.ts` 第 21 行設定 `token` 為服務 token。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeatureOptInService.ts:6</code> 每次呼叫都建立新的 DI 容器，可能造成資源浪費與狀態不一致</summary>

`getFeatureOptInService()` 每次呼叫都會執行 `createContainer()` 並載入模組，這會建立全新的容器與服務實例。若服務內部有狀態（例如快取）或依賴的資源（如資料庫連線）需要共享，這種做法會導致狀態無法共享，且頻繁建立容器可能影響效能。

**失敗情境**：在多個請求同時呼叫 `getFeatureOptInService()` 時，每個請求都會建立獨立的服務實例，若服務內部有跨請求的狀態（如記憶體快取），將無法共享，可能導致資料不一致或效能下降。

**建議修法**：考慮使用單例模式，在模組載入時建立一次容器並重用，或使用應用程式層級的 DI 容器來管理生命週期。

**判斷依據**：diff 中新增的 `packages/features/di/containers/FeatureOptInService.ts` 第 6-8 行顯示每次呼叫都會建立新容器。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/containers/FeaturesRepository.ts:4</code> 每次呼叫都建立新的 DI 容器，可能造成資源浪費與狀態不一致</summary>

`getFeaturesRepository()` 每次呼叫都會執行 `createContainer()` 並載入模組，這會建立全新的容器與 `FeaturesRepository` 實例。若 `FeaturesRepository` 內部有狀態或依賴的資源（如 Prisma client）需要共享，這種做法會導致資源重複建立，且可能造成連線池耗盡。

**失敗情境**：在高併發情境下，每個請求都建立新的 `FeaturesRepository` 與 Prisma client，可能導致資料庫連線數過多，影響效能或觸發連線上限。

**建議修法**：考慮使用單例模式，在模組載入時建立一次容器並重用，或使用應用程式層級的 DI 容器來管理生命週期。

**判斷依據**：diff 中新增的 `packages/features/di/containers/FeaturesRepository.ts` 第 5-7 行顯示每次呼叫都會建立新容器。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6389 (cache hit 6272) ｜ completion tokens 1297 ｜ PR #13</sub>