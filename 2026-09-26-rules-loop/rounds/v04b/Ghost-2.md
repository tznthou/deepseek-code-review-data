<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 修正回覆表單錯誤繼承父評論作者資訊的問題，移除 FormWrapper 的 comment prop，並調整回覆目標 ID 的來源。主要風險在於 member 可能為 null 時，`member?.expertise` 的判斷會導致編輯器永遠不可編輯，且 `openForm` 可能為 null 時直接存取 `openForm.in_reply_to_snippet` 會拋出錯誤。建議先處理這兩個問題，並確認回覆目標 ID 的變更符合預期。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/comments-ui/src/components/content/forms/form.tsx:264` | member 為 null 時編輯器將永遠不可編輯 | 0.95 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 可能為 null 時直接存取屬性導致錯誤 | 0.80 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標 ID 改為 parent.id 可能不正確 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> member 為 null 時編輯器將永遠不可編輯</summary>

在 `useEffect` 中，原本使用 `memberName` 判斷是否可編輯，現在改為 `!!member?.expertise`。若 `member` 為 null（例如未登入），`member?.expertise` 會是 `undefined`，導致 `editor.setEditable(false)`，使用者將無法輸入回覆。

**失敗情境**：未登入使用者嘗試回覆評論時，編輯器會是唯讀狀態。

**建議**：改回使用 `memberName` 或改用 `!!member?.name` 來判斷，確保未登入或無名稱的使用者仍可編輯。

**判斷依據**：diff 中此行將原本的 `!!memberName` 改為 `!!member?.expertise`，而 `member` 可能為 null。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 可能為 null 時直接存取屬性導致錯誤</summary>

在 `FormWrapper` 中，原本使用 `openForm?.in_reply_to_snippet` 安全存取，現在改為 `openForm.in_reply_to_snippet`。若 `openForm` 為 null 或 undefined，會拋出 `TypeError`。

**失敗情境**：當 `openForm` 為 null 時（例如表單未開啟），元件會崩潰。

**建議**：保留可選串連 `openForm?.in_reply_to_snippet`，或確保 `openForm` 在此處一定存在。

**判斷依據**：diff 中此行移除了 `openForm` 後面的 `?`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標 ID 改為 parent.id 可能不正確</summary>

原本使用 `openForm.in_reply_to_id` 作為回覆目標，現在改為 `parent.id`。若 `openForm` 代表的是對某個回覆的回覆（即 `in_reply_to_id` 指向該回覆），則此變更會導致回覆掛到錯誤的父評論下。

**失敗情境**：使用者點擊回覆某個回覆時，新回覆會錯誤地成為頂層評論的回覆。

**建議**：確認 `parent` 是否總是指向要回覆的評論，若不是，應保留 `openForm.in_reply_to_id`。

**判斷依據**：diff 中此行將 `openForm.in_reply_to_id` 改為 `parent.id`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4768 (cache hit 4736) ｜ completion tokens 936 ｜ PR #2</sub>