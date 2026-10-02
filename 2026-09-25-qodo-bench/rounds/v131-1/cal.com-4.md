<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 在 booking API 的回應中新增 displayEmail 欄位，以提供不含 OAuth CUID 後綴的乾淨 email。主要實作位於 output.service.ts，透過正規表達式移除 email 中的 +25 字元後綴。整體方向合理，但正規表達式可能誤刪合法 email 中的加號標籤，且 displayEmail 被標記為必填，可能造成既有 API 用戶端相容性問題。建議修正正規表達式並考慮將 displayEmail 設為可選。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96` | 正規表達式可能誤刪合法 email 中的加號標籤 | 0.80 |
| ⚠️ | Major | `packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32` | displayEmail 被標記為必填，可能破壞 API 相容性 | 0.70 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424` | 移除排序可能改變回應順序 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96</code> 正規表達式可能誤刪合法 email 中的加號標籤</summary>

`getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除 email 中加號後綴，但此模式會匹配任何 email 中加號後恰好 25 個英數字元的片段。例如 `user+tag@example.com` 若 `tag` 長度為 25，則整個 `+tag` 會被移除，導致 displayEmail 變成 `user@example.com`，但原始 email 的加號部分可能是使用者自訂的合法標籤，而非 OAuth CUID。這可能造成顯示錯誤的 email。

建議：確認 OAuth CUID 的實際格式，並使用更精確的匹配（例如固定前綴或更嚴格的長度與字元集），或改為從資料庫中直接取得原始 email，而非事後用正規表達式移除。

**判斷依據**：diff 中新增的 getDisplayEmail 方法使用正規表達式 /\+[a-zA-Z0-9]{25}/，可能誤刪合法 email 中的加號標籤。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32</code> displayEmail 被標記為必填，可能破壞 API 相容性</summary>

在 BookingAttendee、BookingHost、ReassignedToDto 等類別中，新增的 displayEmail 欄位被標記為必填（沒有 @IsOptional()），且 OpenAPI 規格中也將 displayEmail 加入 required 陣列。這表示所有 API 回應都必須包含 displayEmail，否則可能導致驗證失敗或客戶端解析錯誤。然而，此欄位是新增的，既有客戶端可能未預期此欄位，若客戶端使用嚴格的 schema 驗證，可能因額外欄位而失敗。

建議：將 displayEmail 設為可選（加上 @IsOptional()），並在 OpenAPI 中不要列為 required，以維持向後相容性。

**判斷依據**：diff 中新增的 displayEmail 欄位沒有 @IsOptional()，且 OpenAPI 的 required 陣列加入了 displayEmail。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424</code> 移除排序可能改變回應順序</summary>

在 getOutputRecurringSeatedBookings 方法中，原本有依 start 時間排序的邏輯，但此 PR 移除了該排序（`return transformed.sort(...)` 改為 `return transformed`）。這可能導致回應中的預約順序不再按時間排序，影響客戶端依賴順序的行為。

建議：確認移除排序是否為預期變更，若需維持原有行為，應保留排序。

**判斷依據**：diff 中將 `return transformed.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());` 改為 `return transformed;`

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11150 (cache hit 1408) ｜ completion tokens 1082 ｜ PR #4</sub>