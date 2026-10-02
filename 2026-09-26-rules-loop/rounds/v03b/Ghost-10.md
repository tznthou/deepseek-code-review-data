<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 Bluesky 啟用流程改為兩階段：先啟用，再輪詢確認 handle。主要變更包括 API 端點升級至 v2、新增 confirmBlueskyHandle 方法、前端輪詢邏輯，以及將 tsconfig 的 strict 模式關閉。風險集中在：關閉 strict 模式可能隱藏型別錯誤、前端輪詢邏輯存在競態與資源清理問題、錯誤處理不完整，以及測試覆蓋不足。建議優先修復 strict 模式與輪詢邏輯。

### Findings（7 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/activitypub/tsconfig.json:18` | [R16] 關閉 TypeScript strict 模式 | 0.95 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103` | 輪詢邏輯可能產生競態條件並導致錯誤的狀態更新 | 0.85 |
| ⚠️ | Major | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:104` | 輪詢失敗時自動停用 Bluesky 可能非使用者預期 | 0.80 |
| ⚠️ | Major | `apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833` | 缺少 accountFollows 查詢的失效處理 | 0.75 |
| 🔸 | Minor | `apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:130` | useEffect 依賴陣列不完整可能導致 stale closure | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:711` | enableBluesky 方法未回傳任何值，可能導致呼叫端誤用 | 0.70 |
| 🔸 | Minor | `apps/activitypub/src/api/activitypub.ts:723` | confirmBlueskyHandle 對 null 或非字串回傳值的處理不一致 | 0.70 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/activitypub/tsconfig.json:18</code> [R16] 關閉 TypeScript strict 模式</summary>

將 `strict` 從 `true` 改為 `false` 違反專案規範 R16，且會降低型別安全，可能隱藏潛在的執行時期錯誤。建議恢復 `strict: true` 並修正所有型別錯誤。

**判斷依據**：diff 中 tsconfig.json 的變更：`-    "strict": true,` 改為 `+    "strict": false,`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103</code> 輪詢邏輯可能產生競態條件並導致錯誤的狀態更新</summary>

在 `useEffect` 中，`confirmHandle` 被非同步呼叫，但沒有檢查元件是否已卸載或依賴是否已變更。若使用者在輪詢期間停用 Bluesky 或快速切換，可能導致過時的 Promise 回呼更新狀態，造成 UI 不一致。建議使用取消旗標或 AbortController 來處理非同步操作的取消。

**判斷依據**：diff 中新增的 `useEffect` 區塊，包含 `setInterval` 與非同步呼叫 `confirmHandle`，但未處理元件卸載或依賴變更時的中止。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:104</code> 輪詢失敗時自動停用 Bluesky 可能非使用者預期</summary>

當輪詢達到最大重試次數時，程式碼會自動呼叫 `disableBlueskyMutation.mutateAsync()` 來停用 Bluesky。這可能導致使用者在未明確同意的情況下被停用，且若停用失敗，錯誤未被處理。建議改為顯示錯誤訊息並讓使用者手動決定是否停用。

**判斷依據**：diff 中新增的錯誤處理區塊，自動呼叫 `disableBlueskyMutation.mutateAsync()`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833</code> 缺少 accountFollows 查詢的失效處理</summary>

在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解指出缺少 `accountFollows` 查詢的失效處理。這可能導致相關資料（如追蹤清單）在確認 handle 後未更新，造成 UI 不一致。建議加入對應的 `invalidateQueries` 呼叫。

**判斷依據**：diff 中新增的註解，明確指出缺少失效處理。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:130</code> useEffect 依賴陣列不完整可能導致 stale closure</summary>

`useEffect` 的依賴陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`，但函式內使用了 `disableBlueskyMutation`。雖然註解聲稱其為 stable，但若未來實作變更，可能導致 stale closure。建議明確加入依賴或使用 ref。

**判斷依據**：diff 中新增的 useEffect 依賴陣列，缺少 `disableBlueskyMutation`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:711</code> enableBluesky 方法未回傳任何值，可能導致呼叫端誤用</summary>

`enableBluesky` 方法現在不回傳任何值（`Promise<void>`），但測試中仍以 `await api.enableBluesky()` 呼叫。若未來需要回傳資料，可能需要修改簽名。建議明確標註回傳型別為 `Promise<void>`。

**判斷依據**：diff 中 `enableBluesky` 方法移除回傳型別與回傳值。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/activitypub/src/api/activitypub.ts:723</code> confirmBlueskyHandle 對 null 或非字串回傳值的處理不一致</summary>

`confirmBlueskyHandle` 方法在 `json` 為 null 或 `json.handle` 不存在時回傳空字串，但若 `json.handle` 為非字串（如數字），`String(json.handle)` 會將其轉為字串，可能不符合預期。建議明確驗證型別。

**判斷依據**：diff 中 `confirmBlueskyHandle` 方法的實作。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11763 (cache hit 11648) ｜ completion tokens 1807 ｜ PR #10</sub>