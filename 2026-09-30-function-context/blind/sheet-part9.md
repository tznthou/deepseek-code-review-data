# 盲標單 9：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part9.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
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

## P0803

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗

> `XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0804

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 0 行）selector 長度檢查可能不完整

> 檢查 `len(selector) < 2` 後，只使用 `selector[0]` 判斷是否為 conversation variable。但後續 `variable_pool.get(selector)` 可能預期 selector 長度為 2，若長度大於 2 可能導致錯誤。建議確認 selector 的合法長度。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## P0805

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行）HINCRBYFLOAT 複寫為 HSETEX KEEPTTL 可能遺失欄位 TTL

> 原程式碼使用 `HASH_SET_KEEP_TTL` 保留欄位 TTL，但複寫指令改為 `HSETEX KEEPTTL`。若 `HSETEX KEEPTTL` 的實作在欄位不存在時不會設定 TTL，則複本上原本沒有 TTL 的欄位將維持無 TTL，但主節點上該欄位可能因 `HINCRBYFLOAT` 而獲得 TTL（例如原本有 TTL 的欄位被更新後，TTL 應保留）。需確認 `HSETEX KEEPTTL` 在欄位不存在時的行為是否與 `HASH_SET_KEEP_TTL` 一致。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0806

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:83`，距錨點 15 行）移除 userSelect 中的 locale 欄位可能影響取消流程

> `userSelect` 中移除了 `locale: true`，但 `handleCancelBooking.ts` 中呼叫 `userRepository.findByIdOrThrow` 取得 organizer 後，使用 `organizer.locale` 來取得翻譯。若 `findByIdOrThrow` 使用此 `userSelect`，則 `organizer.locale` 將為 `undefined`，可能導致翻譯失敗或錯誤。請確認 `findByIdOrThrow` 的實作是否包含 `locale`，或保留此欄位。

finding 片段：`locale: true, ⏎ timeFormat: true,`

## P0807

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 10 行）SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外

> 在解析現有 SSL_CERT_DIR 時，程式碼對每個目錄呼叫 `Path.GetFullPath(dir)`，但僅以 `catch` 捕捉例外並回傳 false。然而，`Path.GetFullPath` 可能因無效路徑字元、過長路徑或權限問題擲回 `ArgumentException`、`PathTooLongException`、`SecurityException` 等。若例外發生，該目錄會被忽略，可能導致誤判憑證目錄已存在或未存在。建議明確捕捉特定例外並記錄，或先驗證路徑格式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0808

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）未定義的 `True` 會導致 ReferenceError

> 在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳 `True`，但 `True` 並未定義（JavaScript 中布林值為 `true`，非 `True`）。這會導致執行時拋出 `ReferenceError: True is not defined`，使函式無法正常完成。

**失敗情境**：使用者在 JSON Schema 編輯器中輸入合法 JSON 並觸發 onChange，函式會拋出錯誤，可能導致 UI 中斷或狀態未更新。

**建議**：將 `return True` 改為 `return true`。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0809

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 分配後未檢查 malloc 失敗

> `slot_buffer = malloc(sizeof(int) * keys_result->numkeys);` 未檢查回傳值是否為 NULL。若記憶體不足，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議加入檢查：
```c
int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);
if (!slot_buffer) return INVALID_CLUSTER_SLOT;
```

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0810

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 5 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0811

**GT**（func）Inconsistent format specifier documentation in RolloutsSettingMessage comment

> The comment for RolloutsSettingMessage incorrectly documents the format specifier as '%1$@' (positional format) while the actual value string uses '%@' (simple format). This mismatch creates confusion for localization teams and could lead to incorrect translations, as translators may attempt to use positional formatting based on the comment when the string implementation doesn't support it. The comment should match the actual format specifier used in the value field.

GT 片段：`public static let RolloutsSettingMessage = MZLocalizedString( ⏎ key: "Settings.Rollouts.Message.v148", ⏎ tableName: "Settings", ⏎ value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.",`

**finding**（`firefox-ios/Shared/Strings.swift:6232`，距錨點 22 行）新增的 V3 字串可能未被使用

> 新增了 `StudiesSettingTitleV3`、`StudiesSettingLinkV3`、`StudiesSettingMessageV3` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

finding 片段：`public static let StudiesSettingTitleV3 = MZLocalizedString( ⏎ key: "Settings.Studies.Title.v148", ⏎ tableName: "Settings", ⏎ value: "Allow Feature Studies",`

