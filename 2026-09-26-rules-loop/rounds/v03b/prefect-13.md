<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件與對應的測試、Storybook 故事，並將編輯頁面串接起來。整體結構清楚，測試涵蓋了主要互動。主要風險在於表單提交時未處理非同步錯誤（handleSubmit 未 await），以及 concurrency limit 的輸入驗證可能允許負數或小數。此外，部分測試的型別斷言可能不準確，且 Storybook 故事重複性高。建議優先修正表單提交的錯誤處理與輸入驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41` | 表單提交未處理非同步錯誤 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | Concurrency limit 輸入允許負數與小數 | 0.75 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158` | 測試中對 mockUpdateWorkPool 的型別斷言可能不準確 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.stories.tsx:23` | Storybook 故事重複性高，可考慮使用 args 重用 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41</code> 表單提交未處理非同步錯誤</summary>

`handleSubmit` 呼叫 `updateWorkPool` 時沒有 `await`，且 `updateWorkPool` 回傳的 Promise 若被拒絕，錯誤不會被捕獲，可能導致 unhandled rejection。建議改為 `async` 函式並 `await updateWorkPool(...)`，或至少在 `onError` 中處理（目前已有 `onError`，但若 Promise 本身 reject 則不會觸發）。

**判斷依據**：diff 中 `handleSubmit` 未標記為 async，且呼叫 `updateWorkPool` 後未接 `.catch` 或 `await`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> Concurrency limit 輸入允許負數與小數</summary>

`onChange` 直接將輸入轉為 `Number`，未驗證是否為正整數。使用者可輸入負數或小數，可能導致 API 請求錯誤或非預期行為。建議在 schema 中加入 `int().positive()` 驗證，或在 `onChange` 中限制。

**判斷依據**：diff 中 `onChange` 直接使用 `Number(value)`，未檢查數值範圍或整數性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158</code> 測試中對 mockUpdateWorkPool 的型別斷言可能不準確</summary>

在 `handles empty concurrency limit as null` 測試中，將 `mockUpdateWorkPool.mock.calls[0]` 斷言為特定型別，但實際呼叫參數可能包含其他欄位，型別斷言可能隱藏錯誤。建議使用更精確的斷言或直接比對物件。

**判斷依據**：diff 中該測試使用型別斷言，可能掩蓋實際參數結構不符的問題。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.stories.tsx:23</code> Storybook 故事重複性高，可考慮使用 args 重用</summary>

多個故事僅變更 workPool 屬性，但重複定義相同的 MSW handler。建議使用 Storybook 的 `args` 或 `render` 函式來減少重複。

**判斷依據**：diff 中多個故事結構相似，僅 workPool 不同。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9266 (cache hit 9216) ｜ completion tokens 1076 ｜ PR #13</sub>