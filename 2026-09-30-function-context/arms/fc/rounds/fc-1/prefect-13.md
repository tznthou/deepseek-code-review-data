<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯 work pool 的 description 與 concurrency limit，並整合了 API 呼叫、表單驗證、Storybook 與測試。整體結構清晰，測試覆蓋良好。主要風險在於 concurrency limit 的輸入處理：Number(value) 可能產生 NaN，且未限制最小值，可能送出無效資料。此外，錯誤處理僅依賴 toast，未保留錯誤狀態供使用者重試。建議修正輸入驗證與錯誤處理後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | concurrency limit 輸入可能產生 NaN 或負數 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:59` | 錯誤處理僅顯示 toast，未保留錯誤狀態 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> concurrency limit 輸入可能產生 NaN 或負數</summary>

在 onChange 中直接使用 `Number(value)`，若使用者輸入非數字字元（例如 'e'、'-'、'+'），可能得到 NaN。此外，沒有驗證最小值，可能送出負數。建議使用 zod schema 驗證（例如 `z.number().int().nonnegative().nullable()`），或在 onChange 中過濾無效輸入。

**判斷依據**：diff 中新增的 onChange handler 直接將輸入轉為 Number，未檢查 NaN 或負數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:59</code> 錯誤處理僅顯示 toast，未保留錯誤狀態</summary>

onError 僅顯示 toast，使用者無法得知具體錯誤內容或重試。建議在表單中顯示錯誤訊息，或保留 mutation 的 error 狀態供使用者參考。

**判斷依據**：diff 中 onError 僅呼叫 toast.error，未將錯誤存入 state 或顯示於表單。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7846 (cache hit 1536) ｜ completion tokens 567 ｜ PR #13</sub>