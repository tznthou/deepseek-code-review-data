<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 統一為集中式 helper（`web/test/i18n-mock.ts`），並更新全域 mock 與文件。整體方向正確，可減少重複並提升一致性。主要風險在於全域 mock 行為變更（回傳值從 key 改為 ns.key）可能影響未更新測試的斷言，以及 helper 中 `createTFunction` 的參數序列化邏輯與既有測試預期不完全一致。建議先確認所有依賴全域 mock 的測試已同步更新，並補齊 helper 的單元測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:24` | createTFunction 的參數序列化與既有測試預期不一致 | 0.80 |
| ⚠️ | Major | `web/vitest.setup.ts:94` | 全域 mock 行為變更可能影響未更新的測試 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 動態匯入 helper 可能導致 mock 延遲 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:10` | helper 檔案缺少單元測試 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:24</code> createTFunction 的參數序列化與既有測試預期不一致</summary>

`createTFunction` 在沒有自訂翻譯時，會將 `options` 中除了 `ns` 以外的參數序列化並附加到回傳字串（例如 `key:{"count":5}`）。但原本全域 mock 的實作只有在 `options` 存在且包含其他參數時才序列化，且序列化時會先移除 `ns`。此處的實作在 `options` 為 `undefined` 時也會建立空物件並刪除 `ns`，但 `Object.keys(params).length` 仍為 0，因此行為相同。然而，若 `options` 包含 `returnObjects: true`，原本全域 mock 會回傳陣列，但新 helper 會回傳字串（因為 `returnObjects` 會被序列化）。這可能導致依賴 `returnObjects` 的測試失敗。建議在 `createTFunction` 中明確處理 `returnObjects`，或保留原本全域 mock 的邏輯。

**判斷依據**：diff 中新增的 `createTFunction` 函式，與 `web/vitest.setup.ts` 中被刪除的舊全域 mock 邏輯相比，缺少對 `returnObjects` 的處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:94</code> 全域 mock 行為變更可能影響未更新的測試</summary>

全域 mock 原本在沒有 `options` 或 `ns` 時回傳 `key`，現在改為使用 `createReactI18nextMock()`，其 `createTFunction` 在沒有自訂翻譯時會回傳 `fullKey`（即 `ns.key` 或 `key`）。但若測試中呼叫 `t('some.key')` 且沒有指定 `ns`，原本會回傳 `'some.key'`，現在仍會回傳 `'some.key'`（因為 `defaultNs` 為 undefined）。然而，若測試中呼叫 `t('some.key', { ns: 'plugin' })`，原本會回傳 `'plugin.some.key'`，現在也會回傳 `'plugin.some.key'`，因此行為一致。但若測試中依賴 `returnObjects` 行為，則會失敗。建議搜尋所有使用 `returnObjects` 的測試並確認是否受影響。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的變更，將原本的 mock 替換為 `createReactI18nextMock()`，而該 helper 的 `createTFunction` 未處理 `returnObjects`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 動態匯入 helper 可能導致 mock 延遲</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 是可行的，但若該模組有副作用或依賴其他 mock，可能造成初始化順序問題。建議確認 `@/test/i18n-mock` 沒有依賴其他需要 mock 的模組，或考慮直接靜態匯入。

**判斷依據**：diff 中 `install.spec.tsx` 的變更，在 `vi.mock` 工廠內動態匯入 helper。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:10</code> helper 檔案缺少單元測試</summary>

新增的 `web/test/i18n-mock.ts` 包含多個函式，但沒有對應的測試。建議為 `createTFunction`、`createUseTranslationMock`、`createTransMock` 和 `createReactI18nextMock` 撰寫單元測試，以確保其行為符合預期，特別是參數序列化和 `returnObjects` 的處理。

**判斷依據**：diff 中新增的檔案沒有包含測試。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12980 (cache hit 10240) ｜ completion tokens 1332 ｜ PR #7</sub>