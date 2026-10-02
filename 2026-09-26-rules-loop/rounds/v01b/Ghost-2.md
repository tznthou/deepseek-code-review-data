<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 修正了回覆表單錯誤繼承父評論作者姓名與專業領域的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆目標 ID 改為 parent.id，並新增兩項 E2E 測試。整體方向正確，但需注意：移除 comment prop 後，FormWrapper 內部的 memberName 與 memberExpertise 僅依賴目前登入會員，可能影響其他使用情境；此外，回覆目標 ID 的變更需確認後端處理邏輯是否相容。建議合併前確認這些行為變更不會造成回歸。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯條件改為 member?.expertise 可能導致無專業領域的會員無法編輯 | 0.80 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標 ID 改為 parent.id 可能影響巢狀回覆的正確性 | 0.75 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:308` | 移除 comment prop 後，FormWrapper 不再顯示父評論作者資訊 | 0.60 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:309` | 移除 comment prop 後，FormWrapper 不再顯示父評論作者專業領域 | 0.60 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 可能為 undefined 時直接存取屬性可能導致錯誤 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯條件改為 member?.expertise 可能導致無專業領域的會員無法編輯</summary>

原本條件為 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。這表示若登入會員沒有設定專業領域（expertise 為 null 或空字串），即使有姓名，編輯器也會被設為不可編輯。這可能不是預期行為，因為姓名與專業領域是獨立欄位，會員可能只填了其中一項。建議確認此變更是否符合產品需求，或改回以 memberName 作為判斷依據。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且依賴陣列由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標 ID 改為 parent.id 可能影響巢狀回覆的正確性</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。若 `openForm` 代表的是回覆某則回覆（即巢狀回覆），則 `parent.id` 可能不是正確的回覆目標。需確認 `parent` 在此元件的定義：若 `parent` 是頂層評論，而 `openForm.in_reply_to_id` 可能指向另一則回覆，則此變更會導致回覆連結錯誤。建議確認後端如何處理 `in_reply_to_id`，並確保此變更不會破壞巢狀回覆功能。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`，且依賴陣列移除了 `openForm`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:308</code> 移除 comment prop 後，FormWrapper 不再顯示父評論作者資訊</summary>

原本 FormWrapper 會以 `member?.name ?? comment?.member?.name` 取得顯示名稱，現在僅使用 `member?.name`。這表示當登入會員沒有姓名時，表單將不會顯示任何名稱，即使父評論作者有姓名。這可能是預期行為（避免錯誤繼承），但需確認是否有其他情境需要顯示父評論作者資訊。

**判斷依據**：diff 中此行由 `const memberName = member?.name ?? comment?.member?.name;` 改為 `const memberName = member?.name;`，且 FormWrapperProps 移除了 `comment` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:309</code> 移除 comment prop 後，FormWrapper 不再顯示父評論作者專業領域</summary>

原本 FormWrapper 會以 `member?.expertise ?? comment?.member?.expertise` 取得專業領域，現在僅使用 `member?.expertise`。這表示當登入會員沒有專業領域時，表單將不會顯示任何專業領域，即使父評論作者有。這可能是預期行為，但需確認是否有其他情境需要顯示父評論作者專業領域。

**判斷依據**：diff 中此行由 `const memberExpertise = member?.expertise ?? comment?.member?.expertise;` 改為 `const memberExpertise = member?.expertise;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 可能為 undefined 時直接存取屬性可能導致錯誤</summary>

原本使用 `openForm?.in_reply_to_snippet` 可選串連，現在改為 `openForm.in_reply_to_snippet`。若 `openForm` 可能為 undefined，則會拋出錯誤。需確認 `openForm` 在此處是否保證存在，否則應保留可選串連。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5888 (cache hit 5760) ｜ completion tokens 1434 ｜ PR #2</sub>