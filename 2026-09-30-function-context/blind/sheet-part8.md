# 盲標單 8：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part8.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0701

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15`，距錨點 0 行）排程條件反轉導致重複排程

> 原本條件為 `!hasScheduled.processOutbox`，修改後變成 `hasScheduled.processOutbox`，這會導致當 `hasScheduled.processOutbox` 為 true 時再次呼叫 `jobsService.addJob`，造成重複排程。應改回 `!hasScheduled.processOutbox`。

finding 片段：`if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`

## P0702

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行）getDisplayEmail 缺少單元測試

> 新增的 `getDisplayEmail` 方法沒有對應的單元測試，尤其是針對各種 email 格式（含加號、無加號、多個加號等）的處理。建議新增測試以確保行為正確。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## P0703

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:56`，距錨點 35 行）Trans mock 未處理 components prop，可能導致依賴該 prop 的測試失敗

> `createTransMock` 回傳的 `Trans` 元件僅接收 `i18nKey` 和 `children`，但實際 react-i18next 的 `Trans` 元件常使用 `components` prop 來插入自訂元件。若元件使用 `<Trans i18nKey="..." components={{ trustSource: <TrustSource /> }} />`，此 mock 會忽略 `components`，導致渲染結果與實際不符，可能使測試無法正確驗證。建議在 `Trans` mock 中處理 `components` prop，例如將 `components` 中的元件渲染在對應位置。

finding 片段：`Trans: ({ i18nKey, children }: { ⏎ i18nKey: string ⏎ children?: React.ReactNode ⏎ }) => {`

## P0704

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1125`，距錨點 0 行）使用 var 宣告 newValues

> 在 inline 模式的 multiselect 分支中，`newValues` 使用 `var` 宣告，而其他類似處使用 `const`。這可能是筆誤，建議改為 `const` 以維持一致性並避免潛在的變數提升問題。

finding 片段：`var newValues = [...effectiveValues, option.value] as T[];`

## P0705

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call, long value string, and long comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextRollouts = NSLocalizedString("Settings.detailTextRollouts", value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", comment: "Description associated to the Rollouts toggle on the settings screen. %@ is the app name (for example \`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:202`，距錨點 7 行）comment 中的引號變更可能影響翻譯工具

> `detailTextSendUsageData` 和 `detailTextStudies` 的 comment 從智慧引號（“ ”）改為直引號（" "）。這可能導致翻譯工具將這些 comment 視為不同，造成翻譯記憶庫不一致。建議確認此變更是否必要，並保持 comment 風格一致。

finding 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

## P0706

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291`，距錨點 7 行）新增的 Task.Yield() 可能造成不必要的延遲

> 在取得 AuthenticationState 前加入 await Task.Yield()，可能是為了避免同步阻塞，但若呼叫端已非同步，此舉可能增加延遲。建議確認其必要性，或改用 ConfigureAwait(false) 以提升效能。

finding 片段：`await Task.Yield();`

## P0707

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外

> 在解析現有 SSL_CERT_DIR 時，程式碼對每個目錄呼叫 `Path.GetFullPath(dir)`，但僅以 `catch` 捕捉例外並回傳 false。然而，`Path.GetFullPath` 可能因無效路徑字元、過長路徑或權限問題擲回 `ArgumentException`、`PathTooLongException`、`SecurityException` 等。若例外發生，該目錄會被忽略，可能導致誤判憑證目錄已存在或未存在。建議明確捕捉特定例外並記錄，或先驗證路徑格式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0708

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2306`，距錨點 3 行）argv 陣列大小不足，寫入 argv[5] 導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但後續指派 `argv[5] = c->argv[2];`，索引 5 超出陣列範圍（合法索引為 0-4）。這會造成堆疊緩衝區溢位，可能導致程式崩潰或任意程式碼執行。

失敗情境：當欄位有過期時間時，執行 HINCRBYFLOAT 即觸發此寫入。

建議修正：將陣列大小改為 6，例如 `robj *argv[6];`。

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0709

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 0 行）clusterDeleteKeysInUnownedSlots 可能刪除正在匯入的 slot 中的 keys

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i) || getImportingSlotSource(i)` 會跳過匯入中的 slot，但若 `getImportingSlotSource(i)` 回傳非 NULL 但該 slot 實際上不屬於我們，仍可能刪除 keys。需確認匯入狀態的處理是否正確。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## P0710

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126`，距錨點 6 行）多 host 情境下 manager 可能被錯誤覆寫

> 條件 `if (manager && currentRendererId === rendererId)` 僅在 rendererId 相同時拋出錯誤。若不同 rendererId（例如 Server 與 WebAssembly 同時存在），則會直接覆寫全域變數 `manager` 與 `currentRendererId`，導致先前 host 的 manager 遺失。這可能造成動態 root components 操作指向錯誤的 manager，或先前 host 的元件無法正常運作。

建議：在多 host 情境下應明確禁止或隔離狀態，例如使用 Map 以 rendererId 為鍵儲存 manager，或至少在覆寫前記錄警告並確保舊 manager 不再被使用。

finding 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

## P0711

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）回傳 `Infinity` 可能造成下游型別或比較問題

> 當暖機完成後，`getWarmupLimit` 回傳 `Infinity`。這可能導致下游程式碼在進行數值比較或計算時出現非預期行為，例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若下游直接使用該值進行算術運算，可能產生 `Infinity` 或 `NaN`。

**建議修法**：
回傳 `emailCount` 本身，或使用一個明確的哨兵值（例如 `Number.MAX_SAFE_INTEGER`），並在文件或型別中說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0712

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 0 行）跨欄位驗證使用 field_validator 可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中新增的跨欄位驗證使用 `@field_validator`，但 `info.data` 在 field_validator 中可能尚未包含其他欄位（取決於驗證順序），導致 `info.data.get("bucket")` 可能為 None，使驗證失效。應改用 `@model_validator(mode='after')` 進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0713

**GT**（func）Missing module resolution in dynamic import causes team assignment tab to fail

> The EventTeamAssignmentTab dynamic import is missing the `.then((mod) => mod)` module resolution that all other tab imports use. This inconsistency will cause the dynamic import to not properly extract the default export, resulting in the team assignment tab failing to render correctly. When users navigate to the team assignment tab for event types, they will encounter a blank screen or rendering error because the component cannot be properly loaded.

GT 片段：`const EventTeamAssignmentTab = dynamic(() => import("./tabs/assignment/EventTeamAssignmentTabWebWrapper"));`

**finding**（`apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52`，距錨點 9 行）動態 import 路徑可能不正確

> 在 EventTypeWebWrapper.tsx 中，多個動態 import 的路徑從絕對路徑改為相對路徑，例如 `import("./tabs/setup/EventSetupTabWebWrapper")`。需確認這些相對路徑是否正確指向目標檔案，否則會導致模組載入失敗。

finding 片段：`const EventSetupTab = dynamic( ⏎ () => import("./tabs/setup/EventSetupTabWebWrapper").then((mod) => mod), ⏎ { loading: () => null } ⏎ );`

## P0714

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）提交前對 email 進行 trim 可能改變既有行為

> 在 `submitHandler` 中，`onSubmit({email: email.trim()})` 會移除 email 前後的空白字元。這可能導致原本包含前後空白的 email 被視為有效（如果驗證邏輯允許），但實際上送出的是修剪後的字串。若後端依賴原始輸入（例如用於比對或記錄），可能造成不一致。建議確認此變更是否為預期行為，並考慮在驗證前進行 trim，或保留原始輸入。

finding 片段：`onSubmit({email: email.trim()});`

## P0715

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 原本的驗證條件為 `if (value <= 0)`，會拒絕 0 和負數；變更後為 `if (value < 0)`，允許 0 值。但屬性文件說明為「strictly positive value」，且錯誤訊息仍為「must be positive」，因此 0 值可能導致後續邏輯錯誤（例如保留 0 個檔案）。建議確認 0 是否為有效值，若不是則應維持 `<= 0` 的檢查。

finding 片段：`if (value < 0)`

## P0716

**GT**（func）Incorrect sequence validation for multiple generic components

