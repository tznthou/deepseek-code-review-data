<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一為集中式 helper（web/test/i18n-mock.ts），並更新全域 mock 與文件。整體方向正確，可減少重複並提高一致性。主要風險在於全域 mock 行為變更（回傳 key 時加上 namespace 前綴）可能影響未更新的測試，以及 helper 中 Trans mock 的 children 處理可能與實際 react-i18next 行為不符。建議確認所有依賴舊行為的測試已更新，並補齊 helper 的單元測試。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:61` | Trans mock 的 children 處理可能與實際 react-i18next 行為不符 | 0.80 |
| ⚠️ | Major | `web/vitest.setup.ts:94` | 全域 mock 行為變更可能導致未更新的測試失敗 | 0.75 |
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | TranslationMap 型別可能過於寬鬆 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:26` | createTFunction 未處理 returnObjects 選項 | 0.65 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 動態 import helper 可能導致 mock 延遲 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:61</code> Trans mock 的 children 處理可能與實際 react-i18next 行為不符</summary>

在 `createTransMock` 中，當 `children` 存在時，回傳 `children` 而非翻譯文字。實際 react-i18next 的 `Trans` 元件會將翻譯文字與 children 結合（例如將 children 插入翻譯字串中的 `<0>` 等標記）。此 mock 可能導致依賴 `Trans` 渲染翻譯文字的測試無法正確驗證。建議參考實際 `Trans` 行為，或至少提供可配置的渲染方式。

**判斷依據**：diff 中新增的 `createTransMock` 函式，第 60 行。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:94</code> 全域 mock 行為變更可能導致未更新的測試失敗</summary>

全域 mock 原本在無 namespace 時回傳 key 本身，現在改為使用 `createReactI18nextMock()`，其 `createTFunction` 在無 namespace 時回傳 `fullKey`（即 key 本身），但當有 namespace 時會加上前綴。這與原本行為一致，但需確認所有依賴舊行為的測試已更新。此外，原本全域 mock 有處理 `returnObjects` 選項，新 helper 未處理，可能導致使用該選項的測試失敗。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的修改，移除了原本的 `useTranslation` 實作，改用 helper。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> TranslationMap 型別可能過於寬鬆</summary>

`interface TranslationMap extends Record<string, string | string[]> {}` 允許值為 string 或 string[]，但 `createTFunction` 回傳型別為 string，若值為 string[] 會導致型別不符。建議明確限制為 string，或處理陣列情況。

**判斷依據**：diff 中新增的 `TranslationMap` 介面。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:26</code> createTFunction 未處理 returnObjects 選項</summary>

原本全域 mock 有處理 `options.returnObjects`，回傳陣列。新 helper 未處理此選項，可能導致使用該功能的測試失敗。建議加入對 `returnObjects` 的支援。

**判斷依據**：diff 中 `createTFunction` 的實作，未見 `returnObjects` 處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 動態 import helper 可能導致 mock 延遲</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 動態載入 helper，可能因非同步載入而影響測試執行時序。建議改為靜態 import（在檔案頂部），或確認此模式在專案中已廣泛使用。

**判斷依據**：diff 中 `install.spec.tsx` 的修改。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12990 (cache hit 12928) ｜ completion tokens 1171 ｜ PR #7</sub>