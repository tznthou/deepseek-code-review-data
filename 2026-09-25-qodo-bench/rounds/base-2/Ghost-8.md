<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 zh 語系的翻譯從台灣用語改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除檔案可能導致程式碼中引用該檔案時出現錯誤，以及翻譯變更可能影響既有使用者的理解。建議確認 comments.json 是否確實不再需要，並檢查所有翻譯變更的上下文。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致引用錯誤 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:9` | 翻譯遺漏變數 {newsletterName} | 0.60 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:117` | 「Name」翻譯不一致 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致引用錯誤</summary>

此 PR 刪除了整個 comments.json 檔案。如果程式碼中有任何地方載入此檔案（例如 i18n 載入器），刪除後會導致執行時期錯誤或缺少翻譯。請確認此檔案確實不再被使用，或提供替代方案。

**判斷依據**：diff 中顯示整個檔案被刪除（deleted file mode 100644），且沒有新增替代檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯遺漏變數 {newsletterName}</summary>

翻譯中移除了 {newsletterName} 變數，但原文仍包含該變數。這可能導致使用者看不到具體的新聞信名稱，影響理解。建議保留變數。

**判斷依據**：原文包含 {newsletterName}，但翻譯中沒有對應的變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:117</code> 「Name」翻譯不一致</summary>

在 portal.json 中，「Name」被改為「名稱」，但在 ghost.json 中仍為「名字」。這可能導致不同頁面顯示不一致。建議統一。

**判斷依據**：diff 中 portal.json 的「Name」從「名字」改為「名稱」，但 ghost.json 的「Name」仍為「名字」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6345 (cache hit 6272) ｜ completion tokens 620 ｜ PR #8</sub>