<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 重新設計了評論管理列表的版面，將原本的多欄表格改為單一主欄位整合作者、文章、時間與操作，並加入文章特色圖片。主要風險在於 `dangerouslySetInnerHTML` 渲染評論 HTML 時未見新增的消毒處理，若後端未徹底淨化，可能造成儲存型 XSS；此外，`CommentContent` 的 `useEffect` 依賴陣列為空，可能導致內容變更時截斷判斷不更新。建議先確認評論內容的消毒流程，並修正 effect 依賴。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容，存在 XSS 風險 | 0.75 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空，可能導致截斷判斷不更新 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:112` | 評論內容未針對隱藏狀態進行視覺降級以外的處理 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容，存在 XSS 風險</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接插入 `item.html`。若評論內容未在後端或前端進行徹底消毒，攻擊者可注入惡意腳本，造成儲存型 XSS。請確認 `item.html` 的來源已通過嚴格的白名單消毒（例如使用 DOMPurify），或改以安全的 HTML 渲染方式。

**判斷依據**：diff 中新增的 `CommentContent` 元件直接使用 `dangerouslySetInnerHTML`，且未見任何消毒處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空，可能導致截斷判斷不更新</summary>

`CommentContent` 的 `useEffect` 僅在掛載時執行一次，若 `item.html` 內容在之後更新（例如從 API 重新取得），`isClamped` 狀態不會重新計算，可能導致「Show more」按鈕顯示錯誤。建議將 `item.html` 加入依賴陣列，或改用 `useLayoutEffect` 並監聽內容變化。

**判斷依據**：diff 中 `useEffect` 的依賴陣列為 `[]`，但內部使用了 `item.html` 相關的 DOM 元素。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:112</code> 評論內容未針對隱藏狀態進行視覺降級以外的處理</summary>

當評論狀態為 `hidden` 時，僅透過 CSS 類別 `text-muted-foreground` 降低文字對比，但內容仍完整顯示。若隱藏評論的目的是防止一般使用者看到，此處可能洩漏內容。請確認產品需求是否允許管理員在列表中看到隱藏評論的全文，或應改為模糊處理。

**判斷依據**：diff 中 `CommentContent` 的 className 僅在 `hidden` 時加入 `text-muted-foreground`，未隱藏內容。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11228 (cache hit 11136) ｜ completion tokens 992 ｜ PR #4</sub>