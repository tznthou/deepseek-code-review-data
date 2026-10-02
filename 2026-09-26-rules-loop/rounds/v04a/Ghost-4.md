<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 重新設計了評論管理列表的版面，將原本的多欄表格改為單一欄位整合顯示作者、日期、文章與內容，並加入文章特色圖片。後端新增回傳 post.feature_image。整體方向合理，但存在幾個需要修正的問題：CommentContent 的 clamp 偵測在內容動態載入或字型載入後可能失效；formatDate 的正規表達式可能誤刪日期中的逗號；onAddFilter 改為必填但呼叫端未同步更新，可能導致執行時期錯誤；此外有數個 React 與程式碼風格違規（缺少 key、按鈕 type、單引號、縮排）。建議修正後再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:92` | CommentContent 的 clamp 偵測可能因內容動態載入或字型載入而失效 | 0.80 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:69` | formatDate 的正規表達式可能誤刪日期中的逗號 | 0.75 |
| ⚠️ | Major | `apps/posts/src/views/comments/components/comments-list.tsx:135` | onAddFilter 改為必填但呼叫端未同步更新，可能導致執行時期錯誤 | 0.70 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:185` | [R14] 列表渲染缺少 key prop | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:198` | [R13] Button 缺少 type 屬性 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | [R18] 使用雙引號而非單引號 | 0.90 |
| 🔸 | Minor | `apps/posts/src/views/comments/components/comments-list.tsx:92` | [R17] 縮排不一致 | 0.90 |

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> CommentContent 的 clamp 偵測可能因內容動態載入或字型載入而失效</summary>

useEffect 僅在元件掛載時執行一次，且依賴陣列為空。若 item.html 內容在掛載後才更新（例如從非同步來源取得），或網頁字型在掛載後才載入完成，scrollHeight 與 clientHeight 的比較結果可能不準確，導致「Show more」按鈕錯誤顯示或隱藏。建議將 item.html 加入依賴陣列，並監聽字型載入事件（如 document.fonts.ready）後重新檢查。

**判斷依據**：useEffect 依賴陣列為空，且未處理字型載入或內容更新。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:69</code> formatDate 的正規表達式可能誤刪日期中的逗號</summary>

正規表達式 /(\d+),(\s+\d{4})/ 會將「Dec 17, 2025」中的逗號移除，但若日期格式因 locale 或瀏覽器實作不同而產生其他逗號位置（例如「December 17, 2025」），可能無法正確處理。建議改用更精確的格式化選項，或使用 toLocaleString 的選項來避免依賴字串取代。

**判斷依據**：正規表達式假設逗號僅出現在日與年之間，但實際格式可能因 locale 而異。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:135</code> onAddFilter 改為必填但呼叫端未同步更新，可能導致執行時期錯誤</summary>

原本 onAddFilter 是選用參數，此 PR 將其改為必填，但未檢查所有呼叫 CommentsList 的地方是否都有傳入此 prop。若某處未傳入，執行到 onClick 時會因為 onAddFilter 為 undefined 而拋出錯誤。建議保留選用或確保所有呼叫端都已更新。

**判斷依據**：型別從選用改為必填，但 diff 中未顯示呼叫端更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:185</code> [R14] 列表渲染缺少 key prop</summary>

在 map 渲染中，TableRow 或其子元件未提供 key prop。React 需要 key 來正確管理列表項目的狀態與效能。請為每個項目加入穩定的 key，例如 item.id。

**判斷依據**：diff 中未見 key 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:198</code> [R13] Button 缺少 type 屬性</summary>

多個 Button 元件未指定 type 屬性。在表單中可能意外觸發提交。請為所有按鈕加上 type="button"（或適當的 type）。

**判斷依據**：Button 元件未見 type 屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> [R18] 使用雙引號而非單引號</summary>

程式碼中多處使用雙引號，但專案規範要求使用單引號。請將字串改為單引號。

**判斷依據**：字串使用雙引號。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/posts/src/views/comments/components/comments-list.tsx:92</code> [R17] 縮排不一致</summary>

部分程式碼縮排為 2 格，但專案規範要求 4 格。請調整縮排。

**判斷依據**：縮排為 2 格。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10184 (cache hit 8960) ｜ completion tokens 1840 ｜ PR #4</sub>