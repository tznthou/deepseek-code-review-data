# 盲標單 7：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part7.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0565

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:43`，距錨點 0 行）布林邏輯變更可能反轉搜尋模式判斷

> 在 `useMarketplaceSearchMode` 中，原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在改為 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。這會導致當 `searchMode` 為 `null` 或 `undefined` 時，判斷結果完全相反：原本不在集合中的分類會被視為搜尋模式，現在變成在集合中的分類才會被視為搜尋模式。這很可能造成 UI 顯示錯誤（例如搜尋模式指示燈、列表行為）。請確認此變更是否為預期，若非預期請恢復 `!`。

finding 片段：`|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`

## P0566

**GT**（rule）Logger uses direct logging.getLogger

> The rule requires logger instances to be created using the pattern `logger: "logging.Logger" = get_logger("module_name")` but this code uses direct `logging.getLogger()` call without proper type annotation or using the standard get_logger utility

GT 片段：`import logging ⏎ logger = logging.getLogger(__name__)`

**finding**（`src/prefect/server/events/triggers.py:73`，距錨點 0 行）logger 取得方式不一致，可能導致日誌層級設定失效

> 原本使用 `get_logger(__name__)` 取得 logger，現在改為 `logging.getLogger(__name__)`。這可能導致日誌層級設定不一致，因為 `get_logger` 可能套用了自訂的 logging 設定。建議維持使用 `get_logger` 以保持一致性。

finding 片段：`logger = logging.getLogger(__name__)`

## P0567

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0568

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:4`，距錨點 0 行）未使用的常數 UNUSED_CONSTANT

> 新增的常數 `UNUSED_CONSTANT` 沒有被任何地方使用，且其名稱暗示這是故意留下的未使用程式碼。這會觸發 lint 警告（如 no-unused-vars），並增加不必要的維護負擔。

**建議修法**：移除該常數及其註解。

finding 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

## P0569

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 Remarks 指派給 Summary 可能改變既有行為

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。若既有使用者依賴 Remarks 出現在 Description 欄位，此變更會造成 breaking change。建議確認此變更是否為預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## P0570

**GT**（func）Incorrect field path for extracting original bundle identifier

> The code attempts to extract the original identifier from the 'bundle' field instead of the root-level 'identifier' field. Since 'bundle' is an object (not a string), the `.as_str()` call will always fail, causing `original_identifier` to always be None. This breaks the ability to track and report which config file overwrites the bundle identifier, as the `find_bundle_identifier_overwriter()` method relies on comparing against the original identifier value.

GT 片段：`let original_identifier = config ⏎ .as_object() ⏎ .and_then(|config| config.get("bundle")) ⏎ .and_then(|id| id.as_str())`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 0 行）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## P0571

**GT**（func）Incorrect comparison logic causes false negatives when comparing slot ranges

> The slotRangeArrayIsEqual function checks if the number of ranges are equal before normalizing and merging adjacent ranges. This causes the function to incorrectly return false (0) when comparing two slot range arrays that represent the same slots but have different numbers of ranges before merging. For example, comparing [1000-1001, 1002-1003] (2 ranges) with [1000-1003] (1 range) will return false even though they represent the same slots after merging. This breaks the task lookup functionality in asmLookupTaskBySlotRangeArray, preventing correct task identification when slot ranges are specified in different but equivalent formats.

GT 片段：`int slotRangeArrayIsEqual(slotRangeArray *slots1, slotRangeArray *slots2) { ⏎ if (slots1->num_ranges != slots2->num_ranges) return 0; ⏎ slotRangeArraySortAndMerge(slots1); ⏎ slotRangeArraySortAndMerge(slots2);`

**finding**（`src/cluster.c:1855`，距錨點 21 行）`slotRangeArraySortAndMerge` 未處理重疊範圍

> 註解明確指出「Overlapping ranges are not merged.」，但若輸入包含重疊範圍（例如 100-200 和 150-250），合併後仍會保留兩個範圍，且後續的驗證會偵測到重疊並回報錯誤。這可能是預期行為，但建議在函式中明確處理或至少記錄此情況，以避免未來誤用。

finding 片段：`/* Sort slot ranges by start slot and merge adjacent ranges. ⏎ * Adjacent means: prev.end + 1 == next.start. ⏎ * e.g. 1000-2000 2001-3000 0-100  =>  0-100 1000-3000 ⏎ *`

## P0572

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）日期計算可能因時區或時序產生 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並取 `Math.ceil`。若 `created_at` 是 UTC 儲存，而伺服器時區非 UTC，可能導致天數計算偏差。此外，若第一封信是在當天稍晚發送，`Math.ceil` 可能將未滿一天算成一天。建議使用 UTC 日期或明確的日界線計算。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0573

**GT**（rule）Non-static internal helper function exported as global symbol

