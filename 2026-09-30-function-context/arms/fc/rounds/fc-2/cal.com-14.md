<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 引入 feature opt-in 的 scope 設定，將原本單一的 HAS_OPT_IN_FEATURES 拆分為 user/team/org 三種，並在 service 層加入 scope 驗證。主要風險在於 `listFeaturesForUser` 的過濾條件疑似寫反（應回傳 globalEnabled 為 true 的項目，但程式碼卻回傳 false），以及 `setUserState` 的 mutation 缺少 await，可能導致錯誤未被正確處理。此外，config.ts 中新增了一個未使用的常數，應移除。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `packages/features/feature-opt-in/services/FeatureOptInService.ts:207` | listFeaturesForUser 過濾條件寫反，導致回傳全域停用的功能 | 0.95 |
| ⚠️ | Major | `packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103` | setUserState mutation 缺少 await，可能導致未處理的 rejection | 0.90 |
| 🔸 | Minor | `packages/features/feature-opt-in/config.ts:5` | 未使用的常數 UNUSED_CONSTANT 應移除 | 0.80 |

<details><summary>🛑 <b>Blocker</b> — <code>packages/features/feature-opt-in/services/FeatureOptInService.ts:207</code> listFeaturesForUser 過濾條件寫反，導致回傳全域停用的功能</summary>

在 `listFeaturesForUser` 中，原本的過濾條件是 `.filter((state) => state.globalEnabled)`，但此 PR 改成了 `.filter((state) => !state.globalEnabled)`。這會讓使用者只看到全域停用的功能，而看不到啟用的功能，完全違反預期行為。

**失敗情境**：當使用者呼叫 `listForUser` API 時，所有全域啟用的 opt-in 功能都會被隱藏，而全域停用的功能反而會出現在列表中。

**建議修法**：將條件改回 `.filter((state) => state.globalEnabled)`。

**判斷依據**：diff 中此行由原本的 `.filter((state) => state.globalEnabled)` 改為 `.filter((state) => !state.globalEnabled)`，且註解仍寫著「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」，明顯矛盾。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103</code> setUserState mutation 缺少 await，可能導致未處理的 rejection</summary>

在 `setUserState` mutation 中，呼叫 `featureOptInService.setUserFeatureState(...)` 時沒有加上 `await`。這會使得該 Promise 的錯誤（例如 scope 驗證失敗的 ErrorWithCode）不會被 tRPC 捕獲，導致客戶端收到成功回應，但實際上狀態並未更新。

**失敗情境**：當使用者嘗試設定一個不屬於 user scope 的功能時，service 會 throw ErrorWithCode，但因為沒有 await，這個錯誤會變成 unhandled promise rejection，而 API 仍回傳 `{ success: true }`。

**建議修法**：加上 `await`，讓錯誤能正確傳播。

**判斷依據**：diff 中此處原本有 `await`，但被移除。其他 mutation（如 setTeamState、setOrganizationState）都保留 `await`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/features/feature-opt-in/config.ts:5</code> 未使用的常數 UNUSED_CONSTANT 應移除</summary>

新增的 `UNUSED_CONSTANT` 常數沒有被任何地方使用，且其名稱暗示這是測試用的殘留程式碼。這會觸發 lint 警告，並增加不必要的維護負擔。

**建議修法**：直接刪除此常數。

**判斷依據**：diff 中新增了此常數，但整個 PR 中沒有其他引用。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16402 (cache hit 16384) ｜ completion tokens 996 ｜ PR #14</sub>