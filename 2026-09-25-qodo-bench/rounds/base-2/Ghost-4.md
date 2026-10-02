<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 重新設計了評論管理列表的版面，將原本的多欄表格改為單一主欄位整合作者、文章、日期與內容，並新增文章特色圖片縮圖。後端在 comments API 的 post 序列化中加入了 feature_image 欄位，並更新了相關測試快照。主要風險在於前端使用 dangerouslySetInnerHTML 渲染評論 HTML，若後端未徹底消毒，可能造成 XSS；此外，CommentContent 元件在內容變更時不會重新計算是否被截斷，可能導致「Show more」按鈕顯示不正確。整體而言，功能改動合理，但需確認 XSS 防護與元件狀態同步。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:110` | 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS | 0.80 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | CommentContent 的截斷偵測不會在內容變更時重新計算 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:110</code> 使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS</summary>

此處直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`。若後端在儲存評論時未對 HTML 進行嚴格消毒（例如允許 `<script>` 或事件屬性），攻擊者可在評論中注入惡意腳本，當管理員查看評論列表時觸發 XSS。

**建議**：確認後端已使用如 DOMPurify 等函式庫進行消毒，或在前端渲染前先消毒。若後端已消毒，請在程式碼中註明並確保涵蓋所有可能路徑。

**判斷依據**：diff 中新增的 `CommentContent` 元件使用了 `dangerouslySetInnerHTML`，且 `item.html` 來自 API 回應，屬於使用者可控內容。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> CommentContent 的截斷偵測不會在內容變更時重新計算</summary>

`useEffect` 的依賴陣列為空，僅在掛載時執行一次。若 `item.html` 在元件生命週期內發生變化（例如從 API 取得更新），`isClamped` 不會重新計算，可能導致「Show more」按鈕顯示錯誤。

**建議**：將 `item.html` 加入依賴陣列，或在內容更新時觸發重新檢查。

**判斷依據**：diff 中新增的 `CommentContent` 元件，其 `useEffect` 依賴陣列為空，但使用了 `item.html`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8995 (cache hit 8960) ｜ completion tokens 780 ｜ PR #4</sub>