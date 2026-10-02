<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，避免訂閱非個人日曆。主要變更包括：在 AdaptersFactory 定義通用日曆後綴、在 CalendarSubscriptionService 傳遞後綴給 repository、在 SelectedCalendarRepository 的查詢中加入 AND 條件以排除這些日曆。整體設計合理，但需注意：1) 後綴比對使用 endsWith 可能誤排除合法日曆（例如使用者自訂日曆名稱結尾相同）；2) 目前 office365_calendar 的後綴清單為空，未來擴充時需確保涵蓋；3) 測試中出現 AND: undefined 的斷言，可能暗示實作細節洩漏，但非功能性問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | 使用 endsWith 過濾可能誤排除合法日曆 | 0.80 |
| 🔸 | Minor | `packages/features/calendar-subscription/adapters/AdaptersFactory.ts:19` | office365_calendar 的通用日曆後綴清單為空 | 0.60 |
| 🔸 | Minor | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:134` | 測試中斷言 AND: undefined 可能過度耦合實作 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> 使用 endsWith 過濾可能誤排除合法日曆</summary>

目前使用 `endsWith` 來排除 externalId 結尾為特定後綴的日曆。若使用者擁有一個自訂日曆，其 externalId 恰好以這些後綴結尾（例如 `mygroup@group.calendar.google.com`），則會被錯誤排除。建議改用更精確的比對方式，例如正規表示式或直接比對完整 ID 模式，或至少確認 Google 日曆 ID 的格式保證這些後綴只出現在通用日曆中。

**判斷依據**：diff 中新增的 AND 條件使用 `endsWith`，且後綴清單包含 `@group.calendar.google.com` 等，可能與使用者自訂日曆 ID 衝突。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/calendar-subscription/adapters/AdaptersFactory.ts:19</code> office365_calendar 的通用日曆後綴清單為空</summary>

目前 `office365_calendar` 的後綴清單為空陣列，這可能導致 Office 365 的通用日曆（如假日、資源）未被過濾。若未來需要支援，應補上對應後綴。若目前無需過濾，建議在註解中說明原因，避免誤解。

**判斷依據**：diff 中 `office365_calendar` 對應的陣列為空。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.test.ts:134</code> 測試中斷言 AND: undefined 可能過度耦合實作</summary>

在未提供 `genericCalendarSuffixes` 的測試中，斷言 `AND: undefined` 出現在查詢參數中。這可能使測試與實作細節過度耦合，未來若調整查詢結構（例如改用其他方式處理空陣列）會導致測試失敗。建議移除對 `AND: undefined` 的斷言，或改為驗證查詢結果而非精確參數。

**判斷依據**：diff 中多個測試案例新增了 `AND: undefined` 的斷言。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4270 (cache hit 1536) ｜ completion tokens 903 ｜ PR #7</sub>