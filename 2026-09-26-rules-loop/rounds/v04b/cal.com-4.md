<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 在 API v2 的訂位輸出中新增 displayEmail 與 displayGuests 欄位，目的是移除 OAuth 後綴（+25 字元）以提供乾淨的顯示用 email。主要風險在於 getDisplayEmail 的正規表達式過於寬鬆，可能誤刪合法 email 中的加號部分；此外，移除排序邏輯可能導致回傳順序不穩定，且新增欄位為必填可能造成既有 API 使用者相容性問題。建議先修正 email 清理邏輯並確認排序移除的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分 | 0.90 |
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能導致回傳順序不穩定 | 0.80 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:60` | cleanEmailForDisplay 方法未使用且可能重複邏輯 | 0.70 |
| 🔸 | Minor | `docs/api-reference/v2/openapi.json:31715` | 新增必填欄位可能造成 API 相容性問題 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除後綴，但此模式會匹配任何 email 中出現的 `+` 後接 25 個字母數字的情況。例如 `user+tag@example.com` 若 tag 長度為 25，則整個 `+tag` 會被移除，導致 email 變成 `user@example.com`，但這可能不是預期的 OAuth 後綴。OAuth 後綴通常有固定格式（例如 `+cuid`），應使用更精確的模式，例如 `/\+[a-z0-9]{25}$/`（假設後綴在 @ 之前且為小寫）。此外，若 email 中同時存在多個符合條件的片段，`replace` 只會移除第一個，可能留下其他後綴。建議先確認 OAuth 後綴的實際格式，並使用更嚴格的匹配。

**判斷依據**：diff 中新增的 getDisplayEmail 方法，正規表達式未限制位置或大小寫，可能誤刪合法 email 中的加號部分。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能導致回傳順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的訂位順序不穩定，影響前端顯示或後續處理。若排序不是必要，應確認呼叫端是否依賴排序；否則應保留排序或改用其他穩定排序方式。

**判斷依據**：diff 中將原本的排序邏輯移除，改為直接回傳 transformed。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:60</code> cleanEmailForDisplay 方法未使用且可能重複邏輯</summary>

在 `BookingAttendee` 類別中新增了 `cleanEmailForDisplay` 靜態方法，但實際清理邏輯在 `output.service.ts` 的 `getDisplayEmail` 中重複實作。這可能導致未來維護不一致。建議將清理邏輯集中在一處，或移除未使用的方法。

**判斷依據**：diff 中新增的靜態方法，但未在程式碼中看到使用。

</details>

<details><summary>🔸 <b>Minor</b> — <code>docs/api-reference/v2/openapi.json:31715</code> 新增必填欄位可能造成 API 相容性問題</summary>

在 OpenAPI 規格中，將 `displayEmail` 加入多個 schema 的 required 陣列，這表示 API 回應中必須包含此欄位。若既有使用者依賴舊的回應格式，可能會因新增必填欄位而受到影響。雖然通常新增欄位不會破壞相容性，但若使用者使用嚴格的 schema 驗證，可能導致錯誤。建議確認是否可將欄位設為選用，或提供適當的版本控制。

**判斷依據**：diff 中將 displayEmail 加入 required 陣列。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11810 (cache hit 11776) ｜ completion tokens 1209 ｜ PR #4</sub>