# 盲標單 2：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part2.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0095

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 20 行）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行適當消毒，攻擊者可注入惡意腳本，導致儲存型 XSS 攻擊。請確認 `item.html` 的來源已受信任且經過消毒（例如使用 DOMPurify），或改用安全的渲染方式。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0096

**GT**（func）Unnecessary re-rendering on every parameter update with same display name

> The DisplayName component removed the check that prevents re-rendering when the display name hasn't changed (line 50-51). This means that every time SetParametersAsync is called with a changed expression (even if it results in the same display name), the component will trigger a render. This causes performance degradation in scenarios with frequent parameter updates, such as forms with dynamic field expressions, leading to unnecessary DOM updates and potential flickering in the UI.

GT 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ _displayName = newDisplayName;`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 0 行）DisplayName 元件在 For 參數變更時可能不會更新顯示名稱

> 在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱。然而，如果 `For` 表達式相同但底層模型屬性的顯示名稱因動態變更（例如資源檔更新或屬性變更）而改變，元件不會重新渲染。這可能導致顯示名稱過時。建議在每次 `SetParametersAsync` 時都重新計算，或提供一個方法來強制更新。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## P0097

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0098

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0099

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行）stream 的 lpsize 計算可能多算最後一個 listpack

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0100

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 24 行）測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時

> captureFrameAndOrigin 會建立真實的 WKWebView 並載入 https://example.com。這使得測試依賴外部網路連線與 WebKit 的實際行為，可能因網路延遲、離線環境或 WebKit 內部變更而失敗或逾時。建議改用 local test server 或注入 mock 的 navigation delegate 來提供所需的 WKFrameInfo 與 WKSecurityOrigin，以提升測試穩定性。

finding 片段：`webView.load(URLRequest(url: url))`

## P0101

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）多個變數更新時多次 flush，可能導致部分更新遺失

> 在 `on_event` 中，對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。若有多個變數需要更新，且其中一個更新失敗，先前已 flush 的變更不會被回滾，導致資料不一致。建議收集所有更新後只 flush 一次，或使用交易包裹所有更新。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0102

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 0 行）clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## P0103

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:244`，距錨點 19 行）memberName 變數不再有 fallback，可能影響其他邏輯

> 原本 `const memberName = member?.name ?? comment?.member?.name;` 現在改為 `const memberName = member?.name;`。如果 member 為 null 或 name 為 null，memberName 會是 undefined。後續程式碼中 `if (progress === 'sending' || (memberName && isAskingDetails))` 的判斷會受到影響，可能導致 isAskingDetails 流程無法正確觸發。建議確認此變更不會影響其他依賴 memberName 的邏輯。

finding 片段：`const memberName = member?.name;`

## P0104

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## P0105

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 0 行）使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤

> 原本 `client.create_flow_run_from_deployment(deployment.id, ...)` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如從名稱解析而來），而 API 期望 UUID，可能導致型別錯誤。

建議：確認 `deployment_id` 的型別，必要時轉換為 UUID。

finding 片段：`deployment_id,`

## P0106

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2562`，距錨點 7 行）HSETEX 指令可能不存在於舊版 Redis，導致複製中斷

> 此變更將 HINCRBYFLOAT 的複製指令改為 HSETEX。若 replica 或 AOF 重播環境的 Redis 版本不支援 HSETEX（例如舊版或某些 fork），複製或 AOF 重播將失敗。建議確認 HSETEX 在所有支援的版本中皆可用，或提供 fallback 機制。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0107

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0108

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:5`，距錨點 0 行）未使用的常數 UNUSED_CONSTANT

> 新增的 `UNUSED_CONSTANT` 常數未被使用，且其值為字串，可能觸發 lint 規則（如 no-unused-vars）。建議移除。

finding 片段：`const UNUSED_CONSTANT = "this-should-be-removed";`

## P0109

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:342`，距錨點 23 行）Redis pipeline 寫入失敗時，快取資料遺失且無重試機制

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，使用 pipeline 批次寫入 Redis。如果 `pipe.execute()` 拋出例外，程式只記錄錯誤，但不會將資料寫入快取，也不會影響回傳值。這會導致下次查詢時仍然 cache miss，增加 API 負載。雖然不影響正確性，但降低了快取效益。

**失敗情境**：Redis 暫時不可用或 pipeline 執行失敗時，所有從 API 取得的資料都不會被快取，下次相同查詢仍會打到 API。

**建議**：考慮加入簡單的重試機制，或在 pipeline 失敗時降級為逐筆寫入（或至少記錄警告）。

finding 片段：`except Exception: ⏎ logger.exception("get_plan_bulk_with_cache: redis pipeline failed")`

## P0110

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0111

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73`，距錨點 0 行）客戶端過濾可能導致已選取的區塊文件無法顯示

