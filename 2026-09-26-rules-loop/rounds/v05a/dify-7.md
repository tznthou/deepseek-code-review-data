<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一抽換為集中式 helper（web/test/i18n-mock.ts），並更新全域 mock 與文件。整體方向正確，可減少重複並提升一致性。主要風險在於全域 mock 行為變更（回傳值加上 namespace 前綴）可能影響未修改的測試，以及 helper 的型別定義與實際使用情境的相容性。建議先確認所有依賴舊行為的測試已同步更新，並修正 helper 的型別問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:4` | [R10] 使用 interface 而非 type 定義 TranslationMap | 0.80 |
| ⚠️ | Major | `web/test/i18n-mock.ts:11` | createTFunction 的 options 型別可能與實際呼叫不符 | 0.75 |
| ⚠️ | Major | `web/vitest.setup.ts:94` | 全域 mock 行為變更可能影響未修改的測試 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:26` | createTFunction 未處理 returnObjects 選項 | 0.60 |
| 🔸 | Minor | `web/test/i18n-mock.ts:22` | createUseTranslationMock 未提供 i18n 物件的完整屬性 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:4</code> [R10] 使用 interface 而非 type 定義 TranslationMap</summary>

此檔案新增了 `interface TranslationMap extends Record<string, string | string[]> {}`，違反專案規範 R10（TypeScript 必須使用 type 而非 interface）。建議改為 `type TranslationMap = Record<string, string | string[]>`。

**判斷依據**：diff 新增行：`+interface TranslationMap extends Record<string, string | string[]> {}`

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:11</code> createTFunction 的 options 型別可能與實際呼叫不符</summary>

`createTFunction` 回傳的函式參數 `options` 型別為 `Record<string, unknown>`，但實際使用時可能傳入 `{ ns?: string, returnObjects?: boolean, [key: string]: unknown }` 等更複雜的型別。若呼叫端傳入 `returnObjects`，目前實作會將其視為一般參數並序列化，可能導致非預期結果。建議明確型別並處理 `returnObjects` 等特殊選項。

**判斷依據**：diff 新增行：`+  return (key: string, options?: Record<string, unknown>) => {`

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:94</code> 全域 mock 行為變更可能影響未修改的測試</summary>

全域 mock 從原本的 `useTranslation` 改為使用 `createReactI18nextMock()`，其回傳的 `t` 函式現在會加上 namespace 前綴（例如 `plugin.category.all`）。這可能導致其他未在此 PR 中修改、但依賴舊行為（回傳原始 key）的測試失敗。建議全面搜尋並更新受影響的測試，或提供相容模式。

**判斷依據**：diff 修改行：`+    ...createReactI18nextMock(),`

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:26</code> createTFunction 未處理 returnObjects 選項</summary>

原本全域 mock 有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 未實作此邏輯，若測試依賴此功能將失敗。建議加入 `returnObjects` 的處理。

**判斷依據**：diff 新增行：`+    const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:22</code> createUseTranslationMock 未提供 i18n 物件的完整屬性</summary>

`createUseTranslationMock` 回傳的 `i18n` 物件僅包含 `language` 和 `changeLanguage`，但實際元件可能使用其他屬性（如 `exists`、`t` 等）。若測試中用到這些屬性，可能導致錯誤。建議補齊常用屬性。

**判斷依據**：diff 新增行：`+      i18n: {
+        language: 'en',
+        changeLanguage: vi.fn(),
+      },`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12900 (cache hit 10240) ｜ completion tokens 1165 ｜ PR #7</sub>