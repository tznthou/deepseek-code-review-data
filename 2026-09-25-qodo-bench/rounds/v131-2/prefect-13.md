<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，並整合到路由中。整體結構清晰，包含 Storybook 與測試。主要風險在於表單提交時未處理非同步錯誤、並行限制輸入未限制最小值、以及測試中對 mock 的型別斷言可能不準確。建議先修正錯誤處理與輸入驗證，再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:73` | 表單提交未處理非同步錯誤 | 0.85 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:109` | 並行限制輸入未限制最小值 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158` | 測試中對 mock 呼叫參數的型別斷言可能不準確 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:73</code> 表單提交未處理非同步錯誤</summary>

`handleSubmit` 呼叫 `updateWorkPool` 時，若 mutation 本身拋出同步例外（例如網路錯誤），由於 `onSubmit` 使用 `void form.handleSubmit(handleSubmit)(e)`，錯誤不會被捕獲，可能導致 unhandled rejection。建議在 `handleSubmit` 內使用 try/catch 或確保 `updateWorkPool` 回傳的 promise 有被 catch。

**判斷依據**：diff 中新增的 `onSubmit` 處理器直接呼叫 `form.handleSubmit` 並忽略回傳的 promise，若 `handleSubmit` 內拋出錯誤，將無法被捕捉。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:109</code> 並行限制輸入未限制最小值</summary>

並行限制輸入使用 `type="number"`，但未設定 `min` 屬性，使用者可以輸入負數或 0。若後端未驗證，可能導致非預期行為。建議加入 `min={0}` 或使用 zod schema 驗證。

**判斷依據**：diff 中新增的 Input 元件僅設定 `type="number"`，未見 `min` 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158</code> 測試中對 mock 呼叫參數的型別斷言可能不準確</summary>

在測試 `handles empty concurrency limit as null` 中，使用 `as` 斷言 `mockUpdateWorkPool.mock.calls[0]` 的型別，但實際呼叫參數可能包含額外欄位，斷言可能過於嚴格或錯誤。建議使用 `expect.objectContaining` 或直接檢查特定屬性。

**判斷依據**：diff 中測試檔案第 150 行附近的型別斷言。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7725 (cache hit 7680) ｜ completion tokens 781 ｜ PR #13</sub>