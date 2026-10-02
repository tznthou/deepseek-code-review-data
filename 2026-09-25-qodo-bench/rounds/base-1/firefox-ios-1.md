<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的本地化字串，並在 Focus iOS 中加入了對應的常數與格式化輔助類別。主要風險在於本地化字串中的格式佔位符不一致（%@ vs %1$@）可能導致執行時期錯誤，以及新增的 SettingsTextFormatter 類別未被使用且可能造成記憶體浪費。建議修正佔位符並移除未使用的程式碼。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `firefox-ios/Shared/Strings.swift:6260` | 格式佔位符不一致可能導致執行時期錯誤 | 0.85 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | 新增的 SettingsTextFormatter 類別未被使用 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>firefox-ios/Shared/Strings.swift:6260</code> 格式佔位符不一致可能導致執行時期錯誤</summary>

在 `RolloutsSettingMessage` 的 value 中使用了 `%@`，但 comment 中說明為 `%1$@`。若翻譯人員依照 comment 使用 `%1$@`，則在執行時期使用 `String(format:)` 時，若只傳入一個參數，`%1$@` 是合法的（指定第一個參數），但若程式碼預期使用 `%@` 而翻譯使用 `%1$@`，可能導致格式字串與參數不匹配。建議統一使用 `%@` 或 `%1$@`，並確保所有翻譯遵循相同格式。

**判斷依據**：diff 中新增的 `RolloutsSettingMessage` 定義，value 使用 `%@`，comment 使用 `%1$@`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> 新增的 SettingsTextFormatter 類別未被使用</summary>

新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

**判斷依據**：diff 中新增的 `SettingsTextFormatter` 類別，但沒有看到任何使用它的程式碼。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4686 (cache hit 1536) ｜ completion tokens 712 ｜ PR #1</sub>