<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件及其測試與 Storybook 故事，並將編輯頁面串接起來。整體結構清晰，測試涵蓋了主要互動流程。主要風險在於表單提交時未處理 description 為 undefined 的情況，可能導致 API 收到 undefined 而非 null；此外，測試中對 useUpdateWorkPool 的 mock 型別定義不完整，可能隱藏型別錯誤。建議修正 description 的處理邏輯，並補強測試的型別定義。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:47` | description 為 undefined 時未轉為 null | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16` | mockUpdateWorkPool 型別定義不完整 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:47</code> description 為 undefined 時未轉為 null</summary>

在 handleSubmit 中，`trimmedDescription` 可能為 undefined（當使用者清空欄位且 schema 允許 undefined 時），但程式碼僅在 `trimmedDescription === ""` 時設為 null，否則直接傳遞 `trimmedDescription`。這可能導致 API 收到 undefined 而非 null，造成型別不符或後端處理錯誤。建議改為 `description: trimmedDescription ? trimmedDescription : null` 或明確處理 undefined。

**判斷依據**：diff 中第 40 行：`description: trimmedDescription === "" ? null : trimmedDescription,`

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16</code> mockUpdateWorkPool 型別定義不完整</summary>

`mockUpdateWorkPool` 的型別定義為 `vi.fn<(data: unknown, options: UpdateWorkPoolOptions) => void>()`，但實際呼叫時第一個參數是 `{ name: string; workPool: { description: string | null; concurrency_limit: number | null } }`。使用 `unknown` 會失去型別檢查，可能隱藏錯誤。建議定義明確的參數型別，例如 `vi.fn<(data: { name: string; workPool: WorkPoolUpdate }, options: UpdateWorkPoolOptions) => void>()`。

**判斷依據**：diff 中第 15-16 行：`const mockUpdateWorkPool = vi.fn<(data: unknown, options: UpdateWorkPoolOptions) => void>();`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9211 (cache hit 9088) ｜ completion tokens 649 ｜ PR #13</sub>