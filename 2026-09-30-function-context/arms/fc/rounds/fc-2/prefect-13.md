<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制。整體結構清晰，包含表單驗證、API 呼叫、成功/失敗處理與測試。主要風險在於並行限制的輸入處理：若使用者輸入負數或非整數，可能導致 API 收到無效值；此外，表單在提交時未處理 API 回傳的錯誤細節，僅顯示通用訊息。建議在合併前修正輸入驗證與錯誤處理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | 並行限制輸入未驗證，可能傳送負數或非整數 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:59` | 錯誤訊息未顯示 API 回傳的細節 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> 並行限制輸入未驗證，可能傳送負數或非整數</summary>

在 `concurrencyLimit` 的輸入處理中，直接將輸入值轉為 `Number`，未檢查是否為正整數。若使用者輸入 `-1` 或 `1.5`，表單會通過驗證並將這些值傳送給 API，可能導致後端錯誤或非預期行為。

建議在 schema 中加入驗證規則，例如使用 zod 的 `int().positive()`，或在 `onChange` 中過濾無效值。

**判斷依據**：diff 中新增的 `onChange` 處理直接將輸入轉為數字，沒有驗證範圍或整數性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:59</code> 錯誤訊息未顯示 API 回傳的細節</summary>

在 `onError` 中，僅使用 `error.message` 顯示錯誤，但 API 可能回傳更詳細的錯誤資訊（例如 404 時的 `detail` 欄位）。這會讓使用者難以理解失敗原因。

建議檢查 error 物件是否包含 API 回傳的資料，並顯示更具體的訊息。

**判斷依據**：diff 中的錯誤處理僅使用 `error.message`，未考慮 API 錯誤結構。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7846 (cache hit 7808) ｜ completion tokens 632 ｜ PR #13</sub>