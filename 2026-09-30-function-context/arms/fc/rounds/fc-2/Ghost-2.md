<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單顯示父評論作者資訊的問題，移除 Form 與 FormWrapper 中對 comment prop 的依賴，並將回覆的 in_reply_to_id 改為 parent.id。主要風險在於 Form 中編輯器可編輯條件從 memberName 改為 member?.expertise，可能導致未設定 expertise 的成員無法編輯，且 FormWrapper 的 openForm 改為必填可能影響其他使用情境。新增測試涵蓋主要情境，但缺少對無 expertise 成員的編輯測試。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯條件改為 member?.expertise 可能導致無 expertise 成員無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | FormWrapper 的 openForm 改為必填可能影響其他使用情境 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯條件改為 member?.expertise 可能導致無 expertise 成員無法編輯</summary>

原本條件為 `!!memberName`，現在改為 `!!member?.expertise`。若登入成員沒有 expertise（例如新使用者或未填寫），編輯器將被設為不可編輯，導致無法輸入回覆。建議改回使用 `memberName` 或同時檢查兩者。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> FormWrapper 的 openForm 改為必填可能影響其他使用情境</summary>

原本 `openForm` 為可選，現在改為必填。若其他元件未傳入 `openForm`，可能導致執行時錯誤。建議確認所有使用 FormWrapper 的地方都有傳入 openForm，或保留可選並處理 undefined。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13299 (cache hit 13184) ｜ completion tokens 580 ｜ PR #2</sub>