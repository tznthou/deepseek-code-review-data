# 盲標單 4：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part4.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0283

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）slot 可能未初始化即被使用

> 在 `extractKeysAndSlot` 中，原本 `*slot` 會先被設為 `INVALID_CLUSTER_SLOT`，但修改後只有當 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 `*slot`。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能導致未初始化變數被使用。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT`，或確保所有呼叫者都已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0284

**GT**（rule）Missing sync wrapper for async function

> The public API function run_deployment is now just an alias to the async-only arun_deployment function, lacking a proper sync compatibility wrapper. This forces users to always use asyncio.run() or similar async context managers in synchronous code.

GT 片段：`# Alias for backwards compatibility ⏎ run_deployment = arun_deployment`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 0 行）`run_deployment` 別名失去同步包裝，同步呼叫會失敗

> 原本 `run_deployment` 有 `@sync_compatible` 裝飾器，可在同步上下文中呼叫。現在 `run_deployment = arun_deployment` 只是 async 函式的別名，同步呼叫會回傳 coroutine 而非執行結果，導致既有同步程式碼失效。建議保留同步包裝或提供明確的同步版本。

finding 片段：`run_deployment = arun_deployment`

## P0285

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 依賴陣列缺少 item.html，可能導致判斷不準確

> `useEffect` 僅在掛載時執行一次，但 `item.html` 可能因資料更新而改變。若內容變更，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示與否不正確。建議將 `item.html` 加入依賴陣列，或在內容變更時重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0286

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0287

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0288

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 5 行）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0289

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或序列化名稱），可能找不到對應的參數。建議確認兩者是否永遠相同，或保留原本的比對方式。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0290

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 18 行）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行適當消毒，攻擊者可注入惡意腳本，導致儲存型 XSS 攻擊。請確認 `item.html` 的來源已受信任且經過消毒（例如使用 DOMPurify），或改用安全的渲染方式。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0291

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）使用 parseInt 而非 Number 處理數字輸入，且未處理 NaN

> 在 Threshold 欄位的 onChange 中使用 `parseInt(e.target.value)`，而其他元件使用 `Number(e.target.value)`。`parseInt` 會解析開頭的數字並忽略後續非數字字元（例如輸入 "10abc" 會得到 10），可能導致非預期的值。此外，若輸入為空字串，`parseInt('')` 會得到 `NaN`，而 `Number('')` 會得到 0。建議統一使用 `Number` 並處理 `NaN` 的情況（例如設為 undefined 或顯示驗證錯誤）。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0292

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 23 行）跨欄位驗證誤用 field_validator，可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中，試圖透過 `info.data.get("bucket")` 取得 bucket 欄位值來進行跨欄位驗證。但此驗證器是 `field_validator`，在驗證 bucket_folder 時，bucket 欄位可能尚未被驗證或設定，因此 `info.data` 中可能沒有 bucket 的值，導致驗證永遠不會觸發。

應改用 `model_validator` 來進行跨欄位驗證，確保所有欄位都已就緒。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0293

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0294

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 3 行）每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## P0295

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not include explicit AAA structure comments ('// Arrange', '// Act', '// Assert' or '// Act & Assert'), violating the test readability rule.

GT 片段：`public async Task CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser(HttpTransportType transportType, string protocolName) ⏎ { ⏎ using (StartVerifiableLog()) ⏎ {`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92`，距錨點 1 行）將測試標記為隔離可能掩蓋真實問題

> 新增 `[QuarantinedTest]` 屬性會使測試在 CI 中暫時停用，可能導致相關錯誤被忽略。若問題未在隔離期間修復，可能累積技術債。建議確認隔離原因並追蹤修復進度。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`

## P0296

**GT**（func）Test completes without waiting for async image download

> The test was converted from async to synchronous but the expectation and wait statement were removed. This causes the test to complete immediately without waiting for the asynchronous image download callback to execute. The XCTAssert statements inside the completion handler will never be verified, resulting in false positive test passes even if the image download fails or produces incorrect results. This is a critical testing bug that undermines test reliability.

