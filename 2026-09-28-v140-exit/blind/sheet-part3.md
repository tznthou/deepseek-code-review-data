# 盲標單 3：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part3.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0189

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 2 行）hasInitializedJsComponents 全域旗標可能導致初始化被跳過

> `hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## P0190

**GT**（rule）Async test method name missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`public async Task CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral(HttpTransportType transportType, string protocolName)`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188`，距錨點 1 行）將測試標記為隔離可能掩蓋真實問題

> 新增 `[QuarantinedTest]` 屬性會使測試在 CI 中暫時停用，可能導致相關錯誤被忽略。若問題未在隔離期間修復，可能累積技術債。建議確認隔離原因並追蹤修復進度。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`

## P0191

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行）配置合併行為改變可能導致後續使用不一致

> 原本的程式碼會將合併後的配置直接指派給 `config_metadata.inner`，現在改為將合併配置存入 `extensions`。這可能導致後續程式碼若仍從 `inner` 讀取配置，將無法取得合併後的結果。請確認所有使用 `config_metadata.inner` 的地方是否已同步更新，或此變更是否為預期行為。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## P0192

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致可能導致下游誤判

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 true。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 false。這兩個地方處理同一事件，但預設值相反，可能導致下游系統在未明確提供此欄位時收到不同的值，造成邏輯錯誤。建議統一預設值，或明確在 DTO 中要求此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0193

**GT**（rule）Pydantic v1 Config class usage

> The rule requires data validation to use Pydantic v2 with ConfigDict(extra='forbid'), but this code uses Pydantic v1 'class Config' syntax with 'extra = allow' which permits undeclared fields

GT 片段：`class AgentThoughtValidation(BaseModel): ⏎ """ ⏎ Validation model for agent thought data before database persistence. ⏎ """`

**finding**（`api/core/agent/base_agent_runner.py:64`，距錨點 0 行）Pydantic 模型使用舊版 Config 語法

> AgentThoughtValidation 使用 class Config 設定 extra = "allow"，但若專案已升級至 Pydantic v2，應改用 model_config = ConfigDict(extra='allow')。目前註解也提到此點，但未修正。

建議確認 Pydantic 版本，若為 v2 則改用新語法。

finding 片段：`class Config: ⏎ extra = "allow"  # Pydantic v1 syntax - should use ConfigDict(extra='forbid')`

## P0194

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 3 行）clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## P0195

**GT**（rule）Any type used for selector parameter

> The rule requires using specific types instead of 'any' annotations. The selector parameter uses 'any' instead of a proper function type signature.

GT 片段：`export function usePluginPageContext(selector: any) { ⏎ return useContextSelector(PluginPageContext, selector) ⏎ }`

**finding**（`web/app/components/plugins/plugin-page/context.tsx:51`，距錨點 0 行）selector 參數型別從函式放寬為 any，喪失型別安全

