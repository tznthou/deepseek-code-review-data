<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，並包含 Storybook 故事與單元測試。整體結構清晰，測試覆蓋良好。主要風險在於表單提交時未處理非同步錯誤（handleSubmit 未 await），可能導致未捕捉的 Promise rejection；此外，測試中 mock 的型別與實際 API 可能不完全匹配，且部分測試斷言依賴實作細節。建議修正非同步錯誤處理後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41` | handleSubmit 未處理非同步錯誤 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16` | mockUpdateWorkPool 型別可能與實際 API 不符 | 0.60 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158` | 測試斷言依賴實作細節 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41</code> handleSubmit 未處理非同步錯誤</summary>

`handleSubmit` 呼叫 `updateWorkPool` 但未 `await` 或回傳其 Promise。若 `updateWorkPool` 內部拋出同步錯誤或回傳 rejected Promise（例如網路層錯誤未由 onError 捕捉），將導致未捕捉的 Promise rejection，可能造成應用程式不穩定。建議將 `handleSubmit` 改為 async 並 `await updateWorkPool(...)`，或確保 `updateWorkPool` 的實作會捕捉所有錯誤並呼叫 onError。

**判斷依據**：diff 中新增的 handleSubmit 函式未使用 await 或回傳 updateWorkPool 的 Promise，且未包覆 try/catch。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:16</code> mockUpdateWorkPool 型別可能與實際 API 不符</summary>

測試中定義的 `mockUpdateWorkPool` 型別為 `(data: unknown, options: UpdateWorkPoolOptions) => void`，但實際 `useUpdateWorkPool` 回傳的 `updateWorkPool` 可能接受不同參數型別（例如 `WorkPoolUpdate` 與 `UseMutationOptions`）。若型別不符，測試可能在編譯階段通過但無法正確模擬行為，或導致測試脆弱。建議從 `@/api/work-pools` 匯入實際型別並使用 `Parameters<ReturnType<typeof useUpdateWorkPool>['updateWorkPool']>` 來定義 mock 型別。

**判斷依據**：diff 中 mockUpdateWorkPool 的型別定義使用自訂的 UpdateWorkPoolOptions，而非從 API 模組匯入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158</code> 測試斷言依賴實作細節</summary>

測試「handles empty concurrency limit as null」直接檢查 `mockUpdateWorkPool.mock.calls[0]` 的參數結構，這與元件內部如何呼叫 `updateWorkPool` 的實作細節耦合。若未來重構參數傳遞方式（例如改為單一物件），測試將失敗。建議改為驗證使用者可見的行為（例如成功 toast 或導航），或使用更穩定的 mock 驗證方式。

**判斷依據**：diff 中測試直接存取 mock 呼叫的參數陣列並斷言其結構。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9246 (cache hit 7680) ｜ completion tokens 980 ｜ PR #13</sub>