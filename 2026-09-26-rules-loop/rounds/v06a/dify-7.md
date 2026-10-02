<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 邏輯統一至 `web/test/i18n-mock.ts` 的輔助函式，並更新全域 mock 以使用這些輔助函式。整體方向正確，可減少重複並提升可維護性。主要風險在於全域 mock 行為變更（回傳值加上 namespace 前綴）可能影響未更新的測試，以及 `createTFunction` 對 `returnObjects` 選項的處理與舊有全域 mock 不一致，可能導致依賴該行為的測試失敗。建議確認所有相關測試已更新，並補上 `returnObjects` 的處理。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | createTFunction 未處理 returnObjects 選項，可能破壞依賴該行為的測試 | 0.80 |
| ⚠️ | Major | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 自訂 Trans mock 可能與全域 mock 衝突，導致測試不穩定 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | i18next-config mock 的 getFixedT 行為變更可能影響其他測試 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 未處理 returnObjects 選項，可能破壞依賴該行為的測試</summary>

舊的全域 mock 在 `web/vitest.setup.ts` 中，當 `options.returnObjects` 為真時，會回傳一個陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`）。新的 `createTFunction` 完全沒有處理 `returnObjects`，而是將所有選項（除了 `ns`）序列化後附加到回傳字串。這會導致任何依賴 `returnObjects` 的測試（例如預期 `t('someKey', { returnObjects: true })` 回傳陣列）失敗。

**失敗情境**：某個元件呼叫 `t('featureList', { returnObjects: true })`，測試預期得到 `['featureList-feature-1', 'featureList-feature-2']`，但新 mock 會回傳 `'featureList:{"returnObjects":true}'`。

**建議**：在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```ts
if (options?.returnObjects)
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
```
並確保其優先於其他邏輯。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊 mock 有 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createTFunction` 沒有此邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 自訂 Trans mock 可能與全域 mock 衝突，導致測試不穩定</summary>

此測試檔案在 `vi.mock('react-i18next', ...)` 中同時使用了 `createReactI18nextMock()` 和自訂的 `Trans` 元件。然而，`createReactI18nextMock` 已經包含一個 `Trans` 元件（由 `createTransMock` 提供）。由於物件展開的順序，自訂的 `Trans` 會覆蓋輔助函式提供的 `Trans`，但這可能不是預期的行為，且可能導致其他測試（如果共用此 mock）受到影響。

**失敗情境**：如果其他測試依賴 `createReactI18nextMock` 的預設 `Trans` 行為（例如渲染 `data-i18n-key` 屬性），但此檔案的自訂 `Trans` 沒有該屬性，則可能導致測試失敗。

**建議**：確認此自訂 `Trans` 是否必要。如果必要，考慮建立一個專門的輔助函式來產生包含自訂 `Trans` 的 mock，而不是在測試中手動覆蓋。

**判斷依據**：diff 中顯示此檔案使用 `createReactI18nextMock()` 並覆蓋 `Trans`，而 `createReactI18nextMock` 本身已包含 `Trans`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> i18next-config mock 的 getFixedT 行為變更可能影響其他測試</summary>

此測試檔案將 `getFixedT` 的 mock 從回傳 key 改為回傳 `ns.key`（當有 `ns` 選項時）。這與全域 mock 的行為一致，但可能影響其他依賴此 mock 的測試（如果有的話）。由於此 mock 是檔案層級的，只影響此檔案，但需確認此檔案中所有相關測試都已更新。

**判斷依據**：diff 中顯示 `getFixedT` 的實作從 `(key: string) => key` 改為有條件地加上 namespace 前綴。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12970 (cache hit 10240) ｜ completion tokens 1635 ｜ PR #7</sub>