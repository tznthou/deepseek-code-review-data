<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案重新命名為 kebab-case，並加入 ESLint 規則強制執行。同時包含一些功能性變更：移除 minimal 模式下的 setLoading(false)、在提交時對 email 進行 trim、調整 getUrlHistory 的回傳邏輯，以及版本號更新。整體風險中等，需特別注意移除 setLoading(false) 可能導致的 UI 狀態不一致，以及 getUrlHistory 回傳型別改變可能造成的問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-page.tsx:29` | 移除 setLoading(false) 可能導致 loading 狀態卡住 | 0.80 |
| ⚠️ | Major | `apps/signup-form/src/utils/helpers.tsx:45` | getUrlHistory 回傳型別可能變為 undefined | 0.70 |
| 🔸 | Minor | `apps/signup-form/src/components/pages/form-view.tsx:56` | email trim 可能改變原本行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-page.tsx:29</code> 移除 setLoading(false) 可能導致 loading 狀態卡住</summary>

在 minimal 模式下，成功送出表單後原本會呼叫 setLoading(false) 來結束載入狀態，但此 PR 移除了該呼叫。若 submit 函式在成功後沒有在其他地方將 loading 設為 false，UI 可能會永遠顯示載入中。請確認 submit 函式的實作，或保留此呼叫。

**判斷依據**：diff 中刪除了 `setLoading(false);` 這一行，且上下文顯示在 `setSuccess(true);` 之後。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/utils/helpers.tsx:45</code> getUrlHistory 回傳型別可能變為 undefined</summary>

原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但修改後直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，此函式現在會回傳 undefined，可能導致呼叫端出現錯誤。請確認呼叫端是否能處理 undefined，或保留原本的條件判斷。

**判斷依據**：diff 中刪除了 `if (history) { return history; }` 的條件判斷，改為直接回傳。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email trim 可能改變原本行為</summary>

在提交時對 email 進行 trim 是合理的，但需確認後端是否已處理 trim，以及是否會影響其他依賴原始輸入的邏輯。

**判斷依據**：diff 中將 `onSubmit({email});` 改為 `onSubmit({email: email.trim()});`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6293 (cache hit 6272) ｜ completion tokens 669 ｜ PR #5</sub>