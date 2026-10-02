<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制。整體結構清晰，包含表單驗證、API 呼叫、錯誤處理與測試。主要風險在於表單提交時未處理非同步錯誤（如網路失敗）可能導致未處理的 Promise rejection，以及測試中對 useUpdateWorkPool 的 mock 方式可能與實際 hook 的實作不一致，導致測試無法有效驗證行為。建議優先修正錯誤處理與測試 mock 的正確性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:43` | 未處理的 Promise rejection 可能導致未捕獲的錯誤 | 0.80 |
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:28` | 測試中 mock 的 useUpdateWorkPool 可能與實際 hook 不符 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:60` | 錯誤訊息可能洩漏敏感資訊 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:43</code> 未處理的 Promise rejection 可能導致未捕獲的錯誤</summary>

在 `handleSubmit` 中呼叫 `updateWorkPool` 時，如果該函式回傳一個 Promise 且發生錯誤（例如網路失敗），而 `onError` 回呼未被正確設定或未處理，可能導致未處理的 Promise rejection。建議確認 `useUpdateWorkPool` 的實作是否會回傳 Promise，並在必要時加上 `.catch` 或確保 `onError` 總是被呼叫。

**判斷依據**：diff 中第 43-50 行顯示 `updateWorkPool` 被呼叫，但沒有 `.catch` 或 await，且 `onError` 僅在 options 中提供，若 hook 實作未正確處理錯誤，可能導致未處理的 rejection。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:28</code> 測試中 mock 的 useUpdateWorkPool 可能與實際 hook 不符</summary>

測試中 mock 了 `useUpdateWorkPool`，回傳一個包含 `updateWorkPool` 和 `isPending` 的物件。但實際 hook 可能回傳不同的結構（例如 `mutate` 而非 `updateWorkPool`），導致測試無法正確驗證元件行為。建議確認實際 hook 的 API，並調整 mock 以符合實際實作。

**判斷依據**：diff 中第 24-31 行顯示 mock 回傳 `updateWorkPool`，但實際 hook 可能使用不同的函式名稱（例如 `mutate`），這可能導致測試無法正確觸發提交邏輯。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:60</code> 錯誤訊息可能洩漏敏感資訊</summary>

在 `onError` 中直接使用 `error.message` 顯示錯誤訊息，如果錯誤訊息包含敏感資訊（例如 API 回應的詳細內容），可能導致資訊洩漏。建議對錯誤訊息進行過濾或使用通用的錯誤訊息。

**判斷依據**：diff 中第 55-57 行顯示錯誤訊息直接使用 `error.message`，未進行任何過濾。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9256 (cache hit 9216) ｜ completion tokens 999 ｜ PR #13</sub>