> The test validates deserialization of multiple closed generic components but checks that both descriptors have sequence number 0 instead of verifying that the second descriptor has sequence number 1. Component descriptors in a collection must have sequential ordering starting from 0, and this test should verify the second component has sequence 1. This incorrect assertion fails to validate proper sequence ordering, which is critical for component initialization and rendering order in Blazor.

GT 片段：`var secondDescriptor = descriptors[1]; ⏎ Assert.Equal(typeof(GenericTestComponent<string>).FullName, secondDescriptor.ComponentType.FullName); ⏎ Assert.Equal(0, secondDescriptor.Sequence);`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 18 行）參數值轉換使用 Convert.ToInt64 可能隱藏型別問題

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 來驗證參數值。如果實際反序列化的值是 `JsonElement` 或其他型別，`Convert.ToInt64` 可能成功轉換，但無法驗證型別是否正確。建議直接斷言型別為 `JsonElement` 並取得其值，或使用 `Assert.IsType<long>` 等更精確的斷言。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0717

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行）`generate_github_mirror_url_from_base` 中移除了 `set_path` 呼叫，可能導致鏡像 URL 不正確

> 原本的程式碼會將 `cdn` 的 path 設定為 `github_url`，但修改後僅回傳 `cdn.to_string()`，這可能導致鏡像 URL 未包含正確的路徑。若 `cdn` 原本有 path，則可能無法正確替換。建議確認此變更是否為預期行為，或改為使用 `Url::parse` 並正確設定 path。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## P0718

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:287`，距錨點 1 行）測試被標記為隔離且開關值變更，可能掩蓋問題

> 測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 被加上 `[QuarantinedTest]` 屬性，且 `DisableThrowNavigationException` 開關從 `false` 改為 `true`。這可能表示測試目前不穩定或失敗，但隔離測試會使其在 CI 中跳過，無法驗證修復。建議確認隔離原因，並在修復後移除隔離標記。

finding 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

## P0719

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）使用 `endsWith` 可能導致全表掃描，影響批次查詢效能

> 在 `where` 條件中使用 `endsWith` 來排除特定後綴的日曆，但資料庫（如 PostgreSQL）通常無法對 `endsWith` 使用一般的 B-tree 索引，這可能導致對 `selectedCalendar` 資料表的全表掃描。若該資料表規模較大，且此查詢被頻繁呼叫（例如定期同步），可能造成顯著的效能問題。

建議：
- 考慮在 `externalId` 上建立反向索引（reverse index）或使用其他可索引的比對方式（例如儲存反轉後的字串並使用 `startsWith`）。
- 若資料量不大或查詢頻率低，可接受此權衡，但應在 PR 描述中說明。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0720

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14`，距錨點 0 行）Suspense 未提供 fallback，可能導致載入時無 UI 回饋

> `<Suspense>` 沒有指定 `fallback` prop。當 `useSuspenseQuery` 暫停元件時，React 會尋找最近的 Suspense boundary 並顯示其 fallback；若沒有 fallback，則會向上尋找其他 boundary，若都沒有，則整個應用程式會 suspend 且無任何 UI 回饋。建議提供明確的 fallback，例如 `<Suspense fallback={<Skeleton />}>`。

finding 片段：`<Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} /> ⏎ </Suspense>`

## P0721

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:342`，距錨點 15 行）快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，程式使用 `for tenant_id, subscription_plan in bulk_plans.items()` 來寫入快取，但 `bulk_plans` 是 `get_plan_bulk` 的回傳值，其中可能包含 `None`（若 `get_plan_bulk` 將無效 tenant 設為 `None`）。這會導致將 `None` 序列化為 JSON 字串 `"null"` 存入 Redis，之後讀取時會因驗證失敗而再次視為 cache miss，但已污染快取。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，程式將 `None` 寫入 Redis，下次讀取時 `json.loads` 得到 `None`，`validate_python` 失敗，該 tenant 永遠無法命中快取。

**建議**：改為迭代 `plans_to_cache`，或先過濾掉 `None` 值。

finding 片段：`for tenant_id, subscription_plan in bulk_plans.items(): ⏎ redis_key = cls._make_plan_cache_key(tenant_id) ⏎ # Serialize dict to JSON string ⏎ json_str = json.dumps(subscription_plan)`

## P0722

**GT**（func）Stream entries incorrectly marked as referenced when cgroups_ref is NULL

> When cgroups_ref is NULL (which occurs after DEBUG RELOAD with empty PEL), the function returns 1 indicating the entry IS referenced, when it should return 0 indicating it is NOT referenced. This inverted logic prevents XADD/XTRIM operations with the ACKED strategy from correctly deleting entries that have been fully acknowledged by all consumer groups. The result is a memory leak where stream entries accumulate unnecessarily because they are incorrectly protected from deletion even though no consumer group has them in their pending entry list.

GT 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1; ⏎ unsigned char buf[sizeof(streamID)]; ⏎ streamEncodeID(buf, id);`

**finding**（`src/t_stream.c:2708`，距錨點 0 行）streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1，可能導致記憶體洩漏

> 新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1（表示被引用）。這可能導致某些清理邏輯（例如 `XADD ... ACKED` 或 `XTRIM`）誤以為 entry 仍被引用而無法刪除，造成記憶體洩漏或資料殘留。需要確認此變更的意圖：若沒有 cgroups，entry 應視為未被引用（回傳 0）才合理。建議檢查相關呼叫點，並考慮回傳 0 或調整邏輯。

finding 片段：`if (!s->cgroups_ref) return 1;`

## P0723

**GT**（func）Navigation exception test disables the exception mechanism it's meant to test

> The NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException test is designed to verify that NavigationException thrown during circular redirects doesn't become an unobserved task exception. The test name, comments, and logic all indicate it should test the exception handling behavior. However, the AppContext switch is set to true, which enables DisableThrowNavigationException, preventing NavigationException from being thrown at all. This fundamentally breaks the test's purpose - it can't validate exception handling behavior when exceptions are disabled. The test navigates to a circular redirect page that relies on NavigationException being thrown and properly handled, but with the switch enabled, the navigation manager uses a different code path that doesn't throw exceptions, making the test validate nothing meaningful.

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 0 行）AppContext.SetSwitch 參數值反轉可能導致測試失效

> 原本設定 `DisableThrowNavigationException` 為 `false`，但此處改為 `true`。若測試目的是驗證例外狀況，此變更可能使測試無法觸發預期的例外行為，導致測試失去意義。請確認此參數值是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0724

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，其他變體都輸出小寫（如 "deb"、"rpm"），但新增的 `Flatpak` 輸出 "Flatpak"（首字母大寫）。這可能導致序列化或比對時出現不一致，例如在產生 bundle 檔名或與其他工具互動時。建議改為 "flatpak"。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0725

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）參數名稱比對從 metadata.Name 改為 propertyName 可能影響既有功能

> 原本使用 `metadata.Name` 來比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或繫結名稱不同），可能導致找不到對應的參數，進而將描述套用到 RequestBody 或完全遺漏。建議確認此變更是否為預期行為，並補充相關測試。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0726

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行）快取資料可能包含 None 值，導致 json.dumps 序列化失敗

> 在 get_plan_bulk_with_cache 中，從 get_plan_bulk 取得的 bulk_plans 可能包含值為 None 的項目（因為 get_plan_bulk 現在會將無效租戶設為 None）。在寫入快取時，程式碼直接對 subscription_plan 呼叫 json.dumps，但 None 不是有效的 JSON 序列化對象，會拋出 TypeError。這會導致整個 pipeline 失敗，且該例外被捕獲後僅記錄日誌，但快取寫入全部失敗。

建議在寫入快取前過濾掉 None 值，或將 None 轉換為其他表示（例如空字典或特殊標記）。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0727

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:203`，距錨點 0 行）新增的 V2 字串可能未被使用

> 新增了 `detailTextSendUsageDataV2`、`labelStudiesV2`、`detailTextStudiesV2` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

finding 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

## P0728

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行）orgId 條件在 UNION 第二段可能過濾不正確

