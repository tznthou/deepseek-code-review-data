<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 i18n mock 邏輯統一至 `web/test/i18n-mock.ts` 的輔助函式，並更新全域 mock 與文件。整體方向正確，可減少重複並提升可維護性。主要風險在於全域 mock 行為變更（回傳值加上 namespace 前綴）可能影響未更新測試的斷言，以及 `createTFunction` 對 `returnObjects` 選項的處理與舊行為不一致。建議確認所有受影響測試已同步更新，並補齊輔助函式的單元測試。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:10` | `createTFunction` 未處理 `returnObjects` 選項，可能導致依賴此功能的測試失敗 | 0.80 |
| ⚠️ | Major | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67` | 自訂 `Trans` mock 覆蓋了輔助函式提供的 `Trans`，可能遺失預設行為 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:31` | `getFixedT` mock 的型別可能與實際函式不符 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:10` | 輔助函式缺少單元測試 | 0.65 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:10</code> `createTFunction` 未處理 `returnObjects` 選項，可能導致依賴此功能的測試失敗</summary>

在舊的全域 mock 中，當 `options.returnObjects` 為真時，會回傳一個陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`）。新的 `createTFunction` 完全沒有檢查 `returnObjects`，因此會回傳字串。若任何測試或元件依賴此行為（例如使用 `returnObjects: true` 來取得多個翻譯），測試將失敗。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，或確認沒有測試使用此選項。

**判斷依據**：diff 中 `web/vitest.setup.ts` 的舊 mock 有 `if (options?.returnObjects) return [`${key}-feature-1`, `${key}-feature-2`]`，但新的 `createTFunction` 沒有此邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:67</code> 自訂 `Trans` mock 覆蓋了輔助函式提供的 `Trans`，可能遺失預設行為</summary>

在此測試中，`vi.mock('react-i18next', ...)` 回傳的物件包含 `...createReactI18nextMock()` 和自訂的 `Trans`。由於物件展開的順序，自訂的 `Trans` 會覆蓋輔助函式提供的 `Trans`。這可能是有意為之，但需確認自訂 `Trans` 是否完整支援所有需要的功能（例如 `components` 的處理）。若輔助函式的 `Trans` 有額外邏輯（如 `data-i18n-key` 屬性），此覆蓋可能導致測試行為不一致。建議檢查是否真的需要覆蓋，或改用輔助函式的參數來客製化。

**判斷依據**：diff 中此測試檔案新增了自訂 `Trans`，且放在 `...createReactI18nextMock()` 之後，因此會覆蓋輔助函式的 `Trans`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:31</code> `getFixedT` mock 的型別可能與實際函式不符</summary>

在 `vi.mock('@/i18n-config/i18next-config', ...)` 中，`getFixedT` 的回傳函式被改為接受 `options?: Record<string, unknown>`，但實際的 `getFixedT` 可能接受不同的參數型別（例如 `i18next.TFunction` 的選項）。若型別不符，可能導致測試中的型別錯誤或誤導。建議確認實際的 `getFixedT` 簽章，並使用正確的型別。

**判斷依據**：diff 中此處的 mock 函式型別從 `(key: string) => key` 改為 `(key: string, options?: Record<string, unknown>) => ...`，但未確認與實際型別一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:10</code> 輔助函式缺少單元測試</summary>

新增的 `web/test/i18n-mock.ts` 包含多個輔助函式，但沒有對應的測試。這些函式將被多個測試檔案使用，若行為有誤可能影響大量測試。建議為這些輔助函式撰寫單元測試，涵蓋自訂翻譯、namespace 前綴、參數序列化等情境。

**判斷依據**：diff 中新增了 `web/test/i18n-mock.ts`，但沒有看到對應的測試檔案。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10265 (cache hit 1408) ｜ completion tokens 1523 ｜ PR #7</sub>