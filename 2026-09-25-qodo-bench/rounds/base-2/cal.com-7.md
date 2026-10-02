<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，透過在 AdapterFactory 中定義後綴清單，並在查詢訂閱批次時以 NOT endsWith 條件排除。整體設計合理，但存在兩個主要風險：一是 office365_calendar 的後綴清單為空，可能導致未來新增後綴時被遺漏；二是 Prisma 查詢中 AND 條件在無後綴時設為 undefined，可能在某些 Prisma 版本中造成型別或行為問題。此外，測試覆蓋了主要路徑，但缺少對空後綴清單的明確驗證。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `packages/features/calendar-subscription/adapters/AdaptersFactory.ts:19` | office365_calendar 的後綴清單為空，可能導致未來遺漏 | 0.60 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | AND 條件設為 undefined 可能導致 Prisma 查詢問題 | 0.55 |

<details><summary>🔸 <b>Minor</b> — <code>packages/features/calendar-subscription/adapters/AdaptersFactory.ts:19</code> office365_calendar 的後綴清單為空，可能導致未來遺漏</summary>

GENERIC_CALENDAR_SUFFIXES 中 office365_calendar 對應的陣列為空。若未來需要為 Office 365 日曆加入通用後綴，開發者可能忘記更新此處，導致過濾失效。建議加入註解說明目前無需過濾，或考慮使用更明確的結構（如 Map）並在取得後綴時檢查是否為空。

**判斷依據**：diff 中 office365_calendar 的後綴陣列為空，且無任何說明。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> AND 條件設為 undefined 可能導致 Prisma 查詢問題</summary>

當 genericCalendarSuffixes 為空或未提供時，AND 被設為 undefined。Prisma 通常會忽略 undefined 的條件，但某些版本或嚴格模式下可能拋出型別錯誤。建議改用條件展開（例如 ...(genericCalendarSuffixes?.length ? { AND: [...] } : {})）以避免傳入 undefined。

**判斷依據**：diff 中 AND 條件在無後綴時被設為 undefined。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4270 (cache hit 4224) ｜ completion tokens 636 ｜ PR #7</sub>