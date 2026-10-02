<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 將 `useTeamMembersWithSegment` hook 從 atoms 套件移至 web 模組，並在 atoms 中保留平台版本（改名為 `useTeamMembersWithSegmentPlatform`）。主要風險在於 `EditWeightsForAllTeamMembers` 元件改用 `teamMembers` 取代 `filteredMembers`，可能導致搜尋過濾功能失效。此外，atoms 套件新增了禁止匯入 `@calcom/trpc/react` 的 lint 規則，但 `useTeamMembersWithSegmentPlatform` 仍直接使用 `trpc`，可能違反新規則。整體改動方向合理，但需確認過濾邏輯與 lint 規則的相容性。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304` | 搜尋過濾功能失效 | 0.90 |
| ⚠️ | Major | `apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:3` | 違反新增的 noRestrictedImports 規則 | 0.80 |
| 🔸 | Minor | `packages/platform/atoms/availability/AvailabilitySettings.tsx:32` | 型別變更可能影響相容性 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304</code> 搜尋過濾功能失效</summary>

原本使用 `filteredMembers` 來顯示經過搜尋過濾的成員列表，現在改為直接使用 `teamMembers`，導致搜尋輸入框的過濾效果消失。若使用者輸入搜尋關鍵字，列表不會更新，可能造成操作錯誤。建議保留 `filteredMembers` 的計算邏輯，或確認此變更為預期行為。

**判斷依據**：diff 中將 `filteredMembers.map` 改為 `teamMembers.map`，且未見其他過濾邏輯調整。

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:3</code> 違反新增的 noRestrictedImports 規則</summary>

此檔案仍匯入 `@calcom/trpc/react`，但 biome.json 新增了針對 atoms 套件的 `noRestrictedImports` 規則，禁止此匯入。這將導致 lint 錯誤，可能阻斷 CI。建議改用其他方式取得 trpc client，或調整規則排除此檔案。

**判斷依據**：diff 中新增的 biome.json 規則明確禁止 `@calcom/trpc/react`，而此檔案未移除該匯入。

</details>

<details><summary>🔸 <b>Minor</b> — <code>packages/platform/atoms/availability/AvailabilitySettings.tsx:32</code> 型別變更可能影響相容性</summary>

將 `travelSchedules` 的型別從 `RouterOutputs["viewer"]["travelSchedules"]["get"]` 改為 `Awaited<ReturnType<typeof TravelScheduleRepository.findTravelSchedulesByUserId>>`。若兩者結構不完全一致，可能導致下游元件型別錯誤。建議確認此變更的相容性，並更新相關測試。

**判斷依據**：diff 中兩處型別替換，未見其他調整。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4365 (cache hit 4352) ｜ completion tokens 807 ｜ PR #12</sub>