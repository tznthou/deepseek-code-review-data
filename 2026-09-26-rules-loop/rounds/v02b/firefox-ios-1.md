<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的多語言字串，並在 Focus 專案中加入了對應的常數與格式化輔助類別。主要風險在於字串格式不一致（%@ 與 %1$@ 混用）、格式化輔助類別缺乏存取控制與文件，以及 linter 排除規則可能掩蓋問題。建議先修正格式一致性與輔助類別的封裝。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | 字串格式佔位符不一致：%@ 與 %1$@ 混用 | 0.80 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R11] SettingsTextFormatter 類別與成員缺少存取控制 | 0.75 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R14] SettingsTextFormatter 缺少文件註解 | 0.70 |
| 🔸 | Minor | `.github/l10n/linter_config_ios.json:8` | Linter 排除規則可能掩蓋格式問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> 字串格式佔位符不一致：%@ 與 %1$@ 混用</summary>

在 `RolloutsSettingMessage` 的 value 中使用 `%@`，但 comment 中卻寫 `%1$@`。這可能導致本地化工具或翻譯人員混淆，且若程式碼使用 `String(format:)` 搭配位置參數（如 `%1$@`）時，實際字串只有 `%@` 會造成 runtime crash 或顯示錯誤。建議統一使用 `%@` 或 `%1$@`，並同步更新 comment。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 字串，value 使用 `%@`，comment 使用 `%1$@`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R11] SettingsTextFormatter 類別與成員缺少存取控制</summary>

新增的 `SettingsTextFormatter` 類別及其成員（`shared`、`init`、`formatStudiesText`、`formatRolloutsText`）均未標示存取控制（如 `public`、`internal`、`private`）。根據規範 R11，所有屬性和方法應有明確的存取控制。此類別可能被外部模組意外使用，且 `shared` 單例的 `init` 未設為 private，可能被外部實例化。建議將類別標為 `final`，並將 `init` 設為 `private`，其他成員視需要設為 `internal` 或 `public`。

**判斷依據**：diff 中新增的 `SettingsTextFormatter` 類別，無任何存取控制修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R14] SettingsTextFormatter 缺少文件註解</summary>

新增的 `SettingsTextFormatter` 類別及其公開方法沒有文件註解。根據規範 R14，公開 API 應有 `///` 註解說明用途。建議為類別和方法加上簡短說明。

**判斷依據**：diff 中新增的類別，無文件註解。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/l10n/linter_config_ios.json:8</code> Linter 排除規則可能掩蓋格式問題</summary>

新增的排除規則 `firefox-ios.xliff:Settings.Studies.Message.v148` 可能用於跳過 quote 檢查，但該字串的 value 包含 `%@`，若格式不正確可能被忽略。建議確認此排除是否必要，並確保字串格式正確。

**判斷依據**：diff 中新增的排除規則。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6745 (cache hit 6656) ｜ completion tokens 1095 ｜ PR #1</sub>