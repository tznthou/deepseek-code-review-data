<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再以輪詢方式確認 handle。主要風險在於前端輪詢邏輯的競態與資源清理、TypeScript 嚴格模式被關閉，以及 API 回傳型別變更後未完整更新相依程式碼。建議優先修正輪詢 effect 的依賴陣列與 cleanup，並恢復 strict 模式。

### Findings（6 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119` | 輪詢 effect 缺少 disableBlueskyMutation 依賴，可能使用到過時的 mutation 實例 | 0.95 |
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript strict 模式，降低型別安全 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | confirmBlueskyHandle mutation 成功後未 invalidate accountFollows query | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢 interval 未在元件 unmount 時正確清理，可能造成記憶體洩漏 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68` | confirmHandle 使用空依賴陣列，可能捕獲過時的 mutation 函式 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 與 disableBluesky 方法缺少回傳型別標註 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119</code> 輪詢 effect 缺少 disableBlueskyMutation 依賴，可能使用到過時的 mutation 實例</summary>

在 `useEffect` 中呼叫了 `disableBlueskyMutation.mutateAsync()`，但依賴陣列僅有 `[account?.blueskyEnabled, account?.blueskyHandleConfirmed, confirmHandle]`，未包含 `disableBlueskyMutation`。雖然註解聲稱 mutation 是穩定的，但 React Query 的 mutation 物件在每次 render 時可能重新建立，若父元件重新渲染導致 mutation 實例更新，此 effect 可能持有舊的 mutation，進而呼叫到過時的函式或造成記憶體洩漏。

**失敗情境**：當使用者啟用 Bluesky 後，父元件因其他狀態更新而重新渲染，`disableBlueskyMutation` 實例改變，但 effect 仍使用舊實例；當輪詢失敗達上限時，呼叫舊實例的 `mutateAsync` 可能無法正確觸發 API 或更新快取。

**建議**：將 `disableBlueskyMutation` 加入依賴陣列，或使用 `useRef` 保存最新的 mutation 實例，並在 effect 內使用 ref。

**判斷依據**：diff 中新增的 useEffect 依賴陣列缺少 disableBlueskyMutation，且註解聲稱 stable 但未提供保證。

</details>

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript strict 模式，降低型別安全</summary>

此 PR 將 `strict` 從 `true` 改為 `false`，違反專案規範 R16（TypeScript Files Must Enable Strict Type Checking）。關閉 strict 模式會讓編譯器不再強制檢查 null/undefined、隱含 any 等常見錯誤來源，可能導致執行時期錯誤未被發現。

**失敗情境**：例如 `account?.blueskyHandle` 可能為 `null`，但在 strict 模式下會強制處理；關閉後若未正確處理，可能導致執行時錯誤。

**建議**：恢復 `strict: true`，並修正因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的 strict 由 true 改為 false，違反 R16。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> confirmBlueskyHandle mutation 成功後未 invalidate accountFollows query</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但註解指出缺少 `accountFollows` query 的 invalidation。這可能導致 UI 上顯示的追蹤狀態與實際不一致，特別是在啟用 Bluesky 後會自動追蹤 brid.gy 帳號的情境。

**失敗情境**：使用者確認 handle 後，畫面可能仍顯示未追蹤 brid.gy，或追蹤列表未更新。

**建議**：在 `onSuccess` 中加入對應的 `queryClient.invalidateQueries` 呼叫，例如 `queryClient.invalidateQueries({ queryKey: QUERY_KEYS.accountFollows(handle) })`。

**判斷依據**：diff 中新增的註解明確指出缺少 invalidation。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢 interval 未在元件 unmount 時正確清理，可能造成記憶體洩漏</summary>

在 `useEffect` 中設定了 `setInterval`，並在 cleanup 函式中 `clearInterval`。但若 effect 因依賴變化而重新執行，舊的 interval 會被清除，新的會被建立，這部分正確。然而，若元件在 interval 執行期間 unmount，cleanup 會執行，但若 interval 回呼正在執行非同步操作（如 `confirmHandle` 中的 `mutateAsync`），該操作可能繼續執行並嘗試更新已 unmount 元件的狀態，導致記憶體洩漏或 React 警告。

**失敗情境**：使用者快速離開頁面，輪詢仍在背景執行，可能觸發 API 呼叫並嘗試更新狀態。

**建議**：在 cleanup 中增加取消機制，例如使用 `AbortController` 或檢查元件是否仍 mounted，並在 mutation 完成後避免 setState。

**判斷依據**：diff 中新增的 setInterval 回呼包含非同步操作，且 cleanup 僅 clearInterval，未處理進行中的非同步操作。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68</code> confirmHandle 使用空依賴陣列，可能捕獲過時的 mutation 函式</summary>

`confirmHandle` 使用 `useCallback` 且依賴陣列為空，但內部呼叫了 `confirmBlueskyHandleMutation.mutateAsync()`。雖然註解聲稱 mutation 是穩定的，但若 mutation 實例因 queryClient 或選項變化而更新，此回呼將永遠使用舊的 mutation，可能導致 API 呼叫失敗或狀態更新錯誤。

**失敗情境**：若 `confirmBlueskyHandleMutation` 的實作依賴於動態變數（如 handle），而該變數在元件生命週期中改變，舊的 mutation 可能使用過時的 handle。

**建議**：將 `confirmBlueskyHandleMutation` 加入依賴陣列，或使用 ref 保存最新 mutation。

**判斷依據**：diff 中新增的 useCallback 依賴陣列為空，但使用了外部 mutation。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 與 disableBluesky 方法缺少回傳型別標註</summary>

`enableBluesky` 和 `disableBluesky` 方法沒有明確的回傳型別，雖然 TypeScript 可以推斷為 `Promise<void>`，但根據專案規範 R08（API Endpoint Controllers Must Have Type Annotations），此處可能違反型別標註要求。

**建議**：明確標註回傳型別為 `Promise<void>`。

**判斷依據**：diff 中新增的方法缺少回傳型別標註。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 10633 (cache hit 9344) ｜ completion tokens 2182 ｜ PR #10</sub>