<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，透過在 AdaptersFactory 中定義後綴清單，並在查詢時加入 NOT endsWith 條件。主要風險在於 AND 條件與既有 OR 條件的組合邏輯，以及後綴比對的大小寫敏感性和萬用字元處理。建議先確認 AND 與 OR 的組合是否符合預期，並考慮使用不區分大小寫的比對。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | AND 條件與 OR 條件組合可能導致邏輯錯誤 | 0.80 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43` | 後綴比對可能區分大小寫 | 0.70 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43` | 後綴可能包含萬用字元或特殊字元 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> AND 條件與 OR 條件組合可能導致邏輯錯誤</summary>

在 Prisma 的 where 中同時使用 OR 和 AND 時，AND 條件會與 OR 條件以 AND 結合，但 OR 內部的條件是 OR 關係。這可能導致過濾條件未如預期套用。例如，若 OR 條件為 (syncSubscribedAt 為 null 或 channelExpiration 小於某時間)，AND 條件為 NOT externalId endsWith 後綴，則最終條件為 (OR 條件) AND (AND 條件)，這通常是正確的。但若未來 OR 條件有變動，可能導致邏輯錯誤。建議明確使用巢狀 AND 或分開條件，並增加測試驗證。

**判斷依據**：diff 中新增的 AND 條件與既有的 OR 條件並列，可能造成邏輯混淆。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43</code> 後綴比對可能區分大小寫</summary>

Prisma 的 endsWith 預設可能區分大小寫，取決於資料庫 collation。若 externalId 可能包含大寫字母，則過濾可能失效。建議使用不區分大小寫的比對，例如使用 mode: 'insensitive'（若資料庫支援）或先將 externalId 轉為小寫再比對。

**判斷依據**：diff 中直接使用 endsWith，未指定大小寫模式。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43</code> 後綴可能包含萬用字元或特殊字元</summary>

後綴字串若包含 Prisma 的萬用字元（如 % 或 _），endsWith 可能將其視為萬用字元而非字面值。目前定義的後綴不包含這些字元，但未來新增時需注意。建議在文件中提醒或使用 escape 處理。

**判斷依據**：diff 中直接使用後綴字串，未進行跳脫。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4234 (cache hit 1408) ｜ completion tokens 832 ｜ PR #7</sub>