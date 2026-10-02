<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制。整體結構清晰，測試涵蓋了主要互動。主要風險在於並行限制輸入的型別轉換（Number(value) 可能產生 NaN）以及表單提交時未處理的錯誤情境。建議修正這些問題後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:114` | 並行限制輸入可能產生 NaN | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:43` | 表單提交錯誤處理不完整 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:114</code> 並行限制輸入可能產生 NaN</summary>

在 onChange 處理中，`Number(value)` 若 value 為空字串或非數字字串（例如使用者輸入 'e' 或 '-'），會得到 `NaN`。這會導致表單提交時將 NaN 傳送到 API，可能造成後端驗證錯誤或資料不一致。建議在轉換前檢查 value 是否為空或非數字，或使用 `Number.isNaN` 驗證。

**判斷依據**：diff 中新增的 onChange 處理直接將輸入轉為 Number，未處理 NaN 情況。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:43</code> 表單提交錯誤處理不完整</summary>

handleSubmit 中呼叫 updateWorkPool 時，僅在 onError 中顯示 toast，但未處理可能出現的同步錯誤（例如 updateWorkPool 拋出例外）。若 updateWorkPool 本身拋出錯誤，將導致未捕捉的 Promise rejection。建議將呼叫包在 try/catch 中，或確保 updateWorkPool 不會拋出同步錯誤。

**判斷依據**：updateWorkPool 呼叫未包在 try/catch 中，且未處理可能的同步錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7761 (cache hit 7680) ｜ completion tokens 588 ｜ PR #13</sub>