## P0812

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4143`，距錨點 0 行）preprocessCommand 中 cross-slot 處理後未設定 slot 為 INVALID_CLUSTER_SLOT

> 在 `preprocessCommand` 中，當 `pcmd->slot == CLUSTER_CROSSSLOT` 時，程式碼設定 `pcmd->read_error = CLIENT_READ_CROSS_SLOT;` 並將 `pcmd->slot = INVALID_CLUSTER_SLOT;`。但若後續程式碼依賴 `pcmd->slot` 為有效值，可能會誤用。建議確認此處重設 slot 的必要性，或考慮在錯誤時直接 return。

finding 片段：`if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT; ⏎ pcmd->slot = INVALID_CLUSTER_SLOT; ⏎ }`

## P0813

**GT**（func）Variable scope error causes UnboundLocalError when template rendering succeeds

> The length validation check was moved inside the try block before the except clause, creating a critical variable scope issue. When `render_template()` succeeds, the `rendered` variable is assigned inside the try block. However, if the length check passes and no exception occurs, execution continues to the return statement outside the try-except block which references `rendered`. In Python, this creates an undefined variable scenario where `rendered` is only defined within the try block scope but accessed outside it, resulting in UnboundLocalError at runtime whenever template rendering succeeds without exceeding length limits.

GT 片段：`try: ⏎ rendered = self._template_renderer.render_template(self.node_data.template, variables) ⏎ if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH: ⏎ return NodeRunResult(`

**finding**（`api/core/workflow/nodes/template_transform/template_transform_node.py:41`，距錨點 27 行）預設 renderer 未使用 factory 注入的 code_executor

> `TemplateTransformNode.__init__` 中，若未提供 `template_renderer`，會建立 `CodeExecutorJinja2TemplateRenderer()`，其內部使用預設的 `CodeExecutor`。但 `DifyNodeFactory` 在建構時可能注入了自訂的 `code_executor`（例如用於測試或沙箱），此時節點使用的 executor 與 factory 不一致。建議將 factory 的 `_code_executor` 傳入 renderer，或由 factory 統一建立 renderer 並注入。

finding 片段：`self._template_renderer = template_renderer or CodeExecutorJinja2TemplateRenderer()`

## P0814

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:173`，距錨點 1 行）錯誤處理中 console.error 可能洩漏敏感資訊

> 在 `onError` 回呼中，使用 `console.error(message, err)` 記錄錯誤。`err` 可能包含 API 回應的詳細資料，包括使用者輸入的資料或後端錯誤訊息，若這些資料包含敏感資訊（如密碼、token），則會洩漏到瀏覽器主控台。

**失敗情境**：建立區塊文件時，若後端因驗證失敗回傳包含使用者輸入的錯誤訊息，該訊息會被記錄到主控台，任何能開啟開發者工具的人都能看到。

**建議**：僅記錄錯誤的類型或一般訊息，避免輸出完整錯誤物件；或使用結構化日誌並確保敏感欄位被遮蔽。

finding 片段：`console.error(message, err);`

## P0815

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:38`，距錨點 0 行）SQLite 不支援 advisory lock，競態條件仍可能發生

> 程式碼僅在 PostgreSQL 時取得 advisory lock，SQLite 則直接跳過。雖然 SQLite 的寫入序列化可能降低機率，但並不能完全避免競態：兩個交易可能同時讀取到相同的 child firings，然後各自嘗試刪除並觸發父觸發器。建議在 SQLite 上使用其他同步機制（例如樂觀鎖或應用層級的鎖），或明確接受此限制並在文件中說明。

finding 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

## P0816

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token);`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 3 行）每次呼叫 getFeatureOptInService 都建立新容器與新服務實例

> `getFeatureOptInService` 每次呼叫都會建立新的 DI 容器並載入模組，這可能導致效能浪費，且若服務內部有狀態（例如快取），狀態不會被共享。建議考慮使用單例模式或模組層級的容器快取。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## P0817

**GT**（func）Missing query invalidation after Bluesky handle confirmation causes stale following list

> The confirmBlueskyHandle mutation successfully updates the account cache but fails to invalidate the accountFollows query. When Bluesky is enabled via Bridgy Fed, the account automatically follows the brid.gy account. Both enableBluesky and disableBluesky mutations properly invalidate QUERY_KEYS.accountFollows('index', 'following') to refresh this list, but confirmBlueskyHandle does not. This means after the handle is confirmed, the UI won't show the brid.gy follow relationship until the user manually refreshes the page or navigates away and back. This is inconsistent with the established pattern in the codebase and creates a confusing user experience where the integration appears incomplete.

GT 片段：`onSuccess(blueskyHandle: string) { ⏎ // If the bluesky handle is empty then the handle was not confirmed ⏎ // so we don't need to update the cache ⏎ if (blueskyHandle === '') {`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833`，距錨點 0 行）useConfirmBlueskyHandleMutationForUser 缺少 accountFollows 查詢的 invalidate

> 在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，更新了帳戶快取，但沒有 invalidate `accountFollows` 查詢。註解也提到「Missing invalidation of accountFollows query that should happen here」。若確認 handle 後會影響 following 列表（例如 brid.gy 帳戶的追蹤狀態），UI 可能不會即時更新。建議加入相應的 invalidateQueries。

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

## P0819

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）手動傳播 HPEXPIREAT 時未處理 createStringObjectFromLongLong 可能失敗的情況

> `createStringObjectFromLongLong(expireat)` 可能因為記憶體不足而回傳 NULL，但程式碼未檢查就直接指派給 argv[2]，後續 alsoPropagate 可能對 NULL 物件進行操作，導致崩潰。

失敗情境：在記憶體極度不足時，執行 HINCRBYFLOAT 且欄位有過期時間。

建議修正：檢查回傳值，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0820

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 0 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0821

**GT**（rule）Error enum doesn't use thiserror

> The rule requires custom error enums to use #[derive(thiserror::Error)] with #[error(...)] attributes, but this Error enum manually implements Display and Error traits instead of using thiserror

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:20`，距錨點 0 行）Error 型別移除 thiserror 衍生可能破壞下游 API

> 原本 `Error` 使用 `thiserror::Error` 衍生，現在改為手動實作 `Display` 和 `std::error::Error`。這可能影響下游依賴此 crate 的程式碼，例如使用 `thiserror` 的 `#[from]` 或依賴 `Error` 的特定 trait 實作。此外，手動實作的 `source()` 方法未包含所有變體（如 `Plist`、`X509Certificate` 等），可能導致錯誤鏈不完整。建議確認此變更是否為有意為之，並考慮提供向後相容的實作。

finding 片段：`#[derive(Debug)] ⏎ pub enum Error {`

## P0822

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）屬性 badge 合併 label 可能造成資訊遺失

> 原本屬性值與權重是分開的兩個 badge，現在合併成單一 label，例如原本顯示為 [屬性值] [權重%]，現在變成 [屬性值 權重%]。這可能導致使用者難以區分屬性值和權重，且若屬性值本身包含空格，合併後的字串可能造成混淆。建議保留原本的分開顯示方式，或在 LimitedBadges 中支援多個 badge 的組合。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0823

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行）缺少輔助函式的單元測試

> 新增的 `createTFunction`、`createUseTranslationMock`、`createTransMock` 等函式沒有對應的測試。建議補上單元測試，確保其行為符合預期，特別是參數處理和 fallback 邏輯。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0824

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題

> 新增的 `SettingsTextFormatter` 使用 singleton 模式，但沒有明顯的必要性。如果這個類別只包含無狀態的方法，可以考慮使用靜態方法，避免不必要的 singleton。另外，如果未來加入狀態，需注意執行緒安全。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0825

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not contain explicit '// Arrange', '// Act', and '// Assert' (or '// Act & Assert') comments to delineate phases, violating the required AAA comment pattern.

GT 片段：`public void EmbeddingServerAppInsideIframe_WithCompressionEnabled_Fails() ⏎ { ⏎ ... ⏎ Assert.True(`

**finding**（`src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107`，距錨點 0 行）測試斷言邏輯變更可能導致測試無法正確捕捉錯誤

> 原本使用 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 檢查單一正則表達式，現在改為同時檢查兩個正則表達式（`ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew`）都必須匹配。這可能過於嚴格：如果實際錯誤訊息只符合其中一種模式，測試就會失敗。請確認是否應使用 `||` 而非 `&&`，或者是否預期錯誤訊息同時包含兩種模式。

finding 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

## P0826

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0827

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）`expect` 取代 fallback 可能導致 panic

> 原本的程式碼在 `name` 為 `None` 時會 fallback 到 `association.ext[0].0`，但現在改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空（或 `ext` 的第一個元素不存在），程式會 panic。這會讓建置流程直接崩潰，且錯誤訊息不夠明確。

建議：保留原本的 fallback 邏輯，或改用更安全的處理方式，例如在 `ext` 為空時使用預設名稱或回傳錯誤。

finding 片段：`.expect("File association must have a name")`

## P0828

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:47`，距錨點 24 行）getUrlHistory 回傳型別可能為 undefined

> 在 `getUrlHistory` 中，原本的寫法會在 `history` 存在時回傳 `history`，否則繼續執行後面的邏輯。修改後直接 `return history;`，但 `getDefaultUrlHistory()` 的回傳型別可能是 `URLHistory | undefined`（從函式定義推斷）。如果 `history` 為 `undefined`，則此函式會回傳 `undefined`，而呼叫端可能預期一定拿到陣列，導致後續處理出錯。建議檢查 `getDefaultUrlHistory` 的回傳型別，並在必要時提供預設值或調整型別。

finding 片段：`return history;`

## P0829

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行）notlike 未使用 escape 參數，跳脫失效

> 在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致 `escaped_value` 中的反斜線被視為一般字元，無法正確跳脫 `%` 和 `_`，使得搜尋結果可能包含不應匹配的資料。

建議修改為：
```python
filters.append(json_field.notlike(f"%{escaped_value}%", escape="\\"))
```

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## P0830

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）讀取 tauri.properties 失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0831

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行）buildInviteLink 條件判斷反轉

> 原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，代表非組織情境使用團隊邀請連結；修改後變成 `if (isOrgContext) { return teamInviteLink; }`，導致組織情境反而回傳團隊邀請連結，非組織情境則回傳組織邀請連結。這會讓邀請連結的格式錯誤，使用者可能被導向錯誤的頁面。

建議將條件改回 `if (!isOrgContext)`，或根據實際需求調整。

finding 片段：`if (isOrgContext) { ⏎ return teamInviteLink; ⏎ }`

## P0832

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行）Flatpak 的 Display 實作使用大寫 "Flatpak"，與其他 bundle 類型的小寫慣例不一致

> 在 `Display for BundleType` 的實作中，新增的 `Flatpak` 分支回傳 `"Flatpak"`，但其他所有分支（如 `"nsis"`, `"app"`, `"dmg"`）皆為小寫。這可能導致序列化或顯示時的不一致，例如在錯誤訊息或日誌中出現大小寫混雜。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0833

**GT**（rule）Missing trailing newline at end of file

> The diff indicates the file has no trailing newline ("\ No newline at end of file"), which violates standard formatting expectations enforced by formatters/linters.

GT 片段：`};\ No newline at end of file`

**finding**（`packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:108`，距錨點 3 行）檔案結尾缺少換行符號

> 檔案結尾缺少換行符號，可能導致某些工具或 diff 顯示異常。建議在最後一行加上換行。

finding 片段：`}; ⏎ \ No newline at end of file`

## P0834

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行）條件判斷邏輯錯誤，導致 JSON5 檔案不再進行 schema 驗證

> 原本的條件是 `config_path.extension() == Some(OsStr::new("json")) || config_path.extension() == Some(OsStr::new("json5"))`，修改後變成 `config_path.extension() == Some(OsStr::new("json")) && config_path.extension() == Some(OsStr::new("json5"))`。這使得條件永遠為 false，因為副檔名不可能同時是 "json" 和 "json5"。因此，所有 JSON5 設定檔都不會進行 schema 驗證，可能導致無效的設定被接受。

建議改回使用 `||` 運算子，或使用 `matches!(config_path.extension(), Some(ext) if ext == "json" || ext == "json5")`。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## P0835

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:513`，距錨點 0 行）大量取消 recurring bookings 時，查詢條件從 `gte: new Date()` 改為 `gte: bookingToDelete.startTime`

