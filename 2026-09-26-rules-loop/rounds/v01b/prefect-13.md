<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件，用於編輯 work pool 的 description 與 concurrency limit，並整合了路由、API hook、測試與 Storybook。整體結構清晰，測試覆蓋良好，但存在一個潛在的型別安全問題：concurrency limit 輸入可能產生 NaN，且未在 schema 中驗證，可能導致 API 收到無效值。此外，測試中對 mock 的型別斷言可能不準確，但影響輕微。建議先修正 NaN 驗證問題再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | concurrency limit 輸入可能產生 NaN 並提交至 API | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158` | 測試中 mock 呼叫參數的型別斷言可能不準確 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> concurrency limit 輸入可能產生 NaN 並提交至 API</summary>

在 `onChange` 處理中，當輸入為空字串時設為 `null`，否則使用 `Number(value)`。若使用者輸入非數字字元（例如 'e'、'-'、'.'），`Number(value)` 會回傳 `NaN`。`NaN` 會被存入表單狀態，且 zod schema 未驗證此欄位（可能僅為 nullable number），因此 `NaN` 可能被提交至 API，導致後端驗證錯誤或資料不一致。

建議在 schema 中增加 `.refine((val) => val === null || !Number.isNaN(val), { message: "必須是有效數字" })`，或在 `onChange` 中檢查 `Number.isNaN` 並設為 `null`。

**判斷依據**：diff 中新增的 `onChange` 處理直接將 `Number(value)` 的結果傳給 `field.onChange`，未檢查 `NaN`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158</code> 測試中 mock 呼叫參數的型別斷言可能不準確</summary>

在 `handles empty concurrency limit as null` 測試中，使用 `as` 斷言將 `mockUpdateWorkPool.mock.calls[0]` 轉型為特定型別，但實際呼叫參數可能包含其他欄位（如 `description`），此斷言可能過於嚴格或誤導。建議使用更精確的型別或直接檢查所需屬性。

**判斷依據**：diff 中新增的測試使用了型別斷言，但未驗證實際物件結構是否完全符合。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9256 (cache hit 9216) ｜ completion tokens 771 ｜ PR #13</sub>