> `filteredData` 使用 `deferredSearch` 進行客戶端過濾，但 `selectedBlockDocument` 是從 `filteredData` 中尋找。若使用者選取了一個區塊文件後，輸入的搜尋字串與該文件名稱不符，則 `selectedBlockDocument` 會變成 `undefined`，導致觸發器顯示「Select a block...」而非已選取的名稱。

**失敗情境**：使用者選取了名為 `my_block_0` 的區塊文件，然後在搜尋框中輸入 `xyz`，此時 `filteredData` 為空，`selectedBlockDocument` 為 `undefined`，觸發器顯示佔位文字，但實際上仍有選取值。

**建議**：`selectedBlockDocument` 應從原始 `data` 中尋找，而非 `filteredData`。

finding 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

## P0112

**GT**（rule）Direct logging.getLogger() call used

> The rule requires loggers to be instantiated using the pattern `logger: "logging.Logger" = get_logger("module_name")` instead of direct `logging.getLogger()` calls

GT 片段：`# Log which UI version is being served ⏎ if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

**finding**（`src/prefect/server/api/server.py:532`，距錨點 0 行）日誌訊息未使用結構化日誌

> 新增的日誌訊息使用 `ui_logger.info("Serving experimental V2 UI")`，但未包含任何上下文（如版本、路徑）。建議使用結構化日誌或至少包含相關資訊，以便於除錯。

finding 片段：`ui_logger.info("Serving experimental V2 UI")`

## P0113

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46`，距錨點 3 行）強制轉型為 AppCompatActivity 可能導致 ClassCastException

> `(activity as AppCompatActivity)` 假設傳入的 activity 一定是 `AppCompatActivity`。如果 Tauri 支援的 activity 類型未來擴展或使用者自訂 activity 未繼承 `AppCompatActivity`，此處將拋出 `ClassCastException`。建議檢查 activity 類型或使用更通用的 `ComponentActivity`（`OnBackPressedDispatcher` 的擁有者）。

finding 片段：`(activity as AppCompatActivity).onBackPressedDispatcher.addCallback(activity, callback)`

## P0114

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 18 行）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行消毒，攻擊者可注入惡意腳本，導致儲存型 XSS。請確認 `item.html` 的來源是否已經過消毒（例如使用 DOMPurify），或改用安全的渲染方式（如 `react-html-parser` 或將 HTML 轉為純文字）。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0115

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## P0116

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）number 輸入類型改為 text 可能影響使用者體驗

> 將 number 輸入的 `type` 從 `"number"` 改為 `"text"`，這會失去瀏覽器原生的數字輸入行為（如上下箭頭、數字鍵盤、自動驗證）。若此變更非刻意為之，建議保留 `type="number"`；若為了移除 maxLength 限制，可考慮其他方式。

finding 片段：`type="text"`