> 原本的 `findMany` 查詢使用 `startTime: { gte: new Date() }`，會找出所有未來時間的 recurring bookings。修改後改為 `gte: bookingToDelete.startTime`，這會包含過去已發生的 bookings（如果 `bookingToDelete.startTime` 在過去）。這可能導致取消不該取消的過去 bookings，或影響後續的處理邏輯。請確認此變更是否符合預期，特別是在處理過去 recurring events 時。

finding 片段：`const allUpdatedBookings = await bookingRepository.findManyIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ recurringEventId: bookingToDelete.recurringEventId, ⏎ startTime: {`

## P0836

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1122`，距錨點 0 行）記憶體洩漏：cross-slot 時未釋放 slot_buffer

> 在偵測到 cross-slot 時，程式碼執行 `free(slot_buffer); return CLUSTER_CROSSSLOT;`，但若 `slot_buffer` 配置成功且迴圈正常結束，最後也有 `free(slot_buffer)`。然而，若在迴圈中發生其他錯誤（例如 `keyHashSlot` 拋出例外？C 語言無例外，但可能有 longjmp），或未來修改程式碼時在迴圈中提前 return，都可能遺漏釋放。目前程式碼看似有釋放，但若 `malloc` 失敗，`slot_buffer` 為 NULL，`free(NULL)` 是安全的，但後續寫入會 crash。

建議：使用 goto 統一清理，或確保所有路徑都釋放記憶體。

finding 片段：`free(slot_buffer); ⏎ return CLUSTER_CROSSSLOT;`

## P0837

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行）notarize_inner 中 wait 邏輯可能反轉

> 在 `notarize_inner` 中，原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這會改變當 `status` 為 `None` 時的行為：原本是 `!wait`（即不等待時才進入），現在變成 `wait`（等待時才進入）。這可能導致在 `wait=false` 且 `status=None` 時，原本會執行的 notarization 流程被跳過，或反之。需要確認此變更是否為預期修正，並檢查相關測試。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## P0838

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:458`，距錨點 4 行）變數作用域錯誤：`source_static_path` 與 `static_subpath` 可能未定義

> 在 `create_ui_app` 函式中，`source_static_path` 和 `static_subpath` 是在 `if v2_enabled:` 和 `else:` 區塊內分別賦值。然而，後續程式碼（如 `static_dir = ... or str(static_subpath)` 和 `copy_directory(str(source_static_path), ...)`）在區塊外使用這兩個變數。若 `v2_enabled` 為真，則 `static_subpath` 未定義；若為假，則 `source_static_path` 未定義，導致 `NameError`。

**失敗情境**：當伺服器啟動且 `v2_enabled` 為真時，執行到 `static_dir = ... or str(static_subpath)` 會拋出 `NameError: name 'static_subpath' is not defined`。

**建議修法**：在 `if` 區塊之前先定義這兩個變數的預設值，或將後續使用邏輯移入對應的條件分支中。

finding 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

## P0839

**GT**（rule）Missing // MARK: section organization

> The new Swift file defines multiple logical sections (nested delegate type, static helper function) but includes no `// MARK:` comments to delineate them, violating the required section organization rule.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 10 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0840

**GT**（rule）Legacy typing imports instead modern syntax

> The rule requires using Python 3.12+ modern type syntax (set[tuple[str, ...]] instead of Set[Tuple[str, ...]]), but the code imports and uses legacy typing module classes Set and Tuple

