<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 FeatureOptInService 與 FeaturesRepository 改為透過 DI 容器取得，並新增對應的 module 與 container。主要風險在於 DI token 的合併方式可能造成 Symbol 重複或型別衝突，以及測試中改用全域容器可能引入跨測試狀態污染。整體方向合理，但需確認 token 唯一性與測試隔離。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/di/modules/FeaturesRepository.ts:19` | moduleLoader.token 設定錯誤，可能導致 DI 解析失敗 | 0.80 |
| ⚠️ | Major | `packages/features/di/tokens.ts:39` | 使用 spread 合併 token 可能造成 Symbol 重複或型別衝突 | 0.75 |
| 🔸 | Minor | `packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82` | 測試改用全域 DI 容器可能造成狀態污染 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/modules/FeaturesRepository.ts:19</code> moduleLoader.token 設定錯誤，可能導致 DI 解析失敗</summary>

在 `FeaturesRepository.ts` 中，`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`，但其他 module（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token（`token`）。這可能導致依賴此 module 的程式碼在解析時取得錯誤的 token，造成 DI 容器無法正確綁定或解析。

建議將 `token` 改為 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），以符合其他 module 的慣例。

**判斷依據**：diff 中新增的 `FeaturesRepository.ts` 第 20 行明確將 `token` 設為 `moduleToken`，而其他 module（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設為 `token`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/features/di/tokens.ts:39</code> 使用 spread 合併 token 可能造成 Symbol 重複或型別衝突</summary>

在 `DI_TOKENS` 物件中，使用 `...FLAGS_DI_TOKENS` 和 `...FEATURE_OPT_IN_DI_TOKENS` 將其他 token 物件展開合併。如果這些物件的 key 與現有 `DI_TOKENS` 的 key 重複，後面的 spread 會覆蓋前面的值，可能導致 token 不一致。此外，`FLAGS_DI_TOKENS` 和 `FEATURE_OPT_IN_DI_TOKENS` 的 key 名稱（`FEATURES_REPOSITORY`、`FEATURE_OPT_IN_SERVICE` 等）與原本的 key 相同，但 Symbol 描述也相同，這可能造成混淆。

建議明確列出需要的 token，或確保合併的物件沒有重複 key，並考慮使用更獨特的 Symbol 描述。

**判斷依據**：diff 中 `packages/features/di/tokens.ts` 第 39 行新增了兩個 spread 運算子，將其他 token 物件合併進 `DI_TOKENS`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.integration-test.ts:82</code> 測試改用全域 DI 容器可能造成狀態污染</summary>

測試中原本直接建立 `FeaturesRepository` 和 `FeatureOptInService`，現在改為使用 `getFeaturesRepository()` 和 `getFeatureOptInService()`，這兩個函式會建立新的容器並載入 module。然而，如果這些容器內部使用了共享的 singleton（例如 Prisma client），可能導致測試之間的狀態互相影響。此外，每個測試都建立新容器可能增加不必要的 overhead。

建議確認容器是否為隔離的，或者考慮在測試中使用 mock 或重置容器狀態。

**判斷依據**：diff 中測試檔案第 82 行將原本的 `new FeaturesRepository(prisma)` 和 `new FeatureOptInService(featuresRepository)` 改為呼叫 `getFeaturesRepository()` 和 `getFeatureOptInService()`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6389 (cache hit 1408) ｜ completion tokens 1036 ｜ PR #13</sub>