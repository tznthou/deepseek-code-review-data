<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Studies 與 Rollouts 設定的本地化字串，並在 Focus 專案中加入了對應的常數與格式化輔助類別。主要風險在於新增的 SettingsTextFormatter 類別違反多項專案規範（R12、R11、R14），且其格式化邏輯可能因字串中的格式符號而導致執行期錯誤。此外，部分字串的註解與實際格式符號不一致，可能造成翻譯混淆。建議先修正上述問題再合併。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] SettingsTextFormatter 類別未標記為 final | 0.90 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:419` | [R11] SettingsTextFormatter 的 shared 屬性缺少明確存取控制 | 0.85 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | [R14] 公開方法 formatStudiesText 缺少文件註解 | 0.80 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:427` | [R14] 公開方法 formatRolloutsText 缺少文件註解 | 0.80 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:424` | formatStudiesText 使用 String(format:) 可能導致執行期錯誤 | 0.75 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:428` | formatRolloutsText 使用 String(format:) 可能導致執行期錯誤 | 0.75 |
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:6260` | RolloutsSettingMessage 的註解與格式符號不一致 | 0.60 |
| 🔸 | Minor | `firefox-ios/Shared/Supporting Files/en-CA.lproj/Settings.strings:257` | en-CA 翻譯中 Rollouts.Message 的格式符號可能不一致 | 0.60 |
| 🔸 | Minor | `firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:257` | en-GB 翻譯中 Rollouts.Message 的格式符號可能不一致 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] SettingsTextFormatter 類別未標記為 final</summary>

新增的 `SettingsTextFormatter` 類別未標記為 `final`，違反專案規範 R12（Classes That Should Not Be Subclassed Must Be Marked Final）。此類別為輔助格式化用途，不應被繼承。建議加上 `final` 修飾詞。

**判斷依據**：diff 中新增的類別宣告為 `class SettingsTextFormatter {`，未使用 `final` 關鍵字。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:419</code> [R11] SettingsTextFormatter 的 shared 屬性缺少明確存取控制</summary>

`static let shared = SettingsTextFormatter()` 未標示存取控制修飾詞（如 `public` 或 `internal`），違反專案規範 R11（Properties and Methods Must Have Appropriate Access Control）。建議明確標示為 `public static let shared` 或 `internal static let shared`，以符合專案慣例。

**判斷依據**：diff 中該行沒有存取控制修飾詞。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> [R14] 公開方法 formatStudiesText 缺少文件註解</summary>

`formatStudiesText(appName:)` 為公開方法，但未提供文件註解（`///`），違反專案規範 R14（Public APIs Must Have Documentation Comments）。建議加入說明方法用途、參數及回傳值的文件註解。

**判斷依據**：diff 中該方法沒有文件註解。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:427</code> [R14] 公開方法 formatRolloutsText 缺少文件註解</summary>

`formatRolloutsText(appName:)` 為公開方法，但未提供文件註解（`///`），違反專案規範 R14（Public APIs Must Have Documentation Comments）。建議加入說明方法用途、參數及回傳值的文件註解。

**判斷依據**：diff 中該方法沒有文件註解。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:424</code> formatStudiesText 使用 String(format:) 可能導致執行期錯誤</summary>

`formatStudiesText` 使用 `String(format: strings.detailTextStudies, appName)`，但 `strings.detailTextStudies` 的值為 `"%@ may install and run studies from time to time."`，其中 `%@` 為格式符號，理論上可正確替換。然而，若翻譯字串中意外包含其他格式符號（如 `%d`）或格式符號數量不符，將導致執行期崩潰或錯誤輸出。建議改用更安全的字串替換方式（例如 `String.localizedStringWithFormat` 或直接使用 `replacingOccurrences(of: "%@", with: appName)`），或確保翻譯字串嚴格遵守格式規範。

**判斷依據**：diff 中該行使用 `String(format:)`，且 `detailTextStudies` 的 value 包含 `%@`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:428</code> formatRolloutsText 使用 String(format:) 可能導致執行期錯誤</summary>

`formatRolloutsText` 使用 `String(format: strings.detailTextRollouts, appName)`，但 `strings.detailTextRollouts` 的值為 `"%@ will improve features, performance, and stability between updates. Changes applied remotely."`，其中 `%@` 為格式符號。與前述問題相同，若翻譯字串包含其他格式符號或格式符號數量不符，將導致執行期錯誤。建議改用更安全的字串替換方式。

**判斷依據**：diff 中該行使用 `String(format:)`，且 `detailTextRollouts` 的 value 包含 `%@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> RolloutsSettingMessage 的註解與格式符號不一致</summary>

`RolloutsSettingMessage` 的 value 為 `"%@ will improve features, performance, and stability between updates. Changes applied remotely."`，但 comment 中寫的是 `%1$@ is the app name`，格式符號不一致（`%@` vs `%1$@`）。這可能導致翻譯人員誤解格式符號的用法。建議統一為 `%@` 或 `%1$@`，並確保與實際使用的格式符號一致。

**判斷依據**：diff 中 value 使用 `%@`，但 comment 使用 `%1$@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Supporting Files/en-CA.lproj/Settings.strings:257</code> en-CA 翻譯中 Rollouts.Message 的格式符號可能不一致</summary>

在 en-CA 的翻譯中，`"Settings.Rollouts.Message.v148" = "%@ will improve features, performance, and stability between updates. Changes applied remotely.";` 使用了 `%@`，但原始碼中的 comment 提到 `%1$@`。雖然目前翻譯與原始碼一致，但若未來翻譯調整格式符號，可能導致不一致。建議確認所有語系的格式符號與原始碼一致。

**判斷依據**：diff 中該行使用 `%@`，但原始碼 comment 使用 `%1$@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:257</code> en-GB 翻譯中 Rollouts.Message 的格式符號可能不一致</summary>

在 en-GB 的翻譯中，`"Settings.Rollouts.Message.v148" = "%@ will improve features, performance, and stability between updates. Changes applied remotely.";` 使用了 `%@`，但原始碼中的 comment 提到 `%1$@`。雖然目前翻譯與原始碼一致，但若未來翻譯調整格式符號，可能導致不一致。建議確認所有語系的格式符號與原始碼一致。

**判斷依據**：diff 中該行使用 `%@`，但原始碼 comment 使用 `%1$@`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6735 (cache hit 4608) ｜ completion tokens 2155 ｜ PR #1</sub>