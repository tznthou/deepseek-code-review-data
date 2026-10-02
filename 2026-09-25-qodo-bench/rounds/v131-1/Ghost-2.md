<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤繼承父評論作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆的 in_reply_to_id 改為 parent.id，以及新增兩個 E2E 測試。整體方向正確，但需注意 member 可能為 null 時 editor.setEditable 的判斷邏輯，以及測試中對 member-name 的斷言可能不穩定。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | member 可能為 null 時 editor.setEditable 判斷錯誤 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:244` | memberName 變數不再有 fallback，可能影響其他邏輯 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:679` | 測試中對 member-name 的斷言可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> member 可能為 null 時 editor.setEditable 判斷錯誤</summary>

原本的判斷是 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。如果 `member` 為 null，`member?.expertise` 會是 undefined，導致 `!!undefined` 為 false，因此編輯器會被設為不可編輯。這可能導致未登入或 member 資料未載入時，使用者無法編輯回覆內容。建議改為 `!!member && !!member.expertise && progress !== 'sending'` 或保留原本的 memberName 判斷。

**判斷依據**：diff 中此行將原本的 `!!memberName` 改為 `!!member?.expertise`，但未考慮 member 為 null 的情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:244</code> memberName 變數不再有 fallback，可能影響其他邏輯</summary>

原本 `const memberName = member?.name ?? comment?.member?.name;` 現在改為 `const memberName = member?.name;`。如果 member 為 null 或 name 為 null，memberName 會是 undefined。後續程式碼中 `if (progress === 'sending' || (memberName && isAskingDetails))` 的判斷會受到影響，可能導致 isAskingDetails 流程無法正確觸發。建議確認此變更不會影響其他依賴 memberName 的邏輯。

**判斷依據**：diff 中移除了 fallback 到 comment?.member?.name 的邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構</summary>

原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。如果 openForm 代表的是回覆某個回覆（即巢狀回覆），則原本的 in_reply_to_id 可能指向上一層回覆的 id，而 parent.id 可能指向頂層評論的 id。這可能導致回覆的巢狀結構不正確。建議確認 parent 的定義是否為直接父評論，並確保此變更符合預期。

**判斷依據**：diff 中將 `openForm.in_reply_to_id` 改為 `parent.id`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:679</code> 測試中對 member-name 的斷言可能不穩定</summary>

在測試 'Reply form does not inherit name from parent comment author' 中，使用 `await expect(memberName).not.toHaveText('Named Author');` 來斷言回覆表單不顯示父評論作者的名字。但若回覆表單顯示的是空字串或 'Anonymous'，此斷言會通過；然而若顯示的是其他文字（例如 'Add your name'），也可能通過。建議改為更精確的斷言，例如檢查是否顯示預期的提示文字。

**判斷依據**：測試中僅使用 not.toHaveText 來排除特定文字，未驗證實際顯示內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3543 (cache hit 1408) ｜ completion tokens 1080 ｜ PR #2</sub>