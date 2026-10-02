<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 統一抽換為 `@/test/i18n-mock` 的輔助函式，並更新全域 mock 與文件。整體方向正確，能減少重複程式碼。主要風險在於全域 mock 行為改變（回傳 key 時加上 namespace 前綴）可能影響未修改的測試，以及 `createTFunction` 對 `returnObjects` 選項的處理與舊實作不同，可能導致依賴該行為的測試失敗。建議確認所有相關測試通過後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | createTFunction 未處理 returnObjects 選項 | 0.80 |
| ⚠️ | Major | `web/vitest.setup.ts:89` | 全域 mock 行為變更可能影響未修改的測試 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 自訂 Trans mock 可能與 createReactI18nextMock 的 Trans 衝突 | 0.60 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | i18next-config mock 的 getFixedT 行為與全域 mock 不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 未處理 returnObjects 選項</summary>

舊的全域 mock 在 `options.returnObjects` 為真時會回傳陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`），但新的 `createTFunction` 完全沒有處理這個選項，而是將 `returnObjects` 視為一般參數，導致回傳字串（例如 `key:{"returnObjects":true}`）。這可能造成依賴此行為的測試失敗。

建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects) {
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
}
```

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊實作有 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新檔案 `web/test/i18n-mock.ts` 的 `createTFunction` 沒有對應邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/vitest.setup.ts:89</code> 全域 mock 行為變更可能影響未修改的測試</summary>

舊的全域 mock 在沒有提供 namespace 時回傳原始 key（例如 `t('key')` 回傳 `'key'`），但新的 `createTFunction` 在沒有 namespace 時回傳 `fullKey`，而 `fullKey` 在沒有 namespace 時就是 key，因此行為相同。然而，當有 namespace 時，舊 mock 回傳 `ns.key`，新 mock 也回傳 `ns.key`，看似一致。但舊 mock 在 `options` 存在但沒有 `ns` 時，會回傳 `key`（因為 `prefix` 為空字串），而新 mock 在 `options` 存在但沒有 `ns` 時，會將 `options` 序列化並附加到 key 後面（例如 `key:{"foo":"bar"}`）。這可能導致依賴舊行為的測試失敗。

建議檢查所有使用全域 mock 的測試，確認是否有傳入非 `ns` 的選項。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊實作在 `options` 存在但無 `ns` 時回傳 `key`，而新實作 `createTFunction` 會將 `options` 序列化並附加。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 自訂 Trans mock 可能與 createReactI18nextMock 的 Trans 衝突</summary>

此處使用 `createReactI18nextMock()` 並覆寫 `Trans`，但 `createReactI18nextMock` 已經包含一個 `Trans` mock。覆寫是允許的，但需確認覆寫後的 `Trans` 行為符合測試預期。目前覆寫的 `Trans` 只處理 `i18nKey` 和 `components.trustSource`，與 `createTransMock` 的實作不同（後者會渲染 children 或翻譯文字）。若測試依賴 `createTransMock` 的行為，可能會失敗。

**判斷依據**：diff 中此檔案新增了自訂的 `Trans` 覆寫，而 `createReactI18nextMock` 本身也提供 `Trans`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> i18next-config mock 的 getFixedT 行為與全域 mock 不一致</summary>

此處的 `getFixedT` mock 在沒有 `options.ns` 時回傳原始 key，但全域 mock 的 `createTFunction` 在沒有 namespace 時回傳 key（相同），但在有 namespace 時回傳 `ns.key`（相同）。然而，`getFixedT` 的 mock 沒有處理其他選項（如 `returnObjects`），可能與全域 mock 的行為不一致。若測試依賴 `getFixedT` 的特定行為，可能需要調整。

**判斷依據**：diff 中此 mock 被修改，但未使用 `createTFunction`，可能與全域 mock 行為不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10301 (cache hit 10240) ｜ completion tokens 1861 ｜ PR #7</sub>