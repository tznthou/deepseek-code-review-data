<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要新增 Studies 與 Rollouts 設定的本地化字串，並在 Focus 專案中加入 SettingsTextFormatter 輔助類別。整體風險低，但發現兩個問題：Rollouts 字串的格式佔位符在程式碼中為 %@，但註解寫成 %1$@，可能造成翻譯混淆；另外 en-GB 檔案結尾刪除了一個換行，可能影響檔案格式。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:6260` | Rollouts 字串的格式佔位符與註解不一致 | 0.80 |
| 🔸 | Minor | `firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:311` | 刪除了檔案結尾的換行 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> Rollouts 字串的格式佔位符與註解不一致</summary>

在 `RolloutsSettingMessage` 的 `value` 中使用 `%@`，但 `comment` 中寫的是 `%1$@`。這可能導致翻譯人員誤解佔位符的格式，進而產生錯誤的翻譯。建議將 `comment` 中的 `%1$@` 改為 `%@`，以保持一致。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 定義，`value` 使用 `%@`，但 `comment` 使用 `%1$@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:311</code> 刪除了檔案結尾的換行</summary>

在 en-GB.lproj/Settings.strings 的 diff 中，最後一行刪除了一個空行（`-` 行）。這可能導致檔案結尾缺少換行符，影響某些工具或版本控制系統的處理。建議保留檔案結尾的換行。

**判斷依據**：diff 中 en-GB.lproj/Settings.strings 的最後一行顯示刪除了一個空行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 17152 (cache hit 17024) ｜ completion tokens 582 ｜ PR #1</sub>