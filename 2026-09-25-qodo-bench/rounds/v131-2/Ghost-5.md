<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案命名改為 kebab-case，並加入 ESLint 規則強制執行。同時包含一些功能性變更：移除 minimal 模式下的 setLoading(false)、email 輸入 trim、getUrlHistory 回傳型別變更、版本號更新與 README 新增發布流程。整體風險中等，需注意 getUrlHistory 的回傳型別變更可能導致呼叫端型別錯誤，以及移除 setLoading(false) 可能造成 UI 狀態不一致。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/utils/helpers.tsx:45` | getUrlHistory 回傳型別從 URLHistory \| undefined 改為 URLHistory，可能導致呼叫端型別錯誤 | 0.80 |
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-page.tsx:29` | 移除 minimal 模式下的 setLoading(false) 可能導致 UI 狀態不一致 | 0.70 |
| 🔸 | Minor | `apps/signup-form/src/components/pages/form-view.tsx:56` | email 輸入 trim 可能改變既有行為，需確認是否為預期 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/utils/helpers.tsx:45</code> getUrlHistory 回傳型別從 URLHistory | undefined 改為 URLHistory，可能導致呼叫端型別錯誤</summary>

原本的程式碼在 history 為 falsy 時會回傳 undefined，現在直接回傳 history，但函式簽章仍為 `URLHistory`。如果 `getDefaultUrlHistory()` 回傳 `undefined`（例如 sessionStorage 中沒有資料），此函式會回傳 `undefined`，與宣告的型別不符。呼叫端若未處理 undefined，可能導致執行時期錯誤。建議確認 `getDefaultUrlHistory` 是否可能回傳 undefined，並調整型別或保留原本的條件判斷。

**判斷依據**：diff 中刪除了原本的 `if (history) { return history; }` 條件，改為直接 `return history;`，但函式簽章仍為 `URLHistory`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-page.tsx:29</code> 移除 minimal 模式下的 setLoading(false) 可能導致 UI 狀態不一致</summary>

在 minimal 模式下，送出成功後原本會呼叫 `setLoading(false)` 來停止載入狀態，但此 PR 移除了該行。如果 `setLoading(false)` 是必要的，移除後可能導致按鈕持續顯示載入中，或無法再次送出。建議確認 minimal 模式的 UI 流程，若需要停止載入，應保留該行。

**判斷依據**：diff 中刪除了 `setLoading(false);` 這一行，但未見其他替代處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email 輸入 trim 可能改變既有行為，需確認是否為預期</summary>

在 submitHandler 中，將 `onSubmit({email})` 改為 `onSubmit({email: email.trim()})`。這會移除使用者輸入前後的空白，可能影響驗證或後端處理。若原本允許空白（例如作為密碼的一部分），此變更可能造成問題。建議確認 email 欄位的驗證邏輯，並確保 trim 是預期行為。

**判斷依據**：diff 中將 `onSubmit({email})` 改為 `onSubmit({email: email.trim()})`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6257 (cache hit 6144) ｜ completion tokens 810 ｜ PR #5</sub>