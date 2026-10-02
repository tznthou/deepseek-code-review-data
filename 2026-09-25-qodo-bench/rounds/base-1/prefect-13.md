<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制。整體結構清晰，使用 react-hook-form 與 zod 進行表單驗證，並包含完整的 Storybook 與測試。主要風險在於並行限制的輸入處理：若使用者輸入負數或非整數值，可能導致 API 收到無效資料；此外，表單提交時未處理欄位值未變更的情況，可能造成不必要的 API 呼叫。建議在 schema 中加入更嚴格的驗證，並考慮加入 dirty check。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | 並行限制輸入未驗證，可能送出負數或非整數值 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41` | 表單提交時未檢查欄位是否變更，可能造成不必要的 API 呼叫 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> 並行限制輸入未驗證，可能送出負數或非整數值</summary>

在 `onChange` 中直接將輸入轉為 `Number`，但未檢查是否為有效整數或正數。若使用者輸入 `-5` 或 `2.5`，表單會接受並在提交時送出，可能導致 API 錯誤或非預期的行為。建議在 zod schema 中加入 `.int().positive()` 驗證，或在 `onChange` 中過濾無效值。

**判斷依據**：diff 中新增的 `onChange` 處理直接將輸入轉為數字，沒有驗證範圍或整數性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41</code> 表單提交時未檢查欄位是否變更，可能造成不必要的 API 呼叫</summary>

即使使用者未修改任何欄位，點擊 Save 仍會呼叫 `updateWorkPool`。這可能導致不必要的網路請求，並在 API 端產生無意義的更新。建議使用 `form.formState.isDirty` 來判斷是否真的需要提交，或在提交前比較初始值。

**判斷依據**：`handleSubmit` 中沒有檢查 `form.formState.isDirty`，直接呼叫 `updateWorkPool`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7761 (cache hit 1536) ｜ completion tokens 622 ｜ PR #13</sub>