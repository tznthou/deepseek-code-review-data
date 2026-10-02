<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 zh 語系檔案的翻譯改為中國大陸用語，並刪除了 comments.json。主要風險在於刪除檔案可能導致程式碼中引用該檔案時出現錯誤，以及部分翻譯變更可能遺失變數或改變語意。建議確認刪除檔案的影響，並修正翻譯中的變數遺失問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/portal.json:9` | 翻譯中遺失變數 {newsletterName} | 0.90 |
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致執行時期錯誤 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:117` | 翻譯「Name」由「名字」改為「名稱」可能不恰當 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯中遺失變數 {newsletterName}</summary>

原文為 "{memberEmail} will no longer receive {newsletterName} newsletter."，翻譯改為 "{memberEmail}将不会再收到新闻信。"，遺漏了 {newsletterName} 變數。這會導致使用者看到的訊息缺少新聞信名稱，且可能造成 i18n 函式庫在插入變數時出現錯誤或顯示不完整。建議保留變數，例如："{memberEmail}将不会再收到{newsletterName}新闻信。"

**判斷依據**：diff 中此行由原本包含 {newsletterName} 的翻譯改為不含該變數的翻譯。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致執行時期錯誤</summary>

此 PR 刪除了整個 comments.json 檔案。如果程式碼中有任何地方載入此檔案（例如透過 i18n 函式庫），刪除後將導致找不到翻譯鍵值，可能回退到預設語言或拋出錯誤。請確認此檔案是否已不再被使用，或是否應保留並更新內容。

**判斷依據**：diff 中顯示整個檔案被刪除（deleted file mode 100644），且沒有新增替代檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:117</code> 翻譯「Name」由「名字」改為「名稱」可能不恰當</summary>

在 portal.json 中，"Name" 的翻譯由「名字」改為「名稱」。在個人資料相關的上下文中，「名字」較為常見且自然；「名稱」通常用於物件或組織。若此處指的是使用者姓名，建議維持「名字」。

**判斷依據**：diff 中此行將 "Name" 的翻譯從「名字」改為「名稱」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6309 (cache hit 1408) ｜ completion tokens 1700 ｜ PR #8</sub>