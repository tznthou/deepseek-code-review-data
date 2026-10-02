# 盲標單 （主 session 抽樣）：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/spot-main.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0036

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行）遞迴順序變更可能導致狀態不一致

> 原本先標記邊為 skipped 再遞迴傳播，現在改為先遞迴再標記。若遞迴過程中發生例外，邊的狀態可能未被正確標記，導致後續節點狀態分析錯誤。建議確認此順序變更的必要性，或加入例外處理確保狀態一致性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0053

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 setLoading(false) 可能導致 loading 狀態無法正確重設

> 在 minimal 模式下，成功送出表單後原本會呼叫 `setLoading(false)` 來重設 loading 狀態，但此 PR 移除了這一行。如果 `setLoading(false)` 是必要的，移除後可能導致 UI 一直顯示 loading 狀態。建議確認 minimal 模式下的狀態管理邏輯，若需要重設 loading 則應保留。

finding 片段：`setSuccess(true);`

## P0070

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行）新增的 `update` 方法回傳型別可能與介面不符

> `IBookingRepository` 介面中定義 `update` 回傳 `Promise<Booking>`，但 `BookingRepository` 的 `update` 方法直接回傳 `this.prismaClient.booking.update(...)`，其回傳型別是 Prisma 的 `Booking` 型別，可能包含更多欄位，但型別上應相容。然而，若 `BookingUpdateData` 的欄位與 Prisma 的 `BookingUpdateInput` 不完全一致，可能導致型別錯誤。建議確認介面與實作的型別一致性。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## P0073

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）`window_features` 中 size 與 position 的設定順序對調可能影響視窗初始狀態

> 原本先設定 position 再設定 size，現在改為先設定 size 再設定 position。在部分平台（如 Windows）上，設定 position 後再設定 size 可能導致視窗位置被重新計算，反之亦然。若此順序調整非刻意為之，可能造成視窗初始位置或大小不符合預期。建議確認此變更的意圖，或恢復原本順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0134

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateToolbarLayout 中 stacks 陣列重複加入 browserActionStack，遺漏 trailingPageActionStack

> 在 `updateToolbarLayout` 方法中，`stacks` 陣列的組成包含了 `browserActionStack` 兩次，而沒有包含 `trailingPageActionStack`。這會導致在動畫期間，`trailingPageActionStack` 中的按鈕 alpha 不會被設定為 1.0，可能造成按鈕在動畫後仍然隱形。

**失敗情境**：當使用者滾動頁面導致工具列動畫觸發時，位於地址欄右側的頁面操作按鈕（例如分享、書籤）可能不會顯示，因為它們的 alpha 未被更新。

**建議修法**：將第二個 `browserActionStack` 改為 `trailingPageActionStack`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0187

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）條件變更可能導致無鍵命令的 slot 未被正確處理

> 原本的條件是 `else if (num_keys > 0)`，現在改為 `else if (num_keys >= 0)`。這表示當 `num_keys == 0`（無鍵命令）時，也會進入此區塊。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（但無鍵命令不應有此值），則會設定 `read_error` 並將 slot 重設為 `INVALID_CLUSTER_SLOT`。然而，若 `num_keys == 0` 且 `pcmd->slot` 為其他值（例如 `INVALID_CLUSTER_SLOT`），則不會有任何動作，但原本的程式碼也不會進入此區塊。這可能改變了無鍵命令的處理流程，需要確認是否會影響後續邏輯。

失敗情境：若某個無鍵命令的 `pcmd->slot` 被錯誤設定為 `CLUSTER_CROSSSLOT`，現在會被標記為 cross-slot 錯誤，但實際上不應如此。

建議：確認 `num_keys == 0` 時 `pcmd->slot` 的可能值，並考慮是否應維持 `num_keys > 0` 的條件。

finding 片段：`} else if (num_keys >= 0) {`

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

## P0285

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行）checkOnboardingRedirect 條件變更可能導致錯誤重新導向

> 原本的邏輯是：只有當 `pendingInvite` 存在且 `onboardingV3Enabled` 為 true 時，才重新導向到 `/onboarding/personal/settings`。修改後變成 `if (hasPendingInvite || onboardingV3Enabled)`，這表示只要 `onboardingV3Enabled` 為 true，無論是否有 pending invite，都會重新導向到 `/onboarding/personal/settings`。這可能導致沒有 pending invite 的使用者也被重新導向，跳過原本的 onboarding 流程。

**失敗情境**：假設 `onboardingV3Enabled` 為 true，且使用者沒有 pending invite。原本應進入 `/onboarding/getting-started`，但修改後會直接進入 `/onboarding/personal/settings`，可能跳過必要的步驟。

