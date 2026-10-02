<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的字串資源，並在 Focus 專案中加入了對應的常數與格式化輔助類別。主要風險在於格式化字串中的佔位符用法不一致（%@ 與 %1$@ 混用），可能導致執行時期錯誤或顯示異常；此外，新增的 SettingsTextFormatter 類別未標記為 final，且其方法未加上 @MainActor，可能違反專案規範。建議先修正佔位符問題，並考慮將類別標記為 final。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | Rollouts 設定訊息使用 %1$@ 佔位符，與其他字串的 %@ 不一致 | 0.90 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] SettingsTextFormatter 類別未標記為 final | 0.80 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | [R09] SettingsTextFormatter 的方法未標記 @MainActor | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> Rollouts 設定訊息使用 %1$@ 佔位符，與其他字串的 %@ 不一致</summary>

在 `RolloutsSettingMessage` 的 value 中使用了 `%1$@`，而其他字串（如 `StudiesSettingMessageV3`）使用 `%@`。在 iOS 的本地化字串中，`%1$@` 是有效的格式說明符，但若程式碼使用 `String(format:)` 搭配單一參數，兩者皆可運作；然而，若使用 `String.localizedStringWithFormat` 或某些本地化機制，`%1$@` 可能無法正確解析，導致顯示原始佔位符或崩潰。建議統一使用 `%@`，除非有明確的多參數排序需求。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 字串 value 包含 `%1$@`，而其他字串使用 `%@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] SettingsTextFormatter 類別未標記為 final</summary>

新增的 `SettingsTextFormatter` 類別未標記為 `final`。根據專案規範 R12，不打算被繼承的類別應標記為 `final`，以利編譯器最佳化並明確設計意圖。此類別僅作為格式化輔助工具，無需繼承，建議加上 `final`。

**判斷依據**：diff 中新增的類別宣告缺少 `final` 關鍵字。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> [R09] SettingsTextFormatter 的方法未標記 @MainActor</summary>

`formatStudiesText` 和 `formatRolloutsText` 方法用於產生 UI 顯示文字，但未標記 `@MainActor`。根據專案規範 R09，涉及 UI 的程式碼應標記 `@MainActor` 以確保在主執行緒執行。雖然這些方法僅進行字串格式化，但若未來在其中加入 UI 相關操作，可能導致執行緒問題。建議將類別或方法標記為 `@MainActor`。

**判斷依據**：diff 中新增的方法未加上 `@MainActor` 屬性。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6755 (cache hit 4608) ｜ completion tokens 856 ｜ PR #1</sub>