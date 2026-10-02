<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將中文翻譯從台灣用語改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除檔案可能導致翻譯缺失，以及部分翻譯變更可能造成語意或格式問題。最需要先確認的是刪除 comments.json 的影響，以及 portal.json 中遺漏變數的翻譯。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:0` | 刪除整個 comments.json 可能導致翻譯缺失 | 0.80 |
| ⚠️ | Major | `ghost/i18n/locales/zh/portal.json:9` | 翻譯中遺漏變數 {newsletterName} | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:0</code> 刪除整個 comments.json 可能導致翻譯缺失</summary>

此 PR 刪除了 `ghost/i18n/locales/zh/comments.json` 檔案，但未提供替代檔案。若應用程式仍會載入此翻譯檔，將導致所有評論相關字串回退到英文或顯示鍵名。請確認此刪除是否為預期行為，或是否應保留檔案並更新內容。

**判斷依據**：diff 中顯示整個檔案被刪除，且沒有新增對應的替代檔案。

</details>

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯中遺漏變數 {newsletterName}</summary>

原翻譯 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 包含變數 `{newsletterName}`，但新翻譯 `"{memberEmail}将不会再收到新闻信。"` 移除了該變數。這可能導致顯示時缺少新聞信名稱，或造成 i18n 函式庫因缺少變數而拋出錯誤。請確認是否應保留變數。

**判斷依據**：diff 中此行將原本包含 `{newsletterName}` 的翻譯改為不含該變數。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8691 (cache hit 8576) ｜ completion tokens 561 ｜ PR #8</sub>