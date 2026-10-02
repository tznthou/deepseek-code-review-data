<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了評論管理清單的版面，將原本的表格欄位整合為單一欄位，並加入作者、文章、時間等資訊的內嵌顯示，同時新增文章特色圖片欄位。主要風險在於 `CommentContent` 元件使用 `dangerouslySetInnerHTML` 渲染評論內容，若評論內容未經適當消毒，可能導致 XSS 攻擊。此外，`useEffect` 中的 resize 事件監聽器未依賴 `item.html`，可能導致內容變更時判斷不準確。建議優先確認評論內容的消毒機制，並修正 effect 的依賴陣列。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列缺少 item.html，可能導致判斷不準確 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行適當消毒，攻擊者可注入惡意腳本，導致儲存型 XSS 攻擊。請確認 `item.html` 的來源已受信任且經過消毒（例如使用 DOMPurify），或改用安全的渲染方式。

**判斷依據**：diff 中新增的 `CommentContent` 元件包含此行，且未見任何消毒處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列缺少 item.html，可能導致判斷不準確</summary>

`useEffect` 僅在掛載時執行一次，但 `item.html` 可能因資料更新而改變。若內容變更，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示與否不正確。建議將 `item.html` 加入依賴陣列，或在內容變更時重新檢查。

**判斷依據**：依賴陣列為空，但函式內使用 `contentRef.current`，其內容可能隨 `item.html` 改變。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8995 (cache hit 1536) ｜ completion tokens 697 ｜ PR #4</sub>