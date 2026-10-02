<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案命名改為 kebab-case，並加入 ESLint 規則強制執行。同時包含一些功能性變更：移除 minimal 模式下的 setLoading(false)、email 輸入 trim、getUrlHistory 回傳型別變更、版本號更新與 README 新增發佈說明。主要風險在於 getUrlHistory 的回傳型別從 URLHistory | undefined 改為 URLHistory，可能導致呼叫端未處理 undefined 而發生執行時期錯誤；另外移除 setLoading(false) 可能造成 loading 狀態卡住。建議先確認這些變更的影響範圍。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/utils/helpers.tsx:44` | getUrlHistory 回傳型別變更可能導致呼叫端未處理 undefined 而發生錯誤 | 0.80 |
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-page.tsx:29` | 移除 setLoading(false) 可能導致 loading 狀態無法正確重設 | 0.70 |
| 🔸 | Minor | `apps/signup-form/src/components/pages/form-view.tsx:56` | email trim 可能改變原本行為，需確認是否符合預期 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/utils/helpers.tsx:44</code> getUrlHistory 回傳型別變更可能導致呼叫端未處理 undefined 而發生錯誤</summary>

原本的程式碼在 `history` 為 falsy 時會回傳 `undefined`，但修改後直接回傳 `history`，型別從 `URLHistory | undefined` 變成 `URLHistory`。如果呼叫端沒有處理 `undefined` 的情況，可能會在執行時期嘗試存取 `history` 的屬性而拋出錯誤。建議確認所有呼叫端是否都有正確處理 `undefined`，或保留原本的條件判斷。

**判斷依據**：diff 中刪除了 `if (history) { return history; }` 的條件判斷，直接回傳 `history`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-page.tsx:29</code> 移除 setLoading(false) 可能導致 loading 狀態無法正確重設</summary>

在 minimal 模式下，成功送出表單後原本會呼叫 `setLoading(false)` 來重設 loading 狀態，但此 PR 移除了這一行。如果 `setLoading(false)` 是必要的，移除後可能導致 UI 一直顯示 loading 狀態。建議確認 minimal 模式下的狀態管理邏輯，若需要重設 loading 則應保留。

**判斷依據**：diff 中刪除了 `setLoading(false);` 這一行。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email trim 可能改變原本行為，需確認是否符合預期</summary>

在 submitHandler 中將 email 加上 `.trim()`，這會移除前後空白。如果原本的驗證邏輯允許前後空白，這可能改變行為。建議確認 email 驗證邏輯是否已處理 trim，或此變更是否為預期。

**判斷依據**：diff 中將 `onSubmit({email});` 改為 `onSubmit({email: email.trim()});`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6293 (cache hit 6272) ｜ completion tokens 769 ｜ PR #5</sub>