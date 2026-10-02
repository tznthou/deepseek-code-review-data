<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 抽換為集中式 helper（web/test/i18n-mock.ts），並更新全域 mock 與文件。主要風險在於全域 mock 行為改變（t 函式現在會加上 namespace 前綴），可能導致未同步更新的測試失敗；此外，helper 中的型別定義與既有規範（R10）不符，且部分測試檔移除了自訂 mock 後可能依賴全域 mock 的未驗證行為。建議先確認所有受影響測試通過，並修正型別定義。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/vitest.setup.ts:94` | 全域 mock 行為變更可能導致未更新測試失敗 | 0.75 |
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | [R10] 使用 interface 而非 type 定義 TranslationMap | 0.90 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 動態 import helper 可能造成非同步 mock 問題 | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:33` | i18next-config mock 行為變更可能影響其他測試 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:94</code> 全域 mock 行為變更可能導致未更新測試失敗</summary>

全域 mock 的 `useTranslation` 改為使用 `createReactI18nextMock()`，其 `t` 函式現在會回傳 `ns.key` 格式（若提供 ns 或 defaultNs）。先前實作在無 options 時回傳原始 key，有 options 時才加前綴。此變更可能影響未同步更新的測試，例如預期回傳原始 key 的斷言。建議全面執行測試並修正所有受影響的斷言。

**判斷依據**：diff 中 web/vitest.setup.ts 第 91 行，取代了原本的 useTranslation 實作。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> [R10] 使用 interface 而非 type 定義 TranslationMap</summary>

專案規範 R10 要求 TypeScript 使用 type 定義而非 interface。此處 `interface TranslationMap extends Record<string, string | string[]> {}` 違反該規範，應改為 `type TranslationMap = Record<string, string | string[]>`。

**判斷依據**：diff 新增檔案 web/test/i18n-mock.ts 第 4 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 動態 import helper 可能造成非同步 mock 問題</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 動態載入 helper。雖然 Vitest 支援非同步工廠，但此模式可能導致 mock 初始化延遲或循環依賴。建議改為頂層靜態 import，或確認此模式在專案中已廣泛使用且無副作用。

**判斷依據**：diff 中 install.spec.tsx 第 67 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:33</code> i18next-config mock 行為變更可能影響其他測試</summary>

此處修改了 `getFixedT` 的 mock 實作，使其在提供 ns 時回傳 `ns.key`。這可能影響依賴此 mock 的其他測試（例如 useMixedTranslation 的測試），需確認所有相關測試已同步更新。

**判斷依據**：diff 中 marketplace/index.spec.tsx 第 30-37 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11541 (cache hit 11520) ｜ completion tokens 1000 ｜ PR #7</sub>