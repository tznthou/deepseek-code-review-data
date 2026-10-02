<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 重新設計了評論管理列表的版面，將原本的多欄位表格改為單一欄位整合顯示作者、時間、文章與評論內容，並加入文章特色圖片、展開/收起功能與計數圖示。主要風險在於 `CommentContent` 元件使用 `dangerouslySetInnerHTML` 渲染評論 HTML，若評論內容未經充分消毒，可能導致 XSS 漏洞；此外，`useEffect` 僅在掛載時執行一次，當評論內容動態更新或視窗大小改變時，可能無法正確判斷是否需要顯示展開按鈕。整體而言，程式碼結構清晰，但需優先處理 XSS 風險與 clamp 偵測的可靠性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.90 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空，無法偵測內容變化 | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:90` | 展開狀態未在內容更新時重設 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

`CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行充分的 HTML 消毒，攻擊者可能注入惡意腳本，導致儲存型 XSS 攻擊。請確認 `item.html` 的來源已透過如 DOMPurify 等函式庫消毒，或改用安全的渲染方式（例如使用 React 元件解析並過濾標籤）。

**判斷依據**：diff 中新增的 `CommentContent` 元件包含此行，且未見任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空，無法偵測內容變化</summary>

`useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如評論被編輯或從 API 重新取得）。若內容高度改變，`isClamped` 狀態不會重新計算，導致展開按鈕顯示不正確。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監聽內容變化。

**判斷依據**：依賴陣列為空，且未使用 ResizeObserver 或 MutationObserver。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:90</code> 展開狀態未在內容更新時重設</summary>

當 `item.html` 更新時，`isExpanded` 狀態可能保留為 true，導致新內容自動展開。若希望內容更新後回到收合狀態，應在 `useEffect` 中重設 `isExpanded`。

**判斷依據**：狀態未與 `item.html` 同步。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8959 (cache hit 8832) ｜ completion tokens 889 ｜ PR #4</sub>