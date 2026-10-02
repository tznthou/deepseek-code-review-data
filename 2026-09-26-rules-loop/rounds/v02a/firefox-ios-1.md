<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的多語言字串，並在 Focus iOS 中加入了對應的常數與格式化輔助類別。主要風險在於字串格式不一致（%@ 與 %1$@ 混用）、格式化輔助類別未遵循專案規範（缺少 final、ViewModel 分離、@MainActor 等），以及 linter 排除規則可能掩蓋問題。建議先修正字串格式與輔助類別設計。

### Findings（9 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | 字串格式不一致：%@ 與 %1$@ 混用 | 0.80 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6245` | 字串格式不一致：%@ 與 %1$@ 混用 | 0.75 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] SettingsTextFormatter 類別未標記為 final | 0.70 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:419` | [R07] 使用單例而非 ViewModel 結構 | 0.70 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | [R09] 格式化方法未標記 @MainActor | 0.60 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:427` | [R09] 格式化方法未標記 @MainActor | 0.60 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | [R11] 方法缺少明確的存取控制 | 0.60 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:427` | [R11] 方法缺少明確的存取控制 | 0.60 |
| 🔸 | Minor | `.github/l10n/linter_config_ios.json:8` | Linter 排除規則可能掩蓋問題 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> 字串格式不一致：%@ 與 %1$@ 混用</summary>

在 `RolloutsSettingMessage` 的 value 中使用 `%@`，但 comment 中卻寫 `%1$@`。這可能導致本地化工具或翻譯人員混淆，且若程式碼使用 `String(format:)` 時參數位置不同，可能造成 runtime crash 或顯示錯誤。建議統一使用 `%@` 或 `%1$@`，並確保 comment 與 value 一致。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 定義，value 使用 `%@`，comment 使用 `%1$@`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6245</code> 字串格式不一致：%@ 與 %1$@ 混用</summary>

在 `StudiesSettingMessageV3` 的 value 中使用 `%@`，但 comment 中卻寫 `%@`（此處一致），但與其他類似字串（如 `RolloutsSettingMessage`）的 comment 使用 `%1$@` 不一致。建議統一所有含格式符的字串 comment 格式，避免混淆。

**判斷依據**：diff 中新增的 `StudiesSettingMessageV3` 定義，value 使用 `%@`，comment 使用 `%@`，但與 `RolloutsSettingMessage` 的 comment 使用 `%1$@` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] SettingsTextFormatter 類別未標記為 final</summary>

新增的 `SettingsTextFormatter` 類別沒有標記為 `final`。根據規範 R12，不應被子類化的類別應標記為 final，以利編譯器優化並防止意外繼承。建議加上 `final` 修飾詞。

**判斷依據**：diff 中新增的類別宣告，缺少 `final` 關鍵字。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:419</code> [R07] 使用單例而非 ViewModel 結構</summary>

`SettingsTextFormatter` 使用單例模式（`static let shared`）來提供格式化功能，但根據規範 R07，UI 元件應使用 ViewModel struct 來封裝配置。此處的格式化邏輯可能應放在 ViewModel 中，或改為 struct 並注入。建議評估是否可改為 struct 並透過依賴注入傳遞。

**判斷依據**：diff 中新增的單例屬性，違反 ViewModel 分離原則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> [R09] 格式化方法未標記 @MainActor</summary>

`formatStudiesText` 和 `formatRolloutsText` 方法用於產生 UI 顯示文字，但未標記 `@MainActor`。若這些方法在背景執行緒被呼叫，可能導致 UI 更新問題。建議加上 `@MainActor` 或確保呼叫端在主執行緒。

**判斷依據**：diff 中新增的方法，未標記 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:427</code> [R09] 格式化方法未標記 @MainActor</summary>

`formatRolloutsText` 方法同樣未標記 `@MainActor`，存在與 `formatStudiesText` 相同的風險。

**判斷依據**：diff 中新增的方法，未標記 @MainActor。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> [R11] 方法缺少明確的存取控制</summary>

`formatStudiesText` 和 `formatRolloutsText` 方法沒有明確的存取控制修飾詞（如 `public`、`internal`、`private`）。根據規範 R11，應明確指定存取層級。建議加上 `internal` 或 `public` 視使用範圍而定。

**判斷依據**：diff 中新增的方法，缺少存取控制修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:427</code> [R11] 方法缺少明確的存取控制</summary>

`formatRolloutsText` 方法同樣缺少明確的存取控制修飾詞。

**判斷依據**：diff 中新增的方法，缺少存取控制修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/l10n/linter_config_ios.json:8</code> Linter 排除規則可能掩蓋問題</summary>

新增了 `firefox-ios.xliff:Settings.Studies.Message.v148` 的排除規則。這可能表示該字串存在 linter 檢查不過的問題（例如引號或格式），但直接排除可能掩蓋了潛在的本地化問題。建議確認排除原因，並修正字串本身而非排除。

**判斷依據**：diff 中新增的排除規則。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6745 (cache hit 1536) ｜ completion tokens 1877 ｜ PR #1</sub>