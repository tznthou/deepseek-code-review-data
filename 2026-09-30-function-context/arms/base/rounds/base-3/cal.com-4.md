<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 為 2024-08-13 預訂 API 新增 displayEmail 與 displayGuests 欄位，目的是回傳去除 OAuth CUID 後綴的乾淨 email。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法 email 中的加號部分；此外，移除 recurring seated bookings 的排序邏輯可能導致輸出順序不穩定，且缺少對應的單元測試。建議修正正規表達式並補回排序，或提供明確的排序保證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除 recurring seated bookings 的排序可能導致輸出順序不穩定 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 缺少單元測試 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 CUID 後綴，但此模式會匹配任何 email 中加號後緊接 25 個英數字的片段。例如 `user+abcdefghijklmnopqrstuvwxyz@example.com` 會被錯誤地移除加號及後續字元，導致顯示錯誤的 email。建議使用更精確的模式，例如僅在 `@` 前匹配 CUID 格式（如 `/\+[a-zA-Z0-9]{25}(?=@)/`），或改用其他方式（如從資料庫取得原始 email）。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制加號後綴的位置，可能誤傷合法 email。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除 recurring seated bookings 的排序可能導致輸出順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的預訂順序不固定，影響前端顯示或測試的穩定性。若排序不再需要，請確認呼叫端能接受任意順序；否則應保留排序。

**判斷依據**：diff 中將原本的排序邏輯 `return transformed.sort(...)` 改為 `return transformed;`，移除了排序。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 缺少單元測試</summary>

新增的 `getDisplayEmail` 方法沒有對應的單元測試，尤其是針對各種 email 格式（含加號、無加號、多個加號等）的處理。建議新增測試以確保行為正確。

**判斷依據**：diff 中僅新增方法，未見相關測試檔案變更。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11186 (cache hit 11136) ｜ completion tokens 870 ｜ PR #4</sub>