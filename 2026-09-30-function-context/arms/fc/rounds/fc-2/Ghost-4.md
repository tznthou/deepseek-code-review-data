<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了管理後台的留言審核列表，將原本的表格欄位改為單一欄位整合顯示作者、時間、文章與內容，並新增文章特色圖片欄位。主要風險在於：1) 使用 dangerouslySetInnerHTML 渲染留言內容，若後端未徹底消毒，可能造成 XSS；2) 新增的 feature_image 欄位直接以 img src 載入，未驗證來源，可能造成追蹤或安全風險；3) 前端 useEffect 依賴空陣列，可能無法正確偵測內容截斷狀態；4) 部分互動元素（如作者名稱）改為按鈕後，可能影響無障礙與鍵盤操作。建議優先確認後端 HTML 消毒機制，並對 feature_image 來源進行驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染留言內容可能導致 XSS | 0.80 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:260` | feature_image 來源未驗證，可能造成追蹤或安全風險 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空，可能無法正確偵測內容截斷 | 0.60 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:120` | 作者名稱改為按鈕後可能影響無障礙與鍵盤操作 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染留言內容可能導致 XSS</summary>

此處直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`，若後端未對留言內容進行完整的 HTML 消毒（例如移除 script 標籤、事件處理器、javascript: 連結等），攻擊者可能注入惡意腳本，在管理員瀏覽器執行。建議確認後端在儲存留言時已使用嚴格的 sanitizer（如 DOMPurify），或在前端渲染前進行消毒。

**判斷依據**：diff 中新增的 CommentContent 元件內使用 dangerouslySetInnerHTML，且 item.html 來自 API，未見任何消毒處理。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:260</code> feature_image 來源未驗證，可能造成追蹤或安全風險</summary>

新增的 `feature_image` 直接以 `<img src={item.post.feature_image} />` 載入，若該 URL 為外部資源，可能洩漏管理員 IP 或觸發追蹤像素。此外，若 URL 為 `data:` 或 `javascript:` 等 scheme，可能造成 XSS。建議限制僅允許同源或受信任的圖片來源，或使用 CSP 限制圖片來源。

**判斷依據**：diff 中新增的 img 標籤直接使用 item.post.feature_image，未見任何來源驗證。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空，可能無法正確偵測內容截斷</summary>

`useEffect` 僅在元件掛載時執行一次，若 `item.html` 內容在掛載後發生變化（例如虛擬滾動重用元件），`isClamped` 狀態可能不會更新。建議將 `item.html` 加入依賴陣列，或在內容更新時重新檢查。

**判斷依據**：useEffect 依賴陣列為空，但元件可能因虛擬滾動而重用，item.html 可能改變。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:120</code> 作者名稱改為按鈕後可能影響無障礙與鍵盤操作</summary>

原本的作者名稱是連結，現在改為按鈕並加上 onClick 過濾功能。按鈕的語意與連結不同，可能影響螢幕讀報器使用者的體驗。建議確認按鈕具有適當的 aria-label，並確保鍵盤操作正常。

**判斷依據**：diff 中將原本的 <a> 改為 <Button>，但未見 aria-label 或 title 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9502 (cache hit 9472) ｜ completion tokens 1272 ｜ PR #4</sub>