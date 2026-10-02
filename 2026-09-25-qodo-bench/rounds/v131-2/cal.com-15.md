<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 套件中對 @calcom/trpc 的相依性移除，改為在 atoms 內自行定義型別，並調整相關 import 路徑與 package.json 的 exports。主要風險在於型別定義的正確性與一致性：新增的 Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際 API 回應不符；validateCreateScheduleInput 驗證不足，可能導致執行階段錯誤；package.json 中移除 "./booker" 匯出可能造成下游 breaking change。建議優先確認 Slot 型別與 API 回應的一致性，並補強驗證邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:19` | Slot 型別中 userIds 型別可能不正確 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足 | 0.70 |
| ⚠️ | Major | `packages/platform/atoms/package.json:58` | 移除 "./booker" 匯出可能造成 breaking change | 0.70 |
| 🔸 | Minor | `packages/platform/atoms/booker/types.ts:115` | SlotInfo 型別可能與實際 API 回應不符 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:19</code> Slot 型別中 userIds 型別可能不正確</summary>

新增的 Slot 型別將 userIds 定義為 string[]，但原本在 @calcom/trpc/server/routers/viewer/slots/types 中的定義為 number[]。若實際 API 回應的 userIds 為數字陣列，此型別會造成下游使用者的型別錯誤，甚至可能影響執行階段行為（例如將數字當字串處理）。建議確認 API 回應的實際型別，若為 number[] 則應修正為 number[]，或保留原定義。

**判斷依據**：diff 中新增的 Slot 型別：`userIds?: string[];`，而刪除的舊型別為 `userIds?: number[];`

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足</summary>

此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生難以追蹤的錯誤。建議使用 zod 或其他驗證方式完整驗證輸入，或至少對 schedule 與 eventTypeId 進行型別檢查。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式，僅檢查 name，未檢查其他屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" 匯出可能造成 breaking change</summary>

原本 package.json 中有 `"./booker": "./booker/index.ts"` 的匯出，此 PR 將其移除，改為 `"./booker/types": "./booker/types.ts"`。若下游使用者依賴 `@calcom/atoms/booker` 的匯入，升級後會出現模組找不到的錯誤。建議保留 `"./booker"` 匯出，或確認沒有下游使用該路徑。

**判斷依據**：diff 中刪除了 `"./booker": "./booker/index.ts"`，新增了 `"./booker/types": "./booker/types.ts"`

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/booker/types.ts:115</code> SlotInfo 型別可能與實際 API 回應不符</summary>

新增的 SlotInfo 型別包含 fromUser 與 toUser 等欄位，但未確認實際 API 回應是否包含這些欄位。若 API 回應的結構不同，可能導致型別錯誤。建議確認 API 回應的實際結構，並調整型別定義。

**判斷依據**：diff 中新增的 SlotInfo 型別，包含多個可選欄位，但未提供來源。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4383 (cache hit 4352) ｜ completion tokens 1267 ｜ PR #15</sub>