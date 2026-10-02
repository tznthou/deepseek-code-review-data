<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件與對應的測試、Storybook 範例，並將編輯路由從佔位內容改為實際表單。整體結構清楚，測試涵蓋了主要互動流程。主要風險在於表單提交時未處理 description 為 undefined 的情況（可能導致 API 收到 undefined 而非 null），以及測試中對 mock 函式的型別斷言可能隱藏真實型別問題。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42` | description 為 undefined 時可能傳送 undefined 而非 null | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158` | 測試中對 mock 函式參數的型別斷言可能隱藏真實型別問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42</code> description 為 undefined 時可能傳送 undefined 而非 null</summary>

在 handleSubmit 中，`trimmedDescription` 的計算為 `data.description?.trim()`。若使用者未輸入任何內容且欄位為空，`data.description` 可能為 `undefined`（取決於 schema 定義），此時 `trimmedDescription` 為 `undefined`，條件 `trimmedDescription === ""` 為 false，因此 `description` 會被設為 `undefined` 而非 `null`。這可能導致 API 收到 `undefined`，而非預期的 `null`，造成資料不一致。

建議：明確處理 `undefined` 情況，例如：
```ts
const trimmedDescription = data.description?.trim();
const description = trimmedDescription ? trimmedDescription : null;
```
或調整 schema 使 `description` 預設為空字串。

**判斷依據**：diff 中新增的 handleSubmit 函式內，該行直接使用 optional chaining，未處理 undefined 結果。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158</code> 測試中對 mock 函式參數的型別斷言可能隱藏真實型別問題</summary>

在測試「handles empty concurrency limit as null」中，使用 `const callArgs = mockUpdateWorkPool.mock.calls[0] as [{ name: string; workPool: { concurrency_limit: number | null } }, UpdateWorkPoolOptions];` 進行型別斷言。若實際呼叫的參數型別與斷言不符，測試仍會通過，但可能掩蓋了元件中傳遞錯誤型別的問題。建議改用 `expect.objectContaining` 或直接檢查特定屬性，避免過度斷言。

**判斷依據**：測試檔案中該行使用型別斷言，可能導致型別錯誤未被偵測。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8463 (cache hit 7680) ｜ completion tokens 731 ｜ PR #13</sub>