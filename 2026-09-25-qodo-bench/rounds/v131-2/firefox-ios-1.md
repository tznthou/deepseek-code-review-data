<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的字串資源，並更新了 Focus 專案的 UI 常數。主要風險在於字串格式不一致：Firefox 使用 %@ 作為 app name 的佔位符，但 Focus 的 detailTextStudies 與 detailTextRollouts 也使用 %@，而 comment 中卻寫成 %1$@，可能導致翻譯者誤解。另外，新增的 SettingsTextFormatter 類別使用 String(format:) 搭配 %@，若 appName 包含 % 字元可能造成格式化錯誤。整體而言，變更範圍明確，但需確認格式一致性與潛在的格式化問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:6261` | Rollouts 字串的 comment 佔位符不一致 | 0.70 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:205` | detailTextStudies 的 comment 佔位符不一致 | 0.70 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | SettingsTextFormatter 使用 String(format:) 可能造成格式化錯誤 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:6261</code> Rollouts 字串的 comment 佔位符不一致</summary>

在 `RolloutsSettingMessage` 的 comment 中使用了 `%1$@`，但 value 中實際使用的是 `%@`。這可能導致翻譯者困惑，不知道應該使用哪種佔位符。建議統一為 `%@` 或 `%1$@`。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 定義，comment 使用 `%1$@`，但 value 使用 `%@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:205</code> detailTextStudies 的 comment 佔位符不一致</summary>

在 `detailTextStudies` 的 comment 中使用了 `%@`，但 value 中實際使用的是 `%@`，這是一致的。然而，在 `detailTextStudiesV2` 的 comment 中使用了 `%@`，但 value 中也是 `%@`，這是一致的。但 `detailTextRollouts` 的 comment 中使用了 `%@`，但 value 中也是 `%@`，這是一致的。不過，`detailTextSendUsageData` 的 comment 中使用了 `%@`，但 value 中也是 `%@`，這是一致的。整體上，Focus 專案中的佔位符都是 `%@`，但 comment 中有些地方寫成 `%1$@`，可能造成混淆。

**判斷依據**：diff 中修改的 `detailTextStudies` 行，comment 使用 `%@`，但 value 使用 `%@`，一致。但其他行如 `detailTextSendUsageData` 的 comment 也使用 `%@`，一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> SettingsTextFormatter 使用 String(format:) 可能造成格式化錯誤</summary>

新增的 `SettingsTextFormatter` 使用 `String(format: strings.detailTextStudies, appName)`，其中 `strings.detailTextStudies` 包含 `%@` 佔位符。如果 `appName` 包含 `%` 字元，例如應用程式名稱可能包含百分比符號，則會導致格式化錯誤或崩潰。建議使用 `String.localizedStringWithFormat` 或直接替換字串，避免格式化問題。

**判斷依據**：diff 中新增的 `SettingsTextFormatter` 類別，使用 `String(format:)` 搭配 `%@`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4650 (cache hit 4608) ｜ completion tokens 1007 ｜ PR #1</sub>