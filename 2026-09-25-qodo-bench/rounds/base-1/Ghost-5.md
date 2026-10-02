<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案重新命名為 kebab-case，並加入 ESLint 規則強制執行。同時包含一些功能性變更：移除 minimal 模式下的 setLoading(false)、在提交時對 email 進行 trim、簡化 getUrlHistory 的回傳邏輯，以及更新 README 與版本號。整體風險中等，需注意移除 setLoading(false) 可能導致 UI 卡在 loading 狀態，以及 getUrlHistory 的簡化可能改變行為。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-page.tsx:29` | 移除 setLoading(false) 可能導致 minimal 模式永遠顯示 loading 狀態 | 0.80 |
| ⚠️ | Major | `apps/signup-form/src/utils/helpers.tsx:45` | getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符 | 0.70 |
| 🔸 | Minor | `apps/signup-form/src/components/pages/form-view.tsx:56` | email.trim() 可能改變原本的驗證行為 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-page.tsx:29</code> 移除 setLoading(false) 可能導致 minimal 模式永遠顯示 loading 狀態</summary>

在 minimal 模式下，送出成功後原本會呼叫 setLoading(false) 來停止 loading 動畫，但此 PR 移除了該行。若 loading 狀態沒有在其他地方被重設，使用者會看到無限的 loading 指示。請確認是否有其他機制（例如元件 unmount 或 effect）會重設 loading，否則應保留此行。

**判斷依據**：diff 中刪除了 `setLoading(false);` 這一行，且未見其他重設 loading 的程式碼。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/utils/helpers.tsx:45</code> getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符</summary>

原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

**判斷依據**：diff 中刪除了 `if (history) { return history; }` 的條件判斷，直接回傳 history。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email.trim() 可能改變原本的驗證行為</summary>

在提交時對 email 進行 trim 是合理的，但需確認驗證邏輯（isValidEmail）是否也應該使用 trim 後的值，否則可能出現前後不一致。例如使用者輸入前後有空白的 email，驗證可能通過但提交的是 trim 後的值，或反之。

**判斷依據**：diff 中將 `onSubmit({email})` 改為 `onSubmit({email: email.trim()})`，但未見驗證邏輯同步修改。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6293 (cache hit 1536) ｜ completion tokens 732 ｜ PR #5</sub>