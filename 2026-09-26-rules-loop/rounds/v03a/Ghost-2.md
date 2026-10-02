<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正回覆表單錯誤顯示父留言作者資訊的問題，主要變更在移除 FormWrapper 對 comment prop 的依賴，並將回覆的 in_reply_to_id 改為 parent.id。整體方向正確，但存在兩個主要風險：一是 Form 元件中編輯器可編輯條件改為 member?.expertise，可能導致有姓名但無 expertise 的成員無法編輯；二是移除 comment prop 後，若其他使用 FormWrapper 的地方仍傳入 comment 會造成型別錯誤。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯條件改為 member?.expertise 可能導致有姓名但無 expertise 的成員無法編輯 | 0.90 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:291` | 移除 FormWrapper 的 comment prop 可能導致其他使用處型別錯誤 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯條件改為 member?.expertise 可能導致有姓名但無 expertise 的成員無法編輯</summary>

原本條件為 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。若成員有姓名但 expertise 為 null（例如測試中的 Jane Replier），編輯器將無法編輯，但成員應可正常回覆。建議改回使用 memberName 或同時檢查兩者。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且測試中設定 member 為 `{name: 'Jane Replier', expertise: null}`，預期應可編輯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:291</code> 移除 FormWrapper 的 comment prop 可能導致其他使用處型別錯誤</summary>

FormWrapper 的 props 型別移除了 `comment?: Comment`，且元件內不再使用。但若其他元件仍傳入 `comment` prop，TypeScript 會報錯。需確認所有使用 FormWrapper 的地方都已移除該 prop。

**判斷依據**：diff 中移除了 `comment?: Comment;` 這一行，且 FormWrapper 函式參數也移除了 `comment`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。若 openForm 代表回覆某則回覆（巢狀回覆），則 in_reply_to_id 應指向被回覆的留言 id，而非最上層 parent id。需確認此變更是否符合預期。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5898 (cache hit 3456) ｜ completion tokens 837 ｜ PR #2</sub>