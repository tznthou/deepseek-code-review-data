<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 應用程式的檔案命名改為 kebab-case，並包含一些程式碼變更：移除 minimal 模式下的 setLoading(false)、在提交時對 email 進行 trim、簡化 getUrlHistory 的回傳邏輯、更新 ESLint 規則與 README。整體風險中等，需注意移除 setLoading(false) 可能導致 loading 狀態卡住，以及 email trim 未同步更新驗證邏輯可能造成不一致。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-page.tsx:29` | 移除 setLoading(false) 可能導致 loading 狀態卡住 | 0.80 |
| 🔸 | Minor | `apps/signup-form/src/components/pages/form-view.tsx:56` | email trim 未同步更新驗證邏輯 | 0.70 |
| 🔸 | Minor | `apps/signup-form/src/utils/helpers.tsx:45` | getUrlHistory 回傳型別可能包含 undefined | 0.60 |
| 🔹 | Nit | `apps/signup-form/src/utils/helpers.tsx:20` | [R18] 字串應使用單引號 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-page.tsx:29</code> 移除 setLoading(false) 可能導致 loading 狀態卡住</summary>

在 minimal 模式下，成功提交後原本會呼叫 setLoading(false) 來停止載入狀態，但此 PR 移除了該呼叫。若 submit 流程中 loading 狀態被設為 true，且沒有其他機制將其設回 false，則 UI 可能永遠顯示載入中。請確認是否有其他路徑會重設 loading，否則應保留此呼叫。

**判斷依據**：diff 中刪除了 `setLoading(false);` 這一行，且上下文顯示此處為 minimal 模式的成功分支。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email trim 未同步更新驗證邏輯</summary>

提交時對 email 進行 trim，但驗證函式 isValidEmail 可能仍使用未 trim 的值。若使用者輸入前後有空白，驗證可能通過但提交的是 trim 後的值，或驗證失敗但 trim 後其實有效。建議在驗證前也進行 trim，或確認 isValidEmail 內部已處理。

**判斷依據**：diff 中此行將 email.trim() 傳入 onSubmit，但未見對應的驗證邏輯變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/utils/helpers.tsx:45</code> getUrlHistory 回傳型別可能包含 undefined</summary>

原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但現在直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，則此函式可能回傳 undefined，與宣告的回傳型別 URLHistory 不符。請確認呼叫端是否能處理 undefined，或調整型別定義。

**判斷依據**：diff 中刪除了 if (history) 檢查，直接回傳 history。

</details>

<details><summary>🔹 <b>Nit</b> — <code>apps/signup-form/src/utils/helpers.tsx:20</code> [R18] 字串應使用單引號</summary>

此專案規範要求使用單引號，但此處將原本的單引號改為雙引號。請改回單引號以符合規範。

**判斷依據**：diff 中將 'ghost-history' 改為 "ghost-history"，違反 R18。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8602 (cache hit 8576) ｜ completion tokens 863 ｜ PR #5</sub>