# 盲標單 6：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part6.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0471

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行）Run Count 顯示邏輯可能將 0 顯示為 0，但使用 `||` 可能導致其他 falsy 值顯示錯誤

> 在 Run Count 欄位中，使用 `taskRun.run_count || 0` 來顯示。若 `run_count` 為 `0`，則會顯示 `0`，這是正確的。但若 `run_count` 為 `null` 或 `undefined`，也會顯示 `0`，這可能掩蓋了資料缺失的情況。建議使用 `??` 運算子來明確處理 null/undefined，並保留 0 的顯示。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## P0472

**GT**（rule）Traditional constructor instead of primary

> The NssDb class uses traditional constructor syntax with repetitive parameter-to-field assignments when primary constructor syntax would be more concise

GT 片段：`private sealed class NssDb ⏎ { ⏎ private readonly string _path; ⏎ private readonly bool _isFirefox;`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:994`，距錨點 0 行）NssDb 類別改寫為傳統屬性，可能違反專案慣例

> 原本的 `NssDb` 使用 primary constructor 與自動實作屬性，現在改為傳統的唯讀屬性與建構子。若專案中普遍使用 primary constructor 或自動實作屬性，此改動可能降低一致性。建議確認專案慣例，若無特殊原因，可保留原本寫法。

finding 片段：`private sealed class NssDb ⏎ { ⏎ private readonly string _path; ⏎ private readonly bool _isFirefox;`

## P0473

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）移除 slack.listen() 可能導致 Slack 服務無法接收事件

> 原本在 `Promise.all` 中有 `slack.listen()`，但修改後被移除。若 Slack 服務需要監聽特定事件（例如發佈通知），移除後可能導致功能失效。請確認 Slack 服務是否已改為其他方式初始化，或此移除是否為有意為之。

finding 片段：`scheduling.init(),`

## P0474

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 23 行）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## P0475

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:132`，距錨點 5 行）Semaphore 未初始化時拋出 RuntimeError 可能導致啟動失敗

> 在 `_replicate_pod_event` 中，若 `_startup_event_semaphore` 為 `None`，會直接拋出 `RuntimeError`。但 `initialize_clients` 是透過 `@kopf.on.startup()` 註冊的，若該函式因故未執行或執行失敗，semaphore 就不會被初始化。此時任何 pod 事件（包括非啟動期間的事件）都會觸發此錯誤，可能導致 observer 無法正常處理事件。建議提供 fallback 行為（例如建立一個預設 semaphore）或更明確的錯誤訊息，並考慮在 `initialize_clients` 中確保 semaphore 一定被建立。

finding 片段：`if _startup_event_semaphore is None: ⏎ raise RuntimeError("Startup event semaphore not initialized")`

## P0476

**GT**（func）Reply threading broken for nested comments due to incorrect in_reply_to_id

> The submit function uses `parent.id` as `in_reply_to_id` instead of `openForm.in_reply_to_id`. For nested replies (replying to a reply), these values differ: `openForm.in_reply_to_id` points to the specific comment being replied to, while `parent.id` points to the top-level parent comment. Using `parent.id` breaks the reply chain, causing nested replies to be incorrectly threaded to the wrong comment. This destroys the conversation hierarchy and makes it impossible to track which comment a user is actually replying to in multi-level discussions.

GT 片段：`const submit = useCallback(async ({html}) => { ⏎ // Send comment to server ⏎ await dispatchAction('addReply', { ⏎ parent: parent,`

**finding**（`apps/comments-ui/src/components/content/forms/reply-form.tsx:30`，距錨點 0 行）in_reply_to_id 改為 parent.id 可能影響回覆邏輯

> 將 `in_reply_to_id` 從 `openForm.in_reply_to_id` 改為 `parent.id`，可能改變回覆的目標。若 `openForm.in_reply_to_id` 原本可能指向不同的父評論（例如回覆回覆），此變更可能導致回覆錯誤。建議確認 parent 是否永遠為正確的回覆目標。

finding 片段：`in_reply_to_id: parent.id,`

## P0477

**GT**（func）Double-wrapping data structure causes matching members to be ignored

> The useTeamMembersWithSegment hook wraps the matchingTeamMembersWithResult in an extra layer when it already has a 'result' property from the trpc query. The trpc query returns { result, troubleshooter, mainWarnings, fallbackWarnings }, but the code creates { result: { result: ... } } by conditionally wrapping it again. This causes useProcessTeamMembersData to receive an incorrectly nested structure where matchingTeamMembersWithResult.result contains an object instead of an array, breaking the segment-based member filtering logic and causing the app to show all team members instead of only those matching the attribute segment.

GT 片段：`const { teamMembers, localWeightsInitialValues } = useProcessTeamMembersData({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:28`，距錨點 0 行）傳給 useProcessTeamMembersData 的 matchingTeamMembersWithResult 型別可能不符

> `useProcessTeamMembersData` 預期 `matchingTeamMembersWithResult` 的型別為 `RouterOutputs['viewer']['attributes']['findTeamMembersMatchingAttributeLogic']`，但此處傳入的 `matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult` 可能導致型別不符。請確認型別定義並修正。

finding 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

## P0478

**GT**（func）ensureMainThread generic function loses return value when dispatched asynchronously

> The generic ensureMainThread<T> function was modified to return T? but has a critical flaw: when not on the main thread, it dispatches the work asynchronously to main queue and immediately returns nil, discarding the actual computation result. This breaks any caller that depends on the return value, as they will always receive nil when called from background threads. The function's contract promises to return the work result but fails to do so in the async dispatch path.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行）ensureMainThread 泛型版本回傳 T? 可能導致呼叫端忽略 nil 而產生邏輯錯誤

> `ensureMainThread<T>` 現在在非主執行緒時回傳 `nil`，但呼叫端可能未處理 nil 而直接使用回傳值，導致非預期的 nil 或崩潰。建議檢查所有呼叫端，確認它們正確處理 nil 情況，或考慮提供非同步版本。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## P0479

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 17 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0480

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行）使用 useSuspenseQuery 但未提供 error boundary

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 error boundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層或應用程式層級加入 error boundary，或改用 `useQuery` 並自行處理錯誤狀態。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## P0481

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 12 行）require 路徑大小寫變更可能導致部署問題

> 檔案從 `MembersAPI.js` 重新命名為 `members-api.js`，但此處的 require 路徑也改為小寫。在大小寫敏感的檔案系統（如 Linux）上，如果部署時未正確處理檔案名稱大小寫，可能導致模組找不到。建議確認 CI/CD 流程能正確處理大小寫變更。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## P0482

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0483

**GT**（func）Race condition from premature TaskCompletionSource recreation

> The _receiveTcs TaskCompletionSource is recreated before checking if the buffer is zero-sized, creating a race condition in the WebSocketWrapper's ReceiveAsync implementation. When a zero-byte read occurs (buffer.Count == 0), the method returns early with the result but the TCS has already been reset. This means if another thread or the background task tries to set a result on the now-recreated TCS while this zero-byte read is in progress, it will affect the next receive operation rather than completing the current one. This breaks the synchronization contract and can cause message loss or out-of-order receives in the stateful reconnection test scenarios where WebSocket message sequencing is critical.

GT 片段：`public override async Task<WebSocketReceiveResult> ReceiveAsync(ArraySegment<byte> buffer, CancellationToken cancellationToken) ⏎ { ⏎ var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408`，距錨點 0 行）`_receiveTcs` 重設時機變更可能影響測試行為

> 在 `WebSocketWrapper.ReceiveAsync` 中，原本在處理零位元組讀取後才重設 `_receiveTcs`，現在改為在 await 後立即重設。這可能導致在零位元組讀取時，新的 `_receiveTcs` 被建立，但後續的 `SetReceiveResult` 可能設定到新的 TCS 上，而測試預期的是舊的 TCS。需要確認此變更是否會造成測試不穩定或失敗。

finding 片段：`var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously); ⏎ // Handle zero-byte reads ⏎ if (buffer.Count == 0)`

## P0484

**GT**（rule）Line exceeds 110 character width

> The rule requires all TypeScript/JavaScript files to use a maximum line width of 110 characters, but this type declaration exceeds this limit at 172 characters

GT 片段：`private helper: AuditActionServiceHelper<typeof RejectedAuditActionService.latestFieldsSchema, typeof RejectedAuditActionService.storedDataSchema>;`

**finding**（`packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19`，距錨點 18 行）RejectedAuditActionService 的 fieldsSchemaV1 變更可能導致既有資料無法解析

> `fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，且 `status` 改為 `BookingStatusChangeSchema`。這可能導致已儲存的 audit log 資料（使用舊 schema）在讀取時解析失敗。

需要確認是否有 migration 或相容性處理。

finding 片段：`const fieldsSchemaV1 = z.object({ ⏎ rejectionReason: z.string().nullable(), ⏎ status: BookingStatusChangeSchema, ⏎ });`

## P0485

**GT**（func）Incorrect requestReschedule flag for seat cancellation webhooks

> The cancelAttendeeSeat function incorrectly sets requestReschedule to true when cancelling individual attendee seats, even though this is not a reschedule request. This flag should be false for regular seat cancellations and only true for actual reschedule requests. External webhook consumers receiving BOOKING_CANCELLED events will incorrectly interpret seat cancellations as reschedule requests, potentially triggering wrong automated workflows, email templates, or business logic in integrated systems.

GT 片段：`const payload: EventPayloadType = { ⏎ ...evt, ⏎ ...eventTypeInfo, ⏎ status: "CANCELLED",`

**finding**（`packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167`，距錨點 0 行）requestReschedule 硬編碼為 true

> 在取消座位（cancelAttendeeSeat）流程中，`requestReschedule` 被硬編碼為 `true`。這可能不正確，因為取消座位不一定代表要求重新排程。建議確認此處的業務邏輯，若取消座位僅是取消單一與會者，應設為 `false`。

finding 片段：`requestReschedule: true,`

## P0486

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）Threshold 輸入未處理 NaN 或小於 1 的值

> Threshold 欄位設定 `min={1}`，但使用者仍可手動輸入 0 或負數，且 `onChange` 直接將值存入表單，沒有驗證。若輸入無效值（如空字串），`Number('')` 會得到 0，可能導致後端驗證錯誤。建議在 onChange 中檢查數值範圍，或依賴表單驗證機制（如 zod schema）來處理。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0487

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 0 行）跨欄位驗證誤用 field_validator，導致 bucket_folder 與 bucket 名稱相同時無法正確驗證

> 在 `_bucket_folder_suffix` 中，使用 `info.data.get("bucket")` 來取得 bucket 欄位，但 `field_validator` 的 `info.data` 只包含已驗證的欄位，且欄位驗證順序不保證 bucket 先被驗證。若 bucket 欄位在 bucket_folder 之後才驗證，則 `info.data.get("bucket")` 會是 None，導致跨欄位驗證失效。應改用 `model_validator(mode='after')` 來進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0488

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:207`，距錨點 5 行）格式化字串參數數量不符

> `detailTextStudiesV2` 與 `detailTextRollouts` 的字串值包含一個 `%@` 佔位符，但 `SettingsTextFormatter` 中的 `formatStudiesText` 與 `formatRolloutsText` 方法僅傳入一個 `appName` 參數，數量相符。然而，`detailTextStudies` 與 `detailTextSendUsageData` 的原始字串也包含 `%@`，但未提供對應的格式化方法，可能導致呼叫端自行格式化時出錯。建議確認所有使用這些字串的程式碼都正確處理了格式化參數。

finding 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

## P0489

**GT**（func）Missing optional chaining causes runtime error when openForm is undefined

> The code accesses `openForm.in_reply_to_snippet` without optional chaining, but openForm can be undefined when rendering certain forms (like the main comment form). The original code correctly used `openForm?.in_reply_to_snippet` with optional chaining. This will cause a "Cannot read property 'in_reply_to_snippet' of undefined" runtime error when the FormWrapper is rendered without an openForm prop, crashing the component.

GT 片段：`let openStyles = ''; ⏎ if (isOpen) { ⏎ const isReplyToReply = !!openForm.in_reply_to_snippet; ⏎ openStyles = isReplyToReply ? 'pl-[1px] pt-[68px] sm:pl-[44px] sm:pt-[56px]' : 'pl-[1px] pt-[48px] sm:pl-[44px] sm:pt-[40px]';`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:313`，距錨點 0 行）openForm 可能為 null 時直接存取 in_reply_to_snippet 可能拋出錯誤

> 在 `const isReplyToReply = !!openForm.in_reply_to_snippet;` 中，若 `openForm` 為 null 或 undefined，則會拋出 TypeError。原本程式碼使用 `openForm?.in_reply_to_snippet` 可選串連，此變更移除了安全保護。建議保留可選串連或確保 openForm 永遠不為 null。

finding 片段：`const isReplyToReply = !!openForm.in_reply_to_snippet;`

## P0490

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 20 行）測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時

> captureFrameAndOrigin 會建立真實的 WKWebView 並載入 https://example.com。這使得測試依賴外部網路連線與 WebKit 的實際行為，可能因網路延遲、離線環境或 WebKit 內部變更而失敗或逾時。建議改用 local test server 或注入 mock 的 navigation delegate 來提供所需的 WKFrameInfo 與 WKSecurityOrigin，以提升測試穩定性。

finding 片段：`webView.load(URLRequest(url: url))`

## P0491

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待

> 在 testRequestMediaCaptureSuccess 中，原本的 expectation 是在 decisionHandler 內 fulfill，但修改後 decisionHandler 不再 fulfill，而是在呼叫 subject.webView 後直接呼叫 expectation.fulfill()。這會導致 expectation 在 decisionHandler 被呼叫前就 fulfill，使得 wait(for:) 立即返回，無法驗證 decisionHandler 是否真的被呼叫。若 decisionHandler 未被呼叫，測試仍會通過，失去測試意義。建議將 expectation.fulfill() 移回 decisionHandler 內。

finding 片段：`subject.webView(MockWKWebView(), ⏎ requestMediaCapturePermissionFor: origin, ⏎ initiatedByFrame: frame, ⏎ type: .cameraAndMicrophone,`

## P0492

**GT**（rule）Direct malloc_usable_size instead of zmalloc_size

> The rule requires all memory operations to use Redis zmalloc wrappers (zmalloc_size) instead of direct libc functions (malloc_usable_size)

GT 片段：`/* All kv-objects has at least kvobj header and embedded key */ ⏎ size_t asize = malloc_usable_size((void *)o);`

**finding**（`src/object.c:1239`，距錨點 22 行）quicklist 取樣計算使用錯誤的分母

> 在 quicklist 的記憶體估算中，原本使用 `elecount` 作為平均的分母，但此 PR 改為 `samples`。然而 `samples` 是已取樣的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會高估每個元素的平均大小，導致整體記憶體估算偏高。

**失敗情境**：建立一個包含多個元素的 quicklist，每個節點包含多個元素，呼叫 MEMORY USAGE 會得到比實際記憶體用量更高的數值。

**建議**：保留原本的 `elecount` 作為分母，或改為計算每個節點的平均元素數再乘以節點數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0493

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0494

**GT**（rule）New code uses unwrap() on fallible operations

> Added code introduces multiple `unwrap()` calls on fallible operations (`parse().unwrap()`, `set_title(...).unwrap()`, and `build().unwrap()`), which violates the rule prohibiting panics/unwraps in favor of explicit error handling via `Result`.

GT 片段：`let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"), ⏎ tauri::WebviewUrl::External("about:blank".parse().unwrap()),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 13 行）`on_new_window` 回呼僅在桌面平台註冊，可能導致非桌面平台行為不一致

> 原本 `on_new_window` 回呼在所有平台都會註冊，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內。這表示在非桌面平台（如行動裝置）上，新視窗請求將不會被處理，可能導致應用程式無法開啟新視窗。若此為預期行為，建議在文件或註解中說明；否則應考慮保留跨平台支援。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## P0495

**GT**（rule）Force unwrap of URL initializer in tests (third occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待

> 在 testRequestMediaCaptureSuccess 中，原本的 expectation 是在 decisionHandler 內 fulfill，但修改後 decisionHandler 不再 fulfill，而是在呼叫 subject.webView 後直接呼叫 expectation.fulfill()。這會導致 expectation 在 decisionHandler 被呼叫前就 fulfill，使得 wait(for:) 立即返回，無法驗證 decisionHandler 是否真的被呼叫。若 decisionHandler 未被呼叫，測試仍會通過，失去測試意義。建議將 expectation.fulfill() 移回 decisionHandler 內。

finding 片段：`subject.webView(MockWKWebView(), ⏎ requestMediaCapturePermissionFor: origin, ⏎ initiatedByFrame: frame, ⏎ type: .cameraAndMicrophone,`

## P0496

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 0 行）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## P0497

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0498

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 1 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待

> 在 testRequestMediaCaptureSuccess 中，原本的 expectation 是在 decisionHandler 內 fulfill，但修改後 decisionHandler 不再 fulfill，而是在呼叫 subject.webView 後直接呼叫 expectation.fulfill()。這會導致 expectation 在 decisionHandler 被呼叫前就 fulfill，使得 wait(for:) 立即返回，無法驗證 decisionHandler 是否真的被呼叫。若 decisionHandler 未被呼叫，測試仍會通過，失去測試意義。建議將 expectation.fulfill() 移回 decisionHandler 內。

finding 片段：`subject.webView(MockWKWebView(), ⏎ requestMediaCapturePermissionFor: origin, ⏎ initiatedByFrame: frame, ⏎ type: .cameraAndMicrophone,`

## P0499

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行）新增的 v147 結構體可能未被使用

> 在 `String` 擴展中新增了 `struct v147`，其中包含原本屬於 `InactiveTabs` 的本地化字串。但這些字串在程式碼中已不再被引用（因為相關視圖已刪除），可能成為死代碼。若確認不再需要，應一併移除；若仍需要保留以供未來使用，建議加上註解說明。

finding 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString(`

## P0500

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）async setUp 中呼叫 @MainActor async 方法缺少 await

> 在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()`，但該方法已標記為 `@MainActor` 且為 async，此處未加 `await`，將導致編譯錯誤。

建議改為：
```swift
await DependencyHelperMock().bootstrapDependencies()
```

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0501

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊

> 當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0502

**GT**（func）Race condition: semaphore initialized after clients during startup

> The `_startup_event_semaphore` is initialized after the orchestration and events clients are created and started. This creates a race condition where Kubernetes pods detected during the client startup phase can trigger `_replicate_pod_event` calls before the semaphore exists. When `event_type` is `None` (startup scenario), the code checks `if _startup_event_semaphore is None` and raises a RuntimeError. However, pods may be detected immediately after clients start but before the semaphore initialization completes, causing the observer to crash with 'Startup event semaphore not initialized' errors during high pod count scenarios.

GT 片段：`@kopf.on.startup() ⏎ async def initialize_clients(logger: kopf.Logger, **kwargs: Any): ⏎ logger.info("Initializing clients") ⏎ global events_client`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:63`，距錨點 0 行）Semaphore 初始化可能失敗或未涵蓋所有啟動路徑

> `_startup_event_semaphore` 在 `initialize_clients` 中初始化，但若該函式未被呼叫或初始化失敗，後續 `_replicate_pod_event` 會拋出 `RuntimeError`。此外，若 `settings.observer.startup_event_concurrency` 為 0 或負數，`asyncio.Semaphore` 會拋出 `ValueError`，導致啟動失敗。建議在初始化時驗證設定值，並考慮提供預設值或 fallback。

finding 片段：`_startup_event_semaphore = asyncio.Semaphore( ⏎ settings.observer.startup_event_concurrency ⏎ )`

## P0503

**GT**（func）Incorrect event level causes important certificate warnings to be suppressed in non-verbose mode

> When verbose mode is not enabled, the event listener is configured with EventLevel.LogAlways instead of the intended EventLevel.Critical. EventLevel.LogAlways (value 0) actually means all events are enabled, not just critical ones. The original PR intended to show only Critical events in non-verbose mode to suppress routine logging. This bug causes all certificate-related events including verbose debug messages to be displayed in non-verbose mode, flooding users with unnecessary output and making it harder to identify actual problems. This breaks the intended user experience where only critical information should be shown by default.

GT 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

**finding**（`src/Tools/dotnet-dev-certs/src/Program.cs:134`，距錨點 0 行）非 verbose 模式下啟用 LogAlways 可能輸出過多資訊

> 原本只有在 verbose 模式才會啟用事件監聽器，現在非 verbose 模式也會啟用並設定為 `EventLevel.LogAlways`。這可能導致原本只在 verbose 下顯示的 LogAlways 事件（如事件 110、114）在一般執行時也輸出，造成資訊過載。需確認這是否為預期行為。

finding 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

## P0504

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行）`createTFunction` 未處理 `returnObjects` 選項，可能導致依賴此功能的測試失敗

> 在舊的全域 mock 中，當 `options.returnObjects` 為真時，會回傳一個陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`）。新的 `createTFunction` 完全沒有檢查 `returnObjects`，因此會回傳字串。若任何測試或元件依賴此行為（例如使用 `returnObjects: true` 來取得多個翻譯），測試將失敗。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，或確認沒有測試使用此選項。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## P0505

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行）Session 未正確關閉，可能導致連線洩漏

> `ConversationVariableUpdaterImpl.update` 中直接建立 `Session(db.engine)` 但未在方法結束時關閉，也未使用 context manager。若 `session.commit()` 拋出例外，session 不會被關閉，造成連線洩漏。建議使用 `with Session(db.engine) as session:` 確保 session 正確關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0506

**GT**（func）Browser navigation uses Forward() instead of Back() breaking test flow

> In the RedirectEnhancedGetToInternal test, after clicking a link that redirects from /redirect to /scroll-to-hash, the test attempts to verify that browser back navigation works correctly. However, the code calls Browser.Navigate().Forward() instead of Browser.Navigate().Back(). Since there is no forward history (the browser just navigated forward to the current page), Forward() does nothing and the browser remains at /scroll-to-hash. The subsequent assertions expect the browser to be back at /redirect with the "Redirections" heading, but it's still at the redirected page, causing the test to fail. The comment explicitly states "See that 'back' takes you to the place from before the redirection" but the code does the opposite action.

GT 片段：`// See that 'back' takes you to the place from before the redirection ⏎ Browser.Navigate().Forward(); ⏎ Browser.Equal("Redirections", () => _originalH1Element.Text); ⏎ Assert.EndsWith("/subdir/redirect", Browser.Url);`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:113`，距錨點 0 行）瀏覽器導航方向可能錯誤

> 在測試 `RedirectEnhancedGetToInternal` 中，原本使用 `Browser.Navigate().Back()` 來驗證返回上一頁，但此 PR 改為 `Browser.Navigate().Forward()`。若測試情境是驗證「返回」行為，使用 Forward 可能導致測試失敗或驗證錯誤的頁面。請確認此變更是否為預期，或是否應保留 Back。

finding 片段：`Browser.Navigate().Forward();`

## P0507

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:98`，距錨點 3 行）dictStoredKey2Key 可能回傳 NULL 導致後續錯誤

> `dictStoredKey2Key` 直接呼叫 `d->type->keyFromStoredKey(key)`，若該回呼實作可能回傳 NULL（例如錯誤處理），則後續的 hash 或比較函式可能收到 NULL 指標而導致 crash。雖然目前提供的回呼（kvGetKey）不會回傳 NULL，但 API 設計上應考慮防禦。

finding 片段：`return (d->type->keyFromStoredKey) ? d->type->keyFromStoredKey(key) : key;`

## P0508

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足，可能接受無效資料

> 此函式僅檢查 input 是否為物件且 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）或 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 zod 或其他 schema 驗證庫完整驗證所有欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0509

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 未被使用

> 新增的 `SettingsTextFormatter` 類別目前沒有被任何程式碼引用，可能是為了未來使用而預留，但若無計畫使用，建議移除以避免死代碼。

finding 片段：`class SettingsTextFormatter {`

## P0510

**GT**（rule）Traditional constructor instead of primary

> The NssDb class uses traditional constructor syntax with repetitive parameter-to-field assignments when primary constructor syntax would be more concise

GT 片段：`private sealed class NssDb ⏎ { ⏎ private readonly string _path; ⏎ private readonly bool _isFirefox;`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:994`，距錨點 0 行）NssDb 類別改動與主要功能無關，可能引入不必要的風險

> 此 PR 將 `NssDb` 類別從 primary constructor 改為傳統的欄位與建構函式，但此改動與 PR 的主要目的（SSL_CERT_DIR 訊息處理）無關。這可能是不小心包含的變更，或是為了符合某種程式碼風格，但增加了 diff 的複雜度，且可能引入不必要的風險（例如若後續有其他程式碼依賴 primary constructor 的行為）。建議確認此改動是否為必要，若非必要則應移除，以保持 PR 專注於單一目的。

finding 片段：`private sealed class NssDb ⏎ { ⏎ private readonly string _path; ⏎ private readonly bool _isFirefox;`

## P0511

**GT**（rule）Missing private modifier on gleanWrapper

> The rule requires that properties have explicit access control modifiers with 'private' for implementation details. The gleanWrapper property lacks the 'private' modifier, exposing an internal implementation detail that should not be accessible outside the struct.

GT 片段：`struct ToolbarTelemetry { ⏎ let gleanWrapper: GleanWrapper ⏎ init(gleanWrapper: GleanWrapper = DefaultGleanWrapper()) { ⏎ self.gleanWrapper = gleanWrapper`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9`，距錨點 0 行）gleanWrapper 屬性從 private 改為 internal，可能破壞封裝

> 將 `private let gleanWrapper` 改為 `let gleanWrapper` 會讓外部可以存取此屬性，可能不是必要的變更。如果只是為了測試，建議使用其他方式（例如依賴注入或測試專用的 init）。

finding 片段：`let gleanWrapper: GleanWrapper`

## P0512

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行）hasPageActions 判斷使用 leadingPageActionStack 而非 trailingPageActionStack，可能影響分隔線顯示

> 在 `updateToolbarLayout` 中，原本使用 `pageActionStack.arrangedSubviews.isEmpty` 來判斷是否有 page actions，此 PR 改為 `leadingPageActionStack.arrangedSubviews.isEmpty`。但此處的 page actions 可能指的是 trailing page actions（因為分隔線位於 trailing page actions 之前），若 leading page actions 為空但 trailing page actions 非空，分隔線可能錯誤隱藏。請確認此處應使用哪個 stack。

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## P0513

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0514

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0515

**GT**（rule）Unused variable causes compilation warning

> The rule requires that compilation completes successfully with no warnings when -Werror flag is enabled. The code contains an unused variable 'total_ranges' that triggers a compilation warning.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1012`，距錨點 0 行）使用 server.db[0] 可能不正確

> `asmCountKeysInSlots` 函式使用 `server.db[0].keys` 來計算 key 數量，但 Redis 支援多個資料庫（預設 16 個），且 slot 與資料庫無關。若 key 存在於非 0 號資料庫，此函式將無法正確計算。

**失敗情境**：在非預設資料庫（例如 `SELECT 1`）中執行 slot migration，日誌中記錄的 key 數量會不正確。

**建議修法**：確認 slot migration 是否僅考慮 db0，或應遍歷所有資料庫。若僅考慮 db0，應在程式碼中明確註明原因。

finding 片段：`unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎  ⏎ unsigned long long key_count = 0;`

## P0516

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 12 行）selector 長度檢查不足，可能導致 IndexError

> 程式碼檢查 `len(selector) < 2` 後才存取 `selector[0]`，但若 selector 長度為 0 或 1，會觸發 IndexError。雖然有檢查，但檢查在存取之後，實際上 `selector[0]` 在 `len(selector) < 2` 時仍會執行，導致錯誤。應先檢查長度再存取。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## P0517

**GT**（func）Wrong display view type for reader mode action

> The handleShowReaderModeAction function sets the wrong displayView type when the user taps the reader mode button. Instead of setting displayView to '.readerMode' (which would show the reader mode view), it's set to '.readerModeLongPressAction' (which is meant for long-press actions). This causes the wrong UI component to be displayed when users try to activate reader mode, breaking the core reader mode functionality and showing an incorrect action sheet instead of the reader view.

GT 片段：`@MainActor ⏎ private static func handleShowReaderModeAction(state: BrowserViewControllerState, ⏎ action: GeneralBrowserAction) -> BrowserViewControllerState { ⏎ return BrowserViewControllerState(`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566`，距錨點 0 行）displayView 從 .readerMode 改為 .readerModeLongPressAction 可能造成錯誤畫面顯示

> 在 `handleShowReaderModeLongPressAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這可能導致長按閱讀模式按鈕時顯示錯誤的畫面，或造成狀態不一致。請確認此變更是否為筆誤，若不是，請提供對應的測試與說明。

finding 片段：`displayView: .readerModeLongPressAction,`

## P0518

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行）position 呼叫參數格式不一致

> 在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，雖然這在 Rust 中不會導致編譯錯誤，但與專案中其他程式碼的風格不一致。建議改為 `self.window_builder.position(position.x, position.y);`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## P0519

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 7 行）並行建置可能產生相同的 versionCode

> 在 `generate_tauri_properties` 中，讀取舊的 versionCode 後直接加 1 寫入，沒有使用鎖定或原子操作。如果兩個建置同時執行（例如 CI 中並行觸發），它們可能讀到相同的舊值，並產生相同的 versionCode，導致上架衝突。建議使用檔案鎖（例如 `flock`）或將 versionCode 儲存在可原子更新的位置（如資料庫或遠端服務）。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0520

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0521

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 0 行）require 路徑大小寫變更可能導致部署問題

> 檔案從 `MembersAPI.js` 重新命名為 `members-api.js`，但此處的 require 路徑也改為小寫。在大小寫敏感的檔案系統（如 Linux）上，如果部署時未正確處理檔案名稱大小寫，可能導致模組找不到。建議確認 CI/CD 流程能正確處理大小寫變更。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## P0522

**GT**（func）Description field incorrectly trims whitespace

> The work pool edit form now calls .trim() on the description before saving (line 42). This removes any intentional leading or trailing whitespace that users may want to preserve in their work pool descriptions, such as indented text or formatting for markdown. The original PR correctly converted empty strings to null using `||`, but the added .trim() operation inappropriately modifies user input. This breaks the principle of preserving user data as-is unless there's a specific business requirement.

GT 片段：`const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool( ⏎ { ⏎ name: workPool.name,`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41`，距錨點 1 行）表單提交時未檢查欄位是否變更，可能造成不必要的 API 呼叫

> 即使使用者未修改任何欄位，點擊 Save 仍會呼叫 `updateWorkPool`。這可能導致不必要的網路請求，並在 API 端產生無意義的更新。建議使用 `form.formState.isDirty` 來判斷是否真的需要提交，或在提交前比較初始值。

finding 片段：`const handleSubmit = (data: WorkPoolEditFormValues) => { ⏎ const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool(`

## P0523

**GT**（func）Unsafe concurrency annotation on non-thread-safe static property

> The static generator property is marked with nonisolated(unsafe) despite the comment explicitly stating 'ContentBlockerGenerator is not thread safe'. This annotation bypasses Swift 6's concurrency safety checks and allows the non-thread-safe ContentBlockerGenerator to be accessed from multiple isolation domains without protection. This creates a potential data race condition where multiple threads could access the generator simultaneously, leading to undefined behavior, crashes, or data corruption. The unsafe annotation should only be used when the developer can guarantee thread safety through other means, which the comment explicitly contradicts.

GT 片段：`@main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏執行緒安全問題

> `nonisolated(unsafe)` 標註表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 實例並非執行緒安全，可能導致資料競爭。建議確認其內部狀態或改為隔離。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0524

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行）直接使用 ureq::get 可能未套用平台憑證設定

> 在 `download_webview2_offline_installer` 中，直接呼叫 `ureq::get(url)` 而非使用 `base_ureq_agent()`，這可能導致此請求未使用系統憑證，與 PR 目的不一致。建議改用 `base_ureq_agent().get(url)` 以確保一致性。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## P0525

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 0 行）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0526

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 原本的驗證條件為 `if (value <= 0)`，會拒絕 0 或負數。變更後為 `if (value < 0)`，允許 0 值。但屬性文件說明為「strictly positive value」，且錯誤訊息仍為「must be positive」，因此允許 0 可能違反設計意圖。若設定為 0，可能導致保留檔案數為 0，造成所有日誌檔案被刪除或無法保留任何檔案。建議確認此變更是否為預期，若非預期應改回 `<= 0`。

finding 片段：`if (value < 0)`

## P0527

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）SMTP_SSL 建構子可能不支援 local_hostname 參數

> 在 Python 3.10 及更早版本中，smtplib.SMTP_SSL 的 __init__ 方法簽名為 (host='', port=0, local_hostname=None, keyfile=None, certfile=None, timeout=..., ...)，實際上接受 local_hostname 參數。但需確認專案使用的 Python 版本是否支援。若版本過舊，可能導致 TypeError。建議檢查 Python 版本，或改用條件式分別建立 SMTP 與 SMTP_SSL 實例，避免將 local_hostname 傳給不支援的類別。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0528

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0529

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:96`，距錨點 7 行）輪詢 effect 缺少對 disableBlueskyMutation 的依賴

> 在 `useEffect` 中呼叫了 `disableBlueskyMutation.mutateAsync()`，但依賴陣列僅包含 `account?.blueskyEnabled`、`account?.blueskyHandleConfirmed` 和 `confirmHandle`。雖然註解聲稱 mutation 是穩定的，但 React Query 的 mutation 物件在每次 render 時可能重新建立，若其身份改變，effect 可能使用到過時的 mutation 實例，導致錯誤或記憶體洩漏。建議將 `disableBlueskyMutation` 加入依賴陣列，或使用 `useCallback` 穩定其參考。

finding 片段：`// eslint-disable-next-line react-hooks/exhaustive-deps ⏎ }, [account?.blueskyEnabled, account?.blueskyHandleConfirmed, confirmHandle]); // disableBlueskyMutation is stable`

## P0530

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1502`，距錨點 0 行）updateMany 未回傳 { count }，與介面不符

> `BookingRepository.updateMany` 的實作呼叫 `this.prismaClient.booking.updateMany` 後沒有回傳結果，但介面 `IBookingRepository` 定義此方法應回傳 `Promise<{ count: number }>`。這會導致呼叫端（例如 `handleCancelBooking` 中的 `await bookingRepository.updateMany(...)`）取得 `undefined`，若後續程式碼依賴回傳值（例如檢查更新筆數）將發生錯誤。

建議：在實作中回傳 `await this.prismaClient.booking.updateMany(...)` 的結果，或調整介面定義。

finding 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

## P0531

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## P0532

**GT**（func）Missing @MainActor annotation in EditBookmarkViewModelTests

> The EditBookmarkViewModelTests class is missing the @MainActor annotation that was added in the PR for Swift 6 concurrency compliance. This test class uses UI components (UITableView) and interacts with MainActor-isolated types. Without the @MainActor annotation, the tests may experience data races or undefined behavior when accessing MainActor-isolated properties, particularly since the setUp and tearDown methods are now async and the test methods interact with UI components. This violates Swift 6 concurrency requirements and can lead to runtime crashes or unpredictable test behavior.

GT 片段：`class EditBookmarkViewModelTests: XCTestCase { ⏎ let folder = MockFxBookmarkNode(type: .folder, ⏎ guid: "1235", ⏎ position: 1,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11`，距錨點 0 行）移除 @MainActor 標註可能導致 UI 操作在背景執行緒執行

> 此測試類別原本有 @MainActor 標註，但在此 PR 中被移除。若測試方法涉及 UI 操作，移除 @MainActor 可能導致測試在背景執行緒執行，造成不可預期的行為。建議確認此類別是否真的不需要 @MainActor，若需要則應保留。

finding 片段：`class EditBookmarkViewModelTests: XCTestCase {`

## P0533

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 未被使用

> 新增的 `SettingsTextFormatter` 類別目前沒有被任何程式碼引用，可能是為了未來使用而預留，但若無計畫使用，建議移除以避免死代碼。

finding 片段：`class SettingsTextFormatter {`

## P0534

**GT**（rule）Async test method name missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`public async Task CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser(HttpTransportType transportType, string protocolName)`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92`，距錨點 1 行）將測試標記為隔離可能掩蓋真實問題

> 新增 `[QuarantinedTest]` 屬性會使測試在 CI 中暫時停用，可能導致相關錯誤被忽略。若問題未在隔離期間修復，可能累積技術債。建議確認隔離原因並追蹤修復進度。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`

## P0535

**GT**（rule）Types package imports from features

> The rule requires that lower-level packages do not import from higher-level packages. The platform types package should not import from the features package as this violates the dependency hierarchy.

GT 片段：`import { ApiProperty } from "@nestjs/swagger"; ⏎ import { Type } from "class-transformer"; ⏎ import { IsEnum, ValidateNested, IsNumber, IsString, IsOptional, IsUrl } from "class-validator"; ⏎ import { SUCCESS_STATUS, ERROR_STATUS } from "@calcom/platform-constants";`

**finding**（`packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6`，距錨點 0 行）新增未使用的 import BookingRepository

> 此 import 似乎未被使用，可能造成 lint 錯誤。建議移除。

finding 片段：`import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`

## P0536

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 型別轉換可能導致 SQL 錯誤

> 在 SQL 查詢中使用 `${orgId}::bigint`，但 orgId 是 number | undefined。若 orgId 為 undefined，會產生 `undefined::bigint`，在 PostgreSQL 中會導致語法錯誤。應使用 Prisma 的參數化查詢或明確處理 undefined。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0537

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行）require 陳述式缺少分號

> 在此檔案的開頭，多個 require 陳述式被移除行尾分號（例如 `const {Router} = require('express')`）。雖然 JavaScript 的自動分號插入（ASI）通常能正常運作，但這與專案中其他檔案的風格不一致，且可能在某些工具或情境下造成問題。建議保留分號以維持一致性。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0538

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token);`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 3 行）每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## P0539

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 1 行）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0540

**GT**（func）Incorrect initialization order in test setup

> In FeatureFlaggedTestSuite.setUp(), the method calls setUpApp() before setUpExperimentVariables(). However, setUpApp() (line 42-44) directly uses jsonFileName and featureName properties that are initialized by setUpExperimentVariables(). This means setUpApp() will be called with nil or uninitialized values, causing addLaunchArgument() to receive invalid parameters. This breaks the experiment/feature flag configuration for all tests inheriting from FeatureFlaggedTestSuite, resulting in tests running with incorrect or missing feature flags.

GT 片段：`override func setUp() async throws { ⏎ continueAfterFailure = false ⏎ setUpApp()  // Called before setUpExperimentVariables ⏎ setUpExperimentVariables()  // Sets jsonFileName and featureName`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48`，距錨點 0 行）setUp() 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試

> 原本的順序是 `setUpExperimentVariables()` 在 `setUpApp()` 之前，現在被調換。若 setUpExperimentVariables() 依賴 setUpApp() 設定的某些狀態，或反之，可能導致測試行為改變。需確認兩者之間是否有相依性。

finding 片段：`setUpApp() ⏎ setUpExperimentVariables()`

## P0541

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0542

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 8 行）測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時

> captureFrameAndOrigin 會建立真實的 WKWebView 並載入 https://example.com。這使得測試依賴外部網路連線與 WebKit 的實際行為，可能因網路延遲、離線環境或 WebKit 內部變更而失敗或逾時。建議改用 local test server 或注入 mock 的 navigation delegate 來提供所需的 WKFrameInfo 與 WKSecurityOrigin，以提升測試穩定性。

finding 片段：`webView.load(URLRequest(url: url))`

## P0543

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 6 行）缺少對新功能的測試

> 新增的自動遞增邏輯沒有對應的單元測試或整合測試。建議添加測試覆蓋以下情境：首次建置、正常遞增、檔案不存在、檔案格式錯誤、並行建置（如果實作鎖定）等。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0544

**GT**（func）Test-to-implementation mismatch: integration test helper uses Math.round while implementation uses Math.floor

> The integration test file defines a helper function `getExpectedLimit` that uses `Math.round` to calculate expected warmup limits, but the actual implementation uses `Math.floor`. This mismatch will cause test failures because the test expects different values than what the implementation produces. For example, on day 1, the formula produces 237.6, which Math.floor rounds to 237 but Math.round rounds to 238. This inconsistency means tests will fail even though the implementation logic might be correct, blocking the PR from merging successfully.

GT 片段：`const getExpectedLimit = (day) => { ⏎ const start = 200; ⏎ const end = 200000; ⏎ const totalDays = 42;`

**finding**（`ghost/core/test/integration/services/email-service/domain-warming.test.js:302`，距錨點 0 行）測試預期值使用 Math.round 與實作 Math.floor 不一致

> 測試中的 `getExpectedLimit` 使用 `Math.round`，而實作使用 `Math.floor`。這可能導致測試在某些天數下預期值與實際值相差 1，造成測試不穩定或誤報。建議統一使用 `Math.floor` 或調整實作。

finding 片段：`return Math.round(start * Math.pow(end / start, day / (totalDays - 1)));`

## P0545

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:145`，距錨點 0 行）userIds 過濾的權限檢查可能過於嚴格或寬鬆

> 在 `getBookings` 中，當 `filters.userIds` 提供時，程式碼檢查 `filters.userIds.every((userId) => allAccessibleUserIds.includes(userId))`。但 `allAccessibleUserIds` 是從 `getUserIdsAndEmailsFromTeamIds` 取得的，該函數只回傳團隊成員的 ID，不包含組織層級的使用者。若使用者具有組織層級的 booking.read 權限，但目標使用者不是任何團隊成員（例如組織管理員），則此檢查會錯誤地拒絕存取。建議改為使用 `permissionCheckService` 檢查每個 userId 是否在可存取的團隊中，或直接查詢使用者是否屬於可存取的團隊。

finding 片段：`const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

## P0546

**GT**（func）Incorrect deployment filtering breaks full-name matching

> The deployment filtering logic checks `dep.name not in deployment_names` instead of checking `full_name not in deployment_names`. This causes the filter to incorrectly evaluate when users specify deployment names in 'flow-name/deployment-name' format. When a user provides a full deployment name like 'my-flow/production', the code checks if 'production' (the short name) is in the list containing 'my-flow/production', which fails, causing the deployment to enter the fallback matching logic unnecessarily. This breaks the fast-path check and could lead to incorrect filtering behavior where deployments are included or excluded inappropriately.

GT 片段：`# If filtering by deployment name, check the full name matches ⏎ full_name = f"{flow_name}/{dep.name}" ⏎ if deployment_names and dep.name not in deployment_names: ⏎ # Only include if the full name matches (filter was by name parts)`

**finding**（`src/prefect/_sdk/fetcher.py:397`，距錨點 0 行）部署名稱過濾邏輯變更可能導致錯誤匹配

> 原本的過濾條件是 `full_name not in deployment_names`，現在改為 `dep.name not in deployment_names`。這會導致當使用者指定完整名稱（例如 `my-flow/production`）時，`dep.name` 只包含 `production`，因此永遠不會匹配，使得過濾失效。建議改回使用 `full_name` 進行比對，或同時檢查 `full_name` 和 `dep.name`。

finding 片段：`if deployment_names and dep.name not in deployment_names:`

## P0547

**GT**（rule）Missing // MARK: section organization

> The new Swift file defines multiple logical sections (nested delegate type, static helper function) but includes no `// MARK:` comments to delineate them, violating the required section organization rule.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 10 行）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0548

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 可能回傳 undefined，與宣告型別不符

> 函式宣告回傳 URLHistory，但修改後直接回傳 getDefaultUrlHistory() 的結果，而該函式可能回傳 undefined（例如 sessionStorage 中無資料或 JSON 解析失敗）。這可能導致呼叫端在未檢查的情況下存取屬性而拋出錯誤。建議保留原本的條件判斷，或明確處理 undefined 的情況。

finding 片段：`return history;`

## P0549

**GT**（func）Insufficient timeout for paste permission dialog causing test flakiness

> The timeout for the 'Allow Paste' permission dialog button was reduced from 1.5 seconds to 0.5 seconds. This is too short for the iOS permission dialog to appear and be interactable, especially on slower devices or under load. The tapIfExists method waits for the element to exist within the specified timeout before attempting to tap it. A 0.5 second timeout may cause the test to miss the permission dialog entirely, preventing the paste action from completing and causing subsequent assertions to fail when the URL is not populated in the address bar.

GT 片段：`urlBar.pressWithRetry(duration: 2.0, element: pasteAction) ⏎ mozWaitForElementToExist(app.tables["Context Menu"]) ⏎ pasteAction.waitAndTap() ⏎ springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471`，距錨點 0 行）tapIfExists 使用固定 timeout 可能不穩定

> 新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 使用固定 0.5 秒等待系統提示出現。在慢速 CI 或裝置上，提示可能延遲出現，導致 tapIfExists 找不到按鈕而失敗。建議使用較長的 timeout 或改用 `mozWaitForElementToExist` 搭配條件點擊。

finding 片段：`springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

## P0550

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0551

**GT**（rule）Public ensureMainThread<T> lacks documentation comment

> A new/modified public API was introduced/changed without an accompanying triple-slash documentation comment describing its purpose/parameters/return value.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? {`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行）ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理

> `ensureMainThread<T>` 現在在非主執行緒時會回傳 `nil`，但呼叫端可能預期它會同步等待或總是有值。這可能導致呼叫端在未檢查 `nil` 的情況下強制解包，造成執行時期錯誤。建議確認所有呼叫端都正確處理了 `nil`，或考慮提供非同步版本。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## P0552

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0553

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行）移除 filteredMembers 導致顯示未篩選的成員清單

> 原本使用 `filteredMembers` 來根據搜尋條件篩選成員，現在改為直接使用 `teamMembers`，這會導致搜尋功能失效，顯示所有成員。請確認是否有其他機制處理篩選，否則應保留 `filteredMembers` 的計算與使用。

finding 片段：`{teamMembers.map((member) => (`

## P0554

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## P0555

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0556

**GT**（rule）JSON formatting deviates from expected formatter output (indentation removed)

> The PR introduces improperly indented JSON (the 'required' key is moved to column 1). This indicates the JSON was not kept formatted per the repository’s formatting/lint-staged expectations (Biome format for JSON).

GT 片段：`-        "required": [ ⏎ +"required": [`

**finding**（`docs/api-reference/v2/openapi.json:31729`，距錨點 2 行）OpenAPI 文件縮排不一致

> 在 `docs/api-reference/v2/openapi.json` 中，`required` 陣列的縮排從原本的 8 空格變成 0 空格，與其他屬性不一致。雖然不影響 JSON 解析，但可能造成維護上的困擾。建議修正縮排。

finding 片段：`"required": [ ⏎ "id", ⏎ "name", ⏎ "email",`

## P0557

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:97`，距錨點 4 行）dictStoredKey2Key 名稱可能造成混淆

> 函式名稱 `dictStoredKey2Key` 中的 '2' 可能被誤解為 'to'，但實際上它是轉換函式。建議使用更明確的名稱，如 `dictGetKeyFromStoredKey`。

finding 片段：`static const void *dictStoredKey2Key(dict *d, const void *key __stored_key) {`

## P0558

**GT**（rule）Missing trailing newline at end of file

> The diff indicates the file has no trailing newline ("\ No newline at end of file"), which violates standard formatting expectations enforced by formatters/linters.

GT 片段：`};\ No newline at end of file`

**finding**（`packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:107`，距錨點 2 行）檔案結尾缺少換行符號

> 檔案結尾缺少換行符號，可能導致某些工具或 diff 顯示異常。建議在最後一行加上換行。

finding 片段：`}; ⏎ \ No newline at end of file`

## P0559

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0560

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行）MouseButtonState 轉換邏輯反轉

> 在 `From<tray_icon::MouseButtonState>` 的實作中，原本 `Up` 對應 `Up`、`Down` 對應 `Down`，但修改後變成 `Up` 對應 `Down`、`Down` 對應 `Up`，導致滑鼠按鈕狀態完全相反。這會造成依賴此轉換的功能（如系統匣事件處理）判斷錯誤。請將 match 分支改回正確對應。

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## P0561

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 1 行）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## P0562

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）條件判斷邏輯反轉可能導致版本解析錯誤

> 原本的條件 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。這會使得當 lock 檔存在且 crate_lock_packages 非空時才進入鎖定版本解析，否則會回退到其他邏輯。若原本意圖是「當 lock 檔存在但找不到對應套件時才回退」，則此變更可能導致在 lock 檔存在且套件存在時仍使用鎖定版本，但若套件不存在則可能錯誤地使用其他來源。需要確認此變更是否為修正既有 bug，還是引入新問題。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0563

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行）bucket_folder 檢查過於寬鬆，可能跳過必要的前綴處理

> 在 `_resolve_path` 中，使用 `if self.bucket_folder and self.bucket_folder in path:` 來判斷路徑是否已包含 bucket_folder。這個檢查只要路徑中任何位置出現 bucket_folder 字串就會成立，即使 bucket_folder 出現在路徑中間或檔名中，也會錯誤地直接返回原始路徑，導致最終儲存路徑缺少必要的前綴。

例如，若 bucket_folder 為 `results/`，而傳入路徑為 `myresults/file.txt`，則 `self.bucket_folder in path` 為 True，函式會直接返回 `myresults/file.txt`，但正確行為應是加上前綴成為 `results/myresults/file.txt`。

建議改為檢查路徑是否以 bucket_folder 開頭（例如使用 `path.startswith(self.bucket_folder)`），或使用 `PurePosixPath` 進行更精確的比對。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0564

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`
