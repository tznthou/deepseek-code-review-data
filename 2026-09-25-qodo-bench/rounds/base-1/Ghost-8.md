<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將繁體中文（zh）翻譯改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除檔案可能導致程式碼引用錯誤或翻譯缺失，以及部分翻譯變更可能造成語意偏差或遺漏變數。建議先確認 comments.json 是否確實不再需要，並修正 portal.json 中遺漏變數的翻譯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/portal.json:9` | 翻譯中遺漏變數 {newsletterName} | 0.90 |
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除整個 comments.json 可能導致翻譯缺失 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:117` | 「Name」翻譯從「名字」改為「名稱」可能造成不一致 | 0.60 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:192` | 「Unsubscribe from all emails」翻譯可能造成語意偏差 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯中遺漏變數 {newsletterName}</summary>

翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

**判斷依據**：diff 中此行將原本包含 `{newsletterName}` 的譯文改為不含該變數的譯文。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除整個 comments.json 可能導致翻譯缺失</summary>

此 PR 刪除了 `ghost/i18n/locales/zh/comments.json` 檔案。如果程式碼中仍有引用此檔案中的翻譯鍵，將導致翻譯缺失或錯誤。請確認此檔案是否已不再使用，或是否應保留並更新內容。

**判斷依據**：diff 顯示整個檔案被刪除，且沒有新增替代檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:117</code> 「Name」翻譯從「名字」改為「名稱」可能造成不一致</summary>

在 portal.json 中，`"Name"` 的翻譯從 `"名字"` 改為 `"名稱"`。但在同檔案的 `"Jamie Larson": "阿宇"` 和 `"jamie@example.com": "ayu@example.com"` 等範例中，可能仍使用「名字」的語境。此外，ghost.json 中 `"Name"` 的翻譯也改為 `"名字"`，可能造成不一致。請確認此變更是否為預期。

**判斷依據**：diff 中此行將 `"Name"` 的翻譯從 `"名字"` 改為 `"名稱"`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:192</code> 「Unsubscribe from all emails」翻譯可能造成語意偏差</summary>

`"Unsubscribe from all emails"` 的翻譯從 `"取消所有新闻信订阅"` 改為 `"取消接收所有邮件"`。原文指的是取消所有電子郵件（可能包含新聞信），但新翻譯可能被理解為取消所有郵件（包括交易郵件等）。請確認此翻譯是否準確。

**判斷依據**：diff 中此行將翻譯改為「取消接收所有邮件」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6345 (cache hit 1536) ｜ completion tokens 1934 ｜ PR #8</sub>