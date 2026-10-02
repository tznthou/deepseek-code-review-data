<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 zh 翻譯檔案中的用語改為中國大陸慣用語，並刪除了 comments.json。主要風險在於刪除檔案可能導致翻譯缺失，以及部分翻譯變更可能造成語意不一致。未發現違反 repo 規範。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致翻譯缺失 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:9` | 翻譯變更可能造成語意不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致翻譯缺失</summary>

此 PR 刪除了整個 comments.json 檔案。如果程式碼中仍引用這些翻譯鍵，將導致介面顯示原始英文或出現錯誤。請確認所有引用已移除或改由其他檔案提供。

**判斷依據**：diff 顯示整個檔案被刪除（deleted file mode 100644），且未新增替代檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯變更可能造成語意不一致</summary>

將 "{memberEmail} will no longer receive {newsletterName} newsletter." 的翻譯從「{memberEmail}将不会再收到{newsletterName}的新闻信。」改為「{memberEmail}将不会再收到新闻信。」，移除了 {newsletterName} 變數。這可能導致使用者無法得知是哪一份新聞信，降低資訊清晰度。

**判斷依據**：diff 中此行翻譯移除了 {newsletterName} 佔位符。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8691 (cache hit 8576) ｜ completion tokens 465 ｜ PR #8</sub>