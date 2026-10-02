<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這次 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，並將 repository 類別更名為 PrismaSelectedCalendarRepository。整體改動符合命名規範（R01），但測試檔案中出現 `AND: undefined` 的斷言，這可能違反了 Biome 的格式或 lint 規則（R03/R06），且測試斷言過於脆弱。建議先確認 lint 是否會因 `AND: undefined` 而失敗，並考慮改用更精確的斷言方式。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:134` | [R03/R06] 測試斷言包含 `AND: undefined`，可能違反 lint 規則或格式 | 0.60 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:164` | [R03/R06] 測試斷言包含 `AND: undefined`，可能違反 lint 規則或格式 | 0.60 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:194` | [R03/R06] 測試斷言包含 `AND: undefined`，可能違反 lint 規則或格式 | 0.60 |

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:134</code> [R03/R06] 測試斷言包含 `AND: undefined`，可能違反 lint 規則或格式</summary>

在測試中，`toHaveBeenCalledWith` 的期望物件包含了 `AND: undefined`。這可能是因為實作中當 `genericCalendarSuffixes` 未提供時，`AND` 會被設為 `undefined`，但 Prisma 的查詢物件通常不應包含值為 `undefined` 的屬性。這可能導致 lint 警告（例如 noExplicitAny 或 noUndefined）或格式問題。建議檢查 Biome 設定，並考慮改用 `expect.objectContaining` 或明確斷言 `AND` 不存在。

**判斷依據**：diff 中新增的測試斷言包含 `AND: undefined`，這可能違反 R03（格式）或 R06（lint 警告視為錯誤）。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:164</code> [R03/R06] 測試斷言包含 `AND: undefined`，可能違反 lint 規則或格式</summary>

同上，另一個測試案例也加入了 `AND: undefined`。這可能導致 lint 警告或格式問題。建議確認 Biome 是否允許在物件字面值中出現 `undefined`，並考慮改用更精確的斷言。

**判斷依據**：diff 中新增的測試斷言包含 `AND: undefined`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:194</code> [R03/R06] 測試斷言包含 `AND: undefined`，可能違反 lint 規則或格式</summary>

同上，另一個測試案例也加入了 `AND: undefined`。這可能導致 lint 警告或格式問題。建議確認 Biome 是否允許在物件字面值中出現 `undefined`，並考慮改用更精確的斷言。

**判斷依據**：diff 中新增的測試斷言包含 `AND: undefined`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5746 (cache hit 5632) ｜ completion tokens 759 ｜ PR #7</sub>