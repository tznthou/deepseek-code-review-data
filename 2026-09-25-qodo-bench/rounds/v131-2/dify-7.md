<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 邏輯統一至 `web/test/i18n-mock.ts`，並更新全域 mock 以使用新的 helper。整體方向正確，能減少重複並提升可維護性。主要風險在於全域 mock 行為變更（回傳值從 key 改為 ns.key）可能影響未更新的測試，以及 `createTFunction` 對 `returnObjects` 選項的處理與舊實作不一致。建議確認所有相關測試已更新，並補上 `returnObjects` 的支援。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | createTFunction 未處理 returnObjects 選項 | 0.80 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 動態 import 可能導致 mock 延遲 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> createTFunction 未處理 returnObjects 選項</summary>

舊的全域 mock 在 `options.returnObjects` 為真時會回傳陣列，但新的 `createTFunction` 沒有這個邏輯。若任何測試或元件依賴此行為，將導致測試失敗或元件渲染錯誤。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```ts
if (options?.returnObjects)
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
```

**判斷依據**：diff 中舊的 `web/vitest.setup.ts` 有 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createTFunction` 沒有此邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 動態 import 可能導致 mock 延遲</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 會使 mock 的建立變成非同步。雖然 Vitest 支援非同步工廠，但若測試在 mock 完成前就執行，可能導致錯誤。建議改為頂層靜態 import，或確認此模式在專案中已普遍使用且無問題。

**判斷依據**：diff 中該檔案新增了 `await import('@/test/i18n-mock')`，而其他檔案都是靜態 import。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10265 (cache hit 10240) ｜ completion tokens 735 ｜ PR #7</sub>