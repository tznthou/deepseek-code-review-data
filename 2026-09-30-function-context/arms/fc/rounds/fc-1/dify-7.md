<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一抽成 `web/test/i18n-mock.ts` 中的輔助函式，並更新全域 mock 與文件。整體方向正確，能減少重複程式碼。主要風險在於 `createReactI18nextMock` 的 `Trans` 元件實作與全域 mock 的整合可能改變既有測試行為，且部分測試檔案移除 mock 後可能依賴全域 mock 的特定行為，需確認測試覆蓋。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:56` | Trans mock 未處理 components prop，可能導致依賴該 prop 的測試失敗 | 0.80 |
| ⚠️ | Major | `web/vitest.setup.ts:91` | 全域 mock 整合 createReactI18nextMock 後，useTranslation 的 returnObjects 行為遺失 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:33` | i18next-config mock 的 getFixedT 實作與全域 mock 不一致 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 動態匯入 createReactI18nextMock 可能造成非同步 mock 問題 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:56</code> Trans mock 未處理 components prop，可能導致依賴該 prop 的測試失敗</summary>

`createTransMock` 回傳的 `Trans` 元件僅接收 `i18nKey` 和 `children`，但實際 react-i18next 的 `Trans` 元件常使用 `components` prop 來插入自訂元件。若元件使用 `<Trans i18nKey="..." components={{ trustSource: <TrustSource /> }} />`，此 mock 會忽略 `components`，導致渲染結果與實際不符，可能使測試無法正確驗證。建議在 `Trans` mock 中處理 `components` prop，例如將 `components` 中的元件渲染在對應位置。

**判斷依據**：diff 中新增的 `createTransMock` 函式，其 `Trans` 元件參數僅有 `i18nKey` 和 `children`，未包含 `components`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:91</code> 全域 mock 整合 createReactI18nextMock 後，useTranslation 的 returnObjects 行為遺失</summary>

原本全域 mock 的 `useTranslation` 有處理 `options.returnObjects`，當設定為 true 時回傳陣列。新的 `createReactI18nextMock` 中的 `createTFunction` 未處理 `returnObjects`，可能導致依賴此行為的測試失敗。建議在 `createTFunction` 中加入 `returnObjects` 的處理，或保留原本的邏輯。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的修改，原本的 `useTranslation` 有 `if (options?.returnObjects) return [...]`，但新的 `createReactI18nextMock` 未包含此邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:33</code> i18next-config mock 的 getFixedT 實作與全域 mock 不一致</summary>

此測試檔案中 `vi.mock('@/i18n-config/i18next-config', ...)` 的 `getFixedT` 回傳的函式現在會處理 `options.ns`，但全域 mock 的 `useMixedTranslation` 可能依賴此 mock 的行為。若 `useMixedTranslation` 使用 `getFixedT` 並傳入 `ns`，此處的實作會回傳 `ns.key`，但全域 mock 的 `createTFunction` 也會處理 `ns`，可能造成不一致。建議確認 `useMixedTranslation` 的實作，確保兩者行為一致。

**判斷依據**：diff 中 `web/app/components/plugins/marketplace/index.spec.tsx` 的修改，`getFixedT` 的實作被改為處理 `options.ns`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 動態匯入 createReactI18nextMock 可能造成非同步 mock 問題</summary>

在 `vi.mock` 中使用 `await import('@/test/i18n-mock')` 是可行的，但需確保該模組在測試環境中可被正確解析。若路徑別名 `@/` 在 Vitest 設定中未涵蓋 `web/test`，可能導致匯入失敗。建議確認 Vitest 的 alias 設定包含 `@/test`。

**判斷依據**：diff 中 `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx` 的修改，使用動態匯入。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12289 (cache hit 1536) ｜ completion tokens 1351 ｜ PR #7</sub>