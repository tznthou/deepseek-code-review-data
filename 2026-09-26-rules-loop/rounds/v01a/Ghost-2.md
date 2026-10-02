<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤繼承父評論作者資訊的問題，將 memberName/memberExpertise 改為僅使用目前登入成員的資料，並新增兩項 E2E 測試。主要風險在於 Form 元件中編輯器可編輯性判斷改為依賴 member.expertise，可能導致無 expertise 的成員無法編輯回覆內容；此外移除 comment prop 後需確認無其他使用處。整體方向正確，但需處理上述可編輯性邏輯問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯性判斷改為依賴 member.expertise 可能導致無 expertise 成員無法編輯 | 0.85 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:291` | 移除 comment prop 後需確認無其他使用處 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能影響回覆串接邏輯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯性判斷改為依賴 member.expertise 可能導致無 expertise 成員無法編輯</summary>

原本 `editor.setEditable(!!memberName && progress !== 'sending')` 使用 memberName 判斷，現在改為 `!!member?.expertise`。若登入成員沒有 expertise（例如一般使用者），編輯器將永遠不可編輯，導致無法輸入回覆內容。建議改回使用 memberName 或改用其他代表成員身分的欄位。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且 dependency array 由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:291</code> 移除 comment prop 後需確認無其他使用處</summary>

FormWrapper 的 props 型別移除了 `comment`，且不再傳入。需確認沒有其他元件依賴此 prop，否則可能造成型別錯誤或功能缺失。

**判斷依據**：diff 中移除了 `comment?: Comment;` 以及解構中的 `comment`，且 reply-form.tsx 中不再傳入 `comment={parent}`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能影響回覆串接邏輯</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。需確認 `parent` 是否為直接父評論，若 `openForm` 可能代表回覆到回覆的情境，此變更可能導致回覆層級錯誤。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`，且 dependency array 移除 `openForm`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5888 (cache hit 3456) ｜ completion tokens 810 ｜ PR #2</sub>