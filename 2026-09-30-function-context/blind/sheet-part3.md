# 盲標單 3：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part3.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0201

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 1 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0202

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47`，距錨點 0 行）BackgroundQueueSize 驗證條件變更可能允許 0 值

> 原本的驗證條件為 `if (value < 0)`，允許 0 值；變更後為 `if (value <= 0)`，拒絕 0 值。但屬性文件說明為「maximum size of the background log message queue or null for no limit」，且錯誤訊息仍為「must be non-negative」，因此 0 值可能被視為有效（表示無佇列？）。建議確認 0 是否為有效值，若不是則應更新錯誤訊息與文件。

finding 片段：`if (value <= 0)`

## P0203

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）`getWarmupLimit` 可能回傳 `Infinity`，呼叫端需能處理

> 當 `day > totalDays` 時，函式回傳 `Infinity`。若呼叫端未預期此值，可能導致後續計算（如 `Math.min`、陣列 slice 等）出現非預期行為。建議確認所有呼叫端都能正確處理 `Infinity`，或改回傳一個明確的哨兵值（例如 `emailCount` 或 `Number.MAX_SAFE_INTEGER`）。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0204

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行）XCTWaiter 使用方式錯誤，導致測試必定逾時

> `XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0205

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2304`，距錨點 5 行）手動傳播指令時未處理 alsoPropagate 的失敗情況

> alsoPropagate 可能因為記憶體不足或其他原因失敗，但程式碼未檢查其回傳值。若傳播失敗，可能導致主從資料不一致。

失敗情境：在記憶體不足或網路異常時，HSET 或 HPEXPIREAT 未能正確傳播到 AOF 或複本。

建議修正：檢查 alsoPropagate 的回傳值，若失敗則進行適當處理（如記錄錯誤或回傳錯誤給客戶端）。

finding 片段：`alsoPropagate(c->db->id, c->argv, c->argc, PROPAGATE_AOF|PROPAGATE_REPL);`

## P0206

**GT**（func）Incorrect operation order causes potential data loss during cluster verification

> The verifyClusterConfigWithData() function executes clusterDeleteKeysInUnownedSlots() before clusterClaimUnassignedSlots(). This reverses the intended logic: the function should first claim ownership of unassigned slots that contain keys (preventing orphaned data), then delete keys from slots that are genuinely owned by other nodes. With this bug, keys in unassigned slots may be incorrectly deleted before the node has a chance to claim ownership, resulting in permanent data loss during cluster startup or recovery scenarios.

GT 片段：`/* Delete keys in unowned slots */ ⏎ clusterDeleteKeysInUnownedSlots(); ⏎ /* Take over slots that we have keys for, but are assigned to no one. */ ⏎ clusterClaimUnassignedSlots();`

**finding**（`src/cluster.c:2167`，距錨點 35 行）clusterDeleteKeysInUnownedSlots() 可能誤刪正在遷移中的 key

> 此函式會刪除所有不在自己 slot 中的 key，但未檢查 slot 是否正在進行 legacy 遷移（例如 MIGRATING 狀態）。雖然註解提到 atomic slot migration 安全，但 legacy 遷移中若節點是 migrating 狀態，刪除 key 可能導致資料遺失。建議增加對 migrating 狀態的檢查，或確認此函式僅在特定條件下呼叫。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## P0207

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68`，距錨點 35 行）confirmHandle 的錯誤處理可能導致未處理的 rejection

> `confirmHandle` 使用 `.then()` 但沒有 `.catch()`。若 `confirmBlueskyHandleMutation.mutateAsync()` 失敗（例如網路錯誤），會產生未處理的 Promise rejection。建議加入 `.catch()` 處理錯誤，或使用 try/catch。

finding 片段：`const confirmHandle = useCallback(() => { ⏎ confirmBlueskyHandleMutation.mutateAsync().then((handle) => { ⏎ if (handle) { ⏎ setHandleConfirmed(true);`

## P0208

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行）Session 未關閉導致連線洩漏

> `ConversationVariableUpdaterImpl.update` 中建立 `Session(db.engine)` 後，在方法結束時未呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保 session 關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0209

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:325`，距錨點 31 行）Redis mget 長度不符時快取完全失效且例外被吞掉

> 在 `get_plan_bulk_with_cache` 中，若 `redis_client.mget(redis_keys)` 回傳的 list 長度與 `tenant_ids` 不符，程式會拋出例外，但該例外被外層的 `except Exception` 捕捉，僅記錄錯誤並將所有 tenant 設為 cache miss。這導致即使 Redis 正常運作，只要 mget 因任何原因回傳長度不符（例如 Redis 叢集節點變更），快取就會完全失效，且開發者難以察覺。

**失敗情境**：Redis 叢集在 mget 期間發生 failover，導致部分 key 遺失，回傳長度小於請求數量。此時所有 tenant 都會被視為 cache miss，直接呼叫 billing API，失去快取效益。

**建議**：不要將長度不符視為致命錯誤。可改為逐 key 檢查，或僅記錄警告並將缺失的 key 視為 miss。若必須拋出例外，應使用更精確的例外型別，並考慮重試機制。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## P0210

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103`，距錨點 0 行）輪詢可能重複觸發 confirmHandle

> 在 `setInterval` 中呼叫 `confirmHandle()`，但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`。若前一次請求尚未完成，下一次 interval 仍會觸發新的請求，可能導致多個併發請求。建議在 `confirmHandle` 中加入進行中標誌，或使用 `isLoading` 狀態防止重入。

finding 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ `

## P0211

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter 使用方式錯誤，導致測試必定逾時

> `XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0212

**GT**（rule）Missing Mozilla Public License header

> The rule requires that every .swift file begins with the exact Mozilla Public License header comment block at the top of the file. This file is missing the required header entirely.

GT 片段：`import ContentBlockingGenerator ⏎ @main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏資料競爭

> 將 `generator` 標記為 `nonisolated(unsafe)` 表示開發者手動保證其執行緒安全，但註解中明確指出 `ContentBlockerGenerator` 並非執行緒安全。若此靜態屬性被多個執行緒同時存取，可能導致資料競爭或未定義行為。建議確認 `ContentBlockerGenerator.factory()` 的回傳值是否真的不可變且內部狀態安全，或考慮使用鎖定、actor 或其他同步機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0213

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:43`，距錨點 0 行）搜尋模式判斷邏輯反轉

> 在 `useMarketplaceSearchMode` 中，原本的條件 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` 被改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，少了否定運算子。這會導致當 `activePluginType` 屬於有 collections 的類別時，`searchMode` 會被設為 `true`，反之則為 `false`，與預期行為完全相反。例如，若使用者選擇一個有 collections 的類別且沒有輸入搜尋文字或標籤，原本應顯示 collections 列表，現在卻會進入搜尋模式，顯示空結果或錯誤內容。

建議將條件改回 `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`。

finding 片段：`|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`

## P0214

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行）程式碼格式：`inner_size` 參數間多餘空白

> `inner_size(size.width,    size.height)` 中 `size.width` 與 `size.height` 之間有四個空格，與專案慣例不符。建議改為單一空格。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## P0215

**GT**（func）Incorrect truthy check for retry_jitter_factor hides valid zero values

> The retry_jitter_factor check was changed from an explicit null/undefined check to a simple truthy check. This is a critical bug because a jitter factor of 0 is a valid configuration value (meaning no randomness in retry delays), but the truthy check treats 0 as falsy and displays "None" instead. This misrepresents the actual task configuration to users, making them think no jitter factor is set when it's actually configured to 0. The original PR correctly distinguished between 'not set' (null/undefined) and 'set to zero' (0), but this change breaks that distinction.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retry Jitter Factor</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retry_jitter_factor`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 0 行）使用 `||` 可能錯誤處理數值 0

