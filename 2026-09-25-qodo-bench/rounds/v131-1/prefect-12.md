<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要為 UI v2 的任務執行詳情頁增加與 Vue 版本的對齊功能：新增狀態對應的 favicon、設定頁面標題、調整麵包屑連結、以及重構詳細資訊欄位以顯示「None」而非隱藏。整體改動方向合理，但存在一些潛在問題：favicon hook 未處理不存在的元素或非預期狀態、依賴全域 DOM 結構、以及部分欄位顯示邏輯可能因 falsy 值（如 0）而顯示錯誤。建議修正後再合併。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `ui-v2/src/hooks/use-state-favicon.ts:40` | favicon 元素可能不存在，導致 setAttribute 拋出錯誤 | 0.80 |
| 🔸 | Minor | `ui-v2/src/hooks/use-state-favicon.ts:55` | cleanup 函式可能使用過時的 colorScheme | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88` | Run Count 顯示邏輯可能將 0 顯示為 0，但使用 `\|\|` 可能導致其他 falsy 值顯示錯誤 | 0.70 |
| 🔸 | Minor | `ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179` | Retry Jitter Factor 使用 truthy 檢查可能將 0 顯示為 None | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:40</code> favicon 元素可能不存在，導致 setAttribute 拋出錯誤</summary>

在 `useStateFavicon` 中，`favicon16` 和 `favicon32` 是透過 `document.getElementById` 取得，若 DOM 中沒有對應 id 的元素（例如 index.html 未包含這些元素），則會是 `null`。雖然使用了 optional chaining (`?.`)，但 `setAttribute` 是在 `favicon16?.setAttribute(...)` 中，若 `favicon16` 為 `null`，則不會執行，因此不會拋出錯誤。然而，若元素存在但為非 `<link>` 元素（例如 id 被其他元素佔用），則 `setAttribute` 仍會執行，但可能無效。更重要的問題是：若 `stateType` 為非預期值（例如未來新增的狀態），`faviconPath` 會指向不存在的 SVG 檔案，導致 favicon 載入失敗。建議加入狀態白名單驗證，或提供 fallback。

**判斷依據**：diff 中新增的 hook 直接使用 `document.getElementById` 取得元素，並假設元素存在且為 link 標籤。若 index.html 未包含這些元素，則 `favicon16` 和 `favicon32` 為 `null`，但 optional chaining 避免了錯誤。然而，若元素不存在，favicon 將不會更新，且沒有 fallback 機制。此外，`stateType` 未經驗證，可能導致無效路徑。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/hooks/use-state-favicon.ts:55</code> cleanup 函式可能使用過時的 colorScheme</summary>

在 `useEffect` 的 cleanup 函式中，使用了 `colorScheme` 變數，但該變數是在 effect 執行時計算的。如果使用者在元件掛載期間改變了系統的顏色偏好（例如從 light 切換到 dark），cleanup 函式仍會使用舊的 `colorScheme`，導致重置 favicon 時使用錯誤的預設圖示。建議在 cleanup 中重新取得 colorScheme，或將 colorScheme 加入 dependency array。

**判斷依據**：cleanup 函式閉包捕獲了 `colorScheme`，但該值在 effect 執行時決定，不會隨系統偏好變化而更新。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88</code> Run Count 顯示邏輯可能將 0 顯示為 0，但使用 `||` 可能導致其他 falsy 值顯示錯誤</summary>

在 Run Count 欄位中，使用 `taskRun.run_count || 0` 來顯示。若 `run_count` 為 `0`，則會顯示 `0`，這是正確的。但若 `run_count` 為 `null` 或 `undefined`，也會顯示 `0`，這可能掩蓋了資料缺失的情況。建議使用 `??` 運算子來明確處理 null/undefined，並保留 0 的顯示。

**判斷依據**：diff 中將原本的條件渲染改為直接顯示 `taskRun.run_count || 0`，若 `run_count` 為 `null` 或 `undefined`，會顯示 `0`，可能誤導使用者。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179</code> Retry Jitter Factor 使用 truthy 檢查可能將 0 顯示為 None</summary>

在 Retry Jitter Factor 欄位中，使用 `taskRun.empirical_policy?.retry_jitter_factor ? ... : "None"`。若 `retry_jitter_factor` 為 `0`（合法值），則會顯示 `None`，但實際上應該顯示 `0`。建議改用 `!== null && !== undefined` 或 `??` 來判斷。

**判斷依據**：diff 中將原本的條件渲染改為 truthy 檢查，但 `0` 是 falsy，會導致顯示錯誤。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7532 (cache hit 1408) ｜ completion tokens 1660 ｜ PR #12</sub>