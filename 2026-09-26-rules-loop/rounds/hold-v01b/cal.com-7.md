<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，透過在 AdapterFactory 中定義後綴並傳遞給 SelectedCalendarRepository 的查詢條件來排除這些日曆。整體設計合理，但存在一個潛在的效能問題：當 genericCalendarSuffixes 為空陣列時，Prisma 查詢中會包含 `AND: undefined`，可能導致不必要的查詢複雜度或錯誤。此外，測試中對 `AND: undefined` 的斷言可能過於脆弱。建議在 repository 層面避免傳遞 undefined 的 AND 條件，並考慮調整測試以更精確地驗證行為。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | 當 genericCalendarSuffixes 為空陣列時，Prisma 查詢包含 `AND: undefined` | 0.60 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:134` | 測試中對 `AND: undefined` 的斷言可能過於脆弱 | 0.50 |

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> 當 genericCalendarSuffixes 為空陣列時，Prisma 查詢包含 `AND: undefined`</summary>

在 `findNextSubscriptionBatch` 方法中，`AND` 條件被設置為 `genericCalendarSuffixes?.length ? ... : undefined`。當 `genericCalendarSuffixes` 為空陣列或未提供時，`AND` 將為 `undefined`。雖然 Prisma 通常會忽略 `undefined` 的條件，但這可能導致生成的 SQL 包含不必要的 `AND` 子句，影響查詢效能或可讀性。建議在建構 where 物件時，僅在需要時才加入 `AND` 屬性，例如使用條件展開。

**判斷依據**：diff 中新增的 `AND` 條件使用了三元運算符，當條件不滿足時賦值為 `undefined`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:134</code> 測試中對 `AND: undefined` 的斷言可能過於脆弱</summary>

在測試中，當未提供 `genericCalendarSuffixes` 時，斷言 `AND: undefined`。這依賴於 Prisma 查詢物件的內部表示，如果未來 Prisma 版本或程式碼重構改變了 `undefined` 的處理方式，測試可能會失敗。建議改為驗證查詢結果的正確性，或使用更寬鬆的匹配器（如 `expect.objectContaining`）來忽略 `AND` 屬性。

**判斷依據**：測試中多次出現 `AND: undefined` 的斷言，這可能過度耦合於實作細節。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5709 (cache hit 5632) ｜ completion tokens 711 ｜ PR #7</sub>