> 在顯示 Retries 時使用 `{taskRun.empirical_policy?.retries ?? "0"}`，此處已使用 `??`，正確。但下方 Retry Jitter Factor 使用 `? ... : "None"`，若值為 0 會顯示「None」，可能不正確。建議改用 `??` 或明確檢查 null/undefined。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## P0216

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:134`，距錨點 10 行）getBookings 中 teamIdsWithBookingPermission 可能為空陣列，導致查詢範圍不正確

> 在 `getBookings` 中，`teamIdsWithBookingPermission` 是透過 `permissionCheckService.getTeamIdsWithPermission` 取得。若使用者沒有任何符合權限的團隊，此陣列為空。後續呼叫 `getEventTypeIdsFromTeamIdsFilter(prisma, teamIdsWithBookingPermission)` 和 `getUserIdsAndEmailsFromTeamIds(prisma, teamIdsWithBookingPermission)` 時，若傳入空陣列，可能導致查詢條件 `in: []` 而回傳空結果，或產生 SQL 錯誤。

**失敗情境**：使用者沒有 booking.read 權限且不是 ADMIN/OWNER，`teamIdsWithBookingPermission` 為空陣列。`getUserIdsAndEmailsFromTeamIds` 中 `teamIds.length === 0` 會回傳 `[[], []]`，但 `getEventTypeIdsFromTeamIdsFilter` 可能未處理空陣列，導致查詢 `eventType.findMany({ where: { teamId: { in: [] } } })` 可能回傳空陣列或拋出錯誤。

**建議修法**：在呼叫前檢查 `teamIdsWithBookingPermission.length`，若為 0 則直接設定 `eventTypeIdsWhereUserHasBookingPermission = []` 和 `userIdsAndEmailsWhereUserHasBookingPermission = [[], []]`，避免不必要的查詢。

finding 片段：`getEventTypeIdsFromTeamIdsFilter(prisma, teamIdsWithBookingPermission), ⏎ getUserIdsAndEmailsFromTeamIds(prisma, teamIdsWithBookingPermission),`

## P0217

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行）XCTWaiter 使用方式錯誤，導致測試必定逾時

> `XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0218

**GT**（rule）Single quotes instead of double quotes

> The rule requires using double quotes for all strings in TypeScript/JavaScript files, but single quotes were used for the empty string assignment.

GT 片段：`const userEmail = session.user.email || '';`

**finding**（`apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30`，距錨點 5 行）新增的 redirect 可能造成無限重導向迴圈

> 在 `getting-started` 頁面新增 redirect 到 `/onboarding/personal/settings`，但若該頁面也執行相同的 pending invite 檢查並 redirect 回來，可能形成迴圈。需要確認 `/onboarding/personal/settings` 的邏輯是否會再次觸發 redirect。

finding 片段：`const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId: session.user.id }); ⏎ if (hasPendingInvite) { ⏎ return redirect("/onboarding/personal/settings"); ⏎ }`

## P0219

**GT**（func）Variable shadowing breaks sampling consistency for STREAM objects

> A local `samples` variable is declared at line 1319 within the OBJ_STREAM branch, shadowing the outer `samples` variable declared at line 1214. This prevents the outer samples counter from being updated during stream memory calculation. While this doesn't break the stream calculation itself, it violates the function's sampling design pattern where the outer `samples` variable tracks total sampling across all object type branches. This inconsistency could lead to unexpected behavior if the function logic is modified to check or use the outer samples counter after processing.

GT 片段：`raxStart(&ri,s->rax); ⏎ raxSeek(&ri,"^",NULL,0); ⏎ size_t lpsize = 0; ⏎ size_t samples = 0;`

**finding**（`src/object.c:1330`，距錨點 10 行）Stream listpack 估算邏輯變更可能導致記憶體高估

> 在 `kvobjComputeSize` 中，原本的估算方式是 `lpsize * (s->rax->numele-1)` 再加上最後一個 listpack 的實際大小，現在改為 `lpsize * s->rax->numele` 後又加上最後一個 listpack 的大小。這會導致最後一個 listpack 被重複計算，造成記憶體使用量高估。

具體情境：當 stream 中的元素數量超過 sample_size 時，程式會先計算前 N 個 listpack 的平均大小，然後乘以總數 `numele`，接著又加上最後一個 listpack 的實際大小。但平均大小已經包含了最後一個 listpack 的貢獻，因此最後一個 listpack 被算了兩次。

建議改回 `lpsize * (s->rax->numele-1)`，或調整邏輯以避免重複計算。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0220

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69`，距錨點 4 行）搜尋過濾邏輯可能因大小寫處理不當而漏掉結果

> 在 `filteredData` 的 `useMemo` 中，使用 `blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase())` 進行過濾。但 `deferredSearch` 可能包含特殊正規表示式字元，雖然 `includes` 是字串比對，不會有正規表示式問題，但若 `blockDocument.name` 為 `null` 或 `undefined`，`toLowerCase()` 會拋出錯誤。

**失敗情境**：當某個區塊文件的名稱是 `null`（例如匿名區塊），使用者輸入搜尋字串時，`blockDocument.name?.toLowerCase()` 會因為 `name` 為 `null` 而拋出 `TypeError`，導致元件崩潰。

**建議**：使用 `blockDocument.name?.toLowerCase() ?? ""` 或先檢查 `name` 是否存在。

finding 片段：`blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()),`

## P0221

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行）變更標記邊為跳過的順序可能導致競態條件

> 原本先標記邊為跳過再遞迴傳播，現在改為先遞迴傳播再標記。若遞迴過程中依賴邊的狀態，可能讀到未更新的狀態。需要確認 `propagate_skip_from_edge` 是否會讀取該邊的狀態，以及此變更是否會影響其他並行操作。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0222

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）日期計算可能因時區或浮點數誤差導致天數不正確

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `new Date(created_at).getTime()` 的差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或 `created_at` 包含時間部分，可能導致天數計算與預期不符。此外，浮點數除法後取 ceil 可能因精度問題造成邊界錯誤。建議改用 UTC 日期字串比較或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0223

**GT**（rule）Cross-field validation uses field validator

> The rule requires cross-field validation to use @model_validator decorator, but the code uses @field_validator which accesses unvalidated fields via info.data, causing order-dependent validation issues

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:774`，距錨點 0 行）field_validator 使用 info.data 可能無法取得其他欄位值

> 在 Pydantic v2 中，`field_validator` 的 `info.data` 僅包含已驗證的欄位，若 `triggering_event` 在 `automation_triggered_event_id` 之後定義，則 `info.data.get("triggering_event")` 可能為 `None`，導致驗證錯誤。建議改用 `model_validator` 或確認欄位順序。

**失敗情境**：若模型欄位順序變更，或使用 `model_construct` 跳過驗證，可能誤報錯誤。

finding 片段：`def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists.""" ⏎ if v is not None and info.data.get("triggering_event") is None: ⏎ raise ValueError(`

## P0224

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行）validateStoredKeyConversion 函式未使用，可能遺漏驗證

