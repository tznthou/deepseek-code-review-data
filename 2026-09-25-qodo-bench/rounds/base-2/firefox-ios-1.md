<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 新增了 Studies 與 Rollouts 設定的本地化字串，並在 Focus iOS 中加入了新的 UI 常數與格式化輔助類別。主要風險在於字串格式不一致（`%@` 與 `%1$@` 混用）、`SettingsTextFormatter` 使用舊版 `detailTextStudies` 而非新的 V2 字串，以及 linter 排除規則可能過於寬鬆。建議修正後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | Rollouts 訊息字串使用 %@ 但 comment 標示 %1$@，可能導致格式錯誤 | 0.90 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2 | 0.85 |
| 🔸 | Minor | `.github/l10n/linter_config_ios.json:8` | Linter 排除規則可能過於寬鬆 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> Rollouts 訊息字串使用 %@ 但 comment 標示 %1$@，可能導致格式錯誤</summary>

`RolloutsSettingMessage` 的 value 使用 `%@`，但 comment 中說明為 `%1$@`。在 iOS 的 `String(format:)` 中，`%@` 與 `%1$@` 皆可接受，但若其他語言翻譯時依 comment 使用位置參數，可能造成格式不一致。建議統一使用 `%@` 或 `%1$@`，並更新 comment。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 定義，value 使用 `%@`，comment 使用 `%1$@`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2</summary>

`formatStudiesText` 方法使用 `strings.detailTextStudies`，但此 PR 新增了 `detailTextStudiesV2`，且新的 Studies 標題與訊息皆已更新。若 UI 應顯示新版文字，此處應改用 `detailTextStudiesV2`，否則使用者會看到舊的說明。

**判斷依據**：diff 中新增的 `SettingsTextFormatter` 類別，`formatStudiesText` 使用 `strings.detailTextStudies`，而同一檔案中新增了 `detailTextStudiesV2`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/l10n/linter_config_ios.json:8</code> Linter 排除規則可能過於寬鬆</summary>

新增的排除規則 `"firefox-ios.xliff:Settings.Studies.Message.v148"` 僅針對特定 key，但若未來有其他類似格式問題，可能需要逐一排除。建議確認此排除是否必要，或改用更精確的規則。

**判斷依據**：diff 中 linter 設定新增的排除項目。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4686 (cache hit 4608) ｜ completion tokens 828 ｜ PR #1</sub>