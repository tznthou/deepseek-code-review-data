<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 的在地化字串，並在 Focus 專案中加入了對應的常數與格式化輔助類別。主要風險在於新增的 SettingsTextFormatter 類別違反多項專案規範（R12、R14、R03），且其格式化方法可能因字串中的格式符與參數數量不符而導致執行期錯誤。此外，en-GB 檔案結尾刪除了一個換行，可能造成檔案格式不一致。建議先修正格式化方法的格式符問題，並補上必要的修飾詞與文件註解。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:424` | 格式化字串的格式符與參數數量不符 | 0.90 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] SettingsTextFormatter 類別未標記為 final | 0.85 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R14] 公用類別與方法缺少文件註解 | 0.80 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:417` | [R03] 缺少 MARK 註解來組織程式碼區段 | 0.70 |
| 🔸 | Minor | `firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:311` | 檔案結尾刪除換行可能造成格式不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:424</code> 格式化字串的格式符與參數數量不符</summary>

`formatStudiesText(appName:)` 使用 `String(format: strings.detailTextStudies, appName)`，但 `strings.detailTextStudies` 的值為 `"%@ may install and run studies from time to time."`，只有一個 `%@`，傳入一個參數是正確的。然而，`formatRolloutsText(appName:)` 使用 `String(format: strings.detailTextRollouts, appName)`，而 `strings.detailTextRollouts` 的值為 `"%@ will improve features, performance, and stability between updates. Changes applied remotely."`，同樣只有一個 `%@`，傳入一個參數也是正確的。但請注意，若未來字串中新增其他格式符（例如 `%d`），此處的參數數量可能不符，導致執行期錯誤。建議改用 `String.localizedStringWithFormat` 或直接使用字串插值，以避免格式符問題。

**判斷依據**：diff 中新增的 `formatStudiesText` 方法使用 `String(format:)`，而對應的字串值包含 `%@`，目前參數數量相符，但此寫法對未來變更較脆弱。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] SettingsTextFormatter 類別未標記為 final</summary>

新增的 `SettingsTextFormatter` 類別未標記為 `final`，且其設計上不應被繼承（僅作為格式化輔助工具）。根據規範 R12，不應被繼承的類別應標記為 `final`，以利編譯器最佳化並明確設計意圖。建議加上 `final` 修飾詞。

**判斷依據**：diff 中新增 `class SettingsTextFormatter {`，未使用 `final`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R14] 公用類別與方法缺少文件註解</summary>

`SettingsTextFormatter` 類別及其方法 `formatStudiesText`、`formatRolloutsText` 均為 internal 或 public（此處為 internal，但作為共用輔助類別可能被其他模組使用），但缺少文件註解。根據規範 R14，公用 API 應包含 `///` 文件註解，說明用途、參數與回傳值。建議補上文件註解。

**判斷依據**：diff 中新增的類別與方法均無文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:417</code> [R03] 缺少 MARK 註解來組織程式碼區段</summary>

新增的 `SettingsTextFormatter` 類別位於 `UIConstants` 結構的尾端，但未使用 `// MARK:` 註解來標示此區段。根據規範 R03，應使用 MARK 註解來組織程式碼，提升可讀性。建議加上 `// MARK: - Settings Text Formatter` 之類的註解。

**判斷依據**：diff 中新增的類別前僅有一般註解，未使用 MARK。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:311</code> 檔案結尾刪除換行可能造成格式不一致</summary>

在 en-GB.lproj/Settings.strings 的 diff 中，最後一行 `"Settings.Translation.ToggleTitle.v145" = "Enable Translations";` 之後的換行被刪除。這可能導致檔案結尾缺少換行，與其他檔案不一致，也可能影響某些編輯器或工具。建議保留檔案結尾的換行。

**判斷依據**：diff 顯示最後一行之後的換行被移除（`-` 行）。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6735 (cache hit 6656) ｜ completion tokens 1322 ｜ PR #1</sub>