GT 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ guard let imageData = try? dataFor(type: assetType) else {`

**finding**（`BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27`，距錨點 0 行）測試改為同步後未等待非同步完成，可能導致測試提前結束或無法驗證結果

> 在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，移除了 `await fulfillment(of: [exp], timeout: 2.0)`，且未使用 `wait(for:timeout:)`。`downloadImage` 的回呼是非同步的，測試方法現在是同步的，因此測試會在回呼執行前就返回，導致測試永遠通過（即使回呼中有 XCTFail 也不會被執行）。建議保留 expectation 並使用 `wait(for:timeout:)` 等待。

finding 片段：`siteDownloader.downloadImage(with: mockedURL, options: [.processor(SVGImageProcessor())]) { result in`

## P0297

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，修改後改為 `expect("File association must have a name")`。若使用者未設定 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定檔中某個 file association 未提供 `name` 且 `ext` 為空陣列，打包時會 panic 並中止。

**建議**：保留原本的 fallback 邏輯，或改用更安全的錯誤處理（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0298

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有除法或轉換可能出錯）。建議回傳 `emailCount` 或一個明確的常數（如 `Number.MAX_SAFE_INTEGER`），並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0299

**GT**（func）ASM cron runs before cluster state update causing stale state issues

> The serverCron() function now calls asmCron() before clusterCron(). This is problematic because clusterCron() contains the call to clusterUpdateState() which updates the cluster's operational state (CLUSTER_OK vs CLUSTER_FAIL). ASM (Atomic Slot Migration) operations depend on having an accurate view of the cluster state to make correct migration decisions. By executing asmCron() first, migration tasks may operate on stale cluster state information from the previous iteration, potentially leading to incorrect slot migration decisions, failed migrations, or data consistency issues during cluster rebalancing operations.

GT 片段：`if (server.cluster_enabled) { ⏎ asmCron(); ⏎ clusterCron(); ⏎ }`

**finding**（`src/server.c:1658`，距錨點 0 行）asmCron() 呼叫順序變更可能影響行為

> 原本 asmCron() 在 clusterCron() 內部呼叫，現在移至 serverCron() 中 clusterCron() 之前。若 asmCron() 依賴 clusterCron() 的某些狀態更新，順序變更可能導致問題。需確認 asmCron() 的相依性。

finding 片段：`asmCron(); ⏎ clusterCron();`

## P0300

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）skeleton address bar 的 leading 約束可能誤接至 rightSkeletonAddressBar

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)` 被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 錯誤地對齊到右側 skeleton bar 的 trailing，造成佈局錯亂。

請確認此變更是否為預期；若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0301

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38`，距錨點 0 行）Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException

> 在 `Redirect()` 方法中，原本的邏輯是當 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時呼叫 `NavigateToLogin`，否則使用 `_tokenResult.RedirectUrl`。現在改為只要 `InteractionOptions != null` 就呼叫 `NavigateToLogin`，但若 `InteractiveRequestUrl` 為 null，`NavigateToLogin` 內部可能會拋出 NullReferenceException。此外，else 分支改為使用 `InteractiveRequestUrl`，但該屬性可能為 null，導致 `NavigateTo` 拋出例外。建議保留對 `InteractiveRequestUrl` 的 null 檢查，或確保在建構 `AccessTokenResult` 時該屬性必不為 null。

finding 片段：`if (_tokenResult.InteractionOptions != null) ⏎ { ⏎ _navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, _tokenResult.InteractionOptions); ⏎ }`

## P0302

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）屬性 badge 合併權重與群組標記，可能影響可讀性

> 原本權重以獨立 badge 顯示，現在合併到 label 中，例如 'Value 80% (group)'，可能讓使用者難以快速區分權重與群組狀態。建議保留分離的 badge 或使用更明確的視覺區分。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0303

**GT**（func）Memory leak due to missing error message reply to client

> In parseSlotRangesOrReply, when slot range validation fails, the error message allocated by slotRangeArrayNormalizeAndValidate is freed with sdsfree(err) but never sent to the client via addReplyErrorSds. This causes two problems: the client receives no error message explaining why their command failed, making debugging difficult, and it breaks the expected behavior where addReplyErrorSds transfers ownership of the sds string. The original PR intended to always send validation errors to the client for proper error reporting.

GT 片段：`sds err = NULL; ⏎ if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots);`

**finding**（`src/cluster.c:2015`，距錨點 0 行）驗證失敗時未回覆錯誤給客戶端

> 在 `parseSlotRangesOrReply` 中，當 `slotRangeArrayNormalizeAndValidate` 回傳錯誤時，程式碼釋放了 `err` 和 `slots` 並回傳 `NULL`，但沒有呼叫 `addReplyErrorSds` 或類似函式將錯誤訊息回傳給客戶端。這會導致客戶端在輸入無效的 slot range 時收到空回覆（nil），而非明確的錯誤訊息，違反 Redis 命令的錯誤處理慣例。

**失敗情境**：執行 `CLUSTER MIGRATION IMPORT 7000 7001 7000 7001`（重疊範圍），客戶端會收到空回覆，無法得知錯誤原因。

**建議修法**：在釋放 `err` 之前，先呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回傳給客戶端，再釋放 `slots`。

finding 片段：`if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots); ⏎ return NULL;`

## P0304

**GT**（func）Type mismatch in total_price initialization breaks Decimal arithmetic

> The total_price field is initialized with integer 0 instead of Decimal(0), creating a type inconsistency. The MessageAgentThought model defines total_price as Mapped[Decimal | None] expecting a Decimal type, and other price fields (message_unit_price, answer_unit_price, etc.) are correctly initialized with Decimal types. This inconsistency will cause type errors during price calculations when the system attempts to perform Decimal arithmetic operations (addition, multiplication) between Decimal and int types, potentially breaking billing computations or causing runtime exceptions.

GT 片段：`answer_price_unit=Decimal(0), ⏎ tokens=0, ⏎ total_price=0, ⏎ position=self.agent_thought_count + 1,`

**finding**（`api/core/agent/base_agent_runner.py:319`，距錨點 7 行）message_unit_price 與 answer_unit_price 的 Decimal 值可能不符預期

> 在 create_agent_thought 中，message_unit_price 設為 Decimal(0)，answer_unit_price 設為 Decimal("0.001")，而 message_price_unit 設為 Decimal("0.001")，answer_price_unit 設為 Decimal(0)。這些值可能與原本的整數 0 和預設 0.001 不同，需確認是否符合業務邏輯。

finding 片段：`message_unit_price=Decimal(0), ⏎ message_price_unit=Decimal("0.001"),`

## P0305

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0306

**GT**（rule）WebServer class missing final keyword

> The WebServer class is not designed for subclassing (it implements a singleton pattern with sharedInstance) but lacks the 'final' keyword, allowing unintended inheritance and missing compiler optimization opportunities

GT 片段：`class WebServer: WebServerProtocol, @unchecked Sendable { ⏎ static let sharedInstance = WebServer() ⏎ private let logger: Logger ⏎ let server = GCDWebServer()`

**finding**（`firefox-ios/Client/Application/WebServer.swift:59`，距錨點 38 行）移除 @Sendable 可能導致 handler 閉包在非主執行緒執行時產生資料競爭

> `WebServer` 類別被標記為 `@unchecked Sendable`，但其 handler 閉包現在不再要求 `@Sendable`。若 handler 閉包捕獲非 Sendable 的狀態，且該閉包在非主執行緒被呼叫，可能導致資料競爭。建議確認 GCDWebServer 呼叫 handler 的執行緒，若可能非主執行緒，應保留 `@Sendable` 或確保閉包內只存取 Sendable 狀態。

finding 片段：`handler: @escaping @MainActor ( ⏎ _ request: GCDWebServerRequest?, ⏎ _ responseCompletion: @escaping @Sendable (GCDWebServerResponse?) -> Void ⏎ ) -> Void`

## P0307

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:914`，距錨點 0 行）dictSetKeyAtLink 使用未轉換的 key 進行查找

> 在 dictSetKeyAtLink 中，當 *link 為 NULL 時，程式碼使用 `dictFindLink(d, addedKey, NULL)` 來查找現有 entry。然而，`addedKey` 是經過 keyDup 處理後的 stored-key，而 `dictFindLink` 預期的是 lookup key。若 dictType 有設定 keyFromStoredKey，則此處應先將 addedKey 轉換為 lookup key，否則可能找不到正確的 entry，導致資料不一致或錯誤。

失敗情境：當 dict 使用 keyFromStoredKey（例如 dbDictType），且呼叫 dictSetKeyAtLink 更新現有 entry 的 key 時，若 stored-key 與 lookup key 不同，dictFindLink 會使用錯誤的 key 進行比較，可能找不到 entry 或找到錯誤的 entry。

建議修正：將 `dictFindLink(d, addedKey, NULL)` 改為 `dictFindLink(d, dictStoredKey2Key(d, addedKey), NULL)`。

finding 片段：`*link = dictFindLink(d, addedKey, NULL);`

## P0308

**GT**（func）Race condition in recurring booking acceptance audit logging

> For recurring bookings, the fireBookingAcceptedEvent function is called BEFORE the database updates the booking statuses to ACCEPTED. This creates a timing issue where the audit system may attempt to record or query booking information before the database transaction completes. The audit logs could reference bookings that are still in PENDING state, or in extreme cases the audit consumer might fail to find consistent booking data. This race condition can lead to inconsistent audit trails, failed audit log creation, or audit records that don't accurately reflect the database state at the time of acceptance.

GT 片段：`const teamId = await getTeamIdFromEventType({ ⏎ eventType: { ⏎ team: { id: eventType?.teamId ?? null }, ⏎ parentId: eventType?.parentId ?? null,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:263`，距錨點 5 行）recurring accepted 流程中 oldStatus 可能不準確

> 在 recurring accepted 流程中，`acceptedBookings` 的 `oldStatus` 取自 `unconfirmedRecurringBookings` 的 `status`，但該查詢僅篩選 `status: PENDING`，因此 `oldStatus` 會是 `PENDING`。若實際上有其他狀態的 booking 被更新（例如 `TENTATIVE`），則 audit log 會不正確。建議確認是否所有可能被更新的狀態都應被記錄，或調整查詢條件。

finding 片段：`acceptedBookings = unconfirmedRecurringBookings.map((booking) => ({ ⏎ oldStatus: booking.status, ⏎ uid: booking.uid, ⏎ }));`

## P0309

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）日期計算可能因時區或時序產生 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並取 `Math.ceil`。若 `created_at` 是 UTC 儲存，而伺服器時區非 UTC，可能導致天數計算偏差。此外，若第一封信是在當天稍晚發送，`Math.ceil` 可能將未滿一天算成一天。建議使用 UTC 日期或明確的日界線計算。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0310

**GT**（func）Incomplete cache clearing during hot reload causes stale display names

> The ClearCache method only clears _memberInfoCache but fails to clear _displayNameCache (line 85). During hot reload scenarios when metadata updates occur, the HotReloadManager triggers ClearCache to ensure fresh metadata is loaded. However, with _displayNameCache not being cleared, the component will continue to display stale display names from cached MemberInfo objects even after the attributes have been modified in code. This breaks the hot reload functionality for DisplayAttribute and DisplayNameAttribute changes, requiring developers to restart the application to see attribute changes take effect.

GT 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 0 行）Hot Reload 時未清除顯示名稱快取

> 在靜態建構函式中，當 Hot Reload 的 MetadataUpdateSupported 為 true 時，訂閱了 OnDeltaApplied 事件並呼叫 ClearCache。但 ClearCache 只清除了 `_memberInfoCache`，沒有清除 `_displayNameCache`。這可能導致在 Hot Reload 後顯示名稱仍然使用舊的快取值。建議在 ClearCache 中同時清除兩個快取。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0311

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:132`，距錨點 5 行）空值處理可能遺失原始資料

> 當輸入為空時，`handleJSONSchemaChange` 會將 `json_schema` 設為 `undefined`，這可能導致使用者清除欄位後無法恢復先前值。建議確認此行為是否符合預期，或改為儲存空字串。

finding 片段：`if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined) ⏎ return null ⏎ }`

## P0312

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0313

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 5 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0314

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能接受無效資料

> 此函式僅檢查 input 是否為物件且 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）或 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 zod 或其他 schema 驗證庫完整驗證所有欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0315

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行）bookingUrl 解析邏輯可能產生錯誤的 URL 前綴

> 在解析 bookingUrl 以取得前綴時，程式碼直接使用 `url.hostname` 而忽略了 port，且未處理 pathname 為空或僅有 slug 的情況。若 bookingUrl 為 `https://example.com:8080/user/slug`，前綴會變成 `https://example.com/user/`，遺失 port；若 bookingUrl 為 `https://example.com/slug`，則前綴會是 `https://example.com/`，可能不符合預期。建議使用 `url.origin` 並更嚴謹地處理路徑分段。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug ⏎ let prefix = "/";`

