# 盲標單 （主 session 抽樣）：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-26-rules-loop/blind/spot-main.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0006

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 驗證條件從 `if (value <= 0)` 改為 `if (value < 0)`，這將允許 `RetainedFileCountLimit = 0`。但文件描述為「strictly positive value」，且 0 可能導致未定義行為（例如保留 0 個檔案）。建議確認此變更是否為預期，若非預期應改回 `<= 0`。

finding 片段：`if (value < 0)`

## P0029

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 回傳型別可能變為 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但修改後直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，此函式現在會回傳 undefined，可能導致呼叫端出現錯誤。請確認呼叫端是否能處理 undefined，或保留原本的條件判斷。

finding 片段：`return history;`

## P0057

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript strict 模式

> 將 `strict` 從 `true` 改為 `false` 違反了專案規範  （TypeScript Must Enable Strict Type Checking）。這會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復 `strict: true`，並修正因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0061

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript strict 模式會降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查，包括 `strictNullChecks`、`strictFunctionTypes` 等，可能導致未處理的 null/undefined 錯誤、錯誤的型別推斷，並隱藏潛在的執行時期錯誤。這通常不是一個可接受的變更，除非有明確的技術原因。建議恢復為 `true`，並修正任何因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0077

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## P0083

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）使用 propertyName 取代 metadata.Name 可能影響參數匹配

> 原本使用 metadata.Name 來尋找 operation.Parameters 中的參數，現在改為 propertyName。若 metadata.Name 與 propertyName 不同，可能導致找不到參數而將描述套用到 RequestBody。需確認此變更符合預期。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0093

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 slot_buffer 可能未完全初始化

> 若 `malloc` 成功但迴圈因 cross-slot 提前結束，`slot_buffer` 中剩餘元素未初始化，但這不影響 free。然而，若未來程式碼讀取這些未初始化值，可能導致問題。建議在 malloc 後使用 `memset` 初始化，或避免分配不必要的記憶體。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0102

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，但原文仍包含該變數。這可能導致使用者看不到具體的新聞信名稱，影響理解。建議保留變數。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0145

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）extractSlotFromKeysResult 迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會多執行一次，當 `j == numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體（配置大小為 `numkeys` 個 int）。此外，`argv[keys_result->keys[j].pos]` 也會讀取超出 `keys_result->keys` 陣列範圍的記憶體。

**失敗情境**：當 `numkeys > 0` 時，最後一次迭代會造成 heap buffer overflow，可能導致程式崩潰或任意程式碼執行。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0155

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:86`，距錨點 22 行）mark_edge_skipped 順序變更可能導致狀態不一致

> 在 _propagate_skip_to_node 中，原本先呼叫 mark_edge_skipped 再遞迴 propagate_skip_from_edge，現在順序對調。這可能導致在遞迴過程中，邊的狀態尚未標記為 skipped，若遞迴中發生錯誤或依賴邊狀態的邏輯，可能造成不一致。需要確認此變更的必要性與影響。

finding 片段：`self._state_manager.mark_edge_skipped(edge.id) ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

## P0194

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）條件判斷變更可能影響無 key 命令的處理

> 原本 `else if (num_keys > 0)` 只在有 key 時檢查 cross-slot，現在改為 `else if (num_keys >= 0)`，這會讓 `num_keys == 0` 的命令也進入檢查。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為無 key 命令不會有 cross-slot），則會設定錯誤。但更可能的是，原本 `num_keys == 0` 時會跳過此區塊，現在會執行，可能影響後續邏輯。

建議確認此變更是否必要，或改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

## P0195

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1830`，距錨點 11 行）AOF_BROKEN_RECOVERED 在非最後檔案時被視為致命錯誤，但日誌訊息仍稱「truncated」

> 在 `loadAppendOnlyFiles` 中，若 `ret == AOF_BROKEN_RECOVERED` 且不是最後一個檔案，程式會記錄「Fatal error: the truncated file is not the last file」。此處的「truncated」可能造成混淆，因為實際上是格式錯誤後自動截斷。建議調整日誌訊息以區分兩種情況。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0208

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> `UIApplication.shared.statusBarOrientation` 在 iOS 13 已棄用，建議改用 `view.window?.windowScene?.interfaceOrientation` 或 `traitCollection.verticalSizeClass` 來判斷方向。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0233

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 remarks 寫入 Summary 可能造成語意不符

