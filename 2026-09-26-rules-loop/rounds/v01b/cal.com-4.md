<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 v2 bookings API 的回應中新增 displayEmail / displayGuests 欄位，目的是移除 OAuth 後綴（+25 字元）以提供乾淨的顯示用 email。主要風險在於 getDisplayEmail 使用固定長度 25 的 regex 來移除後綴，若後綴長度不同或 email 本身含加號，可能錯誤移除或未移除；此外，移除排序邏輯可能導致回傳順序不穩定，且新增欄位為 required 可能造成既有客戶端相容性問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | getDisplayEmail 的 regex 假設後綴固定為 25 個字元，可能無法正確移除所有 OAuth 後綴 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能導致回傳順序不穩定 | 0.60 |
| 🔸 | Minor | `docs/api-reference/v2/openapi.json:31715` | 新增 required 欄位可能破壞向後相容性 | 0.50 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> getDisplayEmail 的 regex 假設後綴固定為 25 個字元，可能無法正確移除所有 OAuth 後綴</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除後綴，但 OAuth 後綴長度可能不是 25，或 email 本身包含加號（例如 `user+tag@example.com`）。若後綴長度不同，則不會被移除；若 email 本身有加號，則可能誤刪。建議改為移除最後一個 `+` 之後的所有字元（例如 `email.replace(/\+[^@]*/, "")`），或使用更精確的規則。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用固定長度 regex，且測試僅涵蓋特定長度後綴，未涵蓋其他長度或含加號的 email。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能導致回傳順序不穩定</summary>

原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，現在直接回傳 `transformed`。若 `bookingsIds` 未排序，回傳順序可能不一致，影響客戶端依賴順序的邏輯。建議保留排序或確認呼叫端已排序。

**判斷依據**：diff 中刪除了排序邏輯，改為直接回傳 transformed。

</details>

<details><summary>🔸 <b>Minor</b> — <code>docs/api-reference/v2/openapi.json:31715</code> 新增 required 欄位可能破壞向後相容性</summary>

在 OpenAPI 規格中將 `displayEmail` 加入 required 陣列，但若既有客戶端未預期此欄位，可能導致驗證錯誤或相容性問題。建議確認此變更是否為 breaking change，並考慮標記為 optional 或提供預設值。

**判斷依據**：diff 中在 required 陣列新增 displayEmail，且未提供預設值或標記為 optional。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 12625 (cache hit 12544) ｜ completion tokens 871 ｜ PR #4</sub>