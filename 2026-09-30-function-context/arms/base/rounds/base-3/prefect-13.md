<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 WorkPoolEditForm 元件，用於編輯工作池的描述與並行限制，並包含 Storybook 與單元測試。整體結構清晰，表單驗證與 API 呼叫整合良好。主要風險在於並行限制的輸入處理：若使用者輸入負數或非整數值，可能導致 API 收到無效資料；此外，表單提交時未處理 description 為 undefined 的情況，可能造成型別不符。建議在 schema 中增加數值範圍與整數驗證，並確認 description 的型別處理。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112` | 並行限制輸入未驗證數值範圍與整數 | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42` | description 可能為 undefined 導致型別不符 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112</code> 並行限制輸入未驗證數值範圍與整數</summary>

在 `onChange` 中直接將輸入轉為 `Number(value)`，但未檢查是否為負數、非整數或超出合理範圍。若使用者輸入 `-5` 或 `2.5`，表單會通過驗證並將無效值傳送給 API，可能導致後端錯誤或非預期行為。建議在 zod schema 中增加 `.int().nonnegative()` 驗證，或在此處進行檢查。

**判斷依據**：diff 中新增的 `onChange` 處理直接將字串轉為數字，未見任何範圍或整數驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42</code> description 可能為 undefined 導致型別不符</summary>

在 `handleSubmit` 中，`data.description?.trim()` 的結果可能為 `undefined`，但後續將 `trimmedDescription === "" ? null : trimmedDescription` 指派給 `description`。若 `data.description` 為 `undefined`，則 `trimmedDescription` 為 `undefined`，最終 `description` 會是 `undefined`，但 `WorkPoolUpdate` 型別可能預期 `string | null`。建議明確處理 `undefined` 情況，例如使用 `data.description?.trim() ?? null`。

**判斷依據**：diff 中 `trimmedDescription` 可能為 `undefined`，且未見對 `undefined` 的明確處理。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7761 (cache hit 7680) ｜ completion tokens 697 ｜ PR #13</sub>