> asmCountKeysInSlots is introduced as a file-local helper (not declared in any header and used only within src/cluster_asm.c in this diff), but it is declared without the 'static' keyword, making it globally visible and violating the encapsulation rule for internal helpers.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1012`，距錨點 0 行）`asmCountKeysInSlots` 可能造成大量迴圈與效能問題

> `asmCountKeysInSlots` 會針對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slot（例如整個 hash slot 空間 0-16383），則會執行 16384 次函式呼叫。雖然 `kvstoreDictSize` 本身可能只是 O(1) 的查詢，但大量的函式呼叫仍可能造成不必要的效能負擔，特別是在日誌記錄或任務啟動時頻繁呼叫。

建議：
- 評估是否有更有效率的方式取得 key 數量，例如直接從 `kvstore` 取得總數，或使用批次 API。
- 若無法避免，考慮加入快取或限制呼叫頻率。

finding 片段：`unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎  ⏎ unsigned long long key_count = 0;`

## P0574

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行）scheduling.init() 呼叫方式變更可能導致 API URL 遺失

> 原本 `scheduling.init()` 會傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，但修改後改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確運作。請確認 `scheduling.init()` 是否已有其他方式取得 API URL，或此變更是否為有意為之。

finding 片段：`scheduling.init(),`

## P0575

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行）使用 malloc 而非 zmalloc 配置 cluster_slot_stats

> 在 clusterCommonInit() 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用標準 malloc，而原本在 server.c 中使用 zmalloc。zmalloc 是 Redis 的記憶體配置封裝，提供記憶體統計與 OOM 處理。若改用 malloc，可能導致記憶體統計不正確，且在記憶體不足時行為不一致。建議改回 zmalloc。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0576

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 0 行）JWT 驗證改為 decode 導致簽章未驗證

> `_isJWTExpired` 從 `jwt.verify` 改為 `jwt.decode`，這會跳過簽章驗證。攻擊者可以偽造一個帶有未來 `exp` 的 token，通過過期檢查，進而使用無效的 token 存取 Tinybird API。建議改回 `jwt.verify`，或在 `_isJWTExpired` 中明確驗證簽章。

finding 片段：`const decoded = jwt.decode(token);`

## P0577

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## P0578

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有除法或轉換可能出錯）。建議回傳 `emailCount` 或一個明確的常數（如 `Number.MAX_SAFE_INTEGER`），並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0579

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0580

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:18`，距錨點 0 行）require 陳述式缺少分號

> `const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list');` 和 `const MagicLink = require('../../lib/magic-link/magic-link');` 保留了分號，但與前面無分號的陳述式不一致。

finding 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

## P0581

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行）移除排序可能改變既有 API 行為

> `getOutputRecurringSeatedBookings` 原本會依 `start` 時間排序回傳的預訂，此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳順序不穩定，影響依賴排序的客戶端。若無明確理由，建議保留排序。

finding 片段：`return transformed;`

## P0582

**GT**（func）Missing handleClose call in single-select mode prevents search input cleanup

> In the unselected options section for single-select mode, the code calls setOpen(false) but fails to call handleClose(), unlike the multiselect path which properly calls handleClose() when autoCloseOnSelect is enabled. This means when a user selects a single option, the popover closes but the search input state is never cleared, causing the next time the popover opens to show stale search results and filtered options from the previous interaction. The handleClose() function is responsible for clearing the search input and triggering the onClose callback, both of which are now skipped in single-select scenarios.

GT 片段：`} else { ⏎ onChange([option.value] as T[]); ⏎ setOpen(false); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1271`，距錨點 4 行）autoCloseOnSelect 在 multiselect 中可能造成非預期關閉

> 在另一個 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { handleClose(); }`，但此處呼叫的 `handleClose` 會同時重置搜尋輸入並呼叫 `onClose`，可能導致 popover 關閉且搜尋被清空。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ handleClose(); ⏎ }`

## P0583

**GT**（func）Audit trail captures wrong previous status for rejected recurring bookings

> When rejecting recurring bookings, the system queries the booking status AFTER updating them to REJECTED rather than BEFORE. This causes the audit trail to incorrectly show the previous status as REJECTED instead of PENDING. The bug occurs because updatedRecurringBookings is queried after the updateMany operation completes, so all bookings already have status REJECTED. This results in audit logs showing nonsensical transitions like REJECTED→REJECTED, breaking the audit trail and making it impossible to determine the actual state change that occurred during rejection.

GT 片段：`const updatedRecurringBookings = await prisma.booking.findMany({ ⏎ where: { ⏎ uid: { ⏎ in: unconfirmedRecurringBookings.map((booking) => booking.uid),`

**finding**（`packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432`，距錨點 0 行）recurring reject 流程中 oldStatus 取得時機錯誤

> 在 recurring reject 流程中，先以 `prisma.booking.updateMany` 將所有符合條件的 booking 更新為 `REJECTED`，之後才查詢 `updatedRecurringBookings` 並將其 `status` 作為 `oldStatus`。此時查詢到的狀態已經是 `REJECTED`，導致 audit log 的 `oldStatus` 錯誤。

建議在更新前先查詢並保存原始狀態，例如：
```ts
const unconfirmedRecurringBookings = await prisma.booking.findMany({ ... });
const oldStatuses = new Map(unconfirmedRecurringBookings.map(b => [b.uid, b.status]));
await prisma.booking.updateMany({ ... });
rejectedBookings = unconfirmedRecurringBookings.map(b => ({ uid: b.uid, oldStatus: oldStatuses.get(b.uid)! }));
```

finding 片段：`const updatedRecurringBookings = await prisma.booking.findMany({ ⏎ where: { ⏎ uid: { ⏎ in: unconfirmedRecurringBookings.map((booking) => booking.uid),`

## P0584

**GT**（rule）Cross-field validation uses field validator

> The rule requires cross-field validation to use @model_validator decorator, but the code uses @field_validator which accesses unvalidated fields via info.data, causing order-dependent validation issues

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行）validator 依賴欄位順序，可能導致驗證失敗