**建議修法**：確認此變更是否為預期行為。若否，應改回 `if (hasPendingInvite && onboardingV3Enabled)`。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) { ⏎ return "/onboarding/personal/settings"; ⏎ }`

## P0291

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 依賴陣列為空，可能無法正確偵測內容截斷

> `useEffect` 僅在掛載時執行一次，若 `item.html` 內容在掛載後變更（例如虛擬滾動重用元件），`isClamped` 可能不會更新。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監測內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0336

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 11 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0399

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）out 參數初始化位置變更可能影響行為

> 在 `TryGetValidatableTypeInfo` 方法中，原本在迴圈後才將 `validatableTypeInfo` 設為 null，現在移到方法開頭。這在功能上等價，但若未來在迴圈前加入其他邏輯，可能造成影響。建議確認此變更是否必要，或僅為程式碼整理。

finding 片段：`validatableTypeInfo = null;`

## P0426

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）變更標記邊為跳過的順序可能導致競態條件

> 原本先標記邊為跳過再遞迴傳播，現在改為先遞迴傳播再標記。若遞迴過程中依賴邊的狀態，可能讀到未更新的狀態。需要確認 `propagate_skip_from_edge` 是否會讀取該邊的狀態，以及此變更是否會影響其他並行操作。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0483

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行）validateStoredKeyConversion 未使用，可能導致錯誤的 keyFromStoredKey 未被偵測

> 新增的 `validateStoredKeyConversion` 函式從未被呼叫。若 dict type 的 `keyFromStoredKey` 回呼有誤（例如回傳 NULL 或錯誤指標），將導致後續雜湊或比較作業出錯，且難以除錯。

**建議**：在 dict 初始化或首次使用時呼叫此驗證函式，或移除該函式以避免 dead code。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) { ⏎ return extracted != NULL;`

## P0502

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 15 行）移除 noTimestamp 選項可能導致 token 包含 iat 欄位

> 原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免在 payload 中加入 `iat`（issued at）欄位，現在移除了該選項，因此產生的 token 會包含 `iat`。這可能影響 token 的驗證邏輯或與其他系統的相容性，但通常不會造成直接問題。若無特定理由，建議保留 `noTimestamp: true` 以維持原有行為。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0503

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0556

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致 `wait(for:)` 永遠等不到 expectation 被 fulfill，直到逾時。

應將 `expectation.fulfill()` 移回 `decisionHandler` 內，與其他測試保持一致。

finding 片段：`wait(for: [expectation]) ⏎ expectation.fulfill()`

## P0567

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1725`，距錨點 2 行）valid_up_to 為 -1 時仍可能嘗試截斷

> 在 fmterr 處理中，若 `valid_up_to == -1`，程式僅記錄警告，但後續仍可能執行 `truncate(aof_filepath, valid_up_to)`，這會將檔案截斷至 -1 的位置，導致未定義行為或檔案損毀。建議在 `valid_up_to == -1` 時直接跳過截斷邏輯，並設定 ret 為 AOF_FAILED。

finding 片段：`if (valid_up_to == -1) { ⏎ serverLog(LL_WARNING,"Last valid command offset is invalid"); ⏎ } else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

## P0589

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 7 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0600

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，可能導致使用者無法知道是哪個新聞信。建議保留變數以提供完整資訊。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。"`

## P0674

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 重新取得資料）。若內容長度改變，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0675

**GT**（func）High-volume threshold boundary applies wrong scaling factor at 400k

> The condition uses `>=` instead of `>` when checking if lastCount qualifies for high-volume capping at exactly 400,000 emails. According to the documented scaling table, 400k should use the 2× multiplier from the thresholds array, but with this bug it immediately applies the high-volume cap of 1.2× or +75k absolute increase. For a site hitting exactly 400k messages, this means getting a limit of 480k (1.2×) or 475k (+75k) instead of the expected 800k (2×). This creates a significant bottleneck at a critical growth milestone and breaks the documented warmup progression.

