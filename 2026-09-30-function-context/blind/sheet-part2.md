# 盲標單 2：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part2.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0101

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1125`，距錨點 0 行）copyBtn 的 bookingUrl 未使用 eventType.bookingUrl

> 在 content.ts 的 copyBtn 事件處理中，bookingUrl 的建構仍使用硬編碼的 `https://cal.com/...`，未使用 `eventType.bookingUrl`，與其他部分的修改不一致。這可能導致複製的連結與實際 bookingUrl 不同，若後端提供了自訂網域或不同路徑，使用者會複製到錯誤的連結。建議統一使用 `eventType.bookingUrl` 或提供 fallback。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## P0102

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:469`，距錨點 31 行）organize_agent_history 中 tool_inputs 與 tool_responses 的解析邏輯重複且可能不一致

> 原本對 tool_input 和 observation 的 JSON 解析各自獨立，現在改為先檢查是否為空字串再解析。但兩者的處理邏輯幾乎相同，可考慮抽成輔助函式以減少重複。

失敗情境：若未來需要修改解析邏輯，可能只改到其中一處而導致不一致。

建議：將 JSON 解析邏輯抽成共用函式。

finding 片段：`tool_input_payload = agent_thought.tool_input ⏎ if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload)`

## P0103

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 2 行）useEffect 依賴陣列為空，可能無法正確偵測內容截斷

> `useEffect` 僅在掛載時執行一次，若 `item.html` 內容在掛載後變更（例如虛擬滾動重用元件），`isClamped` 可能不會更新。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監測內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0104

**GT**（func）Unused variable 'elecount' causes build failure with -Werror

> The variable 'elecount' is declared and incremented in the QUICKLIST encoding branch (line 1236: 'elecount += node->count') but is never used after the PR changed the calculation from 'elesize/elecount' to 'elesize/samples'. This creates an unused-but-set variable which triggers compiler warnings under -Wall (enabled in Makefile) and causes build failures when compiling with -Werror flag. This violates AGENTS.MD Rule #4 which requires the codebase to compile without warnings when REDIS_CFLAGS="-Werror" is enabled.

GT 片段：`size_t elesize = 0, elecount = 0, samples = 0; ⏎ ... ⏎ if (o->encoding == OBJ_ENCODING_QUICKLIST) { ⏎ quicklist *ql = o->ptr;`

**finding**（`src/object.c:1239`，距錨點 0 行）quicklist 取樣平均計算可能不準確

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 計算平均元素大小，現在改為 `elesize/samples*ql->count`。但 `samples` 是取樣的節點數，而 `elesize` 是這些節點中所有元素的總大小，`elecount` 是這些節點中的元素總數。若每個節點的元素數量不同，使用 `samples` 作為分母會導致平均元素大小計算錯誤。例如，若取樣了 5 個節點，但其中一個節點包含 100 個元素，其他節點各包含 1 個元素，則 `elesize` 會包含 104 個元素的大小，但除以 `samples`（5）會高估平均元素大小。建議改回使用 `elecount` 作為分母，或改為計算每個節點的平均元素大小再乘以節點數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0105

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 23 行）跨欄位驗證使用 field_validator 可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中新增的跨欄位驗證使用 `@field_validator`，但 `info.data` 在 field_validator 中可能尚未包含其他欄位（取決於驗證順序），導致 `info.data.get("bucket")` 可能為 None，使驗證失效。應改用 `@model_validator(mode='after')` 進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0106

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）argv 陣列大小不足，寫入 argv[5] 導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但後續指派 `argv[5] = c->argv[2];`，索引 5 超出陣列範圍（合法索引為 0-4）。這會造成堆疊緩衝區溢位，可能導致程式崩潰或任意程式碼執行。

失敗情境：當欄位有過期時間時，執行 HINCRBYFLOAT 即觸發此寫入。

建議修正：將陣列大小改為 6，例如 `robj *argv[6];`。

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0107

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142`，距錨點 0 行）拖放排序索引參數順序錯誤

> 在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能導致排序方向相反。`moveItem` 的實作是 `newValues.splice(to, 0, newValues.splice(from, 1)[0])`，其中 `from` 是來源索引，`to` 是目標索引。但呼叫時傳入 `newIndex` 作為 `from`，`oldIndex` 作為 `to`，會將項目從新位置移回舊位置，造成拖放後順序不變或錯亂。應改為 `moveItem(oldIndex, newIndex)`。

finding 片段：`moveItem(newIndex, oldIndex);`

## P0108

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 4 行）`run_deployment` 失去同步執行能力，破壞向後相容性

> 原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步與非同步環境中呼叫。現在改為 `run_deployment = arun_deployment`，而 `arun_deployment` 是純 async 函式，因此在同步環境中呼叫 `run_deployment(...)` 會回傳 coroutine 物件，而不會實際執行流程。這會導致所有現有同步呼叫者的程式碼靜默失敗（例如在腳本或同步函式中呼叫）。

建議：保留一個同步包裝函式，例如使用 `asyncio.run` 或 `anyio.from_thread.run` 來執行 async 版本，或使用 `@sync_compatible` 裝飾器來維持原有行為。

finding 片段：`run_deployment = arun_deployment`

## P0109

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試中 preamble marker 的型別名稱斷言錯誤

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，實際渲染的元件型別是 `GenericComponent<int>`，但斷言卻使用了 `typeof(GenericComponent<string>).Assembly.GetName().Name` 和 `typeof(GenericComponent<string>).FullName`。這會導致測試失敗，因為 `GenericComponent<string>` 的 full name 與 `GenericComponent<int>` 不同。建議改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0110

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:75`，距錨點 17 行）Popover 內容無法透過鍵盤操作

> PopoverTrigger 使用 Button 元件，但未提供 onKeyDown 或 focus 管理，鍵盤使用者無法開啟或瀏覽 popover 內容。建議加入適當的鍵盤事件處理（例如 Enter/Space 開啟、Escape 關閉），並確保焦點能移至 popover 內。

finding 片段：`<PopoverTrigger asChild> ⏎ <Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0"`

## P0111

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:46`，距錨點 6 行）變數不存在時僅記錄警告，可能隱藏錯誤

> 當 `variable_pool.get(selector)` 回傳非 `Variable` 時，僅記錄警告並繼續。若預期該變數一定存在，此情況可能代表上游邏輯錯誤，建議考慮拋出例外或提高日誌等級。

finding 片段：`if not isinstance(variable, Variable): ⏎ logger.warning( ⏎ "Conversation variable not found in variable pool. selector=%s", ⏎ selector,`

## P0112

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行）移除 getOutputRecurringSeatedBookings 的排序可能導致回傳順序不穩定

> 原本 `getOutputRecurringSeatedBookings` 會依 `start` 時間排序回傳的 bookings，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的 recurring bookings 順序不固定，影響前端顯示或測試的穩定性。

**失敗情境**：若資料庫回傳的 bookings 順序未依時間排序，前端可能顯示錯誤的順序，或依賴順序的測試（如 e2e）會 flaky。

**建議**：除非有明確理由，否則應保留排序邏輯，或確認呼叫端已自行排序。

finding 片段：`return transformed;`

## P0113

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103`，距錨點 0 行）輪詢邏輯可能造成重複請求與狀態不一致

> 在 `useEffect` 中，當 `account?.blueskyEnabled` 為 true 且 `account?.blueskyHandleConfirmed` 為 false 時，會設定一個 interval 每 5 秒呼叫 `confirmHandle`。但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`，若前一次請求尚未完成，下一次 interval 又會觸發，可能造成多個並行請求。此外，`retryCountRef` 在 interval 內遞增，但若請求失敗（例如網路錯誤），`confirmHandle` 的 promise 會被 reject，但 interval 仍會繼續，可能導致錯誤未被處理且重試次數計算不正確。建議在 `confirmHandle` 中加入防護，例如檢查 mutation 是否正在進行，或使用 `isPending` 狀態來避免重複請求。

finding 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ `

## P0114

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行）scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作

> 原本 `scheduling.init()` 會傳入 `apiUrl` 參數，用於建構排程服務所需的 API URL。移除後，排程服務可能無法正確取得 API 位址，導致排程任務失敗或無法觸發。建議確認 `scheduling.init()` 是否已改為從其他來源取得 API URL，或此參數是否已不再需要。

finding 片段：`scheduling.init(),`

## P0115

**GT**（func）Incorrect deployment filtering breaks full-name matching

> The deployment filtering logic checks `dep.name not in deployment_names` instead of checking `full_name not in deployment_names`. This causes the filter to incorrectly evaluate when users specify deployment names in 'flow-name/deployment-name' format. When a user provides a full deployment name like 'my-flow/production', the code checks if 'production' (the short name) is in the list containing 'my-flow/production', which fails, causing the deployment to enter the fallback matching logic unnecessarily. This breaks the fast-path check and could lead to incorrect filtering behavior where deployments are included or excluded inappropriately.

GT 片段：`# If filtering by deployment name, check the full name matches ⏎ full_name = f"{flow_name}/{dep.name}" ⏎ if deployment_names and dep.name not in deployment_names: ⏎ # Only include if the full name matches (filter was by name parts)`

**finding**（`src/prefect/_sdk/fetcher.py:397`，距錨點 0 行）部署名稱過濾邏輯變更可能改變行為

> 原本的過濾條件是 `full_name not in deployment_names`，現在改為 `dep.name not in deployment_names`。這可能導致當使用者指定完整名稱（如 `flow-name/deployment-name`）時，過濾邏輯無法正確匹配，因為 `dep.name` 只包含部署名稱，不包含 flow 名稱。需確認此變更是否符合預期，並考慮是否應同時檢查 `full_name` 和 `dep.name`。

finding 片段：`if deployment_names and dep.name not in deployment_names:`

## P0116

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判

> 在 Linux 上，檔案路徑是區分大小寫的。使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能將不同目錄視為相同（例如 `/Certs` 與 `/certs`），導致錯誤地認為憑證目錄已存在於 SSL_CERT_DIR 中，進而跳過必要的設定。建議在 Unix 平台上使用 `StringComparison.Ordinal`，或根據作業系統動態選擇比較方式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0117

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert smtp is not None 可能被最佳化移除

> 新增的 `assert smtp is not None` 在 Python 最佳化模式（-O）下會被移除，且此處 smtp 必定不為 None，因為建構子已指派。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0118

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38`，距錨點 3 行）未處理團隊不存在或無權限的例外

> `TeamService.createInvite` 在團隊不存在時會拋出 `ErrorWithCode(ErrorCode.NotFound)`，但控制器未捕獲此例外，可能導致 500 錯誤而非 404。建議加入例外處理或使用全域例外過濾器，確保回傳適當的 HTTP 狀態碼。

finding 片段：`const result = await TeamService.createInvite(teamId);`

## P0119

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:43`，距錨點 0 行）selector 長度檢查可能不足

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 `selector[0]` 是否為 `CONVERSATION_VARIABLE_NODE_ID`。若 selector 長度大於等於 2 但第一個元素不是 conversation variable node id，後續 `variable_pool.get(selector)` 可能回傳非 conversation variable，但程式碼仍會嘗試更新。建議增加明確檢查。

finding 片段：`if selector[0] != CONVERSATION_VARIABLE_NODE_ID: ⏎ continue`

## P0120

**GT**（func）Test constructs invalid path with double slashes

> The test constructs `already_prefixed_path = f"{bucket_folder}/abc123"` but bucket_folder always ends with a trailing slash (enforced by the _bucket_folder_suffix validator). This creates paths like 'results//abc123' with double slashes. While the double-nesting prevention logic should handle this, the test no longer accurately simulates the actual scenario described in issue #20174 where paths are already correctly prefixed without double slashes. This makes the test less effective at catching regressions in the double-nesting prevention logic.

GT 片段：`# Simulate path that already has bucket_folder prefix ⏎ # (as would happen when create_result_record calls _resolve_path) ⏎ already_prefixed_path = f"{bucket_folder}/abc123" ⏎ # When write_path calls _resolve_path again, it should NOT double-nest`

**finding**（`src/integrations/prefect-gcp/tests/test_cloud_storage.py:153`，距錨點 3 行）測試未涵蓋 bucket_folder 為空字串的情況

> 測試 `test_resolve_path_no_double_nesting` 在 `bucket_folder` 為空時直接 skip，但未驗證空字串時的行為。雖然現有測試可能已涵蓋，但此回歸測試應確保在無 bucket_folder 時不會誤觸發前綴檢查。

finding 片段：`if not bucket_folder: ⏎ pytest.skip("Test only applies when bucket_folder is set")`

## P0121

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 22 行）dev 模式下 versionCode 的 clamp 順序可能導致非預期結果

> 在 dev 模式下，程式先檢查 `version_code == 0` 和 `> 2100000000` 並回傳錯誤，然後才執行 `clamp(1, 2100000000)`。這表示如果 semver 計算出的 `version_code` 超過上限，dev 模式會直接失敗，而不是被 clamp 到上限。原本在 `tauri-build` 中的邏輯是先 clamp 再檢查，行為可能不一致。建議確認預期行為，並調整順序或移除重複檢查。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## P0122

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:584`，距錨點 0 行）hasPendingInviteByUserId 查詢條件錯誤，永遠回傳 false

> 此方法用於檢查使用者是否有 pending invite，但查詢條件為 `accepted: true`，這會找出已接受的 membership，而非未接受的邀請。因此，當使用者有 pending invite 時，此方法會回傳 `false`，導致 PR 的主要功能（重新導向）完全失效。

**失敗情境**：使用者透過邀請連結註冊，系統建立了 `accepted: false` 的 membership。當使用者進入 `/onboarding/getting-started` 頁面時，`hasPendingInviteByUserId` 回傳 `false`，因此不會重新導向到 `/onboarding/personal/settings`，使用者會停留在錯誤的頁面。

**建議修法**：將查詢條件改為 `accepted: false`。

finding 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

## P0123

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行）bookingUrl 解析邏輯可能產生錯誤的前綴

> 在解析 bookingUrl 以顯示 URL 前綴時，程式碼使用 `new URL(props.bookingUrl)` 並從 pathname 中移除最後一段（slug）。然而，若 bookingUrl 包含 query string 或 hash，`url.pathname` 不會包含這些部分，因此前綴可能不完整。此外，若 bookingUrl 的 pathname 為空或僅有 slug，前綴會變成 `/`，導致顯示不正確。建議改用更穩健的方式，例如直接從 bookingUrl 中移除最後一個路徑段，或使用正規表達式。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug ⏎ let prefix = "/";`

## P0124

**GT**（rule）Cross-field validation uses field validator

> The rule requires cross-field validation to use @model_validator decorator, but the code uses @field_validator which accesses unvalidated fields via info.data, causing order-dependent validation issues

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行）field_validator 可能無法正確取得 triggering_event

> `validate_automation_triggered_event_id` 使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 包含已驗證的欄位，但若 `triggering_event` 在 `automation_triggered_event_id` 之後才被驗證，則可能尚未存在於 `info.data` 中，導致驗證失敗或誤判。

**失敗情境**：若欄位驗證順序導致 `triggering_event` 尚未被處理，則即使 `triggering_event` 實際存在，驗證器也可能拋出錯誤。

**建議修法**：改用 `info.data.get("triggering_event")` 或使用 `model_fields_set` 來檢查欄位是否已設定。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## P0125

**GT**（func）Browser navigation uses Forward() instead of Back() breaking test flow

> In the RedirectEnhancedGetToInternal test, after clicking a link that redirects from /redirect to /scroll-to-hash, the test attempts to verify that browser back navigation works correctly. However, the code calls Browser.Navigate().Forward() instead of Browser.Navigate().Back(). Since there is no forward history (the browser just navigated forward to the current page), Forward() does nothing and the browser remains at /scroll-to-hash. The subsequent assertions expect the browser to be back at /redirect with the "Redirections" heading, but it's still at the redirected page, causing the test to fail. The comment explicitly states "See that 'back' takes you to the place from before the redirection" but the code does the opposite action.

GT 片段：`// See that 'back' takes you to the place from before the redirection ⏎ Browser.Navigate().Forward(); ⏎ Browser.Equal("Redirections", () => _originalH1Element.Text); ⏎ Assert.EndsWith("/subdir/redirect", Browser.Url);`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:113`，距錨點 0 行）將 Back 改為 Forward 可能導致測試驗證錯誤的頁面

> 在測試 `RedirectEnhancedGetToInternal` 中，原本使用 `Browser.Navigate().Back()` 來驗證返回上一頁，但此變更改為 `Forward()`。這可能導致測試驗證錯誤的頁面，因為 Forward 通常用於前進到下一頁，而非返回。若意圖是驗證返回行為，應保留 Back；若意圖是驗證前進行為，則需確認測試名稱與斷言是否相符。

finding 片段：`Browser.Navigate().Forward();`

## P0126

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行）SMTP 類別選擇邏輯可能改變非 TLS 與 TLS 模式的行為

> 原本程式碼根據 use_tls 和 opportunistic_tls 明確選擇 SMTP 或 SMTP_SSL，並在 opportunistic TLS 時先建立 SMTP 再呼叫 starttls。新程式碼使用三元運算子選擇類別，但條件 `(self.use_tls and not self.opportunistic_tls)` 在 use_tls=False 時會選擇 SMTP（正確），但在 use_tls=True 且 opportunistic_tls=True 時也會選擇 SMTP（正確），然而在 use_tls=True 且 opportunistic_tls=False 時選擇 SMTP_SSL（正確）。看似等價，但需注意原本在非 TLS 模式下（use_tls=False）直接建立 SMTP，新程式碼也相同。然而，原本在 opportunistic TLS 模式下，先建立 SMTP 後呼叫 ehlo(self.server)，新程式碼改為 ehlo(local_host)，其中 local_host 可能為空字串，這可能導致 HELO 命令使用空字串而非伺服器位址，違反 SMTP 規範。建議確認 local_host 為空時應回退為 self.server。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0127

**GT**（rule）Line length exceeds SwiftLint limit

> This added/modified line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextStudies = NSLocalizedString("Settings.detailTextStudies", value: "%@ may install and run studies from time to time.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focus\" or \"Firefox Klar\").")`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:202`，距錨點 3 行）comment 中的引號變更可能影響翻譯工具

> `detailTextSendUsageData` 和 `detailTextStudies` 的 comment 從智慧引號（“ ”）改為直引號（" "）。這可能導致翻譯工具將這些 comment 視為不同，造成翻譯記憶庫不一致。建議確認此變更是否必要，並保持 comment 風格一致。

finding 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

## P0128

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行）未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗

> `XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0129

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行）使用 String(format:) 搭配本地化字串可能導致崩潰

> `SettingsTextFormatter` 中的 `formatStudiesText` 和 `formatRolloutsText` 使用 `String(format: strings.detailTextStudies, appName)`。`detailTextStudies` 和 `detailTextRollouts` 是本地化字串，其內容可能包含額外的格式說明符（例如翻譯後的字串可能包含 `%d` 或 `%2$@`），這會導致 `String(format:)` 在執行時期因參數數量不符而崩潰，或顯示錯誤的內容。建議改用 `String.localizedStringWithFormat` 或避免使用格式字串，直接使用字串插值或替換。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ } ⏎ `

## P0130

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）檔案寫入前設定權限可能導致失敗

> 在 `write_and_make_executable` 中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會回傳錯誤，導致函式失敗。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0131

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 2 行）hasInitializedJsComponents 旗標可能導致初始化遺漏

> `hasInitializedJsComponents` 為全域布林值，一旦設為 true 後，即使後續呼叫傳入不同的 `jsComponentInitializers` 或 `jsComponentParameters`，也不會重新執行初始化。若不同 renderer 需要不同的初始化集合，此旗標會阻止必要的初始化。

建議：考慮以 rendererId 或初始化內容的 hash 作為鍵來判斷是否需要重新初始化，或明確記錄此限制。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## P0132

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:184`，距錨點 30 行）錄製端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能造成授權不足

> `getBookingRecordings` 端點的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。讀取錄製通常只需要讀取權限，改為寫入權限可能導致僅有讀取權限的 API 金鑰或使用者無法存取錄製，造成不必要的授權失敗。

**失敗情境**：具有 `BOOKING_READ` 權限但無 `BOOKING_WRITE` 權限的 API 金鑰呼叫此端點時，會收到 403 Forbidden，即使該使用者有權讀取錄製。

**建議**：確認此變更是否為刻意設計。若錄製讀取不應要求寫入權限，請改回 `BOOKING_READ`。

finding 片段：`@Permissions([BOOKING_WRITE])`

## P0133

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）批次輸入驗證在 max_length 未定義時可能失效

> 在 `checkBatchInputs` 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 來取得長度上限，現在改為直接使用 `varItem.max_length`。如果後端未提供 `max_length`（例如舊資料或未設定），則 `varItem.max_length` 為 `undefined`，比較 `item[varIndex].length > undefined` 會得到 `false`，導致超長輸入不會被擋下。

**失敗情境**：使用者上傳的 CSV 中某欄位超過後端允許的長度，但該變數的 `max_length` 未定義，驗證會通過，可能造成後續 API 錯誤或資料截斷。

**建議**：確認後端一定提供 `max_length`，或在此處加入 fallback（例如 `varItem.max_length ?? DEFAULT_VALUE_MAX_LEN`，但需保留常數）。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0134

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateToolbarLayout 中 stacks 陣列重複加入 browserActionStack，遺漏 trailingPageActionStack

> 在 `updateToolbarLayout` 方法中，`stacks` 陣列的組成包含了 `browserActionStack` 兩次，而沒有包含 `trailingPageActionStack`。這會導致在動畫期間，`trailingPageActionStack` 中的按鈕 alpha 不會被設定為 1.0，可能造成按鈕在動畫後仍然隱形。

**失敗情境**：當使用者滾動頁面導致工具列動畫觸發時，位於地址欄右側的頁面操作按鈕（例如分享、書籤）可能不會顯示，因為它們的 alpha 未被更新。

**建議修法**：將第二個 `browserActionStack` 改為 `trailingPageActionStack`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0135

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）讀取 tauri.properties 失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0136

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）argv 陣列大小不足，寫入 argv[5] 導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但後續指派 `argv[5] = c->argv[2];`，索引 5 超出陣列範圍（合法索引為 0-4）。這會造成堆疊緩衝區溢位，可能導致程式崩潰或任意程式碼執行。

失敗情境：當欄位有過期時間時，執行 HINCRBYFLOAT 即觸發此寫入。

建議修正：將陣列大小改為 6，例如 `robj *argv[6];`。

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0137

**GT**（func）Test uses list equality instead of tuple conversion for event selector

> The test compares event.selector (which is a Sequence[str]) with a list literal using ==. While this might work in some cases due to Python's sequence equality, it's fragile and inconsistent with the pattern used elsewhere in the codebase. The original code correctly converted to tuple for comparison (tuple(event.selector) == ('conversation', 'conv_var')). This change breaks the filtering logic and will likely cause the test to fail to properly identify conversation variable chunk events, leading to false test failures.

GT 片段：`conv_var_chunk_events = [ ⏎ event ⏎ for event in events ⏎ if isinstance(event, NodeRunStreamChunkEvent) and event.selector == ["conversation", "conv_var"]`

**finding**（`api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75`，距錨點 4 行）測試假設所有 conversation variable chunk events 的值都等於 input_query，可能過於嚴格

> 測試中斷言所有 `conv_var_chunk_events` 的 `chunk` 都等於 `input_query`。但若串流過程中有多個 chunk（例如分段傳輸），此斷言可能失敗。建議改為檢查最後一個 chunk 或累積結果。

finding 片段：`assert all(event.chunk == input_query for event in conv_var_chunk_events), ( ⏎ "Expected streamed conversation variable value to match the input query" ⏎ )`

## P0138

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 24 行）dev 模式下 versionCode 的 clamp 順序可能導致非預期結果

> 在 dev 模式下，程式先檢查 `version_code == 0` 和 `> 2100000000` 並回傳錯誤，然後才執行 `clamp(1, 2100000000)`。這表示如果 semver 計算出的 `version_code` 超過上限，dev 模式會直接失敗，而不是被 clamp 到上限。原本在 `tauri-build` 中的邏輯是先 clamp 再檢查，行為可能不一致。建議確認預期行為，並調整順序或移除重複檢查。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## P0139

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）批次輸入驗證在 max_length 未定義時可能失效

> 在 `checkBatchInputs` 中，原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 來取得長度上限，現在改為直接使用 `varItem.max_length`。如果後端未提供 `max_length`（例如舊資料或未設定），則 `varItem.max_length` 為 `undefined`，比較 `item[varIndex].length > undefined` 會得到 `false`，導致超長輸入不會被擋下。

**失敗情境**：使用者上傳的 CSV 中某欄位超過後端允許的長度，但該變數的 `max_length` 未定義，驗證會通過，可能造成後續 API 錯誤或資料截斷。

**建議**：確認後端一定提供 `max_length`，或在此處加入 fallback（例如 `varItem.max_length ?? DEFAULT_VALUE_MAX_LEN`，但需保留常數）。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0140

**GT**（func）Incomplete cache clearing during hot reload causes stale display names

> The ClearCache method only clears _memberInfoCache but fails to clear _displayNameCache (line 85). During hot reload scenarios when metadata updates occur, the HotReloadManager triggers ClearCache to ensure fresh metadata is loaded. However, with _displayNameCache not being cleared, the component will continue to display stale display names from cached MemberInfo objects even after the attributes have been modified in code. This breaks the hot reload functionality for DisplayAttribute and DisplayNameAttribute changes, requiring developers to restart the application to see attribute changes take effect.

GT 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 0 行）Hot Reload 時未清除 _displayNameCache，可能導致顯示名稱過期

> `ClearCache` 方法只清除了 `_memberInfoCache`，但 `_displayNameCache` 未被清除。當 Hot Reload 套用中繼資料變更（例如修改屬性的 `DisplayAttribute`）時，`_displayNameCache` 中快取的舊顯示名稱將繼續被使用，導致 UI 顯示過期的名稱。

**失敗情境**：開發者在 Hot Reload 期間修改了某個屬性的 `DisplayAttribute.Name`，但頁面仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0141

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:34`，距錨點 18 行）conversation_id 取得方式與既有邏輯不同，可能導致行為差異

> 此處使用 `self.graph_runtime_state.system_variable.conversation_id`，而舊邏輯是從 variable pool 取得 `["sys", "conversation_id"]`。若 system_variable 的 conversation_id 與 variable pool 中的不一致，可能造成更新到錯誤的 conversation。需確認兩者來源是否一致。

finding 片段：`conversation_id = self.graph_runtime_state.system_variable.conversation_id`

## P0142

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27`，距錨點 0 行）使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中被跳過

> 在 `testRequestAuthorization` 中，原本的 `XCTAssertTrue` 被改為 `assert`。`assert` 在 release 建置中會被編譯器移除，導致測試失去驗證功能。建議改回 `XCTAssertTrue` 或使用 `XCTAssert`。

finding 片段：`assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

## P0143

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:253`，距錨點 0 行）reload_config 直接覆寫整個 ConfigMetadata 可能遺失未重新載入的欄位

> `reload_config` 現在直接以 `*config = load_config(...)` 覆寫整個結構。若 `load_config` 在解析過程中因某些原因未能完整填入所有欄位（例如新增的欄位在舊版設定檔中不存在），可能導致原本存在於 `config` 中的值被清除。建議確認 `load_config` 是否保證完整重建所有欄位，或改為僅更新必要的部分。

finding 片段：`*config = load_config(merge_configs, true, target, tauri_dir)?;`

## P0144

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:202`，距錨點 5 行）comment 中的引號變更可能影響翻譯工具

> `detailTextSendUsageData` 和 `detailTextStudies` 的 comment 從智慧引號（“ ”）改為直引號（" "）。這可能導致翻譯工具將這些 comment 視為不同，造成翻譯記憶庫不一致。建議確認此變更是否必要，並保持 comment 風格一致。

finding 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

## P0145

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）async setUp 中呼叫 @MainActor 方法缺少 await

> `DependencyHelperMock().bootstrapDependencies()` 已標記為 `@MainActor`，但在 async `setUp` 中呼叫時未加上 `await`。這會導致編譯錯誤，因為從非隔離的 async 函式呼叫 main actor 方法必須 await。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0146

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖曳的 prefix 項目，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包括 prefixItems 對應的項目。但這些項目在 `SchemaFormInputArrayItem` 中因 `canMove` 為 false 而停用拖曳（`useSortable` 的 `disabled` 設為 true）。將停用的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過停用項目或碰撞偵測錯誤。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => index >= prefixItemsCount).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0147

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷變更可能導致權限繞過

> 原本的 `isCurrentUser` 判斷為 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示若 `filters.userIds` 包含當前用戶 ID 和其他用戶 ID，則 `isCurrentUser` 為 true，可能導致後續權限檢查放寬，允許存取其他用戶的 bookings。建議確認此變更是否為預期，並增加測試。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0148

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1122`，距錨點 7 行）記憶體洩漏：cross-slot 時未釋放 slot_buffer

> 在偵測到 cross-slot 時，程式碼執行 `free(slot_buffer); return CLUSTER_CROSSSLOT;`，但若 `slot_buffer` 配置成功且迴圈正常結束，最後也有 `free(slot_buffer)`。然而，若在迴圈中發生其他錯誤（例如 `keyHashSlot` 拋出例外？C 語言無例外，但可能有 longjmp），或未來修改程式碼時在迴圈中提前 return，都可能遺漏釋放。目前程式碼看似有釋放，但若 `malloc` 失敗，`slot_buffer` 為 NULL，`free(NULL)` 是安全的，但後續寫入會 crash。

建議：使用 goto 統一清理，或確保所有路徑都釋放記憶體。

finding 片段：`free(slot_buffer); ⏎ return CLUSTER_CROSSSLOT;`

## P0149

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行）Slot.userIds 型別從 number[] 改為 string[]，可能導致執行時期錯誤

> 原本 @calcom/trpc/server/routers/viewer/slots/types 中的 Slot.userIds 型別為 number[]，但此處新定義為 string[]。若實際 API 回傳的 userIds 是數字陣列，則使用此型別的程式碼（例如將 userIds 傳給其他函式）可能因型別不符而發生錯誤。建議確認實際資料型別，並保持與原定義一致。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## P0150

**GT**（func）Inverted reply discard logic causes test infrastructure failure

> The condition for discarding replies is inverted - replies are discarded when count is NOT a multiple of frequency (!=), rather than when it IS a multiple (==). This causes the test to read and discard replies at the wrong times, leading to a buffer overflow of unread replies. The discard_replies_every helper is called throughout the test suite after batches of Redis commands to prevent reply buffer buildup. With this bug, replies accumulate in the buffer instead of being cleared, causing test hangs or failures when the client tries to send new commands with a full reply buffer.

GT 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

**finding**（`tests/unit/memefficiency.tcl:70`，距錨點 0 行）測試輔助函式 discard_replies_every 的參數名稱可能造成混淆

> 新函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 在呼叫時傳入的值相同（例如 10000），但語意不同：`frequency` 是觸發間隔，`discard_num` 是每次丟棄的回覆數。雖然目前呼叫都一致，但未來可能誤用。建議在函式內加入註解或改用更明確的參數名稱。

finding 片段：`proc discard_replies_every {rd count frequency discard_num} {`

## P0151

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行）`expect` 取代 fallback 可能導致 panic

> 原本的程式碼在 `name` 為 `None` 時會 fallback 到 `association.ext[0].0`，但現在改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空（或 `ext` 的第一個元素不存在），程式會 panic。這會讓建置流程直接崩潰，且錯誤訊息不夠明確。

建議：保留原本的 fallback 邏輯，或改用更安全的處理方式，例如在 `ext` 為空時使用預設名稱或回傳錯誤。

finding 片段：`.expect("File association must have a name")`

## P0152

**GT**（func）Inconsistent format specifier documentation in RolloutsSettingMessage comment

> The comment for RolloutsSettingMessage incorrectly documents the format specifier as '%1$@' (positional format) while the actual value string uses '%@' (simple format). This mismatch creates confusion for localization teams and could lead to incorrect translations, as translators may attempt to use positional formatting based on the comment when the string implementation doesn't support it. The comment should match the actual format specifier used in the value field.

GT 片段：`public static let RolloutsSettingMessage = MZLocalizedString( ⏎ key: "Settings.Rollouts.Message.v148", ⏎ tableName: "Settings", ⏎ value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.",`

**finding**（`firefox-ios/Shared/Strings.swift:6260`，距錨點 0 行）格式字串不一致：%@ 與 %1$@ 混用

> 在 `RolloutsSettingMessage` 中使用了 `%@`，但註解寫的是 `%1$@`。在 iOS 的本地化字串中，若使用位置參數（如 `%1$@`），則所有格式符都應使用位置參數，否則可能導致參數錯位或無法正確替換。建議統一使用 `%@` 或 `%1$@`，並更新註解。

finding 片段：`value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", ⏎ comment: "A short description that explains that Mozilla may change features remotely. %1$@ is the app name (e.g. Firefox)."`

## P0153

**GT**（func）Missing router import causes undefined variable error in BookerWebWrapper

> The `useRouter` hook is removed from the imports but the `router` variable is still used in multiple places within the component (lines 193, 228, 233, 239). This will cause a ReferenceError at runtime when any of these code paths are executed, such as when toggling the overlay calendar, navigating for instant meetings, or handling calendar interactions. The router is critical for navigation functionality in the booking flow.

GT 片段：`import { useSession } from "next-auth/react"; ⏎ import { useSearchParams, usePathname } from "next/navigation"; ⏎ import { useMemo, useCallback, useEffect } from "react"; ⏎ import React from "react";`

**finding**（`apps/web/modules/bookings/components/BookerWebWrapper.tsx:4`，距錨點 0 行）移除 useRouter import 但程式碼仍使用 router

> 在 diff 中，原本的 `import { useSearchParams, usePathname, useRouter } from "next/navigation";` 被改為 `import { useSearchParams, usePathname } from "next/navigation";`，且原本的 `const router = useRouter();` 也被移除。然而，在後續的程式碼中仍有多處使用 `router`，例如 `router.push(...)`、`router.push("/apps/categories/calendar")` 等。這會導致執行時出現 `ReferenceError: router is not defined`。

建議：保留 `useRouter` 的 import 與宣告，或改用其他方式取得 router。

finding 片段：`import { useSearchParams, usePathname } from "next/navigation";`

## P0154

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 9 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0155

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 未驗證 schedule 結構，可能接受無效資料

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 是否為符合預期的陣列結構。若呼叫端傳入錯誤格式的 schedule，可能導致後續 API 請求失敗或產生未預期的行為。建議加入對 schedule 的型別檢查，例如確認其為二維陣列且元素包含 start 和 end。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0156

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行）CFBundleTypeExtensions 條件判斷邏輯相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，這與預期相反。當副檔名清單為空時，不應插入該鍵；反之，當有副檔名時才應插入。目前的行為會導致所有有副檔名的關聯都不會寫入 `CFBundleTypeExtensions`，使得 macOS 無法正確建立檔案關聯。

建議改為 `if !association.ext.is_empty() { ... }`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0157

**GT**（func）Incorrect Reader Mode URL handling in cancelEditMode

> The cancelEditMode function now incorrectly preserves reader mode URLs when canceling edit mode. The logic was changed from '&&' (AND) to '||' (OR), which means reader mode URLs will now be kept instead of being cleared. This breaks the expected behavior where reader mode URLs should be filtered out when canceling URL editing, potentially causing the address bar to display internal reader:// URLs to users instead of the original webpage URL.

GT 片段：`@MainActor ⏎ private func cancelEditMode(windowUUID: WindowUUID) { ⏎ var url = tabManager(for: windowUUID).selectedTab?.url ⏎ if let currentURL = url {`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 39 行）readerModeState 的 isEnabled 判斷反轉可能導致錯誤的遙測事件

> 原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會讓 `readerModeButtonTapped` 的 `isEnabled` 參數傳入相反的值，導致遙測數據錯誤。例如，當 Reader Mode 可用時，原本應記錄為 enabled，現在卻記錄為 disabled。請確認此變更是否為預期行為，若非必要請回復。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## P0158

**GT**（func）Missing error logging in TanStack devtools lazy import

> The TanStackDevtoolsLoader silently swallows import errors without logging them, making it impossible to debug why the devtools fail to load. This creates an inconsistent error handling pattern compared to the ReactScanLoader (in the same PR), which properly logs errors with console.error before returning a fallback component. When developers encounter issues with TanStack devtools not appearing, they will have no visibility into whether it's due to an import failure, missing dependencies, or other issues.

GT 片段：`const TanStackDevtoolsWrapper = lazy(() => ⏎ import('./devtools').then(module => ({ ⏎ default: module.TanStackDevtoolsWrapper, ⏎ })).catch(() => {`

**finding**（`web/app/components/devtools/tanstack/loader.tsx:10`，距錨點 0 行）TanStack devtools 載入失敗時完全靜默

> catch 區塊直接回傳 `{ default: () => null }`，沒有任何錯誤記錄。這使得開發者無法得知 devtools 載入失敗，可能導致問題難以診斷。建議至少加入 `console.error` 或類似的日誌。

finding 片段：`return { default: () => null }`

## P0159

**GT**（func）Test completes without waiting for async image download

> The test was converted from async to synchronous but the expectation and wait statement were removed. This causes the test to complete immediately without waiting for the asynchronous image download callback to execute. The XCTAssert statements inside the completion handler will never be verified, resulting in false positive test passes even if the image download fails or produces incorrect results. This is a critical testing bug that undermines test reliability.

GT 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ guard let imageData = try? dataFor(type: assetType) else {`

**finding**（`BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12`，距錨點 0 行）測試從 async 改為同步可能導致執行緒阻塞或逾時

> 原本使用 `await fulfillment(of:timeout:)` 等待非同步 callback，現在改為同步的 `wait(for:timeout:)`。若 callback 在背景執行緒執行，`wait(for:timeout:)` 會阻塞主執行緒，可能導致測試逾時或死鎖。建議保留 async 版本，或確認 callback 執行緒與測試執行緒的關係。

finding 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() {`

## P0160

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。如果使用者未在設定中提供 `name` 且 `ext` 為空，程式會 panic。雖然 schema 可能要求 `name` 或 `ext` 至少一個存在，但此處的變更增加了執行時錯誤的風險。建議保留原本的 fallback 邏輯，或改為更安全的處理方式。

finding 片段：`.expect("File association must have a name")`

## P0161

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:25`，距錨點 0 行）SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性

> SMTPClient 在建構時直接從全域 dify_config 讀取 SMTP_LOCAL_HOSTNAME，這使得 SMTPClient 與全域設定耦合，難以在測試中隔離或在不同設定下重用。建議將 local_hostname 作為建構子參數傳入，由呼叫端負責提供設定值。

finding 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

## P0162

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）殘留的 console.log 可能洩漏敏感資訊

> 新增的 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })` 會將批次輸入的資料輸出到主控台，可能包含使用者提供的敏感內容。建議移除或改用適當的日誌機制。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0163

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:101`，距錨點 0 行）`findPage` 回傳值可能未定義 `data` 屬性，導致執行時期錯誤

> `#getHighestCount` 改為呼叫 `findPage` 後，直接存取 `result.data.length`。若 `findPage` 的實作在某些情況下（例如資料庫錯誤、回傳格式不符）未提供 `data` 陣列，將拋出 `TypeError`。建議先檢查 `result` 與 `result.data` 是否存在，或使用選用鏈結（`result?.data?.length`）並提供預設值。

finding 片段：`const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC', ⏎ limit: 1`

## P0164

**GT**（func）JSON schema validation uses non-normalized value

> The validation logic for jsonObject type validates jsonSchemaValue instead of normalizedJsonSchema. This is problematic because normalizedJsonSchema is computed earlier and correctly handles the case where an empty schema should be undefined. By validating jsonSchemaValue directly, the code validates the raw tempPayload value instead of the cleaned version. This inconsistency means that validation may pass but the wrong data could be saved, or validation may fail when it should succeed if the schema is empty but not yet normalized.

GT 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue) ⏎ if (schema?.type !== 'object') {`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:311`，距錨點 0 行）`jsonSchemaValue` 可能不是字串，導致 JSON.parse 收到非字串

> 在 `handleConfirm` 中，`jsonSchemaValue` 的型別是 `InputVar['json_schema']`，可能是 `string | undefined`。程式碼先檢查 `!isSchemaEmpty && typeof jsonSchemaValue === 'string'`，但 `isSchemaEmpty` 的實作中，若 `value` 不是 null/undefined 且不是字串，會回傳 `false`。因此，若 `jsonSchemaValue` 是其他型別（例如數字或物件），`isSchemaEmpty` 會回傳 `false`，但 `typeof jsonSchemaValue === 'string'` 會是 `false`，所以不會進入 JSON.parse 的區塊，而是直接呼叫 `onConfirm`。這可能導致非字串的 schema 被儲存，與預期不符。建議在 `isJsonSchemaEmpty` 中明確處理非字串型別，或在此處增加型別檢查。

finding 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue)`

## P0165

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2571`，距錨點 11 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，但此處傳入的參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。根據 HSETEX 語法，正確順序應為 `HSETEX key [KEEPTTL] FIELDS num field value`，因此 `shared.keepttl` 應在 `shared.fields` 之前，但此處 `shared.keepttl` 在 `shared.fields` 之後，可能導致複寫指令格式錯誤。

失敗情境：當主節點執行 HINCRBYFLOAT 時，複本會收到錯誤格式的 HSETEX 指令，導致複寫中斷或資料不一致。

建議修正：調整參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0166

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行）回傳的 token 與實際建立的 verificationToken 不一致

> `createInvite` 原本回傳 `token`（隨機產生的 token），現在改為回傳 `newToken.identifier`。但 `identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的 token。這會導致 API 回傳的 token 無法用於驗證邀請，且與 `inviteLink` 中的 token 不一致。

失敗情境：使用者取得邀請連結後，使用連結中的 token 進行驗證，但資料庫中的 verificationToken 的 token 欄位是隨機產生的 token，而 identifier 是固定格式，因此驗證會失敗。

建議：回傳 `token` 而非 `newToken.identifier`。

finding 片段：`token: newToken.identifier,`

## P0167

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行）Session 未關閉，可能導致連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但沒有呼叫 `close()` 或使用 context manager。每次呼叫都會建立新的 session，若未正確關閉，可能耗盡資料庫連線池。建議使用 `with Session(db.engine) as session:` 或確保在 finally 中關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0168

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:132`，距錨點 5 行）semaphore 未初始化時拋出 RuntimeError 可能中斷事件處理

> 在 `_replicate_pod_event` 中，若 `_startup_event_semaphore` 為 `None`，會拋出 `RuntimeError`。這可能發生在 `initialize_clients` 尚未執行或執行失敗時，導致事件處理中斷。建議考慮更優雅的處理方式，例如記錄警告並跳過 semaphore 限制。

finding 片段：`if _startup_event_semaphore is None: ⏎ raise RuntimeError("Startup event semaphore not initialized")`

## P0169

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:202`，距錨點 0 行）fail() 方法中 triggered 事件的 related 參數誤用

> 在 `fail()` 方法中，`prefect.automation.action.triggered` 事件的 `related` 參數被設定為 `self._resulting_related_resources`，而非建構好的 `related_resources`。這會導致該事件缺少 `triggering-event` 和 `automation-triggered-event` 關聯，破壞事件追蹤功能。

**失敗情境**：當 action 失敗時，產生的 `action.triggered` 事件將不包含任何相關資源，使用者無法從該事件追溯到觸發事件或 automation 狀態變更事件。

**建議修法**：將該行改為 `related=related_resources`。

finding 片段：`related=self._resulting_related_resources,`

## P0170

**GT**（rule）New/modified path resolution introduces panics/unwraps for fallible operations

> `resolve_dirs` uses `panic!` and `unwrap()` (`tauri.parent().unwrap()`) for fallible operations (project discovery/path parent resolution) instead of returning a `Result`, violating the rule to make failure explicit rather than panicking.

GT 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| { ⏎ let env_var_name = env_tauri_app_path().is_some().then(|| format!("`{ENV_TAURI_APP_PATH}`")); ⏎ panic!("Couldn't recognize the {} folder as a Tauri project. It must contain a `{}`, `{}` o`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:131`，距錨點 0 行）resolve_dirs 使用 get_or_init 可能導致 panic 訊息不一致

> `TAURI_DIR.get_or_init` 的初始化閉包中，若 `resolve_tauri_dir()` 回傳 `None`，會 panic。但 `FRONTEND_DIR.get_or_init` 的閉包中，若 `resolve_frontend_dir()` 回傳 `None`，會使用 `tauri.parent().unwrap()`，若 `tauri` 沒有 parent 也會 panic。這些 panic 訊息可能不如原本的 `expect` 明確，且 `get_or_init` 在初始化失敗時不會重試，可能導致後續呼叫永遠 panic。

finding 片段：`let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| { ⏎ let env_var_name = env_tauri_app_path().is_some().then(|| format!("`{ENV_TAURI_APP_PATH}`")); ⏎ panic!("Couldn't recognize the {} folder as a Tauri project. It must contain a `{}`, `{}` or `{}` file in any subfolder.", ⏎ `

## P0171

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行）buildInviteLink 條件判斷反轉

> 原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，代表非組織情境使用團隊邀請連結；修改後變成 `if (isOrgContext) { return teamInviteLink; }`，導致組織情境反而回傳團隊邀請連結，非組織情境則回傳組織邀請連結。這會讓邀請連結的格式錯誤，使用者可能被導向錯誤的頁面。

建議將條件改回 `if (!isOrgContext)`，或根據實際需求調整。

finding 片段：`if (isOrgContext) { ⏎ return teamInviteLink; ⏎ }`

## P0172

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1371`，距錨點 38 行）module 類型的記憶體計算可能重複計算 header

> 在 module 類型的記憶體計算中，原本直接使用 `moduleGetMemUsage` 的回傳值，現在改為 `asize += moduleGetMemUsage(...)`。但 `asize` 已經包含了 `malloc_usable_size((void *)o)`，即 kvobj header 的大小。若 `moduleGetMemUsage` 的回傳值也包含 header 的大小，則會重複計算。建議確認 `moduleGetMemUsage` 的實作，並避免重複計算。

finding 片段：`asize += moduleGetMemUsage(key, o, sample_size, dbid);`

## P0173

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行）'not contains' 分支未傳入 escape 參數，跳脫字元失效

> 在 'not contains' 條件中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"`。這會導致 `escaped_value` 中的反斜線被視為一般字元，而非跳脫字元，因此 `%` 和 `_` 仍會被當作萬用字元。例如，若 value 為 "50%"，escaped_value 為 "50\\%"，但由於未指定 escape，資料庫會將 "\\" 視為普通字元，而 "%" 仍為萬用字元，導致查詢結果不符合預期。建議改為 `json_field.notlike(f"%{escaped_value}%", escape="\\")`。

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## P0174

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行）clusterCommonInit 使用 malloc 而非 zmalloc 分配 cluster_slot_stats

> 在 clusterCommonInit 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用了標準 malloc，而非 Redis 慣用的 zmalloc。這會導致記憶體分配未納入 Redis 的記憶體統計，且無法在 OOM 時觸發 Redis 的錯誤處理。建議改用 `zmalloc`。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0175

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 0 行）config 值型別不一致可能導致行為差異

> 在測試中，未設定時使用 `configUtils.set('memberWelcomeEmailTestInbox', '')`（空字串），而單元測試中 stub 回傳 `undefined`。在程式碼中，`welcomeEmailConfig` 若為空字串，`if (welcomeEmailConfig || ...)` 會視為 falsy，因此不會觸發歡迎郵件；但若 config 實際回傳 `undefined`，行為相同。然而，若 config 回傳其他 falsy 值（如 `null`、`0`），行為可能不同。建議統一 config 的預設值，並在程式碼中明確檢查是否為有效字串。

失敗情境：若 config 設定為空字串，且 `WELCOME_EMAIL_SOURCES.includes(source)` 為 false，則不會建立 outbox；但若 config 設定為 `null`，`welcomeEmailConfig` 為 null，`if (null || ...)` 仍會進入，可能造成非預期行為。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0176

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。如果使用者未在設定中提供 `name` 且 `ext` 為空，程式會 panic。雖然 schema 可能要求 `name` 或 `ext` 至少一個存在，但此處的變更增加了執行時錯誤的風險。建議保留原本的 fallback 邏輯，或改為更安全的處理方式。

finding 片段：`.expect("File association must have a name")`

## P0177

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行）移除 strict=True 可能導致 zip 靜默截斷

> 在 `_fetch_work_pools_parallel` 中，原本使用 `zip(pool_names_list, results, strict=True)` 確保兩個序列長度一致。移除 `strict=True` 後，若 `pool_names_list` 和 `results` 長度不同，zip 會靜默截斷到較短的長度，導致部分 work pool 的結果被忽略，且不會有任何錯誤提示。這可能造成 SDK 資料不完整，且難以偵錯。建議保留 `strict=True`，或明確處理長度不一致的情況。

finding 片段：`for name, result in zip(pool_names_list, results):`

## P0178

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:43`，距錨點 9 行）selector 長度檢查可能不足

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 `selector[0]` 是否為 `CONVERSATION_VARIABLE_NODE_ID`。若 selector 長度大於等於 2 但第一個元素不是 conversation variable node id，後續 `variable_pool.get(selector)` 可能回傳非 conversation variable，但程式碼仍會嘗試更新。建議增加明確檢查。

finding 片段：`if selector[0] != CONVERSATION_VARIABLE_NODE_ID: ⏎ continue`

## P0179

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行）當 SMTP_LOCAL_HOSTNAME 為空字串時，local_hostname 傳入 None 可能導致非預期行為

> 程式碼使用 `local_host or None`，若設定為空字串，則傳入 None。smtplib 在建構時若 local_hostname 為 None，會自動使用 socket.getfqdn()，這可能與預期不符（預期不覆寫時應使用預設行為，但 None 可能觸發不同的行為）。建議明確處理空字串，例如僅在設定非空時才傳遞 local_hostname 參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0180

**GT**（func）orgId parameter not propagated in getTeamIdsWithPermission

> The method getTeamIdsWithPermission accepts an orgId parameter to scope permission checks to a specific organization, but it fails to pass this parameter to the underlying getTeamIdsWithPermissions method. This causes organization scoping to be ignored when checking single permissions, allowing users to potentially access teams from all organizations instead of only the specified one. The bug breaks the core security feature introduced in this PR where organization-scoped permission checks were meant to restrict access based on orgId.

GT 片段：`async getTeamIdsWithPermission({ ⏎ userId, ⏎ permission, ⏎ fallbackRoles,`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:205`，距錨點 8 行）Fallback 查詢的 orgId 過濾條件可能排除應包含的團隊

> 在 `getTeamsWithFallbackRoles` 的第一個 SELECT 中，orgId 過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`，同樣只包含組織本身及其直接子團隊。若使用者是組織成員，且目標團隊是更深層級的子團隊，則會被排除。

**失敗情境**：組織 A（id=1）有子團隊 B（parentId=1），B 有子團隊 C（parentId=B.id）。使用者是組織 A 的 ADMIN，查詢 `orgId=1` 時，團隊 C 不會被回傳。

**建議修法**：與 PBAC 查詢相同，需確認業務需求並調整條件以涵蓋所有後代團隊。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0181

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行）listFeaturesForUser 過濾條件寫反，導致回傳全域停用的功能

> 在 `listFeaturesForUser` 方法中，原本應該回傳 `globalEnabled` 為 true 的功能，但程式碼卻寫成 `filter((state) => !state.globalEnabled)`，這會回傳所有全域停用的功能，而使用者將看不到任何已啟用的功能。

**失敗情境**：當使用者呼叫 `listForUser` API 時，會收到一個空陣列（或僅包含停用功能的陣列），導致前端無法顯示任何可設定的功能。

**建議修法**：將條件改為 `filter((state) => state.globalEnabled)`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## P0182

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈條件錯誤導致 heap buffer overflow

> 在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 只配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成 heap buffer overflow。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之外的元素，可能導致越界讀取。

失敗情境：當命令包含至少一個 key 時，迴圈會多執行一次，寫入 `slot_buffer[numkeys]`，可能破壞 heap 中相鄰的資料，甚至導致程式崩潰或被利用。

建議修正：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0183

**GT**（func）orgId parameter not propagated in getTeamIdsWithPermission

> The method getTeamIdsWithPermission accepts an orgId parameter to scope permission checks to a specific organization, but it fails to pass this parameter to the underlying getTeamIdsWithPermissions method. This causes organization scoping to be ignored when checking single permissions, allowing users to potentially access teams from all organizations instead of only the specified one. The bug breaks the core security feature introduced in this PR where organization-scoped permission checks were meant to restrict access based on orgId.

GT 片段：`async getTeamIdsWithPermission({ ⏎ userId, ⏎ permission, ⏎ fallbackRoles,`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:174`，距錨點 39 行）PBAC 查詢的 orgId 過濾條件可能排除應包含的團隊

> 在 `getTeamsWithPBACPermissions` 的第一個 SELECT 中，orgId 過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`。這表示當 `orgId` 指定為某個組織 ID 時，只會回傳該組織本身或其直接子團隊。然而，若使用者是透過組織成員身分取得權限，且目標團隊是組織的孫層級（grandchild），則會被排除。

**失敗情境**：組織 A（id=1）有子團隊 B（parentId=1），B 有子團隊 C（parentId=B.id）。使用者是組織 A 的成員，具有 booking.read 權限，查詢 `orgId=1` 時，團隊 C 不會被回傳，但實際上使用者應有權限存取 C 的 bookings。

**建議修法**：考慮使用遞迴 CTE 或調整條件以包含所有後代團隊，或確認業務需求是否僅限直接子團隊。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0184

**GT**（rule）MSTest attribute in xUnit project

> The rule requires test projects to consistently use the xUnit framework, but the test method uses MSTest's [TestMethod] attribute instead of xUnit's [Fact] attribute

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException()`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:287`，距錨點 0 行）測試被標記為隔離且開關值變更，可能掩蓋問題

> 測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 被加上 `[QuarantinedTest]` 屬性，且 `DisableThrowNavigationException` 開關從 `false` 改為 `true`。這可能表示測試目前不穩定或失敗，但隔離測試會使其在 CI 中跳過，無法驗證修復。建議確認隔離原因，並在修復後移除隔離標記。

finding 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

## P0185

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）讀取失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或解析失敗時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致意外重置版本碼，尤其是在檔案被誤刪或格式錯誤時，造成 Google Play 上傳失敗。

建議：在無法讀取時發出警告或錯誤，或提供明確的 fallback 策略。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0186

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行）quicklist 取樣平均計算可能不準確

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count` 計算平均元素大小，現在改為 `elesize/samples*ql->count`。但 `samples` 是取樣的節點數，而 `elesize` 是這些節點中所有元素的總大小，`elecount` 是這些節點中的元素總數。若每個節點的元素數量不同，使用 `samples` 作為分母會導致平均元素大小計算錯誤。例如，若取樣了 5 個節點，但其中一個節點包含 100 個元素，其他節點各包含 1 個元素，則 `elesize` 會包含 104 個元素的大小，但除以 `samples`（5）會高估平均元素大小。建議改回使用 `elecount` 作為分母，或改為計算每個節點的平均元素大小再乘以節點數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0187

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）條件變更可能導致無鍵命令的 slot 未被正確處理

> 原本的條件是 `else if (num_keys > 0)`，現在改為 `else if (num_keys >= 0)`。這表示當 `num_keys == 0`（無鍵命令）時，也會進入此區塊。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（但無鍵命令不應有此值），則會設定 `read_error` 並將 slot 重設為 `INVALID_CLUSTER_SLOT`。然而，若 `num_keys == 0` 且 `pcmd->slot` 為其他值（例如 `INVALID_CLUSTER_SLOT`），則不會有任何動作，但原本的程式碼也不會進入此區塊。這可能改變了無鍵命令的處理流程，需要確認是否會影響後續邏輯。

失敗情境：若某個無鍵命令的 `pcmd->slot` 被錯誤設定為 `CLUSTER_CROSSSLOT`，現在會被標記為 cross-slot 錯誤，但實際上不應如此。

建議：確認 `num_keys == 0` 時 `pcmd->slot` 的可能值，並考慮是否應維持 `num_keys > 0` 的條件。

finding 片段：`} else if (num_keys >= 0) {`

## P0188

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 20 行）dangerouslySetInnerHTML 可能導致 XSS

> `item.html` 直接透過 `dangerouslySetInnerHTML` 渲染，若評論內容未經適當消毒，攻擊者可注入惡意腳本。建議確認後端已對 HTML 進行消毒，或改用安全的渲染方式（如 DOMPurify）。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0189

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行）重新加入未使用的 Inactive Tabs 字串

> 在 `Strings.swift` 中，原本刪除的 Inactive Tabs 相關字串被重新加入至新的 `v147` 結構中，但程式碼中已無任何使用這些字串的地方。這可能造成混淆，且若未來誤用可能導致功能回歸。

**建議**：確認這些字串是否真的需要保留。若無使用，應一併刪除；若為了向後相容或未來功能，應加上明確註解。

finding 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

## P0190

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0191

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行）bookingUrl 解析邏輯可能產生錯誤的 URL 前綴

> 在 `BasicsTab.tsx` 中，解析 `bookingUrl` 以取得前綴的邏輯會將 URL 的 pathname 最後一段移除，但若 `bookingUrl` 的 pathname 不包含 slug（例如 `https://cal.com/username`），則會錯誤地移除 username，導致前綴變成 `https://cal.com/`。此外，若 `bookingUrl` 包含 query string 或 hash，這些部分不會被包含在前綴中，可能導致顯示不完整。建議改為直接使用 `bookingUrl` 的 origin 加上 pathname 的前段，或由後端提供明確的 prefix 欄位。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ // Get path without the last segment (slug) ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug`

## P0192

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行）複寫指令未包含 TTL 參數，可能無法保留過期時間

> `HSETEX` 指令若未指定 TTL 選項，可能預設為不設定過期時間，導致複本上欄位 TTL 遺失。需確認 `HSETEX` 在僅有 `KEEPTTL` 而無 TTL 選項時的行為。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0193

**GT**（func）Incorrect automation_triggered_event_id for state-specific actions

> When actions_on_trigger or actions_on_resolve are executed, they should be linked to their specific triggered_event.id or resolved_event.id respectively. However, the code incorrectly uses primary_state_change_event_id (which always prefers Triggered over Resolved) for both types of actions. This breaks the tracing chain for actions_on_resolve - they will reference the wrong event ID when only a Resolved state change occurs, making it impossible to correctly trace the action back to the automation.resolved event that actually prompted it.

GT 片段：`# Conditionally add in actions that fire on specific trigger states ⏎ if TriggerState.Triggered in firing.trigger_states: ⏎ triggered_event = state_change_events[TriggerState.Triggered] ⏎ source_actions += [`

**finding**（`src/prefect/server/events/triggers.py:445`，距錨點 13 行）primary_state_change_event 可能為 None 但未處理

> `primary_state_change_event` 可能為 None（當 `state_change_events` 中沒有 Triggered 或 Resolved 狀態時），但後續直接使用 `primary_state_change_event.id`，可能導致 AttributeError。

**失敗情境**：若 `firing.trigger_states` 不包含 Triggered 或 Resolved（例如僅有其他狀態），則 `primary_state_change_event` 為 None，存取 `.id` 會拋出例外。

**建議修法**：在使用前檢查 `primary_state_change_event` 是否為 None，或確保 `state_change_events` 至少包含一個狀態。

finding 片段：`primary_state_change_event_id = ( ⏎ primary_state_change_event.id if primary_state_change_event else None ⏎ )`

## P0194

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 0 行）改用 `jwt.decode` 跳過簽章驗證，可能接受被竄改的 token

> `_isJWTExpired` 原本使用 `jwt.verify` 驗證簽章，現在改用 `jwt.decode` 只解碼不驗證。若攻擊者能取得或猜測 token 結構，可能偽造未過期的 token 來繞過過期檢查。雖然後續使用 token 時 Tinybird 仍會驗證簽章，但此處的過期判斷可能被欺騙，導致服務使用已過期或無效的 token 進行請求。建議改回 `jwt.verify` 或明確說明為何不需要驗證。

finding 片段：`const decoded = jwt.decode(token);`

## P0195

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 23 行）取得 identifier 的欄位從 "identifier" 改為 "bundle"，可能導致行為錯誤

> 原本從 config 物件中取得 "identifier" 欄位，現在改為取得 "bundle" 欄位。但 "bundle" 通常是一個物件，而非字串，因此 `as_str()` 會回傳 `None`，導致 `original_identifier` 永遠為 `None`。這可能影響後續依賴此值的邏輯（例如合併設定或驗證）。請確認此變更是否為預期，若不是，應改回 "identifier"。

finding 片段：`.and_then(|config| config.get("bundle"))`

## P0196

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1125`，距錨點 0 行）使用 var 宣告變數可能導致作用域問題

> 在 multiselect 的 onSelect 中，將 `const newValues` 改為 `var newValues`。雖然在此情境下可能無實際影響，但 var 有函式作用域且可能提升，建議維持 const 以保持一致性與可讀性。

finding 片段：`var newValues = [...effectiveValues, option.value] as T[];`

## P0197

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）cli.js 版本號與 tauri-cli 版本不一致

> 此處將 cli.js 的版本從 2.8.1 改為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 升至 2.8.1。若 cli.js 應與 tauri-cli 版本同步，則此處可能誤升；反之若為刻意，則需確認版本對應關係。

finding 片段：`"version": "2.8.2",`

## P0198

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳未定義的 `True` 可能導致 ReferenceError

> 在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳了 `True`（大寫 T）。在 TypeScript/JavaScript 中，`True` 不是內建的全域變數，除非有自訂的全域宣告，否則執行到此處會拋出 `ReferenceError: True is not defined`。這會中斷函式執行，且由於此函式是事件處理器，錯誤可能不會被明顯捕捉，導致 UI 行為異常。建議改為回傳 `true` 或直接不回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0199

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）未定義的 `True` 會導致 ReferenceError

> 在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳 `True`，但 `True` 並未定義（JavaScript 中布林值為 `true`，非 `True`）。這會導致執行時拋出 `ReferenceError: True is not defined`，使函式無法正常完成。

**失敗情境**：使用者在 JSON Schema 編輯器中輸入合法 JSON 並觸發 onChange，函式會拋出錯誤，可能導致 UI 中斷或狀態未更新。

**建議**：將 `return True` 改為 `return true`。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0200

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行）local_hostname 參數傳遞空字串可能導致 SMTP 連線失敗

> 程式碼使用 `local_host or None` 將空字串轉為 None，但 smtplib.SMTP 的 local_hostname 參數若為 None，會使用 socket.getfqdn() 取得本機主機名稱。若設定 SMTP_LOCAL_HOSTNAME 為空字串，原本意圖可能是使用預設值，但傳遞 None 會觸發 getfqdn()，可能導致 DNS 查詢延遲或失敗。建議明確處理空字串，例如直接傳遞 local_host（若為空字串則由 smtplib 自行處理）或設定為 None 前先檢查。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`
