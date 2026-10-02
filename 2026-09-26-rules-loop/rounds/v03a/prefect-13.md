<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，並包含 Storybook 故事與單元測試。整體結構清晰，表單使用 react-hook-form 與 zod 驗證，測試涵蓋主要互動。主要風險在於並行限制輸入的型別轉換可能產生 NaN，以及表單提交時未處理驗證失敗的情境。建議修正後合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:114` | 並行限制輸入可能產生 NaN | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41` | 表單提交未處理驗證失敗 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:114</code> 並行限制輸入可能產生 NaN</summary>

在 onChange 處理中，將輸入值轉為 Number，但未檢查轉換結果是否為 NaN。若使用者輸入非數字字元（例如 'e'、'-'、'+'），Number(value) 會回傳 NaN，導致表單狀態包含 NaN，可能造成後端 API 收到無效的 concurrency_limit。建議在轉換前驗證輸入是否為有效數字，或使用 zod schema 的 number 驗證來攔截。

**判斷依據**：diff 中新增的 onChange 處理直接將 e.target.value 轉為 Number，未檢查 NaN。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41</code> 表單提交未處理驗證失敗</summary>

handleSubmit 直接呼叫 updateWorkPool，但未檢查表單驗證是否通過。若使用者輸入無效資料（例如非數字並行限制），zodResolver 會阻止提交，但此處沒有處理驗證失敗的 UI 回饋。建議使用 form.handleSubmit 的回傳值或搭配 onInvalid 來顯示錯誤訊息。

**判斷依據**：handleSubmit 函式未檢查 form.formState.errors 或使用 form.handleSubmit 的錯誤處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9266 (cache hit 7680) ｜ completion tokens 544 ｜ PR #13</sub>