> 在 `getTeamsWithPBACPermissions` 的 UNION 第二段，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})` 中，`org` 是父組織，`child` 是子團隊。若 `orgId` 指定為父組織 ID，則 `org."id" = ${orgId}` 成立，會包含所有子團隊；若 `orgId` 指定為子團隊 ID，則 `child."id" = ${orgId}` 成立，但 `org."id" = ${orgId}` 不成立，因此只會包含該子團隊。這可能符合預期，但需確認是否應包含父組織本身。建議明確註釋意圖並增加測試。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## P0729

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 20 行）測試依賴真實網路，可能不穩定

> `captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或不穩定，導致測試逾時或失敗。

建議改用本地 HTML 字串或 `data:` URL 來避免外部依賴，或使用 `WKWebView` 的 `loadHTMLString` 方法。

finding 片段：`webView.load(URLRequest(url: url))`

## P0730

**GT**（rule）Line exceeds 110-character limit

> This newly added line appears to exceed the 110 character line-width requirement enforced by Biome formatting rules.

GT 片段：`return featureOptInService.listFeaturesForTeam({ teamId: input.teamId, parentOrgId, scope: "team" });`

**finding**（`packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103`，距錨點 31 行）setUserState mutation 缺少 await，可能造成未處理的 Promise rejection

> 在 `setUserState` mutation 中，呼叫 `featureOptInService.setUserFeatureState(...)` 時沒有加上 `await`。這會導致如果該方法拋出錯誤（例如 scope 驗證失敗），錯誤不會被 tRPC 正確捕獲，而會成為 unhandled promise rejection，可能導致伺服器不穩定或回傳錯誤的狀態碼。

**失敗情境**：當使用者嘗試設定一個不允許在 user scope 設定的功能時，`setUserFeatureState` 會拋出 `ErrorWithCode`，但因為沒有 `await`，這個錯誤不會被 tRPC 的錯誤處理機制攔截，客戶端可能收到成功回應，但實際上操作並未完成。

**建議修法**：在呼叫前加上 `await`。

finding 片段：`featureOptInService.setUserFeatureState({ ⏎ userId: ctx.user.id, ⏎ featureId: input.slug, ⏎ state: input.state,`

## P0731

**GT**（func）Incorrect event level causes important certificate warnings to be suppressed in non-verbose mode

> When verbose mode is not enabled, the event listener is configured with EventLevel.LogAlways instead of the intended EventLevel.Critical. EventLevel.LogAlways (value 0) actually means all events are enabled, not just critical ones. The original PR intended to show only Critical events in non-verbose mode to suppress routine logging. This bug causes all certificate-related events including verbose debug messages to be displayed in non-verbose mode, flooding users with unnecessary output and making it harder to identify actual problems. This breaks the intended user experience where only critical information should be shown by default.

GT 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

**finding**（`src/Tools/dotnet-dev-certs/src/Program.cs:127`，距錨點 7 行）ReporterEventListener 未釋放可能造成資源洩漏

> 在 `OnExecute` 中建立了 `ReporterEventListener` 實例，但未在結束時呼叫 `Dispose`。`EventListener` 實作 `IDisposable`，若未釋放可能導致事件監聽器持續存在，造成記憶體或資源洩漏。建議使用 `using` 陳述式或明確呼叫 `Dispose`。

finding 片段：`var listener = new ReporterEventListener(reporter);`

## P0732

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook

> 新增的 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 表示只要環境變數未設定或設為任何非 "false" 的值，webhook 都會啟用。但若部署環境中未設定此變數，且程式碼預期預設為停用，則會意外啟用；反之若預期預設為啟用，則此邏輯正確。需確認此環境變數的預設行為，並考慮加入更明確的設定或文件。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0733

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行）`expect` 取代 fallback 可能導致 panic

> 原本的程式碼在 `name` 為 `None` 時會 fallback 到 `association.ext[0].0`，但現在改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空（或 `ext` 的第一個元素不存在），程式會 panic。這會讓建置流程直接崩潰，且錯誤訊息不夠明確。

建議：保留原本的 fallback 邏輯，或改用更安全的處理方式，例如在 `ext` 為空時使用預設名稱或回傳錯誤。

finding 片段：`.expect("File association must have a name")`

## P0734

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行）Session 未關閉導致連線洩漏

> `ConversationVariableUpdaterImpl.update` 中建立 `Session(db.engine)` 後，在方法結束時未呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保 session 關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0735

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行）搜尋過濾功能失效：渲染改用 teamMembers 而非 filteredMembers

> 原本使用 `filteredMembers` 來根據搜尋字串過濾成員，但此 PR 將渲染改為直接使用 `teamMembers`，導致搜尋功能完全失效。使用者輸入搜尋關鍵字後，列表不會有任何變化。

建議：保留 `filteredMembers` 的計算邏輯，並在渲染時使用 `filteredMembers`。

finding 片段：`{teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))} ⏎ {teamMembers.length === 0 && (`

