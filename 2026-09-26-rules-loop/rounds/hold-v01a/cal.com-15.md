<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 從 @calcom/trpc/server 依賴中解耦，改為在 atoms 內定義所需型別，並調整相關 import 與 biome 規則。主要風險在於型別定義可能與原 trpc 型別不一致，導致 API 契約漂移；此外新增的 validateCreateScheduleInput 驗證過於寬鬆，可能讓無效資料進入 API。建議先確認型別相容性並強化輸入驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際 API 回應不符 | 0.80 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足，可能允許無效的 schedule 結構 | 0.75 |
| 🔸 | Minor | `packages/platform/atoms/package.json:58` | 移除 "./booker" 匯出可能導致下游匯入中斷 | 0.70 |
| 🔸 | Minor | `packages/platform/atoms/hooks/schedules/types.ts:1` | 新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際 API 回應不符</summary>

原本從 @calcom/trpc/server/routers/viewer/slots/types 匯入的 Slot 型別中 userIds 為 number[]，但此處新定義為 string[]。若實際 API 回傳的 userIds 為數字陣列，將導致型別錯誤或執行時期問題。請確認 API 實際回傳型別，並保持與原定義一致。

**判斷依據**：diff 中新增的 Slot 型別定義 userIds?: string[]，而刪除的舊型別為 userIds?: number[]。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足，可能允許無效的 schedule 結構</summary>

此函式僅驗證 name 為非空字串，未驗證 schedule 欄位的結構（例如是否為陣列、元素是否為 { start, end } 物件）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 Zod schema 進行完整驗證，或至少檢查 schedule 的型別與元素結構。

**判斷依據**：diff 中新增的 validateCreateScheduleInput 函式僅檢查 name，未檢查 schedule 欄位。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" 匯出可能導致下游匯入中斷</summary>

原本 package.json 中有 "./booker": "./booker/index.ts" 的匯出，現在被替換為 "./booker/types": "./booker/types.ts"。若其他套件或應用程式依賴 "@calcom/atoms/booker" 匯入，將導致模組解析失敗。請確認是否有其他程式碼使用該匯入路徑，並考慮保留舊匯出或提供相容性別名。

**判斷依據**：diff 中刪除了 "./booker": "./booker/index.ts"，新增了 "./booker/types": "./booker/types.ts"。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:1</code> 新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用</summary>

檔案中定義的 Schedule 型別未加上 export，但後續的 CreateScheduleHandlerReturn 等型別使用了它。若其他檔案需要直接使用 Schedule，將無法匯入。建議將 Schedule 加上 export，或確認其僅供內部使用。

**判斷依據**：diff 中新增的 Schedule 型別未加 export。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 5858 (cache hit 4352) ｜ completion tokens 1146 ｜ PR #15</sub>