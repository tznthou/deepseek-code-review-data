<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 zh 語系檔中的詞彙從台灣用語改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除 comments.json 可能導致相關功能缺少翻譯，以及部分翻譯變更可能造成語意混淆或遺漏變數。建議確認刪除檔案的影響範圍，並修正翻譯中的變數遺漏與語意問題。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/portal.json:9` | 翻譯中遺漏變數 {newsletterName} | 0.90 |
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致評論功能缺少翻譯 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:117` | 翻譯 'Name' 從 '名字' 改為 '名稱' 可能造成語意混淆 | 0.70 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:213` | 翻譯 'You're not receiving emails' 從 '您当前不会收到电子邮件。' 改為 '您将不会收到邮件。' 可能改變時態 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯中遺漏變數 {newsletterName}</summary>

翻譯字串 '{memberEmail} will no longer receive {newsletterName} newsletter.' 的譯文從 '{memberEmail}将不会再收到{newsletterName}的新闻信。' 改為 '{memberEmail}将不会再收到新闻信。'，遺漏了 {newsletterName} 變數。這會導致使用者無法得知具體是哪個新聞信，且可能造成格式錯誤。請保留變數，例如：'{memberEmail}将不会再收到{newsletterName}新闻信。'

**判斷依據**：diff 中此行將原本包含 {newsletterName} 的譯文改為不含變數的版本。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致評論功能缺少翻譯</summary>

此 PR 刪除了整個 comments.json 檔案，但未提供替代檔案或說明。若程式碼仍引用這些翻譯鍵，將導致評論相關介面顯示原始英文或出現錯誤。請確認是否有其他語系檔或合併計畫，否則應保留此檔案或提供替代方案。

**判斷依據**：diff 中顯示 comments.json 被刪除，且無新增對應檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:117</code> 翻譯 'Name' 從 '名字' 改為 '名稱' 可能造成語意混淆</summary>

在 portal.json 中，'Name' 的翻譯從 '名字' 改為 '名稱'。'名稱' 通常用於物件或非人類實體，而此處可能用於使用者姓名，建議維持 '名字' 或使用 '姓名'。請確認上下文後調整。

**判斷依據**：diff 中此行將 'Name' 的翻譯改為 '名称'。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:213</code> 翻譯 'You're not receiving emails' 從 '您当前不会收到电子邮件。' 改為 '您将不会收到邮件。' 可能改變時態</summary>

原文 'You're not receiving emails' 是現在進行式，表示目前狀態，但新譯文 '您将不会收到邮件。' 使用未來式，可能造成誤解。建議改為 '您当前不会收到邮件。' 或 '您目前不会收到邮件。'

**判斷依據**：diff 中此行將原本的現在式翻譯改為未來式。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6345 (cache hit 6272) ｜ completion tokens 928 ｜ PR #8</sub>