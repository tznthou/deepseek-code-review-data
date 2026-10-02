# 盲標單：finding 跟 GT 是不是同一個問題

判準（Martian）：**一個 code change 能同時修掉兩者**才算 `same`；同處、相關但講的是別的問題算 `partial`；否則 `no`。
本單刻意不含 confidence、severity。標在 `labels.csv`：`pair,label,note`。

## base-1:cal.com-11:1|cal.com-11#3

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行，候選管道 loc）requestReschedule 預設值不一致

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這會導致同一事件在不同 webhook 版本中收到不同的預設值，可能造成下游系統誤判。建議統一預設值，或明確在 DTO 中必填此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## base-1:cal.com-11:2|cal.com-11#0

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行，候選管道 loc）新增 ENABLE_WEBHOOKS 環境變數可能意外停用 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，則 `webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），則會意外停用所有取消 booking 的 webhook，可能導致下游系統收不到通知。建議確認此環境變數名稱是否專用，或改用更明確的名稱，並在文件中說明。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## base-1:cal.com-11:4|cal.com-11#1

**GT**（func）Incorrect requestReschedule flag for seat cancellation webhooks

> The cancelAttendeeSeat function incorrectly sets requestReschedule to true when cancelling individual attendee seats, even though this is not a reschedule request. This flag should be false for regular seat cancellations and only true for actual reschedule requests. External webhook consumers receiving BOOKING_CANCELLED events will incorrectly interpret seat cancellations as reschedule requests, potentially triggering wrong automated workflows, email templates, or business logic in integrated systems.

GT 片段：`const payload: EventPayloadType = { ⏎ ...evt, ⏎ ...eventTypeInfo, ⏎ status: "CANCELLED",`

**finding**（`packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167`，距錨點 0 行，候選管道 loc）requestReschedule 硬編碼為 true

> 在取消座位（cancelAttendeeSeat）流程中，`requestReschedule` 被硬編碼為 `true`。這可能不正確，因為取消座位不一定代表要求重新排程。建議確認此處的業務邏輯，若取消座位僅是取消單一與會者，應設為 `false`。

finding 片段：`requestReschedule: true,`

## base-1:cal.com-12:1|cal.com-12#2

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行，候選管道 loc）搜尋過濾功能失效：渲染改用 teamMembers 而非 filteredMembers

> 原本使用 `filteredMembers` 來渲染成員列表，以支援搜尋過濾功能。此變更改為直接使用 `teamMembers`，導致搜尋輸入不會影響顯示的成員列表。請確認此變更是否為預期行為；若非預期，應保留 `filteredMembers` 的過濾邏輯。

finding 片段：`{teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))} ⏎ {teamMembers.length === 0 && (`

## base-1:cal.com-12:3|cal.com-12#1

**GT**（func）Double-wrapping data structure causes matching members to be ignored

> The useTeamMembersWithSegment hook wraps the matchingTeamMembersWithResult in an extra layer when it already has a 'result' property from the trpc query. The trpc query returns { result, troubleshooter, mainWarnings, fallbackWarnings }, but the code creates { result: { result: ... } } by conditionally wrapping it again. This causes useProcessTeamMembersData to receive an incorrectly nested structure where matchingTeamMembersWithResult.result contains an object instead of an array, breaking the segment-based member filtering logic and causing the app to show all team members instead of only those matching the attribute segment.

GT 片段：`const { teamMembers, localWeightsInitialValues } = useProcessTeamMembersData({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:16`，距錨點 9 行，候選管道 ident）查詢條件可能不正確：teamId 為 0 時仍可能啟用查詢

> 查詢的 `enabled` 條件為 `assignRRMembersUsingSegment && !!queryValue && !!teamId`，但傳入的 `teamId` 可能為 0（例如未選擇團隊時），此時 `!!teamId` 為 false，查詢不會執行。然而，在 `useQuery` 的參數中使用了 `teamId: teamId || 0`，若 `teamId` 為 0 且查詢被啟用（例如其他條件為真），則會以 teamId=0 進行查詢，可能導致非預期結果。請確認此邏輯是否符合預期。

finding 片段：`teamId: teamId || 0, ⏎ attributesQueryValue: queryValue as AttributesQueryValue, ⏎ _enablePerf: true,`

## base-1:cal.com-12:4|cal.com-12#5

**GT**（rule）Missing trailing newline at end of file

> The diff indicates the file has no trailing newline ("\ No newline at end of file"), which violates standard formatting expectations enforced by formatters/linters.

GT 片段：`};\ No newline at end of file`

**finding**（`packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:107`，距錨點 2 行，候選管道 loc）檔案結尾缺少換行符號

> 檔案結尾缺少換行符號，可能導致某些工具或 diff 顯示異常。建議在最後一行加上換行。

finding 片段：`}; ⏎ \ No newline at end of file`

## base-1:cal.com-13:2|cal.com-13#3

**GT**（func）FeatureOptInService creates isolated containers breaking dependency sharing

> The getFeatureOptInService() function creates a fresh DI container on every call, which then loads its dependencies including FeaturesRepository into that isolated container. This breaks the expected dependency injection pattern where services should share repository instances. When code calls both getFeaturesRepository() and getFeatureOptInService(), they each create separate containers with separate FeaturesRepository instances, leading to inconsistent cached state and duplicated database connections. The FeatureOptInService's repository will have different cached data than repositories retrieved elsewhere, causing unpredictable behavior in feature flag resolution.

GT 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 0 行，候選管道 loc）每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## base-1:cal.com-13:2|cal.com-13#4

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token);`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 3 行，候選管道 loc）每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## base-1:cal.com-13:3|cal.com-13#1

**GT**（func）Container created on every function call breaks singleton pattern

> The getFeaturesRepository() function now creates a new DI container instance on every invocation instead of reusing a module-level singleton container. This causes each call to return a different FeaturesRepository instance with its own PrismaClient connection, breaking the singleton pattern. This leads to database connection pool exhaustion and inconsistent cached state across repository instances, as FeaturesRepository maintains an internal cache for features (line 34 in features.repository.ts checks FeaturesRepository.featuresCache).

GT 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 0 行，候選管道 loc）每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## base-1:cal.com-13:3|cal.com-13#5

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 3 行，候選管道 loc）每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## base-1:cal.com-13:4|cal.com-13#2

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行，候選管道 loc）moduleLoader 的 token 可能與綁定 token 不一致

> 在 `moduleLoader` 中，`token` 被設定為 `moduleToken`，但 `bindModuleToClassOnToken` 的 `token` 參數是 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。這可能導致使用 `moduleLoader.token` 來取得實例時，實際上是取得模組 token 而非服務 token，造成型別或實例錯誤。建議確認 `moduleLoader.token` 應該回傳服務 token 還是模組 token，並保持一致性。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## base-1:cal.com-14:1|cal.com-14#3

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行，候選管道 loc）listFeaturesForUser 過濾條件邏輯錯誤

> 在 `listFeaturesForUser` 方法中，原本的過濾條件是 `state.globalEnabled`，但此 PR 將其改為 `!state.globalEnabled`。這會導致只回傳全域停用的功能，而全域啟用的功能反而被排除。這與方法的文件說明「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」完全相反。

**失敗情境**：當使用者呼叫此方法時，所有全域啟用的功能都不會出現在結果中，而全域停用的功能卻會出現。這將導致使用者介面顯示錯誤的功能列表，或讓使用者無法看到應該可用的功能。

**建議修法**：將條件改回 `state.globalEnabled`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## base-1:cal.com-14:2|cal.com-14#0

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:4`，距錨點 0 行，候選管道 loc）未使用的常數 UNUSED_CONSTANT

> 新增的常數 `UNUSED_CONSTANT` 沒有被任何地方使用，且其名稱暗示這是故意留下的未使用程式碼。這會觸發 lint 警告（如 no-unused-vars），並增加不必要的維護負擔。

**建議修法**：移除該常數及其註解。

finding 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

## base-1:cal.com-15:1|cal.com-15#1

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行，候選管道 loc）Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤

> 原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot.userIds 的型別是 number[]，但此處新定義的 Slot.userIds 為 string[]。這可能導致使用此型別的下游程式碼（例如 apps/web/test/lib/getSchedule/expects.ts）在編譯或執行時出現型別不符的錯誤。請確認實際資料型別，若為 number[] 應修正為 number[]，或若確實為 string[] 則需同步更新所有使用處。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## base-1:cal.com-15:2|cal.com-15#0

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#3

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行，候選管道 ident）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#4

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#6

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#7

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:4|cal.com-15#0

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#3

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#4

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#6

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#7

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-16:1|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 10 行，候選管道 ident）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-1:cal.com-16:1|cal.com-16#2

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 0 行，候選管道 loc）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-1:cal.com-16:1|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 8 行，候選管道 ident）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-1:cal.com-16:2|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 0 行，候選管道 loc）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-1:cal.com-16:2|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行，候選管道 ident）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-1:cal.com-16:3|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 21 行，候選管道 ident）逐字稿端點的 guard 順序可能影響錯誤回應

> 在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## base-1:cal.com-16:3|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 0 行，候選管道 loc）逐字稿端點的 guard 順序可能影響錯誤回應

> 在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## base-1:cal.com-2:1|cal.com-2#1

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:588`，距錨點 0 行，候選管道 loc）hasPendingInviteByUserId 的 accepted 條件寫反

> 方法名稱是 hasPendingInviteByUserId，但查詢條件為 `accepted: true`，這會回傳「已接受」的邀請，而非「待處理」的邀請。這導致呼叫端（onboarding 頁面與 checkOnboardingRedirect）在用戶有已接受邀請時誤判為有 pending invite，進而錯誤 redirect。應改為 `accepted: false`。

finding 片段：`accepted: true,`

## base-1:cal.com-2:2|cal.com-2#2

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行，候選管道 loc）條件由 AND 改為 OR 可能改變既有流程

> 原本只有在同時有 pending invite 且 onboarding-v3 啟用時才導向 personal/settings，現在改成任一條件成立即導向。若 onboarding-v3 啟用但用戶沒有 pending invite，原本會繼續其他流程，現在會直接導向 personal/settings。請確認此行為變更是否符合預期。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) {`

## base-1:cal.com-3:1|cal.com-3#2

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1502`，距錨點 0 行，候選管道 loc）updateMany 未回傳 { count }，與介面不符

> `BookingRepository.updateMany` 的實作呼叫 `this.prismaClient.booking.updateMany` 後沒有回傳結果，但介面 `IBookingRepository` 定義此方法應回傳 `Promise<{ count: number }>`。這會導致呼叫端（例如 `handleCancelBooking` 中的 `await bookingRepository.updateMany(...)`）取得 `undefined`，若後續程式碼依賴回傳值（例如檢查更新筆數）將發生錯誤。

建議：在實作中回傳 `await this.prismaClient.booking.updateMany(...)` 的結果，或調整介面定義。

finding 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

## base-1:cal.com-3:2|cal.com-3#3

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:98`，距錨點 0 行，候選管道 loc）移除 userSelect 中的 locale 欄位可能導致取消流程錯誤

> `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但在 `handleCancelBooking` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。若 `findByIdOrThrow` 使用此 `userSelect`，回傳的 organizer 物件將缺少 `locale`，導致 `organizer.locale` 為 `undefined`，可能觸發錯誤或使用錯誤的預設語言。

建議：確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 `locale` 則應保留該欄位，或改用其他方式取得。

finding 片段：`createdDate: true, ⏎ trialEndsAt: true, ⏎ completedOnboarding: true, ⏎ timeFormat: true,`

## base-1:cal.com-3:3|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:500`，距錨點 0 行，候選管道 loc）updateMany 呼叫未處理回傳值，可能掩蓋錯誤

> 在 `handleCancelBooking` 中，`await bookingRepository.updateMany(...)` 的結果未被使用。若 `updateMany` 實作未正確回傳（如前述 blocker），此處不會察覺錯誤。此外，即使回傳 `{ count }`，也應檢查是否更新了預期的筆數，以確保取消操作成功。

建議：檢查回傳的 `count` 是否符合預期，並在不符合時記錄錯誤或拋出例外。

finding 片段：`await bookingRepository.updateMany({ ⏎ where: { ⏎ recurringEventId, ⏎ startTime: {`

## base-1:cal.com-3:4|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:513`，距錨點 0 行，候選管道 loc）findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能遺漏時區處理

> 在 `handleCancelBooking` 中，`findManyIncludeWorkflowRemindersAndReferences` 的 `where` 條件使用 `gte: bookingToDelete.startTime`，但 `bookingToDelete.startTime` 是 Date 物件，可能包含時區資訊。若資料庫儲存的是 UTC，而此處傳入的 Date 未正確轉換，可能導致查詢結果不正確。

建議：確認 `bookingToDelete.startTime` 的時區處理，必要時使用 UTC 時間進行比較。

finding 片段：`const allUpdatedBookings = await bookingRepository.findManyIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ recurringEventId: bookingToDelete.recurringEventId, ⏎ startTime: {`

## base-1:cal.com-3:5|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:546`，距錨點 30 行，候選管道 ident）updateIncludeWorkflowRemindersAndReferences 的 where 條件改為 uid 可能影響行為

> 原本的 `prisma.booking.update` 使用 `where: uid ? { uid } : { id }`，現在改為固定使用 `uid: bookingToDelete.uid`。若 `bookingToDelete.uid` 為空或未定義，將導致查詢失敗。雖然 `bookingToDelete` 應有 uid，但此變更可能影響某些邊界情況。

建議：確認 `bookingToDelete.uid` 一定存在，或保留原本的條件邏輯。

finding 片段：`const updatedBooking = await bookingRepository.updateIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ uid: bookingToDelete.uid, ⏎ },`

## base-1:cal.com-3:6|cal.com-3#2

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行，候選管道 loc）update 方法未使用 select，可能回傳過多資料

> `BookingRepository.update` 方法直接呼叫 `this.prismaClient.booking.update` 而未指定 `select`，可能回傳完整的 Booking 物件，包含不必要的關聯資料，影響效能。若呼叫端只需要部分欄位，建議加入 `select` 參數。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## base-1:cal.com-4:1|cal.com-4#4

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行，候選管道 loc）getDisplayEmail 正規表示式可能誤刪合法郵件中的加號標籤

> `getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除加號後 25 個字元。此模式假設所有加號後綴都是 CUID，但合法郵件地址（如 `user+tag@example.com`）中的加號標籤也會被移除，導致顯示錯誤。例如 `john+notes@example.com` 會變成 `john@example.com`。建議改用更精確的 CUID 格式（例如 `/\+[a-z0-9]{25}$/` 並檢查是否為 CUID），或僅在已知為 OAuth 產生的郵件時才移除。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## base-1:cal.com-4:2|cal.com-4#1

**GT**（func）Lost `this` context in displayGuests mapping causes runtime error

> In the `getOutputBooking` method at line 171, the code passes `this.getDisplayEmail` directly to the `map` function without binding the `this` context. This causes a runtime error because when `getDisplayEmail` is invoked inside the `map` callback, `this` will be `undefined`, resulting in "Cannot read property 'replace' of undefined" or similar errors. The arrow function `(guest: string) => this.getDisplayEmail(guest)` was removed, which was necessary to preserve the `this` binding. This will break all bookings that have guests.

GT 片段：`if ( ⏎ bookingTransformed.bookingFieldsResponses?.guests && ⏎ Array.isArray(bookingTransformed.bookingFieldsResponses.guests) ⏎ ) {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169`，距錨點 0 行，候選管道 model_line）displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## base-1:cal.com-4:2|cal.com-4#5

**GT**（rule）Line(s) exceed the 110 character line width requirement

> The added assignment line is longer than the 110 character limit required by the Biome formatting rules for TS/JS files.

GT 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169`，距錨點 2 行，候選管道 model_line）displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## base-1:cal.com-4:3|cal.com-4#2

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行，候選管道 loc）移除排序可能改變既有 API 行為

> `getOutputRecurringSeatedBookings` 原本會依 `start` 時間排序回傳的預訂，此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳順序不穩定，影響依賴排序的客戶端。若無明確理由，建議保留排序。

finding 片段：`return transformed;`

## base-1:cal.com-4:4|cal.com-4#6

**GT**（rule）JSON formatting deviates from expected formatter output (indentation removed)

> The PR introduces improperly indented JSON (the 'required' key is moved to column 1). This indicates the JSON was not kept formatted per the repository’s formatting/lint-staged expectations (Biome format for JSON).

GT 片段：`-        "required": [ ⏎ +"required": [`

**finding**（`docs/api-reference/v2/openapi.json:31729`，距錨點 2 行，候選管道 model_line）OpenAPI 文件縮排不一致

> 在 `docs/api-reference/v2/openapi.json` 中，`required` 陣列的縮排從原本的 8 空格變成 0 空格，與其他屬性不一致。雖然不影響 JSON 解析，但可能造成維護上的困擾。建議修正縮排。

finding 片段：`"required": [ ⏎ "id", ⏎ "name", ⏎ "email",`

## base-1:cal.com-5:1|cal.com-5#2

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行，候選管道 loc）bookingUrl 解析邏輯可能產生錯誤的顯示前綴

> 在解析 bookingUrl 以取得顯示前綴時，程式碼使用 `url.hostname` 而非 `url.host`，這會忽略埠號。若 bookingUrl 包含非標準埠（例如開發環境），顯示的連結將不正確。此外，若 bookingUrl 為相對路徑或格式不符，`new URL` 會拋出例外，但 catch 區塊僅回退到 `cal.com/${props.username}/`，可能與實際網域不符。建議使用 `url.host` 並考慮更完整的錯誤處理。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ // Get path without the last segment (slug) ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug`

## base-1:cal.com-5:3|cal.com-5#3

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1125`，距錨點 0 行，候選管道 model_line）複製連結功能未使用 bookingUrl，可能導致不一致

> 在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接 `https://cal.com/${username}/${slug}`，而未使用 `eventType.bookingUrl`。這與其他地方的修改不一致，可能導致使用者複製到舊格式的連結。建議統一使用 `eventType.bookingUrl` 或提供一致的 fallback。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## base-1:cal.com-6:1|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行，候選管道 loc）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## base-1:cal.com-6:1|cal.com-6#3

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行，候選管道 loc）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## base-1:cal.com-6:2|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行，候選管道 loc）buildInviteLink 條件判斷反轉

> 原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

finding 片段：`if (isOrgContext) {`

## base-1:cal.com-6:2|cal.com-6#3

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行，候選管道 ident）buildInviteLink 條件判斷反轉

> 原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

finding 片段：`if (isOrgContext) {`

## base-1:cal.com-6:3|cal.com-6#1

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行，候選管道 loc）缺少團隊成員資格驗證

> 控制器使用 `@Roles("TEAM_MEMBER")` 來限制角色，但未驗證使用者是否為該團隊的成員。任何具有 TEAM_MEMBER 角色的使用者（可能是其他團隊的成員）都可以對任意 teamId 建立邀請。應在服務層或控制器中加入團隊成員資格檢查，例如確認使用者與 teamId 的關聯。

finding 片段：`@Roles("TEAM_MEMBER")`

## base-1:cal.com-6:4|cal.com-6#6

**GT**（rule）Line exceeds Biome configured line width

> The codebase formatting rule specifies a 110 character line width. This added line is clearly longer than 110 characters (chained call with long template literal), violating the configured formatting constraints.

GT 片段：`+      const first = await request(app.getHttpServer()).post(`/v2/teams/${team.id}/invite`).expect(200);`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:68`，距錨點 7 行，候選管道 model_line）測試可能因 token 不一致而失敗

> 測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會因為 token 回傳為 identifier 而失敗。此外，非管理員和非成員的測試預期 403，但若控制器未檢查團隊成員資格，這些測試可能不會通過。

finding 片段：`expect(response.body.data.inviteLink).toContain(response.body.data.token);`

## base-1:cal.com-7:1|cal.com-7#2

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行，候選管道 loc）使用 endsWith 過濾可能誤排除合法日曆

> 目前使用 `endsWith` 來排除 externalId 結尾為特定後綴的日曆。若使用者擁有一個自訂日曆，其 externalId 恰好以這些後綴結尾（例如 `mygroup@group.calendar.google.com`），則會被錯誤排除。建議改用更精確的比對方式，例如正規表示式或直接比對完整 ID 模式，或至少確認 Google 日曆 ID 的格式保證這些後綴只出現在通用日曆中。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## base-1:cal.com-8:1|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行，候選管道 ident）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:1|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行，候選管道 model_line）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:1|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行，候選管道 ident）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:2|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行，候選管道 ident）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:2|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行，候選管道 model_line）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:2|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行，候選管道 ident）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:3|cal.com-8#2

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行，候選管道 loc）屬性 badge 合併權重與群組標記，可能影響可讀性

> 原本權重以獨立 badge 顯示，現在合併到 label 中，例如 'Value 80% (group)'，可能讓使用者難以快速區分權重與群組狀態。建議保留分離的 badge 或使用更明確的視覺區分。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## base-1:cal.com-8:4|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行，候選管道 ident）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:4|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行，候選管道 loc）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:4|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行，候選管道 ident）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:5|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行，候選管道 ident）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:5|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行，候選管道 loc）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:5|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行，候選管道 ident）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-9:1|cal.com-9#2

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:53`，距錨點 0 行，候選管道 loc）sortHosts 函式在移動時被意外修改，priority 比較方向反轉

> 在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，原本的 `return priorityB - priorityA;` 被改成了 `return priorityA - priorityB;`（在 `isRRWeightsEnabled` 為 true 且權重相等時）。這會反轉優先權排序，可能導致主機選擇錯誤。

**失敗情境**：當啟用 RR 權重且兩個主機權重相同時，優先權較低（數值較大）的主機會被排在前面，違反預期。

**建議**：將該行改回 `return priorityB - priorityA;`，與原始邏輯一致。

finding 片段：`return priorityA - priorityB;`

## base-1:dify-1:1|dify-1#0

**GT**（rule）Legacy typing imports instead modern syntax

> The rule requires using Python 3.12+ modern type syntax (set[tuple[str, ...]] instead of Set[Tuple[str, ...]]), but the code imports and uses legacy typing module classes Set and Tuple

GT 片段：`from collections.abc import Mapping, Sequence ⏎ from typing import TYPE_CHECKING, Any, Set, Tuple ⏎ ... ⏎ def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行，候選管道 loc）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## base-1:dify-1:1|dify-1#1

**GT**（func）Type mismatch in blocks_variable_output prevents variable blocking

> The blocks_variable_output method compares a Sequence (assigned_variable_selector) directly against a set of tuples (variable_selectors), but fails to convert the Sequence to a tuple first. This type mismatch causes the 'in' check to always return False, meaning the Variable Assigner node will never properly block streaming output of conversation variables. As a result, the response coordinator will incorrectly allow streaming to proceed before conversation variables are updated, violating the intended synchronization logic and potentially showing stale variable values to users.

GT 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool: ⏎ """ ⏎ Check if this Variable Assigner node blocks the output of specific variables. ⏎ Returns True if this node updates any of the requested conversation variables.`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行，候選管道 loc）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## base-1:dify-1:2|dify-1#3

**GT**（func）Test uses list equality instead of tuple conversion for event selector

> The test compares event.selector (which is a Sequence[str]) with a list literal using ==. While this might work in some cases due to Python's sequence equality, it's fragile and inconsistent with the pattern used elsewhere in the codebase. The original code correctly converted to tuple for comparison (tuple(event.selector) == ('conversation', 'conv_var')). This change breaks the filtering logic and will likely cause the test to fail to properly identify conversation variable chunk events, leading to false test failures.

GT 片段：`conv_var_chunk_events = [ ⏎ event ⏎ for event in events ⏎ if isinstance(event, NodeRunStreamChunkEvent) and event.selector == ["conversation", "conv_var"]`

**finding**（`api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75`，距錨點 4 行，候選管道 loc）測試假設所有 chunk 事件的值都等於輸入值，可能過於嚴格

> 測試中 `assert all(event.chunk == input_query for event in conv_var_chunk_events)` 假設每個 chunk 事件的值都完全等於輸入字串。若串流實作將輸入拆分成多個 chunk（例如逐字元），此斷言將失敗。建議改為驗證串接後的值等於輸入值，或放寬為檢查事件存在且值非空。

finding 片段：`assert all(event.chunk == input_query for event in conv_var_chunk_events), ( ⏎ "Expected streamed conversation variable value to match the input query" ⏎ )`

## base-1:dify-10:1|dify-10#2

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行，候選管道 loc）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## base-1:dify-10:1|dify-10#4

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:292`，距錨點 33 行，候選管道 ident）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## base-1:dify-10:2|dify-10#1

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:370`，距錨點 0 行，候選管道 loc）Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲

> 在 `get_plan_bulk_with_cache` 方法中，當 Redis `mget` 失敗時，程式碼會回退到呼叫 `get_plan_bulk` 取得資料，然後仍然嘗試使用 pipeline 將結果寫入 Redis。如果 Redis 持續故障（例如連線中斷），每次呼叫都會執行這個寫入嘗試，而寫入操作本身可能會因為連線問題而阻塞或拋出例外，增加不必要的延遲。

**具體失敗情境**：
1. Redis 服務暫時不可用。
2. 呼叫 `get_plan_bulk_with_cache`，`mget` 拋出例外，進入回退流程。
3. 從 API 取得資料後，嘗試建立 pipeline 並執行 `setex`，但由於 Redis 仍不可用，pipeline 執行失敗，記錄例外。
4. 這個流程在每次呼叫時都會重複，即使 Redis 一直不可用，也會不斷嘗試寫入，浪費資源。

**建議修法**：
- 在 `mget` 失敗時，設定一個標誌（例如 `redis_available = False`），並在後續的寫入步驟中檢查此標誌，若為 `False` 則跳過寫入。
- 或者，將寫入操作包裹在單獨的 `try-except` 中，但考慮到效能，最好在已知 Redis 不可用時完全跳過。

finding 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

## base-1:dify-10:2|dify-10#3

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:370`，距錨點 10 行，候選管道 ident）Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲

> 在 `get_plan_bulk_with_cache` 方法中，當 Redis `mget` 失敗時，程式碼會回退到呼叫 `get_plan_bulk` 取得資料，然後仍然嘗試使用 pipeline 將結果寫入 Redis。如果 Redis 持續故障（例如連線中斷），每次呼叫都會執行這個寫入嘗試，而寫入操作本身可能會因為連線問題而阻塞或拋出例外，增加不必要的延遲。

**具體失敗情境**：
1. Redis 服務暫時不可用。
2. 呼叫 `get_plan_bulk_with_cache`，`mget` 拋出例外，進入回退流程。
3. 從 API 取得資料後，嘗試建立 pipeline 並執行 `setex`，但由於 Redis 仍不可用，pipeline 執行失敗，記錄例外。
4. 這個流程在每次呼叫時都會重複，即使 Redis 一直不可用，也會不斷嘗試寫入，浪費資源。

**建議修法**：
- 在 `mget` 失敗時，設定一個標誌（例如 `redis_available = False`），並在後續的寫入步驟中檢查此標誌，若為 `False` 則跳過寫入。
- 或者，將寫入操作包裹在單獨的 `try-except` 中，但考慮到效能，最好在已知 Redis 不可用時完全跳過。

finding 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

## base-1:dify-11:1|dify-11#3

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行，候選管道 loc）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-1:dify-11:1|dify-11#4

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行，候選管道 ident）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-1:dify-11:1|dify-11#5

**GT**（rule）Broad exception catch (except Exception) added for tool_responses JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type. The new code introduces another broad `except Exception:` while parsing JSON observations.

GT 片段：`if observation_payload: ⏎ try: ⏎ tool_responses = json.loads(observation_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 19 行，候選管道 ident）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-1:dify-11:3|dify-11#0

**GT**（rule）Pydantic v1 Config class usage

> The rule requires data validation to use Pydantic v2 with ConfigDict(extra='forbid'), but this code uses Pydantic v1 'class Config' syntax with 'extra = allow' which permits undeclared fields

GT 片段：`class AgentThoughtValidation(BaseModel): ⏎ """ ⏎ Validation model for agent thought data before database persistence. ⏎ """`

**finding**（`api/core/agent/base_agent_runner.py:64`，距錨點 0 行，候選管道 loc）Pydantic 模型使用舊版 Config 語法

> AgentThoughtValidation 使用 class Config 設定 extra = "allow"，但若專案已升級至 Pydantic v2，應改用 model_config = ConfigDict(extra='allow')。目前註解也提到此點，但未修正。

建議確認 Pydantic 版本，若為 v2 則改用新語法。

finding 片段：`class Config: ⏎ extra = "allow"  # Pydantic v1 syntax - should use ConfigDict(extra='forbid')`

## base-1:dify-12:2|dify-12#1

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行，候選管道 loc）notlike 未傳入 escape 參數，跳脫失效

> 在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致跳脫字元被視為一般字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成搜尋結果不正確，且可能被用於繞過預期的過濾邏輯。

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## base-1:dify-12:3|dify-12#2

**GT**（func）Incorrect escape character in IRIS vector database LIKE query

> The IRIS vector database implementation escapes special characters using backslash (via escape_like_pattern which produces \%, \_, \\) but then specifies ESCAPE '|' in the SQL query instead of ESCAPE '\'. This mismatch causes the database to look for the wrong escape character - it will treat | as the escape character while the string contains backslash escapes. As a result, the escaped special characters won't be properly interpreted, allowing SQL wildcards to remain active and causing search queries with special characters to produce incorrect results or security vulnerabilities.

GT 片段：`escaped_query = escape_like_pattern(query) ⏎ query_pattern = f"%{escaped_query}%" ⏎ sql = f""" ⏎ SELECT TOP {top_k} id, text, meta`

**finding**（`api/core/rag/datasource/vdb/iris/iris_vector.py:298`，距錨點 0 行，候選管道 loc）IRIS 的 LIKE 查詢使用 ESCAPE '|' 但跳脫函式使用反斜線

> 程式碼使用 `escape_like_pattern` 跳脫，該函式以反斜線作為跳脫字元，但 SQL 中指定 `ESCAPE '|'`，兩者不一致。這會導致跳脫字元不被識別，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元。應將 ESCAPE 子句改為 `ESCAPE '\\'` 或修改跳脫函式以使用 `|`。

finding 片段：`WHERE text LIKE ? ESCAPE '|'`

## base-1:dify-13:1|dify-13#0

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行，候選管道 loc）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-1:dify-13:1|dify-13#1

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行，候選管道 loc）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-1:dify-2:1|dify-2#0

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行，候選管道 loc）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## base-1:dify-2:1|dify-2#1

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行，候選管道 loc）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## base-1:dify-2:2|dify-2#3

**GT**（func）JSON schema validation uses non-normalized value

> The validation logic for jsonObject type validates jsonSchemaValue instead of normalizedJsonSchema. This is problematic because normalizedJsonSchema is computed earlier and correctly handles the case where an empty schema should be undefined. By validating jsonSchemaValue directly, the code validates the raw tempPayload value instead of the cleaned version. This inconsistency means that validation may pass but the wrong data could be saved, or validation may fail when it should succeed if the schema is empty but not yet normalized.

GT 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue) ⏎ if (schema?.type !== 'object') {`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:311`，距錨點 0 行，候選管道 loc）jsonSchemaValue 型別檢查不完整，可能跳過驗證

> 在 handleConfirm 中，驗證 JSON Schema 的條件為 `typeof jsonSchemaValue === 'string'`。但 tempPayload.json_schema 的型別可能是物件（例如從 API 載入時），此時若為物件，則不會進行 JSON.parse 和 type 檢查，直接通過驗證。這可能導致非 object 型別的 schema 被儲存。

建議改為：若 jsonSchemaValue 不是字串，先將其轉為字串（例如 JSON.stringify）再進行解析與驗證，或明確處理物件型別。

finding 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue)`

## base-1:dify-3:1|dify-3#1

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:37`，距錨點 0 行，候選管道 loc）render_template 可能回傳 None，導致後續 len() 拋出 TypeError

> 在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 缺少 `'result'` 鍵，`rendered` 會是 `None`，函式直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，會拋出 `TypeError: object of type 'NoneType' has no len()`，且此例外未被捕捉，導致節點執行失敗且無明確錯誤訊息。建議在回傳前檢查 `rendered` 是否為 `None`，若為 `None` 則拋出 `TemplateRenderError`。

finding 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

## base-1:dify-4:1|dify-4#0

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行，候選管道 loc）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## base-1:dify-4:1|dify-4#4

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行，候選管道 loc）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## base-1:dify-4:2|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行，候選管道 loc）在迴圈內呼叫 flush，且 flush 為空實作

> `on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## base-1:dify-4:2|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行，候選管道 loc）在迴圈內呼叫 flush，且 flush 為空實作

> `on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## base-1:dify-4:4|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 0 行，候選管道 loc）selector 長度檢查可能不完整

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## base-1:dify-4:4|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 12 行，候選管道 ident）selector 長度檢查可能不完整

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## base-1:dify-5:1|dify-5#0

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行，候選管道 loc）console.log 可能洩漏使用者輸入資料

> 新增的 `console.log` 會將批次輸入的資料（包含使用者提供的內容）輸出到瀏覽器主控台。這可能導致敏感資訊外洩，且不應存在於正式程式碼中。

建議移除該行。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## base-1:dify-5:2|dify-5#1

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行，候選管道 loc）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## base-1:dify-5:2|dify-5#4

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行，候選管道 loc）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## base-1:dify-5:3|dify-5#3

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行，候選管道 loc）數字輸入框類型從 number 改為 text 可能影響驗證

> 將數字輸入框的 `type` 從 `number` 改為 `text`，可能導致瀏覽器不再自動驗證數字格式，且行動裝置可能顯示不同的鍵盤。若此變更非刻意為之，建議保留 `type="number"`。

finding 片段：`type="text"`

## base-1:dify-6:1|dify-6#0

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:1|dify-6#1

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:1|dify-6#2

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:1|dify-6#3

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:2|dify-6#0

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行，候選管道 loc）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## base-1:dify-6:2|dify-6#1

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:32`，距錨點 0 行，候選管道 loc）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## base-1:dify-6:2|dify-6#3

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行，候選管道 loc）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## base-1:dify-7:1|dify-7#1

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 27 行，候選管道 ident）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-1:dify-7:1|dify-7#2

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 0 行，候選管道 loc）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-1:dify-7:1|dify-7#3

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 0 行，候選管道 loc）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-1:dify-7:2|dify-7#1

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 15 行，候選管道 ident）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## base-1:dify-7:2|dify-7#2

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 3 行，候選管道 loc）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`
