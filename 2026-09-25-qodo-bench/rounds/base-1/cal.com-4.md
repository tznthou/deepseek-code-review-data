<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 2024-08-13 預訂 API 的輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 郵件中的 CUID 後綴（+25 字元）以供顯示。主要變更在 output.service.ts 中新增 getDisplayEmail 方法，並在 attendees、hosts、bookingFieldsResponses 等處套用。整體風險中等：正規表示式可能誤刪合法郵件中的加號標籤；displayGuests 的 map 回呼在嚴格模式下可能因 this 為 undefined 而拋錯；移除排序可能改變既有 API 行為；OpenAPI 文件格式有縮排問題。建議修正上述問題後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表示式可能誤刪合法郵件中的加號標籤 | 0.80 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169` | displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯 | 0.75 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能改變既有 API 行為 | 0.70 |
| 🔸 | Minor | `docs/api-reference/v2/openapi.json:31729` | OpenAPI 文件縮排不一致 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表示式可能誤刪合法郵件中的加號標籤</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除加號後 25 個字元。此模式假設所有加號後綴都是 CUID，但合法郵件地址（如 `user+tag@example.com`）中的加號標籤也會被移除，導致顯示錯誤。例如 `john+notes@example.com` 會變成 `john@example.com`。建議改用更精確的 CUID 格式（例如 `/\+[a-z0-9]{25}$/` 並檢查是否為 CUID），或僅在已知為 OAuth 產生的郵件時才移除。

**判斷依據**：diff 中新增的 getDisplayEmail 方法，正規表示式 `/\+[a-zA-Z0-9]{25}/` 會匹配任何加號後接 25 個字母數字，不限於 CUID。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169</code> displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯</summary>

在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

**判斷依據**：diff 中新增的程式碼直接將 `this.getDisplayEmail` 作為 `map` 的回呼，未綁定 `this`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能改變既有 API 行為</summary>

`getOutputRecurringSeatedBookings` 原本會依 `start` 時間排序回傳的預訂，此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳順序不穩定，影響依賴排序的客戶端。若無明確理由，建議保留排序。

**判斷依據**：diff 中刪除了 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());`，改為 `return transformed;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>docs/api-reference/v2/openapi.json:31729</code> OpenAPI 文件縮排不一致</summary>

在 `docs/api-reference/v2/openapi.json` 中，`required` 陣列的縮排從原本的 8 空格變成 0 空格，與其他屬性不一致。雖然不影響 JSON 解析，但可能造成維護上的困擾。建議修正縮排。

**判斷依據**：diff 中 `required` 陣列的行首沒有縮排，與前後文不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11186 (cache hit 1536) ｜ completion tokens 1230 ｜ PR #4</sub>