<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的相依性移除，改為在 atoms 內定義型別，並調整相關 import 與 biome 規則。主要風險在於型別定義的正確性與一致性：Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際資料不符；新增的 validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤；GetAvailableSlotsResponse 的 slots 型別從陣列改為 Record<string, SlotInfo[]>，需確認與 API 回應一致。整體而言，此重構方向合理，但需修正上述型別問題並補齊驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際資料不符 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤 | 0.75 |
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:134` | GetAvailableSlotsResponse 的 slots 型別從陣列改為 Record<string, SlotInfo[]>，可能與 API 回應不符 | 0.70 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" 匯出可能造成 breaking change | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際資料不符</summary>

原本的 Slot 型別定義在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，userIds 為 number[]。此處新定義的 Slot 型別將 userIds 改為 string[]，但實際 API 回傳的 userIds 可能仍是 number[]。若使用此型別進行型別檢查，可能導致誤判或執行時期錯誤。建議確認實際資料型別，若為 number[] 則應維持 number[]。

**判斷依據**：diff 中新增的 Slot 型別定義，與被移除的 @calcom/trpc/server/routers/viewer/slots/types.ts 中的 Slot 型別相比，userIds 型別從 number[] 改為 string[]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤</summary>

validateCreateScheduleInput 僅驗證 name 為非空字串，未驗證其他屬性（如 schedule、eventTypeId）的型別與格式。若呼叫端傳入錯誤型別的 schedule 或 eventTypeId，可能導致後續 API 呼叫失敗或產生非預期行為。建議加入更完整的驗證，或使用 zod 等 schema 驗證工具。

**判斷依據**：新增的 validateCreateScheduleInput 函式僅檢查 name，未檢查其他屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:134</code> GetAvailableSlotsResponse 的 slots 型別從陣列改為 Record<string, SlotInfo[]>，可能與 API 回應不符</summary>

原本的 GetAvailableSlotsResponse 定義在 @calcom/trpc/server/routers/viewer/slots/util.ts 中，slots 為 Slot[]。此處新定義的 GetAvailableSlotsResponse 將 slots 改為 Record<string, SlotInfo[]>，若 API 實際回傳的格式為陣列，則型別不符。建議確認 API 回應格式，若為陣列則應維持陣列型別。

**判斷依據**：diff 中新增的 GetAvailableSlotsResponse 型別定義，與被移除的 @calcom/trpc/server/routers/viewer/slots/util.ts 中的 GetAvailableSlotsResponse 型別相比，slots 型別從 Slot[] 改為 Record<string, SlotInfo[]>。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" 匯出可能造成 breaking change</summary>

原本 package.json 中有 "./booker": "./booker/index.ts" 的匯出，此 PR 將其移除，改為 "./booker/types": "./booker/types.ts"。若其他套件或應用程式依賴 "./booker" 匯出，移除後將導致匯入失敗。建議確認是否有其他程式碼使用此匯出，若有必要可保留 "./booker" 匯出並指向新的檔案。

**判斷依據**：diff 中 package.json 的 exports 欄位，移除了 "./booker" 匯出，新增了 "./booker/types" 匯出。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4443 (cache hit 4352) ｜ completion tokens 1313 ｜ PR #15</sub>