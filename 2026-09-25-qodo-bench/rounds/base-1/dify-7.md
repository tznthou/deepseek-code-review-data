<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一抽換為集中式 helper（`web/test/i18n-mock.ts`），並更新全域 mock 與相關文件。整體方向正確，可減少重複並提升可維護性。主要風險在於全域 mock 行為變更（回傳值從 key 改為 ns.key）可能影響未更新到的測試，以及 helper 中 `createTFunction` 對 `options` 的處理可能與實際 react-i18next 行為有差異。建議確認所有依賴舊行為的測試都已更新，並補齊 helper 的單元測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:12` | createTFunction 對 options 的處理可能與實際 react-i18next 不一致 | 0.80 |
| 🔸 | Minor | `web/test/i18n-mock.ts:24` | 序列化 params 時未處理 returnObjects 選項 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69` | 動態 import helper 可能導致 mock 延遲 | 0.70 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:33` | i18next-config mock 的 getFixedT 行為變更可能影響其他測試 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:12</code> createTFunction 對 options 的處理可能與實際 react-i18next 不一致</summary>

`createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

**判斷依據**：diff 中新增的 `createTFunction` 函式，第 13-14 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:24</code> 序列化 params 時未處理 returnObjects 選項</summary>

全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

**判斷依據**：diff 中新增的 `createTFunction` 函式，第 21-23 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:69</code> 動態 import helper 可能導致 mock 延遲</summary>

在 `vi.mock` 工廠中使用 `await import('@/test/i18n-mock')` 會延遲 mock 的建立，可能影響測試執行順序。建議直接靜態 import helper，或確認此模式在專案中已廣泛使用且無副作用。

**判斷依據**：diff 中 install.spec.tsx 第 67 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:33</code> i18next-config mock 的 getFixedT 行為變更可能影響其他測試</summary>

此處將 `getFixedT` 的 mock 改為回傳 `ns.key` 格式，但未確認是否有其他測試依賴原本回傳 key 的行為。建議搜尋所有使用 `getFixedT` 的測試，確保沒有遺漏。

**判斷依據**：diff 中 marketplace/index.spec.tsx 第 30-37 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10301 (cache hit 1536) ｜ completion tokens 1073 ｜ PR #7</sub>