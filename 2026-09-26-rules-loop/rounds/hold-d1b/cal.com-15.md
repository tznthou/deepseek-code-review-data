<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 對 @calcom/trpc 的依賴移除，改為在 atoms 內定義所需型別，並調整相關 import 與 package exports。主要風險在於型別定義可能與原 trpc 端不一致，以及新增的 validateCreateScheduleInput 驗證邏輯過於寬鬆，可能導致執行階段錯誤。建議先確認型別相容性並補強輸入驗證。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | [R05] 新增的 validateCreateScheduleInput 未使用 Zod schema，且驗證不完整 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | 型別 Slot 的 userIds 型別可能與原 trpc 定義不一致 | 0.70 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" export 可能造成 breaking change | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> [R05] 新增的 validateCreateScheduleInput 未使用 Zod schema，且驗證不完整</summary>

此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 與 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 為字串），將在後續處理時才失敗，且錯誤訊息不明確。建議使用 Zod 定義 schema 並進行完整驗證，以符合專案規範 R05。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式，僅檢查 name 欄位，未對 schedule 與 eventTypeId 進行驗證。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> 型別 Slot 的 userIds 型別可能與原 trpc 定義不一致</summary>

原 trpc 的 Slot 型別中 `userIds?: number[]`，但此處定義為 `userIds?: string[]`。若實際 API 回傳數字陣列，將導致型別不符，可能造成執行階段錯誤或型別斷言失效。請確認正確型別並修正。

**判斷依據**：diff 中新增的 Slot 型別，與被移除的 trpc Slot 型別相比，userIds 型別從 number[] 改為 string[]。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" export 可能造成 breaking change</summary>

原本 exports 中有 `"./booker": "./booker/index.ts"`，此 PR 將其改為 `"./booker/types": "./booker/types.ts"`。若外部套件依賴 `@calcom/atoms/booker` 路徑，將無法再匯入。請確認是否需保留舊路徑或提供相容性。

**判斷依據**：diff 中 package.json 的 exports 變更，移除了 "./booker" 項目。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5895 (cache hit 5888) ｜ completion tokens 906 ｜ PR #15</sub>