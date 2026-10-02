<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 在 v2 訂位 API 的回應中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 後綴（+25 字元）以提供乾淨的顯示用電子郵件。主要風險在於正規表達式過於寬鬆，可能誤刪合法電子郵件中的加號部分；此外，移除排序邏輯可能導致回傳順序不穩定，且 OpenAPI 文件中的縮排不一致。整體而言，功能方向正確，但需修正正規表達式與排序問題後再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97` | 正規表達式可能誤刪合法電子郵件中的加號部分 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能導致回傳順序不穩定 | 0.80 |
| 🔸 | Minor | `docs/api-reference/v2/openapi.json:31726` | OpenAPI 文件縮排不一致 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:97</code> 正規表達式可能誤刪合法電子郵件中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除加號後綴，但此模式會匹配任何加號後接 25 個英數字的字串，不限於 OAuth 後綴。例如 `user+tag@example.com` 中的 `+tag` 若長度為 25 且全為英數字，也會被移除，導致顯示錯誤。建議使用更精確的模式，例如 `/\+[a-zA-Z0-9]{25}@/` 或先驗證後綴格式。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用寬鬆的正規表達式，未限制後綴必須在 @ 之前或符合特定格式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能導致回傳順序不穩定</summary>

`getOutputRecurringSeatedBookings` 原本會依開始時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的訂位順序不固定，影響前端顯示或測試穩定性。若排序非必要，請確認呼叫端能接受任意順序；否則應保留排序。

**判斷依據**：diff 中刪除了 `return transformed.sort(...)` 並改為 `return transformed;`，未提供排序移除的理由。

</details>

<details><summary>🔸 <b>Minor</b> — <code>docs/api-reference/v2/openapi.json:31726</code> OpenAPI 文件縮排不一致</summary>

在 `required` 陣列的修改中，縮排從原本的 8 空格變成 0 空格，可能導致 JSON 格式錯誤或閱讀困難。請檢查並修正縮排。

**判斷依據**：diff 中顯示 `"required": [` 的縮排被移除，與前後不一致。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11186 (cache hit 11136) ｜ completion tokens 787 ｜ PR #4</sub>