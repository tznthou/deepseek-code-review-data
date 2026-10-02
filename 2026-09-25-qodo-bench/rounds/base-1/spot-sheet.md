## base-1:Ghost-1:2|Ghost-1#1

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行，候選管道 loc）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## base-1:Ghost-1:2|Ghost-1#3

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行，候選管道 loc）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## base-1:aspnetcore-1:2|aspnetcore-1#6

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 3 行，候選管道 loc）AppContext.SetSwitch 參數值可能相反

> 在測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 中，原本設定 `DisableThrowNavigationException` 為 `false`，但此 PR 改為 `true`。若測試目的是驗證「不拋出例外」的行為，設定為 `true` 可能導致測試情境與預期相反，進而無法正確驗證。請確認此變更是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-1:aspnetcore-6:1|aspnetcore-6#2

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38`，距錨點 0 行，候選管道 loc）Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException

> 原本的程式碼在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 NavigateToLogin，否則使用 `_tokenResult.RedirectUrl!`。修改後，當 `InteractionOptions != null` 但 `InteractiveRequestUrl` 為 null 時，會直接傳遞 null 給 NavigateToLogin，可能導致 NullReferenceException。建議保留 null 檢查或提供替代邏輯。

finding 片段：`if (_tokenResult.InteractionOptions != null) ⏎ { ⏎ _navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, _tokenResult.InteractionOptions); ⏎ }`

## base-1:aspnetcore-8:1|aspnetcore-8#1

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行，候選管道 loc）將 remarks 寫入 Summary 可能改變既有 API 文件行為

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。這會將 `<remarks>` 的內容放到 OpenAPI 的 `summary` 欄位，而非 `description`。若既有使用者依賴 `description` 來顯示備註，此變更會造成文件內容遺失或錯置。建議確認此變更是否符合預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## base-1:cal.com-11:1|cal.com-11#3

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行，候選管道 loc）requestReschedule 預設值不一致

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這會導致同一事件在不同 webhook 版本中收到不同的預設值，可能造成下游系統誤判。建議統一預設值，或明確在 DTO 中必填此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## base-1:cal.com-16:2|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行，候選管道 ident）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-1:cal.com-6:1|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行，候選管道 loc）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## base-1:cal.com-6:3|cal.com-6#1

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行，候選管道 loc）缺少團隊成員資格驗證

> 控制器使用 `@Roles("TEAM_MEMBER")` 來限制角色，但未驗證使用者是否為該團隊的成員。任何具有 TEAM_MEMBER 角色的使用者（可能是其他團隊的成員）都可以對任意 teamId 建立邀請。應在服務層或控制器中加入團隊成員資格檢查，例如確認使用者與 teamId 的關聯。

finding 片段：`@Roles("TEAM_MEMBER")`

## base-1:cal.com-8:2|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行，候選管道 ident）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:dify-2:1|dify-2#1

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行，候選管道 loc）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

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

## base-1:dify-7:2|dify-7#3

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 0 行，候選管道 loc）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## base-1:firefox-ios-1:2|firefox-ios-1#1

**GT**（func）Incorrect localized string reference in SettingsTextFormatter

> The formatStudiesText method references strings.detailTextStudies instead of strings.detailTextStudiesV2. This causes the formatter to display the old v1 Studies message ('%@ may install and run studies from time to time.') instead of the new v148 message ('%@ randomly selects users to test features, which improves quality for everyone.') that was added in this PR. The helper class was clearly intended to format the new v148 strings based on the PR context, but uses the wrong string constant.

GT 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 5 行，候選管道 loc）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## base-1:firefox-ios-11:1|firefox-ios-11#2

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行，候選管道 loc）updateActionStack 的 stacks 合併誤將 pageActionStack 改為 browserActionStack

> 在 `updateActionStack` 方法中，原本合併 `browserActionStack`、`navigationActionStack`、`leadingPageActionStack`、`pageActionStack` 的 arrangedSubviews，但此 PR 將最後一項改為 `browserActionStack`，導致 `trailingPageActionStack`（原 `pageActionStack`）的 arrangedSubviews 未被納入。這會使後續的動畫或可視性更新遺漏 trailing page actions，可能造成 UI 不一致或動畫失效。

建議改回 `trailingPageActionStack.arrangedSubviews`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## base-1:firefox-ios-3:3|firefox-ios-3#0

**GT**（rule）UI constants not in UX struct

> The rule requires UI constants and magic numbers to be organized within a dedicated nested UX struct, but the button size constant (40) is hardcoded directly in the constraint definitions instead of being defined in a private struct UX.

GT 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

**finding**（`firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192`，距錨點 0 行，候選管道 loc）移除 UX.buttonSize 常數改為魔法數字 40

> 原本使用 UX.buttonSize 常數，現在直接寫死為 40。這降低了可讀性與可維護性，若未來需要調整按鈕大小，需修改多處。建議保留常數或使用有意義的名稱。

finding 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

## base-1:firefox-ios-7:1|firefox-ios-7#2

**GT**（func）ensureMainThread generic function loses return value when dispatched asynchronously

> The generic ensureMainThread<T> function was modified to return T? but has a critical flaw: when not on the main thread, it dispatches the work asynchronously to main queue and immediately returns nil, discarding the actual computation result. This breaks any caller that depends on the return value, as they will always receive nil when called from background threads. The function's contract promises to return the work result but fails to do so in the async dispatch path.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行，候選管道 loc）ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理

> `ensureMainThread<T>` 現在在非主執行緒時會回傳 `nil`，但呼叫端可能預期它會同步等待或總是有值。這可能導致呼叫端在未檢查 `nil` 的情況下強制解包，造成執行時期錯誤。建議確認所有呼叫端都正確處理了 `nil`，或考慮提供非同步版本。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## base-1:prefect-3:2|prefect-3#2

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行，候選管道 loc）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## base-1:prefect-5:1|prefect-5#0

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行，候選管道 ident）bucket_folder 檢查過於寬鬆，可能跳過必要的前綴處理

> 在 `_resolve_path` 中，使用 `if self.bucket_folder and self.bucket_folder in path:` 來判斷路徑是否已包含 bucket_folder。這個檢查只要路徑中任何位置出現 bucket_folder 字串就會成立，即使 bucket_folder 出現在路徑中間或檔名中，也會錯誤地直接返回原始路徑，導致最終儲存路徑缺少必要的前綴。

例如，若 bucket_folder 為 `results/`，而傳入路徑為 `myresults/file.txt`，則 `self.bucket_folder in path` 為 True，函式會直接返回 `myresults/file.txt`，但正確行為應是加上前綴成為 `results/myresults/file.txt`。

建議改為檢查路徑是否以 bucket_folder 開頭（例如使用 `path.startswith(self.bucket_folder)`），或使用 `PurePosixPath` 進行更精確的比對。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-1:prefect-6:5|prefect-6#3

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 17 行，候選管道 ident）使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤

> 原本 `client.create_flow_run_from_deployment(deployment.id, ...)` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如從名稱解析而來），而 API 期望 UUID，可能導致型別錯誤。

建議：確認 `deployment_id` 的型別，必要時轉換為 UUID。

finding 片段：`deployment_id,`

## base-1:redis-2:3|redis-2#6

**GT**（rule）Non-static internal helper function exported as global symbol

> asmCountKeysInSlots is introduced as a file-local helper (not declared in any header and used only within src/cluster_asm.c in this diff), but it is declared without the 'static' keyword, making it globally visible and violating the encapsulation rule for internal helpers.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1012`，距錨點 0 行，候選管道 loc）`asmCountKeysInSlots` 可能造成大量迴圈與效能問題

