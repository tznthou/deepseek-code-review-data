<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了管理後台的留言審核列表，將原本的多欄表格改為單一主欄位整合作者、時間、文章與留言內容，並新增文章特色圖片欄位。主要風險在於：1) 使用 dangerouslySetInnerHTML 渲染留言 HTML，若後端未徹底消毒，可能造成 XSS；2) 新增的 CommentContent 元件在 useEffect 中依賴空依賴陣列，可能無法正確偵測內容截斷狀態；3) 部分程式碼違反專案規範（如 JSX props 排序、按鈕 type 屬性）。建議優先處理 XSS 風險與 useEffect 依賴問題。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染留言 HTML 可能導致 XSS | 0.80 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | useEffect 依賴陣列為空可能導致截斷偵測失效 | 0.75 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:112` | [R13] Button 元素缺少明確的 type 屬性 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:194` | [R12] JSX props 排序不符合標準順序 | 0.85 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:196` | 使用非空斷言 (!) 可能導致執行時期錯誤 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染留言 HTML 可能導致 XSS</summary>

此處直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`。若後端在儲存留言時未對 HTML 進行嚴格消毒（例如允許 `<script>` 或事件屬性），攻擊者可在留言中注入惡意腳本，當管理員查看留言列表時觸發 XSS。

建議：
- 確認後端在儲存留言時已使用如 DOMPurify 等函式庫進行消毒，並限制允許的標籤與屬性。
- 若無法保證後端消毒，應在前端渲染前再次消毒，或改用安全的渲染方式（如 React 元件組合）。

**判斷依據**：diff 中新增的 CommentContent 元件內使用 dangerouslySetInnerHTML 直接輸出 item.html。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> useEffect 依賴陣列為空可能導致截斷偵測失效</summary>

`useEffect` 的依賴陣列為空，僅在元件掛載時執行一次。若 `item.html` 內容在掛載後發生變化（例如因分頁載入更多資料而更新），`isClamped` 狀態不會重新計算，可能導致「Show more」按鈕顯示不正確。

建議：將 `item.html` 加入依賴陣列，或在內容更新時觸發重新檢查。

**判斷依據**：diff 中新增的 CommentContent 元件內 useEffect 依賴陣列為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:112</code> [R13] Button 元素缺少明確的 type 屬性</summary>

此處的 `<Button>` 元件未指定 `type` 屬性。在表單中，預設 type 為 submit，可能導致非預期的表單提交。建議明確指定 `type="button"`。

**判斷依據**：diff 中新增的 ExpandButton 元件內的 Button 未設定 type 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:194</code> [R12] JSX props 排序不符合標準順序</summary>

此處 `<Button>` 的 props 順序為 `className`, `size`, `variant`, `onClick`，但標準順序應為保留 props、一般 props（字母序）、callbacks、shorthand props。`onClick` 應放在最後。建議調整為 `className`, `size`, `variant`, `onClick` 的順序（目前 onClick 在 variant 之後，但 variant 與 size 皆為一般 props，應按字母序排列，且 onClick 為 callback 應置於最後）。

**判斷依據**：diff 中新增的 Button 元件 props 順序不符合規範。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:196</code> 使用非空斷言 (!) 可能導致執行時期錯誤</summary>

在 `onClick` 中使用 `item.member!.id` 和 `item.post!.id`，但條件判斷已確保存在，理論上安全。然而，若未來條件變更或資料結構變動，非空斷言可能隱藏潛在的 null/undefined 錯誤。建議使用明確的變數或可選串連來避免非空斷言。

**判斷依據**：diff 中多處使用非空斷言。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11304 (cache hit 1536) ｜ completion tokens 1498 ｜ PR #4</sub>