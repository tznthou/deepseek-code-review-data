<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將繁體中文翻譯改為中國大陸用語，並刪除了 comments.json 檔案。主要風險在於刪除檔案可能導致翻譯缺失，以及部分翻譯變更可能不符合繁體中文使用者的習慣。建議確認刪除檔案的影響，並重新評估部分用語的變更。

### Findings（10 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ghost/i18n/locales/zh/comments.json:1` | 刪除 comments.json 可能導致翻譯缺失 | 0.80 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:9` | 翻譯變更可能遺失變數 | 0.60 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:58` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:63` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:85` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:117` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:124` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:176` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:192` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |
| 🔸 | Minor | `ghost/i18n/locales/zh/portal.json:212` | 翻譯用語可能不符合繁體中文習慣 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>ghost/i18n/locales/zh/comments.json:1</code> 刪除 comments.json 可能導致翻譯缺失</summary>

此 PR 刪除了整個 comments.json 檔案，其中包含大量評論功能的翻譯字串。如果這些翻譯沒有在其他地方提供，使用者將看到英文原文或缺失的字串。請確認是否已將這些翻譯移至其他檔案，或確認刪除是有意為之。

**判斷依據**：diff 顯示整個檔案被刪除，且沒有新增對應的翻譯檔案。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:9</code> 翻譯變更可能遺失變數</summary>

原文為「{memberEmail} will no longer receive {newsletterName} newsletter.」，新翻譯為「{memberEmail}将不会再收到新闻信。」，遺漏了 {newsletterName} 變數。這可能導致使用者無法得知具體是哪個新聞信。建議保留變數，例如「{memberEmail}将不会再收到{newsletterName}新闻信。」

**判斷依據**：diff 中此行將原本包含 {newsletterName} 的翻譯改為不包含變數的版本。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:58</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「偏好設定」改為「偏好设置」，但「设置」是簡體中文用語，繁體中文通常使用「設定」。建議維持「偏好設定」或改為「偏好設置」需確認目標受眾。

**判斷依據**：diff 中將「偏好設定」改為「偏好设置」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:63</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「設定」改為「设置」，但「设置」是簡體中文用語。建議維持「設定」。

**判斷依據**：diff 中將「設定」改為「设置」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:85</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「会籍」改為「订阅」，但「订阅」是簡體中文用語，繁體中文通常使用「訂閱」。建議使用「訂閱」。

**判斷依據**：diff 中將「会籍」改為「订阅」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:117</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「名字」改為「名称」，但「名称」通常用於事物而非人。建議維持「名字」。

**判斷依據**：diff 中將「名字」改為「名称」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:124</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「新闻信」改為「邮件通讯」，但「邮件通讯」較少使用，且可能與其他翻譯不一致。建議維持「新闻信」或統一用語。

**判斷依據**：diff 中將「新闻信」改為「邮件通讯」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:176</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「仅限邀请」改為「仅限受邀访问」，但「受邀访问」較為冗長。建議維持「仅限邀请」或改為「仅限受邀」。

**判斷依據**：diff 中將「仅限邀请」改為「仅限受邀访问」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:192</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「新闻信」改為「邮件」，但「邮件」範圍較廣，可能失去特定性。建議維持「新闻信」或改為「電子報」。

**判斷依據**：diff 中將「新闻信」改為「邮件」。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ghost/i18n/locales/zh/portal.json:212</code> 翻譯用語可能不符合繁體中文習慣</summary>

將「电子邮件」改為「邮件」，但「邮件」較為口語。建議維持「电子邮件」或統一用語。

**判斷依據**：diff 中將「电子邮件」改為「邮件」。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8654 (cache hit 6272) ｜ completion tokens 1829 ｜ PR #8</sub>