> 原本將 `<remarks>` 內容寫入 `operation.Description`，現在改為寫入 `operation.Summary`。在 OpenAPI 中，Summary 應為簡短摘要，而 Description 為詳細說明。若 remarks 內容較長，放入 Summary 可能導致 API 文件顯示不當。建議確認此變更是否符合預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## P0247

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1115`，距錨點 0 行）使用 free 而非 zfree

> 根據規範  ，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

finding 片段：`free(slot_buffer);`

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

## P0285

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0298

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）測試斷言對象可能錯誤

> 原本測試在選擇 Light 主題後，檢查 `lightThemeView` 的值是否為 "1"。修改後改為檢查 `darkThemeView` 的值，但變數名稱仍為 `lightIsSelected`，且後續選擇 Dark 主題的斷言可能未同步調整。這可能導致測試無法正確驗證主題選擇，或產生誤導性的測試結果。建議確認此修改是否為預期行為，並同步更新變數名稱與後續斷言。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0315

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 2 行）行動裝置上 Popover 可能無法透過點擊開啟

> 在行動裝置上（isMobile 為 true），handleMouseEnter 和 handleMouseLeave 都不會觸發 setIsOpen，因此 Popover 只能透過點擊觸發。但 PopoverTrigger 包著一個 Button，點擊 Button 時會觸發 Popover 的 onOpenChange，但因為沒有阻止預設行為，可能導致按鈕的點擊事件與 Popover 的開啟邏輯衝突。此外，PopoverContent 上的 onMouseEnter/onMouseLeave 在行動裝置上也不會觸發，因此點擊外部關閉後，再次點擊按鈕可能無法重新開啟。建議在行動裝置上使用 click 事件來控制 Popover，並確保 PopoverTrigger 的點擊行為正確。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0326

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷邏輯變更可能影響行為

> 原本 `isCurrentUser` 是 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示當 userIds 包含多個 ID 且其中包含當前使用者時，會被視為 current user，可能放寬權限檢查。請確認這是否符合預期。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0370

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致可能導致下游誤判

> 在 BookingPayloadBuilder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true` 作為預設值，但在 BookingWebhookFactory 中則使用 `params.requestReschedule ?? false`。這兩個地方對同一欄位的預設值不同，可能導致不同路徑產生的 webhook payload 不一致，進而影響下游系統的判斷。建議統一預設值，並明確其語意。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0385

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）out 參數初始化位置調整可能影響可讀性

> 將 `validatableTypeInfo = null;` 移至方法開頭，雖然功能上無差異，但可能降低可讀性，因為初始化與後續邏輯分離。若無特殊原因，建議保留在迴圈後。

finding 片段：`validatableTypeInfo = null;`

## P0389

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行）「Name」翻譯從「名字」改為「名稱」可能造成不一致

> 在 portal.json 中，`"Name"` 的翻譯從 `"名字"` 改為 `"名稱"`。但在同檔案的 `"Jamie Larson": "阿宇"` 和 `"jamie@example.com": "ayu@example.com"` 等範例中，可能仍使用「名字」的語境。此外，ghost.json 中 `"Name"` 的翻譯也改為 `"名字"`，可能造成不一致。請確認此變更是否為預期。

finding 片段：`"Name": "名称",`

## P0409

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行）快取寫入時可能將 None 序列化為 'null' 字串

> 即使修正了變數名稱，如果 `plans_to_cache` 中包含值為 `None` 的項目（例如 `get_plan_bulk` 回傳的字典中某個 tenant 的值為 `None`），`json.dumps(None)` 會產生字串 `'null'`。之後讀取快取時，`json.loads('null')` 會得到 `None`，然後 `validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，`plans_to_cache` 包含 `tenant-1`，寫入快取的值為 `'null'`。下次讀取時，`json.loads` 得到 `None`，驗證失敗，進入 cache miss，重新呼叫 API，但 API 可能再次回傳 `None`，形成無效快取。

**建議修法**：在寫入快取前，過濾掉值為 `None` 的項目，或確保 `get_plan_bulk` 不會回傳 `None` 值。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0505

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0508

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 18 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0520

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）skeleton address bar 的 leading 約束可能誤接至 rightSkeletonAddressBar

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)` 被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 錯誤地對齊到右側 skeleton bar 的 trailing，造成佈局錯亂。

請確認此變更是否為預期；若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0535

**GT**（rule）Single underscore include guard used

> The rule requires header files to use include guards with double underscores at the start (e.g., __FILENAME_H), but the code uses a single underscore prefix instead (_REDIS_H)

GT 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

**finding**（`src/server.h:15`，距錨點 0 行）變更 include guard 巨集名稱可能影響外部程式碼

> 將 `__REDIS_H` 改為 `_REDIS_H` 可能導致與其他使用相同 guard 的程式碼衝突，或破壞依賴舊巨集名稱的條件編譯。雖然影響不大，但建議確認此變更的必要性。

finding 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

## P0558

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）truncate 後未更新 AOF 檔案大小相關的狀態

> truncate 成功後，程式僅將檔案描述子 seek 到結尾，但未更新 server 中可能記錄的 AOF 檔案大小或 offset 等狀態。這可能導致後續 AOF 寫入時發生錯誤或覆蓋。建議檢查是否有相關狀態需要更新。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`
