<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的 description 與 concurrency_limit。整體結構清晰，使用 react-hook-form + zod 進行表單驗證，並包含完整的 Storybook 與測試。主要風險在於 concurrency_limit 的輸入處理：若使用者輸入負數或非整數值，前端不會阻擋，可能導致 API 收到無效資料。此外，測試中 mock 的型別與實際 hook 回傳不完全一致，可能隱藏型別錯誤。建議優先修正輸入驗證，並考慮在 schema 中加入限制。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | concurrency_limit 允許負數與非整數輸入 | 0.85 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16` | mockUpdateWorkPool 型別與實際 hook 回傳不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> concurrency_limit 允許負數與非整數輸入</summary>

在 `onChange` 中直接將輸入值轉為 `Number(value)`，未檢查是否為正整數。若使用者輸入 `-5` 或 `2.5`，表單會接受並提交，可能導致後端驗證失敗或產生非預期行為。建議在 zod schema 中加入 `.int().positive()` 驗證，或在 `onChange` 中阻擋無效值。

**判斷依據**：diff 中新增的 `onChange` 處理直接將字串轉為數字，沒有驗證範圍或整數性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16</code> mockUpdateWorkPool 型別與實際 hook 回傳不一致</summary>

`mockUpdateWorkPool` 被定義為 `vi.fn<(data: unknown, options: UpdateWorkPoolOptions) => void>()`，但實際 `useUpdateWorkPool` 回傳的 `updateWorkPool` 函式簽章可能不同（例如參數型別更具體）。這可能導致測試中對參數的斷言不準確，或隱藏型別錯誤。建議使用 `Parameters<ReturnType<typeof useUpdateWorkPool>['updateWorkPool']>` 來取得正確型別。

**判斷依據**：測試中手動定義了 `UpdateWorkPoolOptions` 型別，但未與實際 API 型別連結。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7725 (cache hit 1408) ｜ completion tokens 664 ｜ PR #13</sub>