> 新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。如果此函式是為了驗證 keyFromStoredKey 回呼的正確性，應在 dict 初始化或插入時呼叫；否則應移除，避免死碼。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) {`

## P0225

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行）程式碼格式：`position` 參數間缺少空格

> `position(position.x,position.y)` 中逗號後缺少空格，與專案慣例不符。建議改為 `position(position.x, position.y)`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## P0226

**GT**（func）Incorrect input value used in NodeRunResult for CLEAR mode

> The code attempts to use updated_variable.to_object() for the CLEAR write mode's input value, but this represents the final cleared state rather than the input that triggered the operation. In CLEAR mode, income_value is actually the zero value generated by SegmentType.get_zero_value(), which is what should be shown as the input. This causes the NodeRunResult to misrepresent what value was used as input to the clear operation, breaking observability and potentially confusing downstream systems that rely on accurate input tracking.

GT 片段：`# Prepare input value for result ⏎ if self.node_data.write_mode == WriteMode.CLEAR: ⏎ result_input_value = updated_variable.to_object() ⏎ else:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:93`，距錨點 9 行）CLEAR 模式下 income_value 可能未定義

> 在 WriteMode.CLEAR 分支中，程式碼未設定 income_value 變數。若 write_mode 為 CLEAR，則後續的 `result_input_value = income_value.to_object()` 會拋出 UnboundLocalError。建議在 CLEAR 分支中明確設定 income_value 或調整邏輯。

finding 片段：`case WriteMode.CLEAR: ⏎ income_value = SegmentType.get_zero_value(original_variable.value_type) ⏎ updated_variable = original_variable.model_copy(update={"value": income_value.to_object()})`

## P0227

**GT**（rule）Line(s) exceed the 110 character line width requirement

> The added assignment line is longer than the 110 character limit required by the Biome formatting rules for TS/JS files.

GT 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165`，距錨點 6 行）displayGuests 的 map 回呼可能遺失 this 綁定

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 直接傳遞 `this.getDisplayEmail` 作為回呼，但 `getDisplayEmail` 是實例方法，若其內部依賴 `this`（目前沒有），未來修改可能導致錯誤。此外，在其他方法中使用了箭頭函式包裝，此處不一致。

**建議**：統一使用箭頭函式，例如 `.map((guest: string) => this.getDisplayEmail(guest))`，以避免潛在的 `this` 綁定問題。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## P0228

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:97`，距錨點 4 行）keyFromStoredKey 回呼可能回傳 NULL，導致後續解參考崩潰

> `dictStoredKey2Key` 直接呼叫 `d->type->keyFromStoredKey(key)` 並回傳其結果，未檢查 NULL。若回呼實作錯誤或輸入異常，可能回傳 NULL，後續 `dictGetHash` 或比較函式會對 NULL 解參考，造成 crash。建議在回呼後檢查 NULL 並處理錯誤。

finding 片段：`static const void *dictStoredKey2Key(dict *d, const void *key __stored_key) { ⏎ return (d->type->keyFromStoredKey) ? d->type->keyFromStoredKey(key) : key; ⏎ }`

## P0229

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 18 行）dangerouslySetInnerHTML 可能導致 XSS

> `item.html` 直接透過 `dangerouslySetInnerHTML` 渲染，若評論內容未經適當消毒，攻擊者可注入惡意腳本。建議確認後端已對 HTML 進行消毒，或改用安全的渲染方式（如 DOMPurify）。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0230

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 16 行）Hot Reload 時未清除顯示名稱快取

> `ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。如果 Hot Reload 期間屬性的顯示名稱屬性發生變更，`_displayNameCache` 可能返回舊值。

**失敗情境**：開發者在 Hot Reload 中修改了屬性的 `[Display]` 屬性，但由於 `_displayNameCache` 未清除，元件仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0231

**GT**（func）Incorrect Reader Mode URL handling in cancelEditMode

> The cancelEditMode function now incorrectly preserves reader mode URLs when canceling edit mode. The logic was changed from '&&' (AND) to '||' (OR), which means reader mode URLs will now be kept instead of being cleared. This breaks the expected behavior where reader mode URLs should be filtered out when canceling URL editing, potentially causing the address bar to display internal reader:// URLs to users instead of the original webpage URL.

GT 片段：`@MainActor ⏎ private func cancelEditMode(windowUUID: WindowUUID) { ⏎ var url = tabManager(for: windowUUID).selectedTab?.url ⏎ if let currentURL = url {`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485`，距錨點 0 行）cancelEditMode 條件反轉可能導致編輯模式無法正確取消

> 原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓一般網頁（非 Reader Mode）也被視為有效 URL，導致 `url` 被設為非 nil，進而影響取消編輯時的行為。例如，使用者在一般網頁編輯網址列後取消編輯，原本應清空網址列，現在卻可能保留原網址，造成使用者困惑。建議確認此變更是否為 QR code 移除的一部分，若非必要請回復原狀。

finding 片段：`url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`

## P0232

**GT**（rule）Direct malloc_usable_size instead of zmalloc_size

> The rule requires all memory operations to use Redis zmalloc wrappers (zmalloc_size) instead of direct libc functions (malloc_usable_size)

GT 片段：`/* All kv-objects has at least kvobj header and embedded key */ ⏎ size_t asize = malloc_usable_size((void *)o);`

**finding**（`src/object.c:1239`，距錨點 22 行）quicklist 取樣平均計算可能不準確

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 計算平均元素大小，現在改為 `elesize/samples*ql->count`。但 `samples` 是取樣的節點數，而 `elesize` 是這些節點中所有元素的總大小，`elecount` 是這些節點中的元素總數。若每個節點的元素數量不同，使用 `samples` 作為分母會導致平均元素大小計算錯誤。例如，若取樣了 5 個節點，但其中一個節點包含 100 個元素，其他節點各包含 1 個元素，則 `elesize` 會包含 104 個元素的大小，但除以 `samples`（5）會高估平均元素大小。建議改回使用 `elecount` 作為分母，或改為計算每個節點的平均元素大小再乘以節點數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0233

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）天數計算 off-by-one：第一天就被當成 day 1

> `#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算經過天數，導致在暖機開始當天（day 0）就會得到 day 1。這會使暖機進度提前一天，例如在第一天就套用 day 1 的 limit（237），而不是 day 0 的 200。

**失敗情境**：
- 使用者在 2024-01-15 12:00 建立第一封 email，並在 2024-01-15 13:00 呼叫 `getWarmupLimit`。
- `#getDaysSinceFirstEmail` 會計算 `(Date.now() - firstEmailTime) / (1000*60*60*24)` ≈ 0.0417，`Math.ceil` 後得到 1。
- `getWarmupLimit` 會回傳 day 1 的 limit（237），而不是 day 0 的 200。

**建議修法**：
改用 `Math.floor` 來計算天數，讓 day 0 代表第一天。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0234

**GT**（func）Incorrect field path for extracting original bundle identifier

> The code attempts to extract the original identifier from the 'bundle' field instead of the root-level 'identifier' field. Since 'bundle' is an object (not a string), the `.as_str()` call will always fail, causing `original_identifier` to always be None. This breaks the ability to track and report which config file overwrites the bundle identifier, as the `find_bundle_identifier_overwriter()` method relies on comparing against the original identifier value.

GT 片段：`let original_identifier = config ⏎ .as_object() ⏎ .and_then(|config| config.get("bundle")) ⏎ .and_then(|id| id.as_str())`

**finding**（`crates/tauri-cli/src/helpers/config.rs:151`，距錨點 24 行）使用 OnceLock 初始化 Validator 可能隱藏初始化錯誤

> `config_schema_validator` 使用 `OnceLock::get_or_init` 來初始化 `jsonschema::Validator`。如果初始化過程中發生 panic（例如 schema 無效），程式會直接 panic，且後續呼叫都會重複 panic。雖然原本的程式碼也會 panic，但現在錯誤訊息可能較不明確。建議考慮使用 `expect` 提供更清楚的錯誤訊息，或改用 `LazyLock` 以獲得更好的錯誤處理。

finding 片段：`static CONFIG_SCHEMA_VALIDATOR: OnceLock<jsonschema::Validator> = OnceLock::new(); ⏎ CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::valid`

## P0235

**GT**（func）Type mismatch in blocks_variable_output prevents variable blocking

> The blocks_variable_output method compares a Sequence (assigned_variable_selector) directly against a set of tuples (variable_selectors), but fails to convert the Sequence to a tuple first. This type mismatch causes the 'in' check to always return False, meaning the Variable Assigner node will never properly block streaming output of conversation variables. As a result, the response coordinator will incorrectly allow streaming to proceed before conversation variables are updated, violating the intended synchronization logic and potentially showing stale variable values to users.

GT 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool: ⏎ """ ⏎ Check if this Variable Assigner node blocks the output of specific variables. ⏎ Returns True if this node updates any of the requested conversation variables.`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行）blocks_variable_output 的型別與效能疑慮

> 方法參數使用 Set[Tuple[str, ...]]，但呼叫端可能傳入其他可迭代型別。此外，每次呼叫都進行集合查找，若頻繁呼叫可能影響效能。建議確認呼叫端型別，並考慮使用 frozenset 或快取。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## P0236

**GT**（rule）Unused import in new component

> The rule requires that all staged files pass 'biome lint --error-on-warnings' before commit. The code imports 'useEffect' from React but never uses it, which triggers a linting warning that should have been caught and fixed by the pre-commit hook.

GT 片段：`import useMediaQuery from "@calcom/lib/hooks/useMediaQuery"; ⏎ import { Badge } from "@calcom/ui/components/badge"; ⏎ import { Button } from "@calcom/ui/components/button"; ⏎ import { Popover, PopoverContent, PopoverTrigger } from "@calcom/ui/components/popover";`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:44`，距錨點 37 行）maxVisible 未限制最小值，可能導致顯示異常

> maxVisible 是外部傳入的 prop，若傳入負數或 0，visibleItems 會是空陣列，而 hiddenItems 會包含所有項目，導致只顯示 +N 的 badge，但點開 popover 後所有項目都在隱藏區。建議加上 maxVisible 的最小值限制（例如 Math.max(1, maxVisible)）。

finding 片段：`visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0237

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The added test method does not contain explicit '// Arrange', '// Act', and '// Assert' (or '// Act & Assert') comments to delineate the AAA phases, violating the required test structure convention.

GT 片段：`[Theory] ⏎ [InlineData("ServerNonPrerendered")] ⏎ [InlineData("WebAssemblyNonPrerendered")] ⏎ public void PersistentStateIsSupportedInDynamicJSRoots(string renderMode)`

**finding**（`src/Components/test/E2ETest/Tests/StatePersistenceTest.cs:282`，距錨點 0 行）測試方法缺少 async 關鍵字

> 新增的測試方法 `PersistentStateIsSupportedInDynamicJSRoots` 未標記為 `async`，但內部使用了 `Browser.Equal` 等非同步等待方法。雖然這些方法可能內部處理等待，但若未來需要 await 其他操作，將無法使用。建議加上 `async` 並在必要處使用 `await`，以符合測試慣例。

finding 片段：`public void PersistentStateIsSupportedInDynamicJSRoots(string renderMode)`

## P0238

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行）自動遞增時未檢查 versionCode 上限

> 當 `auto_increment_version_code` 為 true 時，直接使用 `saturating_add(1)`，但未檢查是否超過 Google Play 的 2100000000 上限。若已達上限，`saturating_add` 會停留在 2100000000，可能導致上傳失敗。

建議：在遞增後檢查上限，若超過則報錯。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

## P0239

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）當 max_length 未定義時，長度檢查可能失效

> 在 `varItem.max_length` 為 `undefined` 時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果為 `false`，因此不會觸發錯誤。這可能導致使用者提交超長文字，造成後端處理問題或資料截斷。建議在 max_length 未定義時，使用合理的預設值或明確跳過檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0240

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行）將 onActionTap 閉包內容包進 Task 可能改變執行時序與錯誤處理

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使 handleAction 的執行延後到當前同步流程之後，可能影響依賴其完成時機的邏輯（例如 completion 的呼叫時機）。此外，若 handleAction 內部有錯誤拋出，原本可能由閉包呼叫者處理，現在錯誤會被 Task 吞掉或延遲處理。建議確認此處非同步化的必要性，或明確處理錯誤並確保 completion 在正確的執行緒上呼叫。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0241

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:121`，距錨點 23 行）getTeamIdsWithPermission 呼叫未傳遞 orgId

> 在 `getBookings` 中呼叫 `permissionCheckService.getTeamIdsWithPermission` 時，傳入了 `orgId: user.orgId ?? undefined`，但 `PermissionCheckService.getTeamIdsWithPermission` 的參數型別為 `orgId?: number`，若 `user.orgId` 為 null，則傳入 undefined，可能導致後續 SQL 查詢中 orgId 為 undefined 而非 null，造成條件判斷錯誤。建議確認 undefined 的處理方式，或改為傳入 null。

finding 片段：`orgId: user.orgId ?? undefined,`

## P0242

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行）XCTWaiter.wait 的結果未檢查

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0243

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行）active_defrag_enabled 恢復為硬編碼 1，忽略原始設定

> 在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存到 `orig_active_defrag`，然後設為 0，但在 `emptyData` 之後卻直接設為 1，而不是恢復為 `orig_active_defrag`。如果原始設定為 0（例如使用者停用主動碎片整理），此函式會意外地啟用它，可能導致非預期的碎片整理行為。

失敗情境：使用者設定 `activedefrag no`，然後執行會觸發 `rdbLoadEmptyDbFunc` 的操作（例如複製同步），之後主動碎片整理會被意外啟用。

建議修改：
```c
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`server.active_defrag_enabled = 1;`

## P0244

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:364`，距錨點 11 行）SSL_CERT_DIR 解析時未處理空目錄項目

> 程式碼使用 `existingSslCertDir.Split(Path.PathSeparator)` 分割環境變數，但未移除空字串項目。若 SSL_CERT_DIR 包含連續分隔符（如 `dir1::dir2`），會產生空字串，後續 `string.IsNullOrWhiteSpace(dir)` 檢查會將其忽略，但可能導致其他邏輯問題。建議使用 `StringSplitOptions.RemoveEmptyEntries` 分割。

finding 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator);`

## P0245

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 20 行）測試依賴外部網路可能導致不穩定

> captureFrameAndOrigin 使用真實的 WKWebView 載入 https://example.com，這需要網路連線。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。建議改用本地 HTML 字串或攔截請求的方式，避免外部依賴。

finding 片段：`webView.load(URLRequest(url: url))`

## P0246

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗

> `XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0247

**GT**（func）Async test assertion never verified due to missing expectation

> The test was updated to use @Sendable closures for Swift 6 concurrency compliance, but the expectation and wait statements were removed. The test now completes immediately without waiting for the asynchronous requestMediaCapturePermission callback. The XCTAssertEqual inside the decisionHandler closure will never execute, causing the test to always pass even when the media capture permission logic is broken. This is particularly problematic because this test validates critical permission handling behavior.

GT 片段：`func testRequestMediaCaptureSuccess() { ⏎ let subject = createSubject(isActive: true) ⏎ let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt)`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38`，距錨點 0 行）移除 expectation 可能導致測試無法驗證非同步行為

> 在 `testRequestMediaCaptureSuccess` 中移除了 expectation 和 wait，若 `requestMediaCapturePermission` 是非同步的，測試可能在 callback 執行前就結束，導致斷言未執行。建議保留 expectation 或改用 async 測試。

finding 片段：`let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in`

## P0248

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）截斷後未更新 AOF 檔案指標可能導致後續寫入錯誤

> 在 `truncate` 成功後，程式嘗試將 `server.aof_fd` 的檔案指標移至結尾，但若 `server.aof_fd` 為 -1（尚未開啟）或 lseek 失敗，則僅記錄警告，未處理錯誤。這可能導致後續 AOF 寫入從錯誤位置開始，造成資料毀損。建議在 lseek 失敗時視為嚴重錯誤，並停止載入。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0249

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 12 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0250

**GT**（func）Browser navigation uses Forward() instead of Back() breaking test flow

> In the RedirectEnhancedGetToInternal test, after clicking a link that redirects from /redirect to /scroll-to-hash, the test attempts to verify that browser back navigation works correctly. However, the code calls Browser.Navigate().Forward() instead of Browser.Navigate().Back(). Since there is no forward history (the browser just navigated forward to the current page), Forward() does nothing and the browser remains at /scroll-to-hash. The subsequent assertions expect the browser to be back at /redirect with the "Redirections" heading, but it's still at the redirected page, causing the test to fail. The comment explicitly states "See that 'back' takes you to the place from before the redirection" but the code does the opposite action.

GT 片段：`// See that 'back' takes you to the place from before the redirection ⏎ Browser.Navigate().Forward(); ⏎ Browser.Equal("Redirections", () => _originalH1Element.Text); ⏎ Assert.EndsWith("/subdir/redirect", Browser.Url);`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:113`，距錨點 0 行）測試中將 Back 改為 Forward 可能導致測試目的不符

> 原本測試使用 `Browser.Navigate().Back()` 來驗證返回上一頁後元素狀態，但此處改為 `Forward()`。若測試目的是驗證「back」行為，此變更可能使測試失去原本的驗證目標，甚至導致測試失敗。請確認此變更是否為預期行為，或是否應保留 `Back()`。

finding 片段：`Browser.Navigate().Forward();`

## P0251

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）window_features 方法中參數順序調整可能影響行為

> 在 `window_features` 方法中，原本先處理 position 再處理 size，現在順序對調。若兩者同時存在，且後者會覆蓋前者的設定，則可能導致最終視窗位置或大小不符合預期。請確認 `self.window_builder` 的 position 和 inner_size 設定是否互相獨立，否則應保持原有順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0252

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）日期計算可能因時區或浮點數誤差導致天數不正確

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `new Date(created_at).getTime()` 的差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或 `created_at` 包含時間部分，可能導致天數計算與預期不符。此外，浮點數除法後取 ceil 可能因精度問題造成邊界錯誤。建議改用 UTC 日期字串比較或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0253

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）`CFBundleTypeExtensions` 條件判斷可能相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，但這與預期相反：通常應該在有副檔名時才加入此鍵。若 `ext` 為空，則不應加入；若 `ext` 非空，則應加入。目前的寫法會導致有副檔名時反而沒有寫入 `CFBundleTypeExtensions`，可能影響檔案關聯功能。

建議：將條件改為 `!association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0254

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:151`，距錨點 1 行）使用 OnceLock 初始化 Validator 可能隱藏初始化錯誤

> `config_schema_validator` 使用 `OnceLock::get_or_init` 來初始化 `jsonschema::Validator`。如果初始化過程中發生 panic（例如 schema 無效），程式會直接 panic，且後續呼叫都會重複 panic。雖然原本的程式碼也會 panic，但現在錯誤訊息可能較不明確。建議考慮使用 `expect` 提供更清楚的錯誤訊息，或改用 `LazyLock` 以獲得更好的錯誤處理。

finding 片段：`static CONFIG_SCHEMA_VALIDATOR: OnceLock<jsonschema::Validator> = OnceLock::new(); ⏎ CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::valid`

## P0255

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）scheduling.init() 移除了 apiUrl 參數，可能導致排程服務無法正確建構 API URL

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入了動態產生的 API URL，現在改成無參數呼叫。如果 scheduling 服務內部需要這個 URL 來進行 API 呼叫，移除後可能導致功能失效或使用錯誤的 URL。建議確認 scheduling.init() 的實作是否已改為自行取得 URL，或是否應保留此參數。

finding 片段：`scheduling.init(),`

## P0256

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）testCheckSystemThemeChanges 中斷言對象可能錯誤

> 在 testCheckSystemThemeChanges 中，原本斷言 lightThemeView 的值，但修改後改為斷言 darkThemeView 的值。這可能導致測試無法正確驗證 Light 模式是否被選中。

具體失敗情境：當使用者選擇 Light 模式後，lightThemeView 的值應為 1，但此處卻檢查 darkThemeView 的值，若 darkThemeView 的值不為 1，測試將失敗。

建議：確認此變更是否為預期行為。若為筆誤，應改回 lightThemeView；若確實要檢查 darkThemeView，請確認測試邏輯正確。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0257

**GT**（rule）Direct import from features package

> The rule requires apps/api/v2 to import from @calcom/platform-libraries instead of directly from @calcom/features, but the code imports TeamService directly from @calcom/features/ee/teams/services/teamService

GT 片段：`import { TeamService } from "@calcom/features/ee/teams/services/teamService";`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38`，距錨點 17 行）未處理團隊不存在或無權限的例外

> `TeamService.createInvite` 在團隊不存在時會拋出 `ErrorWithCode(ErrorCode.NotFound)`，但控制器未捕獲此例外，可能導致 500 錯誤而非 404。建議加入例外處理或使用全域例外過濾器，確保回傳適當的 HTTP 狀態碼。

finding 片段：`const result = await TeamService.createInvite(teamId);`

## P0258

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:117`，距錨點 26 行）使用 `||` 可能錯誤處理空字串

> 在顯示 Cache Key 和 Dynamic Key 時使用 `{taskRun.cache_key || "None"}`，若 `cache_key` 為空字串（合法值），則會顯示「None」，可能造成混淆。建議使用 `??` 運算子。

finding 片段：`<dd className="font-mono">{taskRun.cache_key || "None"}</dd>`

## P0259

**GT**（rule）Missing braces in for loop

> The rule requires all control flow statements (if, else, for, foreach, while, do-while) to use curly braces even for single-line bodies, but the inner for loop omits curly braces

GT 片段：`for (const [initializerIdentifier, componentIdentifiers] of Object.entries(jsComponentInitializers)) { ⏎ const initializerFunc = DotNet.findJSFunction(initializerIdentifier, 0) as JSComponentInitializerCallback; ⏎ for (const componentIdentifier of componentIdentifiers) ⏎ initializerFunc(componentIde`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 4 行）hasInitializedJsComponents 旗標可能導致初始化遺漏

> `hasInitializedJsComponents` 為全域布林值，一旦設為 true 後，即使後續呼叫傳入不同的 `jsComponentInitializers` 或 `jsComponentParameters`，也不會重新執行初始化。若不同 renderer 需要不同的初始化集合，此旗標會阻止必要的初始化。

建議：考慮以 rendererId 或初始化內容的 hash 作為鍵來判斷是否需要重新初始化，或明確記錄此限制。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## P0260

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateActionStack 中重複加入 browserActionStack

> 在 `updateActionStack` 方法中，原本應該加入 `trailingPageActionStack.arrangedSubviews`，但程式碼卻再次加入了 `browserActionStack.arrangedSubviews`，導致 `browserActionStack` 的 arrangedSubviews 被加入兩次。這會造成重複的視圖、動畫異常，甚至可能導致約束衝突。

建議修正為：
```swift
let stacks = browserActionStack.arrangedSubviews +
             navigationActionStack.arrangedSubviews +
             leadingPageActionStack.arrangedSubviews +
             trailingPageActionStack.arrangedSubviews
```

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0261

**GT**（func）Thread safety violation calling @MainActor completion handler from background thread

> In the handleServerTrust method, when SSL/TLS certificate validation fails (guard else clause), the @MainActor-isolated completionHandler is called directly from the background dispatchQueue without using ensureMainThread wrapper. This violates Swift Concurrency's actor isolation and can cause runtime crashes or data races. The success path correctly wraps the completion call in ensureMainThread, but the failure path at line 1343 does not, creating inconsistent thread safety behavior.

GT 片段：`func handleServerTrust( ⏎ challenge: URLAuthenticationChallenge, ⏎ dispatchQueue: DispatchQueueInterface, ⏎ completionHandler: @escaping @MainActor (URLSession.AuthChallengeDisposition, URLCredential?) -> Void`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343`，距錨點 0 行）直接呼叫 completionHandler 可能違反執行緒隔離

> 原本使用 `ensureMainThread` 確保 completionHandler 在主執行緒執行，現在直接呼叫。若此函式可能在非主執行緒被呼叫，則 completionHandler（標註 @MainActor）會在錯誤的執行緒執行，可能導致 UI 更新問題或 runtime crash。

**失敗情境**：`handleServerTrust` 在 `dispatchQueue.async` 閉包內執行（背景執行緒），若進入 else 分支，直接呼叫 completionHandler 會將 @MainActor 閉包在背景執行緒執行，違反 actor isolation。

**建議**：保留 `ensureMainThread` 包裝，或確認此分支一定在主執行緒。

finding 片段：`completionHandler(.performDefaultHandling, nil)`

## P0262

**GT**（rule）Non-strict inequality operator used

> The rule requires using strict equality operators (=== or !==) for all comparisons, but the code uses != instead of !== to check if count is null

GT 片段：`const count = result.data[0].get('csd_email_count'); ⏎ return count != null ? count : 0;`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:102`，距錨點 9 行）findPage 查詢的 filter 使用 <= 可能包含今日資料

> 原本 `findOne` 使用 `created_at:<${today}` 排除今日，但改為 `findPage` 後 filter 變成 `created_at:<=${today}`，這會包含今日建立的 email。若今日已有 email，則 `#getHighestCount` 可能取到今日的 csd_email_count，導致 warmup limit 計算錯誤。建議確認是否應排除今日，若需排除，應改回 `<`。

finding 片段：`filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,`

## P0263

**GT**（rule）MSTest attribute in xUnit project

> The rule requires test projects to consistently use the xUnit framework, but the test method uses MSTest's [TestMethod] attribute instead of xUnit's [Fact] attribute

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException()`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 2 行）AppContext.SetSwitch 參數值反轉可能導致測試失效

> 原本設定 `DisableThrowNavigationException` 為 `false`，但此處改為 `true`。若測試目的是驗證例外狀況，此變更可能使測試無法觸發預期的例外行為，導致測試失去意義。請確認此參數值是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0264

**GT**（func）Version suffix applied in local development mode, breaking local Tinybird instances

> The PR removes the critical `!localEnabled` check that previously prevented version suffixes from being applied when running against local Tinybird instances. The old code only applied versioning in production (`options.tbVersion && !localEnabled`), but the new code always applies versioning when configured (`statsConfig?.version`), regardless of whether local mode is enabled. This breaks local development because local Tinybird instances typically only have base endpoint versions (e.g., `api_kpis`), not the v2 variants (e.g., `api_kpis_v2`), causing 404 errors when developers try to use local Tinybird for testing. The corresponding test 'ignores tbVersion when local is enabled' was also removed, confirming this behavior change was intentional but problematic.

GT 片段：`// Use version from config if provided for constructing the URL ⏎ // Pattern: api_kpis -> api_kpis_v2 (single underscore + version) ⏎ const version = statsConfig?.version; ⏎ const pipeUrl = version ?`

**finding**（`ghost/core/core/server/services/stats/utils/tinybird.js:37`，距錨點 0 行）未驗證的 version 字串直接拼接進 URL，可能導致路徑操縱

> `version` 來自 `statsConfig?.version`，直接以字串拼接方式插入 URL（`/v0/pipes/${pipeName}_${version}.json`）。若 config 中的 `version` 未經嚴格驗證（例如只允許 `[a-zA-Z0-9_-]+`），攻擊者或錯誤設定可能注入 `../` 等路徑片段，導致請求被導向非預期的 Tinybird pipe，甚至繞過權限控制。建議在 `buildRequest` 中對 `version` 進行正規表示式驗證，或使用 Tinybird 提供的參數化 pipe 名稱機制。

finding 片段：`const version = statsConfig?.version; ⏎ const pipeUrl = version ? ⏎ `/v0/pipes/${pipeName}_${version}.json` : ⏎ `/v0/pipes/${pipeName}.json`;`

## P0265

**GT**（rule）Line exceeds 110 character width

> The rule requires all TypeScript/JavaScript files to use a maximum line width of 110 characters, but this type declaration exceeds this limit at 172 characters

GT 片段：`private helper: AuditActionServiceHelper<typeof RejectedAuditActionService.latestFieldsSchema, typeof RejectedAuditActionService.storedDataSchema>;`

**finding**（`packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:20`，距錨點 17 行）RejectedAuditActionService 的 rejectionReason 型別變更可能影響既有資料

> `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，這表示不再記錄舊的 rejection reason。若既有 audit log 中有舊格式的資料，解析時可能會失敗。需要確認是否有 migration 或相容性處理。

finding 片段：`rejectionReason: z.string().nullable(),`

## P0266

**GT**（rule）Test method missing test prefix

> The rule requires test methods to start with 'test' prefix, but the method 'verifyBookmarksShareNormalWebsiteReminders' does not follow this naming convention

GT 片段：`// https://mozilla.testrail.io/index.php?/cases/view/2864380 ⏎ func verifyBookmarksShareNormalWebsiteReminders() { ⏎ app.launch() ⏎ if #available(iOS 17, *) {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47`，距錨點 0 行）測試方法改名可能導致不再被 XCTest 執行

> 將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders` 後，該方法不再以 `test` 開頭，XCTest 不會自動將其視為測試案例執行。若此方法仍應作為測試執行，請保留 `test` 前綴；若改為輔助方法，則應確認其被其他測試正確呼叫。

finding 片段：`func verifyBookmarksShareNormalWebsiteReminders() {`

## P0267

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 15 行）emailAddressService.init() 改為非同步呼叫可能影響相依服務

> 原本 `emailAddressService.init()` 是同步呼叫（前面有 `await`），現在改為在 `Promise.all` 中非同步執行。若其他服務（如 newsletter 或 email service）依賴 email address service 初始化完成，可能導致競態條件。建議確認這些服務是否已正確處理非同步初始化。

finding 片段：`emailAddressService.init(),`

## P0268

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 未驗證 schedule 結構，可能接受無效資料

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 是否為符合預期的陣列結構。若呼叫端傳入錯誤格式的 schedule，可能導致後續 API 請求失敗或產生未預期的行為。建議加入對 schedule 的型別檢查，例如確認其為二維陣列且元素包含 start 和 end。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0269

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行）測試依賴外部網路可能導致不穩定

> captureFrameAndOrigin 使用真實的 WKWebView 載入 https://example.com，這需要網路連線。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。建議改用本地 HTML 字串或攔截請求的方式，避免外部依賴。

finding 片段：`webView.load(URLRequest(url: url))`

## P0270

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 0 行）參數序列化方式與舊 mock 不一致

> 舊的全域 mock 在序列化參數時會排除 `ns` 並使用 `JSON.stringify`，但新的 `createTFunction` 使用 `delete params.ns` 後再序列化，兩者結果相同，但若 `options` 為 `undefined` 或 `null`，`delete` 可能拋出錯誤。此外，舊 mock 在 `options` 存在但無其他參數時不會加上後綴，新函式則會加上 `:{}`，可能導致測試斷言失敗。建議明確處理 `options` 為空的情況，並保持與舊行為一致。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## P0271

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:417`，距錨點 1 行）新增的 SettingsTextFormatter 可能未被使用

> `SettingsTextFormatter` 類別被新增，但在此 diff 中未看到任何使用它的程式碼。如果沒有其他地方使用，這將是死代碼，增加維護負擔。建議確認是否有後續 PR 會使用，或考慮延後加入。

finding 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ `

## P0272

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷邏輯變更可能導致權限繞過

> 原本的 `isCurrentUser` 判斷為 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示若 `filters.userIds` 包含多個 ID，且其中包含當前使用者 ID，則 `isCurrentUser` 為 true，即使其他 ID 不在可存取範圍內，也不會觸發 FORBIDDEN 錯誤。這可能導致使用者可以查詢到不應存取的 bookings。

**失敗情境**：使用者 A（id=1）請求 `filters.userIds = [1, 2]`，其中使用者 2 不屬於 A 的團隊或組織。由於 `isCurrentUser` 為 true，`areUserIdsWithinUserOrgOrTeam` 的檢查被跳過，A 可以取得使用者 2 的 bookings。

**建議修法**：恢復原本的嚴格判斷，或改為檢查所有 userIds 是否都在可存取範圍內，且當前使用者 ID 必須單獨存在時才視為 current user。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0273

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 0 行）autoCloseOnSelect 在 multiselect 中可能導致非預期關閉

> 在 multiselect 的 onSelect 中，若設定 autoCloseOnSelect 為 true，會在選取後呼叫 onClose 關閉 popover。這可能與 multiselect 的預期行為（允許連續選取多個選項）衝突，且 onClose 可能觸發父層狀態重置（如清除 selectedFieldKeyForOptions），導致使用者無法連續選取。建議確認此行為是否符合產品需求，或考慮僅在特定條件下關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## P0274

**GT**（func）Incorrect comparison logic causes false negatives when comparing slot ranges

> The slotRangeArrayIsEqual function checks if the number of ranges are equal before normalizing and merging adjacent ranges. This causes the function to incorrectly return false (0) when comparing two slot range arrays that represent the same slots but have different numbers of ranges before merging. For example, comparing [1000-1001, 1002-1003] (2 ranges) with [1000-1003] (1 range) will return false even though they represent the same slots after merging. This breaks the task lookup functionality in asmLookupTaskBySlotRangeArray, preventing correct task identification when slot ranges are specified in different but equivalent formats.

GT 片段：`int slotRangeArrayIsEqual(slotRangeArray *slots1, slotRangeArray *slots2) { ⏎ if (slots1->num_ranges != slots2->num_ranges) return 0; ⏎ slotRangeArraySortAndMerge(slots1); ⏎ slotRangeArraySortAndMerge(slots2);`

**finding**（`src/cluster.c:1855`，距錨點 21 行）slotRangeArraySortAndMerge 未合併重疊區間，可能導致驗證失敗或錯誤合併

> `slotRangeArraySortAndMerge` 的註解明確指出「Overlapping ranges are not merged.」，但函式名稱和用途暗示會合併相鄰區間。若輸入包含重疊區間（例如 `0-100 50-150`），排序後相鄰檢查 `prev.end + 1 == next.start` 不成立，因此不會合併，但後續的 `slotRangeArrayNormalizeAndValidate` 會偵測到重疊並回傳錯誤。這可能不是預期行為，因為呼叫端可能期望重疊區間被合併或至少被視為有效。

具體情境：
- 使用者輸入 `CLUSTER MIGRATION IMPORT 0 100 50 150`，預期可能被視為 `0-150`，但實際上會因為重疊而回傳錯誤。
- 若未來有其他程式碼依賴此函式來正規化重疊區間，可能會產生非預期結果。

建議：明確函式的行為，若只合併相鄰區間，應在函式名稱或註解中強調，並確保所有呼叫端都了解重疊區間不會被合併。或者考慮合併重疊區間，以符合直覺。

finding 片段：`/* Sort slot ranges by start slot and merge adjacent ranges. ⏎ * Adjacent means: prev.end + 1 == next.start. ⏎ * e.g. 1000-2000 2001-3000 0-100  =>  0-100 1000-3000 ⏎ *`

## P0275

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:546`，距錨點 30 行）取消單一預約時改用 uid 作為唯一條件，可能忽略 id 參數

> 原本的程式碼使用 `const where: Prisma.BookingWhereUniqueInput = uid ? { uid } : { id };`，會根據是否有 `uid` 來決定用哪個唯一鍵。修改後直接使用 `where: { uid: bookingToDelete.uid }`，完全忽略傳入的 `id`。如果呼叫端只提供 `id` 而沒有 `uid`，或 `uid` 與 `id` 不一致，可能導致更新錯誤的預約或找不到預約。建議保留原本的條件邏輯，或確保 `bookingToDelete.uid` 一定存在且正確。

finding 片段：`const updatedBooking = await bookingRepository.updateIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ uid: bookingToDelete.uid, ⏎ },`

## P0276

**GT**（rule）Unused WorkPoolUpdate type import

> The rule requires that unused imports should be automatically removed by the linter, but WorkPoolUpdate type is imported and never used in the file

GT 片段：`import { useUpdateWorkPool, type WorkPool, type WorkPoolUpdate } from "@/api/work-pools";`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42`，距錨點 37 行）description 可能為 undefined 導致型別不符

> 在 `handleSubmit` 中，`data.description?.trim()` 的結果可能為 `undefined`，但後續將 `trimmedDescription === "" ? null : trimmedDescription` 指派給 `description`。若 `data.description` 為 `undefined`，則 `trimmedDescription` 為 `undefined`，最終 `description` 會是 `undefined`，但 `WorkPoolUpdate` 型別可能預期 `string | null`。建議明確處理 `undefined` 情況，例如使用 `data.description?.trim() ?? null`。

finding 片段：`const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool( ⏎ { ⏎ name: workPool.name,`

## P0277

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行）Storybook 裝飾器中的 queryClient 與元件使用的 queryClient 不一致

> 在 `createTestRouter` 中，`context` 使用了 `new QueryClient()`，但裝飾器外層的 `QueryClientProvider` 使用的是模組頂層的 `queryClient`。這可能導致元件內部的 `useSuspenseQuery` 使用到錯誤的 queryClient 實例，造成測試行為不一致或快取問題。建議在 `createTestRouter` 中傳入相同的 `queryClient` 實例，或將 `queryClient` 的建立移到裝飾器內。

finding 片段：`context: { queryClient: new QueryClient() },`

## P0278

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行）TOML 解析錯誤被錯誤地包裝為 FormatJson，而非 FormatToml

> 原本的程式碼將 TOML 解析錯誤包裝為 `ConfigError::FormatToml`，但修改後改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會導致錯誤分類不正確，使用者看到 JSON 格式錯誤的訊息，但實際上是 TOML 解析失敗。建議保留 `FormatToml` 變體，或新增專門的 TOML 錯誤變體。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## P0279

**GT**（func）Case mismatch between BundleType serialization and deserialization for Flatpak

> The Display implementation for BundleType::Flatpak returns "Flatpak" with capital 'F', while the Deserialize implementation expects lowercase "flatpak". This creates a serialization round-trip bug where serializing a Flatpak bundle type and then deserializing it will fail. Any code that serializes bundle configurations to strings (for CLI output, config files, or API responses) and then attempts to parse them back will encounter deserialization errors. This inconsistency breaks the expected behavior that Display and Deserialize should be compatible with each other.

GT 片段：`impl Display for BundleType { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ write!( ⏎ f,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 0 行）Flatpak 的 Display 實作使用大寫 "Flatpak"，與其他 bundle 類型的小寫慣例不一致

> 在 `Display for BundleType` 的實作中，新增的 `Flatpak` 分支回傳 `"Flatpak"`，但其他所有分支（如 `"nsis"`, `"app"`, `"dmg"`）皆為小寫。這可能導致序列化或顯示時的不一致，例如在錯誤訊息或日誌中出現大小寫混雜。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0280

**GT**（func）clear_child_firings returns wrong ID field breaking race detection

> The DELETE...RETURNING statement returns child_trigger_id instead of child_firing_id, causing a critical type mismatch in the race detection logic. The caller in triggers.py expects firing IDs (specific instances of firings) but receives trigger IDs (the template/definition). Since firing_ids contains UUIDs of specific firing instances while deleted_ids contains trigger template IDs, the comparison deleted_ids != firing_ids will always evaluate to true, causing the system to incorrectly believe it lost the race and skip all legitimate trigger firings. This breaks the entire compound trigger firing mechanism.

GT 片段：`result = await session.execute( ⏎ sa.delete(db.CompositeTriggerChildFiring) ⏎ .filter( ⏎ db.CompositeTriggerChildFiring.automation_id == trigger.automation.id,`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:134`，距錨點 13 行）clear_child_firings 回傳型別變更可能影響其他呼叫者

> `clear_child_firings` 的回傳型別從 `None` 改為 `set[UUID]`，但此函式可能被其他模組呼叫。若其他呼叫者未預期回傳值，可能導致型別錯誤或行為不符。建議確認所有呼叫點都已更新，或保留原回傳型別並新增另一個函式。

finding 片段：`async def clear_child_firings( ⏎ db: PrefectDBInterface, ⏎ session: AsyncSession, ⏎ trigger: CompositeTrigger,`

## P0281

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行）listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能

> 原本的程式碼是 `.filter((state) => state.globalEnabled)`，但此 PR 改成了 `.filter((state) => !state.globalEnabled)`。這會讓使用者看不到任何全域啟用的功能，反而看到被停用的功能。

**失敗情境**：當某個功能在 flags 設定中 `enabled: true` 時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能；反之，若功能被停用，卻會出現在回傳結果中。

**建議修法**：改回 `.filter((state) => state.globalEnabled)`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## P0282

**GT**（func）Incorrect localized string reference in SettingsTextFormatter

> The formatStudiesText method references strings.detailTextStudies instead of strings.detailTextStudiesV2. This causes the formatter to display the old v1 Studies message ('%@ may install and run studies from time to time.') instead of the new v148 message ('%@ randomly selects users to test features, which improves quality for everyone.') that was added in this PR. The helper class was clearly intended to format the new v148 strings based on the PR context, but uses the wrong string constant.

GT 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:417`，距錨點 6 行）新增的 SettingsTextFormatter 可能未被使用

> `SettingsTextFormatter` 類別被新增，但在此 diff 中未看到任何使用它的程式碼。如果沒有其他地方使用，這將是死代碼，增加維護負擔。建議確認是否有後續 PR 會使用，或考慮延後加入。

finding 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ `

## P0283

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 15 行）參數序列化方式與舊 mock 不一致

> 舊的全域 mock 在序列化參數時會排除 `ns` 並使用 `JSON.stringify`，但新的 `createTFunction` 使用 `delete params.ns` 後再序列化，兩者結果相同，但若 `options` 為 `undefined` 或 `null`，`delete` 可能拋出錯誤。此外，舊 mock 在 `options` 存在但無其他參數時不會加上後綴，新函式則會加上 `:{}`，可能導致測試斷言失敗。建議明確處理 `options` 為空的情況，並保持與舊行為一致。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## P0284

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43`，距錨點 0 行）endsWith 過濾對大小寫敏感，可能漏掉部分通用日曆

> `endsWith` 在 Prisma 中通常對大小寫敏感（取決於資料庫 collation）。若日曆 ID 的大小寫與後綴不一致（例如 `@Group.Calendar.Google.com`），則不會被過濾。

**失敗情境**：使用者擁有大小寫不同的通用日曆時，仍會被訂閱，導致不必要的同步。

**建議**：考慮使用不區分大小寫的比對（例如 `mode: 'insensitive'`）或先將 `externalId` 轉為小寫再比對。

finding 片段：`NOT: { externalId: { endsWith: suffix } },`

## P0285

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行）checkOnboardingRedirect 條件變更可能導致錯誤重新導向

> 原本的邏輯是：只有當 `pendingInvite` 存在且 `onboardingV3Enabled` 為 true 時，才重新導向到 `/onboarding/personal/settings`。修改後變成 `if (hasPendingInvite || onboardingV3Enabled)`，這表示只要 `onboardingV3Enabled` 為 true，無論是否有 pending invite，都會重新導向到 `/onboarding/personal/settings`。這可能導致沒有 pending invite 的使用者也被重新導向，跳過原本的 onboarding 流程。

**失敗情境**：假設 `onboardingV3Enabled` 為 true，且使用者沒有 pending invite。原本應進入 `/onboarding/getting-started`，但修改後會直接進入 `/onboarding/personal/settings`，可能跳過必要的步驟。

**建議修法**：確認此變更是否為預期行為。若否，應改回 `if (hasPendingInvite && onboardingV3Enabled)`。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) { ⏎ return "/onboarding/personal/settings"; ⏎ }`

## P0286

**GT**（rule）Public Error enum missing #[non_exhaustive]

> `Error` is a public error enum but is not marked `#[non_exhaustive]`, which makes future additions of variants a breaking change for downstream users.

GT 片段：`#[derive(Debug)] ⏎ pub enum Error {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:20`，距錨點 0 行）Error 型別移除 thiserror 衍生可能破壞下游 API

> 原本 `Error` 使用 `thiserror::Error` 衍生，現在改為手動實作 `Display` 和 `std::error::Error`。這可能影響下游依賴此 crate 的程式碼，例如使用 `thiserror` 的 `#[from]` 或依賴 `Error` 的特定 trait 實作。此外，手動實作的 `source()` 方法未包含所有變體（如 `Plist`、`X509Certificate` 等），可能導致錯誤鏈不完整。建議確認此變更是否為有意為之，並考慮提供向後相容的實作。

finding 片段：`#[derive(Debug)] ⏎ pub enum Error {`

## P0287

**GT**（rule）Dead store / unused variable `normalizedJsonSchema`

> SonarJS no-dead-store is enforced at error level. `normalizedJsonSchema` is assigned but never used afterwards, making it a dead store and a lint violation.

GT 片段：`const jsonSchemaValue = tempPayload.json_schema ⏎ const isSchemaEmpty = isJsonSchemaEmpty(jsonSchemaValue) ⏎ const normalizedJsonSchema = isSchemaEmpty ? undefined : jsonSchemaValue`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:255`，距錨點 4 行）空 schema 設定為 undefined 可能與後端預期不符

> 在 `handleConfirm` 中，若 schema 為空，會將 `json_schema` 設為 `undefined` 後傳給 `onConfirm`。這可能導致後端收到缺少 `json_schema` 欄位的 payload，若後端預期該欄位存在（即使是空字串），可能造成錯誤。建議確認後端 API 對 `json_schema` 的處理方式，或改為傳送空字串。

finding 片段：`const payloadToSave = isSchemaEmpty ⏎ ? { ...tempPayload, json_schema: undefined } ⏎ : tempPayload`

## P0288

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 2 行）autoCloseOnSelect 在 multiselect 中可能導致非預期關閉

> 在 multiselect 的 onSelect 中，若設定 autoCloseOnSelect 為 true，會在選取後呼叫 onClose 關閉 popover。這可能與 multiselect 的預期行為（允許連續選取多個選項）衝突，且 onClose 可能觸發父層狀態重置（如清除 selectedFieldKeyForOptions），導致使用者無法連續選取。建議確認此行為是否符合產品需求，或考慮僅在特定條件下關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## P0289

**GT**（func）Unsafe concurrency annotation on non-thread-safe static property

> The static generator property is marked with nonisolated(unsafe) despite the comment explicitly stating 'ContentBlockerGenerator is not thread safe'. This annotation bypasses Swift 6's concurrency safety checks and allows the non-thread-safe ContentBlockerGenerator to be accessed from multiple isolation domains without protection. This creates a potential data race condition where multiple threads could access the generator simultaneously, leading to undefined behavior, crashes, or data corruption. The unsafe annotation should only be used when the developer can guarantee thread safety through other means, which the comment explicitly contradicts.

GT 片段：`@main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）nonisolated(unsafe) 可能隱藏執行緒安全問題

> 使用 `nonisolated(unsafe)` 來繞過 Swift 6 的嚴格並發檢查，但若 `ContentBlockerGenerator` 真的非執行緒安全，此標註只是暫時壓制問題。建議確認其執行緒安全性，或改用其他並發安全機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0290

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判

> 在 Linux 上，檔案路徑是區分大小寫的。使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能將不同目錄視為相同（例如 `/Certs` 與 `/certs`），導致錯誤地認為憑證目錄已存在於 SSL_CERT_DIR 中，進而跳過必要的設定。建議在 Unix 平台上使用 `StringComparison.Ordinal`，或根據作業系統動態選擇比較方式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0291

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 依賴陣列為空，可能無法正確偵測內容截斷

> `useEffect` 僅在掛載時執行一次，若 `item.html` 內容在掛載後變更（例如虛擬滾動重用元件），`isClamped` 可能不會更新。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監測內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0292

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行）無 listener 時直接呼叫 onBackPressed 可能導致非預期關閉

> 當沒有 JS listener 且 webView 無法返回時，程式碼會呼叫 `activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是關閉 Activity。若開發者希望攔截返回鍵但尚未註冊 listener，或 listener 被移除的瞬間，可能導致應用意外退出。建議改為停用 callback 並讓系統處理，或提供明確的預設行為。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## P0293

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 strict 模式將大幅降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查選項（包括 `noImplicitAny`、`strictNullChecks` 等），可能隱藏潛在的型別錯誤，並與專案既有的嚴格模式慣例相違背。建議恢復為 `true`，並修正因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0294

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call, long value string, and long comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextRollouts = NSLocalizedString("Settings.detailTextRollouts", value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", comment: "Description associated to the Rollouts toggle on the settings screen. %@ is the app name (for example \`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:203`，距錨點 6 行）新增的 V2 字串可能未被使用

> 新增了 `detailTextSendUsageDataV2`、`labelStudiesV2`、`detailTextStudiesV2` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

finding 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

## P0295

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 7 行）不同 renderer 啟用時會覆寫全域狀態，可能導致舊 renderer 的 manager 失效

> 在 `enableJSRootComponents` 中，當 `manager` 已存在且 `currentRendererId !== rendererId` 時，程式碼不會拋出錯誤，而是直接覆寫 `currentRendererId` 和 `manager`。這可能導致舊 renderer 的 manager 被取代，若舊 renderer 仍在運作，後續呼叫 `getInteropMethods` 或相關操作可能使用到錯誤的 manager，造成非預期行為。建議在這種情況下拋出錯誤或明確處理多 renderer 情境。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## P0296

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:37`，距錨點 0 行）render_template 可能回傳 None，違反回傳型別標註

> `render_template` 的型別標註為 `-> str`，但當 `result.get("result")` 為 None 時會回傳 None。這會導致呼叫端在未檢查的情況下發生型別錯誤。建議在 None 時拋出 `TemplateRenderError`，確保回傳值永遠是 str。

finding 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

## P0297

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行）CFBundleTypeExtensions 條件判斷邏輯相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，這與預期相反。當副檔名清單為空時，不應插入該鍵；反之，當有副檔名時才應插入。目前的行為會導致所有有副檔名的關聯都不會寫入 `CFBundleTypeExtensions`，使得 macOS 無法正確建立檔案關聯。

建議改為 `if !association.ext.is_empty() { ... }`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0298

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）遞迴順序變更可能導致狀態不一致

> 原本先標記邊為 skipped 再遞迴傳播，現在改為先遞迴再標記。若遞迴過程中發生例外，邊的狀態可能未被正確標記，導致後續節點狀態分析錯誤。建議確認此順序變更的必要性，或加入例外處理確保狀態一致性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0299

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:56`，距錨點 11 行）Trans mock 未處理 components prop，可能導致依賴該 prop 的測試失敗

> `createTransMock` 回傳的 `Trans` 元件僅接收 `i18nKey` 和 `children`，但實際 react-i18next 的 `Trans` 元件常使用 `components` prop 來插入自訂元件。若元件使用 `<Trans i18nKey="..." components={{ trustSource: <TrustSource /> }} />`，此 mock 會忽略 `components`，導致渲染結果與實際不符，可能使測試無法正確驗證。建議在 `Trans` mock 中處理 `components` prop，例如將 `components` 中的元件渲染在對應位置。

finding 片段：`Trans: ({ i18nKey, children }: { ⏎ i18nKey: string ⏎ children?: React.ReactNode ⏎ }) => {`

## P0300

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 0 行）移除型別檢查可能導致非 dict 值被指派給 job_vars_schema

> 原本的程式碼會檢查 `base_job_template["variables"]` 是否為 dict，若不是則不指派。移除檢查後，若 `variables` 的值不是 dict（例如是字串或 None），`job_vars_schema` 會被指派為該值，後續使用時可能發生型別錯誤。

建議保留型別檢查，或明確處理非 dict 的情況。

finding 片段：`job_vars_schema = base_job_template["variables"]`
