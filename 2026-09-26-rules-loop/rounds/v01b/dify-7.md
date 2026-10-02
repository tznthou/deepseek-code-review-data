<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 統一為集中式 helper（`web/test/i18n-mock.ts`），並更新全域 mock 與文件。整體方向合理，可減少重複並提升一致性。主要風險在於全域 mock 行為變更（回傳 key 時加上 namespace 前綴）可能影響未修改的測試，以及 helper 中 `TranslationMap` 型別與 `createTFunction` 的實作細節。建議確認所有依賴舊行為的測試已同步更新，並補齊 helper 的單元測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | [R10] 使用 interface 而非 type 定義 TranslationMap | 0.80 |
| 🔸 | Minor | `web/test/i18n-mock.ts:10` | createTFunction 的 fallback 行為可能與全域 mock 不一致 | 0.70 |
| 🔸 | Minor | `web/vitest.setup.ts:89` | 全域 mock 行為變更可能影響未修改的測試 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 動態 import helper 可能導致 vi.mock 工廠非同步問題 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> [R10] 使用 interface 而非 type 定義 TranslationMap</summary>

專案規範 R10 要求 TypeScript 型別宣告使用 `type` 而非 `interface`。此處使用 `interface TranslationMap extends Record<string, string | string[]> {}`，違反該規範。建議改為 `type TranslationMap = Record<string, string | string[]>`。

**判斷依據**：diff 新增檔案 web/test/i18n-mock.ts 第 4 行使用 interface 宣告。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 的 fallback 行為可能與全域 mock 不一致</summary>

全域 mock 原本在 `options.returnObjects` 存在時回傳陣列，但新的 `createTFunction` 未處理 `returnObjects` 選項。若測試依賴此行為，可能導致失敗。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，或明確文件說明不支援。

**判斷依據**：diff 中新增的 createTFunction 未處理 returnObjects，而舊全域 mock 有處理（見 web/vitest.setup.ts 刪除的程式碼）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/vitest.setup.ts:89</code> 全域 mock 行為變更可能影響未修改的測試</summary>

全域 mock 從原本的 `useTranslation` 改為使用 `createReactI18nextMock()`，其回傳的 `t` 函式在沒有自訂翻譯時會回傳 `ns.key`（若提供 ns）而非原本的 `key`。這可能導致其他未修改的測試期望值改變。建議搜尋所有依賴舊行為的測試並更新，或考慮保留舊行為作為預設。

**判斷依據**：diff 中 web/vitest.setup.ts 的變更，刪除了原本的 useTranslation mock，改用 createReactI18nextMock。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 動態 import helper 可能導致 vi.mock 工廠非同步問題</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 是允許的，但需確保該模組在測試環境中可被正確解析。若路徑別名設定有誤，可能導致測試失敗。建議確認 `@/test/i18n-mock` 的解析正常，或考慮直接靜態 import。

**判斷依據**：diff 中 install.spec.tsx 的 vi.mock 工廠使用動態 import。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12980 (cache hit 12928) ｜ completion tokens 1384 ｜ PR #7</sub>