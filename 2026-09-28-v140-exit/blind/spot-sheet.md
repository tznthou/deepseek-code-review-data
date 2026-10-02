# 盲標單 （主 session 抽樣）：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/spot-main.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0016

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 原本的驗證條件 `value <= 0` 會拒絕 0 和負數，但變更後只拒絕負數，允許 0。若設定為 0，可能導致不保留任何檔案，造成資料遺失或非預期行為。建議確認 0 是否為有效值，若不是，應維持原本的 `<= 0` 驗證。

finding 片段：`if (value < 0)`

## P0027

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 4 行）GTK 腳本存在性檢查邏輯反轉

> 原本的邏輯是「若檔案不存在，則下載並寫入」，但修改後變成「若檔案存在，則寫入內嵌內容」。這會導致：
1. 當檔案不存在時，不會建立該檔案，後續執行可能因缺少腳本而失敗。
2. 當檔案已存在時，會用內嵌內容覆蓋，可能破壞使用者自訂的腳本。

建議改回 `if !gtk.exists()` 的條件。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0070

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:133`，距錨點 14 行）`get_or_create_client` 可能建立非預期的 client

> 原本使用 `@inject_client` 裝飾器，會根據上下文注入 client，若未提供則建立新的 client。現在改為 `get_or_create_client(client)`，其行為可能不同：若 `client` 為 None，它會建立一個新的 client，但可能未正確處理與目前執行中 flow run 的關聯（例如使用相同的 API URL 或認證）。這可能導致在 flow 內呼叫時無法正確連結父子關係。

建議：確認 `get_or_create_client` 的實作是否符合預期，或保留原本的 `@inject_client` 機制。

finding 片段：`client, _ = get_or_create_client(client)`

## P0107

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0217

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 建立的 robj 未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後未呼叫 decrRefCount 釋放。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。建議在 alsoPropagate 呼叫後立即釋放 argv[2]，或改用其他方式避免手動管理記憶體。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0241

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert smtp is not None 為冗餘且可能被最佳化移除

> assert smtp is not None 在建立 SMTP 實例後立即執行，但該實例必定非 None，因此 assert 永遠為真。若使用 python -O 執行，assert 會被移除，不影響功能。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0306

**GT**（rule）WebServer class missing final keyword

> The WebServer class is not designed for subclassing (it implements a singleton pattern with sharedInstance) but lacks the 'final' keyword, allowing unintended inheritance and missing compiler optimization opportunities

GT 片段：`class WebServer: WebServerProtocol, @unchecked Sendable { ⏎ static let sharedInstance = WebServer() ⏎ private let logger: Logger ⏎ let server = GCDWebServer()`

**finding**（`firefox-ios/Client/Application/WebServer.swift:59`，距錨點 38 行）移除 @Sendable 可能導致 handler 閉包在非主執行緒執行時產生資料競爭

> `WebServer` 類別被標記為 `@unchecked Sendable`，但其 handler 閉包現在不再要求 `@Sendable`。若 handler 閉包捕獲非 Sendable 的狀態，且該閉包在非主執行緒被呼叫，可能導致資料競爭。建議確認 GCDWebServer 呼叫 handler 的執行緒，若可能非主執行緒，應保留 `@Sendable` 或確保閉包內只存取 Sendable 狀態。

finding 片段：`handler: @escaping @MainActor ( ⏎ _ request: GCDWebServerRequest?, ⏎ _ responseCompletion: @escaping @Sendable (GCDWebServerResponse?) -> Void ⏎ ) -> Void`

## P0382

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## P0390

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行）條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions

> 在 `create_info_plist` 中，原本的程式碼無條件加入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才加入。這會導致當 `ext` 非空時（正常情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，造成檔案關聯失效。

**失敗情境**：使用者設定 `ext: ["png"]`，產生的 Info.plist 將缺少 `CFBundleTypeExtensions`，macOS 無法將 .png 檔案與應用程式關聯。

**建議**：移除 `if association.ext.is_empty()` 條件，改回無條件加入，或改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0434

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0463

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）versionCode 達到上限時靜默飽和

> 使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0500

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）async setUp 中呼叫 @MainActor async 方法缺少 await

> 在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()`，但該方法已標記為 `@MainActor` 且為 async，此處未加 `await`，將導致編譯錯誤。

建議改為：
```swift
await DependencyHelperMock().bootstrapDependencies()
```

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0574

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行）scheduling.init() 呼叫方式變更可能導致 API URL 遺失

> 原本 `scheduling.init()` 會傳入 `{apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)}`，但修改後改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確運作。請確認 `scheduling.init()` 是否已有其他方式取得 API URL，或此變更是否為有意為之。

finding 片段：`scheduling.init(),`

## P0595

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）骨架視圖約束可能錯誤：toolbar.leadingAnchor 應約束到 leftSkeletonAddressBar.trailingAnchor

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor` 約束到 `leftSkeletonAddressBar.trailingAnchor`，但此 PR 將其改為 `rightSkeletonAddressBar.trailingAnchor`。這可能導致 toolbar 的左側與右側骨架視圖的右側對齊，造成佈局錯亂。請確認此變更是否為預期行為，若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0609

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:129`，距錨點 8 行）Semaphore 僅在 event_type 為 None 時使用，可能無法涵蓋所有啟動事件

> Semaphore 僅在 `event_type is None` 的分支中使用，但啟動時可能還有其他事件類型（如 `ADDED`）也需要限制並發。若啟動時大量 `ADDED` 事件同時觸發，仍可能造成 API 過載。建議確認啟動期間所有事件類型都應受 semaphore 限制。

finding 片段：`if event_type is None: ⏎ if orchestration_client is None: ⏎ raise RuntimeError("Orchestration client not initialized") ⏎ if _startup_event_semaphore is None:`

## P0628

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 6 行）新增的 Task.Yield() 可能造成登出流程的競態或延遲

> 在 `ProcessLogOut` 中，於取得驗證狀態前新增了 `await Task.Yield();`。這可能導致登出流程延遲，且若 `AuthenticationProvider.GetAuthenticationStateAsync()` 依賴某些同步狀態，可能引入競態。建議移除或提供明確理由。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎  ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

## P0659

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行）移除 `strict=True` 可能掩蓋 zip 長度不匹配

> 原本使用 `zip(pool_names_list, results, strict=True)` 會在長度不一致時拋出 `ValueError`，現在移除 `strict=True` 後，若 `pool_names_list` 和 `results` 長度不同，多餘的元素會被靜默忽略，可能導致部分工作池未被處理且無任何警告。建議保留 `strict=True` 或手動檢查長度。

finding 片段：`for name, result in zip(pool_names_list, results):`

## P0679

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）_serverToken 型別變更可能導致後續使用錯誤

> `_serverToken` 原本存 token 字串，現在改存整個 token 物件（包含 `token` 和 `exp`）。若其他程式碼仍預期 `_serverToken` 是字串，可能導致型別錯誤或功能失效。請確認所有使用 `_serverToken` 的地方都已更新。

finding 片段：`this._serverToken = tokenData;`

## P0690

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68`，距錨點 15 行）輪詢可能產生競態條件

> `confirmHandle` 使用 `mutateAsync` 但未處理錯誤，且輪詢間隔固定為 5 秒。若前一次請求尚未完成，下一次輪詢可能同時發出多個請求，導致伺服器壓力或狀態不一致。此外，若 `confirmBlueskyHandleMutation` 失敗（例如網路錯誤），錯誤未被捕獲，可能造成 unhandled rejection。建議在 `confirmHandle` 中加入錯誤處理，並考慮使用 `isPending` 或鎖定機制避免重疊請求。

finding 片段：`const confirmHandle = useCallback(() => { ⏎ confirmBlueskyHandleMutation.mutateAsync().then((handle) => { ⏎ if (handle) { ⏎ setHandleConfirmed(true);`

## P0694

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0697

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0699

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0714

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:274`，距錨點 3 行）將同步閉包改為 Task 可能改變執行順序與時機

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會將原本同步的呼叫變成非同步，可能導致呼叫端預期完成後立即執行的程式碼延後執行，或與其他非同步操作產生競態。此外，Task 未處理取消或錯誤，若 handleAction 拋出錯誤，可能導致未處理的錯誤。建議確認此變更的必要性，並考慮使用 Task { @MainActor in ... } 確保在主執行緒執行，或保留同步呼叫並調整閉包標註。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0718

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳值型別錯誤：使用 Python 的 `True` 而非 JavaScript 的 `true`

> 在 `handleJSONSchemaChange` 函式中，成功解析 JSON 後回傳了 `True`（Python 布林值），但在 JavaScript/TypeScript 中應為 `true`。這會導致回傳值型別不一致，且若呼叫端依賴此回傳值，可能造成非預期行為。建議改為 `return true`。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0749

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:25`，距錨點 0 行）throttle 方法中 lastExecutionTime 更新順序改變可能影響節流邏輯

> 原本 `lastExecutionTime` 在 guard 之後才更新，現在移到 guard 之前。這可能導致在 threshold 條件不滿足時也更新了時間，影響後續呼叫的節流判斷。請確認此變更是否為預期行為。

finding 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

## P0752

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1125`，距錨點 0 行）複製連結功能未使用 bookingUrl，可能導致不一致

> 在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接 `https://cal.com/${username}/${slug}`，而未使用 `eventType.bookingUrl`。這與其他地方的修改不一致，可能導致使用者複製到舊格式的連結。建議統一使用 `eventType.bookingUrl` 或提供一致的 fallback。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## P0783

**GT**（func）Incorrect async Task wrapper breaks MainActor isolation in onboarding action handler

> The onActionTap closure is wrapped in a Task block without ensuring MainActor isolation. The OnboardingFlowViewModel expects this closure to be @MainActor isolated, but Task {} creates a new async context that may execute on a different executor. This causes the completion handler and handleAction calls to potentially run off the main thread, leading to concurrency violations and potential crashes when UI updates occur. The original code directly called onboardingService.handleAction which maintained proper MainActor isolation.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in ⏎ guard let onboardingService = self?.onboardingService else { return } ⏎ Task { ⏎ onboardingService.handleAction(`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行）將 onActionTap 閉包內容包在 Task 中可能改變執行順序與錯誤處理

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使得 handleAction 的執行變成非同步，可能導致呼叫端預期的同步行為失效。例如，若 handleAction 內部有需要立即完成的狀態更新，或 completion 需要在特定時序被呼叫，延遲可能造成 UI 不一致。此外，Task 中未處理可能的錯誤（如 handleAction 拋錯），可能導致錯誤被吞掉。建議確認 handleAction 是否為非同步設計，或考慮使用 Task { @MainActor in ... } 並明確處理錯誤。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0784

**GT**（rule）Test method missing test prefix

> The rule requires test methods to start with 'test' prefix, but the method 'verifyBookmarksShareNormalWebsiteReminders' does not follow this naming convention

GT 片段：`// https://mozilla.testrail.io/index.php?/cases/view/2864380 ⏎ func verifyBookmarksShareNormalWebsiteReminders() { ⏎ app.launch() ⏎ if #available(iOS 17, *) {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47`，距錨點 0 行）測試方法改名後失去 test 前綴，可能不再被 XCTest 執行

> 方法 `testBookmarksShareNormalWebsiteReminders` 被改名為 `verifyBookmarksShareNormalWebsiteReminders`，但 XCTest 只會自動執行以 `test` 開頭的方法。若此方法原本是測試案例，改名後將不再被執行，導致測試覆蓋率下降。建議保留 `test` 前綴，或確認此方法已改為輔助方法並有對應的測試呼叫。

finding 片段：`func verifyBookmarksShareNormalWebsiteReminders() {`

## P0791

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容變成工具輸入，而非實際的觀察結果，造成歷史訊息錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史記錄中的工具回應會顯示輸入參數而非輸出結果，影響後續模型理解上下文。

建議改回使用 `tool_responses`，並考慮是否需要 `str()` 轉換。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0807

**GT**（rule）UI-related test lifecycle method not annotated with @MainActor

> This test creates/configures a UIViewController in setUp, which is UI work. Rule 9 requires UI-related code to be annotated with @MainActor (either on the class or the method). The modified setUp() signature is not annotated and the class is not marked @MainActor in the diff.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/SyncContentSettingsViewControllerTests.swift:15`，距錨點 0 行）缺少 @MainActor 標註可能導致 UI 操作在背景執行緒執行

> 此測試類別操作 UI 元件（SyncContentSettingsViewController），但未加上 @MainActor 標註。在 Swift 6 中，若測試方法未標註 @MainActor，則 setUp/tearDown 可能不在主執行緒執行，導致 UI 相關操作失敗或產生不可預期的行為。建議在類別宣告前加上 @MainActor。

finding 片段：`class SyncContentSettingsViewControllerTests: XCTestCase {`
