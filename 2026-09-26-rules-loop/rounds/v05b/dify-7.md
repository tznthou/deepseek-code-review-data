<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 邏輯統一至新的輔助函式 `createReactI18nextMock`，並更新全域 mock 以使用該函式。整體方向正確，可減少重複並提升可維護性。主要風險在於全域 mock 行為的變更（回傳鍵值時加上 namespace 前綴）可能影響未修改的測試，且部分測試檔案移除 mock 後可能依賴全域 mock 的特定行為。建議確認所有受影響的測試仍通過，並檢查 `createTFunction` 的參數序列化邏輯與既有測試的相容性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:13` | 全域 mock 行為變更可能導致未修改的測試失敗 | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:73` | 自訂 Trans mock 可能與全域 mock 不一致 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:33` | i18next-config mock 行為變更可能影響其他測試 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | TranslationMap 型別可能過於寬鬆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:13</code> 全域 mock 行為變更可能導致未修改的測試失敗</summary>

全域 mock 原本在沒有 options 或 ns 時回傳原始 key，現在 `createTFunction` 在沒有 ns 時回傳 `fullKey`（即 key 本身），但若 options 存在且包含 ns，則回傳 `ns.key`。這與原本行為一致，但需確認所有依賴全域 mock 的測試是否預期此行為。此外，原本全域 mock 在 `options.returnObjects` 為真時回傳陣列，但新的 `createTFunction` 未處理此情況，可能導致使用 `returnObjects` 的測試失敗。

**判斷依據**：diff 中 `web/vitest.setup.ts` 移除了原本處理 `returnObjects` 的邏輯，改為呼叫 `createReactI18nextMock()`，而 `createTFunction` 未實作 `returnObjects` 分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:73</code> 自訂 Trans mock 可能與全域 mock 不一致</summary>

此測試檔案覆寫了 `Trans` 元件，但未使用 `createTransMock`，而是自行定義。這可能導致與其他使用 `createReactI18nextMock` 的測試行為不一致。建議改用 `createReactI18nextMock` 並傳入自訂翻譯，或至少使用 `createTransMock` 來保持一致性。

**判斷依據**：diff 中此處保留了自訂 Trans 實作，而其他檔案已改用輔助函式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:33</code> i18next-config mock 行為變更可能影響其他測試</summary>

此處修改了 `getFixedT` 的 mock，使其在提供 ns 時回傳 `ns.key`。這與全域 mock 的行為一致，但需確認此 mock 是否僅用於此測試檔案，若其他測試也依賴此 mock，可能受到影響。

**判斷依據**：diff 中此 mock 的實作被修改，且測試斷言也相應更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> TranslationMap 型別可能過於寬鬆</summary>

`TranslationMap` 定義為 `Record<string, string | string[]>`，允許值為陣列，但 `createTFunction` 回傳型別為 `string`，若翻譯值為陣列，回傳值將是陣列而非字串，可能導致型別不符。建議明確翻譯值型別或處理陣列情況。

**判斷依據**：diff 中新增的型別定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12900 (cache hit 12800) ｜ completion tokens 1259 ｜ PR #7</sub>