## P0736

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:46`，距錨點 0 行）變數不存在時僅記錄警告，可能隱藏錯誤

> 當 `variable_pool.get(selector)` 回傳非 `Variable` 時，僅記錄警告並繼續。若預期該變數一定存在，此情況可能代表上游邏輯錯誤，建議考慮拋出例外或提高日誌等級。

finding 片段：`if not isinstance(variable, Variable): ⏎ logger.warning( ⏎ "Conversation variable not found in variable pool. selector=%s", ⏎ selector,`

## P0737

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 0 行）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 錄音端點原本使用 `@Permissions([BOOKING_READ])`，現在改為 `@Permissions([BOOKING_WRITE])`。讀取錄音應只需要讀取權限，改為寫入權限可能讓具有寫入權限但無讀取權限的使用者也能存取錄音，造成權限擴張。除非有特殊原因，否則應維持 `BOOKING_READ`。

finding 片段：`@Permissions([BOOKING_WRITE])`

## P0738

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，此處傳入 6 個參數，但 `HSETEX` 指令的語法為 `HSETEX key [NX|XX] [KEEPTTL] [EX|PX|EXAT|PXAT] FIELDS num field value [field value ...]`。目前建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`，缺少 TTL 選項，可能導致語法錯誤或行為不符預期。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0739

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:286`，距錨點 39 行）get_plan_bulk 將無效 tenant 設為 None，可能造成下游型別錯誤

> 在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式會將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端可能預期每個值都是有效的 `SubscriptionPlan`。這可能導致下游在存取 `plan` 或 `expiration_date` 時發生 `AttributeError` 或 `TypeError`。

**失敗情境**：某 tenant 的 billing API 回傳格式錯誤，`get_plan_bulk` 回傳包含 `None` 的 dict，呼叫端若直接使用 `result[tenant_id]['plan']` 就會崩潰。

**建議**：跳過無效 tenant（不要加入 dict），或回傳一個明確的錯誤物件。若必須保留 `None`，應更新型別標註並在文件說明。

finding 片段：`except Exception: ⏎ logger.exception( ⏎ "get_plan_bulk: failed to validate subscription plan for tenant(%s)", tenant_id ⏎ )`

## P0740

**GT**（func）Inverted conditional logic in setUserFeatureState causes wrong branch execution

> The conditional check for handling the 'inherit' state has been inverted from `if (state === 'inherit')` to `if (state !== 'inherit')`. This causes the method to incorrectly pass the state without assignedBy when state is 'enabled' or 'disabled', and incorrectly attempts to access assignedBy property (which doesn't exist in the union type) when state is 'inherit', leading to runtime TypeScript errors and incorrect database operations. When users try to enable/disable a feature, the assignedBy tracking will be lost, and when they set it to inherit, the code will crash trying to access a non-existent property.

GT 片段：`if (state !== "inherit") { ⏎ await this.featuresRepository.setUserFeatureState({ userId, featureId, state }); ⏎ } else { ⏎ const { assignedBy } = input;`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:264`，距錨點 0 行）setUserFeatureState 條件判斷反轉，導致 enabled/disabled 狀態不會被寫入

> 原本的邏輯是 `if (state === "inherit")` 才呼叫 `setUserFeatureState`，否則走 `assignedBy` 分支。但此 PR 將條件改為 `if (state !== "inherit")`，使得當 state 為 `enabled` 或 `disabled` 時，會進入原本處理 `inherit` 的 else 分支，而該分支會嘗試從 input 取得 `assignedBy`，但 input 型別中 `assignedBy` 是必要的，因此可能不會立即出錯，但邏輯完全相反。

**失敗情境**：使用者嘗試將功能設為 enabled 或 disabled 時，實際呼叫的是 `setUserFeatureState({ userId, featureId, state })`，但這個呼叫缺少 `assignedBy`，可能導致 repository 層錯誤或資料不一致。

**建議修法**：改回 `if (state === "inherit")`。

finding 片段：`if (state !== "inherit") { ⏎ await this.featuresRepository.setUserFeatureState({ userId, featureId, state }); ⏎ } else { ⏎ const { assignedBy } = input;`

## P0741

**GT**（rule）Broad exception catch (except Exception) added for tool_responses JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type. The new code introduces another broad `except Exception:` while parsing JSON observations.

GT 片段：`if observation_payload: ⏎ try: ⏎ tool_responses = json.loads(observation_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:469`，距錨點 4 行）organize_agent_history 中 tool_inputs 與 tool_responses 的解析邏輯重複且可能不一致

> 原本對 tool_input 和 observation 的 JSON 解析各自獨立，現在改為先檢查是否為空字串再解析。但兩者的處理邏輯幾乎相同，可考慮抽成輔助函式以減少重複。

失敗情境：若未來需要修改解析邏輯，可能只改到其中一處而導致不一致。

建議：將 JSON 解析邏輯抽成共用函式。

finding 片段：`tool_input_payload = agent_thought.tool_input ⏎ if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload)`

## P0742

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行）程式碼風格不一致：部分 require 陳述式缺少分號

> 在此檔案中，前 10 行的 require 陳述式沒有以分號結尾，但後續的 require 陳述式（例如 `const EventRepository = require('./repositories/event-repository');`）卻有分號。這可能是無意的，且與專案慣例不一致。建議統一加上分號。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0743

**GT**（func）Incorrect boolean operator in regex validation

> The test assertion uses AND (&&) operator instead of OR (||) when checking if the log message matches either the old or new CSP error pattern. This causes the test to fail because a log message cannot simultaneously match both regex patterns - they represent different browser error message formats. The original intent was to accept either format, but the AND operator requires both patterns to match at the same time, which is impossible. This will cause the test to fail even when receiving a valid CSP error message in either format.

GT 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

**finding**（`src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:103`，距錨點 2 行）CSP 錯誤訊息比對使用兩個 Regex 可能過於嚴格

> 測試改為同時比對舊版和新版的 CSP 錯誤訊息。若瀏覽器更新後產生第三種格式，測試將失敗。建議使用單一 Regex 涵蓋所有可能格式，或使用更寬鬆的比對。

finding 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

## P0744

**GT**（rule）Force unwrap of URL initializer in tests (third occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致 `wait(for:)` 永遠等不到 expectation 被 fulfill，直到逾時。

應將 `expectation.fulfill()` 移回 `decisionHandler` 內，與其他測試保持一致。

finding 片段：`wait(for: [expectation]) ⏎ expectation.fulfill()`

## P0745

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:307`，距錨點 0 行）空狀態判斷錯誤：使用 teamMembers.length 而非 filteredMembers.length

> 原本以 `filteredMembers.length === 0` 顯示「無成員」訊息，現在改為 `teamMembers.length === 0`，導致當過濾後無結果時，不會顯示空狀態，反而顯示所有成員。

**失敗情境**：搜尋無匹配成員時，列表仍顯示所有成員，且無空狀態提示。

**建議**：改回使用 `filteredMembers.length`。

finding 片段：`{teamMembers.length === 0 && ( ⏎ <div className="text-subtle py-4 text-center text-sm">{t("no_members_found")}</div> ⏎ )}`

## P0746

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:203`，距錨點 4 行）新增的 V2 字串可能未被使用

> 新增了 `detailTextSendUsageDataV2`、`labelStudiesV2`、`detailTextStudiesV2` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

finding 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

## P0747

**GT**（func）Missing optional chaining causes runtime error when openForm is undefined

> The code accesses `openForm.in_reply_to_snippet` without optional chaining, but openForm can be undefined when rendering certain forms (like the main comment form). The original code correctly used `openForm?.in_reply_to_snippet` with optional chaining. This will cause a "Cannot read property 'in_reply_to_snippet' of undefined" runtime error when the FormWrapper is rendered without an openForm prop, crashing the component.

GT 片段：`let openStyles = ''; ⏎ if (isOpen) { ⏎ const isReplyToReply = !!openForm.in_reply_to_snippet; ⏎ openStyles = isReplyToReply ? 'pl-[1px] pt-[68px] sm:pl-[44px] sm:pt-[56px]' : 'pl-[1px] pt-[48px] sm:pl-[44px] sm:pt-[40px]';`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:313`，距錨點 0 行）openForm 參數改為必填，需確認所有呼叫點皆已更新

> FormWrapper 的 props 型別中 `openForm?: OpenCommentForm` 改為 `openForm: OpenCommentForm`，且使用 `openForm.in_reply_to_snippet` 時不再使用可選串連。若其他元件未傳入 openForm，可能導致執行時期錯誤。請確認所有使用 FormWrapper 的地方都已傳入 openForm。

finding 片段：`const isReplyToReply = !!openForm.in_reply_to_snippet;`

## P0748

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 17 行）clusterDeleteKeysInUnownedSlots 中 clusterDelKeysInSlot 的參數可能導致資料遺失

> 在 clusterDeleteKeysInUnownedSlots 中呼叫 `clusterDelKeysInSlot(i, 0)`。第二個參數的語意需要確認：若為 `save` 旗標，傳 0 可能表示不保存，但若為其他語意（例如是否為 async），可能導致錯誤。請檢查 clusterDelKeysInSlot 的定義，確保傳入正確的參數。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## P0749

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2571`，距錨點 11 行）複寫指令未包含 TTL 參數，可能無法保留過期時間

> `HSETEX` 指令若未指定 TTL 選項，可能預設為不設定過期時間，導致複本上欄位 TTL 遺失。需確認 `HSETEX` 在僅有 `KEEPTTL` 而無 TTL 選項時的行為。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0750

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行）Flatpak 的 Display 實作使用大寫 "Flatpak"，與其他 bundle 類型的小寫慣例不一致

> 在 `Display for BundleType` 的實作中，新增的 `Flatpak` 分支回傳 `"Flatpak"`，但其他所有分支（如 `"nsis"`, `"app"`, `"dmg"`）皆為小寫。這可能導致序列化或顯示時的不一致，例如在錯誤訊息或日誌中出現大小寫混雜。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0751

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2571`，距錨點 0 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，此處傳入 6 個參數，但 `HSETEX` 指令的語法為 `HSETEX key [NX|XX] [KEEPTTL] [EX|PX|EXAT|PXAT] FIELDS num field value [field value ...]`。目前建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`，缺少 TTL 選項，可能導致語法錯誤或行為不符預期。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0752

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）SMTP 類別選擇邏輯可能改變非 TLS 與 TLS 模式的行為

> 原本程式碼根據 use_tls 和 opportunistic_tls 明確選擇 SMTP 或 SMTP_SSL，並在 opportunistic TLS 時先建立 SMTP 再呼叫 starttls。新程式碼使用三元運算子選擇類別，但條件 `(self.use_tls and not self.opportunistic_tls)` 在 use_tls=False 時會選擇 SMTP（正確），但在 use_tls=True 且 opportunistic_tls=True 時也會選擇 SMTP（正確），然而在 use_tls=True 且 opportunistic_tls=False 時選擇 SMTP_SSL（正確）。看似等價，但需注意原本在非 TLS 模式下（use_tls=False）直接建立 SMTP，新程式碼也相同。然而，原本在 opportunistic TLS 模式下，先建立 SMTP 後呼叫 ehlo(self.server)，新程式碼改為 ehlo(local_host)，其中 local_host 可能為空字串，這可能導致 HELO 命令使用空字串而非伺服器位址，違反 SMTP 規範。建議確認 local_host 為空時應回退為 self.server。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0753

**GT**（func）Type mismatch in total_price initialization breaks Decimal arithmetic

> The total_price field is initialized with integer 0 instead of Decimal(0), creating a type inconsistency. The MessageAgentThought model defines total_price as Mapped[Decimal | None] expecting a Decimal type, and other price fields (message_unit_price, answer_unit_price, etc.) are correctly initialized with Decimal types. This inconsistency will cause type errors during price calculations when the system attempts to perform Decimal arithmetic operations (addition, multiplication) between Decimal and int types, potentially breaking billing computations or causing runtime exceptions.

GT 片段：`answer_price_unit=Decimal(0), ⏎ tokens=0, ⏎ total_price=0, ⏎ position=self.agent_thought_count + 1,`

**finding**（`api/core/agent/base_agent_runner.py:319`，距錨點 7 行）message_unit_price 與 answer_price_unit 的預設值可能與既有資料不一致

> 在 create_agent_thought 中，`message_unit_price` 由 `0` 改為 `Decimal(0)`，`message_price_unit` 由 `0` 改為 `Decimal("0.001")`，`answer_unit_price` 由 `0` 改為 `Decimal("0.001")`，`answer_price_unit` 由 `0` 改為 `Decimal(0)`。這些變更可能影響計費邏輯，且與模型定義中的 server_default 不完全一致。

失敗情境：若既有資料依賴舊的預設值，可能導致計算錯誤或顯示異常。

建議：確認這些預設值變更是有意為之，並與模型定義及資料庫 schema 對齊。

finding 片段：`message_unit_price=Decimal(0), ⏎ message_price_unit=Decimal("0.001"), ⏎ message_files=json.dumps(messages_ids) if messages_ids else "", ⏎ answer="",`

## P0754

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）天數計算 off-by-one：第一天就被當成 day 1

> `#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算經過天數，導致在暖機開始當天（day 0）就會得到 day 1。這會使暖機進度提前一天，例如在第一天就套用 day 1 的 limit（237），而不是 day 0 的 200。

**失敗情境**：
- 使用者在 2024-01-15 12:00 建立第一封 email，並在 2024-01-15 13:00 呼叫 `getWarmupLimit`。
- `#getDaysSinceFirstEmail` 會計算 `(Date.now() - firstEmailTime) / (1000*60*60*24)` ≈ 0.0417，`Math.ceil` 後得到 1。
- `getWarmupLimit` 會回傳 day 1 的 limit（237），而不是 day 0 的 200。

**建議修法**：
改用 `Math.floor` 來計算天數，讓 day 0 代表第一天。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0755

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:26`，距錨點 0 行）throttle 方法中 lastExecutionTime 更新時機變更可能導致節流失效

> 原本的實作在檢查時間間隔後才更新 `lastExecutionTime`，現在則在檢查前就更新。這會使得連續呼叫時，第二次呼叫的 `timeIntervalSinceNow` 會是負的且絕對值很小，導致 `guard` 條件不成立而直接 return，造成節流永遠無法觸發。

**失敗情境**：假設 `threshold = 1` 秒，連續呼叫 `throttle` 兩次（間隔小於 1 秒），第一次呼叫後 `lastExecutionTime` 被設為現在，第二次呼叫時 `timeIntervalSinceNow` 約為 -0.1 秒，`-0.1 < -1` 為 false，guard 失敗直接 return，completion 永遠不會被執行。

**建議**：將 `lastExecutionTime = Date()` 移回 guard 之後，或改為在 guard 通過後才更新。

finding 片段：`lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return }`

## P0756

**GT**（rule）Missing trailing newline at end of file

> Biome formatting conventions require LF line endings and proper file termination. This file is missing the final newline, as indicated by the diff marker.

GT 片段：`export default EventLimitsTabWebWrapper; ⏎ \ No newline at end of file`

**finding**（`apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8`，距錨點 0 行）檔案缺少結尾換行

> 檔案最後一行 `export default EventLimitsTabWebWrapper;` 沒有換行符號，可能導致某些工具或 linter 警告。建議補上換行。

finding 片段：`export default EventLimitsTabWebWrapper;`

## P0757

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）setUp 中呼叫 @MainActor 方法但類別未標註 @MainActor

> `DependencyHelperMock().bootstrapDependencies()` 現在是 @MainActor 方法，但 `LaunchScreenViewModelTests` 類別沒有標註 @MainActor。此處未加 await（diff 中仍為 `DependencyHelperMock().bootstrapDependencies()`），在 Swift 6 下可能導致編譯錯誤。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0758

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:46`，距錨點 2 行）SQLite 上完全沒有鎖保護，競態條件仍可能發生

> 在 SQLite 上，`acquire_composite_trigger_lock` 直接跳過（註解說明 SQLite 序列化寫入，但讀取與寫入之間仍可能有競態）。`clear_child_firings` 的 DELETE ... RETURNING 雖然能偵測到競爭，但若兩個交易都讀到相同的 child firings，其中一個會刪除成功，另一個刪除 0 筆並跳過觸發，這可能導致複合觸發器永遠不觸發（如果兩個子觸發器事件分別由不同交易處理，且每個交易都只看到自己的 firing）。

建議在 SQLite 上使用其他同步機制（例如 application-level lock 或樂觀鎖），或至少記錄警告。

finding 片段：`# SQLite doesn't support advisory locks, but SQLite also serializes writes ⏎ # at the database level, so the race condition is less likely to occur`

## P0759

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:913`，距錨點 0 行）dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找，可能找不到既有鍵

> 在 `dictSetKeyAtLink` 的 `newItem == 0` 分支中，原本使用 `key` 呼叫 `dictFindLink`，現在改為使用 `addedKey`。但 `addedKey` 是經過 `keyDup` 複製後的新指標，若 `keyDup` 有實作（例如某些 dict type），則 `addedKey` 與原本儲存在 dict 中的 key 指標不同，導致 `dictFindLink` 無法找到對應的 entry，進而觸發 assert 失敗或錯誤更新。

**失敗情境**：若 dict type 有 `keyDup` 回呼，且呼叫 `dictSetKeyAtLink(d, newKey, &link, 0)` 來更新既有 entry 的 key，則 `addedKey` 是新複製的 key，與 dict 中儲存的舊 key 不同，`dictFindLink` 會找不到，導致 assert 失敗。

**建議**：應使用原始的 `key` 進行查找，而不是 `addedKey`。

finding 片段：`if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL); ⏎ }`

## P0760

**GT**（func）Empty lines not filtered in Expected Events textarea

> In the CustomTriggerFields component, the onChange handler for the Expected Events textarea fails to filter out empty or whitespace-only lines. When users press Enter multiple times or leave blank lines between events, these empty strings are included in the events array sent to the trigger configuration. This will cause backend validation failures or create malformed automation triggers that expect empty event names, leading to automations that never fire correctly.

GT 片段：`onChange={(e) => { ⏎ const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined); ⏎ }}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38`，距錨點 0 行）空字串轉換為 undefined 可能導致非預期行為

> 在 `onChange` 中，當使用者清空 textarea 時，`lines` 會是 `['']`，因此 `lines.length > 0` 為 true，會將 `['']` 設為值，而不是 `undefined`。這可能導致表單驗證或後續處理出現問題。建議改為：`field.onChange(lines.length > 0 && lines[0] !== '' ? lines : undefined)` 或類似邏輯。

finding 片段：`const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined);`

## P0761

**GT**（rule）Line exceeds 110 character width

> Biome formatting requires a max line width of 110 characters. This reformatted method signature is on a single line and appears to exceed the configured line width; it should be wrapped.

GT 片段：`async hasAcceptedMembershipByEmail({ email, teamId }: { email: string; teamId: number }): Promise<boolean> {`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:584`，距錨點 18 行）hasPendingInviteByUserId 查詢條件錯誤，永遠回傳 false

> 此方法用於檢查使用者是否有 pending invite，但查詢條件為 `accepted: true`，這會找出已接受的 membership，而非未接受的邀請。因此，當使用者有 pending invite 時，此方法會回傳 `false`，導致 PR 的主要功能（重新導向）完全失效。

**失敗情境**：使用者透過邀請連結註冊，系統建立了 `accepted: false` 的 membership。當使用者進入 `/onboarding/getting-started` 頁面時，`hasPendingInviteByUserId` 回傳 `false`，因此不會重新導向到 `/onboarding/personal/settings`，使用者會停留在錯誤的頁面。

**建議修法**：將查詢條件改為 `accepted: false`。

finding 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

## P0762

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行）linuxdeploy 下載 URL 使用錯誤的架構變數

> 原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為直接使用 `arch`。這可能導致 i686 架構下載到錯誤的檔案。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0763

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行）Popover 內容的 hover 處理可能造成閃爍

> PopoverContent 上也設定了 onMouseEnter 和 onMouseLeave，當滑鼠從 trigger 移動到 popover 內容時，可能會因為 mouseleave 觸發關閉，然後 mouseenter 又開啟，造成閃爍。建議使用 Popover 的 hover 模式或設定適當的 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0764

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行）讀取失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或解析失敗時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致意外重置版本碼，尤其是在檔案被誤刪或格式錯誤時，造成 Google Play 上傳失敗。

建議：在無法讀取時發出警告或錯誤，或提供明確的 fallback 策略。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0765

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行）自動遞增時未檢查 versionCode 上限

> 當 `auto_increment_version_code` 為 true 時，直接使用 `saturating_add(1)`，但未檢查是否超過 Google Play 的 2100000000 上限。若已達上限，`saturating_add` 會停留在 2100000000，可能導致上傳失敗。

建議：在遞增後檢查上限，若超過則報錯。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

## P0766

**GT**（func）Cookie deletion incorrectly calls SetCookie instead of DeleteCookie

> The delete_cookie function is sending a WebviewMessage::SetCookie message instead of WebviewMessage::DeleteCookie. This causes the cookie to be set/updated instead of being deleted when the delete_cookie API is called. Any code attempting to delete cookies will fail to remove them, and may inadvertently persist or update cookies that should be removed. This breaks the entire cookie deletion functionality and creates a security concern where sensitive cookies cannot be properly removed.

GT 片段：`fn delete_cookie(&self, cookie: Cookie<'_>) -> Result<()> { ⏎ send_user_message( ⏎ &self.context, ⏎ Message::Webview(`

**finding**（`crates/tauri-runtime-wry/src/lib.rs:1718`，距錨點 0 行）delete_cookie 改為 SetCookie 可能無法正確刪除 cookie

> 在 `delete_cookie` 方法中，原本傳送 `WebviewMessage::DeleteCookie`，現在改為 `WebviewMessage::SetCookie`。這可能導致 cookie 被設定而不是刪除，除非 `SetCookie` 的實作會檢查 cookie 的過期時間或 max-age 來決定是否刪除。請確認 `SetCookie` 的處理邏輯是否支援刪除語意，否則應保留 `DeleteCookie` 或使用其他刪除機制。

finding 片段：`WebviewMessage::SetCookie(cookie.into_owned()),`

## P0767

**GT**（rule）Missing ConfigureAwait(false) on Task.Yield

> The rule requires all await expressions in library code (non-test, non-sample projects) to use .ConfigureAwait(false) to avoid capturing the synchronization context, but the await Task.Yield() expression at line 291 omits it.

GT 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 0 行）登出流程中新增的 Task.Yield 可能引入競態

> 在 `ProcessLogOut` 中，於驗證登出狀態後、取得驗證狀態前新增了 `await Task.Yield()`。這會讓出執行緒，可能導致後續的 `AuthenticationProvider.GetAuthenticationStateAsync()` 讀取到不一致的狀態。例如，若使用者在 `Task.Yield()` 期間登入或登出，可能導致登出流程使用過時的驗證狀態。建議移除 `Task.Yield()`，或說明其必要性並確保狀態一致性。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## P0768

**GT**（rule）Static property missing explicit access control modifier

> Rule 11 requires explicit access control on properties/methods. The modified static property `generator` is declared without an explicit access modifier (e.g., `private`, `internal`, `public`).

GT 片段：`// FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）nonisolated(unsafe) 可能隱藏執行緒安全問題

> 使用 `nonisolated(unsafe)` 來繞過 Swift 6 的嚴格並發檢查，但若 `ContentBlockerGenerator` 真的非執行緒安全，此標註只是暫時壓制問題。建議確認其執行緒安全性，或改用其他並發安全機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0769

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2310`，距錨點 0 行）使用 shared.fields 與 shared.integers[1] 作為 HPEXPIREAT 參數，但未確認其初始化狀態

> shared.fields 在 createSharedObjects 中初始化，但 shared.integers[1] 是否已初始化需確認。若未初始化，可能導致傳播錯誤的指令。

失敗情境：若 shared.integers[1] 未正確初始化，傳播的 HPEXPIREAT 指令可能包含錯誤的參數。

建議修正：確認 shared.integers[1] 在 createSharedObjects 中已正確初始化，或改用其他方式建立整數物件。

finding 片段：`argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1];`

## P0770

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 remarks 指派給 Summary 可能改變 API 文件語意

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。在 OpenAPI 中，Summary 是簡短摘要，Description 是詳細說明。若 remarks 內容較長，放入 Summary 可能導致文件品質下降。建議確認此變更是否為預期行為，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## P0771

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）React Scan 載入失敗時僅回傳空元件，且錯誤僅記錄於 console

> 當 `import('./scan')` 失敗時，catch 區塊回傳 `{ default: () => null }`，這會讓開發者無法在 UI 上察覺 devtools 未載入。雖然有 `console.error`，但在生產環境中可能被忽略。建議在開發模式下顯示一個明確的錯誤提示元件，或至少提供一個可視的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0772

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:42`，距錨點 0 行）使用 Python hash() 作為 advisory lock key 會因 hash randomization 而失效

> `lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建的 `hash()`，其值在每次程序啟動時會因 hash randomization 而不同（除非設定 PYTHONHASHSEED）。這表示不同的 worker 程序（或甚至同一程序重啟後）對同一個 trigger.id 會計算出不同的 lock key，導致 advisory lock 無法跨程序互斥，競態條件依然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）並取模，或使用 `uuid.UUID.int` 屬性，確保跨程序一致。

finding 片段：`lock_key = hash(str(trigger.id)) % (2**63)`

## P0773

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:913`，距錨點 0 行）dictSetKeyAtLink 中新增鍵時未使用轉換後的 key 進行查找

> 在 `dictSetKeyAtLink` 中，當 `newItem` 為真且需要重新查找 bucket 時，使用 `dictStoredKey2Key(d, key)` 轉換，但後續 `dictFindLink(d, addedKey, NULL)` 使用 `addedKey`（可能已複製的 stored key），未轉換為 lookup key。若 keyDup 回傳 stored key 格式，可能導致查找失敗。

finding 片段：`if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL); ⏎ }`

## P0774

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1105`，距錨點 18 行）autoCloseOnSelect 在 inline 模式未呼叫 onClose

