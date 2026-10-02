<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了過濾通用日曆（如 Google 的群組、資源日曆）的功能，透過在查詢批次中加入 `genericCalendarSuffixes` 並以 `endsWith` 條件排除。整體設計合理，但存在一個潛在的效能問題：`endsWith` 在資料庫中通常無法使用索引，可能導致全表掃描，尤其在 `selectedCalendar` 資料表很大時會影響批次查詢效能。此外，`office365_calendar` 的後綴清單為空，可能是有意為之，但建議確認是否需支援。測試涵蓋了主要情境，但缺少對空陣列或未提供參數時的明確測試。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41` | 使用 `endsWith` 可能導致全表掃描，影響批次查詢效能 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41</code> 使用 `endsWith` 可能導致全表掃描，影響批次查詢效能</summary>

在 `where` 條件中使用 `endsWith` 來排除特定後綴的日曆，但資料庫（如 PostgreSQL）通常無法對 `endsWith` 使用一般的 B-tree 索引，這可能導致對 `selectedCalendar` 資料表的全表掃描。若該資料表規模較大，且此查詢被頻繁呼叫（例如定期同步），可能造成顯著的效能問題。

建議：
- 考慮在 `externalId` 上建立反向索引（reverse index）或使用其他可索引的比對方式（例如儲存反轉後的字串並使用 `startsWith`）。
- 若資料量不大或查詢頻率低，可接受此權衡，但應在 PR 描述中說明。

**判斷依據**：diff 中新增的 `AND` 條件使用了 `endsWith`，且未見任何索引調整或效能考量。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4270 (cache hit 4224) ｜ completion tokens 519 ｜ PR #7</sub>