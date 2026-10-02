<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為錄音與逐字稿端點加上正式的身分驗證與權限控制，並補上對應的 e2e 測試。整體方向正確，但錄音端點的權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度限制，且 transcripts 端點的 guard 順序有變，可能影響錯誤回應。此外，移除 message 欄位屬於 API 破壞性變更，需確認客戶端相容性。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216` | 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度限制 | 0.80 |
| 🔸 | Minor | `apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238` | transcripts 端點 guard 順序變更可能影響錯誤回應 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:59` | 移除 message 欄位為 API 破壞性變更 | 0.70 |
| 🔸 | Minor | `packages/platform/types/bookings/2024-08-13/outputs/get-booking-transcripts.output.ts:17` | 移除 message 欄位為 API 破壞性變更 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216</code> 錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE 可能過度限制</summary>

此端點原本使用 BOOKING_READ 權限，現在改為 BOOKING_WRITE。讀取錄音通常只需要讀取權限，要求寫入權限可能導致僅有讀取權限的用戶無法存取錄音，造成不必要的 breaking change。建議確認是否有特殊原因需要寫入權限，否則應維持 BOOKING_READ。

**判斷依據**：diff 中將 @Permissions([BOOKING_READ]) 改為 @Permissions([BOOKING_WRITE])

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238</code> transcripts 端點 guard 順序變更可能影響錯誤回應</summary>

原本的 guard 順序為 BookingUidGuard，現在改為 BookingPbacGuard, ApiAuthGuard, BookingUidGuard。若 BookingPbacGuard 在 ApiAuthGuard 之前執行，未驗證的請求可能先被 Pbac 攔截，導致回應 403 而非 401，影響客戶端錯誤處理。建議確認 guard 執行順序是否符合預期。

**判斷依據**：diff 中將 @UseGuards(BookingUidGuard) 改為 @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:59</code> 移除 message 欄位為 API 破壞性變更</summary>

此 PR 移除了輸出型別中的 message 欄位，這會導致 API 回應不再包含該欄位。若客戶端仍依賴此欄位，可能造成相容性問題。建議確認所有客戶端已更新，或考慮保留欄位並標記為 deprecated。

**判斷依據**：diff 中刪除了 message 欄位的定義

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/types/bookings/2024-08-13/outputs/get-booking-transcripts.output.ts:17</code> 移除 message 欄位為 API 破壞性變更</summary>

此 PR 移除了輸出型別中的 message 欄位，這會導致 API 回應不再包含該欄位。若客戶端仍依賴此欄位，可能造成相容性問題。建議確認所有客戶端已更新，或考慮保留欄位並標記為 deprecated。

**判斷依據**：diff 中刪除了 message 欄位的定義

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6035 (cache hit 6016) ｜ completion tokens 932 ｜ PR #16</sub>