> 在 inline 模式（`inline={true}`）的 `SelectOptionsPopover` 中，當 `field.autoCloseOnSelect` 為 true 且為 multiselect 時，程式碼呼叫了 `onClose?.()`，但 `onClose` 是從 props 傳入的，在 `Filters` 元件中 inline 模式的 `onClose` 會設定 `setAddFilterOpen(false)` 並清除 `selectedFieldKeyForOptions`。然而，在 `SelectOptionsPopover` 的 inline 分支中，`onClose` 被呼叫後，外層的 `Popover` 可能不會正確關閉，因為 inline 模式沒有自己的 `open` state 控制。這可能導致 popover 無法關閉或狀態不同步。建議確認 inline 模式下 autoCloseOnSelect 的關閉邏輯是否正確。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## P0775

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2571`，距錨點 11 行）HINCRBYFLOAT 複寫為 HSETEX KEEPTTL 可能遺失欄位 TTL

> 原程式碼使用 `HASH_SET_KEEP_TTL` 保留欄位 TTL，但複寫指令改為 `HSETEX KEEPTTL`。若 `HSETEX KEEPTTL` 的實作在欄位不存在時不會設定 TTL，則複本上原本沒有 TTL 的欄位將維持無 TTL，但主節點上該欄位可能因 `HINCRBYFLOAT` 而獲得 TTL（例如原本有 TTL 的欄位被更新後，TTL 應保留）。需確認 `HSETEX KEEPTTL` 在欄位不存在時的行為是否與 `HASH_SET_KEEP_TTL` 一致。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0776

**GT**（func）Race detection compares lengths instead of ID sets allowing double-firing

> The race detection logic compares only the count of deleted IDs rather than verifying the exact set of IDs match. This comparison using len(deleted_ids) != len(firing_ids) will incorrectly pass when a worker deletes the same number of firings but with different IDs than expected. For example, if firing_ids is {A, B} but deleted_ids is {C, D}, both have length 2 so the check passes and the trigger fires incorrectly. The correct implementation should use set equality (deleted_ids != firing_ids) to ensure the exact same firings were claimed, preventing spurious trigger firings when workers race.

GT 片段：`# Clear by firing id, and only proceed if we won the race to claim them. ⏎ # This prevents double-firing when multiple workers evaluate concurrently. ⏎ deleted_ids = await clear_child_firings( ⏎ session, trigger, firing_ids=list(firing_ids)`

