<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的依賴移除，改為在 atoms 內定義型別，並調整相關 import 與 package exports。主要風險在於型別定義不一致（Slot.userIds 型別從 number[] 改為 string[]，可能導致下游錯誤）、新增的 validateCreateScheduleInput 驗證不足（未檢查 schedule 結構與 eventTypeId 型別），以及 package.json 中移除 "./booker" export 可能造成 breaking change。建議先修正型別不一致與驗證邏輯，並確認 export 移除的影響。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤 | 0.90 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤 | 0.85 |
| ⚠️ | Major | `packages/platform/atoms/package.json:58` | 移除 "./booker" export 可能造成 breaking change | 0.80 |
| 🔸 | Minor | `packages/platform/atoms/hooks/schedules/types.ts:49` | validateCreateScheduleInput 回傳型別未嚴格驗證 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤</summary>

原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot.userIds 的型別是 number[]，但此處新定義的 Slot.userIds 型別為 string[]。這可能導致使用該型別的下游程式碼（例如 apps/web/test/lib/getSchedule/expects.ts）在編譯或執行時發生型別不符的錯誤。建議確認實際資料型別，若確實為 string[] 則需同步更新所有相關程式碼；若為 number[] 則應修正此處定義。

**判斷依據**：diff 中新增的 Slot 型別定義 userIds?: string[]，而刪除的舊型別為 userIds?: number[]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤</summary>

此函式僅驗證 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）及 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式的資料，可能導致後續 API 呼叫失敗或產生難以除錯的錯誤。建議使用 Zod 或更完整的型別檢查來驗證輸入。

**判斷依據**：函式中僅檢查 name，未檢查 schedule 與 eventTypeId。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" export 可能造成 breaking change</summary>

原本 package.json 中有 "./booker": "./booker/index.ts" 的 export，此 PR 將其移除，僅保留 "./booker/types": "./booker/types.ts"。若其他套件或應用程式依賴 "@calcom/atoms/booker" 的 import，將導致模組解析失敗。建議確認是否有下游使用者，若有必要則保留原 export 或提供替代路徑。

**判斷依據**：diff 中刪除了 "./booker": "./booker/index.ts"，僅新增 "./booker/types"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:49</code> validateCreateScheduleInput 回傳型別未嚴格驗證</summary>

函式回傳型別為 CreateScheduleInput，但僅透過型別斷言 (as CreateScheduleInput) 轉換，未實際驗證 schedule 與 eventTypeId 的型別。這可能導致呼叫端誤以為輸入已通過驗證，但實際上可能包含無效資料。建議使用型別守衛或 Zod schema 來確保型別安全。

**判斷依據**：函式結尾直接使用 as 斷言，未進行額外驗證。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5858 (cache hit 5760) ｜ completion tokens 1182 ｜ PR #15</sub>