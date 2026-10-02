# 盲標單 3：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-26-rules-loop/blind/labels-part3.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0227

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 來決定是否發送 webhook。若部署環境未設定此變數，則 `webhooksEnabled` 為 true，行為不變；但若設定為 "false"，則所有取消相關的 webhook 都會被靜默停用，且沒有 log 記錄。這可能導致生產環境中 webhook 意外失效。建議確認此環境變數的用途與部署設定，並考慮在停用時輸出警告 log。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0228

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）toolbar.leadingAnchor 錯誤地連接到 rightSkeletonAddressBar.trailingAnchor

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor` 應連接到 `leftSkeletonAddressBar.trailingAnchor`，但此 PR 將其改為連接到 `rightSkeletonAddressBar.trailingAnchor`。這會造成 toolbar 的左側與右側骨架條的右側對齊，導致 toolbar 與骨架條重疊或超出畫面，並可能引發無法滿足的 Auto Layout 約束。

**失敗情境**：當 `toolbarHelper.isSwipingTabsEnabled` 為 true 且骨架條顯示時，toolbar 會被錯誤定位，使用者可能看到 toolbar 與右側骨架條重疊，或產生約束衝突警告。

**建議**：將該行改回 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor).isActive = true`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0229

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試中未驗證 Descriptor 內容

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，僅驗證了 preamble marker 的 Assembly 與 TypeName，但未驗證 descriptor 的內容（例如參數定義與值）。這可能導致測試涵蓋不足，無法確保序列化與反序列化的正確性。建議參考其他測試（如 ServerMode 測試）增加對 descriptor 的驗證。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0230

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行）child team 過濾條件可能排除應包含的團隊

> 在 UNION 的第二個查詢中，條件為 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`。此條件只允許 org 本身或 child 等於 orgId，但若 orgId 是父組織，則 child 的 parentId 等於 orgId 的團隊不會被包含。這可能導致當 orgId 指定為父組織時，其下所有子團隊都被排除，與預期行為不符。建議改為 `child."parentId" = ${orgId}` 或加入 parentId 條件。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## P0231

**GT**（rule）Single underscore include guard used

> The rule requires header files to use include guards with double underscores at the start (e.g., __FILENAME_H), but the code uses a single underscore prefix instead (_REDIS_H)

GT 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

**finding**（`src/server.h:15`，距錨點 0 行）Include guard 從 __REDIS_H 改成 _REDIS_H，違反專案規範

> 專案規範   要求 header file 的 include guard 必須使用雙底線開頭和結尾（例如 `__REDIS_H`）。這個 PR 將 `__REDIS_H` 改成 `_REDIS_H`，違反了規範。

**建議**：改回 `__REDIS_H`，或使用符合規範的命名。

finding 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

## P0232

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行）start_execution 呼叫時機可能造成狀態不一致

> 在 `enqueue_node` 之前呼叫 `start_execution` 可能導致節點在尚未進入佇列時就被標記為執行中，若後續 `enqueue_node` 失敗，狀態將不一致。建議確認 `start_execution` 的實作是否具冪等性，或調整呼叫順序。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0233

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 remarks 寫入 Summary 可能造成語意不符

> 原本將 `<remarks>` 內容寫入 `operation.Description`，現在改為寫入 `operation.Summary`。在 OpenAPI 中，Summary 應為簡短摘要，而 Description 為詳細說明。若 remarks 內容較長，放入 Summary 可能導致 API 文件顯示不當。建議確認此變更是否符合預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## P0234

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行）自動截斷可能造成資料遺失，且未提供足夠的警告或備份機制

> 當 aof-load-broken 啟用且損壞部分小於 max-size 時，程式會直接 truncate 檔案，丟棄損壞部分之後的所有資料。這可能導致資料遺失，且僅記錄 warning。建議在 truncate 前先將原始檔案備份（例如複製一份），或至少提供更明確的警告，讓使用者知道有多少資料被丟棄。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0235

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 輸出日誌，應改用 logging

> 在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0236

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 19 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}> ⏎ <Badge variant="gray">+{hiddenItems.length}</Badge> ⏎ </Button>`

## P0237

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 19 行）鍵盤使用者無法操作 Popover

> PopoverTrigger 包著 Button，但 Button 沒有設定 onClick 處理常式，而是依賴 Popover 的 onOpenChange。鍵盤使用者聚焦到 Button 後按 Enter 或 Space 會觸發 Button 的點擊事件，但 Popover 可能不會因此開啟，因為 PopoverTrigger 的 asChild 會將事件處理器傳遞給 Button，但 Button 本身沒有 onClick，可能導致事件無法正確觸發 Popover 的開啟。建議明確設定 Button 的 onClick 來切換 isOpen，或確保 PopoverTrigger 的事件處理能正確傳遞。

finding 片段：`<Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0" ⏎ aria-label={`Show ${hiddenItems.length} more items`}`

## P0238

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:20`，距錨點 0 行）字串應使用單引號

> 此專案規範要求使用單引號，但此處將原本的單引號改為雙引號。請改回單引號以符合規範。

finding 片段：`const STORAGE_KEY = "ghost-history";`

## P0239

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖曳項目，可能導致拖放行為異常

> `sortableKeys` 包含所有項目的 key，包括 prefixItems（不可拖曳）。雖然 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled` 屬性設為 `!canMove`，但將不可拖曳項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳可移動項目時，不可移動項目仍被視為潛在目標。