**finding**（`src/prefect/server/events/triggers.py:396`，距錨點 0 行）刪除數量比較可能因重複 firing_ids 而誤判

> 在 `evaluate_composite_trigger` 中，比較 `len(deleted_ids) != len(firing_ids)` 來判斷是否成功刪除所有 firing。但 `firing_ids` 是 set，而 `deleted_ids` 也是 set，若 `firing_ids` 中有重複（雖然 set 不會重複），但若資料庫中因某些原因存在重複的 child_firing_id（例如先前未清理乾淨），刪除數量可能小於預期，導致誤判為競態而跳過觸發。建議使用集合比較（`deleted_ids == firing_ids`）或確認資料庫唯一性。

finding 片段：`if len(deleted_ids) != len(firing_ids):`

## P0777

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳未定義的 `True` 可能導致 ReferenceError

> 在 `handleJSONSchemaChange` 中，成功解析 JSON 後回傳了 `True`（大寫 T）。在 TypeScript/JavaScript 中，`True` 不是內建的全域變數，除非有自訂的全域宣告，否則執行到此處會拋出 `ReferenceError: True is not defined`。這會中斷函式執行，且由於此函式是事件處理器，錯誤可能不會被明顯捕捉，導致 UI 行為異常。建議改為回傳 `true` 或直接不回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0778

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:364`，距錨點 2 行）SSL_CERT_DIR 解析時未處理空目錄項目

> 程式碼使用 `existingSslCertDir.Split(Path.PathSeparator)` 分割環境變數，但未移除空字串項目。若 SSL_CERT_DIR 包含連續分隔符（如 `dir1::dir2`），會產生空字串，後續 `string.IsNullOrWhiteSpace(dir)` 檢查會將其忽略，但可能導致其他邏輯問題。建議使用 `StringSplitOptions.RemoveEmptyEntries` 分割。

finding 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator);`

