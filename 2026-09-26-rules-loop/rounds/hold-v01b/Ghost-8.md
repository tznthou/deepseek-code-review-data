<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將繁體中文翻譯改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除檔案可能導致缺少翻譯鍵，以及用語變更可能不符合繁體中文使用者的習慣。建議確認刪除檔案的影響，並考慮保留繁體中文用語。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致缺少翻譯鍵 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:9` | 翻譯變更可能不符合繁體中文習慣 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致缺少翻譯鍵</summary>

此 PR 刪除了整個 comments.json 檔案，但未提供替代檔案。如果應用程式仍會載入此檔案，將導致缺少翻譯鍵，可能顯示鍵名或英文原文。建議確認是否有其他檔案提供相同翻譯，或保留此檔案。

**判斷依據**：diff 顯示整個檔案被刪除，沒有新增對應檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯變更可能不符合繁體中文習慣</summary>

將「新聞信」改為「邮件通讯」等用語，可能不符合繁體中文使用者的習慣。建議確認目標受眾，若為繁體中文使用者，應保留原有用語。

**判斷依據**：diff 中多處將「新聞信」改為「邮件通讯」等中國大陸用語。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8654 (cache hit 8576) ｜ completion tokens 442 ｜ PR #8</sub>