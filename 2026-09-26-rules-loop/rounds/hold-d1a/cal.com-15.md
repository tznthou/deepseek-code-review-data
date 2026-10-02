<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 對 @calcom/trpc 的依賴移除，改為在 atoms 內定義型別，並調整 package.json 的 exports 與 biome 的 import 限制。主要風險在於型別定義可能與實際 API 回傳不一致，以及新增的 validateCreateScheduleInput 驗證過於寬鬆，可能導致執行階段錯誤。建議先確認型別正確性與驗證邏輯。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | [R05] 新增的 validateCreateScheduleInput 未使用 Zod schema，且型別轉換不安全 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際 API 不符 | 0.70 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" export 可能造成 breaking change | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> [R05] 新增的 validateCreateScheduleInput 未使用 Zod schema，且型別轉換不安全</summary>

此函式僅檢查 `name` 為非空字串，其餘欄位（如 `schedule`、`eventTypeId`）未做任何驗證，直接以 `as CreateScheduleInput` 斷言。若呼叫端傳入錯誤型別（例如 `schedule` 為字串），將在後續處理時才發生錯誤，且錯誤訊息不明確。建議使用 Zod schema 定義並驗證輸入，或至少對每個欄位進行型別檢查。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式，僅驗證 name，其餘欄位直接斷言型別，違反 R05 的型別安全模式。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際 API 不符</summary>

原本從 @calcom/trpc 匯入的 Slot 型別中 `userIds?: number[]`，此處新定義改為 `userIds?: string[]`。若 API 實際回傳 number[]，將導致型別錯誤或執行階段問題。請確認 API 規格，若確實為 string[] 則需同步更新相關使用處。

**判斷依據**：diff 中新增的 Slot 型別，與被移除的 trpc 版本相比，userIds 型別從 number[] 改為 string[]。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" export 可能造成 breaking change</summary>

原本 exports 中有 `"./booker": "./booker/index.ts"`，此 PR 將其改為 `"./booker/types": "./booker/types.ts"`。若其他套件或應用程式依賴 `@calcom/atoms/booker` 的匯入，將導致解析失敗。建議保留原有 export 或確認無外部使用。

**判斷依據**：diff 中 package.json 的 exports 變更，移除了 "./booker" 路徑。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5895 (cache hit 5760) ｜ completion tokens 950 ｜ PR #15</sub>