> `usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。這會讓呼叫端可以傳入任意值，若傳入非函式，`useContextSelector` 可能拋出錯誤或產生非預期行為。建議保留原本的函式型別，或使用更精確的泛型。

finding 片段：`export function usePluginPageContext(selector: any) {`

## P0196

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行）callback 的 isEnabled 狀態管理可能導致返回鍵失效

> 在 `handleOnBackPressed` 中，當沒有 listener 且 WebView 無法回上一頁時，會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再設回 `true`。然而，`activity.onBackPressed()` 可能會觸發 Activity 的銷毀或暫停，此時 callback 可能已被移除，重新設為 `true` 可能無效或造成記憶體洩漏。此外，如果 `activity.onBackPressed()` 拋出例外，`isEnabled` 將永遠保持 `false`，導致後續返回鍵完全失效。建議使用 try-finally 確保狀態恢復，或避免直接呼叫 `onBackPressed()`。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## P0197

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `CommentContent` 中的 `useEffect` 僅在掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 載入或狀態變更）。若內容更新後高度改變，`isClamped` 不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0198

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:202`，距錨點 0 行）action.triggered 事件誤用 self._resulting_related_resources，遺漏 triggering-event 關聯

> 在 `fail` 方法中，`action.triggered` 事件的 `related` 參數被設為 `self._resulting_related_resources`，而非包含 triggering-event 的 `related_resources`。這會導致該事件缺少 triggering-event 關聯，破壞追溯鏈。應改為 `related=related_resources`。

finding 片段：`related=self._resulting_related_resources,`

## P0199

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0200

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行）require 陳述式缺少分號

> 在此檔案的開頭，多個 require 陳述式被移除行尾分號（例如 `const {Router} = require('express')`）。雖然 JavaScript 的自動分號插入（ASI）通常能正常運作，但這與專案中其他檔案的風格不一致，且可能在某些工具或情境下造成問題。建議保留分號以維持一致性。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0201

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73`，距錨點 2 行）客戶端過濾可能導致已選取的區塊文件無法顯示

> `filteredData` 使用 `deferredSearch` 進行客戶端過濾，但 `selectedBlockDocument` 是從 `filteredData` 中尋找。若使用者選取了一個區塊文件後，輸入的搜尋字串與該文件名稱不符，則 `selectedBlockDocument` 會變成 `undefined`，導致觸發器顯示「Select a block...」而非已選取的名稱。

**失敗情境**：使用者選取了名為 `my_block_0` 的區塊文件，然後在搜尋框中輸入 `xyz`，此時 `filteredData` 為空，`selectedBlockDocument` 為 `undefined`，觸發器顯示佔位文字，但實際上仍有選取值。

**建議**：`selectedBlockDocument` 應從原始 `data` 中尋找，而非 `filteredData`。

finding 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

## P0202

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行）單筆接受時 oldStatus 硬編碼為 ACCEPTED，可能記錄錯誤的 audit log

> 在 `handleConfirmation` 中，當 `recurringEventId` 不存在時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態，這會導致 audit log 中的 `oldStatus` 不正確。

建議從資料庫查詢 booking 的實際狀態，或使用先前已取得的 `booking.status`。

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## P0203

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）`window_features` 方法中 size 與 position 的設定順序可能影響視窗初始位置

> 在 `window_features` 方法中，原本先設定 position 再設定 size，現在改為先設定 size 再設定 position。在某些平台或視窗管理器中，設定順序可能影響最終視窗位置（例如先設定 size 可能導致 position 被重設）。建議確認此變更不會造成回歸，或考慮保持原有順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0204

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行）移除排序可能改變回應順序

> 在 getOutputRecurringSeatedBookings 方法中，原本有依 start 時間排序的邏輯，但此 PR 移除了該排序（`return transformed.sort(...)` 改為 `return transformed`）。這可能導致回應中的預約順序不再按時間排序，影響客戶端依賴順序的行為。

建議：確認移除排序是否為預期變更，若需維持原有行為，應保留排序。

finding 片段：`return transformed;`

## P0205

**GT**（func）Missing query invalidation after Bluesky handle confirmation causes stale following list

> The confirmBlueskyHandle mutation successfully updates the account cache but fails to invalidate the accountFollows query. When Bluesky is enabled via Bridgy Fed, the account automatically follows the brid.gy account. Both enableBluesky and disableBluesky mutations properly invalidate QUERY_KEYS.accountFollows('index', 'following') to refresh this list, but confirmBlueskyHandle does not. This means after the handle is confirmed, the UI won't show the brid.gy follow relationship until the user manually refreshes the page or navigates away and back. This is inconsistent with the established pattern in the codebase and creates a confusing user experience where the integration appears incomplete.

GT 片段：`onSuccess(blueskyHandle: string) { ⏎ // If the bluesky handle is empty then the handle was not confirmed ⏎ // so we don't need to update the cache ⏎ if (blueskyHandle === '') {`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833`，距錨點 0 行）缺少 accountFollows 查詢的失效處理

> 在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到缺少 `accountFollows` 查詢的失效處理。這可能導致相關資料不同步。建議補上對應的 `queryClient.invalidateQueries`。

finding 片段：`// Note: Missing invalidation of accountFollows query that should happen here`

## P0206

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 型別轉換可能導致 SQL 錯誤或錯誤結果

> 在 `getTeamsWithPBACPermissions` 的 SQL 中，`${orgId}::bigint` 的寫法在 orgId 為 undefined 時會產生 `undefined::bigint`，這在 PostgreSQL 中會導致語法錯誤。即使 orgId 有值，直接將參數內插到 SQL 字串中也存在 SQL injection 風險（雖然 orgId 來自內部，但應使用參數化查詢）。建議改用 Prisma 的參數化查詢，例如 `orgId ? Prisma.sql`${orgId}`` : Prisma.sql`NULL``，或使用 `Prisma.join` 等方式。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0207

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，修改後改為 `expect("File association must have a name")`。若使用者未設定 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定檔中某個 file association 未提供 `name` 且 `ext` 為空陣列，打包時會 panic 並中止。

**建議**：保留原本的 fallback 邏輯，或改用更安全的錯誤處理（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0208

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）write_and_make_executable 先設定權限再寫入可能導致問題

> 函式改為先執行 `fs::set_permissions` 再執行 `fs::write`。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致函式提前返回，檔案永遠不會被建立。此外，即使檔案存在，先設定權限再寫入也可能在寫入過程中因權限不足而失敗。建議維持原本的先寫入再設定權限的順序。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0209

**GT**（func）Double-wrapping data structure causes matching members to be ignored

> The useTeamMembersWithSegment hook wraps the matchingTeamMembersWithResult in an extra layer when it already has a 'result' property from the trpc query. The trpc query returns { result, troubleshooter, mainWarnings, fallbackWarnings }, but the code creates { result: { result: ... } } by conditionally wrapping it again. This causes useProcessTeamMembersData to receive an incorrectly nested structure where matchingTeamMembersWithResult.result contains an object instead of an array, breaking the segment-based member filtering logic and causing the app to show all team members instead of only those matching the attribute segment.

GT 片段：`const { teamMembers, localWeightsInitialValues } = useProcessTeamMembersData({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:16`，距錨點 9 行）查詢條件可能不正確：teamId 為 0 時仍可能啟用查詢

> 查詢的 `enabled` 條件為 `assignRRMembersUsingSegment && !!queryValue && !!teamId`，但傳入的 `teamId` 可能為 0（例如未選擇團隊時），此時 `!!teamId` 為 false，查詢不會執行。然而，在 `useQuery` 的參數中使用了 `teamId: teamId || 0`，若 `teamId` 為 0 且查詢被啟用（例如其他條件為真），則會以 teamId=0 進行查詢，可能導致非預期結果。請確認此邏輯是否符合預期。

finding 片段：`teamId: teamId || 0, ⏎ attributesQueryValue: queryValue as AttributesQueryValue, ⏎ _enablePerf: true,`

## P0210

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateActionStack 的 stacks 合併誤將 pageActionStack 改為 browserActionStack

> 在 `updateActionStack` 方法中，原本合併 `browserActionStack`、`navigationActionStack`、`leadingPageActionStack`、`pageActionStack` 的 arrangedSubviews，但此 PR 將最後一項改為 `browserActionStack`，導致 `trailingPageActionStack`（原 `pageActionStack`）的 arrangedSubviews 未被納入。這會使後續的動畫或可視性更新遺漏 trailing page actions，可能造成 UI 不一致或動畫失效。

建議改回 `trailingPageActionStack.arrangedSubviews`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0211

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 移至 Promise.all 可能改變初始化時序

> 原本 `emailAddressService.init()` 是單獨 await，現在被移入 `Promise.all` 中。若其他服務依賴 emailAddressService 初始化完成，可能造成競態。請確認此變更不會影響相依服務的初始化順序。

finding 片段：`emailAddressService.init(),`

## P0212

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0213

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0214

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:44`，距錨點 9 行）GetMemberInfo 方法可能拋出不明確的例外

> 當表達式不是 MemberExpression 時，會拋出 ArgumentException，但訊息中使用了 `accessorBody.GetType().Name`，這可能不夠明確。建議提供更具體的錯誤訊息，例如包含表達式的實際內容。

finding 片段：`throw new ArgumentException( ⏎ $"The provided expression contains a {accessorBody.GetType().Name} which is not supported. " + ⏎ $"Only simple member accessors (fields, properties) of an object are supported.");`

## P0215

**GT**（rule）Missing ConfigureAwait(false) on Task.Yield

> The rule requires all await expressions in library code (non-test, non-sample projects) to use .ConfigureAwait(false) to avoid capturing the synchronization context, but the await Task.Yield() expression at line 291 omits it.

GT 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 0 行）新增的 Task.Yield() 可能改變登出流程的時序

> 在 ProcessLogOut 中新增 `await Task.Yield();` 會讓出執行緒，可能導致後續的 AuthenticationState 取得延遲，或與其他非同步操作產生競態。若此變更非為了解決特定問題，建議移除；若為必要，請補充說明原因並確保測試涵蓋此情境。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## P0216

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行）inner_size 呼叫參數格式錯誤，可能導致編譯失敗

> 在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這在 Rust 中可能被解析為兩個獨立的 token，導致編譯錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## P0217

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 建立的 robj 未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後未呼叫 decrRefCount 釋放。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。建議在 alsoPropagate 呼叫後立即釋放 argv[2]，或改用其他方式避免手動管理記憶體。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0218

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 strict 模式會大幅降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查選項（包括 `noImplicitAny`、`strictNullChecks` 等），可能隱藏潛在的型別錯誤，導致執行時期錯誤。這通常不是解決型別錯誤的正確方式，應修正具體的型別問題，而不是全域關閉嚴格模式。

finding 片段：`"strict": false,`

## P0219

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:365`，距錨點 10 行）使用 Path.GetFullPath 比較路徑可能因相對路徑或符號連結而誤判

> 在檢查現有 SSL_CERT_DIR 是否已包含憑證目錄時，程式碼使用 `Path.GetFullPath(dir)` 與 `certDirFullPath` 進行比較。然而，`SSL_CERT_DIR` 中的路徑可能是相對路徑，或是包含符號連結，而 `Path.GetFullPath` 只會將相對路徑轉換為絕對路徑，但不會解析符號連結。這可能導致即使實際指向相同目錄，但因為路徑表示不同而被誤判為未包含，進而重複建議設定環境變數，或誤判為已包含而跳過必要的提示。建議使用 `Path.GetFullPath` 後再透過 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `FullName` 來處理符號連結，或使用 `Path.TrimEndingDirectorySeparator` 標準化路徑分隔符號。

finding 片段：`var certDirFullPath = Path.GetFullPath(prettyCertDir); ⏎ var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir))`

## P0220

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 3 行）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## P0221

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 19 行）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## P0222

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 5 行）高量級（400k+）計算邏輯錯誤

> 在 `getWarmupLimit` 中，當 `lastCount >= 400000` 時，程式碼計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 與 `absoluteIncrease = lastCount + 75000`，並回傳兩者最小值。但若 `lastCount` 為 400,000，`scaledIncrease` 為 480,000，`absoluteIncrease` 為 475,000，回傳 475,000，與測試預期的 800,000 不符。此邏輯與註解「cap the increase at 20% or 75k absolute」矛盾，應為 `Math.min(lastCount * 1.2, lastCount + 75000)`，但需確認預期行為。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## P0223

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0224

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈條件錯誤導致堆積緩衝區溢位

> 在 `extractSlotFromKeysResult` 中，迴圈條件 `j <= keys_result->numkeys` 會多執行一次，而 `slot_buffer` 只配置了 `keys_result->numkeys` 個元素，因此最後一次迭代會寫入 `slot_buffer[numkeys]`，造成堆積緩衝區溢位。此外，該次迭代還會讀取 `argv[keys_result->keys[numkeys].pos]`，可能讀取到未初始化的記憶體。

建議將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0225

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行）缺少團隊成員資格驗證

> 控制器使用 `@Roles("TEAM_MEMBER")` 來限制角色，但未驗證使用者是否為該團隊的成員。任何具有 TEAM_MEMBER 角色的使用者（可能是其他團隊的成員）都可以對任意 teamId 建立邀請。應在服務層或控制器中加入團隊成員資格檢查，例如確認使用者與 teamId 的關聯。

finding 片段：`@Roles("TEAM_MEMBER")`

## P0226

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:46`，距錨點 2 行）SQLite 不支援 advisory lock，但程式碼未處理此情況

> 程式碼僅在 dialect 為 postgresql 時執行 advisory lock，但對於 SQLite 等其他資料庫，函式直接返回，沒有提供任何替代的鎖定機制。雖然註解提到 SQLite 會序列化寫入，但這並不能完全防止競態條件，特別是在多程序或多執行緒環境下。建議明確處理 SQLite 的情況，例如使用檔案鎖或依賴資料庫的交易隔離級別，並在文件中說明。

finding 片段：`# SQLite doesn't support advisory locks, but SQLite also serializes writes ⏎ # at the database level, so the race condition is less likely to occur`

## P0227

**GT**（func）Incorrect sequence validation for multiple generic components

> The test validates deserialization of multiple closed generic components but checks that both descriptors have sequence number 0 instead of verifying that the second descriptor has sequence number 1. Component descriptors in a collection must have sequential ordering starting from 0, and this test should verify the second component has sequence 1. This incorrect assertion fails to validate proper sequence ordering, which is critical for component initialization and rendering order in Blazor.

GT 片段：`var secondDescriptor = descriptors[1]; ⏎ Assert.Equal(typeof(GenericTestComponent<string>).FullName, secondDescriptor.ComponentType.FullName); ⏎ Assert.Equal(0, secondDescriptor.Sequence);`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 18 行）參數值型別轉換脆弱

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 Int64。但 `parameters["Value"]` 的實際型別取決於 deserializer 的實作，若其為 `JsonElement` 或 `int`，此轉換可能拋出例外或得到非預期結果。

建議直接斷言參數值的型別與值，例如：
```csharp
var value = Assert.IsType<JsonElement>(parameters["Value"]);
Assert.Equal(42, value.GetInt32());
```

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0228

**GT**（func）Missing query invalidation after Bluesky handle confirmation causes stale following list

> The confirmBlueskyHandle mutation successfully updates the account cache but fails to invalidate the accountFollows query. When Bluesky is enabled via Bridgy Fed, the account automatically follows the brid.gy account. Both enableBluesky and disableBluesky mutations properly invalidate QUERY_KEYS.accountFollows('index', 'following') to refresh this list, but confirmBlueskyHandle does not. This means after the handle is confirmed, the UI won't show the brid.gy follow relationship until the user manually refreshes the page or navigates away and back. This is inconsistent with the established pattern in the codebase and creates a confusing user experience where the integration appears incomplete.

GT 片段：`onSuccess(blueskyHandle: string) { ⏎ // If the bluesky handle is empty then the handle was not confirmed ⏎ // so we don't need to update the cache ⏎ if (blueskyHandle === '') {`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833`，距錨點 0 行）確認 handle 後未 invalidate 相關查詢

> 在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但註解指出缺少 `accountFollows` 查詢的 invalidation。這可能導致 UI 顯示過時的追蹤狀態，例如啟用 Bluesky 後應自動追蹤 brid.gy 帳戶，但相關列表不會更新。建議加入對應的 `queryClient.invalidateQueries` 呼叫。

finding 片段：`// Note: Missing invalidation of accountFollows query that should happen here`

## P0229

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行）Session 未正確關閉，可能導致連線洩漏

> `ConversationVariableUpdaterImpl.update` 中直接建立 `Session(db.engine)` 但未在方法結束時關閉，也未使用 context manager。若 `session.commit()` 拋出例外，session 不會被關閉，造成連線洩漏。建議使用 `with Session(db.engine) as session:` 確保 session 正確關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0230

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0231

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179`，距錨點 2 行）建立失敗時未關閉對話框或提供重試

> `createBlockDocument` 的 `onError` 僅顯示 toast 錯誤，但對話框仍保持開啟，使用者可能重複提交。建議在錯誤時保持對話框開啟，但提供明確的錯誤訊息，或考慮自動關閉。

finding 片段：`onError: (err) => { ⏎ const message = "Unknown error while creating block."; ⏎ toast.error(message); ⏎ console.error(message, err);`

## P0232

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485`，距錨點 36 行）cancelEditMode 條件變更可能導致非網頁 URL 被錯誤保留

> 原本條件 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)` 改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓 reader mode URL 也被保留，但 reader mode URL 並非一般網頁，可能導致取消編輯時網址列顯示 reader mode 的內部 URL，而非使用者預期的內容。建議確認此變更是否為預期行為，若非必要請回復原條件。

finding 片段：`url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`

## P0233

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 15 行）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## P0234

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 0 行）transcripts 端點的 guard 順序與 recordings 不一致

> recordings 端點使用 `@UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`，而 transcripts 端點使用 `@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`。順序不同可能影響錯誤回應（例如未驗證時先觸發 Pbac 而非 ApiAuth）。建議統一順序。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## P0235

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0236

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 3 行）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## P0237

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 可能回傳 undefined，與宣告型別不符

> 函式宣告回傳 URLHistory，但修改後直接回傳 getDefaultUrlHistory() 的結果，而該函式可能回傳 undefined（例如 sessionStorage 中無資料或 JSON 解析失敗）。這可能導致呼叫端在未檢查的情況下存取屬性而拋出錯誤。建議保留原本的條件判斷，或明確處理 undefined 的情況。

finding 片段：`return history;`

## P0238

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行）quicklist 取樣計算使用錯誤的分母

> 在 quicklist 的記憶體估算中，原本使用 `elecount` 作為平均的分母，但此 PR 改為 `samples`。然而 `samples` 是已取樣的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會高估每個元素的平均大小，導致整體記憶體估算偏高。

**失敗情境**：建立一個包含多個元素的 quicklist，每個節點包含多個元素，呼叫 MEMORY USAGE 會得到比實際記憶體用量更高的數值。

**建議**：保留原本的 `elecount` 作為分母，或改為計算每個節點的平均元素數再乘以節點數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0239

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:25`，距錨點 7 行）local_host 為空字串時傳入空字串而非 None

> local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""，若設定為空字串，則 local_host 為空字串。在建構 SMTP 時傳入 local_hostname=local_host or None，但 local_host 為空字串時，local_host or None 會得到 None，因此實際上傳入 None，這部分正確。但後續 opportunistic TLS 模式中，smtp.ehlo(local_host) 會傳入空字串，可能導致 EHLO 命令格式錯誤。建議在呼叫 ehlo 時也使用 local_host or None，或確保 local_host 不為空字串。

finding 片段：`smtp.ehlo(local_host) ⏎ smtp.starttls() ⏎ smtp.ehlo(local_host)`

## P0240

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:416`，距錨點 0 行）webhooksEnabled 為 false 時仍會建立空陣列並呼叫 Promise.all

> 當 `webhooksEnabled` 為 false 時，`promises` 為空陣列，但仍會執行 `await Promise.all(promises)`。雖然功能上無影響，但可讀性較差，且可能讓讀者誤以為仍有非同步操作。建議直接 return 或使用 if 條件包住整個 webhook 發送區塊。

finding 片段：`const promises = webhooksEnabled ? webhooks.map((webhook) =>`

## P0241

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert smtp is not None 為冗餘且可能被最佳化移除

> assert smtp is not None 在建立 SMTP 實例後立即執行，但該實例必定非 None，因此 assert 永遠為真。若使用 python -O 執行，assert 會被移除，不影響功能。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0242

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:149`，距錨點 0 行）在非同步上下文中，`collect_task_run_inputs` 未使用 `await`，可能導致未預期的行為

> 原本的程式碼使用 `await collect_task_run_inputs(v)`，但修改後移除了 `await`。若 `collect_task_run_inputs` 是 async 函式，這會導致回傳 coroutine 而非實際值，造成後續錯誤。請確認該函式是否為同步函式，若不是，應保留 `await`。

finding 片段：`k: collect_task_run_inputs(v) for k, v in parameters.items()`

## P0243

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行）回傳的 token 與實際儲存的 token 不一致

> 在 `createInvite` 中，原本回傳的是隨機產生的 `token`，但現在改為回傳 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位不是真正的邀請 token，而 `inviteLink` 中使用的 token 仍是原始的隨機 token，造成兩者不一致。使用者若使用回傳的 `token` 進行驗證，將無法成功加入團隊。

**建議**：回傳原始的 `token` 變數，而不是 `newToken.identifier`。

finding 片段：`token: newToken.identifier,`

## P0244

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）mark_edge_skipped 順序調整可能影響遞迴邏輯

> 將 `mark_edge_skipped` 移到 `propagate_skip_from_edge` 之後，可能導致在遞迴過程中邊的狀態尚未被標記為 skipped，若遞迴中再次檢查該邊的狀態可能得到不一致的結果。建議確認此順序調整是否為必要，並確保不會影響其他邏輯。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0245

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0246

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行）notarize_inner 中 map_or 邏輯變更可能導致非預期行為

> 原本 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 在 status 為 None 時回傳 `!wait`，現在改為 `wait`。這會影響後續的條件判斷：當 `wait` 為 true 且 status 為 None 時，原本會進入 if 區塊，現在則不會。需要確認此變更是否為預期修正，否則可能導致 notarization 流程在特定情況下被跳過。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## P0247

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同。

建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0248

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行）條件判斷從 OR 改為 AND，導致 JSON 設定檔不再進行驗證

> 原本的條件是當副檔名為 `json` 或 `json5` 時進行驗證，但改為 AND 後，只有副檔名同時為 `json` 和 `json5`（不可能）才會驗證，實際上完全停用了驗證。這會讓所有 JSON 設定檔跳過 schema 驗證，可能導致錯誤的設定被接受。請改回 OR 邏輯。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## P0249

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions

> 在 `create_info_plist` 中，原本的程式碼無條件加入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才加入。這會導致當 `ext` 非空時（正常情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，造成檔案關聯失效。

**失敗情境**：使用者設定 `ext: ["png"]`，產生的 Info.plist 將缺少 `CFBundleTypeExtensions`，macOS 無法將 .png 檔案與應用程式關聯。

**建議**：移除 `if association.ext.is_empty()` 條件，改回無條件加入，或改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0250

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 16 行）Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不更新

> `ClearCache` 方法僅清除了 `_memberInfoCache`，但未清除 `_displayNameCache`。當 Hot Reload 應用程式碼變更時，如果屬性的顯示名稱（例如透過 `DisplayAttribute` 或 `DisplayNameAttribute`）發生變化，快取中的舊值將繼續被使用，導致顯示名稱不正確。建議同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0251

**GT**（func）ASM cron runs before cluster state update causing stale state issues

> The serverCron() function now calls asmCron() before clusterCron(). This is problematic because clusterCron() contains the call to clusterUpdateState() which updates the cluster's operational state (CLUSTER_OK vs CLUSTER_FAIL). ASM (Atomic Slot Migration) operations depend on having an accurate view of the cluster state to make correct migration decisions. By executing asmCron() first, migration tasks may operate on stale cluster state information from the previous iteration, potentially leading to incorrect slot migration decisions, failed migrations, or data consistency issues during cluster rebalancing operations.

GT 片段：`if (server.cluster_enabled) { ⏎ asmCron(); ⏎ clusterCron(); ⏎ }`

**finding**（`src/server.c:1658`，距錨點 0 行）asmCron() 呼叫順序可能影響原子槽遷移

> 原本 asmCron() 在 clusterCron() 內部最後呼叫，現在移到 serverCron 中 clusterCron() 之前。若 asmCron 依賴 clusterCron 更新後的叢集狀態，順序變更可能導致行為錯誤。建議確認 asmCron 的相依性，或維持原本順序。

finding 片段：`asmCron(); ⏎ clusterCron();`

## P0252

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0253

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 建立的 robj 未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後未呼叫 decrRefCount 釋放。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。建議在 alsoPropagate 呼叫後立即釋放 argv[2]，或改用其他方式避免手動管理記憶體。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0254

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1724`，距錨點 3 行）錯誤訊息中使用 %lld 但參數型別為 off_t，可能導致格式不符

> 在 `serverLog` 中使用 `%lld` 格式說明符，但傳入的參數 `(long long)(sb.st_size - valid_up_to)` 和 `(long long)(server.aof_load_broken_max_size)` 已經轉型為 `long long`，因此格式正確。然而，`server.aof_load_broken_max_size` 的型別是 `off_t`，在某些平台上可能是 64 位元，但轉型為 `long long` 是安全的。此處沒有實際問題，但建議保持一致性。

finding 片段：`serverLog(LL_WARNING, ⏎ "AOF loaded anyway because aof-load-broken is enabled and " ⏎ "broken size '%lld' is less than aof-load-broken-max-size '%lld'", ⏎ (long long)(sb.st_size - valid_up_to), (long long)(server.aof_load_broken_max_size));`

## P0255

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 0 行）JWT 簽署移除 noTimestamp 可能影響 token 格式

> `jwt.sign` 原本有 `{noTimestamp: true}`，現在移除後 token 會包含 `iat` 欄位。若 Tinybird 端對 token 格式有特定要求，可能導致驗證失敗。建議確認 Tinybird 是否接受帶有 `iat` 的 token。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0256

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:342`，距錨點 38 行）Redis pipeline 寫入失敗時，快取資料遺失且無重試機制

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，使用 pipeline 批次寫入 Redis。如果 `pipe.execute()` 拋出例外，程式只記錄錯誤，但不會將資料寫入快取，也不會影響回傳值。這會導致下次查詢時仍然 cache miss，增加 API 負載。雖然不影響正確性，但降低了快取效益。

**失敗情境**：Redis 暫時不可用或 pipeline 執行失敗時，所有從 API 取得的資料都不會被快取，下次相同查詢仍會打到 API。

**建議**：考慮加入簡單的重試機制，或在 pipeline 失敗時降級為逐筆寫入（或至少記錄警告）。

finding 片段：`except Exception: ⏎ logger.exception("get_plan_bulk_with_cache: redis pipeline failed")`

## P0257

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 0 行）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## P0258

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:370`，距錨點 10 行）Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲

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

## P0259

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## P0260

**GT**（func）Incorrect logical operator in tearDown causing theme reset to be skipped for all iPad tests

> The tearDown method uses OR (||) instead of AND (&&) when checking if the test should skip theme reset. This causes the theme reset to be skipped for ALL tests running on iPad devices, not just the testSelectBottomPlacement test. The original intent was to skip theme reset only when BOTH conditions are true (the test is testSelectBottomPlacement AND it's running on iPad), but the current code skips it when EITHER condition is true. This will leave the theme in Dark mode after any test runs on iPad, potentially affecting subsequent tests that expect Light theme.

GT 片段：`override func tearDown() async throws { ⏎ if #available(iOS 17.0, *) { ⏎ if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there.`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29`，距錨點 0 行）tearDown 提前 return 可能略過 app.terminate() 與 super.tearDown()

> 在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立時直接 `return`，導致後續的 `app.terminate()` 與 `try await super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的隔離性。建議改為使用 `if` 條件包住主題切換，而不是直接 return，確保清理邏輯總會執行。

finding 片段：`if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there. ⏎ return ⏎ } else {`

## P0261

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0262

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:25`，距錨點 2 行）local_host 為空字串時傳入空字串而非 None

> local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""，若設定為空字串，則 local_host 為空字串。在建構 SMTP 時傳入 local_hostname=local_host or None，但 local_host 為空字串時，local_host or None 會得到 None，因此實際上傳入 None，這部分正確。但後續 opportunistic TLS 模式中，smtp.ehlo(local_host) 會傳入空字串，可能導致 EHLO 命令格式錯誤。建議在呼叫 ehlo 時也使用 local_host or None，或確保 local_host 不為空字串。

finding 片段：`smtp.ehlo(local_host) ⏎ smtp.starttls() ⏎ smtp.ehlo(local_host)`

## P0263

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0264

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）max_length 未定義時批次驗證失效

> 在 `checkBatchInputs` 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 確保有預設值，現在改為直接使用 `varItem.max_length`。若 `max_length` 未定義（例如舊資料或未設定），`item[varIndex].length > undefined` 的結果永遠是 `false`，導致長度驗證完全失效，使用者可以提交任意長度的輸入。

建議：在比較前先檢查 `varItem.max_length` 是否存在，若不存在則跳過驗證或使用其他預設值。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0265

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，修改後改為 `expect("File association must have a name")`。若使用者未設定 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定檔中某個 file association 未提供 `name` 且 `ext` 為空陣列，打包時會 panic 並中止。

**建議**：保留原本的 fallback 邏輯，或改用更安全的錯誤處理（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0266

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行）SMTP_SSL 建構子可能不支援 local_hostname 參數

> 在 Python 3.10 及更早版本中，smtplib.SMTP_SSL 的 __init__ 方法簽名為 (host='', port=0, local_hostname=None, keyfile=None, certfile=None, timeout=..., ...)，實際上接受 local_hostname 參數。但需確認專案使用的 Python 版本是否支援。若版本過舊，可能導致 TypeError。建議檢查 Python 版本，或改用條件式分別建立 SMTP 與 SMTP_SSL 實例，避免將 local_hostname 傳給不支援的類別。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0267

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行）TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤

> 在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但升級後改為使用 `ConfigError::FormatJson`，並將錯誤轉為字串後包裝成 `serde_json::Error`。這會導致錯誤類型不正確，使用者將看到誤導的錯誤訊息（例如「JSON 格式錯誤」而非「TOML 格式錯誤」），且可能丟失錯誤的結構化資訊（如行號、欄位）。建議保留 `ConfigError::FormatToml` 變體，並直接傳遞 `toml::de::Error`。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## P0268

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行）「Name」翻譯從「名字」改為「名稱」可能造成不一致

> 在 portal.json 中，`"Name"` 的翻譯從 `"名字"` 改為 `"名稱"`。但在同檔案的 `"Jamie Larson": "阿宇"` 和 `"jamie@example.com": "ayu@example.com"` 等範例中，可能仍使用「名字」的語境。此外，ghost.json 中 `"Name"` 的翻譯也改為 `"名字"`，可能造成不一致。請確認此變更是否為預期。

finding 片段：`"Name": "名称",`

## P0269

**GT**（func）Inverted reply discard logic causes test infrastructure failure

> The condition for discarding replies is inverted - replies are discarded when count is NOT a multiple of frequency (!=), rather than when it IS a multiple (==). This causes the test to read and discard replies at the wrong times, leading to a buffer overflow of unread replies. The discard_replies_every helper is called throughout the test suite after batches of Redis commands to prevent reply buffer buildup. With this bug, replies accumulate in the buffer instead of being cleared, causing test hangs or failures when the client tries to send new commands with a full reply buffer.

GT 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

**finding**（`tests/unit/memefficiency.tcl:70`，距錨點 0 行）discard_replies_every 函式參數名稱可能造成混淆

> 函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 的語意不夠清晰。`frequency` 代表每多少次觸發一次丟棄，`discard_num` 代表每次丟棄的數量。但呼叫時傳入的數值可能與預期不符，例如在 lpush 的測試中，原本每次丟棄 20000 個 replies，但函式呼叫為 `discard_replies_every $rd $count 10000 20000`，這表示每 10000 次丟棄 20000 個 replies，與原本邏輯相同，但可讀性較差。

建議：考慮重新命名參數或加入註解，以提升可讀性。

finding 片段：`proc discard_replies_every {rd count frequency discard_num} {`

## P0270

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0271

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 0 行）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## P0272

**GT**（rule）Line(s) exceed the 110 character line width requirement

> The added assignment line is longer than the 110 character limit required by the Biome formatting rules for TS/JS files.

GT 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169`，距錨點 2 行）displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## P0273

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）max_length 未定義時批次驗證失效

> 在 `checkBatchInputs` 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 確保有預設值，現在改為直接使用 `varItem.max_length`。若 `max_length` 未定義（例如舊資料或未設定），`item[varIndex].length > undefined` 的結果永遠是 `false`，導致長度驗證完全失效，使用者可以提交任意長度的輸入。

建議：在比較前先檢查 `varItem.max_length` 是否存在，若不存在則跳過驗證或使用其他預設值。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0274

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行）`Dirs` 持有 `&'static Path` 可能導致生命週期問題

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但其實際指向的 `PathBuf` 儲存在 `OnceLock` 中。雖然 `OnceLock` 的內容在程式結束前不會被釋放，因此生命週期上可行，但這會造成記憶體永遠無法回收，且若未來改為非靜態儲存，將導致 dangling reference。建議改為持有 `PathBuf` 或使用 `Arc<Path>`，以避免潛在的生命週期問題。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## P0275

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:16`，距錨點 5 行）IS_DEV 判斷可能在 client bundle 中失效

> `IS_DEV` 從 `@/config` 匯入，若該值在建置時被替換為 `false`，則在 production 環境中 devtools 不會載入，符合預期。但若 `IS_DEV` 是 runtime 判斷（例如依賴 `process.env.NODE_ENV`），在 client bundle 中可能無法正確反映環境，導致 devtools 在 production 中意外載入，或反之在 development 中未載入。建議確認 `IS_DEV` 的實作方式，並考慮在建置時使用 `process.env.NODE_ENV` 進行靜態替換。

finding 片段：`if (!IS_DEV) ⏎ return null`

## P0276

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 17 行）測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時

> captureFrameAndOrigin 會建立真實的 WKWebView 並載入 https://example.com。這使得測試依賴外部網路連線與 WebKit 的實際行為，可能因網路延遲、離線環境或 WebKit 內部變更而失敗或逾時。建議改用 local test server 或注入 mock 的 navigation delegate 來提供所需的 WKFrameInfo 與 WKSecurityOrigin，以提升測試穩定性。

finding 片段：`webView.load(URLRequest(url: url))`

## P0277

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行）單筆 accepted 的 oldStatus 被硬編碼為 ACCEPTED

> 在非 recurring 的 accepted 流程中，`acceptedBookings` 的 `oldStatus` 被直接設定為 `BookingStatus.ACCEPTED`，但實際上 booking 在確認前可能是 `PENDING` 或其他狀態。這會導致 audit log 中的狀態變更記錄不正確。

建議在更新前取得 booking 的原始狀態，例如：
```ts
const oldStatus = booking.status;
// ... 更新 booking ...
acceptedBookings = [{ uid: booking.uid, oldStatus }];
```

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## P0278

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 21 行）逐字稿端點的 guard 順序可能影響錯誤回應

> 在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## P0279

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 12 行）缺少對新功能的測試

> 新增的自動遞增邏輯沒有對應的單元測試或整合測試。建議添加測試覆蓋以下情境：首次建置、正常遞增、檔案不存在、檔案格式錯誤、並行建置（如果實作鎖定）等。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0280

**GT**（func）Incorrect async Task wrapper breaks MainActor isolation in onboarding action handler

> The onActionTap closure is wrapped in a Task block without ensuring MainActor isolation. The OnboardingFlowViewModel expects this closure to be @MainActor isolated, but Task {} creates a new async context that may execute on a different executor. This causes the completion handler and handleAction calls to potentially run off the main thread, leading to concurrency violations and potential crashes when UI updates occur. The original code directly called onboardingService.handleAction which maintained proper MainActor isolation.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in ⏎ guard let onboardingService = self?.onboardingService else { return } ⏎ Task { ⏎ onboardingService.handleAction(`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:274`，距錨點 0 行）將同步閉包改為 Task 可能改變執行順序與時機

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會將原本同步的呼叫變成非同步，可能導致呼叫端預期完成後立即執行的程式碼延後執行，或與其他非同步操作產生競態。此外，Task 未處理取消或錯誤，若 handleAction 拋出錯誤，可能導致未處理的錯誤。建議確認此變更的必要性，並考慮使用 Task { @MainActor in ... } 確保在主執行緒執行，或保留同步呼叫並調整閉包標註。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0281

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 0 行）selector 長度檢查不足，可能導致 IndexError

> 程式碼檢查 `len(selector) < 2` 後才存取 `selector[0]`，但若 selector 長度為 0 或 1，會觸發 IndexError。雖然有檢查，但檢查在存取之後，實際上 `selector[0]` 在 `len(selector) < 2` 時仍會執行，導致錯誤。應先檢查長度再存取。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## P0282

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`
