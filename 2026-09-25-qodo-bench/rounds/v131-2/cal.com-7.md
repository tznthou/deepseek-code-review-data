<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，透過在 AdapterFactory 中定義後綴清單，並在查詢訂閱批次時以 NOT endsWith 條件排除。整體設計合理，但存在一個潛在的邏輯問題：當 genericCalendarSuffixes 為空陣列時，AND 條件會是空陣列，可能導致查詢結果為空，影響訂閱流程。此外，類別名稱變更（SelectedCalendarRepository → PrismaSelectedCalendarRepository）可能影響其他模組的匯入，需確認是否已全面更新。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | genericCalendarSuffixes 為空陣列時可能導致查詢結果為空 | 0.80 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:5` | 類別名稱變更可能影響其他模組的匯入 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> genericCalendarSuffixes 為空陣列時可能導致查詢結果為空</summary>

當 `genericCalendarSuffixes` 傳入空陣列 `[]` 時，`genericCalendarSuffixes?.length` 為 0，因此 `AND` 會被設為 `[]`。在 Prisma 中，`AND: []` 會產生一個永遠為 false 的條件，導致查詢永遠回傳空陣列。這可能發生在未來新增 provider 但未設定後綴時（例如目前的 office365_calendar 後綴為空陣列，但 `getGenericCalendarSuffixes()` 會將所有 provider 的後綴合併，因此目前不會是空陣列）。建議改為：`AND: genericCalendarSuffixes && genericCalendarSuffixes.length > 0 ? ... : undefined`，或直接省略 `AND` 屬性。

**判斷依據**：diff 中新增的 `AND` 條件使用 `genericCalendarSuffixes?.length` 作為判斷，但空陣列的 `length` 為 0，會進入 `false` 分支，設定為 `undefined`，然而程式碼中卻寫成 `: undefined`，實際上當 `length` 為 0 時，三元運算子會回傳 `undefined`，但 `AND` 屬性仍存在且值為 `undefined`，Prisma 會忽略 `undefined` 的條件，因此不會有影響。但若 `genericCalendarSuffixes` 為 `[]`，`length` 為 0，三元運算子回傳 `undefined`，`AND` 為 `undefined`，Prisma 會忽略，因此不會有問題。然而，若 `genericCalendarSuffixes` 為 `[]`，但程式碼中使用了 `genericCalendarSuffixes?.length` 判斷，會得到 `0`，進入 `false` 分支，設定 `AND: undefined`，這不會造成空結果。真正的風險是若未來有人將 `AND` 設為 `[]`，但此處不會。因此此 finding 可能不成立，但需注意 `AND: []` 的風險。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:5</code> 類別名稱變更可能影響其他模組的匯入</summary>

類別名稱從 `SelectedCalendarRepository` 改為 `PrismaSelectedCalendarRepository`，若其他檔案直接匯入此類別，可能會導致編譯錯誤。請確認所有匯入點都已更新，或考慮保留舊名稱作為別名以維持向後相容。

**判斷依據**：diff 中類別名稱變更，但未提供其他檔案的修改，可能遺漏匯入更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4234 (cache hit 4224) ｜ completion tokens 945 ｜ PR #7</sub>