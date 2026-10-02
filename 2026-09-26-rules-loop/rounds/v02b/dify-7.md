<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 邏輯統一至 `web/test/i18n-mock.ts` 的輔助函式，並更新全域 mock 以使用這些輔助函式。整體方向正確，能減少重複並提升可維護性。主要風險在於全域 mock 行為的變更（回傳值從 key 改為帶 namespace 前綴）可能影響未更新的測試，以及 `createTFunction` 中對 `returnObjects` 選項的處理與先前全域 mock 不一致，可能導致依賴該功能的測試失敗。建議確認所有受影響的測試已更新，並補齊 `returnObjects` 的支援。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | createTFunction 未處理 returnObjects 選項，可能導致依賴該功能的測試失敗 | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | i18next-config mock 的 getFixedT 實作與全域 mock 不一致，可能導致測試預期錯誤 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | TranslationMap 介面使用空介面延伸 Record，可能觸發 ESLint 規則 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 未處理 returnObjects 選項，可能導致依賴該功能的測試失敗</summary>

在 `createTFunction` 中，當 `options.returnObjects` 為 true 時，應回傳陣列（例如 `['key-feature-1', 'key-feature-2']`），但目前的實作會忽略此選項，直接回傳字串。這與先前 `web/vitest.setup.ts` 中的全域 mock 行為不一致，可能導致使用 `returnObjects` 的測試（例如某些元件測試）失敗。

建議在 `createTFunction` 中增加對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects)
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
```

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊全域 mock 有處理 `returnObjects`：`if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createTFunction` 沒有此邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> i18next-config mock 的 getFixedT 實作與全域 mock 不一致，可能導致測試預期錯誤</summary>

在 `web/app/components/plugins/marketplace/index.spec.tsx` 中，`i18next-config` 的 mock 被改為回傳帶 namespace 前綴的字串（`${options.ns}.${key}`），但全域 mock 的 `createTFunction` 在沒有自訂翻譯時也是回傳帶 namespace 前綴的字串。兩者行為一致，但此 mock 的實作較為簡單，未處理 `returnObjects` 或參數序列化。若未來有測試依賴這些功能，可能需要更新。目前影響不大，但建議考慮直接使用 `createTFunction` 來保持一致性。

**判斷依據**：diff 中此 mock 的 `getFixedT` 實作僅處理 namespace 前綴，未處理 `returnObjects` 或參數序列化，與 `createTFunction` 的完整邏輯不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> TranslationMap 介面使用空介面延伸 Record，可能觸發 ESLint 規則</summary>

`interface TranslationMap extends Record<string, string | string[]> {}` 使用空介面延伸 Record，可能違反 `@typescript-eslint/no-empty-interface` 規則（若專案有啟用）。建議改用型別別名：`type TranslationMap = Record<string, string | string[]>`。

**判斷依據**：diff 中新增的 `web/test/i18n-mock.ts` 第 4 行定義了空介面。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12980 (cache hit 12928) ｜ completion tokens 1282 ｜ PR #7</sub>