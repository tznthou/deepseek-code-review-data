<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將 `useTeamMembersWithSegment` hook 從 atoms 套件移至 web 模組，以移除 atoms 對 `@calcom/trpc/react` 的依賴。主要風險在於 `EditWeightsForAllTeamMembers` 元件中，原本使用 `filteredMembers` 的渲染邏輯改為直接使用 `teamMembers`，可能導致搜尋過濾功能失效。此外，`AvailabilitySettings` 的型別變更可能造成型別不相容，且新 hook 的查詢條件與資料處理邏輯需進一步驗證。

### Findings（4 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304` | 搜尋過濾功能失效：渲染改用 teamMembers 而非 filteredMembers | 0.95 |
| ⚠️ | Major | `packages/platform/atoms/availability/AvailabilitySettings.tsx:102` | travelSchedules 型別變更可能導致型別不相容 | 0.80 |
| ⚠️ | Major | `apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:16` | 查詢條件可能不正確：teamId 為 0 時仍可能啟用查詢 | 0.75 |
| 🔸 | Minor | `packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:107` | 檔案結尾缺少換行符號 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304</code> 搜尋過濾功能失效：渲染改用 teamMembers 而非 filteredMembers</summary>

原本使用 `filteredMembers` 來渲染成員列表，以支援搜尋過濾功能。此變更改為直接使用 `teamMembers`，導致搜尋輸入不會影響顯示的成員列表。請確認此變更是否為預期行為；若非預期，應保留 `filteredMembers` 的過濾邏輯。

**判斷依據**：diff 中將 `filteredMembers.map` 改為 `teamMembers.map`，且空狀態判斷也從 `filteredMembers.length === 0` 改為 `teamMembers.length === 0`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/platform/atoms/availability/AvailabilitySettings.tsx:102</code> travelSchedules 型別變更可能導致型別不相容</summary>

原本使用 `RouterOutputs["viewer"]["travelSchedules"]["get"]` 型別，現改為 `Awaited<ReturnType<typeof TravelScheduleRepository.findTravelSchedulesByUserId>>`。若 repository 方法的回傳型別與原本的 tRPC 輸出型別不完全一致，可能導致下游元件型別錯誤。請確認兩者結構相同，或考慮保留原始型別並以別名方式引入。

**判斷依據**：diff 中將 `RouterOutputs["viewer"]["travelSchedules"]["get"]` 替換為 `Awaited<ReturnType<typeof TravelScheduleRepository.findTravelSchedulesByUserId>>`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:16</code> 查詢條件可能不正確：teamId 為 0 時仍可能啟用查詢</summary>

查詢的 `enabled` 條件為 `assignRRMembersUsingSegment && !!queryValue && !!teamId`，但傳入的 `teamId` 可能為 0（例如未選擇團隊時），此時 `!!teamId` 為 false，查詢不會執行。然而，在 `useQuery` 的參數中使用了 `teamId: teamId || 0`，若 `teamId` 為 0 且查詢被啟用（例如其他條件為真），則會以 teamId=0 進行查詢，可能導致非預期結果。請確認此邏輯是否符合預期。

**判斷依據**：diff 中新增的 hook 程式碼顯示 `teamId: teamId || 0`，且 `enabled` 條件包含 `!!teamId`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:107</code> 檔案結尾缺少換行符號</summary>

檔案結尾缺少換行符號，可能導致某些工具或 diff 顯示異常。建議在最後一行加上換行。

**判斷依據**：diff 顯示檔案結尾為 `};
\ No newline at end of file`。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4401 (cache hit 1536) ｜ completion tokens 1175 ｜ PR #12</sub>