GT 片段：`from collections.abc import Mapping, Sequence ⏎ from typing import TYPE_CHECKING, Any, Set, Tuple ⏎ ... ⏎ def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行）blocks_variable_output 的型別與效能疑慮

> 方法參數使用 Set[Tuple[str, ...]]，但呼叫端可能傳入其他可迭代型別。此外，每次呼叫都進行集合查找，若頻繁呼叫可能影響效能。建議確認呼叫端型別，並考慮使用 frozenset 或快取。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## P0841

**GT**（rule）Missing sync wrapper for async function

> The public API function run_deployment is now just an alias to the async-only arun_deployment function, lacking a proper sync compatibility wrapper. This forces users to always use asyncio.run() or similar async context managers in synchronous code.

GT 片段：`# Alias for backwards compatibility ⏎ run_deployment = arun_deployment`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 0 行）`run_deployment` 失去同步執行能力，破壞向後相容性

> 原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步與非同步環境中呼叫。現在改為 `run_deployment = arun_deployment`，而 `arun_deployment` 是純 async 函式，因此在同步環境中呼叫 `run_deployment(...)` 會回傳 coroutine 物件，而不會實際執行流程。這會導致所有現有同步呼叫者的程式碼靜默失敗（例如在腳本或同步函式中呼叫）。

建議：保留一個同步包裝函式，例如使用 `asyncio.run` 或 `anyio.from_thread.run` 來執行 async 版本，或使用 `@sync_compatible` 裝飾器來維持原有行為。

finding 片段：`run_deployment = arun_deployment`

## P0842

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 3 行）每次呼叫 getFeaturesRepository 都建立新容器與新 repository 實例

> 與 `getFeatureOptInService` 相同，每次呼叫都建立新容器，可能造成不必要的資源消耗。若 repository 無狀態則影響較小，但仍建議考慮快取。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## P0843

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 12 行）selector 長度檢查可能不完整

> 檢查 `len(selector) < 2` 後，只使用 `selector[0]` 判斷是否為 conversation variable。但後續 `variable_pool.get(selector)` 可能預期 selector 長度為 2，若長度大於 2 可能導致錯誤。建議確認 selector 的合法長度。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## P0844

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）extractKeysAndSlot 中 slot 可能未初始化

> 在 `extractKeysAndSlot` 中，原本有 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，現在改為僅在 `num_keys > 0` 時才設定 slot。若 `num_keys == 0` 或 `num_keys < 0`，`*slot` 將不會被設定，可能保留呼叫者傳入的舊值。這可能導致呼叫者誤用未初始化的 slot。

失敗情境：若呼叫者未先初始化 `*slot`，且 `num_keys == 0`，則 `*slot` 的值未定義，可能造成錯誤判斷。

建議：保留 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，或確保所有呼叫者都先初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0845

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行）路徑前綴檢查未考慮正規化

> 即使改用 `startswith`，若 `path` 未正規化（例如包含 `./` 或 `../`），可能仍會誤判。建議先將 `path` 轉為 `PurePosixPath` 並正規化後再比較前綴。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0846

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）number 輸入的 type 從 number 改為 text 可能影響使用者體驗

> 在 `PromptValuePanel` 中，原本 number 類型的輸入使用 `<Input type="number">`，現在改為 `<Input type="text">`。這會失去瀏覽器原生的數字輸入行為（如上下箭頭、輸入驗證），且可能導致使用者輸入非數字字元。

**失敗情境**：使用者在數字欄位輸入字母，後續處理可能出錯。

**建議**：確認此變更是否為預期。若需保留數字輸入，應維持 `type="number"` 並加上適當驗證。

finding 片段：`type="text"`

## P0847

**GT**（func）orgId parameter not propagated in getTeamIdsWithPermission

> The method getTeamIdsWithPermission accepts an orgId parameter to scope permission checks to a specific organization, but it fails to pass this parameter to the underlying getTeamIdsWithPermissions method. This causes organization scoping to be ignored when checking single permissions, allowing users to potentially access teams from all organizations instead of only the specified one. The bug breaks the core security feature introduced in this PR where organization-scoped permission checks were meant to restrict access based on orgId.

GT 片段：`async getTeamIdsWithPermission({ ⏎ userId, ⏎ permission, ⏎ fallbackRoles,`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222`，距錨點 0 行）getTeamIdsWithPermission 未將 orgId 傳遞給 getTeamIdsWithPermissions

> 在 `getTeamIdsWithPermission` 方法中，呼叫 `this.getTeamIdsWithPermissions` 時未包含 `orgId` 參數，導致即使呼叫端提供 `orgId`，實際查詢也不會套用組織範圍過濾。這會造成權限範圍擴大，可能讓使用者取得不屬於其組織的團隊 ID。

**失敗情境**：呼叫 `getTeamIdsWithPermission({ userId, permission, fallbackRoles, orgId: 123 })` 時，`orgId` 被忽略，回傳所有符合權限的團隊，而非僅限於 org 123 及其子團隊。

**建議修法**：將 `orgId` 傳入 `getTeamIdsWithPermissions` 呼叫中：
```ts
return this.getTeamIdsWithPermissions({ userId, permissions: [permission], fallbackRoles, orgId });
```

finding 片段：`return this.getTeamIdsWithPermissions({ userId, permissions: [permission], fallbackRoles });`

## P0848

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 0 行）getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。如果 `getRecordings` 是非同步方法，則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這會導致 API 回傳錯誤的資料格式，且可能造成序列化問題。請確認 `getRecordings` 是否為 async，若是則必須加上 `await`。

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0849

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1830`，距錨點 11 行）AOF_BROKEN_RECOVERED 在多檔案 AOF 中可能被誤判為成功

> 在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且不是最後一個檔案時，程式會將 ret 改為 AOF_FAILED，但後續的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 條件會讓程式進入 cleanup，可能導致整個載入流程提前結束，而非僅跳過該檔案。建議確認此處的邏輯是否符合預期。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0850

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 0 行）不同 renderer 啟用時會覆寫全域狀態，可能導致舊 renderer 的 manager 失效

> 在 `enableJSRootComponents` 中，當 `manager` 已存在且 `currentRendererId !== rendererId` 時，程式碼不會拋出錯誤，而是直接覆寫 `currentRendererId` 和 `manager`。這可能導致舊 renderer 的 manager 被取代，若舊 renderer 仍在運作，後續呼叫 `getInteropMethods` 或相關操作可能使用到錯誤的 manager，造成非預期行為。建議在這種情況下拋出錯誤或明確處理多 renderer 情境。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## P0851

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 17 行）使用 jwt.decode 跳過簽章驗證可能接受被竄改的 token

> `_isJWTExpired` 原本使用 `jwt.verify` 來驗證 token 的簽章與有效性，現在改為 `jwt.decode` 僅解碼 payload 而不驗證簽章。這表示攻擊者若取得或猜測到 token，可以竄改 payload（例如延長 `exp`）而不被偵測，導致過期 token 被接受。雖然此 token 可能僅用於內部服務，但仍存在安全風險。

建議：若需驗證過期，應使用 `jwt.verify` 並捕捉 `TokenExpiredError` 來判斷是否過期，或至少使用 `jwt.verify` 的 `ignoreExpiration` 選項。

