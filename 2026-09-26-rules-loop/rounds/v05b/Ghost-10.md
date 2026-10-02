<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用再輪詢確認 handle，並將 API 升級至 v2。主要風險在於前端輪詢邏輯的競態與資源清理問題、TypeScript 嚴格模式被關閉，以及 API 回傳型別與快取更新邏輯的潛在缺陷。建議優先修正輪詢 effect 的依賴與競態，並恢復 strict 模式。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:121` | 輪詢 effect 缺少 confirmBlueskyHandleMutation 依賴，可能使用過時閉包 | 0.90 |
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119` | 輪詢 interval 未在元件卸載時清理，可能造成記憶體洩漏與錯誤請求 | 0.85 |
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript strict 模式，降低型別安全 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109` | 輪詢重試次數上限後自動停用 Bluesky，可能造成非預期停用 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | confirmBlueskyHandle 成功後未 invalidate accountFollows query | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/api/activitypub.ts:732` | confirmBlueskyHandle 回傳型別可能與實際 API 不符 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2725` | updateAccountBlueskyCache 的型別定義可能過於寬鬆 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:121</code> 輪詢 effect 缺少 confirmBlueskyHandleMutation 依賴，可能使用過時閉包</summary>

useEffect 的依賴陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`，但 `confirmHandle` 內部呼叫了 `confirmBlueskyHandleMutation.mutateAsync()`。若 mutation 物件在元件生命週期中被重新建立（例如因 queryClient 或 options 變更），此 effect 不會重新執行，導致輪詢使用舊的 mutation 實例，可能造成請求失效或狀態不同步。

建議將 `confirmBlueskyHandleMutation` 加入依賴陣列，或使用 `useRef` 保存最新的 mutation 實例。

**判斷依據**：diff 中新增的 useEffect 依賴陣列未包含 `confirmBlueskyHandleMutation`，而 `confirmHandle` 使用該 mutation。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119</code> 輪詢 interval 未在元件卸載時清理，可能造成記憶體洩漏與錯誤請求</summary>

useEffect 的回傳清理函式僅在依賴變更時執行，但若元件在輪詢進行中卸載，React 會呼叫該清理函式，因此 interval 會被清除。然而，若 `confirmBlueskyHandleMutation` 的 promise 在清理後才 resolve，其 `.then` 中的 `setHandleConfirmed` 仍會執行，可能導致對已卸載元件的狀態更新。此外，若 `disableBlueskyMutation.mutateAsync()` 在清理後才執行，也可能造成非預期的 API 呼叫。

建議在清理函式中加入取消機制（如 AbortController 或 flag），並在 promise 回呼中檢查元件是否仍掛載。

**判斷依據**：diff 中新增的 useEffect 回傳清理函式僅清除 interval，未處理進行中的非同步操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript strict 模式，降低型別安全</summary>

此 PR 將 `strict` 從 `true` 改為 `false`，違反專案規範 R16（TypeScript 檔案必須啟用嚴格型別檢查）。這會導致編譯器不再強制檢查 null/undefined、隱含 any 等問題，可能引入執行時期錯誤。

建議恢復 `strict: true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的 strict 設定被改為 false。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:109</code> 輪詢重試次數上限後自動停用 Bluesky，可能造成非預期停用</summary>

當 `retryCountRef.current >= MAX_CONFIRMATION_RETRIES` 時，程式會呼叫 `disableBlueskyMutation.mutateAsync()` 並顯示錯誤。若使用者只是暫時離開頁面或網路不穩，此邏輯會自動停用 Bluesky，可能造成使用者困惑。此外，`disableBlueskyMutation` 的 onSuccess 會更新快取，但此處未處理其可能的錯誤。

建議改為僅停止輪詢並顯示錯誤，由使用者手動決定是否停用，或至少提供明確的提示與重試選項。

**判斷依據**：diff 中新增的輪詢上限處理邏輯呼叫 disableBlueskyMutation。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> confirmBlueskyHandle 成功後未 invalidate accountFollows query</summary>

程式碼註解指出「Missing invalidation of accountFollows query that should happen here」。啟用 Bluesky 後，帳號會自動追蹤 brid.gy 帳號，但此 mutation 成功後未 invalidate 相關的追蹤查詢，可能導致 UI 顯示過時的追蹤狀態。

建議在 onSuccess 中加入對 accountFollows query 的 invalidate，或移除該註解並說明原因。

**判斷依據**：diff 中新增的 useConfirmBlueskyHandleMutationForUser 函式內有此註解。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/api/activitypub.ts:732</code> confirmBlueskyHandle 回傳型別可能與實際 API 不符</summary>

函式回傳型別為 `Promise<string>`，但實作中若 `json.handle` 為 null 或 undefined，會回傳空字串。然而，若 API 回傳的 handle 為非字串型別（如數字），`String(json.handle)` 會將其轉為字串，可能掩蓋型別錯誤。此外，`Account` 介面中 `blueskyHandle` 已改為 `string | null`，但此函式仍回傳 `string`，可能造成型別不一致。

建議確認 API 合約，並考慮回傳 `string | null` 或進行更嚴格的型別檢查。

**判斷依據**：diff 中 confirmBlueskyHandle 的實作仍使用 String() 轉換。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2725</code> updateAccountBlueskyCache 的型別定義可能過於寬鬆</summary>

`BlueskyDetails` 型別要求 `blueskyEnabled` 和 `blueskyHandleConfirmed` 為 boolean，但 `setQueryData` 的回呼參數 `currentProfile` 可能包含其他欄位，且此處直接展開 `blueskyDetails` 可能覆蓋其他屬性。若未來 `Account` 介面新增欄位，此處可能遺漏。

建議使用更精確的型別或使用 Partial 更新。

**判斷依據**：diff 中新增的型別定義與 setQueryData 的使用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11677 (cache hit 11648) ｜ completion tokens 1942 ｜ PR #10</sub>