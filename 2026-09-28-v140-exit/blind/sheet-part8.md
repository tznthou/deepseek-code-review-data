# 盲標單 8：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part8.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0659

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行）移除 `strict=True` 可能掩蓋 zip 長度不匹配

> 原本使用 `zip(pool_names_list, results, strict=True)` 會在長度不一致時拋出 `ValueError`，現在移除 `strict=True` 後，若 `pool_names_list` 和 `results` 長度不同，多餘的元素會被靜默忽略，可能導致部分工作池未被處理且無任何警告。建議保留 `strict=True` 或手動檢查長度。

finding 片段：`for name, result in zip(pool_names_list, results):`

## P0660

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142`，距錨點 5 行）handleDragEnd 中 moveItem 參數順序錯誤導致拖曳方向相反

> 在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能與 `moveItem` 的預期相反。從既有程式碼 `moveUp={() => moveItem(index, index - 1)}` 和 `moveDown={() => moveItem(index, index + 1)}` 推測，`moveItem` 的第一個參數是來源索引，第二個是目標索引。但拖曳時，`oldIndex` 是來源，`newIndex` 是目標，因此應呼叫 `moveItem(oldIndex, newIndex)`。目前寫法會導致拖曳後項目移動到錯誤位置，甚至可能超出陣列範圍。

finding 片段：`moveItem(newIndex, oldIndex);`

## P0661

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 0 行）跨欄位驗證誤用 field_validator，可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中，試圖透過 `info.data.get("bucket")` 取得 bucket 欄位值來進行跨欄位驗證。但此驗證器是 `field_validator`，在驗證 bucket_folder 時，bucket 欄位可能尚未被驗證或設定，因此 `info.data` 中可能沒有 bucket 的值，導致驗證永遠不會觸發。

應改用 `model_validator` 來進行跨欄位驗證，確保所有欄位都已就緒。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0662

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 9 行）並行建置可能產生相同的 versionCode

> 在 `generate_tauri_properties` 中，讀取舊的 versionCode 後直接加 1 寫入，沒有使用鎖定或原子操作。如果兩個建置同時執行（例如 CI 中並行觸發），它們可能讀到相同的舊值，並產生相同的 versionCode，導致上架衝突。建議使用檔案鎖（例如 `flock`）或將 versionCode 儲存在可原子更新的位置（如資料庫或遠端服務）。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0663

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 為 null 時的行為不一致

> 在 getTeamsWithPBACPermissions 中，orgId 參數型別為 number | null，但 SQL 條件使用 `${orgId}::bigint IS NULL`。若 orgId 為 null，會產生 `null::bigint`，在 PostgreSQL 中可能被視為 NULL，但行為依賴於資料庫。建議明確處理 null 與 undefined。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0664

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行）moduleLoader.token 設定錯誤，可能導致 DI 解析失敗

> 在 `FeaturesRepository.ts` 中，`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`，但其他 module（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token（`token`）。這可能導致依賴此 module 的程式碼在解析時取得錯誤的 token，造成 DI 容器無法正確綁定或解析。

建議將 `token` 改為 `token`（即 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`），以符合其他 module 的慣例。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## P0665

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）日期計算可能因時區或時序產生 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並取 `Math.ceil`。若 `created_at` 是 UTC 儲存，而伺服器時區非 UTC，可能導致天數計算偏差。此外，若第一封信是在當天稍晚發送，`Math.ceil` 可能將未滿一天算成一天。建議使用 UTC 日期或明確的日界線計算。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0666

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 5 行）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## P0667

**GT**（func）Removed HTML5 min validation from concurrency limit input

> The concurrency limit input field previously had `min={0}` attribute (HTML5 validation) to prevent negative numbers from being entered. This attribute was removed in this PR change. While the Zod schema still validates that the value must be >= 0, users now lose immediate feedback when trying to enter negative values. They can type a negative number like `-5` and only discover it's invalid after clicking Save, rather than being prevented from entering it in the first place. This degrades the user experience by removing client-side validation that provides instant feedback.

