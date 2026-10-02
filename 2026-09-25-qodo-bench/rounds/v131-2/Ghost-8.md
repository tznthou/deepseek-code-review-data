<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 zh 語系檔中的詞彙從台灣用語改為中國大陸用語，並刪除了 comments.json。主要風險在於刪除檔案可能導致程式碼中引用該檔案的翻譯鍵時出現缺失，進而顯示原始英文或錯誤。此外，部分翻譯變更可能造成語意混淆（如「Name」從「名字」改為「名稱」）。整體而言，變更本身無安全疑慮，但需確認刪除檔案的必要性與引用完整性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致翻譯鍵缺失 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:9` | 翻譯遺漏變數 {newsletterName} | 0.70 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:117` | 「Name」翻譯從「名字」改為「名稱」可能造成混淆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致翻譯鍵缺失</summary>

此 PR 刪除了整個 comments.json 檔案。若程式碼中仍有引用該檔案中的翻譯鍵（例如 `"{amount} comments"`、`"Add comment"` 等），在執行時將找不到對應翻譯，可能回退為英文或顯示鍵名。請確認所有引用均已移除或改由其他檔案提供，否則應保留此檔案。

**判斷依據**：diff 顯示整個檔案被刪除，且未見其他檔案新增相同翻譯鍵。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯遺漏變數 {newsletterName}</summary>

翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 原本包含 `{newsletterName}` 變數，但新翻譯 `"{memberEmail}将不会再收到新闻信。"` 遺漏了該變數。這可能導致使用者無法得知具體是哪一份新聞信，影響資訊完整性。建議保留變數，例如 `"{memberEmail}将不会再收到{newsletterName}新闻信。"`

**判斷依據**：diff 中此行將原本包含 `{newsletterName}` 的翻譯改為不含該變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:117</code> 「Name」翻譯從「名字」改為「名稱」可能造成混淆</summary>

在 portal.json 中，`"Name"` 的翻譯從「名字」改為「名稱」。在個人資料欄位中，「名稱」可能不如「名字」自然，且與 ghost.json 中的「名字」不一致。建議統一使用「名字」或「姓名」。

**判斷依據**：diff 顯示 `"Name"` 的翻譯從「名字」改為「名稱」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6309 (cache hit 6272) ｜ completion tokens 787 ｜ PR #8</sub>