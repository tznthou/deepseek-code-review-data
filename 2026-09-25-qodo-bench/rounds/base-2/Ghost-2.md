<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單顯示父留言作者資訊的問題，移除 FormWrapper 的 comment prop 並改用目前登入成員的資料。主要風險在於 Form 元件中編輯器可編輯性判斷改為依賴 member.expertise，可能導致有姓名但無 expertise 的成員無法編輯，且 ReplyForm 的 in_reply_to_id 改為 parent.id 可能影響巢狀回覆。整體方向正確，但需確認上述行為變更是否符合預期。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯性改依賴 expertise，可能導致有姓名但無 expertise 的成員無法編輯 | 0.80 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能影響巢狀回覆 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | 移除 openForm 的 optional chaining 可能導致錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯性改依賴 expertise，可能導致有姓名但無 expertise 的成員無法編輯</summary>

原本 `editor.setEditable(!!memberName && progress !== 'sending')` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending')`。若成員有姓名但 expertise 為 null（例如一般使用者），編輯器將無法編輯，即使他們有權限發表留言。這可能造成功能回歸。建議改回使用 memberName 或同時檢查兩者。

**判斷依據**：diff 中此行取代了原本的 `editor.setEditable(!!memberName && progress !== 'sending');`，且 dependency array 從 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能影響巢狀回覆</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。若 openForm 代表回覆某則回覆（巢狀回覆），則 in_reply_to_id 應指向被回覆的回覆 ID，而非最上層 parent 的 ID。這可能導致回覆串結構錯誤。請確認 openForm 的語意：若 openForm 是針對特定回覆，則應保留原本的 `openForm.in_reply_to_id`。

**判斷依據**：diff 中此行取代了 `in_reply_to_id: openForm.in_reply_to_id,`，且 dependency array 移除了 openForm。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> 移除 openForm 的 optional chaining 可能導致錯誤</summary>

原本 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`。若 openForm 可能為 null 或 undefined，則會拋出 TypeError。請確認 openForm 在此處是否保證存在。

**判斷依據**：diff 中移除了 optional chaining 運算子 `?.`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3579 (cache hit 3456) ｜ completion tokens 826 ｜ PR #2</sub>