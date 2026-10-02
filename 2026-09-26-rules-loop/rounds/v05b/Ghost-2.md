<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單不應繼承父評論作者的名稱與專業領域的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆的 in_reply_to_id 改為 parent.id，並新增兩個 E2E 測試。整體方向正確，但需注意 member 可能為 undefined 的防禦性處理，以及測試中對 member-name 的斷言可能因元件未渲染該元素而失敗。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | member 可能為 undefined，直接存取 member.expertise 可能導致執行錯誤 | 0.75 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:679` | 測試中對 member-name 的斷言可能因元素不存在而失敗 | 0.65 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯條件改為 member.expertise，可能與原本意圖不符 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> member 可能為 undefined，直接存取 member.expertise 可能導致執行錯誤</summary>

在 `useEffect` 中，`member` 可能為 `undefined`（例如尚未載入或登出狀態），直接使用 `member?.expertise` 仍可能因 `member` 為 `undefined` 而拋出錯誤。建議使用 `member?.expertise` 或先檢查 `member` 是否存在。

**判斷依據**：diff 中將原本的 `!!memberName` 改為 `!!member?.expertise`，但 `member` 本身可能為 undefined，雖然使用了 optional chaining，但若 `member` 為 undefined，`member?.expertise` 會回傳 undefined，`!!undefined` 為 false，不會拋錯。但若 `member` 為 null，`member?.expertise` 同樣安全。因此此處可能無實際錯誤，但需確認 `member` 的型別是否允許 null/undefined。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。若 `openForm` 代表回覆某則回覆（即巢狀回覆），則 `parent` 可能不是直接父評論，導致回覆層級錯誤。需確認 `parent` 的定義是否為直接父評論。

**判斷依據**：diff 中將 `openForm.in_reply_to_id` 改為 `parent.id`，但 `parent` 是傳入的 prop，可能代表頂層評論而非直接父評論。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:679</code> 測試中對 member-name 的斷言可能因元素不存在而失敗</summary>

在第二個測試中，`await expect(memberName).not.toHaveText('Named Author');` 若 `member-name` 元素不存在，`toHaveText` 會拋出錯誤，導致測試失敗。建議先確認元素是否存在，或改用 `toBeHidden()` 等斷言。

**判斷依據**：diff 中新增的測試直接對 `memberName` 使用 `not.toHaveText`，但若該元素未渲染，測試會失敗。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯條件改為 member.expertise，可能與原本意圖不符</summary>

原本條件為 `!!memberName`，現在改為 `!!member?.expertise`。若使用者有姓名但沒有專業領域，編輯器將無法編輯，這可能不是預期行為。建議確認需求：是否應以 `memberName` 或 `member` 存在與否來決定可編輯性。

**判斷依據**：diff 中將 `!!memberName` 改為 `!!member?.expertise`，但 `memberName` 原本是 `member?.name ?? comment?.member?.name`，現在移除 comment 後，若 member 有 name 但無 expertise，編輯器將被停用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5812 (cache hit 5760) ｜ completion tokens 1095 ｜ PR #2</sub>