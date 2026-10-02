<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤顯示父留言作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、改用 member 的 expertise 來控制編輯器可編輯性，以及將回覆的 in_reply_to_id 改為 parent.id。整體方向正確，但需注意 member 可能為 null 時的可編輯性邏輯、openForm 可能為 null 的風險，以及測試中對 member-name 的斷言可能不穩定。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | member 為 null 時編輯器可能被錯誤設為可編輯 | 0.80 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 可能為 null 導致執行錯誤 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:678` | 測試斷言可能不穩定：member-name 可能不存在 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> member 為 null 時編輯器可能被錯誤設為可編輯</summary>

在 useEffect 中，`editor.setEditable(!!member?.expertise && progress !== 'sending')` 當 `member` 為 null 時，`member?.expertise` 為 undefined，導致 `!!undefined` 為 false，編輯器將被設為不可編輯。若使用者未登入（member 為 null），回覆表單可能無法輸入。建議改為 `editor.setEditable(progress !== 'sending')` 或明確處理 member 為 null 的情況。

**判斷依據**：diff 中將原本的 `editor.setEditable(!!memberName && progress !== 'sending')` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending')`，且 dependency array 從 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 可能為 null 導致執行錯誤</summary>

在 `FormWrapper` 中，`const isReplyToReply = !!openForm.in_reply_to_snippet;` 直接存取 `openForm.in_reply_to_snippet`，但 `openForm` 的型別可能允許 null（從原本的 `openForm?.in_reply_to_snippet` 改為 `openForm.in_reply_to_snippet`）。若 `openForm` 為 null，會拋出 TypeError。建議保留 optional chaining 或確保 openForm 不為 null。

**判斷依據**：diff 中將 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`，移除了 optional chaining。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:678</code> 測試斷言可能不穩定：member-name 可能不存在</summary>

在測試「Reply form does not inherit name from parent comment author」中，`await expect(memberName).not.toHaveText('Named Author');` 若 `member-name` 元素不存在，此斷言會失敗。但根據測試情境，登入會員的 name 為 null，可能導致該元素不渲染。建議先確認元素存在或改用其他方式驗證。

**判斷依據**：測試中設定 `mockedApi.setMember({name: null, expertise: 'Some Expertise'})`，若元件在 name 為 null 時不渲染 `member-name`，則 `getByTestId` 會拋出錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5888 (cache hit 5760) ｜ completion tokens 942 ｜ PR #2</sub>