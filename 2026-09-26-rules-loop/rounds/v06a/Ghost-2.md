<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單顯示父評論作者資訊的問題，移除 FormWrapper 的 comment prop 並調整回覆目標 ID 的來源。主要風險在於 Form 元件中編輯器可編輯性判斷改用 member?.expertise，可能導致有姓名但無 expertise 的成員無法編輯，且測試未涵蓋此情境。另有 openForm 可選性不一致、依賴陣列未更新等次要問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯性判斷改用 expertise 可能導致有姓名但無 expertise 的成員無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 可能為 undefined，直接存取 in_reply_to_snippet 有風險 | 0.60 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | useCallback 依賴陣列未包含 parent.id，可能導致回覆目標錯誤 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯性判斷改用 expertise 可能導致有姓名但無 expertise 的成員無法編輯</summary>

原本以 memberName 判斷是否可編輯，現在改為 member?.expertise。若成員有姓名但 expertise 為 null（如測試中 'Jane Replier'），編輯器將被設為不可編輯，使用者無法輸入回覆。建議改回以 memberName 判斷，或同時考慮兩者。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且測試案例 'Reply form does not inherit expertise from parent comment author' 設定成員 expertise 為 null，但未驗證編輯器是否可編輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 可能為 undefined，直接存取 in_reply_to_snippet 有風險</summary>

原本使用 `openForm?.in_reply_to_snippet`，現在改為 `openForm.in_reply_to_snippet`。若 openForm 可能為 undefined，會拋出 TypeError。請確認 openForm 在此處必定有值，或保留可選鏈。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`，移除了可選鏈。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> useCallback 依賴陣列未包含 parent.id，可能導致回覆目標錯誤</summary>

回覆目標 ID 改為 parent.id，但 useCallback 依賴陣列仍為 [parent, postId, dispatchAction]，未包含 parent.id。若 parent 物件相同但 id 改變（不太可能），可能使用舊值。建議將依賴改為 [parent.id, postId, dispatchAction] 或直接使用 parent.id。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`，但下方依賴陣列未變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5878 (cache hit 3456) ｜ completion tokens 832 ｜ PR #2</sub>