> `validate_automation_triggered_event_id` 使用 `info.data.get("triggering_event")` 檢查 triggering_event 是否存在，但 Pydantic v2 的 `info.data` 僅包含已驗證的欄位，若 `automation_triggered_event_id` 在 `triggering_event` 之前定義，則 `info.data` 中可能尚無 triggering_event，導致誤判。建議改用 `info.data.get("triggering_event", None) is not None` 或使用 `model_validator`。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## P0585

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）滾動索引超出範圍

> 在 `createTabScrollBehavior` 中，當沒有選取分頁時，回傳的 `toIndex` 使用了 `state.tabs.count`，但陣列索引是從 0 開始，因此最後一個有效索引是 `count - 1`。這會導致 `IndexPath(row:section:)` 使用無效的 row，可能造成滾動到錯誤位置或當機。

建議改為 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0586

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行）start_execution 在 enqueue 之前呼叫可能導致狀態不一致

> 在 `enqueue_node` 之前呼叫 `start_execution` 可能造成節點狀態被標記為執行中，但尚未進入佇列。若後續 `enqueue_node` 失敗或拋出例外，節點會停留在執行中狀態而無法被正確處理。建議確認 `start_execution` 的實作是否具冪等性，或調整呼叫順序。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0587

**GT**（rule）Force unwrap of URL initializer in tests (second occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0588

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:370`，距錨點 0 行）Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲

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

## P0589

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 10 行）hasInitializedJsComponents 全域旗標可能導致初始化被跳過

> `hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## P0590

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）新增 ENABLE_WEBHOOKS 環境變數開關可能意外停用所有 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，webhooks 會正常發送；但若設定為 "false"，則所有 webhook 都會被停用。這可能影響所有依賴 webhook 的功能，且此變更未在 PR 描述中提及。建議確認此環境變數的部署設定，並考慮使用更明確的名稱或預設值。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0591

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）條件判斷變更可能影響無 key 命令的處理

> 原本 `else if (num_keys > 0)` 只在有 key 時檢查 cross-slot，現在改為 `else if (num_keys >= 0)`，這會讓 `num_keys == 0` 的命令也進入檢查。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為無 key 命令不會有 cross-slot），則會設定錯誤。但更可能的是，原本 `num_keys == 0` 時會跳過此區塊，現在會執行，可能影響後續邏輯。

建議確認此變更是否必要，或改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

## P0592

**GT**（func）Unnecessary re-rendering on every parameter update with same display name

> The DisplayName component removed the check that prevents re-rendering when the display name hasn't changed (line 50-51). This means that every time SetParametersAsync is called with a changed expression (even if it results in the same display name), the component will trigger a render. This causes performance degradation in scenarios with frequent parameter updates, such as forms with dynamic field expressions, leading to unnecessary DOM updates and potential flickering in the UI.

GT 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ _displayName = newDisplayName;`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 0 行）參數未變更時不會重新渲染，可能導致顯示名稱過時

> 在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱並渲染。然而，如果 `For` 表達式相同，但目標屬性的顯示名稱可能因其他因素（例如資源檔變更、動態屬性變更）而改變，元件將不會更新。這可能導致顯示名稱與實際屬性不一致。建議在每次 `SetParametersAsync` 呼叫時都重新計算顯示名稱，或提供一種機制來強制更新。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## P0593

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:132`，距錨點 0 行）空值處理可能遺失原始資料

> 當輸入為空時，`handleJSONSchemaChange` 會將 `json_schema` 設為 `undefined`，這可能導致使用者清除欄位後無法恢復先前值。建議確認此行為是否符合預期，或改為儲存空字串。

finding 片段：`if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined) ⏎ return null ⏎ }`

## P0594

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:231`，距錨點 0 行）輪詢迴圈中先 sleep 再檢查狀態，可能延遲回傳

> 原本先檢查狀態再 sleep，修改後先 sleep 再檢查。這會導致即使 flow run 已完成，仍會等待一個 `poll_interval` 才回傳。若 `poll_interval` 較大，可能造成不必要的延遲。建議先檢查狀態再 sleep。

finding 片段：`await anyio.sleep(poll_interval)`

## P0595

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）骨架視圖約束可能錯誤：toolbar.leadingAnchor 應約束到 leftSkeletonAddressBar.trailingAnchor

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor` 約束到 `leftSkeletonAddressBar.trailingAnchor`，但此 PR 將其改為 `rightSkeletonAddressBar.trailingAnchor`。這可能導致 toolbar 的左側與右側骨架視圖的右側對齊，造成佈局錯亂。請確認此變更是否為預期行為，若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0596

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43`，距錨點 0 行）後綴比對可能區分大小寫

> Prisma 的 endsWith 預設可能區分大小寫，取決於資料庫 collation。若 externalId 可能包含大寫字母，則過濾可能失效。建議使用不區分大小寫的比對，例如使用 mode: 'insensitive'（若資料庫支援）或先將 externalId 轉為小寫再比對。

finding 片段：`NOT: { externalId: { endsWith: suffix } }`

## P0597

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:98`，距錨點 0 行）移除 userSelect 中的 locale 欄位可能導致取消流程錯誤

> `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但在 `handleCancelBooking` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。若 `findByIdOrThrow` 使用此 `userSelect`，回傳的 organizer 物件將缺少 `locale`，導致 `organizer.locale` 為 `undefined`，可能觸發錯誤或使用錯誤的預設語言。

建議：確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 `locale` 則應保留該欄位，或改用其他方式取得。

finding 片段：`createdDate: true, ⏎ trialEndsAt: true, ⏎ completedOnboarding: true, ⏎ timeFormat: true,`

## P0598

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:53`，距錨點 0 行）sortHosts 函式在移動時被意外修改，priority 比較方向反轉

> 在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，原本的 `return priorityB - priorityA;` 被改成了 `return priorityA - priorityB;`（在 `isRRWeightsEnabled` 為 true 且權重相等時）。這會反轉優先權排序，可能導致主機選擇錯誤。

**失敗情境**：當啟用 RR 權重且兩個主機權重相同時，優先權較低（數值較大）的主機會被排在前面，違反預期。

**建議**：將該行改回 `return priorityB - priorityA;`，與原始邏輯一致。

finding 片段：`return priorityA - priorityB;`

## P0599

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能接受無效資料

> 此函式僅檢查 input 是否為物件且 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）或 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 zod 或其他 schema 驗證庫完整驗證所有欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0600

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0601

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行）使用子字串比對判斷路徑前綴，可能誤判

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，若 `path` 中包含 bucket_folder 但並非前綴（例如 `path = "myresults/abc"` 且 `bucket_folder = "results/"`），會錯誤地視為已前綴而直接返回，導致路徑未正確解析。應改為檢查 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0602

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:264`，距錨點 0 行）member 可能為 null 時存取 member.expertise 可能拋出錯誤

> 在 `editor.setEditable(!!member?.expertise && progress !== 'sending')` 中，若 `member` 為 null，`member?.expertise` 會回傳 undefined，`!!undefined` 為 false，因此不會拋出錯誤。但此處邏輯與原本使用 `memberName` 不同，可能導致編輯器在成員沒有 expertise 時被設為不可編輯，即使成員有名字。建議確認此行為是否符合預期，或改用 `member?.name` 或同時檢查兩者。

finding 片段：`editor.setEditable(!!member?.expertise && progress !== 'sending');`

## P0603

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 40 行）缺少對新功能的測試

> 新增的自動遞增邏輯沒有對應的單元測試或整合測試。建議添加測試覆蓋以下情境：首次建置、正常遞增、檔案不存在、檔案格式錯誤、並行建置（如果實作鎖定）等。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0604

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 8 行）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0605

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 10 行）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0606

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行）bucket_folder 檢查過於寬鬆，可能跳過必要的前綴處理

> 在 `_resolve_path` 中，使用 `if self.bucket_folder and self.bucket_folder in path:` 來判斷路徑是否已包含 bucket_folder。這個檢查只要路徑中任何位置出現 bucket_folder 字串就會成立，即使 bucket_folder 出現在路徑中間或檔名中，也會錯誤地直接返回原始路徑，導致最終儲存路徑缺少必要的前綴。

例如，若 bucket_folder 為 `results/`，而傳入路徑為 `myresults/file.txt`，則 `self.bucket_folder in path` 為 True，函式會直接返回 `myresults/file.txt`，但正確行為應是加上前綴成為 `results/myresults/file.txt`。

建議改為檢查路徑是否以 bucket_folder 開頭（例如使用 `path.startswith(self.bucket_folder)`），或使用 `PurePosixPath` 進行更精確的比對。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0607

**GT**（rule）MSTest attribute in xUnit project

> The rule requires test projects to consistently use the xUnit framework, but the test method uses MSTest's [TestMethod] attribute instead of xUnit's [Fact] attribute

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException()`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 2 行）AppContext.SetSwitch 參數值可能相反

> 在測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 中，原本設定 `DisableThrowNavigationException` 為 `false`，但此 PR 改為 `true`。若測試目的是驗證「不拋出例外」的行為，設定為 `true` 可能導致測試情境與預期相反，進而無法正確驗證。請確認此變更是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0608

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 0 行）Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證

> 當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0609

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:129`，距錨點 8 行）Semaphore 僅在 event_type 為 None 時使用，可能無法涵蓋所有啟動事件

> Semaphore 僅在 `event_type is None` 的分支中使用，但啟動時可能還有其他事件類型（如 `ADDED`）也需要限制並發。若啟動時大量 `ADDED` 事件同時觸發，仍可能造成 API 過載。建議確認啟動期間所有事件類型都應受 semaphore 限制。

finding 片段：`if event_type is None: ⏎ if orchestration_client is None: ⏎ raise RuntimeError("Orchestration client not initialized") ⏎ if _startup_event_semaphore is None:`

## P0610

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行）buildInviteLink 條件判斷反轉，導致連結格式錯誤

> 原本的邏輯是：如果不是組織情境（`!isOrgContext`），直接回傳 `teamInviteLink`；否則（組織情境）會加上 getting started 路徑。修改後變成：如果是組織情境（`isOrgContext`），直接回傳 `teamInviteLink`；否則（非組織情境）才加上 getting started 路徑。這與原本的意圖相反，可能導致非組織團隊的邀請連結錯誤地包含 getting started 路徑，而組織團隊的連結缺少該路徑。

**建議**：將條件改回 `if (!isOrgContext)`，或確認變數名稱與邏輯是否正確。

finding 片段：`if (isOrgContext) {`

## P0611

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0612

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含

> 在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0613

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107`，距錨點 0 行）輪詢失敗時自動停用 Bluesky 可能非預期

> 當輪詢達到最大次數時，程式碼會自動呼叫 `disableBlueskyMutation.mutateAsync()` 停用 Bluesky。這可能導致使用者在未明確同意的情況下被停用，且若停用失敗，錯誤未被處理。建議改為僅顯示錯誤訊息，讓使用者手動決定是否停用。

finding 片段：`toast.error('Something went wrong, please try again.'); ⏎  ⏎ await disableBlueskyMutation.mutateAsync(); ⏎ setLoading(false);`

## P0614

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0615

**GT**（func）Incorrect deployment filtering breaks full-name matching

> The deployment filtering logic checks `dep.name not in deployment_names` instead of checking `full_name not in deployment_names`. This causes the filter to incorrectly evaluate when users specify deployment names in 'flow-name/deployment-name' format. When a user provides a full deployment name like 'my-flow/production', the code checks if 'production' (the short name) is in the list containing 'my-flow/production', which fails, causing the deployment to enter the fallback matching logic unnecessarily. This breaks the fast-path check and could lead to incorrect filtering behavior where deployments are included or excluded inappropriately.

GT 片段：`# If filtering by deployment name, check the full name matches ⏎ full_name = f"{flow_name}/{dep.name}" ⏎ if deployment_names and dep.name not in deployment_names: ⏎ # Only include if the full name matches (filter was by name parts)`

**finding**（`src/prefect/_sdk/fetcher.py:397`，距錨點 0 行）部署名稱過濾邏輯變更可能改變行為

> 原本的過濾條件是 `full_name not in deployment_names`，現在改為 `dep.name not in deployment_names`。這可能導致當使用者指定完整名稱（如 `flow-name/deployment-name`）時，過濾邏輯無法正確匹配，因為 `dep.name` 只包含部署名稱，不包含 flow 名稱。需要確認此變更是否為預期，並確保過濾行為符合文件描述。

finding 片段：`if deployment_names and dep.name not in deployment_names:`

## P0616

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47`，距錨點 0 行）BackgroundQueueSize 驗證條件變更可能禁止 0 值

> 原本的驗證條件 `value < 0` 允許 0（表示無佇列），但變更後 `value <= 0` 會拒絕 0。若原本有使用者設定 0 來停用佇列，此變更將導致例外。建議確認 0 是否為有效值，若不是，應更新文件說明；若是，應維持原本的驗證。

finding 片段：`if (value <= 0)`

## P0617

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 0 行）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## P0618

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:498`，距錨點 0 行）取消後續預訂時使用 bookingToDelete.startTime 作為 gte 條件可能不正確

> 在 `cancelSubsequentBookings` 為 true 時，原本使用 `new Date()` 作為 `gte` 條件，現在改為 `bookingToDelete.startTime`。這可能導致取消的範圍包含過去已完成的預訂，或遺漏了在 `bookingToDelete.startTime` 之後但已過去的預訂。請確認此變更是否符合業務邏輯。

finding 片段：`const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date();`

## P0619

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:231`，距錨點 16 行）輪詢迴圈中先 sleep 再檢查狀態，可能延遲回傳

> 原本先檢查狀態再 sleep，修改後先 sleep 再檢查。這會導致即使 flow run 已完成，仍會等待一個 `poll_interval` 才回傳。若 `poll_interval` 較大，可能造成不必要的延遲。建議先檢查狀態再 sleep。

finding 片段：`await anyio.sleep(poll_interval)`

## P0620

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0621

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0622

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行）validateCreateScheduleInput 驗證不足，可能接受無效資料

> 此函式僅檢查 input 是否為物件且 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）或 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 zod 或其他 schema 驗證庫完整驗證所有欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0623

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 0 行）GTK 腳本存在性檢查邏輯反轉

> 原本的邏輯是「若檔案不存在，則下載並寫入」，但修改後變成「若檔案存在，則寫入內嵌內容」。這會導致：
1. 當檔案不存在時，不會建立該檔案，後續執行可能因缺少腳本而失敗。
2. 當檔案已存在時，會用內嵌內容覆蓋，可能破壞使用者自訂的腳本。

建議改回 `if !gtk.exists()` 的條件。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0624

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 24 行）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## P0625

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）條件判斷修正可能改變既有行為

> 原本條件為 `lock.is_some() && crate_lock_packages.is_empty()`，修改後為 `lock.is_some() && !crate_lock_packages.is_empty()`。這會反轉條件，可能導致在 lock 檔案存在但套件清單為空時，不再進入原本的處理邏輯，或在非空時進入原本不應執行的邏輯。

**失敗情境**：若 `crate_lock_packages` 為空且 lock 檔案存在，原本會執行某段程式碼，修改後將跳過；反之亦然。需確認此修正是否正確對應預期行為。

**建議**：驗證此條件修正是否為 bug fix，並確認所有呼叫路徑的行為符合預期。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0626

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:43`，距錨點 0 行）後綴可能包含萬用字元或特殊字元

> 後綴字串若包含 Prisma 的萬用字元（如 % 或 _），endsWith 可能將其視為萬用字元而非字面值。目前定義的後綴不包含這些字元，但未來新增時需注意。建議在文件中提醒或使用 escape 處理。

finding 片段：`NOT: { externalId: { endsWith: suffix } }`

## P0627

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）在迴圈內呼叫 flush，且 flush 為空實作

> `on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0628

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 6 行）新增的 Task.Yield() 可能造成登出流程的競態或延遲

> 在 `ProcessLogOut` 中，於取得驗證狀態前新增了 `await Task.Yield();`。這可能導致登出流程延遲，且若 `AuthenticationProvider.GetAuthenticationStateAsync()` 依賴某些同步狀態，可能引入競態。建議移除或提供明確理由。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎  ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

## P0629

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0630

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行）回傳的 token 與實際儲存的 token 不一致

> 在 `createInvite` 中，原本回傳的是隨機產生的 `token`，但現在改為回傳 `newToken.identifier`。`identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位不是真正的邀請 token，而 `inviteLink` 中使用的 token 仍是原始的隨機 token，造成兩者不一致。使用者若使用回傳的 `token` 進行驗證，將無法成功加入團隊。

**建議**：回傳原始的 `token` 變數，而不是 `newToken.identifier`。

finding 片段：`token: newToken.identifier,`

## P0631

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:102`，距錨點 0 行）日期過濾條件從「<」改為「<=」可能納入今天的郵件

> 原本使用 `created_at:<今天日期` 排除今天的郵件，但改為 `created_at:<=今天日期` 後，會包含今天建立的郵件。這可能導致 #getHighestCount 回傳今天的郵件數量，進而讓暖機上限膨脹，甚至造成無限成長。建議維持原本的 `<` 運算子，或明確排除今天的郵件。

finding 片段：`filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,`

## P0632

**GT**（func）Audit trail captures wrong previous status for rejected recurring bookings

> When rejecting recurring bookings, the system queries the booking status AFTER updating them to REJECTED rather than BEFORE. This causes the audit trail to incorrectly show the previous status as REJECTED instead of PENDING. The bug occurs because updatedRecurringBookings is queried after the updateMany operation completes, so all bookings already have status REJECTED. This results in audit logs showing nonsensical transitions like REJECTED→REJECTED, breaking the audit trail and making it impossible to determine the actual state change that occurred during rejection.

GT 片段：`const updatedRecurringBookings = await prisma.booking.findMany({ ⏎ where: { ⏎ uid: { ⏎ in: unconfirmedRecurringBookings.map((booking) => booking.uid),`

**finding**（`packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:468`，距錨點 22 行）reject 單筆 booking 時 oldStatus 取得時機錯誤

> 在非 recurring 的 reject 流程中，`rejectedBookings` 的 `oldStatus` 取自 `booking.status`，但此時 `booking` 物件已在稍早的 `prisma.booking.update` 中被更新為 `REJECTED`，因此 `oldStatus` 會是 `REJECTED` 而非原本的 `PENDING`。這會導致 audit log 中的狀態變更記錄錯誤（old 和 new 都是 REJECTED）。

建議在更新前先保存原始狀態，例如：
```ts
const oldStatus = booking.status;
await prisma.booking.update({ ... });
rejectedBookings = [{ uid: booking.uid, oldStatus }];
```

finding 片段：`rejectedBookings = [ ⏎ { ⏎ uid: booking.uid, ⏎ oldStatus: booking.status,`

## P0633

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行）validateStoredKeyConversion 函式未使用

> 新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。這可能是開發中的除錯程式碼，若無用途應移除，以免造成混淆。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) {`

## P0634

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行）使用 malloc 而非 zmalloc 配置 cluster_slot_stats

> 在 clusterCommonInit() 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用標準 malloc，而原本在 server.c 中使用 zmalloc。zmalloc 是 Redis 的記憶體配置封裝，提供記憶體統計與 OOM 處理。若改用 malloc，可能導致記憶體統計不正確，且在記憶體不足時行為不一致。建議改回 zmalloc。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0635

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:37`，距錨點 0 行）render_template 可能回傳 None，導致後續 len() 拋出 TypeError

> 在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 缺少 `'result'` 鍵，`rendered` 會是 `None`，函式直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，會拋出 `TypeError: object of type 'NoneType' has no len()`，且此例外未被捕捉，導致節點執行失敗且無明確錯誤訊息。建議在回傳前檢查 `rendered` 是否為 `None`，若為 `None` 則拋出 `TemplateRenderError`。

finding 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

## P0636

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題

> 原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

finding 片段：`emailAddressService.init(),`

## P0637

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:11`，距錨點 0 行）React Scan 載入失敗時回傳的元件可能導致渲染錯誤

> 在 `lazy` 的 `catch` 中回傳 `{ default: () => null }`，但 `ReactScan` 元件本身可能接受 props 或依賴 context。若 `ReactScan` 在渲染時需要特定 props 或 context，這個 fallback 元件可能無法滿足，導致錯誤。此外，`lazy` 的 factory 必須回傳一個 Promise，其 resolve 值必須是 `{ default: Component }`，此處符合，但 fallback 元件若被渲染且內部有 hook 或依賴，可能造成問題。建議改為回傳一個明確的 fallback 元件，或直接讓錯誤拋出並由 error boundary 處理。

finding 片段：`return { default: () => null }`

## P0638

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行）將 onActionTap 閉包內容包在 Task 中可能改變執行順序與錯誤處理

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使得 handleAction 的執行變成非同步，可能導致呼叫端預期的同步行為失效。例如，若 handleAction 內部有需要立即完成的狀態更新，或 completion 需要在特定時序被呼叫，延遲可能造成 UI 不一致。此外，Task 中未處理可能的錯誤（如 handleAction 拋錯），可能導致錯誤被吞掉。建議確認 handleAction 是否為非同步設計，或考慮使用 Task { @MainActor in ... } 並明確處理錯誤。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0639

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 1 行）config 值未驗證，可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，但未驗證其型別或內容。若 config 值為空字串、0、false 等 falsy 值，則條件為 false，不會建立 outbox；若為任意 truthy 值（例如 'false' 字串），則會建立 outbox。建議明確驗證該值是否為有效的 email 或布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0640

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同。

建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0641

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0642

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行）MouseButtonState 的 From 實作將 Up/Down 對應反轉

> 在 `From<tray_icon::MouseButtonState>` 的實作中，原本的對應是 `Up => Up`、`Down => Down`，但此 PR 將其改為 `Up => Down`、`Down => Up`。這會導致所有從 `tray_icon` 轉換而來的滑鼠狀態都被反轉，例如使用者放開滑鼠時會被回報為按下。此變更與 PR 主旨（derive default）無關，且明顯是邏輯錯誤。

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## P0643

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 3 行）AppContext.SetSwitch 參數值可能相反

> 在測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 中，原本設定 `DisableThrowNavigationException` 為 `false`，但此 PR 改為 `true`。若測試目的是驗證「不拋出例外」的行為，設定為 `true` 可能導致測試情境與預期相反，進而無法正確驗證。請確認此變更是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0644

**GT**（func）Lost `this` context in displayGuests mapping causes runtime error

> In the `getOutputBooking` method at line 171, the code passes `this.getDisplayEmail` directly to the `map` function without binding the `this` context. This causes a runtime error because when `getDisplayEmail` is invoked inside the `map` callback, `this` will be `undefined`, resulting in "Cannot read property 'replace' of undefined" or similar errors. The arrow function `(guest: string) => this.getDisplayEmail(guest)` was removed, which was necessary to preserve the `this` binding. This will break all bookings that have guests.

GT 片段：`if ( ⏎ bookingTransformed.bookingFieldsResponses?.guests && ⏎ Array.isArray(bookingTransformed.bookingFieldsResponses.guests) ⏎ ) {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169`，距錨點 0 行）displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## P0645

**GT**（func）Token caching stores entire object instead of token string

> In the getToken method, when caching the JWT token, the code now stores the entire tokenData object (containing both 'token' and 'exp' properties) instead of just extracting the token string. This causes the returned token structure to be malformed as {token: {token: string, exp: number}, exp: number} instead of the expected {token: string, exp: number}. This will break any consumers of the Tinybird API (like the /api/tinybird/token endpoint and stats/tinybird.js) that expect a string token value, causing authentication failures when making requests to Tinybird pipes.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）`_serverToken` 型態從字串改為物件，可能導致後續使用錯誤

> 在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token;` 將 token 字串存入 `_serverToken`，但現在改為 `this._serverToken = tokenData;`，存入的是整個物件。然而，`_isJWTExpired` 方法仍預期接收 token 字串（呼叫 `jwt.decode(token)`），且其他可能使用 `_serverToken` 的地方（如回傳給呼叫端）也可能預期是字串。這會導致型別不一致，可能造成執行時期錯誤或驗證失敗。

**失敗情境**：當 `_serverToken` 被當作字串使用時（例如傳給 `jwt.decode` 或直接回傳），會因為它是物件而拋出錯誤或產生非預期行為。

**建議**：維持 `_serverToken` 為 token 字串，另外儲存 exp 或其他必要資訊。例如：
```js
this._serverToken = tokenData.token;
this._serverTokenExp = tokenData.exp;
```

finding 片段：`this._serverToken = tokenData;`

## P0646

**GT**（func）JSON schema validation uses non-normalized value

> The validation logic for jsonObject type validates jsonSchemaValue instead of normalizedJsonSchema. This is problematic because normalizedJsonSchema is computed earlier and correctly handles the case where an empty schema should be undefined. By validating jsonSchemaValue directly, the code validates the raw tempPayload value instead of the cleaned version. This inconsistency means that validation may pass but the wrong data could be saved, or validation may fail when it should succeed if the schema is empty but not yet normalized.

GT 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue) ⏎ if (schema?.type !== 'object') {`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:311`，距錨點 0 行）jsonSchemaValue 型別檢查不完整，可能跳過驗證

> 在 handleConfirm 中，驗證 JSON Schema 的條件為 `typeof jsonSchemaValue === 'string'`。但 tempPayload.json_schema 的型別可能是物件（例如從 API 載入時），此時若為物件，則不會進行 JSON.parse 和 type 檢查，直接通過驗證。這可能導致非 object 型別的 schema 被儲存。

建議改為：若 jsonSchemaValue 不是字串，先將其轉為字串（例如 JSON.stringify）再進行解析與驗證，或明確處理物件型別。

finding 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue)`

## P0647

**GT**（func）Incorrect Reader Mode URL handling in cancelEditMode

> The cancelEditMode function now incorrectly preserves reader mode URLs when canceling edit mode. The logic was changed from '&&' (AND) to '||' (OR), which means reader mode URLs will now be kept instead of being cleared. This breaks the expected behavior where reader mode URLs should be filtered out when canceling URL editing, potentially causing the address bar to display internal reader:// URLs to users instead of the original webpage URL.

GT 片段：`@MainActor ⏎ private func cancelEditMode(windowUUID: WindowUUID) { ⏎ var url = tabManager(for: windowUUID).selectedTab?.url ⏎ if let currentURL = url {`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485`，距錨點 0 行）cancelEditMode 中的 URL 判斷邏輯反轉，可能導致編輯模式取消時 URL 遺失

> 原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓非網頁 URL（例如 about:blank）或閱讀模式 URL 也被保留，可能導致取消編輯時工具列顯示錯誤的 URL。請確認此變更的意圖，並補充測試。

finding 片段：`url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`

## P0648

**GT**（func）Removed HTML5 min validation from concurrency limit input

> The concurrency limit input field previously had `min={0}` attribute (HTML5 validation) to prevent negative numbers from being entered. This attribute was removed in this PR change. While the Zod schema still validates that the value must be >= 0, users now lose immediate feedback when trying to enter negative values. They can type a negative number like `-5` and only discover it's invalid after clicking Save, rather than being prevented from entering it in the first place. This degrades the user experience by removing client-side validation that provides instant feedback.

GT 片段：`<Input ⏎ {...field} ⏎ type="number" ⏎ placeholder="Unlimited"`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112`，距錨點 0 行）並行限制輸入未驗證，可能送出負數或非整數值

> 在 `onChange` 中直接將輸入轉為 `Number`，但未檢查是否為有效整數或正數。若使用者輸入 `-5` 或 `2.5`，表單會接受並在提交時送出，可能導致 API 錯誤或非預期的行為。建議在 zod schema 中加入 `.int().positive()` 驗證，或在 `onChange` 中過濾無效值。

finding 片段：`onChange={(e) => { ⏎ const value = e.target.value; ⏎ field.onChange(value === "" ? null : Number(value)); ⏎ }}`

## P0649

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）mark_edge_skipped 順序調整可能影響遞迴邏輯

> 將 `mark_edge_skipped` 移到 `propagate_skip_from_edge` 之後，可能導致在遞迴過程中邊的狀態尚未被標記為 skipped，若遞迴中再次檢查該邊的狀態可能得到不一致的結果。建議確認此順序調整是否為必要，並確保不會影響其他邏輯。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0650

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:32`，距錨點 7 行）assert smtp is not None 為冗餘且可能被最佳化移除

> assert smtp is not None 在建立 SMTP 實例後立即執行，但該實例必定非 None，因此 assert 永遠為真。若使用 python -O 執行，assert 會被移除，不影響功能。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0651

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 40 行）並行建置可能產生相同的 versionCode

> 在 `generate_tauri_properties` 中，讀取舊的 versionCode 後直接加 1 寫入，沒有使用鎖定或原子操作。如果兩個建置同時執行（例如 CI 中並行觸發），它們可能讀到相同的舊值，並產生相同的 versionCode，導致上架衝突。建議使用檔案鎖（例如 `flock`）或將 versionCode 儲存在可原子更新的位置（如資料庫或遠端服務）。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0652

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0653

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2562`，距錨點 2 行）HSETEX 指令可能不存在於舊版 Redis，導致複製中斷

> 此變更將 HINCRBYFLOAT 的複製指令改為 HSETEX。若 replica 或 AOF 重播環境的 Redis 版本不支援 HSETEX（例如舊版或某些 fork），複製或 AOF 重播將失敗。建議確認 HSETEX 在所有支援的版本中皆可用，或提供 fallback 機制。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0654

**GT**（func）Query parameter naming collision between plugin page and marketplace

> The plugin page context changed from 'category' to 'tab' query parameter (line 71), but the marketplace useActivePluginType still uses 'tab' instead of 'category' (line 23 in atoms.ts). This creates a naming collision where both components try to control the same 'tab' URL query parameter for different purposes. When users navigate between the plugin page tabs and marketplace categories, the URL state will conflict causing incorrect active states and navigation issues. The marketplace should use 'category' parameter while the plugin page uses 'tab' parameter to maintain their independent states.

GT 片段：`export function useActivePluginType() { ⏎ return useQueryState('tab', marketplaceSearchParamsParsers.category) ⏎ }`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:23`，距錨點 0 行）query key 從 'category' 改為 'tab' 可能破壞既有連結

> `useActivePluginType` 的 query key 從 `'category'` 改為 `'tab'`。若使用者已將帶有 `?category=...` 的網址加入書籤或分享，升級後這些連結將不再生效，可能導致使用者看到非預期的分類。建議考慮保留舊 key 的相容性，或確認此變更為可接受的 breaking change。

finding 片段：`return useQueryState('tab', marketplaceSearchParamsParsers.category)`

## P0655

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15`，距錨點 0 行）排程條件反轉導致重複排程

> 原本條件 `!hasScheduled.processOutbox` 在未排程時才排程，現在改為 `hasScheduled.processOutbox`，變成已排程時才排程。這會導致：
1. 首次呼叫時 `hasScheduled.processOutbox` 為 false，不會排程。
2. 若之後某次呼叫時 `hasScheduled.processOutbox` 被設為 true（例如手動設定或未來程式碼變更），則會重複排程。
建議改回 `!hasScheduled.processOutbox`。

finding 片段：`if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`

## P0656

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行）角色裝飾器可能允許非管理員成員建立邀請

> 控制器使用 `@Roles("TEAM_MEMBER")`，這表示任何團隊成員（包括一般成員）都可以呼叫此端點。然而，e2e 測試中有一個情境是「User is Team Member (not Admin)」預期會回傳 403。這可能表示角色檢查的邏輯有誤，或者測試情境與實際權限設計不一致。如果預期只有管理員可以建立邀請，應該使用 `@Roles("TEAM_ADMIN")` 或類似角色。

**建議**：確認此端點的權限需求，並調整 `@Roles` 裝飾器或測試期望。

finding 片段：`@Roles("TEAM_MEMBER")`

## P0657

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0658

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 15 行）emailAddressService.init() 移至 Promise.all 可能改變初始化時序

> 原本 `emailAddressService.init()` 是單獨 await，現在被移入 `Promise.all` 中。若其他服務依賴 emailAddressService 初始化完成，可能造成競態。請確認此變更不會影響相依服務的初始化順序。

finding 片段：`emailAddressService.init(),`
