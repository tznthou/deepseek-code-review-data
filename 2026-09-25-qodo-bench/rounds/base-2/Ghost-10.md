<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用再輪詢確認 handle，並更新 API 端點至 v2。主要風險在於前端輪詢邏輯的競態與資源清理、TypeScript strict 模式被關閉，以及 API 回傳型別與快取更新的一致性。建議優先修正輪詢 effect 的依賴與清理，並恢復 strict 模式。

### Findings（8 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢 effect 缺少 confirmBlueskyHandleMutation 依賴，可能使用過時閉包 | 0.90 |
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式可能隱藏型別錯誤 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107` | 輪詢失敗時呼叫 disableBlueskyMutation 可能觸發非預期的快取更新 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119` | 輪詢 effect 未清理進行中的 mutation，可能導致記憶體洩漏或狀態更新於已卸載元件 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32` | 初始 loading 狀態依賴 account 資料，可能導致閃爍或錯誤的載入指示 | 0.75 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | confirmBlueskyHandle mutation 缺少 accountFollows 查詢的失效處理 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 和 disableBluesky 方法缺少回傳型別標註 | 0.60 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2725` | BlueskyDetails 型別未匯出，可能限制重用性 | 0.50 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢 effect 缺少 confirmBlueskyHandleMutation 依賴，可能使用過時閉包</summary>

useEffect 的依賴陣列僅包含 `account?.blueskyEnabled`, `account?.blueskyHandleConfirmed`, `confirmHandle`，但 `confirmHandle` 內部呼叫了 `confirmBlueskyHandleMutation.mutateAsync()`。若 mutation 函式在元件生命週期中因 queryClient 或 API 實例變更而更新，此 effect 不會重新執行，導致輪詢使用舊的 mutation 函式，可能造成請求發送到錯誤的 API 端點或使用過時的 token。建議將 `confirmBlueskyHandleMutation` 加入依賴陣列，或使用 ref 保存最新的 mutation 函式。

**判斷依據**：useEffect 依賴陣列為 `[account?.blueskyEnabled, account?.blueskyHandleConfirmed, confirmHandle]`，但 `confirmHandle` 使用 `confirmBlueskyHandleMutation`，而該 mutation 未列入依賴。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式可能隱藏型別錯誤</summary>

將 `strict` 從 true 改為 false 會降低型別安全性，可能導致未處理的 null/undefined 錯誤在編譯期未被發現。此變更應有充分理由，否則建議恢復 strict 並修正相關型別錯誤。

**判斷依據**：tsconfig.json 中 `strict` 由 true 改為 false。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107</code> 輪詢失敗時呼叫 disableBlueskyMutation 可能觸發非預期的快取更新</summary>

當輪詢達到最大重試次數時，程式碼呼叫 `disableBlueskyMutation.mutateAsync()` 來停用 Bluesky。但 `disableBlueskyMutation` 的 onSuccess 會將快取中的 `blueskyEnabled` 設為 false，這可能與使用者原本的啟用意圖衝突。若使用者已成功啟用但 handle 確認失敗，此操作會將 UI 狀態改回未啟用，但後端可能仍處於啟用狀態，造成不一致。建議改為呼叫專用的取消或重設 API，或至少在停用前確認後端狀態。

**判斷依據**：在 `retryCountRef.current >= MAX_CONFIRMATION_RETRIES` 分支中呼叫 `disableBlueskyMutation.mutateAsync()`，而該 mutation 的 onSuccess 會更新快取為 `blueskyEnabled: false`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119</code> 輪詢 effect 未清理進行中的 mutation，可能導致記憶體洩漏或狀態更新於已卸載元件</summary>

useEffect 的回傳函式僅清除 interval，但若 interval 觸發的 `confirmHandle()` 正在進行非同步請求，元件卸載後該請求仍可能完成並呼叫 `setHandleConfirmed` 或觸發 mutation 的 onSuccess，造成對已卸載元件的狀態更新。建議使用 AbortController 或追蹤 mounted 狀態，並在清理時取消進行中的請求。

**判斷依據**：useEffect 的 cleanup 僅清除 interval，未處理進行中的 `confirmBlueskyHandleMutation.mutateAsync()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32</code> 初始 loading 狀態依賴 account 資料，可能導致閃爍或錯誤的載入指示</summary>

`useState` 的初始值使用 `account?.blueskyEnabled && !account?.blueskyHandleConfirmed`，但 `account` 在首次渲染時可能尚未載入（undefined），因此初始 loading 為 false。當 account 載入後，useEffect 會根據條件設定 loading，但這可能造成短暫的 UI 閃爍。建議將初始 loading 設為 true，並在 account 載入後再決定是否顯示載入狀態。

**判斷依據**：useState 初始化依賴於非同步取得的 account 資料，可能導致初始狀態不正確。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> confirmBlueskyHandle mutation 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 onSuccess 中，程式碼註解指出缺少 accountFollows 查詢的失效。若 handle 確認後會影響帳號的追蹤關係（例如自動追蹤 brid.gy 帳號），則未失效該查詢可能導致 UI 顯示過時的追蹤狀態。建議加入對應的 query invalidation。

**判斷依據**：程式碼中的註解明確指出缺少 invalidation，且 enable/disable mutation 均有對應的失效處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 和 disableBluesky 方法缺少回傳型別標註</summary>

這兩個方法現在沒有明確的回傳型別，雖然 TypeScript 可以推斷為 Promise<void>，但建議顯式標註以提升可讀性與維護性。

**判斷依據**：方法簽名缺少回傳型別，與其他方法（如 confirmBlueskyHandle）不一致。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2725</code> BlueskyDetails 型別未匯出，可能限制重用性</summary>

`BlueskyDetails` 型別定義在檔案內部但未匯出，若其他模組需要此型別則無法使用。建議匯出以提升可維護性。

**判斷依據**：型別定義未加上 export 關鍵字。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9444 (cache hit 9344) ｜ completion tokens 2136 ｜ PR #10</sub>