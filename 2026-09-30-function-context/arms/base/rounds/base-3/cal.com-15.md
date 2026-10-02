<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的型別依賴移除，改為在 atoms 內自行定義型別，並調整相關 import 與 biome 規則。主要風險在於型別定義不一致：Slot.userIds 型別從 number[] 改為 string[]，可能導致執行時期錯誤；validateCreateScheduleInput 未驗證 schedule 結構，可能傳入無效資料。建議先修正型別不一致問題，並補強輸入驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot.userIds 型別從 number[] 改為 string[]，可能導致執行時期錯誤 | 0.90 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 未驗證 schedule 結構，可能接受無效資料 | 0.80 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" 匯出可能造成 breaking change | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot.userIds 型別從 number[] 改為 string[]，可能導致執行時期錯誤</summary>

原本 @calcom/trpc/server/routers/viewer/slots/types 中的 Slot.userIds 型別為 number[]，但此處新定義為 string[]。若實際 API 回傳的 userIds 是數字陣列，則使用此型別的程式碼（例如將 userIds 傳給其他函式）可能因型別不符而發生錯誤。建議確認實際資料型別，並保持與原定義一致。

**判斷依據**：diff 中新增的 Slot 型別定義 userIds?: string[]，而刪除的舊定義為 userIds?: number[]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 未驗證 schedule 結構，可能接受無效資料</summary>

validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 是否為符合預期的陣列結構。若呼叫端傳入錯誤格式的 schedule，可能導致後續 API 請求失敗或產生未預期的行為。建議加入對 schedule 的型別檢查，例如確認其為二維陣列且元素包含 start 和 end。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式僅驗證 name，未驗證 schedule。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" 匯出可能造成 breaking change</summary>

原本 package.json 中有 "./booker": "./booker/index.ts" 的匯出，現在改為 "./booker/types": "./booker/types.ts"。若外部使用者依賴 "./booker" 匯入，升級後會找不到模組。建議保留 "./booker" 匯出，或確認此變更為預期的 breaking change。

**判斷依據**：diff 中刪除了 "./booker": "./booker/index.ts"，新增了 "./booker/types": "./booker/types.ts"。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4419 (cache hit 4352) ｜ completion tokens 937 ｜ PR #15</sub>