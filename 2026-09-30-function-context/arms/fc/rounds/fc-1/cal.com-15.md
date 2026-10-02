<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的型別依賴移除，改為在 atoms 內自行定義型別，並調整相關 import 與 package exports。主要風險在於型別定義可能與實際 API 回傳不一致，尤其是 Slot 型別中 userIds 的型別從 number[] 改為 string[]，可能導致下游使用錯誤。另外，新增的 validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API。建議確認型別正確性並補強驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot 型別中 userIds 型別可能不正確 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足 | 0.75 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" export 可能造成 breaking change | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot 型別中 userIds 型別可能不正確</summary>

原本從 @calcom/trpc/server/routers/viewer/slots/types 匯入的 Slot 型別中，userIds 為 number[]，但此處新定義的 Slot 型別將 userIds 設為 string[]。若實際 API 回傳的 userIds 為 number[]，則使用此型別的程式碼（例如將 userIds 轉為字串或進行數值運算）會出現型別錯誤或執行期錯誤。建議確認 API 實際回傳型別，若為 number[] 則應修正為 number[]。

**判斷依據**：diff 中新增的 Slot 型別定義 userIds?: string[]，而刪除的原始型別為 userIds?: number[]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足</summary>

validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式僅檢查 name，未檢查其他屬性。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" export 可能造成 breaking change</summary>

原本 package.json 中有 "./booker": "./booker/index.ts" 的 export，此 PR 將其移除並新增 "./booker/types": "./booker/types.ts"。若其他套件或應用程式依賴 "./booker" 這個 export，升級後會導致 import 失敗。建議確認是否有外部使用，若有必要可保留 "./booker" export 或提供替代路徑。

**判斷依據**：diff 中刪除了 "./booker": "./booker/index.ts"，新增了 "./booker/types": "./booker/types.ts"。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4443 (cache hit 1536) ｜ completion tokens 973 ｜ PR #15</sub>