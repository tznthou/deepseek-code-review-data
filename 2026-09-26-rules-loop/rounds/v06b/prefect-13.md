<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，包含表單驗證、API 呼叫、成功/失敗處理與測試。整體結構清晰，但存在數個問題：最嚴重的是表單提交時未處理 React Hook Form 的驗證錯誤，可能導致使用者看到錯誤卻仍送出請求；此外，並行限制輸入未限制最小值，可能送出負數；測試中 mock 的型別與實際 API 不符，可能隱藏型別錯誤；Storybook 中多個 story 重複相同的 mock handler，可簡化。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:73` | 表單提交未處理驗證錯誤，可能導致無效資料送出 | 0.95 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:108` | 並行限制輸入未限制最小值，可能送出負數 | 0.85 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16` | 測試中 mock 的型別與實際 API 不符，可能隱藏型別錯誤 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.stories.tsx:27` | Storybook 中重複的 mock handler 可簡化 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:73</code> 表單提交未處理驗證錯誤，可能導致無效資料送出</summary>

在 `handleSubmit` 中直接呼叫 `updateWorkPool`，但未檢查 `form.handleSubmit` 的結果。React Hook Form 的 `handleSubmit` 會先執行驗證，若驗證失敗則不會呼叫傳入的 callback，但此處的寫法 `onSubmit={(e) => void form.handleSubmit(handleSubmit)(e)}` 忽略了回傳值，因此即使驗證失敗，使用者仍可能看到錯誤訊息，但表單不會送出，造成困惑。更嚴重的是，若驗證通過但 `updateWorkPool` 拋出同步錯誤（例如網路錯誤），則錯誤不會被捕獲，可能導致未處理的 Promise rejection。

**建議**：使用 `form.handleSubmit(handleSubmit)` 直接作為 `onSubmit`，讓 React Hook Form 處理驗證與錯誤；或明確處理驗證失敗的情況，例如：
```tsx
onSubmit={form.handleSubmit(handleSubmit)}
```
並確保 `handleSubmit` 中的非同步操作有適當的錯誤處理。

**判斷依據**：在 work-pool-edit-form.tsx 第 46 行，`onSubmit` 使用 `void form.handleSubmit(handleSubmit)(e)`，忽略了 `handleSubmit` 的回傳值，且未處理驗證失敗或非同步錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:108</code> 並行限制輸入未限制最小值，可能送出負數</summary>

在 `concurrencyLimit` 的輸入欄位中，`type="number"` 但未設定 `min` 屬性，也未在 schema 中驗證非負。使用者可以輸入負數（例如 -1），表單會通過驗證並送出，可能導致後端錯誤或非預期行為。

**建議**：在 `workPoolEditSchema` 中對 `concurrencyLimit` 加入 `.min(0)` 驗證，或在輸入欄位加上 `min={0}`。

**判斷依據**：在 work-pool-edit-form.tsx 第 108 行，`Input` 元件未設定 `min` 屬性，且 schema 未驗證非負。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16</code> 測試中 mock 的型別與實際 API 不符，可能隱藏型別錯誤</summary>

在測試中，`mockUpdateWorkPool` 被定義為 `vi.fn<(data: unknown, options: UpdateWorkPoolOptions) => void>()`，但實際的 `useUpdateWorkPool` 回傳的 `updateWorkPool` 函式簽章可能不同（例如接受特定型別的參數）。這可能導致測試通過但實際使用時型別錯誤。

**建議**：從 `@/api/work-pools` 匯入實際的型別，並使用正確的函式簽章來定義 mock，例如：
```ts
const mockUpdateWorkPool = vi.fn<Parameters<ReturnType<typeof useUpdateWorkPool>['updateWorkPool']>>();
```

**判斷依據**：在 work-pool-edit-form.test.tsx 第 18 行，mock 函式使用 `unknown` 作為資料參數型別，可能與實際 API 不符。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.stories.tsx:27</code> Storybook 中重複的 mock handler 可簡化</summary>

多個 story 都定義了相同的 `http.patch` handler，僅回傳 204。這會造成重複程式碼，且未來若 API 變更需修改多處。

**建議**：將共用的 handler 提取為常數，並在 story 的 `parameters.msw.handlers` 中引用。

**判斷依據**：在 work-pool-edit-form.stories.tsx 中，多個 story 重複相同的 handler 定義。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9246 (cache hit 9216) ｜ completion tokens 1539 ｜ PR #13</sub>