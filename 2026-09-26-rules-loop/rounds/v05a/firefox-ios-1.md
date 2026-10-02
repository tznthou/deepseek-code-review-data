<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 Studies 與 Rollouts 設定的多語言字串，並在 Focus 專案中加入了新的 UI 常數與格式化輔助類別。主要風險在於新增的 SettingsTextFormatter 類別未標記為 final、缺少文件註解，且未遵循既有的 ViewModel 架構；此外，部分字串的格式說明不一致，可能導致在地化翻譯錯誤。建議先修正這些問題再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R12] SettingsTextFormatter 應標記為 final | 0.90 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:423` | [R14] 公用方法缺少文件註解 | 0.80 |
| 🔸 | Minor | `focus-ios/Blockzilla/UIComponents/UIConstants.swift:418` | [R07] 應使用 ViewModel 結構而非獨立格式化類別 | 0.70 |
| 🔸 | Minor | `firefox-ios/Shared/Strings.swift:6261` | 格式說明不一致：Rollouts 訊息使用 %@ 但註解寫 %1$@ | 0.70 |

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R12] SettingsTextFormatter 應標記為 final</summary>

此類別為輔助格式化用途，不應被繼承。建議加上 `final` 修飾詞以符合專案規範並提升效能。

**判斷依據**：新增的類別未標記 final，違反 R12。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:423</code> [R14] 公用方法缺少文件註解</summary>

`formatStudiesText` 與 `formatRolloutsText` 為公用方法，應加上 `///` 文件註解說明用途與參數。

**判斷依據**：公用方法未附文件註解，違反 R14。

</details>

<details><summary>🔸 <b>Minor</b> — <code>focus-ios/Blockzilla/UIComponents/UIConstants.swift:418</code> [R07] 應使用 ViewModel 結構而非獨立格式化類別</summary>

此格式化邏輯可能應整合至對應的 ViewModel 中，以符合專案使用 ViewModel 配置 UI 的慣例。

**判斷依據**：新增獨立類別處理 UI 文字格式化，可能違反 R07 的 ViewModel 架構。

</details>

<details><summary>🔸 <b>Minor</b> — <code>firefox-ios/Shared/Strings.swift:6261</code> 格式說明不一致：Rollouts 訊息使用 %@ 但註解寫 %1$@</summary>

在 `RolloutsSettingMessage` 的註解中寫 `%1$@`，但實際字串使用 `%@`。這可能導致翻譯者困惑，建議統一為 `%@`。

**判斷依據**：註解與實際格式字串不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6697 (cache hit 4608) ｜ completion tokens 755 ｜ PR #1</sub>