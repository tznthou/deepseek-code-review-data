<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的依賴移除，改為在 atoms 內定義型別。主要風險在於型別定義不一致：Slot.userIds 型別從 number[] 改為 string[]，可能導致下游使用錯誤；新增的 validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API；package.json 的 exports 變更可能破壞既有匯入。建議先修正型別不一致與驗證邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤 | 0.90 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API | 0.85 |
| ⚠️ | Major | `packages/platform/atoms/package.json:58` | 移除 "./booker" 匯出可能破壞既有匯入 | 0.80 |
| 🔸 | Minor | `packages/platform/atoms/hooks/schedules/types.ts:1` | Schedule 型別缺少部分欄位，可能與實際 API 回應不符 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤</summary>

原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot.userIds 的型別是 number[]，但此處新定義的 Slot.userIds 為 string[]。這可能導致使用此型別的下游程式碼（例如 apps/web/test/lib/getSchedule/expects.ts）在編譯或執行時出現型別不符的錯誤。請確認實際資料型別，若為 number[] 應修正為 number[]，或若確實為 string[] 則需同步更新所有使用處。

**判斷依據**：diff 中新增的 Slot 型別 userIds 為 string[]，而原 trpc 型別為 number[]（見刪除的程式碼）。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API</summary>

此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

**判斷依據**：函式只檢查 name，未檢查其他屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" 匯出可能破壞既有匯入</summary>

原本 exports 中有 "./booker": "./booker/index.ts"，現在改為 "./booker/types": "./booker/types.ts"。這會讓任何匯入 "@calcom/atoms/booker" 的程式碼失效。若此匯出路徑已被使用，應保留並新增 "./booker/types"，而非取代。

**判斷依據**：diff 中刪除了 "./booker": "./booker/index.ts"，新增了 "./booker/types": "./booker/types.ts"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:1</code> Schedule 型別缺少部分欄位，可能與實際 API 回應不符</summary>

新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

**判斷依據**：原 trpc 的 Schedule 型別可能更複雜，此處簡化可能導致型別不完整。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4419 (cache hit 1536) ｜ completion tokens 1209 ｜ PR #15</sub>