## P0779

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 10 行）clusterDeleteKeysInUnownedSlots() 可能誤刪正在遷移中的 key

> 此函式會刪除所有不在自己 slot 中的 key，但未檢查 slot 是否正在進行 legacy 遷移（例如 MIGRATING 狀態）。雖然註解提到 atomic slot migration 安全，但 legacy 遷移中若節點是 migrating 狀態，刪除 key 可能導致資料遺失。建議增加對 migrating 狀態的檢查，或確認此函式僅在特定條件下呼叫。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## P0780

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:12`，距錨點 6 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const EventRepository = require('./repositories/event-repository'); ⏎ const ProductRepository = require('./repositories/product-repository'); ⏎ const RouterController = require('./controllers/router-controller'); ⏎ const MemberController = require('./controllers/member-controller');`

## P0781

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2310`，距錨點 0 行）使用 shared.fields 與 shared.integers[1] 作為 HPEXPIREAT 參數，但未確認其初始化狀態

> shared.fields 在 createSharedObjects 中初始化，但 shared.integers[1] 是否已初始化需確認。若未初始化，可能導致傳播錯誤的指令。

失敗情境：若 shared.integers[1] 未正確初始化，傳播的 HPEXPIREAT 指令可能包含錯誤的參數。

建議修正：確認 shared.integers[1] 在 createSharedObjects 中已正確初始化，或改用其他方式建立整數物件。

finding 片段：`argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1];`

## P0782

**GT**（func）Incorrect async Task wrapper breaks MainActor isolation in onboarding action handler

> The onActionTap closure is wrapped in a Task block without ensuring MainActor isolation. The OnboardingFlowViewModel expects this closure to be @MainActor isolated, but Task {} creates a new async context that may execute on a different executor. This causes the completion handler and handleAction calls to potentially run off the main thread, leading to concurrency violations and potential crashes when UI updates occur. The original code directly called onboardingService.handleAction which maintained proper MainActor isolation.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in ⏎ guard let onboardingService = self?.onboardingService else { return } ⏎ Task { ⏎ onboardingService.handleAction(`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行）將 onActionTap 閉包內容包進 Task 可能改變執行時序與錯誤處理

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使 handleAction 的執行延後到當前同步流程之後，可能影響依賴其完成時機的邏輯（例如 completion 的呼叫時機）。此外，若 handleAction 內部有錯誤拋出，原本可能由閉包呼叫者處理，現在錯誤會被 Task 吞掉或延遲處理。建議確認此處非同步化的必要性，或明確處理錯誤並確保 completion 在正確的執行緒上呼叫。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0783

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行）錯誤類型從 FormatToml 改為 FormatJson，導致 TOML 解析錯誤被誤報為 JSON 錯誤

> 在 `do_parse_toml` 函式中，原本將 `toml::from_str` 的錯誤包裝為 `ConfigError::FormatToml`，但升級後改為 `ConfigError::FormatJson`，並將錯誤轉為 `serde_json::Error`。這會讓 TOML 解析失敗時回報為 JSON 格式錯誤，誤導使用者。應保留 `FormatToml` 變體，或新增對應的錯誤類型。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## P0784

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行）下載 WebView2 離線安裝程式時未檢查 HTTP 狀態碼

> 直接使用 `ureq::get(url).call()` 後未檢查回應狀態碼，若伺服器回傳 404 或其他錯誤，仍會將錯誤頁面內容寫入檔案。建議檢查 `response.status()` 或使用 `response.into_body().read_to_end()` 前先確認狀態碼為 2xx。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## P0785

**GT**（rule）Unused variable causes compilation warning