## P0117

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:207`，距錨點 4 行）格式化字串參數數量不符

> `detailTextStudiesV2` 與 `detailTextRollouts` 的字串值包含一個 `%@` 佔位符，但 `SettingsTextFormatter` 中的 `formatStudiesText` 與 `formatRolloutsText` 方法僅傳入一個 `appName` 參數，數量相符。然而，`detailTextStudies` 與 `detailTextSendUsageData` 的原始字串也包含 `%@`，但未提供對應的格式化方法，可能導致呼叫端自行格式化時出錯。建議確認所有使用這些字串的程式碼都正確處理了格式化參數。

finding 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

## P0118

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not include explicit AAA structure comments ('// Arrange', '// Act', '// Assert' or '// Act & Assert'), violating the test readability rule.

GT 片段：`public async Task CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral(HttpTransportType transportType, string protocolName) ⏎ { ⏎ using (StartVerifiableLog()) ⏎ {`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188`，距錨點 1 行）將測試標記為隔離可能掩蓋真實問題

> 新增 `[QuarantinedTest]` 屬性會使測試在 CI 中暫時停用，可能導致相關錯誤被忽略。若問題未在隔離期間修復，可能累積技術債。建議確認隔離原因並追蹤修復進度。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`

## P0119

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能導致授權不足

> 此端點為讀取錄音，但權限改為 `BOOKING_WRITE`。若客戶端僅有讀取權限，將無法存取，可能造成整合中斷。建議確認此變更是否為刻意，或應維持 `BOOKING_READ`。

finding 片段：`@Permissions([BOOKING_WRITE])`

## P0120

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0121

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:264`，距錨點 0 行）member 可能為 null 時 editor.setEditable 判斷錯誤

> 原本的判斷是 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。如果 `member` 為 null，`member?.expertise` 會是 undefined，導致 `!!undefined` 為 false，因此編輯器會被設為不可編輯。這可能導致未登入或 member 資料未載入時，使用者無法編輯回覆內容。建議改為 `!!member && !!member.expertise && progress !== 'sending'` 或保留原本的 memberName 判斷。

finding 片段：`editor.setEditable(!!member?.expertise && progress !== 'sending');`

## P0122

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 0 行）autoCloseOnSelect 在 multiselect 中可能造成非預期關閉

> 在 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { onClose?.(); }`，但此處呼叫的 `onClose` 可能只關閉 popover 而不會重置選取狀態，且與下方註解「For multiselect, don't close the popover to allow multiple selections」矛盾。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## P0123

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 27 行）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## P0124

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 13 行）拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0125

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 16 行）Hot Reload 時未清除顯示名稱快取

> 在靜態建構函式中，當 Hot Reload 的 MetadataUpdateSupported 為 true 時，訂閱了 OnDeltaApplied 事件並呼叫 ClearCache。但 ClearCache 只清除了 `_memberInfoCache`，沒有清除 `_displayNameCache`。這可能導致在 Hot Reload 後顯示名稱仍然使用舊的快取值。建議在 ClearCache 中同時清除兩個快取。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0126

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 的實作中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體如 `Nsis`、`App`、`Dmg` 都回傳小寫字串。這可能導致序列化或顯示時的不一致，建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0127

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1122`，距錨點 0 行）copyBtn 的 bookingUrl 未使用 eventType.bookingUrl

> 在 copyBtn 的事件處理中，bookingUrl 仍使用硬編碼的 `https://cal.com/...`，未像 previewBtn 一樣使用 `eventType.bookingUrl`。這可能導致複製的連結與實際 bookingUrl 不一致。建議改為 `eventType.bookingUrl || ...`。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## P0128

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:275`，距錨點 0 行）bookingUrl 為空時顯示 fallback 但可能與實際不符

> 當 `props.bookingUrl` 為空時，回傳 `cal.com/${props.username}/`，但若 username 也為空，則會顯示 `cal.com/undefined/`。建議在 username 缺失時提供更合理的 fallback，或隱藏前綴。

finding 片段：`return `cal.com/${props.username}/`;`

## P0129

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行）返回鍵處理可能導致 callback 永久停用

> 在 `handleOnBackPressed` 中，當 WebView 無法回上一頁時，程式碼會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再將 `this.isEnabled = true`。然而，如果 `activity.onBackPressed()` 拋出例外或未正常返回（例如 activity 不是 `AppCompatActivity` 或系統行為不同），`isEnabled` 將永遠保持 `false`，導致後續返回鍵事件完全失效。建議使用 try-finally 確保 `isEnabled` 恢復，或改用 `OnBackPressedCallback` 的 `setEnabled` 方法管理狀態。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## P0130

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 15 行）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## P0131

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:247`，距錨點 4 行）reload_config 可能導致資料競爭

> `reload_config` 接受 `&mut ConfigMetadata`，但呼叫端可能同時有多個執行緒持有同一個 `ConfigMetadata` 的參考（例如在 `run_dev_watcher` 中，`config` 被包在 `Mutex` 中，但鎖定後傳遞的是 `&mut` 參考，而其他執行緒可能也在存取）。

具體情境：在 dev 模式下，檔案監視器執行緒與主執行緒可能同時存取 `config`，導致資料競爭。

建議：確保所有對 `ConfigMetadata` 的存取都透過 Mutex 保護，或使用不可變共享（如 `Arc<RwLock<ConfigMetadata>>`）。

finding 片段：`pub fn reload_config( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

## P0132

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行）notlike 查詢未傳入 escape 參數

> 在 'not contains' 條件中，使用了 notlike 但未傳入 escape 參數。這會導致跳脫後的反斜線被資料庫視為普通字元，而非跳脫字元，使得 % 和 _ 仍被當作萬用字元，造成查詢結果不正確。

建議：在 notlike 呼叫中加入 escape="\\"。

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## P0133

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:292`，距錨點 33 行）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## P0134

**GT**（func）Stream entries incorrectly marked as referenced when cgroups_ref is NULL

> When cgroups_ref is NULL (which occurs after DEBUG RELOAD with empty PEL), the function returns 1 indicating the entry IS referenced, when it should return 0 indicating it is NOT referenced. This inverted logic prevents XADD/XTRIM operations with the ACKED strategy from correctly deleting entries that have been fully acknowledged by all consumer groups. The result is a memory leak where stream entries accumulate unnecessarily because they are incorrectly protected from deletion even though no consumer group has them in their pending entry list.

GT 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1; ⏎ unsigned char buf[sizeof(streamID)]; ⏎ streamEncodeID(buf, id);`

**finding**（`src/t_stream.c:2708`，距錨點 0 行）streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留

> 新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1，表示該 entry 被引用。這可能導致 stream 的 entry 無法被刪除，即使沒有 consumer group 引用它。

失敗情境：當 stream 沒有 consumer groups 時，呼叫 streamEntryIsReferenced 會回傳 1，使得呼叫者認為 entry 仍被引用，因此不會刪除它，可能造成記憶體洩漏或資料不一致。

建議：確認此處的意圖。若 cgroups_ref 為 NULL，應回傳 0（未被引用）而非 1。或者，應檢查呼叫者是否正確處理此情況。

finding 片段：`if (!s->cgroups_ref) return 1;`

## P0135

**GT**（func）Incorrect type conversion in generic component parameter assertion

> The test validates a generic component with an int type parameter but uses Convert.ToInt64 instead of Convert.ToInt32 to assert the parameter value. Since the parameter is defined as int (System.Int32) in GenericTestComponent<int>, this creates a type mismatch. The assertion compares a long (Int64) value to the expected int (Int32) value 42, which will cause the test to fail even though the component deserialization is working correctly. This breaks the validation logic for generic component parameters.

GT 片段：`var parameters = deserializedDescriptor.Parameters.ToDictionary(); ⏎ Assert.Single(parameters); ⏎ Assert.Contains("Value", parameters.Keys); ⏎ Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 0 行）參數值型別轉換脆弱

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 Int64。但 `parameters["Value"]` 的實際型別取決於 deserializer 的實作，若其為 `JsonElement` 或 `int`，此轉換可能拋出例外或得到非預期結果。

建議直接斷言參數值的型別與值，例如：
```csharp
var value = Assert.IsType<JsonElement>(parameters["Value"]);
Assert.Equal(42, value.GetInt32());
```

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0136

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）`window_features` 方法中 size 與 position 的設定順序可能影響視窗初始位置

> 在 `window_features` 方法中，原本先設定 position 再設定 size，現在改為先設定 size 再設定 position。在某些平台或視窗管理器中，設定順序可能影響最終視窗位置（例如先設定 size 可能導致 position 被重設）。建議確認此變更不會造成回歸，或考慮保持原有順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0137

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:207`，距錨點 0 行）格式化字串參數數量不符

> `detailTextStudiesV2` 與 `detailTextRollouts` 的字串值包含一個 `%@` 佔位符，但 `SettingsTextFormatter` 中的 `formatStudiesText` 與 `formatRolloutsText` 方法僅傳入一個 `appName` 參數，數量相符。然而，`detailTextStudies` 與 `detailTextSendUsageData` 的原始字串也包含 `%@`，但未提供對應的格式化方法，可能導致呼叫端自行格式化時出錯。建議確認所有使用這些字串的程式碼都正確處理了格式化參數。

finding 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

## P0138

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0139

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行）RequestBody.Description 指派順序變更可能影響範例設定

> 原本 `operation.RequestBody.Description = description;` 在範例處理之前，現在移到範例處理之後。若範例處理中發生例外，Description 可能不會被設定。建議確認此順序變更是否必要，或將 Description 指派保持在前面。

finding 片段：`operation.RequestBody.Description = description;`

## P0140

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:18`，距錨點 8 行）require 陳述式缺少分號

> `const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list');` 和 `const MagicLink = require('../../lib/magic-link/magic-link');` 保留了分號，但與前面無分號的陳述式不一致。

finding 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

## P0141

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0142

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 10 行）路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含

> 在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0143

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:23`，距錨點 17 行）query key 從 'category' 改為 'tab' 可能破壞既有連結

> `useActivePluginType` 的 query key 從 `'category'` 改為 `'tab'`。若使用者已將帶有 `?category=...` 的網址加入書籤或分享，升級後這些連結將不再生效，可能導致使用者看到非預期的分類。建議考慮保留舊 key 的相容性，或確認此變更為可接受的 breaking change。

finding 片段：`return useQueryState('tab', marketplaceSearchParamsParsers.category)`

## P0144

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 12 行）並行建置可能產生相同的 versionCode

> 在 `generate_tauri_properties` 中，讀取舊的 versionCode 後直接加 1 寫入，沒有使用鎖定或原子操作。如果兩個建置同時執行（例如 CI 中並行觸發），它們可能讀到相同的舊值，並產生相同的 versionCode，導致上架衝突。建議使用檔案鎖（例如 `flock`）或將 versionCode 儲存在可原子更新的位置（如資料庫或遠端服務）。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0145

**GT**（func）Unused variable 'elecount' causes build failure with -Werror

> The variable 'elecount' is declared and incremented in the QUICKLIST encoding branch (line 1236: 'elecount += node->count') but is never used after the PR changed the calculation from 'elesize/elecount' to 'elesize/samples'. This creates an unused-but-set variable which triggers compiler warnings under -Wall (enabled in Makefile) and causes build failures when compiling with -Werror flag. This violates AGENTS.MD Rule #4 which requires the codebase to compile without warnings when REDIS_CFLAGS="-Werror" is enabled.

GT 片段：`size_t elesize = 0, elecount = 0, samples = 0; ⏎ ... ⏎ if (o->encoding == OBJ_ENCODING_QUICKLIST) { ⏎ quicklist *ql = o->ptr;`

**finding**（`src/object.c:1239`，距錨點 0 行）quicklist 取樣計算使用錯誤的分母

> 在 quicklist 的記憶體估算中，原本使用 `elecount` 作為平均的分母，但此 PR 改為 `samples`。然而 `samples` 是已取樣的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會高估每個元素的平均大小，導致整體記憶體估算偏高。

**失敗情境**：建立一個包含多個元素的 quicklist，每個節點包含多個元素，呼叫 MEMORY USAGE 會得到比實際記憶體用量更高的數值。

**建議**：保留原本的 `elecount` 作為分母，或改為計算每個節點的平均元素數再乘以節點數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0146

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 setLoading(false) 可能導致 minimal 模式永遠顯示 loading 狀態

> 在 minimal 模式下，送出成功後原本會呼叫 setLoading(false) 來停止 loading 動畫，但此 PR 移除了該行。若 loading 狀態沒有在其他地方被重設，使用者會看到無限的 loading 指示。請確認是否有其他機制（例如元件 unmount 或 effect）會重設 loading，否則應保留此行。

finding 片段：`setSuccess(true);`

## P0147

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳索引錯亂

> `sortableKeys` 由 `localKeyedValues.map((item) => item.key)` 產生，包含所有項目，但實際上只有非 prefix items 可拖曳（`canMove` 為 true）。當存在 prefix items 時，拖曳一般項目時，`over.id` 可能指向不可拖曳的 prefix item，導致 `newIndex` 計算錯誤，或拖曳行為不符合預期。建議 `sortableKeys` 只包含可拖曳項目的 key，例如先 filter `getCanMoveForIndex(index)` 為 true 的項目。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0148

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 0 行）reader mode 狀態布林值對調可能造成遙測數據錯誤

> 原本 `case .available: true` 改為 `false`，`default: false` 改為 `true`。這會使 `isReaderModeEnabled` 的語意相反，導致 `readerModeButtonTapped` 遙測事件記錄錯誤的啟用狀態。若此變更非預期，請修正；若為預期，請確認遙測定義是否需同步調整。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## P0149

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email.trim() 可能改變原本的驗證行為

> 在提交時對 email 進行 trim 是合理的，但需確認驗證邏輯（isValidEmail）是否也應該使用 trim 後的值，否則可能出現前後不一致。例如使用者輸入前後有空白的 email，驗證可能通過但提交的是 trim 後的值，或反之。

finding 片段：`onSubmit({email: email.trim()});`

## P0150

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 0 行）逐字稿端點的 guard 順序可能影響錯誤回應

> 在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## P0151

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0152

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0153

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 0 行）config 值未驗證，可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，但未驗證其型別或內容。若 config 值為空字串、0、false 等 falsy 值，則條件為 false，不會建立 outbox；若為任意 truthy 值（例如 'false' 字串），則會建立 outbox。建議明確驗證該值是否為有效的 email 或布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0154

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126`，距錨點 0 行）renderer 切換時可能錯誤拋出例外

> 條件 `if (manager && currentRendererId === rendererId)` 只在 manager 存在且 rendererId 相同時拋出例外。若 manager 存在但 rendererId 不同（例如從 Server 切換到 WebAssembly），則不會拋出例外，而是直接覆寫 manager 和 currentRendererId。這可能導致舊 manager 的資源未被正確處理，或新舊 manager 狀態混亂。

建議明確處理 rendererId 不同的情況，例如記錄警告或採取其他措施。

finding 片段：`if (manager && currentRendererId === rendererId) { ⏎ throw new Error('Dynamic root components have already been enabled.'); ⏎ }`

## P0155

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 9 行）缺少對新功能的測試

> 新增的自動遞增邏輯沒有對應的單元測試或整合測試。建議添加測試覆蓋以下情境：首次建置、正常遞增、檔案不存在、檔案格式錯誤、並行建置（如果實作鎖定）等。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0156

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0157

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 未被使用

> 新增的 `SettingsTextFormatter` 類別目前沒有被任何程式碼引用，可能是為了未來使用而預留，但若無計畫使用，建議移除以避免死代碼。

finding 片段：`class SettingsTextFormatter {`

## P0158

**GT**（func）Token caching stores entire object instead of token string

> In the getToken method, when caching the JWT token, the code now stores the entire tokenData object (containing both 'token' and 'exp' properties) instead of just extracting the token string. This causes the returned token structure to be malformed as {token: {token: string, exp: number}, exp: number} instead of the expected {token: string, exp: number}. This will break any consumers of the Tinybird API (like the /api/tinybird/token endpoint and stats/tinybird.js) that expect a string token value, causing authentication failures when making requests to Tinybird pipes.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）_serverToken 型別變更可能導致後續使用錯誤

> `_serverToken` 原本存 token 字串，現在改存整個 token 物件（包含 `token` 和 `exp`）。若其他程式碼仍預期 `_serverToken` 是字串，可能導致型別錯誤或功能失效。請確認所有使用 `_serverToken` 的地方都已更新。

finding 片段：`this._serverToken = tokenData;`

## P0159

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 15 行）emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題

> 原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

finding 片段：`emailAddressService.init(),`

## P0160

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行）versionCode 達到上限時靜默飽和

> 使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0161

**GT**（func）Unsafe concurrency annotation on non-thread-safe static property

> The static generator property is marked with nonisolated(unsafe) despite the comment explicitly stating 'ContentBlockerGenerator is not thread safe'. This annotation bypasses Swift 6's concurrency safety checks and allows the non-thread-safe ContentBlockerGenerator to be accessed from multiple isolation domains without protection. This creates a potential data race condition where multiple threads could access the generator simultaneously, leading to undefined behavior, crashes, or data corruption. The unsafe annotation should only be used when the developer can guarantee thread safety through other means, which the comment explicitly contradicts.

GT 片段：`@main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏資料競爭

> `generator` 被標註為 `nonisolated(unsafe) static let`，這表示編譯器不會檢查其執行緒安全性。如果 `ContentBlockerGenerator` 實例不是執行緒安全的，多個執行緒同時存取可能導致資料競爭。建議確認 `ContentBlockerGenerator` 是否為 Sendable，或改用其他隔離機制（如 actor 或鎖）。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0162

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）console.log 可能洩漏使用者輸入資料

> 新增的 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })` 會將批次輸入的標頭資料輸出到瀏覽器主控台。`headerData` 可能包含使用者上傳的 CSV 內容，若其中含有敏感資訊（如個人資料），將造成資料外洩風險。

建議：移除此 console.log，或改用不記錄資料內容的除錯方式。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0163

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行）重新命名檔案時混入非預期的格式變更

> 此檔案除了更新 require 路徑外，還移除了所有行尾分號，並將部分 require 陳述式的引號從單引號改為雙引號。這與專案中其他檔案的風格不一致，且可能違反 ESLint 規則。建議只保留必要的路徑變更，避免混入格式調整。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0164

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行）position 呼叫參數格式不一致

> 在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，雖然這在 Rust 中不會導致編譯錯誤，但與專案中其他程式碼的風格不一致。建議改為 `self.window_builder.position(position.x, position.y);`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## P0165

**GT**（rule）Error enum doesn't use thiserror

> The rule requires custom error enums to use #[derive(thiserror::Error)] with #[error(...)] attributes, but this Error enum manually implements Display and Error traits instead of using thiserror

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 38 行）手動實作 Error trait 可能遺漏 source 方法

> 新的 Error 實作中，`source()` 方法僅回傳部分變體的底層錯誤（TempDir、FailedToUploadApp、CommandFailed、Fs），其他變體（如 Plist、X509Certificate 等）未提供 source。這可能導致錯誤鏈不完整，影響使用 `anyhow` 或 `thiserror` 的呼叫端。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## P0166

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 0 行）未更新 jsComponentParametersByIdentifier

> 在重新啟用時，程式碼更新了 `manager` 和 `currentRendererId`，但未更新 `jsComponentParametersByIdentifier`。若新的 renderer 提供了不同的參數，舊參數仍會被使用，可能導致元件初始化時使用過時資料。

建議在重新啟用時一併更新 `jsComponentParametersByIdentifier`。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## P0167

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32`，距錨點 18 行）loading 初始狀態依賴 account 可能導致閃爍

> `loading` 的初始值使用 `useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed)`，但 `account` 在首次 render 時可能尚未載入（undefined），導致初始為 false。當 account 載入後，effect 會設定 loading，但可能造成短暫的 UI 閃爍。建議在 account 載入前顯示載入指示，或延後判斷。

finding 片段：`const [loading, setLoading] = useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed);`

## P0168

**GT**（func）Keyword trimming logic may break escape sequences

> The workflow app service trims the keyword to 30 characters and then applies escape_like_pattern(). However, this creates a subtle bug: if a backslash character appears exactly at position 30, the trim could split an escape sequence that the user intended. More critically, if special characters appear in positions 28-30, they'll be included in the escaped output, but any context around them will be lost, potentially creating malformed escape sequences. The trimming should occur AFTER escaping to preserve the integrity of the escape sequences, or better yet, the escaping should be done before any string manipulation.

GT 片段：`# Escape special characters in keyword to prevent SQL injection via LIKE wildcards ⏎ keyword_trimmed = keyword[:30] ⏎ escaped_keyword = escape_like_pattern(keyword_trimmed) ⏎ keyword_like_val = f"%{escaped_keyword}%"`

**finding**（`api/services/workflow_app_service.py:94`，距錨點 0 行）移除 unicode_escape 可能導致搜尋行為改變

> 原本的程式碼將關鍵字進行 unicode_escape 編碼，以處理非 ASCII 字元。新程式碼直接使用原始關鍵字，可能導致對包含非 ASCII 字元的搜尋行為改變，特別是在資料庫儲存為 unicode escape 格式時。

建議：確認此變更不會影響現有功能，或保留必要的編碼處理。

finding 片段：`keyword_like_val = f"%{escaped_keyword}%"`

## P0169

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:458`，距錨點 4 行）V2 UI 啟用時，靜態路徑設定可能錯誤

> 在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`source_static_path` 設為 `prefect.__ui_v2_static_path__`，但 `static_subpath` 設為 `prefect.__ui_static_subpath__`（V1 的子路徑）。這可能導致 V2 UI 的靜態檔案被複製到 V1 的子路徑，造成路徑混淆或覆蓋。請確認 `static_subpath` 是否應為 V2 專用的子路徑。

finding 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

## P0170

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行）命名空間與類別縮排變更可能造成不必要的 diff

> 此變更將原本的 file-scoped namespace 改為 block-scoped namespace，並調整類別縮排。這與專案中其他測試檔案的風格可能不一致，且增加了 diff 的噪音。若無特殊原因，建議維持原本的 file-scoped namespace 寫法。

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ { ⏎ public class ServerComponentDeserializerTest ⏎ {`

## P0171

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0172

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行）`merge_with` 不再合併設定，而是儲存擴充資料，可能破壞合併功能

> 原本的程式碼會將 `merge_config` 合併到 `config_metadata.inner` 中，但此變更改為將 `merge_config` 存入 `extensions`。這可能導致合併功能失效，影響依賴此行為的呼叫者。請確認此變更的意圖，若需保留合併行為，應保留原本的合併邏輯。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## P0173

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38`，距錨點 0 行）Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException

> 原本的程式碼在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 NavigateToLogin，否則使用 `_tokenResult.RedirectUrl!`。修改後，當 `InteractionOptions != null` 但 `InteractiveRequestUrl` 為 null 時，會直接傳遞 null 給 NavigateToLogin，可能導致 NullReferenceException。建議保留 null 檢查或提供替代邏輯。

finding 片段：`if (_tokenResult.InteractionOptions != null) ⏎ { ⏎ _navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, _tokenResult.InteractionOptions); ⏎ }`

## P0174

**GT**（rule）MSTest attribute in xUnit project

> The rule requires test projects to consistently use the xUnit framework, but the test method uses MSTest's [TestMethod] attribute instead of xUnit's [Fact] attribute

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException()`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 2 行）AppContext.SetSwitch 參數反轉可能導致測試失效

