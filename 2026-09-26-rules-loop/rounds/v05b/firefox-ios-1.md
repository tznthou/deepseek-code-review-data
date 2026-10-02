<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Studies 與 Rollouts 設定的多語言字串，並在 Focus 專案中加入了新的 UI 常數與格式化輔助類別。主要風險在於新增的 SettingsTextFormatter 類別違反了多項專案規範（R12、R14、R11、R03），且其格式化方法可能因字串格式符與參數數量不符而導致執行階段錯誤。此外，部分新增字串的格式符與註解不一致，可能造成翻譯問題。建議先修正格式化邏輯與類別設計，再合併。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | 格式化字串與參數數量不符，可能導致執行階段錯誤 | 0.95 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] 類別未標記為 final，且不應被繼承 | 0.90 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R14] 公開 API 缺少文件註解 | 0.90 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:419` | [R11] 屬性與方法缺少明確的存取控制 | 0.85 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:417` | [R03] 缺少 MARK 註解來組織程式碼區段 | 0.80 |
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:6260` | 格式符與註解不一致 | 0.75 |
| 🔸 | Minor | `firefox-ios/Shared/Supporting Files/en-CA.lproj/Settings.strings:257` | 格式符與註解不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> 格式化字串與參數數量不符，可能導致執行階段錯誤</summary>

`formatStudiesText(appName:)` 使用 `String(format: strings.detailTextStudies, appName)`，但 `strings.detailTextStudies` 的值為 `"%@ may install and run studies from time to time."`，只有一個 `%@` 格式符，傳入一個參數是正確的。然而，`formatRolloutsText(appName:)` 使用 `String(format: strings.detailTextRollouts, appName)`，而 `strings.detailTextRollouts` 的值為 `"%@ will improve features, performance, and stability between updates. Changes applied remotely."`，同樣只有一個 `%@`，傳入一個參數也是正確的。但請注意，`strings.detailTextSendUsageData` 的值為 `"Mozilla strives to collect only what we need to provide and improve %@ for everyone."`，也只有一個 `%@`，但此處未使用。真正的問題在於 `strings.detailTextStudiesV2` 的值為 `"%@ randomly selects users to test features, which improves quality for everyone."`，只有一個 `%@`，但 `formatStudiesText` 使用的是 `strings.detailTextStudies`（舊版），而非 `V2`。如果意圖使用新版字串，應改用 `strings.detailTextStudiesV2`。此外，`strings.detailTextRollouts` 的值只有一個 `%@`，但若未來字串變更為多個格式符，此處未做防護。建議明確使用對應的字串常數，並考慮使用更安全的格式化方式（如 `String.localizedStringWithFormat`）或檢查格式符數量。

**判斷依據**：diff 中新增的 `formatStudiesText` 方法使用了 `strings.detailTextStudies`，但新增的 `strings.detailTextStudiesV2` 未被使用，可能導致顯示舊版文字。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] 類別未標記為 final，且不應被繼承</summary>

新增的 `SettingsTextFormatter` 類別未標記為 `final`，且其設計為單例（`static let shared`）並包含私有初始化器，明顯不應被繼承。根據規範 R12，應將此類別標記為 `final` 以防止意外繼承並提升效能。

**判斷依據**：diff 中新增的類別宣告為 `class SettingsTextFormatter {`，缺少 `final` 關鍵字。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R14] 公開 API 缺少文件註解</summary>

`SettingsTextFormatter` 類別及其方法 `formatStudiesText(appName:)` 和 `formatRolloutsText(appName:)` 均為公開（internal 或 public）API，但缺少文件註解（`///`）。根據規範 R14，應為這些 API 添加說明其用途、參數和回傳值的文件註解。

**判斷依據**：diff 中新增的類別和方法均無文件註解。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:419</code> [R11] 屬性與方法缺少明確的存取控制</summary>

`SettingsTextFormatter` 類別中的 `shared` 屬性、`formatStudiesText` 和 `formatRolloutsText` 方法均未標註明確的存取控制修飾詞（如 `public`、`internal`、`private`）。根據規範 R11，應明確指定其存取層級，以符合資訊隱藏原則。

**判斷依據**：diff 中新增的屬性和方法均無存取控制修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:417</code> [R03] 缺少 MARK 註解來組織程式碼區段</summary>

新增的 `SettingsTextFormatter` 類別位於 `UIConstants` 結構的尾端，但未使用 `// MARK:` 註解來標示此區段。根據規範 R03，應使用 MARK 註解來組織程式碼，例如 `// MARK: - Settings Text Formatter`，以提高可讀性。

**判斷依據**：diff 中新增的類別前僅有一般註解，未使用 MARK 註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> 格式符與註解不一致</summary>

`RolloutsSettingMessage` 的值為 `"%@ will improve features, performance, and stability between updates. Changes applied remotely."`，但註解中寫的是 `%1$@ is the app name`，使用了位置格式符 `%1$@`，而實際字串中只有 `%@`。這可能導致翻譯人員困惑，或在不同語言中格式符位置不同時出錯。建議統一使用 `%@` 或 `%1$@`，並確保註解與實際格式符一致。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 字串值只有一個 `%@`，但註解使用了 `%1$@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Supporting Files/en-CA.lproj/Settings.strings:257</code> 格式符與註解不一致</summary>

`Settings.Rollouts.Message.v148` 的值為 `"%@ will improve features, performance, and stability between updates. Changes applied remotely."`，但註解中寫的是 `%@ is the app name`，而實際字串中只有一個 `%@`，這是一致的。然而，在 `en-GB.lproj` 中相同的字串值也是只有一個 `%@`，但註解卻寫 `%1$@ is the app name`，不一致。建議統一所有語系的格式符與註解。

**判斷依據**：diff 中新增的字串值只有一個 `%@`，但對應的註解在 en-GB 中使用了 `%1$@`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6697 (cache hit 6656) ｜ completion tokens 2008 ｜ PR #1</sub>