finding 片段：`const decoded = jwt.decode(token);`

## P0852

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）scrollToTab 的 toIndex 可能超出範圍

> 在 `createTabScrollBehavior` 中，當沒有選取分頁時，回傳 `ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`。陣列索引是從 0 開始，最後一個有效索引是 `count - 1`，因此 `count` 會超出範圍。這會導致 `scrollToTab` 中的 `IndexPath(row:section:)` 無效，可能造成滾動失敗或越界存取。

建議改為 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0853

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試中使用了錯誤的泛型型別進行驗證

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，渲染的元件型別是 `GenericComponent<int>`（`typeof(GenericComponent<int>)`），但後續驗證 preamble marker 時卻使用了 `GenericComponent<string>` 的組件名稱與完整名稱：
```csharp
Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly);
Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);
```
這會導致測試失敗，因為實際序列化的型別資訊應為 `GenericComponent<int>`。建議將這兩行改為使用 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0854

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:78`，距錨點 25 行）輪詢 effect 缺少對 disableBlueskyMutation 的依賴

> 在 `useEffect` 中呼叫了 `disableBlueskyMutation.mutateAsync()`，但依賴陣列僅包含 `account?.blueskyEnabled`, `account?.blueskyHandleConfirmed`, `confirmHandle`，並註解 `disableBlueskyMutation is stable`。若 mutation 函式因 hook 重新渲染而改變（例如 queryClient 或 handle 變化），可能導致 effect 使用過時的 mutation 函式。建議將 `disableBlueskyMutation` 加入依賴陣列，或確認其穩定性。

finding 片段：`// eslint-disable-next-line react-hooks/exhaustive-deps ⏎ }, [account?.blueskyEnabled, account?.blueskyHandleConfirmed, confirmHandle]); // disableBlueskyMutation is stable`

## P0855

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）setupSkeletonAddressBarsLayout 中新增的 isLandscape 變數未使用

> 在 `setupSkeletonAddressBarsLayout` 中，新增了 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`，但該變數在後續程式碼中並未被使用。這可能是開發過程中的殘留，建議移除或實際使用。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0856

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:18`，距錨點 0 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

## P0857

**GT**（func）Missing error source for FailedToEncodeDER variant

> The Error::source() implementation is missing a case for Error::FailedToEncodeDER, which wraps an std::io::Error. This breaks error chain propagation when DER encoding fails. Callers using error context or debugging tools that traverse the error chain will lose the underlying IO error information, making it difficult to diagnose encoding failures. The original PR explicitly added source() support for this variant in the thiserror migration, but this manual implementation omits it.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行）Error::source() 未涵蓋所有可提供來源的變體

