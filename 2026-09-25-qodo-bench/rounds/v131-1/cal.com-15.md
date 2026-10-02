<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 @calcom/atoms 中對 @calcom/trpc 的依賴移除，改為在 atoms 內定義型別，並調整相關 import 與 package.json 的 exports。主要風險在於型別定義不一致：Slot 的 userIds 型別從 number[] 改為 string[]，可能導致下游使用時型別不符；新增的 validateCreateScheduleInput 驗證不足，未檢查 schedule 結構與 eventTypeId 型別；package.json 中移除了 "./booker" 的 export，可能造成使用該路徑的消費者建置失敗。建議先確認 Slot 的實際型別，並補強驗證邏輯與 exports 相容性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `packages/platform/atoms/booker/types.ts:17` | Slot 型別中 userIds 型別從 number[] 改為 string[]，可能造成型別不符 | 0.90 |
| ⚠️ | Major | `packages/platform/atoms/hooks/schedules/types.ts:38` | validateCreateScheduleInput 驗證不足，可能接受無效資料 | 0.85 |
| ⚠️ | Major | `packages/platform/atoms/package.json:58` | 移除 "./booker" export 可能導致下游匯入失敗 | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/booker/types.ts:17</code> Slot 型別中 userIds 型別從 number[] 改為 string[]，可能造成型別不符</summary>

原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot 的 userIds 型別為 number[]，但此處新定義的 Slot 將 userIds 改為 string[]。若實際資料中 userIds 為數字陣列，則使用此型別的程式碼（例如將 userIds 傳給其他函式）會出現型別錯誤。建議確認 userIds 的實際型別，若為 number[] 則應改回，或使用 union 型別。

**判斷依據**：diff 中新增的 Slot 型別定義，與被刪除的原始型別（userIds?: number[]）不同。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/hooks/schedules/types.ts:38</code> validateCreateScheduleInput 驗證不足，可能接受無效資料</summary>

此函式僅檢查 input 是否為物件且 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）或 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 zod 或其他 schema 驗證庫完整驗證所有欄位。

**判斷依據**：新增的驗證函式僅檢查 name，未檢查其他屬性。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/package.json:58</code> 移除 "./booker" export 可能導致下游匯入失敗</summary>

原本 exports 中有 "./booker": "./booker/index.ts"，此 PR 將其改為 "./booker/types": "./booker/types.ts"。若其他套件或應用程式使用 `import ... from "@calcom/atoms/booker"`，在升級後會因為找不到 export 而導致建置錯誤。建議保留 "./booker" 的 export，或確認所有使用方都已更新。

**判斷依據**：diff 中刪除了 "./booker": "./booker/index.ts"，新增了 "./booker/types": "./booker/types.ts"。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4383 (cache hit 1408) ｜ completion tokens 1020 ｜ PR #15</sub>