建議：僅將可移動項目的 key 傳入 SortableContext，或確認 dnd-kit 對 disabled 項目的處理符合預期。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0240

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:350`，距錨點 30 行）快取寫入時使用了錯誤的變數 bulk_plans 而非 plans_to_cache

> 在 Step 3 的快取寫入迴圈中，程式碼遍歷的是 `bulk_plans.items()`，但 `bulk_plans` 是從 `get_plan_bulk` 回傳的完整字典，而 `plans_to_cache` 才是經過篩選、只包含需要快取的項目。這會導致即使某個 tenant 的 plan 驗證失敗（在 `get_plan_bulk` 中被設為 `None`），仍然會被寫入快取，造成快取中存有無效資料。

**失敗情境**：假設 `get_plan_bulk` 回傳 `{'tenant-1': valid_plan, 'tenant-2': None}`，則 `plans_to_cache` 只包含 `tenant-1`，但迴圈會將 `tenant-2` 也寫入快取，值為 `None`。下次讀取快取時，`json.loads('null')` 會得到 `None`，然後 `subscription_adapter.validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**建議修法**：將迴圈改為遍歷 `plans_to_cache.items()`。

finding 片段：`for tenant_id, subscription_plan in bulk_plans.items():`

## P0241

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:20`，距錨點 23 行）字串應使用單引號

> 此專案規範要求使用單引號，但此處將原本的單引號改為雙引號。請改回單引號以符合規範。

finding 片段：`const STORAGE_KEY = "ghost-history";`

## P0242

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）當 max_length 未定義時，比較邏輯可能失效

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，移除後若 `varItem.max_length` 為 undefined，則 `item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果為 false，導致長度檢查失效。應保留預設值或明確處理 undefined 情況。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0243

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 17 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0244

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 19 行）start_execution 呼叫時機可能造成狀態不一致

> 在 `enqueue_node` 之前呼叫 `start_execution` 可能導致節點在尚未進入佇列時就被標記為執行中，若後續 `enqueue_node` 失敗，狀態將不一致。建議確認 `start_execution` 的實作是否具冪等性，或調整呼叫順序。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0245

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `work-queue-status-trigger-fields.tsx` but does not add a corresponding `work-queue-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const WorkQueueStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-queue-status-trigger-fields.tsx:28`，距錨點 0 行）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## P0246

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴組合方式與後端不一致，導致端點名稱錯誤

> 此處將 `config.version` 直接加在 `endpointName` 前面，形成 `v2_api_kpis`；但後端 `tinybird.js` 是將版本加在後面，形成 `api_kpis_v2`。當前端設定 `version: 'v2'` 時，會呼叫不存在的端點 `v2_api_kpis`，造成 404。

建議改為與後端一致的後綴方式：
```ts
const finalEndpointName = config.version ? `${endpointName}_${config.version}` : endpointName;
```

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0247

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1115`，距錨點 0 行）使用 free 而非 zfree

> 根據規範  ，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

finding 片段：`free(slot_buffer);`

## P0248

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

## P0249

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖曳項目，可能導致拖放行為異常

> `sortableKeys` 包含所有項目的 key，包括 prefixItems（不可拖曳）。雖然 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled` 屬性設為 `!canMove`，但將不可拖曳項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳可移動項目時，不可移動項目仍被視為潛在目標。

建議：僅將可移動項目的 key 傳入 SortableContext，或確認 dnd-kit 對 disabled 項目的處理符合預期。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0250

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1117`，距錨點 2 行）使用 free 而非 zfree

> 根據規範  ，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

finding 片段：`free(slot_buffer);`

## P0251

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）AND 條件在 genericCalendarSuffixes 為空陣列時會產生空 AND，可能影響查詢結果

> 當 `genericCalendarSuffixes` 為空陣列時，`genericCalendarSuffixes?.length` 為 0，因此 `AND` 會被設為 `undefined`，這與未提供該參數時的行為一致。但若未來有其他條件需要加入 `AND`，此處的邏輯可能需要調整。目前影響不大，但建議考慮使用更明確的條件判斷。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0252

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:133`，距錨點 0 行）handleDragEnd 未驗證 over 項目是否可移動

> 在 `handleDragEnd` 中，僅檢查 `over` 存在且 id 不同，未確認 `over` 對應的項目是否可移動（即非 prefix item）。若使用者將可移動項目拖到 prefix item 上，會執行 `moveItem`，可能導致 prefix item 被移動或陣列順序錯誤。

建議：在執行移動前，檢查 `over` 對應的 index 是否滿足 `getCanMoveForIndex(newIndex)`。

finding 片段：`if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ );`

## P0253

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）回傳 Infinity 可能導致呼叫端未預期行為

> 當暖機天數超過 `totalDays` 時，`getWarmupLimit` 回傳 `Infinity`。若呼叫端將此值用於後續計算（例如分配郵件數量），可能產生非預期結果。建議回傳一個明確的數值（例如 `emailCount`）或定義一個特殊常數，並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0254

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行）get_plan_bulk 將驗證失敗的租戶設為 None，可能導致下游錯誤

> 在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼將 `results[tenant_id]` 設為 `None`。這可能導致呼叫端在後續處理時遇到 `None` 值而發生錯誤，因為原本的契約是回傳 `dict[str, SubscriptionPlan]`，且 `SubscriptionPlan` 不包含 `None`。建議改為跳過該租戶（不加入 results），或記錄錯誤後重新拋出例外，讓呼叫端決定如何處理。

finding 片段：`results[tenant_id] = None`

## P0255

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 型別轉換可能導致 SQL 錯誤

> 在 SQL 查詢中使用 `${orgId}::bigint`，但 orgId 是 number | undefined。若 orgId 為 undefined，會產生 `undefined::bigint`，在 PostgreSQL 中會導致語法錯誤。應使用 Prisma 的參數化查詢或明確處理 undefined。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0256

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0257

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行）linuxdeploy 下載 URL 使用錯誤的架構變數

> 原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為 `arch`。若 `arch` 為 i686，則會下載不存在的 i686 版本，導致下載失敗。應保留 `linuxdeploy_arch`。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0258

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）操作順序調整可能影響測試穩定性

