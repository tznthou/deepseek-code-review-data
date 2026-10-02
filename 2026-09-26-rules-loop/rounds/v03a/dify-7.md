<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將多個測試檔案中重複的 react-i18next mock 統一抽換為集中式 helper（web/test/i18n-mock.ts），並更新全域 mock 與文件。主要風險在於全域 mock 行為改變（回傳值加上 namespace 前綴）可能導致未同步更新的測試失敗，以及 helper 中 `createTFunction` 的參數序列化邏輯與舊 mock 不完全一致。建議先確認所有受影響測試已更新，並檢查 helper 的型別與行為是否符合預期。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `web/test/i18n-mock.ts:26` | createTFunction 的參數序列化可能與舊 mock 不一致 | 0.80 |
| ⚠️ | Major | `web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:72` | 自訂 Trans mock 可能與 helper 衝突 | 0.75 |
| 🔸 | Minor | `web/app/components/plugins/marketplace/index.spec.tsx:33` | i18next-config mock 的 getFixedT 行為改變可能影響其他測試 | 0.70 |
| 🔸 | Minor | `web/test/i18n-mock.ts:4` | TranslationMap 介面可能違反 R10（應使用 type 而非 interface） | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>web/test/i18n-mock.ts:26</code> createTFunction 的參數序列化可能與舊 mock 不一致</summary>

在 `createTFunction` 中，當有額外參數時，回傳值會加上 `:${JSON.stringify(params)}`。但舊的全域 mock 在 `options` 存在時，會先移除 `ns` 再序列化其餘參數，且若無其餘參數則不加後綴。此處邏輯看似相同，但需注意 `options` 可能包含 `returnObjects` 等特殊屬性，舊 mock 有針對 `returnObjects` 回傳陣列，新 helper 未處理此情況，可能導致依賴該行為的測試失敗。建議補上 `returnObjects` 的處理，或確認沒有測試使用此功能。

**判斷依據**：diff 中新增的 `createTFunction` 未處理 `options.returnObjects`，而舊的 `web/vitest.setup.ts` 中有 `if (options?.returnObjects) return [...]` 的邏輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>web/app/components/plugins/install-plugin/install-from-local-package/steps/install.spec.tsx:72</code> 自訂 Trans mock 可能與 helper 衝突</summary>

此處使用 `createReactI18nextMock()` 後又覆寫 `Trans`，但 `createReactI18nextMock` 已經包含一個 `Trans` mock。覆寫後的行為與 helper 不同，可能導致測試預期不一致。建議確認此覆寫是否必要，或改用 helper 提供的自訂翻譯功能。

**判斷依據**：diff 中該檔案新增了 `...createReactI18nextMock()` 並覆寫 `Trans`，但 helper 本身已提供 `Trans`，可能造成不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/app/components/plugins/marketplace/index.spec.tsx:33</code> i18next-config mock 的 getFixedT 行為改變可能影響其他測試</summary>

此處將 `getFixedT` 改為回傳帶 namespace 前綴的字串，但此 mock 僅在此檔案中定義，若其他測試依賴原本回傳 key 的行為，可能受到影響。建議確認此變更是否僅限於此測試檔案，或應更新全域 mock。

**判斷依據**：diff 中此檔案的 `getFixedT` mock 被修改，但其他檔案可能仍使用舊的 mock 行為。

</details>

<details><summary>🔸 <b>Minor</b> — <code>web/test/i18n-mock.ts:4</code> TranslationMap 介面可能違反 R10（應使用 type 而非 interface）</summary>

專案規範 R10 要求 TypeScript 使用 type 定義而非 interface。此處使用 `interface TranslationMap`，可能違反規範。建議改為 `type TranslationMap = Record<string, string | string[]>`。

**判斷依據**：diff 中新增的 `interface TranslationMap`，而專案規範 R10 明確要求使用 type。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12990 (cache hit 10240) ｜ completion tokens 1187 ｜ PR #7</sub>