> 原本設定 DisableThrowNavigationException 為 false，現在改為 true。若測試目的是驗證例外拋出，設為 true 會停用例外，可能使測試無法觸發預期行為。需確認此變更是否為預期修正。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0175

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 7 行）transcripts 端點的 guard 順序與 recordings 不一致

> recordings 端點使用 `@UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`，而 transcripts 端點使用 `@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`。順序不同可能影響錯誤回應（例如未驗證時先觸發 Pbac 而非 ApiAuth）。建議統一順序。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## P0176

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）slot 可能未初始化即被使用

> 在 `extractKeysAndSlot` 中，原本的程式碼會先將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，再根據 `num_keys` 決定是否呼叫 `extractSlotFromKeysResult`。修改後，只有當 `num_keys > 0` 時才會設定 `*slot`，若 `num_keys == 0` 或 `num_keys < 0`，`*slot` 將保持未初始化狀態。呼叫端若未檢查 `num_keys` 就直接使用 `*slot`，可能導致未定義行為。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT;`。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0177

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0178

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126`，距錨點 6 行）renderer 切換時可能錯誤拋出例外

> 條件 `if (manager && currentRendererId === rendererId)` 只在 manager 存在且 rendererId 相同時拋出例外。若 manager 存在但 rendererId 不同（例如從 Server 切換到 WebAssembly），則不會拋出例外，而是直接覆寫 manager 和 currentRendererId。這可能導致舊 manager 的資源未被正確處理，或新舊 manager 狀態混亂。

