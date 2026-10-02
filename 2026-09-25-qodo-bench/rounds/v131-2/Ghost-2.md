<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤繼承父評論作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆目標 ID 改為 parent.id，並新增兩項 E2E 測試。整體方向正確，但需注意：移除 comment prop 後，FormWrapper 不再有父評論資料，若未來需要顯示父評論資訊將無法取得；此外，回覆表單的編輯器可編輯性改為依賴 member.expertise，可能導致有姓名但無 expertise 的使用者無法編輯，需確認是否符合預期。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯性改為依賴 expertise，可能導致部分使用者無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標 ID 改為 parent.id，可能影響巢狀回覆 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/src/components/content/forms/form.tsx:291` | 移除 comment prop 可能影響未來功能擴充 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯性改為依賴 expertise，可能導致部分使用者無法編輯</summary>

原本編輯器可編輯性取決於 memberName 是否存在，現在改為 member?.expertise。若使用者有姓名但沒有 expertise（例如一般使用者），編輯器將無法編輯，可能造成功能回歸。建議確認此變更是否符合產品需求，或改回以 memberName 判斷。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且依賴陣列由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標 ID 改為 parent.id，可能影響巢狀回覆</summary>

原本使用 openForm.in_reply_to_id 作為回覆目標，現在改為 parent.id。若 parent 是回覆的回覆（即巢狀回覆），parent.id 可能不是正確的頂層回覆 ID，導致回覆鏈結錯誤。需確認 parent 的定義及後端處理邏輯。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`，且依賴陣列移除 openForm。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:291</code> 移除 comment prop 可能影響未來功能擴充</summary>

FormWrapper 原本可接收 comment prop 以顯示父評論資訊，現在完全移除。若未來需要顯示父評論作者資訊或引用內容，將需要重新加入。目前無直接影響，但需注意擴充性。

**判斷依據**：diff 中移除了 `comment?: Comment;` 及對應的解構與使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3543 (cache hit 3456) ｜ completion tokens 803 ｜ PR #2</sub>