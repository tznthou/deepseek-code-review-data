<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤顯示父留言作者資訊的問題。主要變更包括：移除 FormWrapper 的 comment prop、將回覆目標 ID 改為 parent.id、以及新增兩項 E2E 測試。整體方向正確，但存在一個可能導致編輯器在成員無 expertise 時無法編輯的邏輯變更，以及測試中對 member-name 的斷言可能不穩定。建議先確認編輯器可編輯性邏輯的意圖。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/form.tsx:264` | 編輯器可編輯性改為依賴 expertise 可能導致無 expertise 成員無法編輯 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:679` | 測試中對 member-name 的斷言可能不穩定 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/form.tsx:264</code> 編輯器可編輯性改為依賴 expertise 可能導致無 expertise 成員無法編輯</summary>

原本 `editor.setEditable(!!memberName && progress !== 'sending')` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending')`。這表示若登入成員沒有 expertise（即使有名字），編輯器將被設為不可編輯，使用者無法輸入回覆。這可能不是預期行為，因為回覆不應要求 expertise。建議確認此變更意圖，若僅為修正顯示問題，應保留以 memberName 判斷可編輯性。

**判斷依據**：diff 中此行由 `editor.setEditable(!!memberName && progress !== 'sending');` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending');`，且 dependency array 也由 `[editor, memberName, progress]` 改為 `[editor, member, progress]`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:679</code> 測試中對 member-name 的斷言可能不穩定</summary>

在第二個測試中，斷言 `await expect(memberName).not.toHaveText('Named Author');` 只檢查不包含父作者名稱，但未驗證實際顯示內容。若元件未正確渲染或顯示其他文字，此斷言仍會通過，無法有效捕捉回歸。建議改為更明確的斷言，例如檢查顯示為空、'Anonymous' 或提示輸入名稱。

**判斷依據**：測試程式碼中此斷言僅使用 not.toHaveText，未對預期內容做正向驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5878 (cache hit 5760) ｜ completion tokens 644 ｜ PR #2</sub>