> 在 testDisableTopSitesSettingsRemovesSection 中，原本先執行 navigator.goto(NewTabScreen) 再點擊 Done，現在改為先點擊 Done 再執行 navigator.goto(NewTabScreen)。這可能導致測試不穩定，因為點擊 Done 後可能尚未完全退出設定頁面，就嘗試導航到 NewTabScreen。建議確認此順序調整是否必要，或考慮增加等待條件。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0259

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 malloc 未檢查且迴圈越界寫入

> 在 `extractSlotFromKeysResult` 中，`malloc` 的回傳值未檢查，若記憶體配置失敗會導致對 NULL 指標寫入。此外，迴圈條件 `j <= keys_result->numkeys` 會寫入 `slot_buffer[numkeys]`，造成堆積緩衝區溢位。建議改為 `j < keys_result->numkeys`，並檢查 `malloc` 回傳值，失敗時回傳 `INVALID_CLUSTER_SLOT`。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎  ⏎ for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0260

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）scrollToTab 的索引計算可能 off-by-one

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但修改後變成 `state.tabs.count`。這可能導致滾動到超出最後一個項目的位置，造成越界或滾動失敗。

建議改回 `state.tabs.count - 1`，或確認 collection view 的 section 數量與 item 數量後再決定。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0261

**GT**（func）Missing directory parameter breaks WiX upgrade code validation

> In `wix_settings`, the environment variable check `std::env::var_os("TAURI_BUNDLER_WIX_FIPS_COMPLIANT")` was changed but the subsequent check incorrectly compares `OsString` with a string literal "true". The original code used `std::env::var()` which returns a `String`, but `var_os()` returns `OsString` which cannot be directly compared with `==` against a string slice. This breaks FIPS compliance detection for WiX installers, potentially creating non-compliant Windows builds when FIPS mode is required.

GT 片段：`fips_compliant: std::env::var_os("TAURI_BUNDLER_WIX_FIPS_COMPLIANT") ⏎ .map(|v| v == "true") ⏎ .unwrap_or(config.fips_compliant),`

**finding**（`crates/tauri-cli/src/helpers/config.rs:74`，距錨點 0 行）`fips_compliant` 使用 `var_os` 取代 `var`，可能導致非 UTF-8 值無法正確比對

> 原本的程式碼使用 `std::env::var("TAURI_BUNDLER_WIX_FIPS_COMPLIANT").ok().map(|v| v == "true")`，現在改為 `std::env::var_os(...).map(|v| v == "true")`。`var_os` 回傳 `OsString`，與 `"true"`（`&str`）比較時，若環境變數包含非 UTF-8 字元，比較結果可能不如預期。雖然此變數通常只會是 `"true"` 或 `"false"`，但使用 `var_os` 可能引入不必要的風險。

建議：若確定環境變數一定是 UTF-8，可繼續使用 `var`；否則應使用 `to_str()` 進行明確轉換。

finding 片段：`fips_compliant: std::env::var_os("TAURI_BUNDLER_WIX_FIPS_COMPLIANT") ⏎ .map(|v| v == "true") ⏎ .unwrap_or(config.fips_compliant),`

