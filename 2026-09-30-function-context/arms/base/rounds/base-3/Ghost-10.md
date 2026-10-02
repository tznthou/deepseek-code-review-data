<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用（enable）再確認 handle（confirm-handle），並更新 API 版本至 v2。主要風險在於前端輪詢邏輯可能造成重複請求或狀態不一致，以及 TypeScript strict 模式被關閉，可能隱藏型別錯誤。建議優先修正輪詢邏輯與恢復 strict 模式。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/activitypub/tsconfig.json:18` | 關閉 TypeScript strict 模式可能隱藏型別錯誤 | 0.90 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能造成重複請求與狀態不一致 | 0.80 |
| 🔸 | Minor | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的 invalidate | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32` | useState 初始化依賴 account 可能導致狀態不同步 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/tsconfig.json:18</code> 關閉 TypeScript strict 模式可能隱藏型別錯誤</summary>

將 `strict` 從 `true` 改為 `false` 會降低型別安全性，可能導致未處理的 null/undefined 或型別錯誤在編譯期未被發現。這與專案原本的嚴格模式慣例相違背，且可能引入潛在的 runtime 錯誤。建議恢復 `strict: true`，並修正任何因此產生的型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能造成重複請求與狀態不一致</summary>

在 `useEffect` 中，當 `account?.blueskyEnabled` 為 true 且 `account?.blueskyHandleConfirmed` 為 false 時，會設定一個 interval 每 5 秒呼叫 `confirmHandle`。但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`，若前一次請求尚未完成，下一次 interval 又會觸發，可能造成多個並行請求。此外，`retryCountRef` 在 interval 內遞增，但若請求失敗（例如網路錯誤），`confirmHandle` 的 promise 會被 reject，但 interval 仍會繼續，可能導致錯誤未被處理且重試次數計算不正確。建議在 `confirmHandle` 中加入防護，例如檢查 mutation 是否正在進行，或使用 `isPending` 狀態來避免重複請求。

**判斷依據**：diff 中新增的 interval 邏輯，`confirmHandle` 沒有檢查 mutation 狀態，且錯誤處理不完整。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的 invalidate</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到「Missing invalidation of accountFollows query that should happen here」。確認 handle 後，帳號的 following 列表可能發生變化（例如自動 follow brid.gy 帳號），但此處未 invalidate 相關查詢，可能導致 UI 顯示過時的 following 資料。建議加入對應的 query invalidation。

**判斷依據**：diff 中新增的註解明確指出缺少 invalidate。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32</code> useState 初始化依賴 account 可能導致狀態不同步</summary>

`const [loading, setLoading] = useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed);` 使用 lazy initializer，但 `account` 可能在元件掛載後才載入，導致初始 loading 狀態不正確。若 `account` 初始為 undefined，loading 會是 false，之後 account 載入後，useEffect 會設定 loading，但可能造成閃爍。建議在 account 載入後再根據其值設定 loading，或使用 useEffect 同步。

**判斷依據**：diff 中新增的 useState 初始化。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 9444 (cache hit 9344) ｜ completion tokens 1190 ｜ PR #10</sub>