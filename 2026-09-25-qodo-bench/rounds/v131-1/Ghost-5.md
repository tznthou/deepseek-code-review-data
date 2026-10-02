<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案名稱改為 kebab-case，並加入 ESLint 規則強制執行。同時包含一些功能性變更：移除 minimal 模式下的 setLoading(false)、在提交時對 email 進行 trim、調整 getUrlHistory 的回傳邏輯、更新 README 與版本號。整體風險中等，需注意 email trim 可能影響既有驗證邏輯，以及 getUrlHistory 的回傳型別變更可能造成呼叫端問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-view.tsx:56` | email.trim() 可能導致驗證邏輯不一致 | 0.80 |
| ⚠️ | Major | `apps/signup-form/src/utils/helpers.tsx:45` | getUrlHistory 可能回傳 undefined，與宣告型別不符 | 0.70 |
| 🔸 | Minor | `apps/signup-form/src/components/pages/form-page.tsx:29` | 移除 minimal 模式下的 setLoading(false) 可能導致 UI 卡在載入狀態 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email.trim() 可能導致驗證邏輯不一致</summary>

在 submitHandler 中將 email 先 trim 再傳給 onSubmit，但上游的驗證（如 isValidEmail）可能是在未 trim 的狀態下進行。若使用者輸入前後有空白，驗證可能通過（例如 isValidEmail 自行 trim）或失敗（若未 trim），但最終送出的 email 已被 trim，可能造成行為不一致。建議確認 isValidEmail 的實作，並在驗證前統一 trim。

**判斷依據**：diff 中此行由 onSubmit({email}); 改為 onSubmit({email: email.trim()});，但未見對應的驗證邏輯調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/utils/helpers.tsx:45</code> getUrlHistory 可能回傳 undefined，與宣告型別不符</summary>

函式宣告回傳 URLHistory，但修改後直接回傳 getDefaultUrlHistory() 的結果，而該函式可能回傳 undefined（例如 sessionStorage 中無資料或 JSON 解析失敗）。這可能導致呼叫端在未檢查的情況下存取屬性而拋出錯誤。建議保留原本的條件判斷，或明確處理 undefined 的情況。

**判斷依據**：diff 中移除了 if (history) { return history; } 的條件，直接回傳 history，但 getDefaultUrlHistory 的回傳型別可能包含 undefined。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/components/pages/form-page.tsx:29</code> 移除 minimal 模式下的 setLoading(false) 可能導致 UI 卡在載入狀態</summary>

在 minimal 模式且訂閱成功時，原本會呼叫 setLoading(false) 來結束載入狀態，但此 PR 移除了該行。若後續沒有其他機制將 loading 設為 false，按鈕可能持續顯示載入中。需確認成功狀態是否會自動重置 loading，否則應保留此行。

**判斷依據**：diff 中刪除了 setLoading(false); 這一行，但未見其他設定 loading 為 false 的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6257 (cache hit 1408) ｜ completion tokens 761 ｜ PR #5</sub>