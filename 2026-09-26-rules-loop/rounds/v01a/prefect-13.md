<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了 WorkPoolEditForm 元件與對應的測試、Storybook stories，並將編輯頁面路由接上表單。整體結構清晰，測試覆蓋了主要互動流程。主要風險在於表單提交時對 description 的 trim 處理可能造成非預期的 null 值，以及測試中對 mock 函式的型別斷言可能隱藏型別錯誤。建議先修正 description 的處理邏輯，並確認測試的型別安全。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42` | description 欄位 trim 後可能將有意義的空白字串轉為 null | 0.80 |
| 🔸 | Minor | `ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158` | 測試中對 mockUpdateWorkPool 的型別斷言可能隱藏型別錯誤 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42</code> description 欄位 trim 後可能將有意義的空白字串轉為 null</summary>

在 handleSubmit 中，`trimmedDescription === "" ? null : trimmedDescription` 會將僅包含空白的 description 轉為 null。若使用者原本 description 為 null，但輸入空白後送出，會將 null 改為 null（無影響）；但若原本 description 為有意義的空白字串（例如多個空格），送出後會被轉為 null，可能非使用者預期。建議保留原始值，或僅在空字串時轉為 null，而非 trim 後判斷。

**判斷依據**：diff 中新增的 handleSubmit 函式，第 42-47 行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/work-pools/edit/work-pool-edit-form.test.tsx:158</code> 測試中對 mockUpdateWorkPool 的型別斷言可能隱藏型別錯誤</summary>

在測試中，`mockUpdateWorkPool.mock.calls[0]` 被斷言為特定型別，但若實際呼叫參數型別不符，測試仍可能通過，因為斷言僅在執行時期檢查。建議使用更精確的型別定義或直接使用 `expect.objectContaining` 進行比對，以確保型別安全。

**判斷依據**：diff 中測試檔案第 137-140 行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9256 (cache hit 7680) ｜ completion tokens 671 ｜ PR #13</sub>