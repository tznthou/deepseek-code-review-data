<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單顯示父留言作者資訊的問題，移除從父留言回退取得 member 名稱與 expertise 的邏輯，並調整回覆 API 的 in_reply_to_id 為 parent.id。主要風險在於 Form 元件中 editor.setEditable 的條件從 memberName 改為 member?.expertise，可能導致未設定 expertise 的已登入成員無法編輯，且測試未涵蓋此情境。另有 openForm 參數改為必填，需確認所有呼叫點皆已更新。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | editor.setEditable 條件改為 member?.expertise 可能導致無 expertise 的成員無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 參數改為必填，需確認所有呼叫點皆已更新 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> editor.setEditable 條件改為 member?.expertise 可能導致無 expertise 的成員無法編輯</summary>

原本條件為 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。若已登入成員沒有設定 expertise（例如新使用者或未填寫），即使有 name，編輯器也會被設為不可編輯，導致無法輸入回覆。建議改回使用 `memberName` 或同時檢查兩者，並新增測試涵蓋此情境。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且測試僅涵蓋 expertise 為 null 時不繼承父留言，未驗證編輯器是否可編輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 參數改為必填，需確認所有呼叫點皆已更新</summary>

FormWrapper 的 props 型別中 `openForm?: OpenCommentForm` 改為 `openForm: OpenCommentForm`，且使用 `openForm.in_reply_to_snippet` 時不再使用可選串連。若其他元件未傳入 openForm，可能導致執行時期錯誤。請確認所有使用 FormWrapper 的地方都已傳入 openForm。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`，且 props 型別移除可選標記。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 13299 (cache hit 1536) ｜ completion tokens 675 ｜ PR #2</sub>