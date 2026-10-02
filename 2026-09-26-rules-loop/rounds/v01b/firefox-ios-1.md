<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的多語言字串，並在 Focus 專案中加入了新的 UI 常數與格式化輔助類別。主要風險在於字串格式不一致（%@ 與 %1$@ 混用）、新增的 SettingsTextFormatter 類別缺乏存取控制與 final 修飾，以及未提供對應的測試。建議先修正格式字串與類別設計，再合併。

### Findings（5 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | 格式字串不一致：%@ 與 %1$@ 混用 | 0.90 |
| ⚠️ | Major | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R11] SettingsTextFormatter 類別與方法缺少存取控制 | 0.85 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] SettingsTextFormatter 應標記為 final | 0.80 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | 新增的格式化方法未提供測試 | 0.75 |
| 🔸 | Minor | `firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:309` | 移除檔案結尾的換行 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> 格式字串不一致：%@ 與 %1$@ 混用</summary>

在 `RolloutsSettingMessage` 中使用了 `%@`，但註解中卻寫 `%1$@`。這可能導致在地化工具或執行時期格式化時出現問題。建議統一使用 `%@` 或 `%1$@`，並更新註解以符合實際格式。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 定義，value 使用 `%@`，但 comment 提到 `%1$@`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R11] SettingsTextFormatter 類別與方法缺少存取控制</summary>

新增的 `SettingsTextFormatter` 類別及其方法未標示任何存取控制（如 `private`、`internal`、`public`）。根據規範 R11，所有屬性和方法應有明確的存取控制。建議將此類別標記為 `final`，並將方法設為 `internal` 或 `public`（視使用範圍而定），同時考慮將 `shared` 設為 `static let` 並加上 `private init`。

**判斷依據**：diff 中新增的 `SettingsTextFormatter` 類別，未標示任何存取控制修飾詞。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] SettingsTextFormatter 應標記為 final</summary>

`SettingsTextFormatter` 類別沒有被設計為可繼承，建議加上 `final` 修飾詞，以符合規範 R12 並提升效能。

**判斷依據**：diff 中新增的類別宣告，缺少 `final` 關鍵字。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> 新增的格式化方法未提供測試</summary>

`formatStudiesText` 和 `formatRolloutsText` 是新的邏輯方法，但沒有對應的測試。建議新增單元測試，驗證格式化的正確性，特別是當 appName 包含特殊字元時。

**判斷依據**：diff 中新增的方法，未見任何測試檔案變更。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Supporting Files/en-GB.lproj/Settings.strings:309</code> 移除檔案結尾的換行</summary>

在 en-GB.lproj/Settings.strings 的 diff 中，最後一行被移除，可能導致檔案結尾缺少換行符。這通常不是問題，但可能影響某些工具或 diff 顯示。建議保留檔案結尾的換行。

**判斷依據**：diff 中顯示刪除了最後一行空行。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6745 (cache hit 6656) ｜ completion tokens 1210 ｜ PR #1</sub>