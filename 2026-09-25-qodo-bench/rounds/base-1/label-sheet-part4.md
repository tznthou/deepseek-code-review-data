# 盲標單：finding 跟 GT 是不是同一個問題

判準（Martian）：**一個 code change 能同時修掉兩者**才算 `same`；同處、相關但講的是別的問題算 `partial`；否則 `no`。
本單刻意不含 confidence、severity。標在 `labels.csv`：`pair,label,note`。

## base-1:prefect-8:1|prefect-8#1

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:462`，距錨點 0 行，候選管道 model_line）V2 啟用時 static_subpath 指派錯誤

> 在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`static_subpath` 被指派為 `prefect.__ui_static_subpath__`（V1 的子路徑），而 `source_static_path` 為 `prefect.__ui_v2_static_path__`。這導致後續 `create_ui_static_subpath` 會將 V2 的靜態檔案複製到 V1 的子路徑，可能覆蓋 V1 檔案或造成路徑衝突。應將 `static_subpath` 指派為 `prefect.__ui_v2_static_subpath__`。

finding 片段：`static_subpath = prefect.__ui_static_subpath__`

## base-1:prefect-8:3|prefect-8#0

**GT**（rule）Direct logging.getLogger() call used

> The rule requires loggers to be instantiated using the pattern `logger: "logging.Logger" = get_logger("module_name")` instead of direct `logging.getLogger()` calls

GT 片段：`# Log which UI version is being served ⏎ if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

**finding**（`src/prefect/server/api/server.py:532`，距錨點 0 行，候選管道 loc）日誌訊息未使用結構化格式

> 新增的日誌訊息 `Serving experimental V2 UI` 使用 f-string 或直接字串，未包含結構化欄位（如 UI 版本），不利於日誌分析。建議使用結構化日誌或至少包含版本資訊。

finding 片段：`ui_logger.info("Serving experimental V2 UI")`

## base-1:prefect-9:1|prefect-9#2

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行，候選管道 loc）缺少 error boundary 處理查詢失敗

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 error boundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層或路由層級加入 error boundary，並提供 fallback UI。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## base-1:prefect-9:2|prefect-9#1

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行，候選管道 loc）stories 中 queryClient 設定不一致

> 在 `createTestRouter` 中建立了一個新的 `QueryClient` 並放入 router context，但 decorator 中使用的 `QueryClientProvider` 是全域的 `queryClient`。這可能導致測試時 query client 不一致，建議統一使用同一個 instance。

finding 片段：`context: { queryClient: new QueryClient() },`

## base-1:redis-1:1|redis-1#2

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:914`，距錨點 0 行，候選管道 loc）dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找可能失敗

> 在 dictSetKeyAtLink 中，當 newItem=0 且 *link 為 NULL 時，程式碼使用 addedKey 呼叫 dictFindLink。但 addedKey 是經過 keyDup 處理後的鍵，可能與原始 key 不同（例如 keyDup 可能複製或轉換鍵）。如果 dictFindLink 使用 addedKey 找不到對應的 entry，則會觸發 assert(*link != NULL) 失敗。

失敗情境：當 dictType.keyDup 非 NULL 且會改變鍵的內容（例如複製 sds 或進行其他轉換），且呼叫者傳入的 key 與儲存的鍵不同時，dictFindLink 將無法找到 entry。

建議：應使用原始 key（或 dictStoredKey2Key(d, key)）進行查找，而不是 addedKey。

finding 片段：`*link = dictFindLink(d, addedKey, NULL);`

## base-1:redis-1:2|redis-1#0

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行，候選管道 loc）validateStoredKeyConversion 函式未被使用

> 新增的 validateStoredKeyConversion 函式在整個 diff 中沒有被呼叫。這可能是未完成的功能或遺留的除錯程式碼。

建議：如果不需要，應移除此函式；如果需要，應在適當的地方呼叫它。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) {`

## base-1:redis-2:2|redis-2#2

**GT**（func）Memory leak due to missing error message reply to client

> In parseSlotRangesOrReply, when slot range validation fails, the error message allocated by slotRangeArrayNormalizeAndValidate is freed with sdsfree(err) but never sent to the client via addReplyErrorSds. This causes two problems: the client receives no error message explaining why their command failed, making debugging difficult, and it breaks the expected behavior where addReplyErrorSds transfers ownership of the sds string. The original PR intended to always send validation errors to the client for proper error reporting.