> The rule requires that compilation completes successfully with no warnings when -Werror flag is enabled. The code contains an unused variable 'total_ranges' that triggers a compilation warning.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1018`，距錨點 0 行）asmCountKeysInSlots 可能造成效能問題或非預期行為

> asmCountKeysInSlots 會對每個 slot 呼叫 kvstoreDictSize，若 slot 範圍很大（例如 0-16383），可能導致大量的函式呼叫，影響效能。此外，此函式在 asmLogTaskEvent 中被呼叫，而 asmLogTaskEvent 可能在任務生命週期的多個事件中被呼叫，若 slot 範圍大且 key 數量多，可能造成明顯延遲。建議考慮快取或使用更有效率的方式計算 key 數量。

finding 片段：`for (int j = slots->ranges[i].start; j <= slots->ranges[i].end; j++) { ⏎ key_count += kvstoreDictSize(server.db[0].keys, j); ⏎ }`

## P0786

**GT**（func）Missing try keyword in async throws method call

> The IpadOnlyTestCase.setUp() method is marked as 'async throws' but calls 'await super.setUp()' without the 'try' keyword. Since BaseTestCase.setUp() is declared as 'async throws', this means any errors thrown by the parent setUp will not be properly propagated and will instead cause a compilation error or runtime crash. This breaks the error handling contract for all iPad-specific test cases that inherit from IpadOnlyTestCase, potentially causing test suite failures or silent test skips.

GT 片段：`class IpadOnlyTestCase: BaseTestCase { ⏎ override func setUp() async throws { ⏎ specificForPlatform = .pad ⏎ if iPad() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508`，距錨點 0 行）IpadOnlyTestCase.setUp() 呼叫 super.setUp() 缺少 try

> 在 `IpadOnlyTestCase` 的 `setUp()` 中，`super.setUp()` 現在是 `async throws`，但呼叫時沒有加上 `try`。這會導致編譯錯誤。

建議改為：
```swift
try await super.setUp()
```

finding 片段：`await super.setUp()`

## P0787

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:325`，距錨點 40 行）Redis mget 長度不符時快取完全失效且例外被吞掉

> 在 `get_plan_bulk_with_cache` 中，若 `redis_client.mget(redis_keys)` 回傳的 list 長度與 `tenant_ids` 不符，程式會拋出例外，但該例外被外層的 `except Exception` 捕捉，僅記錄錯誤並將所有 tenant 設為 cache miss。這導致即使 Redis 正常運作，只要 mget 因任何原因回傳長度不符（例如 Redis 叢集節點變更），快取就會完全失效，且開發者難以察覺。

**失敗情境**：Redis 叢集在 mget 期間發生 failover，導致部分 key 遺失，回傳長度小於請求數量。此時所有 tenant 都會被視為 cache miss，直接呼叫 billing API，失去快取效益。

**建議**：不要將長度不符視為致命錯誤。可改為逐 key 檢查，或僅記錄警告並將缺失的 key 視為 miss。若必須拋出例外，應使用更精確的例外型別，並考慮重試機制。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## P0788

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:25`，距錨點 5 行）tearDown 中呼叫 reset 未 await

> `DependencyHelperMock().reset()` 未標記為 `@MainActor`，但 `tearDown` 已改為 async 且未 await。若 `reset` 未來改為 main actor 隔離，此處將需要 await。目前可能無編譯錯誤，但建議統一加上 `await` 以符合 async 慣例。

finding 片段：`DependencyHelperMock().reset()`

## P0789

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）write_and_make_executable 中先設定權限再寫入檔案，可能導致權限設定失敗或檔案內容被覆蓋

> 在 `write_and_make_executable` 函式中，原本的順序是先寫入檔案再設定權限，但此 PR 將其反轉為先設定權限再寫入。這會造成兩個問題：
1. 如果 `fs::set_permissions` 失敗（例如檔案不存在），函式會回傳錯誤，但此時檔案尚未寫入，可能導致後續流程中斷。
2. 如果 `fs::write` 成功，它會以預設權限建立或覆蓋檔案，使得先前設定的 0o770 權限失效，最終檔案權限可能不是預期的 0o770。

建議恢復原本的順序：先 `fs::write`，再 `fs::set_permissions`。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0790

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 10 行）hasInitializedJsComponents 旗標可能導致初始化遺漏

> `hasInitializedJsComponents` 為全域布林值，一旦設為 true 後，即使後續呼叫傳入不同的 `jsComponentInitializers` 或 `jsComponentParameters`，也不會重新執行初始化。若不同 renderer 需要不同的初始化集合，此旗標會阻止必要的初始化。

建議：考慮以 rendererId 或初始化內容的 hash 作為鍵來判斷是否需要重新初始化，或明確記錄此限制。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## P0791

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖曳的 prefix 項目，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包括 prefixItems 對應的項目。但這些項目在 `SchemaFormInputArrayItem` 中因 `canMove` 為 false 而停用拖曳（`useSortable` 的 `disabled` 設為 true）。將停用的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過停用項目或碰撞偵測錯誤。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => index >= prefixItemsCount).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0792

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 21 行）FakeWKNavigationDelegate 可能無法捕捉 targetFrame

> 在 decidePolicyFor navigationAction 中，navigationAction.targetFrame 可能為 nil（例如新視窗或某些重定向），此時 capturedFrame 為 nil，導致測試失敗。建議處理 targetFrame 為 nil 的情況，或使用其他 delegate 方法。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0793

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行）測試依賴真實網路，可能不穩定

> `captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或不穩定，導致測試逾時或失敗。

建議改用本地 HTML 字串或 `data:` URL 來避免外部依賴，或使用 `WKWebView` 的 `loadHTMLString` 方法。

finding 片段：`webView.load(URLRequest(url: url))`

## P0794

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）threshold 欄位使用 parseInt 而非 Number

> 在其他元件中，threshold 的 onChange 使用 `Number(e.target.value)`，但此處使用 `parseInt(e.target.value)`。`parseInt` 會忽略非數字字元，例如輸入 '12abc' 會得到 12，而 `Number` 會得到 NaN。建議統一使用 `Number` 以保持一致性並避免非預期行為。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0795

**GT**（rule）Line exceeds 110 character width

> Biome formatting requires a max line width of 110 characters. This newly added line appears to exceed that limit and should be wrapped across multiple lines.

GT 片段：`const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId: session.user.id });`

**finding**（`apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30`，距錨點 0 行）新增的 redirect 可能造成無限重導向迴圈

> 在 `getting-started` 頁面新增 redirect 到 `/onboarding/personal/settings`，但若該頁面也執行相同的 pending invite 檢查並 redirect 回來，可能形成迴圈。需要確認 `/onboarding/personal/settings` 的邏輯是否會再次觸發 redirect。

finding 片段：`const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId: session.user.id }); ⏎ if (hasPendingInvite) { ⏎ return redirect("/onboarding/personal/settings"); ⏎ }`

## P0796

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行）generate_github_mirror_url_from_base 移除 set_path 可能改變行為

> 原本的程式碼會將 `cdn` 的 path 設定為 `github_url`，但修改後直接使用 `cdn.to_string()`，這可能導致 mirror URL 的 path 未被正確設定，影響 GitHub 下載的 mirror 功能。需確認此變更是否為預期行為。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## P0797

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:32`，距錨點 0 行）assert smtp is not None 可能被最佳化移除

> 新增的 `assert smtp is not None` 在 Python 最佳化模式（-O）下會被移除，且此處 smtp 必定不為 None，因為建構子已指派。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0798

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）日期計算可能因時區或浮點數誤差導致天數不正確

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `new Date(created_at).getTime()` 的差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或 `created_at` 包含時間部分，可能導致天數計算與預期不符。此外，浮點數除法後取 ceil 可能因精度問題造成邊界錯誤。建議改用 UTC 日期字串比較或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0799

**GT**（rule）Missing sync wrapper for async function

> The public API function run_deployment is now just an alias to the async-only arun_deployment function, lacking a proper sync compatibility wrapper. This forces users to always use asyncio.run() or similar async context managers in synchronous code.

GT 片段：`# Alias for backwards compatibility ⏎ run_deployment = arun_deployment`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 0 行）同步呼叫路徑失效：`run_deployment` 不再支援同步執行

> 原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫。此 PR 移除了該裝飾器，並將 `run_deployment` 設為 `arun_deployment` 的別名，但 `arun_deployment` 是純非同步函式。這導致所有現有的同步呼叫（例如 `run_deployment(...)` 在沒有事件迴圈的環境中）會拋出 `RuntimeError` 或回傳 coroutine 物件而非實際結果。測試中仍使用 `_sync=True` 參數呼叫，但該參數已不存在於函式簽名中，會引發 `TypeError`。

**失敗情境**：任何在同步 Python 腳本或測試中呼叫 `run_deployment` 的使用者，會遇到 `TypeError: run_deployment() got an unexpected keyword argument '_sync'` 或 `RuntimeError: no running event loop`。

**建議**：保留同步包裝器，例如使用 `asyncio.run` 或 `anyio.run` 在同步函式中執行非同步邏輯，或提供獨立的同步函式。

finding 片段：`run_deployment = arun_deployment`

## P0800

**GT**（func）Incorrect initialization order in test setup

> In FeatureFlaggedTestSuite.setUp(), the method calls setUpApp() before setUpExperimentVariables(). However, setUpApp() (line 42-44) directly uses jsonFileName and featureName properties that are initialized by setUpExperimentVariables(). This means setUpApp() will be called with nil or uninitialized values, causing addLaunchArgument() to receive invalid parameters. This breaks the experiment/feature flag configuration for all tests inheriting from FeatureFlaggedTestSuite, resulting in tests running with incorrect or missing feature flags.

GT 片段：`override func setUp() async throws { ⏎ continueAfterFailure = false ⏎ setUpApp()  // Called before setUpExperimentVariables ⏎ setUpExperimentVariables()  // Sets jsonFileName and featureName`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48`，距錨點 0 行）setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試行為

> 原本的順序是先 `setUpExperimentVariables()` 再 `setUpApp()`，現在改成先 `setUpApp()` 再 `setUpExperimentVariables()`。如果 `setUpApp()` 依賴實驗變數的設定，這個順序變更可能導致測試行為改變。建議確認此變更是否為刻意為之，並確保不會影響測試結果。

finding 片段：`setUpApp() ⏎ setUpExperimentVariables()`
