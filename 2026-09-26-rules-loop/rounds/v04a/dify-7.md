<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 抽換為集中式 helper（web/test/i18n-mock.ts），並更新全域 mock 與文件。整體方向正確，能減少重複並統一 mock 行為。主要風險在於全域 mock 行為變更（t 函式現在會加上 namespace 前綴）可能影響未修改的測試，且新 helper 的型別與實作有潛在問題（如 TranslationMap 介面、Trans mock 未處理 components、createTFunction 的參數序列化順序）。建議修正後合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:4` | TranslationMap 介面定義錯誤，可能導致型別不符 | 0.80 |
| ⚠️ | Major | `web/test/i18n-mock.ts:26` | createTFunction 的參數序列化順序可能與既有 mock 不一致 | 0.75 |
| ⚠️ | Major | `web/test/i18n-mock.ts:61` | Trans mock 未處理 components prop，可能導致測試失敗 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 混合使用全域 mock 與自訂 Trans，可能造成不一致 | 0.60 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:33` | i18next-config mock 的 getFixedT 實作可能與全域 mock 不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:4</code> TranslationMap 介面定義錯誤，可能導致型別不符</summary>

`interface TranslationMap extends Record<string, string | string[]> {}` 使用了 `interface` 而非 `type`，違反專案規範 R10（TypeScript Must Use Type Definitions Instead of Interfaces）。此外，`Record<string, string | string[]>` 允許陣列值，但 `createTFunction` 的回傳型別為 `string`，若翻譯值為陣列，回傳型別會不符。建議改為 `type TranslationMap = Record<string, string>`，除非有明確需要陣列值的情境。

**判斷依據**：diff 中新增的 `web/test/i18n-mock.ts` 第 4 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:26</code> createTFunction 的參數序列化順序可能與既有 mock 不一致</summary>

在 `createTFunction` 中，當沒有自訂翻譯時，會將 `options` 中除了 `ns` 以外的參數序列化並附加到回傳字串。但原本全域 mock 的實作是：若 `options` 存在且包含 `returnObjects`，會回傳陣列；否則若 `options` 或 `ns` 存在，才進行序列化。新的實作忽略了 `returnObjects` 的處理，且序列化條件不同，可能導致依賴舊行為的測試失敗。建議檢查所有使用全域 mock 的測試，確認是否有依賴 `returnObjects` 或特定序列化格式。

**判斷依據**：diff 中 `web/test/i18n-mock.ts` 第 11 行附近，以及 `web/vitest.setup.ts` 中被移除的舊實作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:61</code> Trans mock 未處理 components prop，可能導致測試失敗</summary>

`createTransMock` 回傳的 `Trans` 元件只渲染 `children` 或翻譯文字，完全忽略 `components` prop。原本在 `install.spec.tsx` 中的自訂 Trans mock 有處理 `components?.trustSource`，但新的全域 mock 沒有。若元件使用 `<Trans components={{...}} />`，測試可能無法正確驗證。建議在 `createTransMock` 中加入對 `components` 的支援，或提供選項讓使用者自訂。

**判斷依據**：diff 中 `web/test/i18n-mock.ts` 第 52 行，以及 `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx` 中保留的自訂 Trans mock。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 混合使用全域 mock 與自訂 Trans，可能造成不一致</summary>

此測試檔案使用 `createReactI18nextMock()` 取得 `useTranslation`，但另外覆寫了 `Trans`。這可能導致 `useTranslation` 與 `Trans` 的行為不一致（例如 `useTranslation` 回傳的 `t` 會加上 namespace 前綴，但 `Trans` 不會）。建議確認此處是否需要完全自訂，或改用 helper 提供的選項。

**判斷依據**：diff 中 `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx` 第 67-72 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:33</code> i18next-config mock 的 getFixedT 實作可能與全域 mock 不一致</summary>

此處將 `getFixedT` 改為回傳帶 namespace 前綴的 key，但全域 mock 的 `useTranslation` 也會加上 namespace 前綴。若 `useMixedTranslation` 內部使用 `getFixedT`，可能導致雙重前綴。建議確認 `useMixedTranslation` 的實作，確保不會重複加上 namespace。

**判斷依據**：diff 中 `web/app/components/plugins/marketplace/index.spec.tsx` 第 31-38 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11541 (cache hit 10240) ｜ completion tokens 1530 ｜ PR #7</sub>