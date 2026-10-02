<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤繼承父留言作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆目標改為 parent.id、以及新增兩項 E2E 測試。整體方向正確，但需注意 member 可能為 null 時 editor.setEditable 的邏輯變更，以及移除 comment prop 後是否影響其他使用 FormWrapper 的地方。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | editor.setEditable 改為依賴 member?.expertise 可能導致編輯器在 member 為 null 時無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:299` | 移除 FormWrapper 的 comment prop 可能影響其他使用此元件的程式碼 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標改為 parent.id 可能影響巢狀回覆的正確性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> editor.setEditable 改為依賴 member?.expertise 可能導致編輯器在 member 為 null 時無法編輯</summary>

原本的條件是 `!!memberName && progress !== 'sending'`，其中 memberName 可能來自 member 或 comment。現在改為 `!!member?.expertise && progress !== 'sending'`，這表示如果目前登入的 member 沒有 expertise（或 member 為 null），編輯器將永遠無法編輯。這可能不是預期行為，因為使用者即使沒有 expertise 也應該能輸入回覆內容。建議確認此變更是否符合產品需求，或改回使用 memberName 作為判斷條件。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且依賴陣列由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:299</code> 移除 FormWrapper 的 comment prop 可能影響其他使用此元件的程式碼</summary>

FormWrapper 的 props 型別移除了 `comment?: Comment`，且元件內不再使用 `comment`。但此元件可能被其他檔案引用並傳入 comment prop，若未同步更新所有使用處，將導致型別錯誤或執行期錯誤。建議搜尋整個程式碼庫確認所有使用 FormWrapper 的地方都已移除 comment prop。

**判斷依據**：diff 中 FormWrapperProps 型別移除了 `comment?: Comment;`，且元件參數解構移除了 `comment,`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標改為 parent.id 可能影響巢狀回覆的正確性</summary>

原本使用 `openForm.in_reply_to_id` 作為回覆目標，現在改為 `parent.id`。這可能改變巢狀回覆的行為：如果 openForm 代表的是對某個回覆的回覆，則原本的 in_reply_to_id 會指向該回覆，而 parent.id 可能指向頂層留言。需確認此變更是否符合預期，特別是在巢狀回覆的情境下。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`，且依賴陣列移除了 openForm。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4768 (cache hit 3456) ｜ completion tokens 898 ｜ PR #2</sub>