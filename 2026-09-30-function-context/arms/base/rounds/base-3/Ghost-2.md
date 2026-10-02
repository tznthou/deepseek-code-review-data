<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤繼承父評論作者資訊的問題。主要變更包括移除 FormWrapper 的 comment prop、將回覆目標改為 parent.id、以及調整編輯器可編輯條件。整體方向正確，但需注意 member 可能為 null 時的可編輯性判斷、openForm 可能為 null 的風險，以及測試中對 UI 文字的脆弱斷言。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | member 可能為 null 時 editor.setEditable 判斷有誤 | 0.75 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:313` | openForm 可能為 null 時存取 in_reply_to_snippet 會拋錯 | 0.70 |
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | 回覆目標改為 parent.id 可能影響巢狀回覆 | 0.70 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:648` | 測試斷言依賴特定 UI 文字，可能脆弱 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> member 可能為 null 時 editor.setEditable 判斷有誤</summary>

原本的判斷是 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。如果 `member` 為 null，`member?.expertise` 會是 undefined，導致 `!!undefined` 為 false，編輯器會被設為不可編輯。但若使用者未登入（member 為 null），回覆表單可能仍應允許輸入（例如匿名回覆）。請確認此情境下的預期行為，並考慮使用 `member?.expertise != null` 或調整條件。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且依賴陣列由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:313</code> openForm 可能為 null 時存取 in_reply_to_snippet 會拋錯</summary>

原本使用 `openForm?.in_reply_to_snippet` 可選串連，現在改為 `openForm.in_reply_to_snippet`。若 `openForm` 可能為 null 或 undefined，此處會拋出 TypeError。請確認 `openForm` 在此情境下是否保證非空，否則應保留可選串連或加入防護。

**判斷依據**：diff 中此行由 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> 回覆目標改為 parent.id 可能影響巢狀回覆</summary>

原本使用 `openForm.in_reply_to_id` 作為回覆目標，現在改為 `parent.id`。若 `parent` 是回覆的回覆（即巢狀回覆），`parent.id` 可能不是正確的頂層回覆 ID，導致回覆鏈結錯誤。請確認此變更是否符合預期，並考慮是否應保留 `openForm.in_reply_to_id` 或使用其他方式取得正確的父 ID。

**判斷依據**：diff 中此行由 `in_reply_to_id: openForm.in_reply_to_id,` 改為 `in_reply_to_id: parent.id,`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:648</code> 測試斷言依賴特定 UI 文字，可能脆弱</summary>

測試中斷言 expertise 按鈕文字為 '·Add your expertise'，若 UI 文字變更（例如改為 'Add expertise' 或加上其他符號），測試會失敗。建議改用更穩定的定位方式（如 data-testid 或部分文字比對）。

**判斷依據**：diff 中新增的測試包含此行，且文字包含特殊字元 '·'，可能因 UI 微調而變動。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3579 (cache hit 3456) ｜ completion tokens 1093 ｜ PR #2</sub>