## P0262

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0263

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:117`，距錨點 27 行）權限邏輯變更可能導致資料外洩或功能回歸

> 原本僅 ADMIN/OWNER 角色可查看的預訂，現在改為任何具有 booking.read 權限的使用者皆可查看。若 PBAC 權限設定不當，可能導致未授權使用者存取他人預訂資料。此外，若 PermissionCheckService 回傳空陣列，則所有查詢分支都會被跳過，可能導致使用者看不到自己的預訂。建議確認 booking.read 權限的預設設定，並確保使用者至少能查看自己的預訂。

finding 片段：`const teamIdsWithBookingPermission = await permissionCheckService.getTeamIdsWithPermission({ ⏎ userId: user.id, ⏎ permission: "booking.read", ⏎ fallbackRoles,`

## P0264

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `work-pool-status-trigger-fields.tsx` but does not add a corresponding `work-pool-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const WorkPoolStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:28`，距錨點 0 行）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## P0265

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）React Scan 載入失敗時僅回傳空元件，使用者無法察覺 devtools 未啟動

> 在 `lazy` 的 `catch` 中，回傳 `{ default: () => null }`，這會讓 `ReactScan` 元件渲染為空。如果動態載入失敗（例如網路問題或 chunk 載入錯誤），使用者將看不到任何 devtools 功能，且沒有任何視覺提示，可能誤以為 devtools 正常運作。建議在 catch 中回傳一個顯示錯誤狀態的元件，或至少保留錯誤 log（目前已有 `console.error`，但使用者看不到）。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0266

**GT**（rule）Missing MIT license header

> The rule requires that every C# source file must start with the exact two-line MIT license header comment: '// Licensed to the .NET Foundation under one or more agreements.' followed by '// The .NET Foundation licenses this file to you under the MIT license.' This file is missing the required license header at the start.

GT 片段：`using System.Collections.Generic; ⏎ using System.Collections.Immutable; ⏎ using System.IO; ⏎ using Microsoft.CodeAnalysis;`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1`，距錨點 0 行）缺少 MIT 授權標頭

> 此檔案開頭原有的 MIT 授權標頭被移除，違反專案規範  。所有 C# 檔案必須以標準的兩行授權註解開頭。請補回：
```
// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the MIT license.
```

finding 片段：`using System.Collections.Generic;`

## P0267

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 0 行）拖放索引計算未考慮 prefixItems，可能導致項目錯位

> `handleDragEnd` 使用 `localKeyedValues` 的索引來呼叫 `moveItem`，但 `moveItem` 預期的是「可移動項目」的索引（已扣除 prefixItems）。當陣列有 prefixItems 時，`localKeyedValues` 包含所有項目，而 `moveItem` 內部可能使用 `getCanMoveForIndex` 或直接操作索引，導致拖放後項目順序錯誤。

建議：在 `handleDragEnd` 中先計算可移動項目的索引，或修改 `moveItem` 使其接受原始索引並在內部處理 prefixItems 偏移。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0268

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行）RequestBody.Description 設定位置變更可能影響行為

> 原本在 if (operation.RequestBody is not null) 區塊開頭就設定 operation.RequestBody.Description = description，現在移到區塊結尾。若中間有 continue 或例外，可能導致描述未被設定。需確認此變更不會造成遺漏。

finding 片段：`operation.RequestBody.Description = description;`

## P0269

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 欄位型別未明確

> `requestReschedule` 在 DTO 和 payload 型別中皆為選用布林值，但未明確其語意。建議在型別定義處加上 JSDoc 說明此欄位代表「是否為 request-reschedule 流程」，以避免未來誤用。

finding 片段：`requestReschedule?: boolean;`

## P0270

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 slot_buffer 可能非必要

> 新增的 `slot_buffer` 僅用於暫存每個 key 的 slot，但實際上可以直接在迴圈中比較，無需配置額外記憶體。這增加了記憶體使用與失敗點。

**建議修法**：移除 `slot_buffer`，直接在迴圈中計算並比較 slot。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0271

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:292`，距錨點 33 行）get_plan_bulk 將無效租戶設為 None，可能導致下游型別錯誤

> 在 `get_plan_bulk` 中，當 `validate_python` 失敗時，程式碼將 `results[tenant_id]` 設為 `None`。但函式的回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（例如 `get_plan_bulk_with_cache`）預期每個值都是 `SubscriptionPlan`。若下游程式碼直接存取 `result[tenant_id]['plan']`，會遇到 `TypeError: 'NoneType' object is not subscriptable`。

**失敗情境**：當某個租戶的 billing API 回傳格式錯誤時，該租戶在結果中為 `None`，而呼叫端未檢查 `None` 就使用，導致執行時期錯誤。

**建議**：不要將無效租戶放入結果字典，或將回傳型別改為 `dict[str, SubscriptionPlan | None]` 並要求呼叫端處理 `None`。

finding 片段：`results[tenant_id] = None`

## P0272

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 malloc 未檢查且迴圈越界寫入

> 在 `extractSlotFromKeysResult` 中，`malloc` 的回傳值未檢查，若記憶體配置失敗會導致對 NULL 指標寫入。此外，迴圈條件 `j <= keys_result->numkeys` 會寫入 `slot_buffer[numkeys]`，造成堆積緩衝區溢位。建議改為 `j < keys_result->numkeys`，並檢查 `malloc` 回傳值，失敗時回傳 `INVALID_CLUSTER_SLOT`。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎  ⏎ for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0273

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行）命名空間與類別縮排變更可能造成不必要的 diff

> 此變更將原本的 file-scoped namespace 改為 block-scoped namespace，並調整類別縮排。這與專案中其他測試檔案的風格可能不一致，且增加了 diff 的噪音。若無特殊原因，建議維持原本的 file-scoped namespace 寫法。

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ { ⏎ public class ServerComponentDeserializerTest ⏎ {`

## P0274

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:94`，距錨點 3 行）estimated_run_time 顯示邏輯與其他欄位不一致

> 其他欄位在空值時顯示 'None'，但 `estimated_run_time` 的判斷條件為 `!== null && !== undefined`，若值為 0 則會顯示 'None'，但 0 可能是有效的估計時間。建議使用 `??` 或 `!= null` 來判斷。

finding 片段：`{taskRun.estimated_run_time !== null && ⏎ taskRun.estimated_run_time !== undefined ⏎ ? formatTaskDuration(taskRun.estimated_run_time) ⏎ : "None"}`

## P0275

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `custom-trigger-fields.tsx` but does not add a corresponding `custom-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const CustomTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" }); ⏎ return (`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:16`，距錨點 0 行）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## P0276

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 回傳型別可能變為 undefined，呼叫端未處理

> 原本在 history 為 falsy 時會回傳 undefined，但現在直接回傳 history，型別從 URLHistory | undefined 變為 URLHistory | null | undefined（若 getDefaultUrlHistory 可能回傳 null）。呼叫端若未處理 null 可能導致執行時期錯誤。建議確認所有呼叫端皆能處理 null，或保留原本的條件判斷。

finding 片段：`return history;`

## P0277

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:247`，距錨點 4 行）reload_config 直接覆寫整個 ConfigMetadata 可能遺失未儲存的變更

> `reload_config` 函式直接將 `*config = load_config(...)` 的結果指派給傳入的 `&mut ConfigMetadata`。若在重新載入前有其他程式碼修改了 `config` 的某些欄位（例如透過 `merge_config_with`），這些變更會在重新載入時被覆蓋。建議先合併現有變更再重新載入，或明確區分唯讀與可變部分。

finding 片段：`pub fn reload_config( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

## P0278

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）日期計算可能因時區或時鐘偏移產生 off-by-one 錯誤

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並無條件進位。若伺服器時區與 UTC 有偏移，或系統時鐘在兩次呼叫間被調整，可能導致天數計算錯誤。例如，若首次 email 建立於 UTC 23:59，而目前時間為 UTC 00:01（相差 2 分鐘），計算結果為 1 天，但實際上可能尚未滿 24 小時。建議改用日曆日期（如 `created_at` 的日期部分與今天的日期差）來計算天數，或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0279

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:86`，距錨點 22 行）mark_edge_skipped 順序變更可能導致狀態不一致

> 在 _propagate_skip_to_node 中，原本先呼叫 mark_edge_skipped 再遞迴 propagate_skip_from_edge，現在順序對調。這可能導致在遞迴過程中，邊的狀態尚未標記為 skipped，若遞迴中發生錯誤或依賴邊狀態的邏輯，可能造成不一致。需要確認此變更的必要性與影響。

finding 片段：`self._state_manager.mark_edge_skipped(edge.id) ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

## P0280

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 remarks 寫入 Summary 可能改變既有 API 文件行為

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。這會將 `<remarks>` 的內容放到 OpenAPI 的 `summary` 欄位，而非 `description`。若既有使用者依賴 `description` 來顯示備註，此變更會造成文件內容遺失或錯置。建議確認此變更是否符合預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## P0281

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊

> 當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0282

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:330`，距錨點 35 行）快取資料驗證失敗時未清除無效快取，可能導致重複失敗

> 在 `get_plan_bulk_with_cache` 中，當從 Redis 讀取的快取資料無法通過 `validate_python` 驗證時，程式碼將該租戶加入 `cache_misses`，但未刪除 Redis 中的無效鍵。這會導致每次呼叫都重複嘗試解析無效資料，並在日誌中產生大量錯誤。

**失敗情境**：若某租戶的快取因版本變更而格式不符，每次批次作業都會嘗試解析並失敗，直到 TTL 過期。

**建議**：在驗證失敗時，主動刪除該租戶的 Redis 鍵（例如 `redis_client.delete(redis_key)`），或使用較短的 TTL 來加速失效。

finding 片段：`except Exception: ⏎ logger.exception( ⏎ "get_plan_bulk_with_cache: process tenant(%s) failed, add to cache misses", tenant_id ⏎ )`

## P0283

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）React Scan 載入失敗時靜默降級，可能隱藏錯誤

> 當 `import('./scan')` 失敗時，`.catch` 回傳一個渲染 `null` 的元件，導致 devtools 完全不出現且沒有任何使用者可見的提示。雖然有 `console.error`，但在 production 環境中可能被忽略。建議在開發環境中顯示一個明顯的錯誤訊息，或至少保留錯誤狀態供後續處理。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0284

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email trim 可能改變原本行為

> 在提交時對 email 進行 trim 是合理的，但需確認後端是否已處理 trim，以及是否會影響其他依賴原始輸入的邏輯。

finding 片段：`onSubmit({email: email.trim()});`

## P0285

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0286

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行）缺少錯誤處理，查詢失敗時元件會直接拋出錯誤

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 ErrorBoundary 包覆，整個應用程式可能崩潰。建議在元件外層加入 ErrorBoundary，或在查詢選項中設定 `retry` 與 `onError` 處理。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## P0287

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）陣列越界：argv 宣告大小為 5，但存取 argv[5]

> 在 hincrbyfloatCommand 中，`robj *argv[5];` 宣告了大小為 5 的陣列，但後續指派了 6 個元素（argv[0] 到 argv[5]），導致寫入超出陣列邊界。這會造成 stack buffer overflow，可能導致程式崩潰或安全漏洞。

建議將陣列大小改為 6：`robj *argv[6];`

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0288

**GT**（rule）Needless return statement in function

> The rule requires all Rust code to pass 'cargo clippy --all-targets --all-features -- -D warnings' without any warnings. The code contains an unnecessary explicit return statement that Clippy will flag with the needless_return lint.

GT 片段：`#[cfg(not(feature = "platform-certs"))] ⏎ let agent: ureq::Agent = ureq::Agent::config_builder() ⏎ .proxy(ureq::Proxy::try_from_env()) ⏎ .build()`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:56`，距錨點 6 行）base_ureq_agent 函式缺少文件註解

> 新增的 `pub(crate) fn base_ureq_agent()` 是 crate 內部公開函式，但未提供文件註解。雖然不是 public API，但為了可維護性，建議加上簡短說明其用途與行為。

finding 片段：`pub(crate) fn base_ureq_agent() -> ureq::Agent {`

## P0289

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用

> 檔案中定義的 Schedule 型別未加上 export，但後續的 CreateScheduleHandlerReturn 等型別使用了它。若其他檔案需要直接使用 Schedule，將無法匯入。建議將 Schedule 加上 export，或確認其僅供內部使用。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0290

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:330`，距錨點 3 行）快取資料驗證失敗時未清除無效快取，可能導致重複失敗

> 在 `get_plan_bulk_with_cache` 中，當從 Redis 讀取的快取資料無法通過 `validate_python` 驗證時，程式碼將該租戶加入 `cache_misses`，但未刪除 Redis 中的無效鍵。這會導致每次呼叫都重複嘗試解析無效資料，並在日誌中產生大量錯誤。

**失敗情境**：若某租戶的快取因版本變更而格式不符，每次批次作業都會嘗試解析並失敗，直到 TTL 過期。

**建議**：在驗證失敗時，主動刪除該租戶的 Redis 鍵（例如 `redis_client.delete(redis_key)`），或使用較短的 TTL 來加速失效。

finding 片段：`except Exception: ⏎ logger.exception( ⏎ "get_plan_bulk_with_cache: process tenant(%s) failed, add to cache misses", tenant_id ⏎ )`

## P0291

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12`，距錨點 17 行）Storybook decorator 中 QueryClient 實例可能造成快取污染

> `createTestRouter` 每次呼叫都會建立新的 QueryClient，但 decorator 外層的 `queryClient` 是模組層級的單例。這可能導致不同 story 之間共用快取，影響測試隔離性。建議將 QueryClient 的建立移入 decorator 內，或使用 Storybook 的 `parameters` 來注入。

finding 片段：`const queryClient = new QueryClient({ ⏎ defaultOptions: { ⏎ queries: { ⏎ retry: false,`

## P0292

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0293

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:49`，距錨點 0 行）validateCreateScheduleInput 回傳型別未嚴格驗證

> 函式回傳型別為 CreateScheduleInput，但僅透過型別斷言 (as CreateScheduleInput) 轉換，未實際驗證 schedule 與 eventTypeId 的型別。這可能導致呼叫端誤以為輸入已通過驗證，但實際上可能包含無效資料。建議使用型別守衛或 Zod schema 來確保型別安全。

finding 片段：`return data as CreateScheduleInput;`

## P0294

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0295

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0296

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0297

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0298

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）測試斷言對象可能錯誤

> 原本測試在選擇 Light 主題後，檢查 `lightThemeView` 的值是否為 "1"。修改後改為檢查 `darkThemeView` 的值，但變數名稱仍為 `lightIsSelected`，且後續選擇 Dark 主題的斷言可能未同步調整。這可能導致測試無法正確驗證主題選擇，或產生誤導性的測試結果。建議確認此修改是否為預期行為，並同步更新變數名稱與後續斷言。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0299

**GT**（rule）Method brace on same line

> The rule requires opening braces to appear on a new line after method declarations, but this method has its opening brace on the same line as the declaration (K&R style).

GT 片段：`[Experimental("ASP0029", UrlFormat = "https://aka.ms/aspnet/analyzer/{0}")] ⏎ public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) { ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:66`，距錨點 0 行）TryGetValidatableParameterInfo 方法格式調整

> 方法簽名從多行改為單行，且大括號位置改變。這僅為格式調整，不影響功能。

finding 片段：`public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) {`

## P0300

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許零值

> 驗證條件由 `value <= 0` 改為 `value < 0`，這將允許 `RetainedFileCountLimit` 設為 0。但屬性文件仍描述為「strictly positive value」，且 0 可能導致未定義行為（例如不保留任何檔案）。請確認此變更是否為預期，若非預期應維持 `<= 0` 的驗證。

finding 片段：`if (value < 0)`

## P0301

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）新增的 console.log 可能洩漏批次輸入資料

> 在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將使用者上傳的批次輸入資料（至少包含標頭列）輸出到瀏覽器主控台。如果資料包含敏感資訊（例如個人資料），可能造成隱私外洩。建議移除這行 console.log，或改用適當的日誌機制（如 debug 級別且不輸出資料內容）。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0302

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）版本不一致：cli.js 版本與 tauri-cli crate 版本不符

> 在 `crates/tauri-cli/metadata-v2.json` 中，`cli.js` 的版本從 `2.8.1` 更新為 `2.8.2`，但 `crates/tauri-cli/Cargo.toml` 中的版本僅從 `2.8.0` 更新為 `2.8.1`。這可能導致發布流程中 npm 套件與 Rust crate 版本不一致，或使用者安裝時取得錯誤的版本資訊。請確認正確的版本號並統一更新。

finding 片段：`"version": "2.8.2",`

## P0303

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 remarks 指派給 Summary 可能改變既有 API 文件語意

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。在 OpenAPI 中，Summary 與 Description 有不同用途：Summary 通常較簡短，Description 較詳細。若既有 XML 註解中 `<remarks>` 內容較長，此變更可能導致產生的 OpenAPI 文件不符合預期。建議確認此變更為有意為之，並考慮是否應同時設定兩者或保留原行為。

finding 片段：`operation.Summary = remarks;`

## P0304

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:42`，距錨點 26 行）items 陣列在 useMemo 依賴中可能導致不必要的重新計算

> useMemo 的依賴陣列包含 items，但 items 是從 props 傳入的陣列。如果父元件每次 render 都建立新的陣列（例如在 UserListTable 中使用 map 產生），則 useMemo 會失效，導致每次 render 都重新 slice。這可能造成效能影響，尤其是在大型表格中。建議使用 useMemo 時考慮 items 的參考穩定性，或使用 useRef 保存上一次的 items 並進行淺比較。

finding 片段：`const { visibleItems, hiddenItems } = useMemo( ⏎ () => ({ ⏎ visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0305

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0306

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）滾動索引可能越界：`toIndex` 應為 `state.tabs.count - 1`

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。若 `state.tabs` 非空，`state.tabs.count` 會超出陣列最後一個元素的索引，導致後續使用 `IndexPath(row:section:)` 時可能觸發越界例外或滾動到不存在的 cell。

**失敗情境**：使用者開啟 tab 面板，沒有任何 tab 被選取（例如剛刪除選取的 tab），且 `state.tabs` 有 3 個元素。此時 `toIndex` 會被設為 3，但有效索引範圍是 0...2。

**建議修法**：改回 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0307

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0308

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0309

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0310

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖曳的 prefix items，可能導致索引錯亂

> `sortableKeys` 使用 `localKeyedValues.map((item) => item.key)` 取得所有項目的 key，但其中包含不可拖曳的 prefix items（`canMove` 為 false）。當拖曳一般項目時，dnd-kit 的排序策略會考慮所有項目，可能導致計算出的 `over.id` 對應到 prefix item，進而使 `newIndex` 指向錯誤位置。建議只將可拖曳項目的 key 傳入 `SortableContext`，或使用 `disabled` 屬性排除 prefix items。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0311

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）preprocessCommand 條件變更可能導致 slot 未初始化

> 原本條件為 `num_keys > 0`，現在改為 `num_keys >= 0`。當 `num_keys == 0` 時，`extractSlotFromKeysResult` 會回傳 `INVALID_CLUSTER_SLOT`，但 `pcmd->slot` 可能未被初始化（若 `extractKeysAndSlot` 未設定）。

**失敗情境**：若 `num_keys == 0` 且 `pcmd->slot` 未初始化，則 `pcmd->slot == CLUSTER_CROSSSLOT` 的判斷可能讀取未初始化的記憶體，導致非預期行為。

**建議修法**：確認 `extractKeysAndSlot` 在 `num_keys == 0` 時會設定 `*slot`，或將條件改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) {`

## P0312

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript strict 模式將大幅降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用多項關鍵的型別檢查（如 `strictNullChecks`、`strictFunctionTypes` 等），可能導致未處理的 `null`/`undefined` 錯誤在編譯期無法被發現，增加 runtime 錯誤風險。此變更與 PR 的主要功能無關，且會影響整個專案的型別安全。建議恢復為 `true`，若有必要可針對特定檔案使用 `// @ts-ignore` 或調整型別定義，而非全域關閉。

finding 片段：`"strict": false,`

## P0313

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 slot_buffer 可能未完全初始化

> 若 `malloc` 成功但迴圈因 cross-slot 提前結束，`slot_buffer` 中剩餘元素未初始化，但這不影響 free。然而，若未來程式碼讀取這些未初始化值，可能導致問題。建議在 malloc 後使用 `memset` 初始化，或避免分配不必要的記憶體。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0314

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）使用 malloc/free 而非 zmalloc/zfree

> 根據規範  ，應使用 zmalloc/zfree 而非標準 malloc/free。此處新增的 `malloc` 和 `free` 違反規範，且無法追蹤記憶體使用。建議改用 `zmalloc` 和 `zfree`。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0315

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 2 行）行動裝置上 Popover 可能無法透過點擊開啟

> 在行動裝置上（isMobile 為 true），handleMouseEnter 和 handleMouseLeave 都不會觸發 setIsOpen，因此 Popover 只能透過點擊觸發。但 PopoverTrigger 包著一個 Button，點擊 Button 時會觸發 Popover 的 onOpenChange，但因為沒有阻止預設行為，可能導致按鈕的點擊事件與 Popover 的開啟邏輯衝突。此外，PopoverContent 上的 onMouseEnter/onMouseLeave 在行動裝置上也不會觸發，因此點擊外部關閉後，再次點擊按鈕可能無法重新開啟。建議在行動裝置上使用 click 事件來控制 Popover，並確保 PopoverTrigger 的點擊行為正確。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0316

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1117`，距錨點 0 行）使用 free 而非 zfree

> 根據規範  ，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

finding 片段：`free(slot_buffer);`

## P0317

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行）Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤

> 原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot.userIds 的型別是 number[]，但此處新定義的 Slot.userIds 為 string[]。這可能導致使用此型別的下游程式碼（例如 apps/web/test/lib/getSchedule/expects.ts）在編譯或執行時出現型別不符的錯誤。請確認實際資料型別，若為 number[] 應修正為 number[]，或若確實為 string[] 則需同步更新所有使用處。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## P0318

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）測試步驟順序調整可能影響穩定性

> 在 `testDisableTopSitesSettingsRemovesSection` 中，原本先 `navigator.goto(NewTabScreen)` 再點擊 "Done"，現在改為先點擊 "Done" 再 `navigator.goto(NewTabScreen)`。如果 "Done" 按鈕在當前畫面不存在或不可點擊，可能導致測試失敗。需要確認此調整是否為了解決特定問題，並驗證在各種裝置與狀態下仍能穩定執行。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0319

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 4 行）gtk 外掛腳本存在時仍會覆寫

> 原本邏輯是當 `gtk` 檔案不存在時才下載，但修改後變成當檔案存在時才寫入內嵌腳本。這會導致已存在的檔案被覆寫，可能不是預期行為。應改為 `if !gtk.exists()`。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0320

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 2 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}> ⏎ <Badge variant="gray">+{hiddenItems.length}</Badge> ⏎ </Button>`

## P0321

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0322

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）preprocessCommand 條件變更可能導致行為改變

> 原本條件為 `num_keys > 0`，現在改為 `num_keys >= 0`。這表示當 `num_keys == 0` 時，也會進入此區塊，但此時 `pcmd->slot` 可能為 `INVALID_CLUSTER_SLOT`（因為沒有 keys），不會觸發 cross-slot 錯誤。然而，若 `num_keys == 0` 且 `pcmd->slot` 意外為 `CLUSTER_CROSSSLOT`（不應發生），則會錯誤地設定 read_error。建議確認此變更是否必要，或改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) {`

## P0323

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:309`，距錨點 21 行）公開函式缺少文件註解

> write_and_make_executable 函式是公開的（pub fn），但沒有文件註解。根據規範  ，所有公開 API 都應該有 /// 文件說明其用途、參數和回傳值。建議補充文件。

finding 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> {`

## P0324

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）記憶體配置失敗未檢查

> `malloc` 的返回值未檢查，若配置失敗（回傳 NULL），後續寫入 `slot_buffer[j]` 會導致空指標解參考，造成程式崩潰。

**失敗情境**：在記憶體不足的環境下，`malloc` 回傳 NULL，程式將在寫入時崩潰。

**建議修法**：檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0325

**GT**（rule）Homepage duplicated in workspace member

> The rule requires workspace members to inherit metadata from the workspace level using `.workspace = true` rather than duplicating values. The homepage field is defined at both workspace and crate level.

GT 片段：`[package] ⏎ name = "tauri-bundler" ⏎ version = "2.6.1" ⏎ authors = [`

**finding**（`crates/tauri-bundler/Cargo.toml:12`，距錨點 0 行）新增 homepage 欄位可能違反 workspace metadata 繼承規範

> 在 `crates/tauri-bundler/Cargo.toml` 中新增了 `homepage = "https://tauri.app/"`。根據規範  ，workspace 成員應繼承 workspace.package 中的 metadata，除非有特殊原因。若 workspace 已定義 homepage，此處重複定義可能導致不一致。建議確認 workspace 是否已定義 homepage，若已定義則移除此處的欄位。

finding 片段：`homepage = "https://tauri.app/"`

## P0326

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷邏輯變更可能影響行為

> 原本 `isCurrentUser` 是 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示當 userIds 包含多個 ID 且其中包含當前使用者時，會被視為 current user，可能放寬權限檢查。請確認這是否符合預期。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0327

**GT**（rule）Public helper methods lack required documentation comments

> The helper methods `checkUrl()`, `copyUrl()`, and `checkCopiedUrl()` were changed to `public` but do not have triple-slash (`///`) documentation comments as required for public APIs.

GT 片段：`// Check for test url in the browser ⏎ public func checkUrl() { ⏎ let urlTextField = app.textFields[AccessibilityIdentifiers.Browser.AddressToolbar.searchTextField] ⏎ mozWaitForValueContains(urlTextField, value: "example.com")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ClipBoardTests.swift:11`，距錨點 0 行）輔助方法改為 public 可能違反封裝原則

> 將 `checkUrl()`、`copyUrl()`、`checkCopiedUrl()` 三個方法從 internal 改為 public。這些方法僅在測試類別內部使用，若無外部呼叫需求，建議維持 internal 或改為 private，以符合最小暴露原則。

finding 片段：`public func checkUrl() {`

## P0328

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateActionStack 的 stacks 合併誤將 pageActionStack 改為 browserActionStack

> 在 `updateActionStack` 方法中，原本合併 `browserActionStack`、`navigationActionStack`、`leadingPageActionStack`、`pageActionStack` 的 arrangedSubviews，但此 PR 將最後一項改為 `browserActionStack`，導致 `trailingPageActionStack`（原 `pageActionStack`）的 arrangedSubviews 未被納入。這會使後續的動畫或可視性更新遺漏 trailing page actions，可能造成 UI 不一致或動畫失效。

建議改回 `trailingPageActionStack.arrangedSubviews`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0329

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）webhook 停用時未記錄任何資訊

> 當 `ENABLE_WEBHOOKS` 設為 `false` 時，程式直接略過 webhook 發送，且未留下任何 log。這可能導致在除錯時難以判斷 webhook 是否因設定而停用。建議至少記錄一條 debug 或 info 等級的 log，說明 webhook 已停用。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎  ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

## P0330

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）新增 console.log 除錯語句

> 在批次輸入驗證前新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將資料輸出到瀏覽器主控台，可能洩漏使用者輸入內容，且違反專案規範  （禁止 console 語句）。請移除該行。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0331

**GT**（func）Missing error logging in TanStack devtools lazy import

> The TanStackDevtoolsLoader silently swallows import errors without logging them, making it impossible to debug why the devtools fail to load. This creates an inconsistent error handling pattern compared to the ReactScanLoader (in the same PR), which properly logs errors with console.error before returning a fallback component. When developers encounter issues with TanStack devtools not appearing, they will have no visibility into whether it's due to an import failure, missing dependencies, or other issues.

GT 片段：`const TanStackDevtoolsWrapper = lazy(() => ⏎ import('./devtools').then(module => ({ ⏎ default: module.TanStackDevtoolsWrapper, ⏎ })).catch(() => {`

**finding**（`web/app/components/devtools/tanstack/loader.tsx:9`，距錨點 0 行）TanStack devtools 載入失敗時完全吞掉錯誤

> `.catch(() => { return { default: () => null } })` 沒有記錄任何錯誤，若動態載入失敗，開發者將無法得知原因。建議至少加上 `console.error` 或類似的錯誤記錄。

finding 片段：`.catch(() => { ⏎ return { default: () => null } ⏎ })`

## P0332

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 而非 logging

> 在生產程式碼中使用 `print` 違反專案規範  ，應改用 `logging` 模組。這會導致輸出不受日誌系統控制，且可能洩漏敏感資訊。建議移除該行或改用 `logger.debug`。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0333

**GT**（rule）Unused import in new component

> The rule requires that all staged files pass 'biome lint --error-on-warnings' before commit. The code imports 'useEffect' from React but never uses it, which triggers a linting warning that should have been caught and fixed by the pre-commit hook.

GT 片段：`import useMediaQuery from "@calcom/lib/hooks/useMediaQuery"; ⏎ import { Badge } from "@calcom/ui/components/badge"; ⏎ import { Button } from "@calcom/ui/components/button"; ⏎ import { Popover, PopoverContent, PopoverTrigger } from "@calcom/ui/components/popover";`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:42`，距錨點 35 行）items 陣列變動時 Popover 狀態未重置

> 當 items 陣列變動（例如從有 hidden items 變成沒有）時，isOpen 狀態可能保持 true，導致 Popover 在沒有 hidden items 時仍然顯示。雖然元件在 items.length === 0 時會回傳 null，但當 hiddenItems 從有變無時，Popover 可能仍然開啟。建議在 items 或 hiddenItems 變化時重置 isOpen。

finding 片段：`const { visibleItems, hiddenItems } = useMemo( ⏎ () => ({ ⏎ visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0334

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行）updateToolbarLayout 中判斷頁面動作存在與否的 stack 錯誤

> 在 updateToolbarLayout 中，原本使用 pageActionStack（即現在的 trailingPageActionStack）來判斷是否有頁面動作，但重構後改為 leadingPageActionStack。這可能導致當只有 trailing 頁面動作而沒有 leading 頁面動作時，分隔線寬度被設為 0，造成 UI 顯示不正確。

建議改回使用 trailingPageActionStack：
```swift
let hasPageActions = !trailingPageActionStack.arrangedSubviews.isEmpty
```

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## P0335

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0336

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）使用 malloc/free 而非 zmalloc/zfree

> 新增的 `malloc` 與 `free` 呼叫違反專案規範  ，應使用 `zmalloc` 與 `zfree` 以利記憶體追蹤。

**建議修法**：將 `malloc` 改為 `zmalloc`，`free` 改為 `zfree`。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0337

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:416`，距錨點 0 行）webhooksEnabled 判斷可能影響既有行為

> 新增的 `webhooksEnabled` 判斷會在環境變數為 "false" 時跳過所有 webhook 發送。若此環境變數未設定，行為不變；但若設定為 "false"，則會完全停用 webhook，可能影響依賴 webhook 的功能。建議確認此變更是否為預期行為，並考慮提供更明確的設定方式。

finding 片段：`const promises = webhooksEnabled ? webhooks.map((webhook) =>`

## P0338

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:325`，距錨點 40 行）Redis mget 回傳值長度檢查可能誤判

> 在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## P0339

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`