> `asmCountKeysInSlots` 會針對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slot（例如整個 hash slot 空間 0-16383），則會執行 16384 次函式呼叫。雖然 `kvstoreDictSize` 本身可能只是 O(1) 的查詢，但大量的函式呼叫仍可能造成不必要的效能負擔，特別是在日誌記錄或任務啟動時頻繁呼叫。

建議：
- 評估是否有更有效率的方式取得 key 數量，例如直接從 `kvstore` 取得總數，或使用批次 API。
- 若無法避免，考慮加入快取或限制呼叫頻率。

finding 片段：`unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎  ⏎ unsigned long long key_count = 0;`

## base-1:redis-4:5|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 17 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-5:1|redis-5#1

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:tauri-1:1|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-10:2|tauri-10#3

**GT**（func）Changed window naming pattern breaks window label consistency

> The window label format for dynamically created windows has been changed from "new-{number}" to "new-window-{number}". This breaks the established naming convention and will cause any code that attempts to retrieve or manipulate these windows using the expected label format to fail. For example, code trying to access "new-0" or "new-1" will not find the windows, as they are now named "new-window-0" and "new-window-1". This affects window management, event handling, and any window lookup operations that depend on the label pattern.

GT 片段：`let number = created_window_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed); ⏎ let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 11 行，候選管道 ident）on_new_window 移至 cfg(desktop) 區塊可能改變非桌面平台行為

> 原本 `on_new_window` 的設定在所有平台都會執行，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內，這表示在非桌面平台（如行動裝置）上，新視窗的建立邏輯將不會被註冊。如果這是預期的行為變更，請確認；否則可能導致非桌面平台無法正確處理新視窗請求。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## base-1:tauri-10:2|tauri-10#5

**GT**（rule）New code uses unwrap() on fallible operations

> Added code introduces multiple `unwrap()` calls on fallible operations (`parse().unwrap()`, `set_title(...).unwrap()`, and `build().unwrap()`), which violates the rule prohibiting panics/unwraps in favor of explicit error handling via `Result`.

GT 片段：`let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"), ⏎ tauri::WebviewUrl::External("about:blank".parse().unwrap()),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 13 行，候選管道 ident）on_new_window 移至 cfg(desktop) 區塊可能改變非桌面平台行為

> 原本 `on_new_window` 的設定在所有平台都會執行，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內，這表示在非桌面平台（如行動裝置）上，新視窗的建立邏輯將不會被註冊。如果這是預期的行為變更，請確認；否則可能導致非桌面平台無法正確處理新視窗請求。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## base-1:tauri-11:1|tauri-11#3

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行，候選管道 loc）條件判斷邏輯反轉可能導致版本解析錯誤

> 原本的條件 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。這會使得當 lock 檔存在且 crate_lock_packages 非空時才進入鎖定版本解析，否則會回退到其他邏輯。若原本意圖是「當 lock 檔存在但找不到對應套件時才回退」，則此變更可能導致在 lock 檔存在且套件存在時仍使用鎖定版本，但若套件不存在則可能錯誤地使用其他來源。需要確認此變更是否為修正既有 bug，還是引入新問題。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## base-1:tauri-12:1|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行，候選管道 loc）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-6:2|tauri-6#1

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行，候選管道 ident）callback 的 isEnabled 狀態管理可能導致返回鍵失效

> 在 `handleOnBackPressed` 中，當沒有 listener 且 WebView 無法回上一頁時，會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再設回 `true`。然而，`activity.onBackPressed()` 可能會觸發 Activity 的銷毀或暫停，此時 callback 可能已被移除，重新設為 `true` 可能無效或造成記憶體洩漏。此外，如果 `activity.onBackPressed()` 拋出例外，`isEnabled` 將永遠保持 `false`，導致後續返回鍵完全失效。建議使用 try-finally 確保狀態恢復，或避免直接呼叫 `onBackPressed()`。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`