> 手動實作的 `source()` 僅回傳 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 的底層錯誤，但 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER` 等變體也包含底層錯誤，卻未回傳。這會讓使用 `Error::source()` 的錯誤鏈走訪中斷，影響錯誤診斷。建議為所有包含底層錯誤的變體實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## P0858

**GT**（func）ASM cron runs before cluster state update causing stale state issues

> The serverCron() function now calls asmCron() before clusterCron(). This is problematic because clusterCron() contains the call to clusterUpdateState() which updates the cluster's operational state (CLUSTER_OK vs CLUSTER_FAIL). ASM (Atomic Slot Migration) operations depend on having an accurate view of the cluster state to make correct migration decisions. By executing asmCron() first, migration tasks may operate on stale cluster state information from the previous iteration, potentially leading to incorrect slot migration decisions, failed migrations, or data consistency issues during cluster rebalancing operations.

GT 片段：`if (server.cluster_enabled) { ⏎ asmCron(); ⏎ clusterCron(); ⏎ }`

**finding**（`src/server.c:1658`，距錨點 0 行）asmCron() 呼叫位置變更可能影響效能

> 原本 asmCron() 在 clusterCron() 內部呼叫，現在移至 serverCron() 中與 clusterCron() 並列。這可能改變執行頻率或順序，若 asmCron() 有相依於 clusterCron() 的狀態更新，可能造成問題。建議確認兩者之間的相依性。

finding 片段：`asmCron(); ⏎ clusterCron();`

## P0859

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not contain explicit '// Arrange', '// Act', and '// Assert' (or '// Act & Assert') comments to delineate phases, violating the required AAA comment pattern.

GT 片段：`public void EmbeddingServerAppInsideIframe_WithCompressionEnabled_Fails() ⏎ { ⏎ ... ⏎ Assert.True(`

**finding**（`src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:103`，距錨點 2 行）CSP 錯誤訊息比對使用兩個 Regex 可能過於嚴格

> 測試改為同時比對舊版和新版的 CSP 錯誤訊息。若瀏覽器更新後產生第三種格式，測試將失敗。建議使用單一 Regex 涵蓋所有可能格式，或使用更寬鬆的比對。

finding 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

## P0860

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1961`，距錨點 0 行）無條件將 active_defrag_enabled 設為 1，可能意外啟用 defrag

> 在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 設為 0，呼叫 `emptyData` 後再無條件設為 1。如果原本 `active_defrag_enabled` 為 0（例如使用者透過設定停用 defrag），此函式會錯誤地啟用 defrag，可能導致非預期的記憶體重整行為，甚至影響效能或穩定性。

建議改為儲存原始值並在最後恢復：
```c
int orig_active_defrag = server.active_defrag_enabled;
server.active_defrag_enabled = 0;
emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`/* Restore the original active defragmentation setting. */ ⏎ server.active_defrag_enabled = 1;`

## P0861

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:211`，距錨點 0 行）`deployment_id` 可能為 `None`，傳入 `create_flow_run_from_deployment` 可能導致型別錯誤

> 在 `name` 不是 UUID 且無法解析為 UUID 時，`deployment_id` 保持為 `None`。後續呼叫 `client.create_flow_run_from_deployment(deployment_id, ...)` 時，若該函式預期 `deployment_id` 為 `UUID` 型別，則可能拋出 `TypeError` 或驗證錯誤。

**失敗情境**：使用者傳入非 UUID 且非合法 UUID 字串的部署名稱（例如 `"my-flow/my-deployment"`），且該名稱無法透過 `read_deployment_by_name` 解析時，`deployment_id` 為 `None`，導致 API 呼叫失敗。

**建議**：在呼叫前檢查 `deployment_id` 是否為 `None`，或改用 `deployment.id`（從 `read_deployment_by_name` 取得的物件）作為參數。

finding 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id,`

## P0862

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤

> 在 testRequestMediaCaptureSuccess 中，decisionHandler 閉包內沒有呼叫 expectation.fulfill()，而是在呼叫 subject.webView(...) 之後直接呼叫 expectation.fulfill()。這會導致測試在 decisionHandler 被呼叫前就完成等待，無法驗證 decisionHandler 是否被呼叫及其內容。若 decisionHandler 從未被呼叫，測試仍會通過，失去測試意義。

建議將 expectation.fulfill() 移回 decisionHandler 閉包內，並移除多餘的 expectation.fulfill()。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0863

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 9 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0864

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 16 行）Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱過期

> `ClearCache` 方法只清除了 `_memberInfoCache`，但 `_displayNameCache` 未被清除。當 Hot Reload 套用中繼資料變更（例如修改屬性的 `DisplayAttribute`）時，`_displayNameCache` 中快取的舊顯示名稱將繼續被使用，導致 UI 顯示過期的名稱。

**失敗情境**：開發者在 Hot Reload 期間修改了某個屬性的 `DisplayAttribute.Name`，但頁面仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0865

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 3 行）clusterDeleteKeysInUnownedSlots 可能刪除正在匯入的 slot 中的 keys

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i) || getImportingSlotSource(i)` 會跳過匯入中的 slot，但若 `getImportingSlotSource(i)` 回傳非 NULL 但該 slot 實際上不屬於我們，仍可能刪除 keys。需確認匯入狀態的處理是否正確。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## P0866

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行）moduleLoader.token 使用 moduleToken 而非 token

> 在 `moduleLoader` 物件中，`token` 屬性被設定為 `moduleToken`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE`），而其他模組通常使用 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`）。這可能導致使用 `moduleLoader.token` 取得服務時型別不符或找不到綁定。請確認此處是否應為 `token` 而非 `moduleToken`。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## P0867

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）多個變數時重複 flush，可能造成效能問題

> 在 `for item in updated_variables:` 迴圈內，每次 `update` 後都呼叫 `flush()`。若有多個 conversation variable 被更新，會造成多次資料庫操作。建議將 `flush()` 移到迴圈外，或讓 `update` 累積變更後一次 flush。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0868

**GT**（func）Swapped answer price unit values causing incorrect billing calculations

> In the create_agent_thought method, the answer_unit_price and answer_price_unit values are swapped. The answer_unit_price is initialized to Decimal('0.001') instead of Decimal(0), while answer_price_unit is initialized to Decimal(0) instead of Decimal('0.001'). This mirrors the correct initialization pattern used for message_unit_price and message_price_unit but with reversed values. This will cause incorrect pricing calculations when computing the total cost of agent responses, potentially leading to billing discrepancies or revenue loss.

GT 片段：`answer="", ⏎ observation="", ⏎ answer_token=0, ⏎ answer_unit_price=Decimal("0.001"),`

**finding**（`api/core/agent/base_agent_runner.py:320`，距錨點 2 行）create_agent_thought 中 message_price_unit 與 answer_price_unit 的初始值可能導致價格計算錯誤

> 在 create_agent_thought 中，`message_price_unit` 被設為 `Decimal("0.001")`，而 `answer_price_unit` 被設為 `Decimal(0)`。這與模型定義中的預設值相反（模型定義中 message_price_unit 預設為 0.001，answer_price_unit 預設為 0.001）。這可能導致後續價格計算時，answer 部分的價格被錯誤地乘以 0，造成總價低估。

失敗情境：當 agent 產生 answer 時，若未更新 answer_price_unit，則總價計算會將 answer 的 token 數乘以 0，導致費用計算錯誤。

建議：確認初始值應與模型預設值一致，或明確設定為正確的價格單位。

finding 片段：`message_price_unit=Decimal("0.001"), ⏎ answer_price_unit=Decimal(0),`

## P0869

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 6 行）登出流程中新增的 Task.Yield 可能引入競態

> 在 `ProcessLogOut` 中，於驗證登出狀態後、取得驗證狀態前新增了 `await Task.Yield()`。這會讓出執行緒，可能導致後續的 `AuthenticationProvider.GetAuthenticationStateAsync()` 讀取到不一致的狀態。例如，若使用者在 `Task.Yield()` 期間登入或登出，可能導致登出流程使用過時的驗證狀態。建議移除 `Task.Yield()`，或說明其必要性並確保狀態一致性。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## P0870

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:378`，距錨點 3 行）過度寬泛的例外處理可能隱藏真實錯誤

> 在解析 SSL_CERT_DIR 中的每個目錄時，使用 `catch` 捕捉所有例外並忽略，可能掩蓋了非預期的錯誤（例如 `Path.GetFullPath` 因權限不足或路徑格式錯誤而拋出的例外）。建議至少記錄例外資訊，或僅捕捉預期的例外類型（如 `ArgumentException`、`NotSupportedException`、`PathTooLongException`）。

finding 片段：`catch ⏎ { ⏎ // Ignore invalid directory entries in SSL_CERT_DIR ⏎ return false;`

## P0871

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0872

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 0 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0873

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:102`，距錨點 0 行）findPage 查詢的 filter 使用 <= 可能包含今日資料

> 原本 `findOne` 使用 `created_at:<${today}` 排除今日，但改為 `findPage` 後 filter 變成 `created_at:<=${today}`，這會包含今日建立的 email。若今日已有 email，則 `#getHighestCount` 可能取到今日的 csd_email_count，導致 warmup limit 計算錯誤。建議確認是否應排除今日，若需排除，應改回 `<`。

finding 片段：`filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,`

## P0874

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫，可能影響依賴它的服務初始化順序

> 原本 `await emailAddressService.init()` 是同步等待完成後才進行後續的 Promise.all，現在改成在 Promise.all 內與其他服務並行初始化。如果其他服務（如 newsletter service 或 email service）依賴 emailAddressService 初始化完成，可能會因為並行執行而產生競態條件。建議確認這些服務的依賴關係，若有必要，應保留 emailAddressService.init() 的 await 順序，或將依賴它的服務也放入同一個 Promise.all 中並確保順序。

finding 片段：`emailAddressService.init(),`

## P0875

**GT**（func）Type mismatch in blocks_variable_output prevents variable blocking

> The blocks_variable_output method compares a Sequence (assigned_variable_selector) directly against a set of tuples (variable_selectors), but fails to convert the Sequence to a tuple first. This type mismatch causes the 'in' check to always return False, meaning the Variable Assigner node will never properly block streaming output of conversation variables. As a result, the response coordinator will incorrectly allow streaming to proceed before conversation variables are updated, violating the intended synchronization logic and potentially showing stale variable values to users.

GT 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool: ⏎ """ ⏎ Check if this Variable Assigner node blocks the output of specific variables. ⏎ Returns True if this node updates any of the requested conversation variables.`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行）型別標註使用 `Set` 與 `Tuple`，與專案慣用的 `set` 和 `tuple` 不一致

> 此處使用 `typing.Set` 和 `typing.Tuple`，但專案其他部分（如 `collections.abc` 的引入）傾向使用內建泛型。建議改用 `set` 和 `tuple` 以維持一致性。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## P0876

**GT**（rule）Unused import: Skeleton

> `Skeleton` is imported but never used in this file, which violates the rule requiring unused imports to be removed.

GT 片段：`import { Skeleton } from "@/components/ui/skeleton";`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14`，距錨點 8 行）Suspense 未提供 fallback，可能導致載入時無 UI 回饋

> `<Suspense>` 沒有指定 `fallback` prop。當 `useSuspenseQuery` 暫停元件時，React 會尋找最近的 Suspense boundary 並顯示其 fallback；若沒有 fallback，則會向上尋找其他 boundary，若都沒有，則整個應用程式會 suspend 且無任何 UI 回饋。建議提供明確的 fallback，例如 `<Suspense fallback={<Skeleton />}>`。

finding 片段：`<Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} /> ⏎ </Suspense>`

## P0877

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 1 行）config 值型別不一致可能導致行為差異

> 在測試中，未設定時使用 `configUtils.set('memberWelcomeEmailTestInbox', '')`（空字串），而單元測試中 stub 回傳 `undefined`。在程式碼中，`welcomeEmailConfig` 若為空字串，`if (welcomeEmailConfig || ...)` 會視為 falsy，因此不會觸發歡迎郵件；但若 config 實際回傳 `undefined`，行為相同。然而，若 config 回傳其他 falsy 值（如 `null`、`0`），行為可能不同。建議統一 config 的預設值，並在程式碼中明確檢查是否為有效字串。

失敗情境：若 config 設定為空字串，且 `WELCOME_EMAIL_SOURCES.includes(source)` 為 false，則不會建立 outbox；但若 config 設定為 `null`，`welcomeEmailConfig` 為 null，`if (null || ...)` 仍會進入，可能造成非預期行為。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0878

**GT**（rule）UI constants not in UX struct

> The rule requires UI constants and magic numbers to be organized within a dedicated nested UX struct, but the button size constant (40) is hardcoded directly in the constraint definitions instead of being defined in a private struct UX.

GT 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

**finding**（`firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192`，距錨點 0 行）移除 UX struct 並硬編碼按鈕尺寸可能降低可維護性

> 原本的 `UX.buttonSize` 常數被移除，改為直接使用數值 `40`。雖然不影響功能，但若未來需要調整尺寸，需修改多處。建議保留常數或使用有意義的命名。

finding 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

## P0879

**GT**（rule）Logger uses direct logging.getLogger

> The rule requires logger instances to be created using the pattern `logger: "logging.Logger" = get_logger("module_name")` but this code uses direct `logging.getLogger()` call without proper type annotation or using the standard get_logger utility

GT 片段：`import logging ⏎ logger = logging.getLogger(__name__)`

**finding**（`src/prefect/server/events/triggers.py:73`，距錨點 0 行）logger 改為標準 logging 可能遺失 Prefect 的日誌上下文

> 原本使用 `get_logger(__name__)` 取得 Prefect 的 logger，現在改為 `logging.getLogger(__name__)`。這可能導致日誌訊息失去 Prefect 的日誌格式、額外上下文（例如 flow run id）或日誌級別控制。如果這是無意的變更，建議恢復使用 `get_logger`。

finding 片段：`logger = logging.getLogger(__name__)`

## P0880

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29`，距錨點 9 行）tearDown 中呼叫 AppContainer.shared.reset() 可能需 await

> `AppContainer.shared.reset()` 若為 @MainActor 方法，在 async tearDown 中應加上 await。目前未加，可能導致編譯錯誤。

finding 片段：`AppContainer.shared.reset()`

## P0881

**GT**（rule）Direct import from features package

> The rule requires apps/api/v2 to import from @calcom/platform-libraries instead of directly from @calcom/features, but the code imports TeamService directly from @calcom/features/ee/teams/services/teamService

GT 片段：`import { TeamService } from "@calcom/features/ee/teams/services/teamService";`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38`，距錨點 17 行）缺少對 teamId 的擁有權或存在性檢查

> 控制器直接呼叫 `TeamService.createInvite(teamId)`，但沒有先驗證目前使用者是否屬於該團隊或團隊是否存在。雖然有 RolesGuard，但 RolesGuard 可能只檢查全域角色，而非針對特定團隊的成員資格。

失敗情境：使用者可能對任意 teamId 建立邀請，即使不是該團隊成員。

建議：在服務層或控制器中加入團隊成員資格檢查。

finding 片段：`const result = await TeamService.createInvite(teamId);`

## P0882

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）天數計算 off-by-one：第一天就被當成 day 1

> `#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算經過天數，導致在暖機開始當天（day 0）就會得到 day 1。這會使暖機進度提前一天，例如在第一天就套用 day 1 的 limit（237），而不是 day 0 的 200。

**失敗情境**：
- 使用者在 2024-01-15 12:00 建立第一封 email，並在 2024-01-15 13:00 呼叫 `getWarmupLimit`。
- `#getDaysSinceFirstEmail` 會計算 `(Date.now() - firstEmailTime) / (1000*60*60*24)` ≈ 0.0417，`Math.ceil` 後得到 1。
- `getWarmupLimit` 會回傳 day 1 的 limit（237），而不是 day 0 的 200。

**建議修法**：
改用 `Math.floor` 來計算天數，讓 day 0 代表第一天。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0883

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:264`，距錨點 0 行）editor.setEditable 條件改為 member?.expertise 可能導致無 expertise 的成員無法編輯

> 原本條件為 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。若已登入成員沒有設定 expertise（例如新使用者或未填寫），即使有 name，編輯器也會被設為不可編輯，導致無法輸入回覆。建議改回使用 `memberName` 或同時檢查兩者，並新增測試涵蓋此情境。

finding 片段：`editor.setEditable(!!member?.expertise && progress !== 'sending');`

## P0884

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）讀取 tauri.properties 失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0885

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:151`，距錨點 2 行）使用 OnceLock 初始化 Validator 可能隱藏初始化錯誤

> `config_schema_validator` 使用 `OnceLock::get_or_init` 來初始化 `jsonschema::Validator`。如果初始化過程中發生 panic（例如 schema 無效），程式會直接 panic，且後續呼叫都會重複 panic。雖然原本的程式碼也會 panic，但現在錯誤訊息可能較不明確。建議考慮使用 `expect` 提供更清楚的錯誤訊息，或改用 `LazyLock` 以獲得更好的錯誤處理。

finding 片段：`static CONFIG_SCHEMA_VALIDATOR: OnceLock<jsonschema::Validator> = OnceLock::new(); ⏎ CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::valid`

## P0886

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行）缺少輔助函式的單元測試

> 新增的 `createTFunction`、`createUseTranslationMock`、`createTransMock` 等函式沒有對應的測試。建議補上單元測試，確保其行為符合預期，特別是參數處理和 fallback 邏輯。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0887

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行）使用 `||` 可能錯誤處理數值 0

> 在顯示 Run Count 時使用 `{taskRun.run_count || 0}`，若 `run_count` 為 0（合法值），則會顯示 0，這符合預期。但若 `run_count` 為其他 falsy 值（如 null、undefined），也會顯示 0，可能掩蓋資料缺失。建議使用 `??` 運算子以精確處理 null/undefined。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## P0888

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 0 行）對 base_job_template['variables'] 的型別假設可能導致錯誤

> 在 `_fetch_work_pool` 中，原本有檢查 `variables` 是否為 dict，現在直接賦值給 `job_vars_schema`。若 `base_job_template['variables']` 不是 dict（例如是 list 或 None），後續使用 `job_vars_schema` 時可能拋出型別錯誤。建議保留型別檢查，或明確處理非 dict 的情況。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## P0889

**GT**（func）Unnecessary re-rendering on every parameter update with same display name

> The DisplayName component removed the check that prevents re-rendering when the display name hasn't changed (line 50-51). This means that every time SetParametersAsync is called with a changed expression (even if it results in the same display name), the component will trigger a render. This causes performance degradation in scenarios with frequent parameter updates, such as forms with dynamic field expressions, leading to unnecessary DOM updates and potential flickering in the UI.

GT 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ _displayName = newDisplayName;`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 0 行）For 參數變更時不會重新渲染

> 在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算並渲染。然而，如果 `For` 表達式相同但底層模型屬性值變更（例如屬性名稱不變但顯示名稱依賴於其他狀態），元件不會重新渲染，導致顯示名稱過期。

**失敗情境**：假設 `For` 表達式為 `() => model.Name`，且 `model.Name` 的顯示名稱依賴於某個可變狀態（例如語言切換），當語言變更時，`For` 表達式不變，元件不會重新渲染，顯示名稱仍為舊語言。

**建議**：移除 `_previousFieldAccessor` 檢查，每次 `SetParametersAsync` 都重新計算並渲染，或至少提供一個機制讓外部觸發重新渲染。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## P0890

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 3 行）參數序列化方式與舊 mock 不一致

> 舊的全域 mock 在序列化參數時會排除 `ns` 並使用 `JSON.stringify`，但新的 `createTFunction` 使用 `delete params.ns` 後再序列化，兩者結果相同，但若 `options` 為 `undefined` 或 `null`，`delete` 可能拋出錯誤。此外，舊 mock 在 `options` 存在但無其他參數時不會加上後綴，新函式則會加上 `:{}`，可能導致測試斷言失敗。建議明確處理 `options` 為空的情況，並保持與舊行為一致。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## P0891

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142`，距錨點 5 行）拖放排序索引參數順序錯誤

> 在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能導致排序方向相反。`moveItem` 的實作是 `newValues.splice(to, 0, newValues.splice(from, 1)[0])`，其中 `from` 是來源索引，`to` 是目標索引。但呼叫時傳入 `newIndex` 作為 `from`，`oldIndex` 作為 `to`，會將項目從新位置移回舊位置，造成拖放後順序不變或錯亂。應改為 `moveItem(oldIndex, newIndex)`。

finding 片段：`moveItem(newIndex, oldIndex);`

## P0892

**GT**（rule）Force unwrap of URL initializer in tests (second occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤

> 在 testRequestMediaCaptureSuccess 中，decisionHandler 閉包內沒有呼叫 expectation.fulfill()，而是在呼叫 subject.webView(...) 之後直接呼叫 expectation.fulfill()。這會導致測試在 decisionHandler 被呼叫前就完成等待，無法驗證 decisionHandler 是否被呼叫及其內容。若 decisionHandler 從未被呼叫，測試仍會通過，失去測試意義。

建議將 expectation.fulfill() 移回 decisionHandler 閉包內，並移除多餘的 expectation.fulfill()。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0893

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行）使用 String(format:) 搭配本地化字串可能導致崩潰

> `SettingsTextFormatter` 中的 `formatStudiesText` 和 `formatRolloutsText` 使用 `String(format: strings.detailTextStudies, appName)`。`detailTextStudies` 和 `detailTextRollouts` 是本地化字串，其內容可能包含額外的格式說明符（例如翻譯後的字串可能包含 `%d` 或 `%2$@`），這會導致 `String(format:)` 在執行時期因參數數量不符而崩潰，或顯示錯誤的內容。建議改用 `String.localizedStringWithFormat` 或避免使用格式字串，直接使用字串插值或替換。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ } ⏎ `

## P0894

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 0 行）拖曳排序的索引計算未考慮 prefixItems，可能導致資料錯位

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 預期的索引是相對於可移動項目（即排除 prefixItems 後）的索引。當陣列包含 prefixItems 時，拖曳非 prefix 項目會導致移動到錯誤的位置，造成資料順序錯誤。

例如：prefixItems 有 2 項，可移動項目從索引 2 開始。若將索引 2 的項目拖到索引 3，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會將項目移到可移動項目中的索引 3，實際上可能超出範圍或錯位。

建議：在計算索引時減去 `prefixItemsCount`，或改用可移動項目的相對索引。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0895

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行）local_hostname 參數傳遞空字串可能導致 SMTP 連線失敗

> 程式碼使用 `local_host or None` 將空字串轉為 None，但 smtplib.SMTP 的 local_hostname 參數若為 None，會使用 socket.getfqdn() 取得本機主機名稱。若設定 SMTP_LOCAL_HOSTNAME 為空字串，原本意圖可能是使用預設值，但傳遞 None 會觸發 getfqdn()，可能導致 DNS 查詢延遲或失敗。建議明確處理空字串，例如直接傳遞 local_host（若為空字串則由 smtplib 自行處理）或設定為 None 前先檢查。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0896

**GT**（rule）Error enum doesn't use thiserror

> The rule requires custom error enums to use #[derive(thiserror::Error)] with #[error(...)] attributes, but this Error enum manually implements Display and Error traits instead of using thiserror

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:64`，距錨點 22 行）Display 實作與原本 thiserror 格式不完全一致

> 原本 `thiserror` 的 `#[error("{context} {path}: {error}")]` 會直接使用 `path` 的 Display，但手動實作改為 `path.display()`，兩者輸出可能不同（例如 `PathBuf` 的 Display 與 `path.display()` 通常相同，但若 path 包含非 UTF-8 字元，`display()` 會使用替代字元）。建議確認是否可接受。

finding 片段：`Error::Plist { context, path, error } => write!(f, "{} {}: {}", context, path.display(), error),`

## P0897

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:44`，距錨點 21 行）getUrlHistory 回傳型別變更可能導致呼叫端未處理 undefined 而發生錯誤

> 原本的程式碼在 `history` 為 falsy 時會回傳 `undefined`，但修改後直接回傳 `history`，型別從 `URLHistory | undefined` 變成 `URLHistory`。如果呼叫端沒有處理 `undefined` 的情況，可能會在執行時期嘗試存取 `history` 的屬性而拋出錯誤。建議確認所有呼叫端是否都有正確處理 `undefined`，或保留原本的條件判斷。

finding 片段：`const history = getDefaultUrlHistory(); ⏎ return history;`
