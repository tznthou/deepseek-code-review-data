<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 統一抽換為 `@/test/i18n-mock` 的輔助函式，並更新全域 mock 以使用相同邏輯。整體方向正確，可減少重複並提升一致性。主要風險在於全域 mock 的行為變更（回傳值從 key 改為 ns.key）可能影響未修改的測試，以及 `createTFunction` 對 `returnObjects` 選項的處理與舊行為不同，可能導致依賴該功能的測試失敗。建議合併前確認所有相關測試通過，並補上 `returnObjects` 的處理。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | createTFunction 未處理 returnObjects 選項，可能破壞依賴該功能的測試 | 0.80 |
| ⚠️ | Major | `web/vitest.setup.ts:89` | 全域 mock 行為變更：回傳值從 key 改為 ns.key，可能影響未修改的測試 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 動態匯入 createReactI18nextMock 可能導致 mock 工廠非同步問題 | 0.60 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | i18next-config mock 的 getFixedT 行為變更可能影響其他測試 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 未處理 returnObjects 選項，可能破壞依賴該功能的測試</summary>

舊的全域 mock 在 `options?.returnObjects` 為真時會回傳陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`），但新的 `createTFunction` 完全忽略此選項，一律回傳字串。若任何測試或元件依賴 `t(key, { returnObjects: true })` 取得陣列，將導致測試失敗或元件行為異常。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，或確認沒有測試使用此功能。

**判斷依據**：diff 中舊的全域 mock 有 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createTFunction` 沒有對應邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:89</code> 全域 mock 行為變更：回傳值從 key 改為 ns.key，可能影響未修改的測試</summary>

舊的全域 mock 在沒有 namespace 時回傳 key，有 namespace 時回傳 `ns.key`。新的 `createReactI18nextMock()` 使用 `createTFunction`，其邏輯是：先查 `translations[fullKey]`，再查 `translations[key]`，最後回傳 `fullKey`（即 `ns.key` 或 key）。但若 `defaultNs` 未提供且 `options.ns` 未提供，`fullKey` 等於 key，行為相同；然而若元件呼叫 `useTranslation('someNs')` 並傳入 defaultNs，舊 mock 會回傳 `someNs.key`，新 mock 也會回傳 `someNs.key`，看似一致。但舊 mock 在 `options` 存在但 `ns` 未提供時，會回傳 key（因為 `ns` 為 undefined，prefix 為空），而新 mock 在 `options` 存在但 `ns` 未提供時，`fullKey` 仍為 key，行為相同。真正的差異在於舊 mock 對 `returnObjects` 的處理（見另一 finding）。此外，全域 mock 現在也包含 `Trans` 元件，這可能影響原本未 mock `Trans` 的測試，但通常是有益的。建議執行完整測試套件以確認沒有回歸。

**判斷依據**：diff 中舊的全域 mock 有 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createReactI18nextMock` 沒有此邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 動態匯入 createReactI18nextMock 可能導致 mock 工廠非同步問題</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 是允許的，但需確保該模組在測試環境中可被正確解析。若路徑別名 `@` 在 Vitest 中設定正確，則無問題。然而，此處將 `createReactI18nextMock()` 的結果與 `actual` 合併，並覆寫 `Trans`，但 `createReactI18nextMock` 已包含 `Trans`，此覆寫可能導致不一致。建議直接使用 `createReactI18nextMock` 並傳入自訂翻譯，或明確說明為何需要覆寫 `Trans`。

**判斷依據**：diff 中此處使用動態匯入並覆寫 Trans，但 createReactI18nextMock 已提供 Trans，可能造成混淆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> i18next-config mock 的 getFixedT 行為變更可能影響其他測試</summary>

此處將 `getFixedT` 的 mock 從回傳 key 改為回傳 `ns.key`（當 options.ns 存在時）。這與全域 mock 的行為一致，但若其他測試依賴此 mock 回傳純 key，可能會失敗。建議確認所有使用此 mock 的測試都已更新。

**判斷依據**：diff 中此 mock 的實作從 `(key: string) => key` 改為有條件地加上 namespace。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12289 (cache hit 12288) ｜ completion tokens 1889 ｜ PR #7</sub>