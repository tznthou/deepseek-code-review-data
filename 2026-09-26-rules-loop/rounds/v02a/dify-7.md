<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一抽換為集中式 helper（web/test/i18n-mock.ts），並更新全域 mock 與文件。整體方向正確，能減少重複並提升可維護性。主要風險在於全域 mock 行為改變（回傳值從 key 改為 ns.key），可能影響未更新測試的斷言；此外，helper 中 Trans mock 的 children 處理可能與實際元件行為不一致，且部分測試檔案移除 mock 後未確認是否依賴全域 mock 的完整功能。建議確認所有受影響測試通過，並補齊 helper 的型別與測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:61` | Trans mock 的 children 處理可能導致測試誤判 | 0.80 |
| ⚠️ | Major | `web/vitest.setup.ts:94` | 全域 mock 行為變更可能破壞未更新的測試 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | 移除 react-i18next mock 後可能依賴全域 mock 的未預期行為 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | TranslationMap 介面可能過於寬鬆 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:61</code> Trans mock 的 children 處理可能導致測試誤判</summary>

在 `createTransMock` 中，當 `children` 存在時，回傳的內容是 `children` 而非翻譯文字。這與實際 react-i18next 的 `Trans` 元件行為不同：實際元件會將翻譯文字與 children 結合（例如將 children 插入翻譯字串中的佔位符）。若測試依賴 `Trans` 渲染翻譯文字，此 mock 會導致測試無法正確驗證。建議改為將翻譯文字與 children 一起渲染，或提供更貼近實際行為的實作。

**判斷依據**：diff 中新增的 `createTransMock` 函式，當 `children` 存在時直接回傳 `children`，忽略翻譯文字。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:94</code> 全域 mock 行為變更可能破壞未更新的測試</summary>

原本全域 mock 的 `t` 函式在沒有 options 時回傳 key，有 options 時回傳 `ns.key`。新的 `createReactI18nextMock` 使用 `createTFunction`，其邏輯為：先檢查自訂翻譯，若無則回傳 `fullKey`（即 `ns.key` 或 `key`）。但當 `options` 存在但沒有 `ns` 且沒有 `defaultNs` 時，`fullKey` 為 `key`，與原本行為一致；然而，原本全域 mock 在 `options` 存在但沒有 `ns` 時，會回傳 `key`（因為 `ns` 為 undefined，prefix 為空），但新邏輯在 `options` 存在且沒有 `ns` 時，`fullKey` 為 `key`，但會加上 params 序列化（若 params 存在）。這可能影響依賴原本行為的測試。此外，原本全域 mock 有處理 `returnObjects` 選項，但新 helper 沒有，可能導致使用 `returnObjects` 的測試失敗。建議確認所有使用全域 mock 的測試是否涵蓋這些情境，並考慮在 helper 中保留 `returnObjects` 支援。

**判斷依據**：diff 中 `web/vitest.setup.ts` 將原本的 mock 替換為 `createReactI18nextMock()`，但新 helper 未處理 `returnObjects` 選項，且 params 序列化邏輯可能不同。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> 移除 react-i18next mock 後可能依賴全域 mock 的未預期行為</summary>

此測試檔案移除了原本的 `vi.mock('react-i18next', ...)`，改為依賴全域 mock。但全域 mock 現在使用 `createReactI18nextMock`，其 `t` 函式會回傳 `ns.key` 格式。測試中已更新部分斷言以符合新行為，但需確認所有使用 `t` 的地方都已更新，且沒有其他依賴原本 mock 行為的測試。

**判斷依據**：diff 中移除了 `vi.mock('react-i18next', ...)`，但未新增替代 mock，依賴全域 mock。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> TranslationMap 介面可能過於寬鬆</summary>

`interface TranslationMap extends Record<string, string | string[]> {}` 允許值為 string 或 string[]，但 `createTFunction` 的回傳型別為 string（因為回傳 `translations[fullKey]` 可能是 string[]，但函式回傳型別未明確，可能導致型別不一致）。建議明確回傳型別，並考慮是否真的需要支援陣列值。

**判斷依據**：diff 中新增的介面定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12980 (cache hit 1536) ｜ completion tokens 1272 ｜ PR #7</sub>