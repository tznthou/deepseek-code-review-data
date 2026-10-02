<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的型別依賴改為本地定義，並調整相關 import 與 package exports。主要風險在於型別定義不一致（如 Slot.userIds 型別從 number[] 改為 string[]、Schedule 型別缺少部分欄位）可能導致執行時期錯誤或型別檢查失效；此外 validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API。建議先修正型別定義與驗證邏輯。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:19` | Slot.userIds 型別從 number[] 改為 string[] 可能造成執行時期錯誤 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:1` | Schedule 型別缺少部分原始欄位，可能導致型別不相容 | 0.75 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API | 0.70 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" export 可能造成 breaking change | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:19</code> Slot.userIds 型別從 number[] 改為 string[] 可能造成執行時期錯誤</summary>

原本 `@calcom/trpc/server/routers/viewer/slots/types` 中的 `Slot.userIds` 型別為 `number[]`，但此處新定義為 `string[]`。若實際 API 回傳的 userIds 是數字陣列，使用此型別的程式碼（例如將 userIds 傳入需要 number 的函式）會在執行時期發生型別不符的錯誤。建議確認 API 實際回傳型別，若為 number[] 則應改回 `number[]`，或使用 union type 並進行轉換。

**判斷依據**：diff 中新增的 Slot 型別定義 `userIds?: string[];` 與被刪除的原始定義 `userIds?: number[];` 不一致。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:1</code> Schedule 型別缺少部分原始欄位，可能導致型別不相容</summary>

新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

**判斷依據**：diff 中新增的 Schedule 型別定義，與原本從 @calcom/trpc 匯入的型別可能不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API</summary>

此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式，僅驗證 name 欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" export 可能造成 breaking change</summary>

原本 package.json 中有 `"./booker": "./booker/index.ts"`，現在改為 `"./booker/types": "./booker/types.ts"`，移除了 `./booker` 這個 export。若有外部使用者直接 import `@calcom/atoms/booker`，升級後會出現 module not found 錯誤。建議保留 `./booker` export 或提供 deprecation 警告。

**判斷依據**：diff 中刪除了 `"./booker": "./booker/index.ts"` 並新增 `"./booker/types"`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4419 (cache hit 4352) ｜ completion tokens 1234 ｜ PR #15</sub>