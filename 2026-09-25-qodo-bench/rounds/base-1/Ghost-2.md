<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤繼承父評論作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆的 in_reply_to_id 改為 parent.id、並新增兩項 E2E 測試。整體方向正確，但需注意 member 可能為 null 時 member?.expertise 的存取安全性，以及 openForm 可能為 null 的風險。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | member 可能為 null 時存取 member.expertise 可能拋出錯誤 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 可能為 null 時直接存取 in_reply_to_snippet 可能拋出錯誤 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能影響回覆邏輯 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> member 可能為 null 時存取 member.expertise 可能拋出錯誤</summary>

在 `editor.setEditable(!!member?.expertise && progress !== 'sending')` 中，若 `member` 為 null，`member?.expertise` 會回傳 undefined，`!!undefined` 為 false，因此不會拋出錯誤。但此處邏輯與原本使用 `memberName` 不同，可能導致編輯器在成員沒有 expertise 時被設為不可編輯，即使成員有名字。建議確認此行為是否符合預期，或改用 `member?.name` 或同時檢查兩者。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且 dependency array 由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 可能為 null 時直接存取 in_reply_to_snippet 可能拋出錯誤</summary>

在 `const isReplyToReply = !!openForm.in_reply_to_snippet;` 中，若 `openForm` 為 null 或 undefined，則會拋出 TypeError。原本程式碼使用 `openForm?.in_reply_to_snippet` 可選串連，此變更移除了安全保護。建議保留可選串連或確保 openForm 永遠不為 null。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能影響回覆邏輯</summary>

將 `in_reply_to_id` 從 `openForm.in_reply_to_id` 改為 `parent.id`，可能改變回覆的目標。若 `openForm.in_reply_to_id` 原本可能指向不同的父評論（例如回覆回覆），此變更可能導致回覆錯誤。建議確認 parent 是否永遠為正確的回覆目標。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3579 (cache hit 1536) ｜ completion tokens 882 ｜ PR #2</sub>