GT 片段：`<Input ⏎ {...field} ⏎ type="number" ⏎ placeholder="Unlimited"`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112`，距錨點 0 行）concurrency_limit 允許負數與非整數輸入

> 在 `onChange` 中直接將輸入值轉為 `Number(value)`，未檢查是否為正整數。若使用者輸入 `-5` 或 `2.5`，表單會接受並提交，可能導致後端驗證失敗或產生非預期行為。建議在 zod schema 中加入 `.int().positive()` 驗證，或在 `onChange` 中阻擋無效值。

finding 片段：`onChange={(e) => { ⏎ const value = e.target.value; ⏎ field.onChange(value === "" ? null : Number(value)); ⏎ }}`

## P0668

**GT**（rule）Unused variable causes compilation warning

> The code declares an unused variable 'unused_flag' that triggers a compilation warning, causing the build to fail when -Werror flag is enabled

GT 片段：`void hincrbyfloatCommand(client *c) { ⏎ long double value, incr; ⏎ long long ll; ⏎ robj *o;`

**finding**（`src/t_hash.c:2244`，距錨點 0 行）變數 unused_flag 宣告後未使用

> 在 hincrbyfloatCommand 中宣告了 `int unused_flag = 0;` 但從未使用。這可能是開發過程中的殘留，應移除。

finding 片段：`int unused_flag = 0;`

## P0669

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 的實作中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體如 `Nsis`、`App`、`Dmg` 都回傳小寫字串。這可能導致序列化或顯示時的不一致，建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0670

**GT**（rule）Public ensureMainThread<T> lacks documentation comment

> A new/modified public API was introduced/changed without an accompanying triple-slash documentation comment describing its purpose/parameters/return value.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? {`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行）ensureMainThread 泛型版本回傳 T? 可能導致呼叫端忽略 nil 而產生邏輯錯誤

> `ensureMainThread<T>` 現在在非主執行緒時回傳 `nil`，但呼叫端可能未處理 nil 而直接使用回傳值，導致非預期的 nil 或崩潰。建議檢查所有呼叫端，確認它們正確處理 nil 情況，或考慮提供非同步版本。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## P0671

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0672

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳索引錯亂

> `sortableKeys` 由 `localKeyedValues.map((item) => item.key)` 產生，包含所有項目，但實際上只有非 prefix items 可拖曳（`canMove` 為 true）。當存在 prefix items 時，拖曳一般項目時，`over.id` 可能指向不可拖曳的 prefix item，導致 `newIndex` 計算錯誤，或拖曳行為不符合預期。建議 `sortableKeys` 只包含可拖曳項目的 key，例如先 filter `getCanMoveForIndex(index)` 為 true 的項目。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0673

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0674

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行）start_execution 在 enqueue 之前呼叫可能導致狀態不一致

> 在 `enqueue_node` 之前呼叫 `start_execution` 可能造成節點狀態被標記為執行中，但尚未進入佇列。若後續 `enqueue_node` 失敗或拋出例外，節點會停留在執行中狀態而無法被正確處理。建議確認 `start_execution` 的實作是否具冪等性，或調整呼叫順序。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0675

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 1 行）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0676

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 移至 Promise.all 可能改變初始化時序

> 原本 `emailAddressService.init()` 是單獨 await，現在被移入 `Promise.all` 中。若其他服務依賴 emailAddressService 初始化完成，可能造成競態。請確認此變更不會影響相依服務的初始化順序。

finding 片段：`emailAddressService.init(),`

## P0677

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行）鏡像 URL 建構邏輯變更可能導致錯誤

> 原本 `cdn.set_path(github_url)` 會將鏡像 URL 的 path 設為完整的 GitHub URL，但修改後直接回傳 `cdn.to_string()`，忽略了 `github_url` 參數。這可能導致鏡像功能失效，或產生錯誤的 URL。

**失敗情境**：當使用者設定 `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` 環境變數時，原本預期會將 GitHub URL 轉換為鏡像 URL，但修改後只回傳鏡像的 base URL，導致下載失敗或下載到錯誤的資源。

**建議**：確認此變更是否為預期行為。若需保留鏡像功能，應正確組合鏡像 base URL 與原始路徑。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## P0678

**GT**（rule）Missing trailing newline at end of file

> The diff indicates the file has no trailing newline ("\ No newline at end of file"), which violates standard formatting expectations enforced by formatters/linters.

GT 片段：`};\ No newline at end of file`

**finding**（`packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:108`，距錨點 3 行）檔案結尾缺少換行符號

> 檔案結尾缺少換行符號，可能導致某些工具或 diff 顯示問題。建議在最後一行加上換行。

finding 片段：`};`

## P0679

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）_serverToken 型別變更可能導致後續使用錯誤

> `_serverToken` 原本存 token 字串，現在改存整個 token 物件（包含 `token` 和 `exp`）。若其他程式碼仍預期 `_serverToken` 是字串，可能導致型別錯誤或功能失效。請確認所有使用 `_serverToken` 的地方都已更新。

finding 片段：`this._serverToken = tokenData;`

## P0680

**GT**（rule）Line exceeds Biome configured line width

> The codebase formatting rule specifies a 110 character line width. This added line is clearly longer than 110 characters (chained call with long template literal), violating the configured formatting constraints.

GT 片段：`+      const first = await request(app.getHttpServer()).post(`/v2/teams/${team.id}/invite`).expect(200);`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:68`，距錨點 7 行）測試可能因 token 不一致而失敗

> 測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會因為 token 回傳為 identifier 而失敗。此外，非管理員和非成員的測試預期 403，但若控制器未檢查團隊成員資格，這些測試可能不會通過。

finding 片段：`expect(response.body.data.inviteLink).toContain(response.body.data.token);`

## P0681

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，修改後改為 `expect("File association must have a name")`。若使用者未設定 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定檔中某個 file association 未提供 `name` 且 `ext` 為空陣列，打包時會 panic 並中止。

**建議**：保留原本的 fallback 邏輯，或改用更安全的錯誤處理（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0682

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行）TOML 解析錯誤被錯誤地包裝為 JSON 錯誤

> 在 `do_parse_toml` 函數中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但更新後改為使用 `ConfigError::FormatJson`，並將錯誤轉換為 `serde_json::Error`。這會導致錯誤類型不匹配，可能使呼叫端無法正確處理 TOML 格式錯誤，且錯誤訊息可能誤導使用者。建議保留 `ConfigError::FormatToml` 變體，或新增一個專門的 TOML 錯誤變體。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## P0683

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）新增 ENABLE_WEBHOOKS 環境變數可能意外停用 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，則 `webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），則會意外停用所有取消 booking 的 webhook，可能導致下游系統收不到通知。建議確認此環境變數名稱是否專用，或改用更明確的名稱，並在文件中說明。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0684

**GT**（func）Swapped source and destination in ditto archive command

> The arguments to the ditto command are reversed: zip_path appears before app_bundle_path, when ditto expects the source (app_bundle_path) before the destination (zip_path). This will cause ditto to fail when attempting to create the notarization archive, as it tries to compress a non-existent zip file into the app bundle directory. The command format should be 'ditto -c -k --keepParent --sequesterRsrc <source> <destination>', but the current order attempts '<destination> <source>', breaking the entire notarization workflow.

GT 片段：`let zip_args = vec![ ⏎ "-c", ⏎ "-k", ⏎ "--keepParent",`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## P0685

**GT**（func）Inconsistent format specifier documentation in RolloutsSettingMessage comment

> The comment for RolloutsSettingMessage incorrectly documents the format specifier as '%1$@' (positional format) while the actual value string uses '%@' (simple format). This mismatch creates confusion for localization teams and could lead to incorrect translations, as translators may attempt to use positional formatting based on the comment when the string implementation doesn't support it. The comment should match the actual format specifier used in the value field.

GT 片段：`public static let RolloutsSettingMessage = MZLocalizedString( ⏎ key: "Settings.Rollouts.Message.v148", ⏎ tableName: "Settings", ⏎ value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.",`

**finding**（`firefox-ios/Shared/Strings.swift:6260`，距錨點 0 行）格式佔位符不一致可能導致執行時期錯誤

> 在 `RolloutsSettingMessage` 的 value 中使用了 `%@`，但 comment 中說明為 `%1$@`。若翻譯人員依照 comment 使用 `%1$@`，則在執行時期使用 `String(format:)` 時，若只傳入一個參數，`%1$@` 是合法的（指定第一個參數），但若程式碼預期使用 `%@` 而翻譯使用 `%1$@`，可能導致格式字串與參數不匹配。建議統一使用 `%@` 或 `%1$@`，並確保所有翻譯遵循相同格式。

finding 片段：`value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", ⏎ comment: "A short description that explains that Mozilla may change features remotely. %1$@ is the app name (e.g. Firefox)."`

## P0686

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行）搜尋過濾同時在伺服器端與客戶端進行，可能導致不一致

> 查詢參數中已包含 `name: { like_: deferredSearch }`，但又在客戶端使用 `filteredData` 進行過濾。這可能導致不必要的客戶端計算，且若伺服器端過濾邏輯與客戶端不同（例如大小寫處理），可能出現不一致的結果。

**建議**：移除客戶端過濾，完全依賴伺服器端過濾，或確保兩者邏輯一致。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0687

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## P0688

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行）鏡像 URL 處理方式變更可能導致錯誤網址

> 原本 `generate_github_mirror_url_from_base` 會將 `cdn` 的 path 設為 `github_url`，現在直接回傳 `cdn.to_string()`。這可能導致鏡像網址不再包含原始 GitHub URL 的路徑，使得下載失敗或指向錯誤資源。需要確認此變更是否為預期行為，並驗證鏡像功能是否仍正常運作。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## P0689

**GT**（rule）Handler logic mixed in schema file

> The rule requires that schema and handler logic are separated into different files. However, the schema file `booking.output.ts` now contains a handler method `cleanEmailForDisplay()` that performs email validation and transformation logic, mixing schema definition with handler logic in the same file.

GT 片段：`// Validate and clean email for display purposes ⏎ static cleanEmailForDisplay(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

**finding**（`packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32`，距錨點 27 行）displayEmail 被標記為必填，可能破壞 API 相容性

> 在 BookingAttendee、BookingHost、ReassignedToDto 等類別中，新增的 displayEmail 欄位被標記為必填（沒有 @IsOptional()），且 OpenAPI 規格中也將 displayEmail 加入 required 陣列。這表示所有 API 回應都必須包含 displayEmail，否則可能導致驗證失敗或客戶端解析錯誤。然而，此欄位是新增的，既有客戶端可能未預期此欄位，若客戶端使用嚴格的 schema 驗證，可能因額外欄位而失敗。

建議：將 displayEmail 設為可選（加上 @IsOptional()），並在 OpenAPI 中不要列為 required，以維持向後相容性。

finding 片段：`@ApiProperty({ type: String, example: "john@example.com", description: "Clean email for display purposes" }) ⏎ @IsString() ⏎ @Expose() ⏎ displayEmail!: string;`

## P0690

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68`，距錨點 15 行）輪詢可能產生競態條件

> `confirmHandle` 使用 `mutateAsync` 但未處理錯誤，且輪詢間隔固定為 5 秒。若前一次請求尚未完成，下一次輪詢可能同時發出多個請求，導致伺服器壓力或狀態不一致。此外，若 `confirmBlueskyHandleMutation` 失敗（例如網路錯誤），錯誤未被捕獲，可能造成 unhandled rejection。建議在 `confirmHandle` 中加入錯誤處理，並考慮使用 `isPending` 或鎖定機制避免重疊請求。

finding 片段：`const confirmHandle = useCallback(() => { ⏎ confirmBlueskyHandleMutation.mutateAsync().then((handle) => { ⏎ if (handle) { ⏎ setHandleConfirmed(true);`

## P0691

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行）bookingUrl 解析邏輯可能產生錯誤的顯示前綴

> 在解析 bookingUrl 以取得顯示前綴時，程式碼使用 `url.hostname` 而非 `url.host`，這會忽略埠號。若 bookingUrl 包含非標準埠（例如開發環境），顯示的連結將不正確。此外，若 bookingUrl 為相對路徑或格式不符，`new URL` 會拋出例外，但 catch 區塊僅回退到 `cal.com/${props.username}/`，可能與實際網域不符。建議使用 `url.host` 並考慮更完整的錯誤處理。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ // Get path without the last segment (slug) ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug`

## P0692

**GT**（func）Incorrect truthy check for retry_jitter_factor hides valid zero values

> The retry_jitter_factor check was changed from an explicit null/undefined check to a simple truthy check. This is a critical bug because a jitter factor of 0 is a valid configuration value (meaning no randomness in retry delays), but the truthy check treats 0 as falsy and displays "None" instead. This misrepresents the actual task configuration to users, making them think no jitter factor is set when it's actually configured to 0. The original PR correctly distinguished between 'not set' (null/undefined) and 'set to zero' (0), but this change breaks that distinction.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retry Jitter Factor</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retry_jitter_factor`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 0 行）Retry Jitter Factor 使用 truthy 檢查可能將 0 顯示為 None

> 在 Retry Jitter Factor 欄位中，使用 `taskRun.empirical_policy?.retry_jitter_factor ? ... : "None"`。若 `retry_jitter_factor` 為 `0`（合法值），則會顯示 `None`，但實際上應該顯示 `0`。建議改用 `!== null && !== undefined` 或 `??` 來判斷。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## P0693

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:186`，距錨點 9 行）驗證失敗時未顯示錯誤

> `catch` 區塊僅顯示通用錯誤訊息，未提供具體驗證失敗原因。建議將 `err` 的詳細資訊納入錯誤訊息，或使用更精確的錯誤處理。

finding 片段：`} catch (err) { ⏎ const message = "Unknown error while validating block data."; ⏎ toast.error(message); ⏎ console.error(message, err);`

## P0694

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0695

**GT**（func）Validation incorrectly rejects proactive triggers with automation_triggered_event_id

> The field_validator for automation_triggered_event_id prevents setting this field when triggering_event is None. However, proactive triggers (which have no triggering_event) still create automation.triggered events and need to link actions to them via automation_triggered_event_id. The code in triggers.py sets automation_triggered_event_id=primary_state_change_event_id for all actions including proactive triggers, causing Pydantic validation to fail at runtime. This breaks all proactive automations, which is a critical functional regression.

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行）欄位驗證器依賴欄位順序，可能因未來調整而失效

> `validate_automation_triggered_event_id` 驗證器使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 僅包含已驗證的欄位，因此若 `triggering_event` 欄位在 `automation_triggered_event_id` 之後定義，驗證器將無法取得其值，導致驗證失效。

失敗情境：若未來有人調整欄位順序，將 `triggering_event` 移到 `automation_triggered_event_id` 之後，則即使 `triggering_event` 為 None，驗證器也不會拋出錯誤，允許不一致的資料。

建議修法：改用 `model_validator` 或在驗證器中直接從 `info.data` 以外的來源取得 `triggering_event`，或使用 `@model_validator(mode='after')` 進行跨欄位驗證。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## P0696

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 15 行）JWT 簽署移除 noTimestamp 可能影響 token 格式

> `jwt.sign` 原本有 `{noTimestamp: true}`，現在移除後 token 會包含 `iat` 欄位。若 Tinybird 端對 token 格式有特定要求，可能導致驗證失敗。建議確認 Tinybird 是否接受帶有 `iat` 的 token。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0697

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0698

**GT**（func）Inverted conditional logic in setUserFeatureState causes wrong branch execution

> The conditional check for handling the 'inherit' state has been inverted from `if (state === 'inherit')` to `if (state !== 'inherit')`. This causes the method to incorrectly pass the state without assignedBy when state is 'enabled' or 'disabled', and incorrectly attempts to access assignedBy property (which doesn't exist in the union type) when state is 'inherit', leading to runtime TypeScript errors and incorrect database operations. When users try to enable/disable a feature, the assignedBy tracking will be lost, and when they set it to inherit, the code will crash trying to access a non-existent property.

GT 片段：`if (state !== "inherit") { ⏎ await this.featuresRepository.setUserFeatureState({ userId, featureId, state }); ⏎ } else { ⏎ const { assignedBy } = input;`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:264`，距錨點 0 行）setUserFeatureState 條件判斷反轉，可能導致 assignedBy 處理錯誤

> 原本的 `if (state === "inherit")` 被改為 `if (state !== "inherit")`，這使得當 state 為 "enabled" 或 "disabled" 時，會進入原本處理 inherit 的分支，嘗試從 input 中取得 `assignedBy` 並呼叫 `setUserFeatureState`。但 TypeScript 的 union type 保證在 state 非 inherit 時 input 一定包含 `assignedBy`，因此不會有 runtime error，但邏輯上與原本意圖相反。

**建議修法**：改回 `if (state === "inherit")`。

finding 片段：`if (state !== "inherit") {`

## P0699

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0700

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）cli.js 版本與 tauri-cli crate 版本不一致

> metadata-v2.json 中的 cli.js 版本從 2.8.1 改為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 升到 2.8.1。這可能導致發布流程中 npm 套件與 Rust crate 版本不匹配，或使用者安裝時取得錯誤的 CLI 版本。請確認此處是否應為 2.8.1，或 tauri-cli 應升到 2.8.2。

finding 片段：`"version": "2.8.2",`

## P0701

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行）SMTP_SSL 建構子可能不支援 local_hostname 參數

> 在 Python 3.10 及更早版本中，smtplib.SMTP_SSL 的 __init__ 方法簽名為 (host='', port=0, local_hostname=None, keyfile=None, certfile=None, timeout=..., ...)，實際上接受 local_hostname 參數。但需確認專案使用的 Python 版本是否支援。若版本過舊，可能導致 TypeError。建議檢查 Python 版本，或改用條件式分別建立 SMTP 與 SMTP_SSL 實例，避免將 local_hostname 傳給不支援的類別。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0702

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:16`，距錨點 3 行）IS_DEV 判斷可能在 client bundle 中失效

> `IS_DEV` 從 `@/config` 匯入，若該值在建置時被替換為 `false`，則在 production 環境中 devtools 不會載入，符合預期。但若 `IS_DEV` 是 runtime 判斷（例如依賴 `process.env.NODE_ENV`），在 client bundle 中可能無法正確反映環境，導致 devtools 在 production 中意外載入，或反之在 development 中未載入。建議確認 `IS_DEV` 的實作方式，並考慮在建置時使用 `process.env.NODE_ENV` 進行靜態替換。

finding 片段：`if (!IS_DEV) ⏎ return null`

## P0703

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

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

## P0704

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）write_and_make_executable 先設定權限再寫入可能導致問題

> 函式改為先執行 `fs::set_permissions` 再執行 `fs::write`。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致函式提前返回，檔案永遠不會被建立。此外，即使檔案存在，先設定權限再寫入也可能在寫入過程中因權限不足而失敗。建議維持原本的先寫入再設定權限的順序。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0705

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 0 行）JWT 驗證改為僅解碼，未驗證簽章

> `_isJWTExpired` 方法原本使用 `jwt.verify(token, this.tinybirdConfig.adminToken)` 來驗證 token 的簽章與有效性，現在改為 `jwt.decode(token)`，只解碼而不驗證簽章。這會讓攻擊者可以偽造 token（只要 payload 包含有效的 `exp` 欄位），繞過驗證。

**失敗情境**：攻擊者自行產生一個帶有未來 `exp` 的 JWT，即使簽章無效，系統仍會視為有效，進而取得未授權的存取。

**建議**：保留 `jwt.verify` 來驗證簽章，若需要解碼 payload 可另行處理。

finding 片段：`const decoded = jwt.decode(token);`

## P0706

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行）XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，函式會回傳 nil，但呼叫端僅以 XCTFail 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果，並在逾時時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0707

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:102`，距錨點 0 行）移除 source 參數傳遞可能影響現有功能

> 原本有將 `options.source` 加入 tinybirdOptions 的邏輯（允許空字串代表 Direct traffic），但此 PR 移除了該區塊。若前端仍會傳送 `source` 參數，則後端將不再將其傳遞給 Tinybird，可能導致 source 過濾失效。請確認是否有其他地方處理 source，或是有意移除。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## P0708

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## P0709

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）SMTP_SSL 建構子可能不支援 local_hostname 參數

> 在 Python 3.10 及更早版本中，smtplib.SMTP_SSL 的 __init__ 方法簽名為 (host='', port=0, local_hostname=None, keyfile=None, certfile=None, timeout=..., ...)，實際上接受 local_hostname 參數。但需確認專案使用的 Python 版本是否支援。若版本過舊，可能導致 TypeError。建議檢查 Python 版本，或改用條件式分別建立 SMTP 與 SMTP_SSL 實例，避免將 local_hostname 傳給不支援的類別。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0710

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0711

**GT**（rule）Any type used for selector parameter

> The rule requires using specific types instead of 'any' annotations. The selector parameter uses 'any' instead of a proper function type signature.

GT 片段：`export function usePluginPageContext(selector: any) { ⏎ return useContextSelector(PluginPageContext, selector) ⏎ }`

**finding**（`web/app/components/plugins/plugin-page/context.tsx:51`，距錨點 0 行）selector 型別從函式放寬為 any，喪失型別安全

> `usePluginPageContext` 的參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會讓 TypeScript 無法檢查傳入的 selector 是否為函式，可能導致 runtime 錯誤（例如傳入非函式值）。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => any` 或更精確的泛型。

finding 片段：`export function usePluginPageContext(selector: any) {`

## P0712

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert smtp is not None 為冗餘且可能被最佳化移除

> assert smtp is not None 在建立 SMTP 實例後立即執行，但該實例必定非 None，因此 assert 永遠為真。若使用 python -O 執行，assert 會被移除，不影響功能。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0713

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，函式會回傳 nil，但呼叫端僅以 XCTFail 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果，並在逾時時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0714

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:274`，距錨點 3 行）將同步閉包改為 Task 可能改變執行順序與時機

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會將原本同步的呼叫變成非同步，可能導致呼叫端預期完成後立即執行的程式碼延後執行，或與其他非同步操作產生競態。此外，Task 未處理取消或錯誤，若 handleAction 拋出錯誤，可能導致未處理的錯誤。建議確認此變更的必要性，並考慮使用 Task { @MainActor in ... } 確保在主執行緒執行，或保留同步呼叫並調整閉包標註。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0715

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0716

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1961`，距錨點 0 行）active_defrag_enabled 未正確還原，可能意外啟用 defrag

> 在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存入 `orig_active_defrag`，然後設為 0，但在函式結尾卻直接設為 1，而非還原為 `orig_active_defrag`。這會導致原本停用 active defrag 的伺服器在執行此函式後被強制啟用，可能造成非預期的記憶體整理行為，甚至影響效能或穩定性。

建議修正：
```c
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`/* Restore the original active defragmentation setting. */ ⏎ server.active_defrag_enabled = 1;`

## P0717

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）versionCode 達到上限時靜默飽和

> 使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0718

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳值型別錯誤：使用 Python 的 `True` 而非 JavaScript 的 `true`

> 在 `handleJSONSchemaChange` 函式中，成功解析 JSON 後回傳了 `True`（Python 布林值），但在 JavaScript/TypeScript 中應為 `true`。這會導致回傳值型別不一致，且若呼叫端依賴此回傳值，可能造成非預期行為。建議改為 `return true`。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0719

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0720

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0721

**GT**（rule）New code uses unwrap() on fallible operations

> Added code introduces multiple `unwrap()` calls on fallible operations (`parse().unwrap()`, `set_title(...).unwrap()`, and `build().unwrap()`), which violates the rule prohibiting panics/unwraps in favor of explicit error handling via `Result`.

GT 片段：`let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"), ⏎ tauri::WebviewUrl::External("about:blank".parse().unwrap()),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 13 行）on_new_window 移至 cfg(desktop) 區塊可能改變非桌面平台行為

> 原本 `on_new_window` 的設定在所有平台都會執行，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內，這表示在非桌面平台（如行動裝置）上，新視窗的建立邏輯將不會被註冊。如果這是預期的行為變更，請確認；否則可能導致非桌面平台無法正確處理新視窗請求。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## P0722

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0723

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:76`，距錨點 16 行）Popover 觸發按鈕缺少鍵盤可訪問性

> PopoverTrigger 使用 Button 元件，但未設定 onClick 或 keyboard 事件來開啟 Popover。依賴 hover 的互動方式對鍵盤使用者不友善，且可能無法透過 Tab 鍵聚焦並開啟。建議加入 onClick 處理，或使用 Popover 的 trigger 屬性設定為 click 或 both。

finding 片段：`<Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0" ⏎ aria-label={`Show ${hiddenItems.length} more items`}`

## P0724

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）參數比對改用 propertyName 可能導致找不到對應參數

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 metadata.Name 與 propertyName 不同（例如使用 BindProperty 或自訂名稱），可能無法正確比對到 operation parameter，導致描述遺失。建議確認此變更的必要性，或保留 metadata.Name 作為比對依據。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0725

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0726

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行）update 方法未使用 select，可能回傳過多資料

> `BookingRepository.update` 方法直接呼叫 `this.prismaClient.booking.update` 而未指定 `select`，可能回傳完整的 Booking 物件，包含不必要的關聯資料，影響效能。若呼叫端只需要部分欄位，建議加入 `select` 參數。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## P0727

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:76`，距錨點 15 行）Popover 觸發按鈕缺少鍵盤可訪問性

> PopoverTrigger 使用 Button 元件，但未設定 onClick 或 keyboard 事件來開啟 Popover。依賴 hover 的互動方式對鍵盤使用者不友善，且可能無法透過 Tab 鍵聚焦並開啟。建議加入 onClick 處理，或使用 Popover 的 trigger 屬性設定為 click 或 both。

finding 片段：`<Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0" ⏎ aria-label={`Show ${hiddenItems.length} more items`}`

## P0728

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行）RequestBody.Description 指派順序變更可能影響範例設定

> 原本 `operation.RequestBody.Description = description;` 在範例處理之前，現在移到範例處理之後。若範例處理中發生例外，Description 可能不會被設定。建議確認此順序變更是否必要，或將 Description 指派保持在前面。

finding 片段：`operation.RequestBody.Description = description;`

## P0729

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行）notlike 未傳入 escape 參數，跳脫失效

> 在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致跳脫字元被視為一般字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成搜尋結果不正確，且可能被用於繞過預期的過濾邏輯。

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## P0730

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）記憶體配置失敗未處理

> `malloc` 可能回傳 NULL，但程式碼未檢查就直接使用 `slot_buffer`，可能導致 NULL 指標解參考。雖然在 Redis 中記憶體配置失敗通常會觸發 OOM 處理，但此處直接使用仍不夠安全。建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或觸發 OOM。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0731

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:76`，距錨點 5 行）Popover 觸發按鈕缺少鍵盤可訪問性

> PopoverTrigger 使用 Button 元件，但未設定 onClick 或 keyboard 事件來開啟 Popover。依賴 hover 的互動方式對鍵盤使用者不友善，且可能無法透過 Tab 鍵聚焦並開啟。建議加入 onClick 處理，或使用 Popover 的 trigger 屬性設定為 click 或 both。

finding 片段：`<Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0" ⏎ aria-label={`Show ${hiddenItems.length} more items`}`

## P0732

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行）buildInviteLink 條件判斷反轉

> 原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

finding 片段：`if (isOrgContext) {`

## P0733

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:12`，距錨點 2 行）require 陳述式缺少分號

> 部分 require 陳述式（如 `const EventRepository = require('./repositories/event-repository');`）保留了分號，而其他則沒有，造成不一致。

finding 片段：`const EventRepository = require('./repositories/event-repository'); ⏎ const ProductRepository = require('./repositories/product-repository'); ⏎ const RouterController = require('./controllers/router-controller'); ⏎ const MemberController = require('./controllers/member-controller');`

## P0734

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行）重新命名檔案時混入非預期的格式變更

> 此檔案除了更新 require 路徑外，還移除了所有行尾分號，並將部分 require 陳述式的引號從單引號改為雙引號。這與專案中其他檔案的風格不一致，且可能違反 ESLint 規則。建議只保留必要的路徑變更，避免混入格式調整。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0735

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0736

**GT**（func）Type mismatch in blocks_variable_output prevents variable blocking

> The blocks_variable_output method compares a Sequence (assigned_variable_selector) directly against a set of tuples (variable_selectors), but fails to convert the Sequence to a tuple first. This type mismatch causes the 'in' check to always return False, meaning the Variable Assigner node will never properly block streaming output of conversation variables. As a result, the response coordinator will incorrectly allow streaming to proceed before conversation variables are updated, violating the intended synchronization logic and potentially showing stale variable values to users.

GT 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool: ⏎ """ ⏎ Check if this Variable Assigner node blocks the output of specific variables. ⏎ Returns True if this node updates any of the requested conversation variables.`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## P0737

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0738

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0739

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:588`，距錨點 0 行）hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false

> 此方法用於檢查使用者是否有待處理的邀請，但查詢條件卻設定為 `accepted: true`，這會導致永遠找不到待處理的邀請（因為待處理邀請的 accepted 為 false）。這使得 PR 的核心功能失效：使用者仍會被導向錯誤的頁面。

**失敗情境**：當使用者有 pending invite（accepted: false）時，`hasPendingInviteByUserId` 會回傳 false，導致 `checkOnboardingRedirect` 和 getting-started 頁面中的條件判斷錯誤，使用者不會被重新導向到 `/onboarding/personal/settings`。

**建議修法**：將 `accepted: true` 改為 `accepted: false`。

finding 片段：`accepted: true,`

## P0740

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）setUp 中呼叫 @MainActor 方法可能造成執行緒問題

> `bootstrapDependencies` 現在是 `@MainActor`，但此測試類別未標記為 `@MainActor`，且 `setUp` 為 async，呼叫時若未在 MainActor 上執行，可能導致 runtime crash 或資料競爭。建議將測試類別標記為 `@MainActor` 或確保在 MainActor 上呼叫。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0741

**GT**（func）Variable shadowing breaks sampling consistency for STREAM objects

> A local `samples` variable is declared at line 1319 within the OBJ_STREAM branch, shadowing the outer `samples` variable declared at line 1214. This prevents the outer samples counter from being updated during stream memory calculation. While this doesn't break the stream calculation itself, it violates the function's sampling design pattern where the outer `samples` variable tracks total sampling across all object type branches. This inconsistency could lead to unexpected behavior if the function logic is modified to check or use the outer samples counter after processing.

GT 片段：`raxStart(&ri,s->rax); ⏎ raxSeek(&ri,"^",NULL,0); ⏎ size_t lpsize = 0; ⏎ size_t samples = 0;`

**finding**（`src/object.c:1330`，距錨點 10 行）stream 的 lpsize 計算可能多算最後一個 listpack

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0742

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0743

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:25`，距錨點 0 行）local_host 為空字串時傳入空字串而非 None

> local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""，若設定為空字串，則 local_host 為空字串。在建構 SMTP 時傳入 local_hostname=local_host or None，但 local_host 為空字串時，local_host or None 會得到 None，因此實際上傳入 None，這部分正確。但後續 opportunistic TLS 模式中，smtp.ehlo(local_host) 會傳入空字串，可能導致 EHLO 命令格式錯誤。建議在呼叫 ehlo 時也使用 local_host or None，或確保 local_host 不為空字串。

finding 片段：`smtp.ehlo(local_host) ⏎ smtp.starttls() ⏎ smtp.ehlo(local_host)`

## P0744

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0745

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 remarks 寫入 Summary 可能改變既有 API 文件行為

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。這會將 `<remarks>` 的內容放到 OpenAPI 的 `summary` 欄位，而非 `description`。若既有使用者依賴 `description` 來顯示備註，此變更會造成文件內容遺失或錯置。建議確認此變更是否符合預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## P0746

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 2 行）多 renderer 並存時初始化可能被跳過

> `hasInitializedJsComponents` 是全域變數，一旦設為 true，之後任何 renderer 呼叫 `enableJSRootComponents` 都不會再執行初始化。若頁面同時存在多個不同 renderer（例如一個 Server 和一個 WebAssembly），且第一個 renderer 初始化後，第二個 renderer 的 JS 元件將不會被初始化，導致功能失效。

建議將 `hasInitializedJsComponents` 改為以 rendererId 為鍵的集合，或將初始化邏輯綁定到每個 manager 實例。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers... ⏎ ... ⏎ hasInitializedJsComponents = true;`

## P0747

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷可能錯誤

> 原本的 `isCurrentUser` 判斷是 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這可能導致當 userIds 包含多個 ID 且其中包含當前使用者時，被視為「僅查詢自己」，從而繞過權限檢查。建議保留原本的嚴格判斷，或明確處理多個 userId 的情況。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0748

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）off-by-one 錯誤：滾動索引超出陣列範圍

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。這會導致 `toIndex` 等於陣列長度，超出有效索引範圍（最後一個索引應為 `count - 1`）。後續在 `TabDisplayView.scrollToTab` 中會使用此索引建立 `IndexPath(row:section:)`，可能造成滾動到不存在的 cell，甚至觸發越界例外。

建議改回 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0749

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:25`，距錨點 0 行）throttle 方法中 lastExecutionTime 更新順序改變可能影響節流邏輯

> 原本 `lastExecutionTime` 在 guard 之後才更新，現在移到 guard 之前。這可能導致在 threshold 條件不滿足時也更新了時間，影響後續呼叫的節流判斷。請確認此變更是否為預期行為。

finding 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

## P0750

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行）versionCode 達到上限時靜默飽和

> 使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0751

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0752

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1125`，距錨點 0 行）複製連結功能未使用 bookingUrl，可能導致不一致

> 在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接 `https://cal.com/${username}/${slug}`，而未使用 `eventType.bookingUrl`。這與其他地方的修改不一致，可能導致使用者複製到舊格式的連結。建議統一使用 `eventType.bookingUrl` 或提供一致的 fallback。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`
