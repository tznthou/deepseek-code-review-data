<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單顯示父留言作者資訊的問題，將 memberName 與 memberExpertise 改為僅使用目前登入成員的資料，並調整回覆目標為 parent.id。主要風險在於移除 fallback 後，若登入成員缺少 name 或 expertise，表單可能出現空白或無法編輯的狀態，且測試僅驗證不顯示父作者資訊，未涵蓋登入成員資料缺失時的表單行為。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 登入成員缺少 expertise 時編輯器將無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:244` | 移除 memberName 的 fallback 可能導致表單顯示空白名稱 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標改為 parent.id 可能影響巢狀回覆 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | 移除 openForm 的 optional chaining 可能導致錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 登入成員缺少 expertise 時編輯器將無法編輯</summary>

原本的條件 `!!memberName && progress !== 'sending'` 改為 `!!member?.expertise && progress !== 'sending'`，這表示當登入成員沒有 expertise 時，編輯器會被設為不可編輯。這可能導致使用者無法輸入回覆內容，尤其是新使用者或未填寫 expertise 的成員。建議改回以 memberName 作為判斷，或另外處理缺少 expertise 的情況。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且依賴陣列也從 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:244</code> 移除 memberName 的 fallback 可能導致表單顯示空白名稱</summary>

原本 `const memberName = member?.name ?? comment?.member?.name;` 在登入成員沒有 name 時會 fallback 到父留言作者的名稱，現在改為 `const memberName = member?.name;`，若登入成員 name 為 null 或 undefined，表單可能顯示空白或觸發其他依賴 memberName 的邏輯。建議確認此情境下的 UI 行為，並考慮提供預設值或提示。

**判斷依據**：diff 中此行由 `const memberName = member?.name ?? comment?.member?.name;` 改為 `const memberName = member?.name;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標改為 parent.id 可能影響巢狀回覆</summary>

原本 `in_reply_to_id: openForm.in_reply_to_id` 改為 `in_reply_to_id: parent.id`，這可能改變回覆的目標。若 openForm 代表的是對某個回覆的回覆（巢狀回覆），則原本的 in_reply_to_id 可能指向該回覆的 id，而現在改為 parent.id 可能導致回覆層級錯誤。建議確認 parent 的定義及巢狀回覆的預期行為。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> 移除 openForm 的 optional chaining 可能導致錯誤</summary>

原本 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`，若 openForm 可能為 null 或 undefined，則會拋出錯誤。建議確認 openForm 在此處是否保證存在，或保留 optional chaining。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5812 (cache hit 3584) ｜ completion tokens 1107 ｜ PR #2</sub>