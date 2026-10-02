<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的本地化字串，並在 Focus 專案中加入了新的 UI 常數與格式化輔助類別。主要風險在於字串格式不一致（%@ 與 %1$@ 混用）、新增的 V2 字串可能未被使用，以及 linter 排除規則可能掩蓋真正的格式問題。建議先確認格式字串的正確性與使用情境。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | 格式字串不一致：%@ 與 %1$@ 混用 | 0.80 |
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6232` | 新增的 V3 字串可能未被使用 | 0.70 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:203` | 新增的 V2 字串可能未被使用 | 0.70 |
| 🔸 | Minor | `.github/l10n/linter_config_ios.json:8` | Linter 排除規則可能掩蓋格式問題 | 0.60 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> 格式字串不一致：%@ 與 %1$@ 混用</summary>

在 `RolloutsSettingMessage` 中使用了 `%@`，但註解寫的是 `%1$@`。在 iOS 的本地化字串中，若使用位置參數（如 `%1$@`），則所有格式符都應使用位置參數，否則可能導致參數錯位或無法正確替換。建議統一使用 `%@` 或 `%1$@`，並更新註解。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 的 value 使用 `%@`，但 comment 提到 `%1$@`，兩者不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6232</code> 新增的 V3 字串可能未被使用</summary>

新增了 `StudiesSettingTitleV3`、`StudiesSettingLinkV3`、`StudiesSettingMessageV3` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

**判斷依據**：diff 中新增了 V3 字串，但沒有看到使用處。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:203</code> 新增的 V2 字串可能未被使用</summary>

新增了 `detailTextSendUsageDataV2`、`labelStudiesV2`、`detailTextStudiesV2` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

**判斷依據**：diff 中新增了 V2 字串，但沒有看到使用處。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/l10n/linter_config_ios.json:8</code> Linter 排除規則可能掩蓋格式問題</summary>

在 linter 設定中新增了排除 `firefox-ios.xliff:Settings.Studies.Message.v148`，這可能掩蓋了該字串的格式問題。建議確認該字串是否真的需要排除，或者是否應該修正格式問題而不是排除。

**判斷依據**：diff 中新增了排除規則。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題</summary>

新增的 `SettingsTextFormatter` 使用 singleton 模式，但沒有明顯的必要性。如果這個類別只包含無狀態的方法，可以考慮使用靜態方法，避免不必要的 singleton。另外，如果未來加入狀態，需注意執行緒安全。

**判斷依據**：diff 中新增了 singleton 類別。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4686 (cache hit 4608) ｜ completion tokens 1357 ｜ PR #1</sub>