## P0316

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:98`，距錨點 0 行）移除 locale 欄位可能導致取消流程中翻譯失敗

> 在 `userSelect` 中移除了 `locale: true`，但取消流程中會使用 `organizer.locale` 來取得翻譯（`getTranslation(organizer.locale ?? "en", "common")`）。若 `locale` 欄位不再被選取，`organizer.locale` 將為 `undefined`，導致翻譯回退到英文，可能影響使用者體驗。請確認此變更是否為預期，或保留 `locale` 欄位。

finding 片段：`createdDate: true, ⏎ trialEndsAt: true, ⏎ completedOnboarding: true, ⏎ -  locale: true,`

## P0317

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0318

**GT**（func）Missing handleClose call in single-select mode prevents search input cleanup

> In the unselected options section for single-select mode, the code calls setOpen(false) but fails to call handleClose(), unlike the multiselect path which properly calls handleClose() when autoCloseOnSelect is enabled. This means when a user selects a single option, the popover closes but the search input state is never cleared, causing the next time the popover opens to show stale search results and filtered options from the previous interaction. The handleClose() function is responsible for clearing the search input and triggering the onClose callback, both of which are now skipped in single-select scenarios.

GT 片段：`} else { ⏎ onChange([option.value] as T[]); ⏎ setOpen(false); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1271`，距錨點 4 行）autoCloseOnSelect 在另一處多選分支中呼叫 handleClose，可能導致狀態不一致

> 在另一個多選分支中，當 autoCloseOnSelect 為 true 時呼叫 handleClose()，但 handleClose 會 setOpen(false) 並清空搜尋輸入。若使用者已達 maxSelections 上限，前面的 return 會阻止 onChange，但 handleClose 仍會執行，導致 popover 關閉但值未更新。建議將 handleClose 的呼叫放在 onChange 成功之後。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ handleClose(); ⏎ }`

## P0319

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）操作順序變更可能影響測試穩定性

> 在 testDisableTopSitesSettingsRemovesSection 中，原本先執行 navigator.goto(NewTabScreen) 再點擊 Done 按鈕，變更後順序相反。這可能導致測試在錯誤的畫面狀態下點擊 Done，進而影響後續驗證。建議確認此順序變更是否為必要，或恢復原順序。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0320

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 6 行）新增的 Task.Yield() 可能改變登出流程的時序

> 在 ProcessLogOut 中新增 `await Task.Yield();` 會讓出執行緒，可能導致後續的 AuthenticationState 取得延遲，或與其他非同步操作產生競態。若此變更非為了解決特定問題，建議移除；若為必要，請補充說明原因並確保測試涵蓋此情境。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## P0321

**GT**（rule）Line exceeds 110-character limit

> This newly added union member type definition is on a single line and exceeds the 110 character line-width limit mandated by Biome configuration.

GT 片段：`| { teamId: number; featureId: FeatureId; state: "enabled" | "disabled"; assignedBy: number; scope?: OptInFeatureScope }`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:264`，距錨點 20 行）setUserFeatureState 條件判斷反轉，可能導致 assignedBy 處理錯誤

> 原本的 `if (state === "inherit")` 被改為 `if (state !== "inherit")`，這使得當 state 為 "enabled" 或 "disabled" 時，會進入原本處理 inherit 的分支，嘗試從 input 中取得 `assignedBy` 並呼叫 `setUserFeatureState`。但 TypeScript 的 union type 保證在 state 非 inherit 時 input 一定包含 `assignedBy`，因此不會有 runtime error，但邏輯上與原本意圖相反。

**建議修法**：改回 `if (state === "inherit")`。

finding 片段：`if (state !== "inherit") {`

## P0322

**GT**（rule）Force unwrap of URL initializer in tests (second occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試永遠等待

> 在 testRequestMediaCaptureSuccess 中，原本的 expectation 是在 decisionHandler 內 fulfill，但修改後 decisionHandler 不再 fulfill，而是在呼叫 subject.webView 後直接呼叫 expectation.fulfill()。這會導致 expectation 在 decisionHandler 被呼叫前就 fulfill，使得 wait(for:) 立即返回，無法驗證 decisionHandler 是否真的被呼叫。若 decisionHandler 未被呼叫，測試仍會通過，失去測試意義。建議將 expectation.fulfill() 移回 decisionHandler 內。

finding 片段：`subject.webView(MockWKWebView(), ⏎ requestMediaCapturePermissionFor: origin, ⏎ initiatedByFrame: frame, ⏎ type: .cameraAndMicrophone,`

## P0323

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 2 行）autoCloseOnSelect 在多選時直接呼叫 onClose，可能繞過 maxSelections 限制

> 在多選分支中，當選取後若 field.autoCloseOnSelect 為 true，會直接呼叫 onClose?.()。但 onClose 通常會關閉 popover 並可能重置狀態，若使用者已達 maxSelections 上限，前面的 return 會阻止 onChange，但 autoCloseOnSelect 仍會執行，導致 popover 關閉但值未更新，造成狀態不一致。建議將 autoCloseOnSelect 的處理放在 onChange 成功之後，並確認 maxSelections 限制已正確處理。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## P0324

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2139`，距錨點 0 行）clusterCommonInit() 中 resetClusterStats() 可能重複初始化

> clusterCommonInit() 呼叫 resetClusterStats()，但原本 clusterInit() 中也呼叫 resetClusterStats()。現在 clusterInit() 中已移除該呼叫，但需確認沒有其他路徑重複初始化。

finding 片段：`resetClusterStats();`

## P0325

**GT**（func）Changed window naming pattern breaks window label consistency

> The window label format for dynamically created windows has been changed from "new-{number}" to "new-window-{number}". This breaks the established naming convention and will cause any code that attempts to retrieve or manipulate these windows using the expected label format to fail. For example, code trying to access "new-0" or "new-1" will not find the windows, as they are now named "new-window-0" and "new-window-1". This affects window management, event handling, and any window lookup operations that depend on the label pattern.

GT 片段：`let number = created_window_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed); ⏎ let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 11 行）`on_new_window` 回呼僅在桌面平台註冊，可能導致非桌面平台行為不一致

> 原本 `on_new_window` 回呼在所有平台都會註冊，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內。這表示在非桌面平台（如行動裝置）上，新視窗請求將不會被處理，可能導致應用程式無法開啟新視窗。若此為預期行為，建議在文件或註解中說明；否則應考慮保留跨平台支援。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## P0326

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> 新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0327

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:588`，距錨點 0 行）hasPendingInviteByUserId 的 accepted 條件寫反

> 方法名稱是 hasPendingInviteByUserId，但查詢條件為 `accepted: true`，這會回傳「已接受」的邀請，而非「待處理」的邀請。這導致呼叫端（onboarding 頁面與 checkOnboardingRedirect）在用戶有已接受邀請時誤判為有 pending invite，進而錯誤 redirect。應改為 `accepted: false`。

finding 片段：`accepted: true,`

## P0328

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0329

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:32`，距錨點 0 行）assert smtp is not None 為冗餘且可能被最佳化移除

> assert smtp is not None 在建立 SMTP 實例後立即執行，但該實例必定非 None，因此 assert 永遠為真。若使用 python -O 執行，assert 會被移除，不影響功能。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0330

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 minimal 模式下的 setLoading(false) 可能導致 UI 卡在載入狀態

> 在 minimal 模式且訂閱成功時，原本會呼叫 setLoading(false) 來結束載入狀態，但此 PR 移除了該行。若後續沒有其他機制將 loading 設為 false，按鈕可能持續顯示載入中。需確認成功狀態是否會自動重置 loading，否則應保留此行。

finding 片段：`setSuccess(true);`

## P0331

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行）XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，函式會回傳 nil，但呼叫端僅以 XCTFail 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果，並在逾時時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0332

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 18 行）Popover 的 hover 觸發可能導致點擊事件無法觸發

> 在桌面端，Popover 的開啟依賴於 onMouseEnter 和 onMouseLeave。當使用者將滑鼠移到觸發按鈕上時，Popover 會開啟，但當滑鼠移入 PopoverContent 時，由於 onMouseLeave 觸發，Popover 會立即關閉，導致使用者無法點擊隱藏項目。這是因為 PopoverContent 的 onMouseEnter 和 onMouseLeave 雖然有設定，但可能因為事件傳遞或元件結構問題而無法正確維持開啟狀態。建議改用 Radix Popover 的 hover 模式或使用延遲關閉機制，確保滑鼠在 PopoverContent 上時不會關閉。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0333

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺失變數 {newsletterName}

> 原文為 "{memberEmail} will no longer receive {newsletterName} newsletter."，翻譯改為 "{memberEmail}将不会再收到新闻信。"，遺漏了 {newsletterName} 變數。這會導致使用者看到的訊息缺少新聞信名稱，且可能造成 i18n 函式庫在插入變數時出現錯誤或顯示不完整。建議保留變數，例如："{memberEmail}将不会再收到{newsletterName}新闻信。"

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0334

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行）XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，函式會回傳 nil，但呼叫端僅以 XCTFail 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果，並在逾時時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0335

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:365`，距錨點 1 行）使用 Path.GetFullPath 比較路徑可能因相對路徑或符號連結而誤判

> 在檢查現有 SSL_CERT_DIR 是否已包含憑證目錄時，程式碼使用 `Path.GetFullPath(dir)` 與 `certDirFullPath` 進行比較。然而，`SSL_CERT_DIR` 中的路徑可能是相對路徑，或是包含符號連結，而 `Path.GetFullPath` 只會將相對路徑轉換為絕對路徑，但不會解析符號連結。這可能導致即使實際指向相同目錄，但因為路徑表示不同而被誤判為未包含，進而重複建議設定環境變數，或誤判為已包含而跳過必要的提示。建議使用 `Path.GetFullPath` 後再透過 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `FullName` 來處理符號連結，或使用 `Path.TrimEndingDirectorySeparator` 標準化路徑分隔符號。

finding 片段：`var certDirFullPath = Path.GetFullPath(prettyCertDir); ⏎ var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir))`

## P0336

**GT**（func）Variable scope error causes UnboundLocalError when template rendering succeeds

> The length validation check was moved inside the try block before the except clause, creating a critical variable scope issue. When `render_template()` succeeds, the `rendered` variable is assigned inside the try block. However, if the length check passes and no exception occurs, execution continues to the return statement outside the try-except block which references `rendered`. In Python, this creates an undefined variable scenario where `rendered` is only defined within the try block scope but accessed outside it, resulting in UnboundLocalError at runtime whenever template rendering succeeds without exceeding length limits.

GT 片段：`try: ⏎ rendered = self._template_renderer.render_template(self.node_data.template, variables) ⏎ if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH: ⏎ return NodeRunResult(`

**finding**（`api/core/workflow/nodes/template_transform/template_transform_node.py:41`，距錨點 27 行）CodeExecutorJinja2TemplateRenderer 未傳入 code_executor，可能導致依賴注入失效

> 在建構 `CodeExecutorJinja2TemplateRenderer` 時未傳入 `code_executor`，若 `CodeExecutor` 類別依賴其他元件（如設定），可能無法正確初始化。建議從 `NodeFactory` 傳入已建立的 `code_executor` 實例，或確認此處使用預設值是否安全。

finding 片段：`self._template_renderer = template_renderer or CodeExecutorJinja2TemplateRenderer()`

## P0337

**GT**（func）Incorrect parameter name prevents timeout configuration in test harness

> The test fixture uses `server_timeout=60` when calling `prefect_test_harness()`, but the correct parameter name is `server_startup_timeout`. This means the intended 60-second timeout is not actually applied, leaving tests vulnerable to the same timeout issues in CI environments that the change was meant to fix. The prefect_test_harness function will ignore the invalid parameter and use its default timeout value instead, potentially causing intermittent test failures when multiple xdist workers start simultaneously in CI.

GT 片段：`# Increase timeout for CI environments where multiple xdist workers ⏎ # start servers simultaneously, which can be slower on Python 3.11+ ⏎ # See https://github.com/PrefectHQ/prefect/issues/16397 ⏎ with prefect_test_harness(server_timeout=60):`

**finding**（`src/integrations/prefect-gcp/tests/conftest.py:19`，距錨點 0 行）移除 disable_logging fixture 可能導致測試輸出過多

> 原本的 `disable_logging` fixture 會關閉 logging to API，移除後可能導致測試期間產生大量 log 輸出，影響 CI 效能或掩蓋重要訊息。若確有必要移除，應確認測試環境已設定適當的 log level。

finding 片段：`with prefect_test_harness(server_timeout=60): ⏎ yield`

## P0338

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142`，距錨點 0 行）handleDragEnd 中 moveItem 參數順序錯誤導致拖曳方向相反

> 在 `handleDragEnd` 中，`moveItem(newIndex, oldIndex)` 的參數順序可能與 `moveItem` 的預期相反。從既有程式碼 `moveUp={() => moveItem(index, index - 1)}` 和 `moveDown={() => moveItem(index, index + 1)}` 推測，`moveItem` 的第一個參數是來源索引，第二個是目標索引。但拖曳時，`oldIndex` 是來源，`newIndex` 是目標，因此應呼叫 `moveItem(oldIndex, newIndex)`。目前寫法會導致拖曳後項目移動到錯誤位置，甚至可能超出陣列範圍。

finding 片段：`moveItem(newIndex, oldIndex);`

## P0339

**GT**（rule）Strict mode disabled in TypeScript config

> The rule requires TypeScript configuration files to have 'strict' set to true in compilerOptions, but it was set to false

GT 片段：`/* Linting */ ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`apps/activitypub/tsconfig.json:18`，距錨點 0 行）關閉 TypeScript strict 模式

> 將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更應有充分理由，否則應恢復為 `true` 並修正相關型別錯誤。

finding 片段：`"strict": false,`

## P0340

**GT**（func）Missing error source for Plist variant breaks error chain

> The Error::source() implementation is missing a case for Error::Plist, which wraps a plist::Error. This breaks error chain propagation when plist parsing or writing fails. The Plist variant is used for reading and writing application configuration files and provisioning profiles, making it one of the most commonly encountered errors. Without proper error source propagation, debugging tools and error context mechanisms lose access to the underlying plist parsing errors, making it difficult to diagnose configuration file issues.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行）手動實作 Error trait 可能遺漏 source 方法

> 新的 Error 實作中，`source()` 方法僅回傳部分變體的底層錯誤（TempDir、FailedToUploadApp、CommandFailed、Fs），其他變體（如 Plist、X509Certificate 等）未提供 source。這可能導致錯誤鏈不完整，影響使用 `anyhow` 或 `thiserror` 的呼叫端。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## P0341

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0342

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## P0343

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:17`，距錨點 0 行）非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題

> `LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 `await`，但該方法現在是 async 且 @MainActor）。這可能導致編譯錯誤或執行緒問題。建議將測試類別標記為 `@MainActor`，並確保呼叫方式正確。

finding 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

## P0344

**GT**（rule）Pydantic v1 Config class usage

> The rule requires data validation to use Pydantic v2 with ConfigDict(extra='forbid'), but this code uses Pydantic v1 'class Config' syntax with 'extra = allow' which permits undeclared fields

GT 片段：`class AgentThoughtValidation(BaseModel): ⏎ """ ⏎ Validation model for agent thought data before database persistence. ⏎ """`

**finding**（`api/core/agent/base_agent_runner.py:64`，距錨點 0 行）AgentThoughtValidation 模型未被使用且 extra 設定錯誤

> 新增的 AgentThoughtValidation 模型定義了 `extra = "allow"`，但註解指出應使用 `ConfigDict(extra='forbid')`。此外，此模型在 diff 中未見任何使用，可能為多餘程式碼。若未來用於驗證，應修正 extra 設定以嚴格拒絕未知欄位，避免意外接受未預期的資料。

finding 片段：`class Config: ⏎ extra = "allow"  # Pydantic v1 syntax - should use ConfigDict(extra='forbid')`

## P0345

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行）回傳 &'static Path 可能造成懸垂指標

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但實際上是從 `OnceLock<PathBuf>` 中取得的參考。雖然 `OnceLock` 是靜態的，但 `PathBuf` 的內容可能在未來被修改或釋放，導致懸垂指標。

具體情境：如果 `OnceLock` 中的值被重新設定（例如在測試中），舊的參考將失效。

建議：改為擁有所有權的 `PathBuf`，或使用 `Arc<Path>` 等安全共享型別。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## P0346

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 0 行）使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤

> 原本使用 `deployment.id`，修改後改為 `deployment_id`。若 `deployment_id` 是字串而 API 預期 UUID，可能導致型別錯誤。請確認 `deployment_id` 的型別與 API 要求一致。

finding 片段：`deployment_id,`

## P0347

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 12 行）require 陳述式缺少分號

> 多個 require 陳述式（如 `const PaymentsService = require('./services/payments-service')`）缺少行尾分號，與專案風格不一致。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## P0348

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）console.log 可能洩漏使用者輸入資料

> 新增的 `console.log` 會將批次輸入的資料（包含使用者提供的內容）輸出到瀏覽器主控台。這可能導致敏感資訊外洩，且不應存在於正式程式碼中。

建議移除該行。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0349

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈條件錯誤導致堆積緩衝區溢位

> 在 `extractSlotFromKeysResult` 中，迴圈條件 `j <= keys_result->numkeys` 會多執行一次，而 `slot_buffer` 只配置了 `keys_result->numkeys` 個元素，因此最後一次迭代會寫入 `slot_buffer[numkeys]`，造成堆積緩衝區溢位。此外，該次迭代還會讀取 `argv[keys_result->keys[numkeys].pos]`，可能讀取到未初始化的記憶體。

建議將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0350

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 3 行）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## P0351

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 0 行）多渲染器情境下 manager 被覆寫但未處理舊 manager

> 當 `currentRendererId !== rendererId` 時，程式會直接覆寫 `manager` 與 `currentRendererId`，但未對舊的 `manager` 做任何處理。雖然註解提到舊的 manager 已失效，但若舊渲染器仍存活（例如同時存在多個電路），可能導致舊渲染器的後續呼叫使用到錯誤的 manager。

建議確認此情境是否可能發生，若可能，應考慮以 Map 管理多個 manager，或明確禁止多渲染器同時啟用。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## P0352

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0353

**GT**（func）High-volume threshold boundary applies wrong scaling factor at 400k

> The condition uses `>=` instead of `>` when checking if lastCount qualifies for high-volume capping at exactly 400,000 emails. According to the documented scaling table, 400k should use the 2× multiplier from the thresholds array, but with this bug it immediately applies the high-volume cap of 1.2× or +75k absolute increase. For a site hitting exactly 400k messages, this means getting a limit of 480k (1.2×) or 475k (+75k) instead of the expected 800k (2×). This creates a significant bottleneck at a critical growth milestone and breaks the documented warmup progression.

GT 片段：`// For high volume senders (400k+), cap the increase at 20% or 75k absolute ⏎ if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold) { ⏎ const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 0 行）高流量分支的計算可能導致上限下降

> 在 `lastCount >= 400000` 時，回傳 `Math.min(scaledIncrease, absoluteIncrease)`。其中 `scaledIncrease = Math.ceil(lastCount * 1.2)`，`absoluteIncrease = lastCount + 75000`。當 `lastCount` 大於 375000 時，`absoluteIncrease` 會小於 `scaledIncrease`，因此回傳 `lastCount + 75000`。這可能導致暖機上限的成長幅度低於預期，但仍在合理範圍內。建議確認此行為是否符合產品需求。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## P0354

**GT**（func）Missing try keyword in async throws method call

> The IpadOnlyTestCase.setUp() method is marked as 'async throws' but calls 'await super.setUp()' without the 'try' keyword. Since BaseTestCase.setUp() is declared as 'async throws', this means any errors thrown by the parent setUp will not be properly propagated and will instead cause a compilation error or runtime crash. This breaks the error handling contract for all iPad-specific test cases that inherit from IpadOnlyTestCase, potentially causing test suite failures or silent test skips.

GT 片段：`class IpadOnlyTestCase: BaseTestCase { ⏎ override func setUp() async throws { ⏎ specificForPlatform = .pad ⏎ if iPad() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:512`，距錨點 0 行）IpadOnlyTestCase 中呼叫 super.setUp() 缺少 try

> 在 IpadOnlyTestCase 的 setUp() 中，呼叫 `await super.setUp()` 但未加上 `try`。由於父類別的 setUp() 現在是 `async throws`，此處會導致編譯錯誤。應改為 `try await super.setUp()`。

finding 片段：`await super.setUp()`

## P0355

**GT**（func）Container created on every function call breaks singleton pattern

> The getFeaturesRepository() function now creates a new DI container instance on every invocation instead of reusing a module-level singleton container. This causes each call to return a different FeaturesRepository instance with its own PrismaClient connection, breaking the singleton pattern. This leads to database connection pool exhaustion and inconsistent cached state across repository instances, as FeaturesRepository maintains an internal cache for features (line 34 in features.repository.ts checks FeaturesRepository.featuresCache).

GT 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 0 行）每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## P0356

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有除法或轉換可能出錯）。建議回傳 `emailCount` 或一個明確的常數（如 `Number.MAX_SAFE_INTEGER`），並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0357

**GT**（func）Missing error source for FailedToEncodeDER variant

> The Error::source() implementation is missing a case for Error::FailedToEncodeDER, which wraps an std::io::Error. This breaks error chain propagation when DER encoding fails. Callers using error context or debugging tools that traverse the error chain will lose the underlying IO error information, making it difficult to diagnose encoding failures. The original PR explicitly added source() support for this variant in the thiserror migration, but this manual implementation omits it.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行）手動實作 Error trait 可能遺漏 source 方法

> 新的 Error 實作中，`source()` 方法僅回傳部分變體的底層錯誤（TempDir、FailedToUploadApp、CommandFailed、Fs），其他變體（如 Plist、X509Certificate 等）未提供 source。這可能導致錯誤鏈不完整，影響使用 `anyhow` 或 `thiserror` 的呼叫端。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## P0358

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行）checkOnboardingRedirect 條件變更可能導致非預期行為

> 原本的條件是 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示即使沒有 pending invite，只要 `onboardingV3Enabled` 為 true，使用者就會被導向 `/onboarding/personal/settings`。這可能改變了原本的邏輯：原本只有在有 pending invite 且啟用 onboarding-v3 時才導向，現在只要啟用 onboarding-v3 就會導向。

**失敗情境**：如果系統啟用了 onboarding-v3，但使用者沒有 pending invite，原本可能應該走其他 onboarding 流程，現在卻會被強制導向 personal settings，可能造成流程中斷或錯誤。

**建議修法**：確認此變更是否符合預期。若原本邏輯正確，應保留 `&&`；若確實需要 `||`，請在 PR 描述中說明原因。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) {`

## P0359

**GT**（func）Race condition: semaphore initialized after clients during startup

> The `_startup_event_semaphore` is initialized after the orchestration and events clients are created and started. This creates a race condition where Kubernetes pods detected during the client startup phase can trigger `_replicate_pod_event` calls before the semaphore exists. When `event_type` is `None` (startup scenario), the code checks `if _startup_event_semaphore is None` and raises a RuntimeError. However, pods may be detected immediately after clients start but before the semaphore initialization completes, causing the observer to crash with 'Startup event semaphore not initialized' errors during high pod count scenarios.

GT 片段：`@kopf.on.startup() ⏎ async def initialize_clients(logger: kopf.Logger, **kwargs: Any): ⏎ logger.info("Initializing clients") ⏎ global events_client`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:47`，距錨點 3 行）全域變數 `_startup_event_semaphore` 缺乏型別標註與初始化說明

> 新增的全域變數 `_startup_event_semaphore` 宣告為 `asyncio.Semaphore | None = None`，但未在模組 docstring 或註解中說明其生命週期與使用方式。這可能導致未來維護者誤用或未正確初始化。建議加入簡短註解說明其用途與初始化時機。

finding 片段：`_startup_event_semaphore: asyncio.Semaphore | None = None`

## P0360

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:202`，距錨點 0 行）fail 方法中 action.triggered 事件的 related 指派錯誤

> 在 `fail` 方法中，建立 `prefect.automation.action.triggered` 事件時，`related` 參數被指派為 `self._resulting_related_resources`，而非包含 triggering-event 和 automation-triggered-event 的 `related_resources`。這會導致 action.triggered 事件缺少應有的相關資源，破壞事件追蹤鏈。

失敗情境：當 action 失敗時，發出的 `prefect.automation.action.triggered` 事件將不包含任何相關資源，使用者無法從該事件追溯到觸發事件或 automation.triggered 事件。

建議修法：將該事件的 `related` 參數改為 `related_resources`。

finding 片段：`related=self._resulting_related_resources,`

## P0361

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行）active defrag 恢復邏輯可能錯誤地啟用 defrag

> 在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

finding 片段：`server.active_defrag_enabled = 1;`

## P0362

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行）mark_edge_skipped 順序調整可能影響遞迴邏輯

> 將 `mark_edge_skipped` 移到 `propagate_skip_from_edge` 之後，可能導致在遞迴過程中邊的狀態尚未被標記為 skipped，若遞迴中再次檢查該邊的狀態可能得到不一致的結果。建議確認此順序調整是否為必要，並確保不會影響其他邏輯。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0363

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行）使用子字串比對判斷路徑前綴，可能誤判

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，若 `path` 中包含 bucket_folder 但並非前綴（例如 `path = "myresults/abc"` 且 `bucket_folder = "results/"`），會錯誤地視為已前綴而直接返回，導致路徑未正確解析。應改為檢查 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0364

**GT**（func）Incorrect initialization order in test setup

> In FeatureFlaggedTestSuite.setUp(), the method calls setUpApp() before setUpExperimentVariables(). However, setUpApp() (line 42-44) directly uses jsonFileName and featureName properties that are initialized by setUpExperimentVariables(). This means setUpApp() will be called with nil or uninitialized values, causing addLaunchArgument() to receive invalid parameters. This breaks the experiment/feature flag configuration for all tests inheriting from FeatureFlaggedTestSuite, resulting in tests running with incorrect or missing feature flags.

GT 片段：`override func setUp() async throws { ⏎ continueAfterFailure = false ⏎ setUpApp()  // Called before setUpExperimentVariables ⏎ setUpExperimentVariables()  // Sets jsonFileName and featureName`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48`，距錨點 0 行）setUp 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試

> 原本的順序是先呼叫 `setUpExperimentVariables()` 再呼叫 `setUpApp()`，但變更後順序顛倒。如果 `setUpApp()` 依賴於實驗變數的設定（例如 launch arguments 中包含實驗變數），則可能導致測試行為不正確。

建議確認此順序變更是否為有意為之，若無必要請恢復原順序。

finding 片段：`setUpApp() ⏎ setUpExperimentVariables()`

## P0365

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 2 行）useEffect 依賴陣列缺少 item.html，可能導致判斷不準確

> `useEffect` 僅在掛載時執行一次，但 `item.html` 可能因資料更新而改變。若內容變更，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示與否不正確。建議將 `item.html` 加入依賴陣列，或在內容變更時重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0366

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:46`，距錨點 2 行）SQLite 上完全沒有鎖保護，競態仍可能發生

> 在 SQLite 上，`acquire_composite_trigger_lock` 直接返回，沒有取得任何鎖。雖然 SQLite 的寫入序列化可能降低機率，但讀取與寫入之間仍可能交錯，導致兩個 worker 都讀到相同的 child firings 並各自嘗試刪除，最終只有一個成功，但另一個可能已經通過檢查並觸發父觸發器。建議對 SQLite 使用其他機制（例如樂觀鎖或應用層級的鎖）。

finding 片段：`# SQLite doesn't support advisory locks, but SQLite also serializes writes ⏎ # at the database level, so the race condition is less likely to occur`

## P0367

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0368

**GT**（func）Changed window naming pattern breaks window label consistency

> The window label format for dynamically created windows has been changed from "new-{number}" to "new-window-{number}". This breaks the established naming convention and will cause any code that attempts to retrieve or manipulate these windows using the expected label format to fail. For example, code trying to access "new-0" or "new-1" will not find the windows, as they are now named "new-window-0" and "new-window-1". This affects window management, event handling, and any window lookup operations that depend on the label pattern.

GT 片段：`let number = created_window_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed); ⏎ let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 11 行）on_new_window 移至 cfg(desktop) 區塊可能改變非桌面平台行為

> 原本 `on_new_window` 的設定在所有平台都會執行，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內，這表示在非桌面平台（如行動裝置）上，新視窗的建立邏輯將不會被註冊。如果這是預期的行為變更，請確認；否則可能導致非桌面平台無法正確處理新視窗請求。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## P0369

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0370

**GT**（rule）Line exceeds 110 character limit (Biome formatting rule)

> The added line appears to exceed the configured 110 character line width requirement, violating the repo's Biome formatting standards.

GT 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:28`，距錨點 0 行）傳給 useProcessTeamMembersData 的 matchingTeamMembersWithResult 型別可能不符

> `useProcessTeamMembersData` 預期 `matchingTeamMembersWithResult` 的型別為 `RouterOutputs['viewer']['attributes']['findTeamMembersMatchingAttributeLogic']`，但此處傳入的 `matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult` 可能導致型別不符。請確認型別定義並修正。

finding 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

## P0371

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1722`，距錨點 5 行）AOF_BROKEN_RECOVERED 在非最後一個檔案時未正確處理，可能導致資料不一致

> 在 loadAppendOnlyFiles 中，當 ret == AOF_BROKEN_RECOVERED 且 !last_file 時，程式碼將 ret 設為 AOF_FAILED 並記錄錯誤，但隨後在 if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) 的條件中，因為 ret 已被改為 AOF_FAILED，所以會進入 cleanup 並中止載入。然而，此處的邏輯有問題：如果 AOF_BROKEN_RECOVERED 發生在非最後一個檔案，實際上檔案已被 truncate 修改，但後續的檔案仍可能被載入，導致資料不一致。建議在非最後一個檔案遇到 AOF_BROKEN_RECOVERED 時，應立即中止載入並回報錯誤，且不應修改原始檔案。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0372

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 0 行）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## P0373

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）在迴圈內呼叫 flush，且 flush 為空實作

> `on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0374

**GT**（func）Browser navigation uses Forward() instead of Back() breaking test flow

> In the RedirectEnhancedGetToInternal test, after clicking a link that redirects from /redirect to /scroll-to-hash, the test attempts to verify that browser back navigation works correctly. However, the code calls Browser.Navigate().Forward() instead of Browser.Navigate().Back(). Since there is no forward history (the browser just navigated forward to the current page), Forward() does nothing and the browser remains at /scroll-to-hash. The subsequent assertions expect the browser to be back at /redirect with the "Redirections" heading, but it's still at the redirected page, causing the test to fail. The comment explicitly states "See that 'back' takes you to the place from before the redirection" but the code does the opposite action.

GT 片段：`// See that 'back' takes you to the place from before the redirection ⏎ Browser.Navigate().Forward(); ⏎ Browser.Equal("Redirections", () => _originalH1Element.Text); ⏎ Assert.EndsWith("/subdir/redirect", Browser.Url);`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:113`，距錨點 0 行）Forward 取代 Back 可能不符合測試意圖

> 原本測試使用 Back 來驗證返回上一頁，現在改為 Forward。若測試目的是驗證返回行為，此變更可能使測試失去意義。需確認是否為預期修正，否則應保留 Back。

finding 片段：`Browser.Navigate().Forward();`

## P0375

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0376

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 19 行）Popover 的 hover 觸發可能導致點擊事件無法觸發

> 在桌面端，Popover 的開啟依賴於 onMouseEnter 和 onMouseLeave。當使用者將滑鼠移到觸發按鈕上時，Popover 會開啟，但當滑鼠移入 PopoverContent 時，由於 onMouseLeave 觸發，Popover 會立即關閉，導致使用者無法點擊隱藏項目。這是因為 PopoverContent 的 onMouseEnter 和 onMouseLeave 雖然有設定，但可能因為事件傳遞或元件結構問題而無法正確維持開啟狀態。建議改用 Radix Popover 的 hover 模式或使用延遲關閉機制，確保滑鼠在 PopoverContent 上時不會關閉。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`
