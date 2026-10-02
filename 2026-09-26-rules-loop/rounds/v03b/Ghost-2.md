<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單不應繼承父留言作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆目標改為 parent.id，以及新增兩項 E2E 測試。整體方向正確，但需注意 member 可能為 null 時 editor.setEditable 的邏輯、移除 comment prop 對其他使用者的影響，以及測試中對 member-name 的斷言可能不穩定。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | editor.setEditable 在 member 為 null 時可能錯誤地啟用編輯器 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:291` | 移除 comment prop 可能影響其他使用 FormWrapper 的元件 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標改為 parent.id 可能影響巢狀回覆邏輯 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:642` | 測試斷言可能不穩定：member-name 可能不存在或顯示其他內容 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> editor.setEditable 在 member 為 null 時可能錯誤地啟用編輯器</summary>

原本的條件是 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。如果 `member` 為 null（例如訪客未登入），`member?.expertise` 會是 undefined，導致 `!!undefined` 為 false，編輯器會被停用。這可能不是預期行為，因為訪客可能仍應能輸入回覆。建議確認訪客情境下的預期行為，並考慮使用 `member?.expertise != null` 或保留原本的 memberName 判斷。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且 dependency array 由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:291</code> 移除 comment prop 可能影響其他使用 FormWrapper 的元件</summary>

FormWrapper 的 props 型別移除了 `comment`，且不再使用 `comment?.member?.name` 和 `comment?.member?.expertise`。若其他元件仍傳入 `comment` prop，TypeScript 會報錯，但若未傳入，行為可能改變。建議搜尋所有使用 FormWrapper 的地方，確認沒有其他地方依賴此 prop。

**判斷依據**：diff 中移除了 `comment?: Comment;` 以及解構中的 `comment,`，並將 `const memberName = member?.name ?? comment?.member?.name;` 改為 `const memberName = member?.name;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標改為 parent.id 可能影響巢狀回覆邏輯</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。若 `openForm.in_reply_to_id` 原本可能指向不同的留言（例如回覆回覆），此變更可能破壞巢狀回覆功能。建議確認 `parent` 是否總是代表正確的回覆目標，並檢查相關測試。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`，且 dependency array 移除了 `openForm`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:642</code> 測試斷言可能不穩定：member-name 可能不存在或顯示其他內容</summary>

測試中 `await expect(replyForm.getByTestId('member-name')).toHaveText('Jane Replier');` 假設回覆表單會顯示登入會員的姓名。但若 UI 在會員姓名為 null 時不顯示該元素，或顯示其他文字（如「Anonymous」），測試可能失敗。建議確認實際 UI 行為，並調整斷言以符合規格。

**判斷依據**：此測試為新增，且依賴於 `member-name` testid 的存在與內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5898 (cache hit 5888) ｜ completion tokens 1146 ｜ PR #2</sub>