<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將中文翻譯從台灣用語改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除檔案可能導致引用該檔案的程式碼出現問題，以及翻譯變更可能影響使用者體驗。建議確認 comments.json 是否確實不再需要，並檢查是否有其他檔案引用其內容。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致引用錯誤 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:9` | 翻譯遺漏變數 {newsletterName} | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致引用錯誤</summary>

此 PR 刪除了整個 comments.json 檔案。如果程式碼或其他翻譯檔案仍引用此檔案中的鍵值，將導致翻譯缺失或錯誤。請確認此檔案是否已不再使用，或是否應保留並更新內容。

**判斷依據**：diff 中顯示整個檔案被刪除（deleted file mode 100644）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯遺漏變數 {newsletterName}</summary>

翻譯中移除了 {newsletterName} 變數，可能導致使用者無法知道是哪個新聞信。建議保留變數以提供完整資訊。

**判斷依據**：diff 中此行將原本包含 {newsletterName} 的翻譯改為不含變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6345 (cache hit 6272) ｜ completion tokens 437 ｜ PR #8</sub>