建議明確處理 rendererId 不同的情況，例如記錄警告或採取其他措施。

finding 片段：`if (manager && currentRendererId === rendererId) { ⏎ throw new Error('Dynamic root components have already been enabled.'); ⏎ }`

## P0179

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0180

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0181

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行）Router context 中的 queryClient 與實際使用的 queryClient 不一致

> 在 `createTestRouter` 中，`context` 設定了新的 `QueryClient`，但 decorator 中使用的 `QueryClientProvider` 是外部的 `queryClient`。這可能導致 router 內部使用不同的 queryClient，造成快取不一致或測試問題。建議統一使用同一個 queryClient 實例。

finding 片段：`context: { queryClient: new QueryClient() },`

## P0182

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0183

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:546`，距錨點 30 行）取消單一預訂時改用 uid 作為唯一條件可能導致錯誤

> 原本使用 `uid ? { uid } : { id }` 來決定更新條件，現在固定使用 `uid: bookingToDelete.uid`。若 `bookingToDelete.uid` 為空或未定義，將導致更新失敗。請確認 `bookingToDelete.uid` 在取消流程中一定存在，或保留原本的條件邏輯。

finding 片段：`const updatedBooking = await bookingRepository.updateIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ uid: bookingToDelete.uid, ⏎ },`

## P0184

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 15 行）JWT 簽署時移除 `noTimestamp` 選項，可能影響 token 格式

> 原本 `jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true})` 明確指定不加入 `iat` 時間戳，現在改為 `jwt.sign(payload, this.tinybirdConfig.adminToken)`，會自動加入 `iat`。這可能影響 token 的 payload 結構，若 Tinybird 端預期沒有 `iat` 欄位，可能導致驗證失敗或行為改變。

**建議**：確認 Tinybird 端是否接受含有 `iat` 的 token，若不需要可保留 `noTimestamp: true`。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0185

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行）Slot 型別中 userIds 型別從 number[] 改為 string[]，可能造成型別不符

> 原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot 的 userIds 型別為 number[]，但此處新定義的 Slot 將 userIds 改為 string[]。若實際資料中 userIds 為數字陣列，則使用此型別的程式碼（例如將 userIds 傳給其他函式）會出現型別錯誤。建議確認 userIds 的實際型別，若為 number[] 則應改回，或使用 union 型別。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## P0186

**GT**（rule）Force unwrap of URL initializer in tests (third occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0187

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:52`，距錨點 0 行）generate_github_alternative_url 忽略替代 URL，可能導致下載失敗

> 在 `generate_github_alternative_url` 函式中，原本應回傳替代 URL（`alt_url`），但修改後改為回傳原始 URL（`url.to_owned()`）。這會使函式失去備援功能：當原始 GitHub URL 無法存取時，原本設計的鏡像站或替代來源將不會被使用，可能導致下載失敗。

**失敗情境**：當使用者位於無法直接存取 GitHub 的環境（例如某些地區或企業網路），且設定了 GitHub 鏡像站時，此函式會忽略鏡像 URL，仍嘗試從原始 GitHub 下載，導致建置工具下載失敗。

**建議**：確認此修改是否為預期行為。若需保留備援機制，應回傳 `alt_url`；若因其他原因需使用原始 URL，請在 PR 描述中說明理由。

finding 片段：`.map(|_alt_url| { ⏎ ( ⏎ ureq::Agent::config_builder() ⏎ .user_agent(BUNDLER_USER_AGENT)`

## P0188

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`
