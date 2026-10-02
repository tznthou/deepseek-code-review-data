<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，並整合了路由與測試。整體結構清晰，測試覆蓋了主要互動流程。主要風險在於表單提交時未處理非同步錯誤、輸入驗證不足（如負數並行限制）、以及測試中 mock 的型別與實際 API 可能不一致。建議先修正錯誤處理與驗證邏輯，再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:73` | 表單提交未處理非同步錯誤 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:91` | 並行限制輸入允許負數 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16` | mock 函式型別與實際 API 可能不符 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:88` | 描述欄位未限制最大長度 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:73</code> 表單提交未處理非同步錯誤</summary>

`handleSubmit` 呼叫 `updateWorkPool` 時，若 mutation 拋出非同步錯誤（例如網路錯誤），錯誤只會由 `onError` 回呼處理，但 `form.handleSubmit` 的 promise 可能被拒絕而未捕捉，導致 unhandled rejection。建議在 `onSubmit` 中使用 `try/catch` 或確保 `updateWorkPool` 不會拋出未處理的 rejection。

**判斷依據**：第 48 行：`onSubmit={(e) => void form.handleSubmit(handleSubmit)(e)}` 未處理 `handleSubmit` 可能拋出的錯誤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:91</code> 並行限制輸入允許負數</summary>

`concurrencyLimit` 欄位使用 `type="number"`，但未設定 `min` 屬性，使用者可以輸入負數。若後端未驗證，可能導致不正確的並行限制。建議加入 `min={0}` 或使用 zod schema 驗證非負整數。

**判斷依據**：第 91-99 行：`Input` 未設定 `min` 屬性，且 `onChange` 直接將值轉為數字，未檢查是否為負數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16</code> mock 函式型別與實際 API 可能不符</summary>

`mockUpdateWorkPool` 的型別為 `(data: unknown, options: UpdateWorkPoolOptions) => void`，但實際的 `useUpdateWorkPool` 回傳的 `updateWorkPool` 可能接受不同的參數型別（例如 `WorkPoolUpdate` 與 `{ onSuccess, onError }`）。這可能導致測試在型別檢查時通過，但實際執行時出現型別錯誤。建議使用更精確的型別或從實際 API 推導。

**判斷依據**：第 18-19 行：mock 函式使用 `unknown` 作為第一個參數型別，可能隱藏型別錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:88</code> 描述欄位未限制最大長度</summary>

`description` 欄位使用 `Textarea`，但未設定 `maxLength` 屬性。若後端有長度限制，使用者可能輸入過長內容導致提交失敗。建議根據 API 規格加入 `maxLength` 或使用 zod schema 驗證。

**判斷依據**：第 78-84 行：`Textarea` 未設定 `maxLength`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8463 (cache hit 8448) ｜ completion tokens 1241 ｜ PR #13</sub>