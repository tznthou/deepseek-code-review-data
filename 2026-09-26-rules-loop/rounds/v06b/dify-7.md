<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一至新的輔助函式 `createReactI18nextMock`，並更新全域 mock 以使用該函式。整體方向正確，可減少重複並提升可維護性。主要風險在於全域 mock 行為的變更（回傳值從 key 改為 ns.key）可能影響未更新的測試，且 `createTFunction` 對 `returnObjects` 選項的處理與舊全域 mock 不一致，可能導致依賴該功能的測試失敗。建議先確認所有相關測試已更新，並補齊 `returnObjects` 的支援。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | createTFunction 未處理 returnObjects 選項，可能導致依賴該功能的測試失敗 | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 自訂 Trans mock 可能與 createReactI18nextMock 的 Trans 衝突 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | i18next-config mock 的 getFixedT 行為變更可能影響其他測試 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 未處理 returnObjects 選項，可能導致依賴該功能的測試失敗</summary>

舊的全域 mock 在 `useTranslation` 中對 `options?.returnObjects` 有特殊處理，會回傳陣列 `[`${key}-feature-1`, `${key}-feature-2`]`。新的 `createTFunction` 完全忽略此選項，僅將 `returnObjects` 視為一般參數並序列化到回傳字串中。這會導致任何依賴 `returnObjects` 的測試（例如預期取得陣列）失敗。

建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects) {
  return [`${key}-feature-1`, `${key}-feature-2`]
}
```
並確保此行為與舊全域 mock 一致。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊全域 mock 包含 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createTFunction` 中沒有對應邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 自訂 Trans mock 可能與 createReactI18nextMock 的 Trans 衝突</summary>

此處使用 `createReactI18nextMock()` 取得預設的 `useTranslation` 和 `Trans`，但隨後又覆寫了 `Trans` 以加入 `data-testid="trans"` 和自訂渲染邏輯。這會導致 `createReactI18nextMock` 提供的 `Trans` 被完全取代，可能遺失其原本的行為（例如處理 `children` 或 `data-i18n-key`）。若此測試需要自訂 `Trans`，建議直接使用 `createUseTranslationMock` 並自行定義 `Trans`，或擴充 `createReactI18nextMock` 以支援自訂 `Trans` 選項。

**判斷依據**：diff 中此檔案新增了 `...createReactI18nextMock()` 並覆寫 `Trans`，但 `createReactI18nextMock` 本身已包含 `Trans` 的實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> i18next-config mock 的 getFixedT 行為變更可能影響其他測試</summary>

此處將 `getFixedT` 的 mock 從回傳 key 改為回傳 `ns.key`（若有 ns），以配合新的全域 mock 行為。但此 mock 僅在此測試檔案中生效，若其他測試檔案也 mock 了 `@/i18n-config/i18next-config` 並依賴舊行為，可能導致不一致。建議確認所有相關測試均已更新，或考慮將此 mock 也集中至輔助函式。

**判斷依據**：diff 中此檔案的 `getFixedT` mock 從 `(key: string) => key` 改為有條件地加上 namespace 前綴。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12970 (cache hit 12928) ｜ completion tokens 1479 ｜ PR #7</sub>