GT 片段：`sds err = NULL; ⏎ if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots);`

**finding**（`src/cluster.c:2015`，距錨點 0 行，候選管道 loc）驗證失敗時未回覆錯誤給客戶端

> 在 `parseSlotRangesOrReply` 中，原本驗證失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但修改後只呼叫 `sdsfree(err)` 釋放錯誤訊息，卻未回覆任何錯誤。這會導致客戶端在提供無效 slot range 時收到空回覆或逾時，而非明確的錯誤訊息。

建議：
- 在釋放 `err` 之前，先呼叫 `addReplyErrorSds(c, err)` 回覆錯誤。
- 或者，若 `err` 為 NULL，則回覆一個通用的錯誤訊息。

finding 片段：`if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err);`

## base-1:redis-2:3|redis-2#0

**GT**（rule）Unused variable causes compilation warning

> The rule requires that compilation completes successfully with no warnings when -Werror flag is enabled. The code contains an unused variable 'total_ranges' that triggers a compilation warning.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1012`，距錨點 0 行，候選管道 loc）`asmCountKeysInSlots` 可能造成大量迴圈與效能問題

> `asmCountKeysInSlots` 會針對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slot（例如整個 hash slot 空間 0-16383），則會執行 16384 次函式呼叫。雖然 `kvstoreDictSize` 本身可能只是 O(1) 的查詢，但大量的函式呼叫仍可能造成不必要的效能負擔，特別是在日誌記錄或任務啟動時頻繁呼叫。

建議：
- 評估是否有更有效率的方式取得 key 數量，例如直接從 `kvstore` 取得總數，或使用批次 API。
- 若無法避免，考慮加入快取或限制呼叫頻率。

finding 片段：`unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎  ⏎ unsigned long long key_count = 0;`

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

## base-1:redis-2:5|redis-2#1

**GT**（func）Incorrect comparison logic causes false negatives when comparing slot ranges

> The slotRangeArrayIsEqual function checks if the number of ranges are equal before normalizing and merging adjacent ranges. This causes the function to incorrectly return false (0) when comparing two slot range arrays that represent the same slots but have different numbers of ranges before merging. For example, comparing [1000-1001, 1002-1003] (2 ranges) with [1000-1003] (1 range) will return false even though they represent the same slots after merging. This breaks the task lookup functionality in asmLookupTaskBySlotRangeArray, preventing correct task identification when slot ranges are specified in different but equivalent formats.

GT 片段：`int slotRangeArrayIsEqual(slotRangeArray *slots1, slotRangeArray *slots2) { ⏎ if (slots1->num_ranges != slots2->num_ranges) return 0; ⏎ slotRangeArraySortAndMerge(slots1); ⏎ slotRangeArraySortAndMerge(slots2);`

**finding**（`src/cluster.c:1855`，距錨點 21 行，候選管道 ident）`slotRangeArraySortAndMerge` 未處理重疊範圍

> 註解明確指出「Overlapping ranges are not merged.」，但若輸入包含重疊範圍（例如 100-200 和 150-250），合併後仍會保留兩個範圍，且後續的驗證會偵測到重疊並回報錯誤。這可能是預期行為，但建議在函式中明確處理或至少記錄此情況，以避免未來誤用。

finding 片段：`/* Sort slot ranges by start slot and merge adjacent ranges. ⏎ * Adjacent means: prev.end + 1 == next.start. ⏎ * e.g. 1000-2000 2001-3000 0-100  =>  0-100 1000-3000 ⏎ *`

## base-1:redis-3:1|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行，候選管道 loc）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## base-1:redis-3:1|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行，候選管道 loc）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## base-1:redis-3:2|redis-3#3

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行，候選管道 loc）slot 可能未初始化即被使用

> 在 `extractKeysAndSlot` 中，原本 `*slot` 會先被設為 `INVALID_CLUSTER_SLOT`，但修改後只有當 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 `*slot`。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能導致未初始化變數被使用。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT`，或確保所有呼叫者都已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## base-1:redis-3:3|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-3:3|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-3:4|redis-3#2

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行，候選管道 loc）條件判斷變更可能影響無 key 命令的處理

> 原本 `else if (num_keys > 0)` 只在有 key 時檢查 cross-slot，現在改為 `else if (num_keys >= 0)`，這會讓 `num_keys == 0` 的命令也進入檢查。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為無 key 命令不會有 cross-slot），則會設定錯誤。但更可能的是，原本 `num_keys == 0` 時會跳過此區塊，現在會執行，可能影響後續邏輯。

建議確認此變更是否必要，或改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

## base-1:redis-3:5|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-3:5|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-4:1|redis-4#0

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行，候選管道 loc）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## base-1:redis-4:1|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行，候選管道 ident）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## base-1:redis-4:2|redis-4#2

**GT**（func）ASM cron runs before cluster state update causing stale state issues

> The serverCron() function now calls asmCron() before clusterCron(). This is problematic because clusterCron() contains the call to clusterUpdateState() which updates the cluster's operational state (CLUSTER_OK vs CLUSTER_FAIL). ASM (Atomic Slot Migration) operations depend on having an accurate view of the cluster state to make correct migration decisions. By executing asmCron() first, migration tasks may operate on stale cluster state information from the previous iteration, potentially leading to incorrect slot migration decisions, failed migrations, or data consistency issues during cluster rebalancing operations.

GT 片段：`if (server.cluster_enabled) { ⏎ asmCron(); ⏎ clusterCron(); ⏎ }`

**finding**（`src/server.c:1658`，距錨點 0 行，候選管道 loc）asmCron() 呼叫順序可能影響原子槽遷移

> 原本 asmCron() 在 clusterCron() 內部最後呼叫，現在移到 serverCron 中 clusterCron() 之前。若 asmCron 依賴 clusterCron 更新後的叢集狀態，順序變更可能導致行為錯誤。建議確認 asmCron 的相依性，或維持原本順序。

finding 片段：`asmCron(); ⏎ clusterCron();`

## base-1:redis-4:4|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 3 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## base-1:redis-4:4|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 0 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## base-1:redis-4:5|redis-4#1

**GT**（func）Incorrect operation order causes potential data loss during cluster verification

> The verifyClusterConfigWithData() function executes clusterDeleteKeysInUnownedSlots() before clusterClaimUnassignedSlots(). This reverses the intended logic: the function should first claim ownership of unassigned slots that contain keys (preventing orphaned data), then delete keys from slots that are genuinely owned by other nodes. With this bug, keys in unassigned slots may be incorrectly deleted before the node has a chance to claim ownership, resulting in permanent data loss during cluster startup or recovery scenarios.

GT 片段：`/* Delete keys in unowned slots */ ⏎ clusterDeleteKeysInUnownedSlots(); ⏎ /* Take over slots that we have keys for, but are assigned to no one. */ ⏎ clusterClaimUnassignedSlots();`

**finding**（`src/cluster.c:2167`，距錨點 35 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-4:5|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 17 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-4:5|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 10 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-5:1|redis-5#0

**GT**（rule）Direct malloc_usable_size instead of zmalloc_size

> The rule requires all memory operations to use Redis zmalloc wrappers (zmalloc_size) instead of direct libc functions (malloc_usable_size)

GT 片段：`/* All kv-objects has at least kvobj header and embedded key */ ⏎ size_t asize = malloc_usable_size((void *)o);`

**finding**（`src/object.c:1239`，距錨點 22 行，候選管道 ident）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:redis-5:1|redis-5#1

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:redis-5:1|redis-5#4

**GT**（func）Unused variable 'elecount' causes build failure with -Werror

> The variable 'elecount' is declared and incremented in the QUICKLIST encoding branch (line 1236: 'elecount += node->count') but is never used after the PR changed the calculation from 'elesize/elecount' to 'elesize/samples'. This creates an unused-but-set variable which triggers compiler warnings under -Wall (enabled in Makefile) and causes build failures when compiling with -Werror flag. This violates AGENTS.MD Rule #4 which requires the codebase to compile without warnings when REDIS_CFLAGS="-Werror" is enabled.

GT 片段：`size_t elesize = 0, elecount = 0, samples = 0; ⏎ ... ⏎ if (o->encoding == OBJ_ENCODING_QUICKLIST) { ⏎ quicklist *ql = o->ptr;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:redis-5:2|redis-5#2

**GT**（func）Variable shadowing breaks sampling consistency for STREAM objects

> A local `samples` variable is declared at line 1319 within the OBJ_STREAM branch, shadowing the outer `samples` variable declared at line 1214. This prevents the outer samples counter from being updated during stream memory calculation. While this doesn't break the stream calculation itself, it violates the function's sampling design pattern where the outer `samples` variable tracks total sampling across all object type branches. This inconsistency could lead to unexpected behavior if the function logic is modified to check or use the outer samples counter after processing.

GT 片段：`raxStart(&ri,s->rax); ⏎ raxSeek(&ri,"^",NULL,0); ⏎ size_t lpsize = 0; ⏎ size_t samples = 0;`

**finding**（`src/object.c:1330`，距錨點 10 行，候選管道 ident）stream 的 lpsize 計算可能多算最後一個 listpack

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## base-1:redis-5:2|redis-5#3

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行，候選管道 loc）stream 的 lpsize 計算可能多算最後一個 listpack

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## base-1:redis-6:1|redis-6#1

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行，候選管道 loc）active defrag 恢復邏輯可能錯誤地啟用 defrag

> 在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

finding 片段：`server.active_defrag_enabled = 1;`

## base-1:redis-6:1|redis-6#4

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行，候選管道 loc）active defrag 恢復邏輯可能錯誤地啟用 defrag

> 在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

finding 片段：`server.active_defrag_enabled = 1;`

## base-1:redis-6:2|redis-6#2

**GT**（func）Stream entries incorrectly marked as referenced when cgroups_ref is NULL

> When cgroups_ref is NULL (which occurs after DEBUG RELOAD with empty PEL), the function returns 1 indicating the entry IS referenced, when it should return 0 indicating it is NOT referenced. This inverted logic prevents XADD/XTRIM operations with the ACKED strategy from correctly deleting entries that have been fully acknowledged by all consumer groups. The result is a memory leak where stream entries accumulate unnecessarily because they are incorrectly protected from deletion even though no consumer group has them in their pending entry list.

GT 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1; ⏎ unsigned char buf[sizeof(streamID)]; ⏎ streamEncodeID(buf, id);`

**finding**（`src/t_stream.c:2708`，距錨點 0 行，候選管道 loc）streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留

> 新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1，表示該 entry 被引用。這可能導致 stream 的 entry 無法被刪除，即使沒有 consumer group 引用它。

失敗情境：當 stream 沒有 consumer groups 時，呼叫 streamEntryIsReferenced 會回傳 1，使得呼叫者認為 entry 仍被引用，因此不會刪除它，可能造成記憶體洩漏或資料不一致。

建議：確認此處的意圖。若 cgroups_ref 為 NULL，應回傳 0（未被引用）而非 1。或者，應檢查呼叫者是否正確處理此情況。

finding 片段：`if (!s->cgroups_ref) return 1;`

## base-1:redis-6:3|redis-6#3

**GT**（func）Inverted reply discard logic causes test infrastructure failure

> The condition for discarding replies is inverted - replies are discarded when count is NOT a multiple of frequency (!=), rather than when it IS a multiple (==). This causes the test to read and discard replies at the wrong times, leading to a buffer overflow of unread replies. The discard_replies_every helper is called throughout the test suite after batches of Redis commands to prevent reply buffer buildup. With this bug, replies accumulate in the buffer instead of being cleared, causing test hangs or failures when the client tries to send new commands with a full reply buffer.

GT 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

**finding**（`tests/unit/memefficiency.tcl:70`，距錨點 0 行，候選管道 loc）discard_replies_every 函式參數名稱可能造成混淆

> 函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 的語意不夠清晰。`frequency` 代表每多少次觸發一次丟棄，`discard_num` 代表每次丟棄的數量。但呼叫時傳入的數值可能與預期不符，例如在 lpush 的測試中，原本每次丟棄 20000 個 replies，但函式呼叫為 `discard_replies_every $rd $count 10000 20000`，這表示每 10000 次丟棄 20000 個 replies，與原本邏輯相同，但可讀性較差。

建議：考慮重新命名參數或加入註解，以提升可讀性。

finding 片段：`proc discard_replies_every {rd count frequency discard_num} {`

## base-1:redis-7:1|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1722`，距錨點 5 行，候選管道 model_line）AOF_BROKEN_RECOVERED 在非最後一個檔案時未正確處理，可能導致資料不一致

> 在 loadAppendOnlyFiles 中，當 ret == AOF_BROKEN_RECOVERED 且 !last_file 時，程式碼將 ret 設為 AOF_FAILED 並記錄錯誤，但隨後在 if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) 的條件中，因為 ret 已被改為 AOF_FAILED，所以會進入 cleanup 並中止載入。然而，此處的邏輯有問題：如果 AOF_BROKEN_RECOVERED 發生在非最後一個檔案，實際上檔案已被 truncate 修改，但後續的檔案仍可能被載入，導致資料不一致。建議在非最後一個檔案遇到 AOF_BROKEN_RECOVERED 時，應立即中止載入並回報錯誤，且不應修改原始檔案。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## base-1:redis-7:3|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行，候選管道 loc）自動截斷可能造成資料遺失，且未提供足夠的警告或備份機制

> 當 aof-load-broken 啟用且損壞部分小於 max-size 時，程式會直接 truncate 檔案，丟棄損壞部分之後的所有資料。這可能導致資料遺失，且僅記錄 warning。建議在 truncate 前先將原始檔案備份（例如複製一份），或至少提供更明確的警告，讓使用者知道有多少資料被丟棄。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## base-1:redis-7:4|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行，候選管道 ident）truncate 後未更新 AOF 檔案大小相關的狀態

> truncate 成功後，程式僅將檔案描述子 seek 到結尾，但未更新 server 中可能記錄的 AOF 檔案大小或 offset 等狀態。這可能導致後續 AOF 寫入時發生錯誤或覆蓋。建議檢查是否有相關狀態需要更新。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## base-1:redis-8:1|redis-8#1

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行，候選管道 loc）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:1|redis-8#3

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2306`，距錨點 3 行，候選管道 loc）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:1|redis-8#4

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行，候選管道 loc）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:2|redis-8#1

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:2|redis-8#3

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:2|redis-8#4

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:3|redis-8#0

**GT**（rule）Unused variable causes compilation warning

> The code declares an unused variable 'unused_flag' that triggers a compilation warning, causing the build to fail when -Werror flag is enabled

GT 片段：`void hincrbyfloatCommand(client *c) { ⏎ long double value, incr; ⏎ long long ll; ⏎ robj *o;`

**finding**（`src/t_hash.c:2244`，距錨點 0 行，候選管道 loc）變數 unused_flag 宣告後未使用

> 在 hincrbyfloatCommand 中宣告了 `int unused_flag = 0;` 但從未使用。這可能是開發過程中的殘留，應移除。

finding 片段：`int unused_flag = 0;`

## base-1:tauri-1:1|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行，候選管道 ident）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行，候選管道 ident）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行，候選管道 ident）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行，候選管道 loc）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行，候選管道 ident）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:3|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 0 行，候選管道 loc）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 5 行，候選管道 loc）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 18 行，候選管道 ident）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 15 行，候選管道 ident）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#5

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 1 行，候選管道 loc）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-10:1|tauri-10#0

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行，候選管道 loc）inner_size 呼叫參數格式錯誤，可能導致編譯失敗

> 在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這在 Rust 中可能被解析為兩個獨立的 token，導致編譯錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## base-1:tauri-10:1|tauri-10#2

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行，候選管道 loc）inner_size 呼叫參數格式錯誤，可能導致編譯失敗

> 在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這在 Rust 中可能被解析為兩個獨立的 token，導致編譯錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

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

## base-1:tauri-10:3|tauri-10#0

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行，候選管道 loc）position 呼叫參數格式不一致

> 在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，雖然這在 Rust 中不會導致編譯錯誤，但與專案中其他程式碼的風格不一致。建議改為 `self.window_builder.position(position.x, position.y);`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## base-1:tauri-10:3|tauri-10#2

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行，候選管道 loc）position 呼叫參數格式不一致

> 在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，雖然這在 Rust 中不會導致編譯錯誤，但與專案中其他程式碼的風格不一致。建議改為 `self.window_builder.position(position.x, position.y);`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## base-1:tauri-11:1|tauri-11#3

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行，候選管道 loc）條件判斷邏輯反轉可能導致版本解析錯誤

> 原本的條件 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。這會使得當 lock 檔存在且 crate_lock_packages 非空時才進入鎖定版本解析，否則會回退到其他邏輯。若原本意圖是「當 lock 檔存在但找不到對應套件時才回退」，則此變更可能導致在 lock 檔存在且套件存在時仍使用鎖定版本，但若套件不存在則可能錯誤地使用其他來源。需要確認此變更是否為修正既有 bug，還是引入新問題。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## base-1:tauri-11:2|tauri-11#1

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行，候選管道 loc）鏡像 URL 處理方式變更可能導致錯誤網址

> 原本 `generate_github_mirror_url_from_base` 會將 `cdn` 的 path 設為 `github_url`，現在直接回傳 `cdn.to_string()`。這可能導致鏡像網址不再包含原始 GitHub URL 的路徑，使得下載失敗或指向錯誤資源。需要確認此變更是否為預期行為，並驗證鏡像功能是否仍正常運作。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## base-1:tauri-11:3|tauri-11#2

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行，候選管道 loc）直接使用 ureq::get 可能未套用平台憑證設定

> 在 `download_webview2_offline_installer` 中，直接呼叫 `ureq::get(url)` 而非使用 `base_ureq_agent()`，這可能導致此請求未使用系統憑證，與 PR 目的不一致。建議改用 `base_ureq_agent().get(url)` 以確保一致性。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## base-1:tauri-12:1|tauri-12#0

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:1|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行，候選管道 loc）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:1|tauri-12#3

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:1|tauri-12#4

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:2|tauri-12#0

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行，候選管道 loc）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-12:2|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行，候選管道 ident）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-12:2|tauri-12#3

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行，候選管道 loc）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-12:2|tauri-12#4

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行，候選管道 loc）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-13:1|tauri-13#3

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行，候選管道 loc）notarize_inner 中 map_or 的條件邏輯可能反轉

> 在 `notarize_inner` 函式中，原本的 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。

此變更會影響當 `status` 為 `None` 時的行為：
- 舊邏輯：若 `wait` 為 false，則 `map_or` 回傳 true（因為 `!wait`），因此會進入 if 區塊並印出 "Notarizing" 訊息。
- 新邏輯：若 `wait` 為 false，則 `map_or` 回傳 false，因此不會進入 if 區塊。

這可能導致在非等待模式下，即使 notarization 尚未完成，也不會印出 "Notarizing" 訊息，進而影響使用者體驗或後續流程。

建議確認此變更是否為預期行為，並考慮是否應保留原邏輯或調整條件。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## base-1:tauri-13:2|tauri-13#2

**GT**（func）Swapped source and destination in ditto archive command

> The arguments to the ditto command are reversed: zip_path appears before app_bundle_path, when ditto expects the source (app_bundle_path) before the destination (zip_path). This will cause ditto to fail when attempting to create the notarization archive, as it tries to compress a non-existent zip file into the app bundle directory. The command format should be 'ditto -c -k --keepParent --sequesterRsrc <source> <destination>', but the current order attempts '<destination> <source>', breaking the entire notarization workflow.

GT 片段：`let zip_args = vec![ ⏎ "-c", ⏎ "-k", ⏎ "--keepParent",`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行，候選管道 model_line）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## base-1:tauri-13:2|tauri-13#7

**GT**（rule）Use of expect() for fallible PathBuf-to-str conversion

> The code uses `.to_str().expect(...)`, which will panic on non-UTF8 paths. The rule requires fallible operations to return/propagate `Result` instead of panicking via `expect`/`unwrap`.

GT 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行，候選管道 model_line）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## base-1:tauri-13:3|tauri-13#0

**GT**（rule）Error enum doesn't use thiserror

> The rule requires custom error enums to use #[derive(thiserror::Error)] with #[error(...)] attributes, but this Error enum manually implements Display and Error traits instead of using thiserror

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 38 行，候選管道 ident）手動實作 Error trait 可能遺漏 source 方法

> 錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## base-1:tauri-13:3|tauri-13#1

**GT**（func）Missing error source for FailedToEncodeDER variant

> The Error::source() implementation is missing a case for Error::FailedToEncodeDER, which wraps an std::io::Error. This breaks error chain propagation when DER encoding fails. Callers using error context or debugging tools that traverse the error chain will lose the underlying IO error information, making it difficult to diagnose encoding failures. The original PR explicitly added source() support for this variant in the thiserror migration, but this manual implementation omits it.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行，候選管道 loc）手動實作 Error trait 可能遺漏 source 方法

> 錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## base-1:tauri-13:3|tauri-13#5

**GT**（func）Missing error source for Plist variant breaks error chain

> The Error::source() implementation is missing a case for Error::Plist, which wraps a plist::Error. This breaks error chain propagation when plist parsing or writing fails. The Plist variant is used for reading and writing application configuration files and provisioning profiles, making it one of the most commonly encountered errors. Without proper error source propagation, debugging tools and error context mechanisms lose access to the underlying plist parsing errors, making it difficult to diagnose configuration file issues.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行，候選管道 loc）手動實作 Error trait 可能遺漏 source 方法

> 錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## base-1:tauri-2:1|tauri-2#0

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行，候選管道 ident）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-1:tauri-2:1|tauri-2#2

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行，候選管道 loc）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-1:tauri-2:1|tauri-2#4

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行，候選管道 ident）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-1:tauri-2:2|tauri-2#1

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行，候選管道 loc）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## base-1:tauri-2:2|tauri-2#3

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行，候選管道 loc）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## base-1:tauri-3:1|tauri-3#1

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行，候選管道 loc）TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤

> 在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但升級後改為使用 `ConfigError::FormatJson`，並將錯誤轉為字串後包裝成 `serde_json::Error`。這會導致錯誤類型不正確，使用者將看到誤導的錯誤訊息（例如「JSON 格式錯誤」而非「TOML 格式錯誤」），且可能丟失錯誤的結構化資訊（如行號、欄位）。建議保留 `ConfigError::FormatToml` 變體，並直接傳遞 `toml::de::Error`。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## base-1:tauri-3:2|tauri-3#0

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行，候選管道 ident）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-1:tauri-3:2|tauri-3#2

**GT**（func）Case mismatch between BundleType serialization and deserialization for Flatpak

> The Display implementation for BundleType::Flatpak returns "Flatpak" with capital 'F', while the Deserialize implementation expects lowercase "flatpak". This creates a serialization round-trip bug where serializing a Flatpak bundle type and then deserializing it will fail. Any code that serializes bundle configurations to strings (for CLI output, config files, or API responses) and then attempts to parse them back will encounter deserialization errors. This inconsistency breaks the expected behavior that Display and Deserialize should be compatible with each other.

GT 片段：`impl Display for BundleType { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ write!( ⏎ f,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 0 行，候選管道 loc）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-1:tauri-3:2|tauri-3#3

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行，候選管道 ident）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-1:tauri-4:1|tauri-4#0

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 24 行，候選管道 ident）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-1:tauri-4:1|tauri-4#1

**GT**（func）Incorrect field path for extracting original bundle identifier

> The code attempts to extract the original identifier from the 'bundle' field instead of the root-level 'identifier' field. Since 'bundle' is an object (not a string), the `.as_str()` call will always fail, causing `original_identifier` to always be None. This breaks the ability to track and report which config file overwrites the bundle identifier, as the `find_bundle_identifier_overwriter()` method relies on comparing against the original identifier value.

GT 片段：`let original_identifier = config ⏎ .as_object() ⏎ .and_then(|config| config.get("bundle")) ⏎ .and_then(|id| id.as_str())`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 0 行，候選管道 loc）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-1:tauri-4:1|tauri-4#4

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 23 行，候選管道 ident）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-1:tauri-4:2|tauri-4#2

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行，候選管道 loc）條件判斷從 OR 改為 AND，導致 JSON 設定檔不再進行驗證

> 原本的條件是當副檔名為 `json` 或 `json5` 時進行驗證，但改為 AND 後，只有副檔名同時為 `json` 和 `json5`（不可能）才會驗證，實際上完全停用了驗證。這會讓所有 JSON 設定檔跳過 schema 驗證，可能導致錯誤的設定被接受。請改回 OR 邏輯。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## base-1:tauri-4:3|tauri-4#3

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行，候選管道 loc）`merge_with` 不再合併設定，而是儲存擴充資料，可能破壞合併功能

> 原本的程式碼會將 `merge_config` 合併到 `config_metadata.inner` 中，但此變更改為將 `merge_config` 存入 `extensions`。這可能導致合併功能失效，影響依賴此行為的呼叫者。請確認此變更的意圖，若需保留合併行為，應保留原本的合併邏輯。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## base-1:tauri-5:1|tauri-5#4

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行，候選管道 loc）`Dirs` 持有 `&'static Path` 可能導致生命週期問題

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但其實際指向的 `PathBuf` 儲存在 `OnceLock` 中。雖然 `OnceLock` 的內容在程式結束前不會被釋放，因此生命週期上可行，但這會造成記憶體永遠無法回收，且若未來改為非靜態儲存，將導致 dangling reference。建議改為持有 `PathBuf` 或使用 `Arc<Path>`，以避免潛在的生命週期問題。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## base-1:tauri-5:3|tauri-5#2

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 8 行，候選管道 ident）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## base-1:tauri-5:3|tauri-5#5

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 18 行，候選管道 ident）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## base-1:tauri-6:1|tauri-6#1

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行，候選管道 ident）無 listener 且 WebView 無法回上一頁時，直接呼叫 activity.onBackPressed() 可能導致 Activity 意外關閉

> 在 `handleOnBackPressed` 中，當 `!hasListener(BACK_BUTTON_EVENT)` 且 `webView?.canGoBack() != true` 時，會執行 `this@AppPlugin.activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是關閉 Activity。如果開發者沒有註冊 listener，使用者按下返回鍵就會直接退出應用程式，這可能不是預期的行為（例如應用程式想要攔截返回鍵但尚未設定 listener）。建議改為不執行任何動作，或提供明確的 API 讓開發者控制是否退出。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## base-1:tauri-6:2|tauri-6#1

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行，候選管道 ident）callback 的 isEnabled 狀態管理可能導致返回鍵失效

> 在 `handleOnBackPressed` 中，當沒有 listener 且 WebView 無法回上一頁時，會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再設回 `true`。然而，`activity.onBackPressed()` 可能會觸發 Activity 的銷毀或暫停，此時 callback 可能已被移除，重新設為 `true` 可能無效或造成記憶體洩漏。此外，如果 `activity.onBackPressed()` 拋出例外，`isEnabled` 將永遠保持 `false`，導致後續返回鍵完全失效。建議使用 try-finally 確保狀態恢復，或避免直接呼叫 `onBackPressed()`。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## base-1:tauri-7:1|tauri-7#1

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:52`，距錨點 0 行，候選管道 loc）generate_github_alternative_url 忽略替代 URL，可能導致下載失敗

> 在 `generate_github_alternative_url` 函式中，原本應回傳替代 URL（`alt_url`），但修改後改為回傳原始 URL（`url.to_owned()`）。這會使函式失去備援功能：當原始 GitHub URL 無法存取時，原本設計的鏡像站或替代來源將不會被使用，可能導致下載失敗。

**失敗情境**：當使用者位於無法直接存取 GitHub 的環境（例如某些地區或企業網路），且設定了 GitHub 鏡像站時，此函式會忽略鏡像 URL，仍嘗試從原始 GitHub 下載，導致建置工具下載失敗。

**建議**：確認此修改是否為預期行為。若需保留備援機制，應回傳 `alt_url`；若因其他原因需使用原始 URL，請在 PR 描述中說明理由。

finding 片段：`.map(|_alt_url| { ⏎ ( ⏎ ureq::Agent::config_builder() ⏎ .user_agent(BUNDLER_USER_AGENT)`

## base-1:tauri-7:2|tauri-7#0

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:99`，距錨點 0 行，候選管道 loc）移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 條件可能影響跨平台行為

> 原本 `HashAlgorithm::Sha256` 僅在 Windows 上啟用，現在移除條件編譯後，所有平台皆可使用 Sha256。這可能是為了修正跨平台雜湊驗證問題，但需確認在其他平台（如 Linux、macOS）上使用 Sha256 是否會造成行為變更或與既有邏輯衝突。

**建議**：確認此變更是否為預期，並檢查是否有其他程式碼依賴此條件編譯。

finding 片段：`pub enum HashAlgorithm { ⏎ Sha256, ⏎ Sha1, ⏎ }`

## base-1:tauri-8:1|tauri-8#1

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行，候選管道 loc）MouseButtonState 的 From 實作將 Up/Down 對應反轉

> 在 `From<tray_icon::MouseButtonState>` 的實作中，原本的對應是 `Up => Up`、`Down => Down`，但此 PR 將其改為 `Up => Down`、`Down => Up`。這會導致所有從 `tray_icon` 轉換而來的滑鼠狀態都被反轉，例如使用者放開滑鼠時會被回報為按下。此變更與 PR 主旨（derive default）無關，且明顯是邏輯錯誤。

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## base-1:tauri-9:1|tauri-9#1

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行，候選管道 loc）cli.js 版本與 tauri-cli crate 版本不一致

> metadata-v2.json 中的 cli.js 版本從 2.8.1 改為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 升到 2.8.1。這可能導致發布流程中 npm 套件與 Rust crate 版本不匹配，或使用者安裝時取得錯誤的 CLI 版本。請確認此處是否應為 2.8.1，或 tauri-cli 應升到 2.8.2。

finding 片段：`"version": "2.8.2",`
