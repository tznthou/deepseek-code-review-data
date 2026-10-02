<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正回覆表單錯誤顯示父留言作者資訊的問題，移除 FormWrapper 中對 comment prop 的依賴，並調整回覆時 in_reply_to_id 的來源。整體方向正確，但存在一個可能影響回覆功能的邏輯變更，以及測試中對 member-name 元素的假設可能不成立，需進一步確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/comments-ui/src/components/content/forms/reply-form.tsx:30` | in_reply_to_id 改為 parent.id 可能導致回覆目標錯誤 | 0.80 |
| 🔸 | Minor | `apps/comments-ui/test/e2e/actions.test.ts:678` | 測試中對 member-name 元素的假設可能不成立 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/comments-ui/src/components/content/forms/reply-form.tsx:30</code> in_reply_to_id 改為 parent.id 可能導致回覆目標錯誤</summary>

原本使用 `openForm.in_reply_to_id` 來指定回覆的目標留言，現在改為 `parent.id`。若 `openForm` 是用於回覆某個子留言（即回覆的回覆），則 `parent` 可能代表頂層留言，而非直接父留言，導致回覆串接錯誤。請確認 `parent` 與 `openForm.in_reply_to_id` 的關係，並確保回覆目標正確。

**判斷依據**：diff 中將 `in_reply_to_id: openForm.in_reply_to_id` 改為 `in_reply_to_id: parent.id`，且 `parent` 是元件 prop，可能不是直接父留言。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/comments-ui/test/e2e/actions.test.ts:678</code> 測試中對 member-name 元素的假設可能不成立</summary>

測試預期回覆表單中有 `member-name` 元素，但若登入成員沒有名稱，該元素可能不會渲染，導致 `getByTestId('member-name')` 找不到元素而失敗。建議先確認元件在無名稱時的行為，或改用更穩健的斷言方式。

**判斷依據**：測試中直接取得 `member-name` 元素，但未確認其在無名稱時是否存在。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5888 (cache hit 1536) ｜ completion tokens 546 ｜ PR #2</sub>