GT 片段：`// For high volume senders (400k+), cap the increase at 20% or 75k absolute ⏎ if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold) { ⏎ const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 0 行）高流量分支可能導致目標上限低於當前值

> 在 `#getTargetLimit` 中，當 `lastCount >= 400_000` 時，計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 和 `absoluteIncrease = lastCount + 75_000`，然後取兩者最小值。但若 `lastCount` 接近 400,000，例如 400,000，則 `scaledIncrease = 480,000`，`absoluteIncrease = 475,000`，回傳 475,000，仍高於 400,000。但若 `lastCount` 為 500,000，則回傳 575,000，高於 500,000。然而，若 `lastCount` 為 400,000 且 `maxAbsoluteIncrease` 較小（例如 50,000），則可能回傳低於 `lastCount` 的值，導致目標上限倒退。目前設定下，`lastCount=400,000` 時回傳 475,000，仍高於 400,000，但若未來調整參數，可能出現倒退。建議明確確保回傳值至少為 `lastCount`，例如使用 `Math.max(lastCount, Math.min(scaledIncrease, absoluteIncrease))`。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## P0698

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:342`，距錨點 23 行）快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，程式使用 `for tenant_id, subscription_plan in bulk_plans.items()` 來寫入快取，但 `bulk_plans` 是 `get_plan_bulk` 的回傳值，其中可能包含 `None`（若 `get_plan_bulk` 將無效 tenant 設為 `None`）。這會導致將 `None` 序列化為 JSON 字串 `"null"` 存入 Redis，之後讀取時會因驗證失敗而再次視為 cache miss，但已污染快取。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，程式將 `None` 寫入 Redis，下次讀取時 `json.loads` 得到 `None`，`validate_python` 失敗，該 tenant 永遠無法命中快取。

**建議**：改為迭代 `plans_to_cache`，或先過濾掉 `None` 值。

finding 片段：`for tenant_id, subscription_plan in bulk_plans.items(): ⏎ redis_key = cls._make_plan_cache_key(tenant_id) ⏎ # Serialize dict to JSON string ⏎ json_str = json.dumps(subscription_plan)`

## P0738

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，此處傳入 6 個參數，但 `HSETEX` 指令的語法為 `HSETEX key [NX|XX] [KEEPTTL] [EX|PX|EXAT|PXAT] FIELDS num field value [field value ...]`。目前建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`，缺少 TTL 選項，可能導致語法錯誤或行為不符預期。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0780

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:12`，距錨點 6 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const EventRepository = require('./repositories/event-repository'); ⏎ const ProductRepository = require('./repositories/product-repository'); ⏎ const RouterController = require('./controllers/router-controller'); ⏎ const MemberController = require('./controllers/member-controller');`

## P0801

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 2 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 重新取得資料）。若內容長度改變，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0802

**GT**（func）Missing query invalidation after Bluesky handle confirmation causes stale following list

> The confirmBlueskyHandle mutation successfully updates the account cache but fails to invalidate the accountFollows query. When Bluesky is enabled via Bridgy Fed, the account automatically follows the brid.gy account. Both enableBluesky and disableBluesky mutations properly invalidate QUERY_KEYS.accountFollows('index', 'following') to refresh this list, but confirmBlueskyHandle does not. This means after the handle is confirmed, the UI won't show the brid.gy follow relationship until the user manually refreshes the page or navigates away and back. This is inconsistent with the established pattern in the codebase and creates a confusing user experience where the integration appears incomplete.

GT 片段：`onSuccess(blueskyHandle: string) { ⏎ // If the bluesky handle is empty then the handle was not confirmed ⏎ // so we don't need to update the cache ⏎ if (blueskyHandle === '') {`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833`，距錨點 0 行）缺少 accountFollows 查詢的 invalidate

> 在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到「Missing invalidation of accountFollows query that should happen here」。確認 handle 後，帳號的 following 列表可能發生變化（例如自動 follow brid.gy 帳號），但此處未 invalidate 相關查詢，可能導致 UI 顯示過時的 following 資料。建議加入對應的 query invalidation。

finding 片段：`// Note: Missing invalidation of accountFollows query that should happen here`

## P0818

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）scrollToTab 索引可能越界

> 在 `createTabScrollBehavior` 中，當沒有選取分頁且 `state.tabs` 不為空時，回傳的 `toIndex` 從 `state.tabs.count - 1` 改為 `state.tabs.count`。這會導致 `IndexPath(row:section:)` 使用超出陣列範圍的 row，進而在 `scrollToTab` 中嘗試滾動到不存在的索引，可能造成應用程式崩潰。

**失敗情境**：使用者開啟多個分頁，但沒有任何分頁被選取（例如剛啟動或切換面板後），此時觸發滾動到選取分頁的行為，就會嘗試滾動到 `tabs.count` 的索引，而陣列最後一個有效索引是 `tabs.count - 1`。

**建議**：改回 `state.tabs.count - 1`，或明確處理 `tabs` 為空的情況。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0830

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）讀取 tauri.properties 失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0874

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫，可能影響依賴它的服務初始化順序

> 原本 `await emailAddressService.init()` 是同步等待完成後才進行後續的 Promise.all，現在改成在 Promise.all 內與其他服務並行初始化。如果其他服務（如 newsletter service 或 email service）依賴 emailAddressService 初始化完成，可能會因為並行執行而產生競態條件。建議確認這些服務的依賴關係，若有必要，應保留 emailAddressService.init() 的 await 順序，或將依賴它的服務也放入同一個 Promise.all 中並確保順序。

finding 片段：`emailAddressService.init(),`
