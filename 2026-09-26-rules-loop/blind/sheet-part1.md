# 盲標單 1：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-26-rules-loop/blind/labels-part1.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0001

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）number 輸入框 type 改為 text 可能破壞數值輸入

> 將 number 輸入框的 `type` 從 `"number"` 改為 `"text"`，這會失去瀏覽器原生的數值輸入行為（如 spinner、行動裝置數字鍵盤），且可能允許非數值字元輸入。若後端預期數值，可能導致提交錯誤。請確認此變更的必要性，或改用 `inputMode="numeric"` 等替代方案。

finding 片段：`type="text"`

## P0002

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行）RequestBody.Description 指派位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在處理範例之前，現在移到範例處理之後。若 `propertyComment.Examples` 存在且解析失敗，原本仍會設定 Description，現在則可能不會。建議確認此順序變更是否會造成行為差異。

finding 片段：`operation.RequestBody.Description = description;`

## P0003

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行）暖身完成後回傳 Infinity 可能導致呼叫端未預期行為

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接使用此值進行數學運算或與其他數值比較，可能產生非預期結果。例如，若呼叫端將此值傳入 `Math.min` 或作為陣列索引，可能導致錯誤。建議回傳 `emailCount`（表示無限制）或定義明確的常數，並確認所有呼叫端都能正確處理。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0004

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0005

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行）truncate 失敗時未設定 ret，可能導致函式回傳成功但 AOF 未修復

> 在 `fmterr` 處理中，如果 `truncate(aof_filepath, valid_up_to)` 失敗（例如權限不足或檔案系統錯誤），程式只記錄警告，但沒有將 `ret` 設為 `AOF_FAILED`。這會讓函式繼續執行到 `cleanup`，最後回傳 `ret` 的目前值（可能是 `AOF_OK` 或 `AOF_TRUNCATED`），導致 Redis 認為 AOF 載入成功，但實際上檔案仍然損壞。

**失敗情境**：當 AOF 檔案權限為唯讀，或磁碟空間不足導致 truncate 失敗時，Redis 會無視錯誤繼續啟動，之後可能讀到損壞的資料或再次崩潰。

**建議**：在 `truncate` 失敗的分支中，將 `ret` 設為 `AOF_FAILED`，並確保後續流程正確處理。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0006

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 驗證條件從 `if (value <= 0)` 改為 `if (value < 0)`，這將允許 `RetainedFileCountLimit = 0`。但文件描述為「strictly positive value」，且 0 可能導致未定義行為（例如保留 0 個檔案）。建議確認此變更是否為預期，若非預期應改回 `<= 0`。

finding 片段：`if (value < 0)`

## P0007

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）使用 console.error 違反前端規範

> 此處使用 `console.error` 記錄錯誤，違反專案規範  （Frontend Code Must Not Use console Statements）。建議改用專案允許的 logging 機制，或移除該 console 語句。

finding 片段：`console.error('Failed to load React Scan devtools:', error)`

## P0008

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）bootstrapDependencies() 為 async 但呼叫處未加 await

> 在 async setUp 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 時未加上 `await`，而該方法已改為 async（標記 @MainActor 且無同步版本）。這會導致編譯錯誤：`async call in a function that does not support concurrency`。

建議改為 `await DependencyHelperMock().bootstrapDependencies()`。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0009

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 回傳型別可能變為 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但修改後直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，此函式現在會回傳 undefined，可能導致呼叫端出現錯誤。請確認呼叫端是否能處理 undefined，或保留原本的條件判斷。

finding 片段：`return history;`

## P0010

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2306`，距錨點 3 行）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0011

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0012

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）暖身完成後回傳 Infinity 可能導致呼叫端未預期行為

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接使用此值進行數學運算或與其他數值比較，可能產生非預期結果。例如，若呼叫端將此值傳入 `Math.min` 或作為陣列索引，可能導致錯誤。建議回傳 `emailCount`（表示無限制）或定義明確的常數，並確認所有呼叫端都能正確處理。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0013

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`public async Task SupportsRouteParametersFromControllers()`

**finding**（`src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:100`，距錨點 1 行）測試方法缺少 Arrange-Act-Assert 註解

> 新增的測試方法 SupportsRouteParametersFromControllers 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範  。建議加入結構化註解以提升可讀性。

finding 片段：`[Fact] ⏎ public async Task SupportsRouteParametersFromControllers() ⏎ {`

## P0014

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）TanStack Devtools 載入失敗時完全靜默

> catch 區塊僅回傳空元件，沒有任何錯誤記錄。這使得在開發環境中若動態 import 失敗，開發者將無法得知原因，增加除錯困難。建議至少加入 `console.error` 或使用 Sentry 記錄錯誤。

finding 片段：`}).catch(() => { ⏎ return { default: () => null } ⏎ }),`

## P0015

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）移除預設 max_length 後可能導致無限制輸入

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 作為長度上限，現在改為直接使用 `varItem.max_length`。若後端未提供 `max_length`（例如舊資料或未設定），則 `varItem.max_length` 為 `undefined`，比較 `item[varIndex].length > undefined` 會得到 `false`，因此不會觸發長度錯誤，等同於無限制。請確認後端是否保證提供 `max_length`，或在前端保留預設值作為 fallback。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0016

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行）缺少 error boundary 處理查詢失敗

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 error boundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層或路由層級加入 error boundary，並提供 fallback UI。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## P0017

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1725`，距錨點 2 行）valid_up_to 可能為 -1 時仍進行截斷

> 在 `fmterr` 處理中，若 `valid_up_to == -1`，程式僅記錄警告，但之後仍可能執行 `truncate(aof_filepath, valid_up_to)`，此時 `valid_up_to` 為 -1，會導致截斷至檔案開頭前一個位元組，造成整個檔案被清空。建議在 `valid_up_to == -1` 時直接跳過截斷邏輯，並設定 `ret = AOF_FAILED`。

finding 片段：`if (valid_up_to == -1) { ⏎ serverLog(LL_WARNING,"Last valid command offset is invalid"); ⏎ } else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

## P0018

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）屬性 badges 的 label 合併了權重與群組標記，可能造成視覺與語意回歸

> 原本的實作中，權重（如 80%）會顯示在獨立的 Badge 中，且群組選項使用 orange variant 並有視覺分隔。現在將權重與群組標記直接附加到 label 字串中，例如 "Value 80% (group)"，這可能導致：
1. 權重不再有獨立的視覺樣式（如背景色），可能降低可讀性。
2. 群組標記 "(group)" 是硬編碼的英文，未使用 i18n，可能導致在地化問題。
3. 若 value 本身包含空格，label 的組合可能產生不必要的空白。
建議保留原本的雙 Badge 結構，或至少將權重與群組標記分開呈現，並使用翻譯。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0019

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試中使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，參數使用 `GenericComponent<int>`，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得組件名稱和完整名稱。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而不是 `GenericComponent<string>`。

**失敗情境**：執行此測試時，`preambleMarker.Assembly` 和 `preambleMarker.TypeName` 會是 `GenericComponent<int>` 的組件和型別名稱，但斷言期望的是 `GenericComponent<string>` 的名稱，因此測試會失敗。

**建議修法**：將斷言中的 `typeof(GenericComponent<string>)` 改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0020

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）sortableKeys 包含不可移動的 prefix items，可能導致拖放索引錯亂

> `sortableKeys` 直接使用所有 `localKeyedValues` 的 key，但 `canMove` 對 prefix items 回傳 false，這些項目不應參與排序。若使用者拖曳可移動項目到 prefix item 上，`handleDragEnd` 會計算出新索引並呼叫 `moveItem`，但 `moveItem` 內部可能未考慮 prefix items 不可移動的限制，導致陣列順序錯誤或 prefix items 被移動。

建議：`sortableKeys` 應只包含 `canMove` 為 true 的項目 key，並在 `handleDragEnd` 中檢查 `over` 是否為可移動項目。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0021

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 0 行）gtk 外掛腳本存在時仍會覆寫

> 原本邏輯是當 `gtk` 檔案不存在時才下載，但修改後變成當檔案存在時才寫入內嵌腳本。這會導致已存在的檔案被覆寫，可能不是預期行為。應改為 `if !gtk.exists()`。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0022

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0023

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯變更可能遺失變數

> 原文為「{memberEmail} will no longer receive {newsletterName} newsletter.」，新翻譯為「{memberEmail}将不会再收到新闻信。」，遺漏了 {newsletterName} 變數。這可能導致使用者無法得知具體是哪個新聞信。建議保留變數，例如「{memberEmail}将不会再收到{newsletterName}新闻信。」

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0024

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 setLoading(false) 可能導致 loading 狀態卡住

> 在 minimal 模式下，成功提交後原本會呼叫 setLoading(false) 來停止載入狀態，但此 PR 移除了該呼叫。若 submit 流程中 loading 狀態被設為 true，且沒有其他機制將其設回 false，則 UI 可能永遠顯示載入中。請確認是否有其他路徑會重設 loading，否則應保留此呼叫。

finding 片段：`setSuccess(true);`

## P0025

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）console.log 可能洩漏使用者輸入資料

> 新增的 `console.log` 會將批次輸入的資料（包含使用者提供的內容）輸出到瀏覽器主控台。這可能導致敏感資訊外洩，且不應存在於正式程式碼中。

建議移除該行。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0026

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行）新增的 v147 結構體可能造成重複定義或未使用

> 原本的 `InactiveTabs` 結構體被刪除，但新增了一個 `v147` 結構體，內容完全相同。這可能導致：
1. 若 `v147` 未被使用，則為無效程式碼。
2. 若其他程式碼仍引用舊的 `InactiveTabs`，則會編譯錯誤。

請確認是否應直接刪除這些字串，或保留但更新引用。

finding 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString(`

## P0027

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈邊界錯誤導致堆積緩衝區溢位

> 在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 僅配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成堆積緩衝區溢位。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之後的記憶體，可能導致未定義行為。

**失敗情境**：當命令包含至少一個 key 時，每次呼叫此函式都會觸發溢位，可能導致程式崩潰或安全漏洞。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0028

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 13 行）拖放索引計算未考慮 prefixItems，可能導致項目錯位

> `handleDragEnd` 使用 `localKeyedValues` 的索引來呼叫 `moveItem`，但 `moveItem` 預期的是「可移動項目」的索引（已扣除 prefixItems）。當陣列有 prefixItems 時，`localKeyedValues` 包含所有項目，而 `moveItem` 內部可能使用 `getCanMoveForIndex` 或直接操作索引，導致拖放後項目順序錯誤。

建議：在 `handleDragEnd` 中先計算可移動項目的索引，或修改 `moveItem` 使其接受原始索引並在內部處理 prefixItems 偏移。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0029

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 回傳型別可能變為 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但修改後直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，此函式現在會回傳 undefined，可能導致呼叫端出現錯誤。請確認呼叫端是否能處理 undefined，或保留原本的條件判斷。

finding 片段：`return history;`

## P0030

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行）json.dumps(subscription_plan) 可能失敗，導致快取寫入中斷

> 在 `get_plan_bulk_with_cache` 中，從 `get_plan_bulk` 取得的 `subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps` 預期可序列化的物件。若 `SubscriptionPlan` 包含非 JSON 相容的型別（例如 datetime、Decimal 等），`json.dumps` 會拋出 `TypeError`，導致整個 pipeline 執行失敗，且該例外被外層 `except` 捕捉後僅記錄日誌，不會寫入任何快取。

**失敗情境**：當 billing API 回傳的 `expiration_date` 是 ISO 格式字串而非整數時，`validate_python` 可能將其轉為 datetime 物件，此時 `json.dumps` 會失敗。

**建議**：在序列化前先將 `subscription_plan` 轉為純 dict（例如 `dict(subscription_plan)`），或使用 Pydantic 的 `model_dump()` 方法（若改用 BaseModel）。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0031

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 setLoading(false) 可能導致 loading 狀態卡住

> 在 minimal 模式下，成功送出表單後原本會呼叫 setLoading(false) 來結束載入狀態，但此 PR 移除了該呼叫。若 submit 函式在成功後沒有在其他地方將 loading 設為 false，UI 可能會永遠顯示載入中。請確認 submit 函式的實作，或保留此呼叫。

finding 片段：`setSuccess(true);`

## P0032

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:68`，距錨點 23 行）Popover 在桌面端僅依賴 mouseenter/mouseleave，缺乏鍵盤與觸控支援

> 在桌面端，Popover 的開啟與關閉僅由 Button 和 PopoverContent 上的 onMouseEnter/onMouseLeave 控制。這會導致：
1. 鍵盤使用者無法聚焦到觸發按鈕並開啟 popover（除非 PopoverTrigger 本身有處理，但此處未提供）。
2. 觸控裝置（如平板）沒有 hover 事件，使用者可能無法查看隱藏的 badges。
建議使用 Popover 的 trigger 屬性（如 click）或確保 Button 可聚焦並處理鍵盤事件，或提供明確的點擊切換。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0033

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）測試斷言可能使用錯誤的 accessibility identifier

> 在 `testCheckSystemThemeChanges` 中，原本檢查 `lightThemeView` 的 value，現在改為檢查 `darkThemeView`。但變數名稱仍為 `lightIsSelected`，且後續斷言 `XCTAssertEqual(lightIsSelected as? String, "1")` 可能與實際選取的主題不符。若測試目的是驗證選取 Light 模式後對應的按鈕狀態，應檢查 `lightThemeView` 而非 `darkThemeView`。建議確認此變更是否為預期，並修正變數名稱與斷言邏輯。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0034

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

## P0035

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 5 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0036

**GT**（func）Public methods lack required documentation comments

> The helper methods checkUrl(), copyUrl(), and checkCopiedUrl() were changed from internal to public visibility in this PR. According to AGENTS.md Rule 14, all public API elements must include triple-slash (///) documentation comments describing their purpose, behavior, parameters, and return values. These methods only have single-line comments (// Comment) instead of proper documentation comments (/// Comment). This violates the repository's explicit compliance rules for public APIs.

GT 片段：`// Check for test url in the browser ⏎ public func checkUrl() { ⏎ // Copy url from the browser ⏎ public func copyUrl() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ClipBoardTests.swift:11`，距錨點 0 行）輔助方法改為 public 可能違反封裝原則

> 將 `checkUrl()`、`copyUrl()`、`checkCopiedUrl()` 三個方法從 internal 改為 public。這些方法僅在測試類別內部使用，若無外部呼叫需求，建議維持 internal 或改為 private，以符合最小暴露原則。

finding 片段：`public func checkUrl() {`

## P0037

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0038

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴組合方式與後端不一致

> 前端將 `config.version` 直接加在 `endpointName` 前面（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是加在後面（`${pipeName}_${version}`）。若同時使用前端與後端，會產生不同的端點名稱（例如前端 `v2_api_kpis` vs 後端 `api_kpis_v2`），導致請求失敗。

建議統一命名規則，例如都使用後綴方式。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0039

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或序列化名稱），可能找不到對應的參數。建議確認兩者是否永遠相同，或保留原本的比對方式。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0040

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## P0041

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）write_and_make_executable 先設定權限再寫入檔案

> 函式 `write_and_make_executable` 先呼叫 `fs::set_permissions` 設定權限，再呼叫 `fs::write` 寫入檔案。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致無法建立檔案。應先寫入檔案再設定權限，或使用 `OpenOptions` 建立檔案後設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0042

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）日期計算可能因時區或時鐘偏移產生 off-by-one 錯誤

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並無條件進位。若伺服器時區與 UTC 有偏移，或系統時鐘在兩次呼叫間被調整，可能導致天數計算錯誤。例如，若首次 email 建立於 UTC 23:59，而目前時間為 UTC 00:01（相差 2 分鐘），計算結果為 1 天，但實際上可能尚未滿 24 小時。建議改用日曆日期（如 `created_at` 的日期部分與今天的日期差）來計算天數，或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0043

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 為 0 時可能被錯誤視為未提供

> 在 SQL 條件 `(${orgId}::bigint IS NULL OR ...)` 中，若 orgId 為 0，則 `0::bigint IS NULL` 為 false，因此會進入後面的 OR 條件。但若 orgId 為 0 且資料庫中沒有 id 為 0 的 team，則結果會是空集合，而非預期的「不限制 orgId」。這可能導致呼叫端傳入 0 時意外地得不到任何結果。建議在 TypeScript 層先將 orgId 轉為 null 或 undefined，或明確處理 0 的情況。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0044

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 18 行）鍵盤使用者無法操作 Popover

> PopoverTrigger 包著 Button，但 Button 沒有設定 onClick 處理常式，而是依賴 Popover 的 onOpenChange。鍵盤使用者聚焦到 Button 後按 Enter 或 Space 會觸發 Button 的點擊事件，但 Popover 可能不會因此開啟，因為 PopoverTrigger 的 asChild 會將事件處理器傳遞給 Button，但 Button 本身沒有 onClick，可能導致事件無法正確觸發 Popover 的開啟。建議明確設定 Button 的 onClick 來切換 isOpen，或確保 PopoverTrigger 的事件處理能正確傳遞。

finding 片段：`<Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0" ⏎ aria-label={`Show ${hiddenItems.length} more items`}`

## P0045

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈邊界錯誤導致堆積緩衝區溢位

> 在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 僅配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成堆積緩衝區溢位。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之後的記憶體，可能導致未定義行為。

**失敗情境**：當命令包含至少一個 key 時，每次呼叫此函式都會觸發溢位，可能導致程式崩潰或安全漏洞。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0046

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）未使用的變數 isLandscape

> 在 setupSkeletonAddressBarsLayout 中新增了 isLandscape 變數，但並未在後續程式碼中使用。這可能是開發中的殘留，應移除或實際使用。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0047

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）條件反轉可能改變行為

> `crate_version` 中的條件由 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。此修正可能正確（原本邏輯可能有誤），但需確認是否會影響依賴版本解析。建議補充測試或說明。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0048

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0049

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行）快取寫入時未處理 json.dumps 可能拋出的例外

> `json.dumps(subscription_plan)` 可能因為 `subscription_plan` 包含不可序列化的物件而拋出 `TypeError`。雖然 `SubscriptionPlan` 是 `TypedDict`，但實際值可能包含其他型別（例如 `datetime` 物件），導致序列化失敗。此例外會中斷整個 pipeline 的執行，且不會被外層的 `try` 捕捉（因為 `try` 只包住 `pipe.execute()`）。

**失敗情境**：如果 `subscription_plan` 中包含一個 `datetime` 物件，`json.dumps` 會拋出 `TypeError`，導致整個快取寫入失敗，且沒有記錄任何錯誤。

**建議修法**：將 `json.dumps` 移入 `try` 區塊，或使用 `default=str` 參數來處理不可序列化的物件。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0050

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0051

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）lseek 失敗後仍可能繼續執行

> 若 `lseek` 失敗，程式記錄警告後並未設定 `ret` 或跳轉到錯誤處理，而是繼續執行 `loaded_ok` 流程。這可能導致 AOF 檔案指標未正確更新，後續寫入可能覆蓋錯誤位置。建議在 `lseek` 失敗時設定 `ret = AOF_FAILED` 並跳轉到 cleanup。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0052

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷邏輯變更可能影響行為

> 原本的 `isCurrentUser` 判斷為 `filters.userIds.length === 1 && user.id === filters.userIds[0]`，現在改為 `filters.userIds.includes(user.id)`。這表示當 `userIds` 包含多個 ID 且其中包含當前使用者時，`isCurrentUser` 會是 true，可能導致後續的權限檢查邏輯改變。

請確認此變更是否符合預期，並確保不會造成權限繞過。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0053

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行）Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤

> 原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot.userIds 的型別是 number[]，但此處新定義的 Slot.userIds 型別為 string[]。這可能導致使用該型別的下游程式碼（例如 apps/web/test/lib/getSchedule/expects.ts）在編譯或執行時發生型別不符的錯誤。建議確認實際資料型別，若確實為 string[] 則需同步更新所有相關程式碼；若為 number[] 則應修正此處定義。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## P0054

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0055

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試使用錯誤的泛型型別參數

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，參數使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為實際元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。

建議將斷言中的 `GenericComponent<string>` 改為 `GenericComponent<int>`，以符合實際使用的型別。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0056

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行）hasPageActions 判斷改用 leadingPageActionStack，可能導致分隔線顯示錯誤

> 原本 `hasPageActions` 是根據 `pageActionStack`（即現在的 `trailingPageActionStack`）是否有 arranged subviews 來決定是否顯示分隔線。此 PR 將其改為檢查 `leadingPageActionStack`。如果 leading 和 trailing page actions 的存在性不一致（例如只有 trailing 有 actions），分隔線的顯示將不正確。

**失敗情境**：當 toolbar 配置為只有 trailing page actions 而沒有 leading page actions 時，`hasPageActions` 會是 false，導致分隔線寬度設為 0，即使 trailing 區域有按鈕也看不到分隔線。

**建議**：應同時考慮 leading 和 trailing page actions，例如 `let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty || !trailingPageActionStack.arrangedSubviews.isEmpty`，或根據實際需求選擇正確的 stack。

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## P0057

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript strict 模式

> 將 `strict` 從 `true` 改為 `false` 違反了專案規範  （TypeScript Must Enable Strict Type Checking）。這會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復 `strict: true`，並修正因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0058

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）crate_version 邏輯修正可能改變既有行為

> 將 `if lock.is_some() && crate_lock_packages.is_empty()` 改為 `if lock.is_some() && !crate_lock_packages.is_empty()`。這會使得原本在 lock 存在但 crate_lock_packages 為空時不執行的程式碼，現在會執行；反之亦然。需確認此修正是否為預期，並評估對版本解析的影響。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0059

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28`，距錨點 8 行）tearDown 中呼叫 reset() 未加 await

> `DependencyHelperMock().reset()` 可能也是 async 或需在主執行緒執行，但此處未加 await。若 reset 為同步方法則無問題，但需確認其簽名。

finding 片段：`DependencyHelperMock().reset()`

## P0060

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0061

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript strict 模式會降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查，包括 `strictNullChecks`、`strictFunctionTypes` 等，可能導致未處理的 null/undefined 錯誤、錯誤的型別推斷，並隱藏潛在的執行時期錯誤。這通常不是一個可接受的變更，除非有明確的技術原因。建議恢復為 `true`，並修正任何因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0062

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> `UIApplication.shared.statusBarOrientation` 在 iOS 13 已棄用，建議改用 `view.window?.windowScene?.interfaceOrientation` 或 `traitCollection.verticalSizeClass` 來判斷方向。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0063

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:325`，距錨點 31 行）Redis mget 回傳值長度檢查可能誤判

> 在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## P0064

**GT**（rule）New/modified path resolution introduces panics/unwraps for fallible operations

> `resolve_dirs` uses `panic!` and `unwrap()` (`tauri.parent().unwrap()`) for fallible operations (project discovery/path parent resolution) instead of returning a `Result`, violating the rule to make failure explicit rather than panicking.

GT 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| { ⏎ let env_var_name = env_tauri_app_path().is_some().then(|| format!("`{ENV_TAURI_APP_PATH}`")); ⏎ panic!("Couldn't recognize the {} folder as a Tauri project. It must contain a `{}`, `{}` o`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:130`，距錨點 0 行）`resolve_dirs()` 使用 `OnceLock` 快取路徑，可能導致測試或動態環境變更時取得舊值

> `resolve_dirs()` 使用 `OnceLock` 的 `get_or_init` 來初始化 `TAURI_DIR` 和 `FRONTEND_DIR`。這表示在一個程序的生命週期內，第一次呼叫後，後續呼叫都會回傳相同的路徑，即使環境變數（如 `TAURI_APP_PATH`、`TAURI_FRONTEND_PATH`）或目前工作目錄已經改變。

**失敗情境**：在測試中，若先以某個工作目錄呼叫 `resolve_dirs()`，之後 `std::env::set_current_dir` 切換到另一個 Tauri 專案，再呼叫 `resolve_dirs()`，仍會回傳第一個專案的路徑，導致後續操作作用在錯誤的目錄上。

**建議**：若需要支援動態變更，應考慮每次重新解析，或提供明確的 reset 機制。若確定程式只會解析一次，則應在文件或註解中說明此限制。

finding 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| {`

## P0065

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行）`Dirs` 持有 `&'static Path` 可能導致生命週期問題

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但其實際指向的 `PathBuf` 儲存在 `OnceLock` 中。雖然 `OnceLock` 的內容在程式結束前不會被釋放，因此生命週期上可行，但這會造成記憶體永遠無法回收，且若未來改為非靜態儲存，將導致 dangling reference。建議改為持有 `PathBuf` 或使用 `Arc<Path>`，以避免潛在的生命週期問題。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## P0066

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0067

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:19`，距錨點 0 行）Slot.userIds 型別從 number[] 改為 string[] 可能造成執行時期錯誤

> 原本 `@calcom/trpc/server/routers/viewer/slots/types` 中的 `Slot.userIds` 型別為 `number[]`，但此處新定義為 `string[]`。若實際 API 回傳的 userIds 是數字陣列，使用此型別的程式碼（例如將 userIds 傳入需要 number 的函式）會在執行時期發生型別不符的錯誤。建議確認 API 實際回傳型別，若為 number[] 則應改回 `number[]`，或使用 union type 並進行轉換。

finding 片段：`userIds?: string[];`

## P0068

**GT**（func）Empty lines not filtered in Expected Events textarea

> In the CustomTriggerFields component, the onChange handler for the Expected Events textarea fails to filter out empty or whitespace-only lines. When users press Enter multiple times or leave blank lines between events, these empty strings are included in the events array sent to the trigger configuration. This will cause backend validation failures or create malformed automation triggers that expect empty event names, leading to automations that never fire correctly.

GT 片段：`onChange={(e) => { ⏎ const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined); ⏎ }}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38`，距錨點 0 行）Expected Events 欄位可能將空陣列轉換為 undefined

> 在 `onChange` 中，當使用者清空 textarea 時，`e.target.value.split("\n")` 會得到 `[""]`，`lines.length > 0` 為 true，因此 `field.onChange([""])` 會將值設為包含一個空字串的陣列，而非預期的 `undefined` 或空陣列。這可能導致表單驗證或後續處理出現非預期行為。建議改為：`const lines = e.target.value.split("\n").filter(line => line.trim() !== ""); field.onChange(lines.length > 0 ? lines : undefined);`

finding 片段：`const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined);`

## P0069

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0070

**GT**（rule）Unused import: Skeleton

> `Skeleton` is imported but never used in this file, which violates the rule requiring unused imports to be removed.

GT 片段：`import { Skeleton } from "@/components/ui/skeleton";`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1`，距錨點 5 行）缺少對應的測試檔案

> 根據規範  ，每個 React 元件檔案應有同目錄下的測試檔案（`flow-icon-text.test.tsx`）。此 PR 新增了元件但未包含測試，可能降低測試覆蓋率。建議補上測試，涵蓋載入狀態、成功渲染和錯誤處理。

finding 片段：`import { useSuspenseQuery } from "@tanstack/react-query";`

## P0071

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 未釋放

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0072

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行）鏡像 URL 可能遺失路徑

> `generate_github_mirror_url_from_base` 移除了 `cdn.set_path(github_url)` 呼叫，改為直接回傳 `cdn.to_string()`。這可能導致鏡像 URL 不再包含原始 GitHub URL 的路徑，使得下載請求指向錯誤的資源。需確認此變更是否為預期行為，或是否應保留路徑設定。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## P0073

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0074

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 未釋放

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0075

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）使用 expect 可能導致 panic

> 在 write_and_make_executable 中，使用 fs::set_permissions 和 fs::write 並以 map_err 處理錯誤，但沒有使用 expect 或 unwrap。然而，函式簽名回傳 Result<(), FileWriteError>，但內部可能因為其他原因 panic？實際上沒有直接使用 expect，但建議確認所有可能的錯誤都被妥善處理。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0076

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）Threshold 輸入使用 parseInt 可能產生 NaN 或截斷

> 使用 `parseInt(e.target.value)` 時，若輸入為空字串或非數字字元，會得到 `NaN`；若輸入包含小數，則會被截斷為整數。這可能導致表單值不正確。建議使用 `Number` 並檢查 `Number.isNaN`，或使用 `parseFloat` 並處理無效輸入。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0077

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## P0078

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12`，距錨點 17 行）Storybook decorator 中的 QueryClient 可能造成快取污染

> 在 `createTestRouter` 中，每次呼叫都會建立一個新的 `QueryClient` 並傳入 router context，但 decorator 外層的 `QueryClientProvider` 使用的是模組層級的 `queryClient`。這可能導致不同 story 之間共用快取，造成測試資料互相干擾。建議在 decorator 內建立新的 `QueryClient` 並傳遞給 `QueryClientProvider`，以確保每個 story 有獨立的查詢客戶端。

finding 片段：`const queryClient = new QueryClient({ ⏎ defaultOptions: { ⏎ queries: { ⏎ retry: false,`

## P0079

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行）validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）及 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式的資料，可能導致後續 API 呼叫失敗或產生難以除錯的錯誤。建議使用 Zod 或更完整的型別檢查來驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0080

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0081

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 使用 createStringObjectFromLongLong 建立後未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後沒有對其呼叫 decrRefCount。這會導致每次執行此路徑時洩漏一個 robj。

失敗情境：任何對具有過期時間的 hash 欄位執行 HINCRBYFLOAT 的請求，都會造成記憶體洩漏，長期下來可能耗盡記憶體。

建議修法：在 alsoPropagate 呼叫之後，加入 decrRefCount(argv[2]); 釋放該物件。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0082

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試中未驗證 Descriptor 內容

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，僅驗證了 preamble marker 的 Assembly 與 TypeName，但未驗證 descriptor 的內容（例如參數定義與值）。這可能導致測試涵蓋不足，無法確保序列化與反序列化的正確性。建議參考其他測試（如 ServerMode 測試）增加對 descriptor 的驗證。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0083

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）使用 propertyName 取代 metadata.Name 可能影響參數匹配

> 原本使用 metadata.Name 來尋找 operation.Parameters 中的參數，現在改為 propertyName。若 metadata.Name 與 propertyName 不同，可能導致找不到參數而將描述套用到 RequestBody。需確認此變更符合預期。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0084

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行）新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用

> 檔案中定義的 Schedule 型別未加上 export，但後續的 CreateScheduleHandlerReturn 等型別使用了它。若其他檔案需要直接使用 Schedule，將無法匯入。建議將 Schedule 加上 export，或確認其僅供內部使用。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0085

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291`，距錨點 18 行）自訂錯誤型別未使用 thiserror

> 新增的 `FileWriteError` 手動實作 `Display` 和 `Error`，但專案規範 要求使用 `thiserror`。建議改用 `#[derive(thiserror::Error)]` 來簡化程式碼並保持一致。

finding 片段：`impl std::fmt::Display for FileWriteError { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ match self { ⏎ FileWriteError::Write(e) => write!(f, "Failed to write file: {}", e),`

## P0086

**GT**（func）Missing error logging in TanStack devtools lazy import

> The TanStackDevtoolsLoader silently swallows import errors without logging them, making it impossible to debug why the devtools fail to load. This creates an inconsistent error handling pattern compared to the ReactScanLoader (in the same PR), which properly logs errors with console.error before returning a fallback component. When developers encounter issues with TanStack devtools not appearing, they will have no visibility into whether it's due to an import failure, missing dependencies, or other issues.

GT 片段：`const TanStackDevtoolsWrapper = lazy(() => ⏎ import('./devtools').then(module => ({ ⏎ default: module.TanStackDevtoolsWrapper, ⏎ })).catch(() => {`

**finding**（`web/app/components/devtools/tanstack/loader.tsx:9`，距錨點 0 行）lazy import 錯誤處理靜默失敗

> 在 lazy import 的 catch 中回傳一個渲染 null 的元件，但未記錄任何錯誤。這可能導致開發工具載入失敗時無法察覺，增加除錯困難。建議至少記錄錯誤訊息。

finding 片段：`}).catch(() => { ⏎ return { default: () => null } ⏎ }),`

## P0087

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行）陣列越界：argv 宣告大小為 5，但存取 argv[5]

> 在 hincrbyfloatCommand 中，`robj *argv[5];` 宣告了大小為 5 的陣列，但後續指派了 6 個元素（argv[0] 到 argv[5]），導致寫入超出陣列邊界。這會造成 stack buffer overflow，可能導致程式崩潰或安全漏洞。

建議將陣列大小改為 6：`robj *argv[6];`

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0088

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷邏輯變更可能導致權限繞過

> 原本 isCurrentUser 僅在 filters.userIds 長度為 1 且等於 user.id 時為 true，現在改為 includes(user.id)。若 filters.userIds 包含多個 ID 且包含 user.id，則 isCurrentUser 為 true，可能允許使用者存取其他使用者的 booking。需確認此變更是否符合預期。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0089

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 slot_buffer 可能非必要

> 新增的 `slot_buffer` 僅用於暫存每個 key 的 slot，但實際上可以直接在迴圈中比較，無需配置額外記憶體。這增加了記憶體使用與失敗點。

**建議修法**：移除 `slot_buffer`，直接在迴圈中計算並比較 slot。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0090

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:376`，距錨點 0 行）快取寫入時可能將 None 序列化為 'null' 字串

> 即使修正了變數名稱，如果 `plans_to_cache` 中包含值為 `None` 的項目（例如 `get_plan_bulk` 回傳的字典中某個 tenant 的值為 `None`），`json.dumps(None)` 會產生字串 `'null'`。之後讀取快取時，`json.loads('null')` 會得到 `None`，然後 `validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，`plans_to_cache` 包含 `tenant-1`，寫入快取的值為 `'null'`。下次讀取時，`json.loads` 得到 `None`，驗證失敗，進入 cache miss，重新呼叫 API，但 API 可能再次回傳 `None`，形成無效快取。

**建議修法**：在寫入快取前，過濾掉值為 `None` 的項目，或確保 `get_plan_bulk` 不會回傳 `None` 值。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0091

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）off-by-one 錯誤：滾動索引超出陣列範圍

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。這會導致 `toIndex` 等於陣列長度，超出有效索引範圍（最後一個索引應為 `count - 1`）。後續在 `TabDisplayView.scrollToTab` 中會使用此索引建立 `IndexPath(row:section:)`，可能造成滾動到不存在的 cell，甚至觸發越界例外。

建議改回 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0092

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28`，距錨點 8 行）tearDown 中呼叫 @MainActor 方法可能導致執行緒問題

> `tearDown` 中呼叫 `DependencyHelperMock().reset()` 未加 `await`，但 `reset` 可能也是 @MainActor 隔離。若測試類別未標記 @MainActor，可能導致編譯錯誤或執行緒問題。建議檢查 `reset` 的隔離屬性，並在必要時加上 `await` 或將類別標記為 @MainActor。

finding 片段：`override func tearDown() async throws { ⏎ AppContainer.shared.reset() ⏎ UserDefaults.standard.removeObject(forKey: PrefsKeys.NimbusUserEnabledFeatureTestsOverride) ⏎ profile = nil`

## P0093

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 中 slot_buffer 可能未完全初始化

> 若 `malloc` 成功但迴圈因 cross-slot 提前結束，`slot_buffer` 中剩餘元素未初始化，但這不影響 free。然而，若未來程式碼讀取這些未初始化值，可能導致問題。建議在 malloc 後使用 `memset` 初始化，或避免分配不必要的記憶體。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0094

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:346`，距錨點 37 行）orgId 過濾條件可能導致 fallback roles 結果不完整

> 在 `getTeamsWithFallbackRoles` 的第一個 UNION 分支中，過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`，同樣只包含直接子團隊。若團隊階層超過兩層，則更深層的子團隊將不會被包含，可能導致使用者無法取得應有的 fallback 權限。

建議與 PBAC 查詢使用一致的階層處理邏輯。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0095

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤

> `LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 方法中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 await，但方法已改為 async @MainActor），可能導致編譯錯誤。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0096

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444`，距錨點 5 行）metadata 為 null 時跳過處理可能遺失部分 XML 註解

> 新增 `metadata is not null` 條件後，當 `parameterDescription.ModelMetadata` 為 null 時會直接跳過整個區塊。若此情況在實際執行中可能發生（例如某些參數沒有對應的 ModelMetadata），則原本可能套用的 XML 註解將不再套用。建議確認此行為是否符合預期，或考慮在 null 時採取其他處理方式。

finding 片段：`if (metadata is not null ⏎ && metadata.MetadataKind == ModelMetadataKind.Property`

## P0097

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行）鏡像 URL 處理方式變更可能導致錯誤網址

> 原本 `generate_github_mirror_url_from_base` 會將 `cdn` 的 path 設為 `github_url`，現在直接回傳 `cdn.to_string()`。這可能導致鏡像網址不再包含原始 GitHub URL 的路徑，使得下載失敗或指向錯誤資源。需要確認此變更是否為預期行為，並驗證鏡像功能是否仍正常運作。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## P0098

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）骨架位址列約束可能誤用 rightSkeletonAddressBar

> 在 `setupSkeletonAddressBars` 中，`toolbar.leadingAnchor` 被約束到 `rightSkeletonAddressBar.trailingAnchor`，但根據前後文，此處應為 `leftSkeletonAddressBar.trailingAnchor`。這可能導致工具列在滑動分頁時位置錯誤。

建議改為 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0099

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 在 cross-slot 時可能洩漏記憶體

> 在偵測到 cross-slot 時，函式會 `free(slot_buffer)` 後回傳 `CLUSTER_CROSSSLOT`，但若 `malloc` 失敗（回傳 NULL），則 `slot_buffer` 為 NULL，`free(NULL)` 是安全的，但後續的 `slot_buffer[j] = this_slot` 會對 NULL 指標寫入，造成 segmentation fault。

**失敗情境**：當記憶體不足導致 `malloc` 回傳 NULL 時，程式會崩潰。

**建議修法**：檢查 `malloc` 回傳值，若為 NULL 則回傳錯誤或改用 `zmalloc`（其會終止程式）。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0100

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行）RequestBody.Description 設定位置變更可能影響行為

> 原本在 if (operation.RequestBody is not null) 區塊開頭就設定 operation.RequestBody.Description = description，現在移到區塊結尾。若中間有 continue 或例外，可能導致描述未被設定。需確認此變更不會造成遺漏。

finding 片段：`operation.RequestBody.Description = description;`

## P0101

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 使用 createStringObjectFromLongLong 建立後未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後沒有對其呼叫 decrRefCount。這會導致每次執行此路徑時洩漏一個 robj。

失敗情境：任何對具有過期時間的 hash 欄位執行 HINCRBYFLOAT 的請求，都會造成記憶體洩漏，長期下來可能耗盡記憶體。

建議修法：在 alsoPropagate 呼叫之後，加入 decrRefCount(argv[2]); 釋放該物件。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0102

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，但原文仍包含該變數。這可能導致使用者看不到具體的新聞信名稱，影響理解。建議保留變數。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0103

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0104

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:42`，距錨點 26 行）items 陣列變動時 Popover 狀態未重置

> 當 items 陣列變動（例如從有 hidden items 變成沒有）時，isOpen 狀態可能保持 true，導致 Popover 在沒有 hidden items 時仍然顯示。雖然元件在 items.length === 0 時會回傳 null，但當 hiddenItems 從有變無時，Popover 可能仍然開啟。建議在 items 或 hiddenItems 變化時重置 isOpen。

finding 片段：`const { visibleItems, hiddenItems } = useMemo( ⏎ () => ({ ⏎ visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0105

**GT**（func）Empty lines not filtered in Expected Events textarea

> In the CustomTriggerFields component, the onChange handler for the Expected Events textarea fails to filter out empty or whitespace-only lines. When users press Enter multiple times or leave blank lines between events, these empty strings are included in the events array sent to the trigger configuration. This will cause backend validation failures or create malformed automation triggers that expect empty event names, leading to automations that never fire correctly.

GT 片段：`onChange={(e) => { ⏎ const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined); ⏎ }}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:59`，距錨點 20 行）Threshold 輸入可能產生 NaN

> 當使用者清空輸入框時，`e.target.value` 為空字串，`Number('')` 會得到 `0`，但若輸入非數字字元（例如 'e'），`Number('e')` 會得到 `NaN`。這可能導致表單值變成 `NaN`，進而影響後續驗證或提交。建議在 onChange 中檢查 `Number.isNaN` 或使用 `parseInt` 並處理 `NaN` 的情況。

finding 片段：`onChange={(e) => field.onChange(Number(e.target.value))}`

## P0106

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯變更可能遺失變數

> 原文為「{memberEmail} will no longer receive {newsletterName} newsletter.」，新翻譯為「{memberEmail}将不会再收到新闻信。」，遺漏了 {newsletterName} 變數。這可能導致使用者無法得知具體是哪個新聞信。建議保留變數，例如「{memberEmail}将不会再收到{newsletterName}新闻信。」

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0107

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:309`，距錨點 5 行）公開函式缺少文件註解

> write_and_make_executable 函式是公開的（pub fn），但沒有文件註解。根據規範  ，所有公開 API 都應該有 /// 文件說明其用途、參數和回傳值。建議補充文件。

finding 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> {`

## P0108

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:330`，距錨點 36 行）快取資料驗證失敗時未清除無效快取，可能導致重複失敗

> 在 `get_plan_bulk_with_cache` 中，當從 Redis 讀取的快取資料無法通過 `validate_python` 驗證時，程式碼將該租戶加入 `cache_misses`，但未刪除 Redis 中的無效鍵。這會導致每次呼叫都重複嘗試解析無效資料，並在日誌中產生大量錯誤。

**失敗情境**：若某租戶的快取因版本變更而格式不符，每次批次作業都會嘗試解析並失敗，直到 TTL 過期。

**建議**：在驗證失敗時，主動刪除該租戶的 Redis 鍵（例如 `redis_client.delete(redis_key)`），或使用較短的 TTL 來加速失效。

finding 片段：`except Exception: ⏎ logger.exception( ⏎ "get_plan_bulk_with_cache: process tenant(%s) failed, add to cache misses", tenant_id ⏎ )`

## P0109

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1735`，距錨點 8 行）日誌訊息中 broken size 可能為負數（第二處）

> 與前一個 finding 類似，此處的 `(long long)(sb.st_size - valid_up_to)` 也可能為負數，建議加入檢查。

finding 片段：`serverLog(LL_WARNING, ⏎ "AOF was not loaded because the size of the corrupted portion " ⏎ "exceeds the configured limit. aof-load-broken is enabled and broken size '%lld' " ⏎ "is bigger than aof-load-broken-max-size '%lld'",`

## P0110

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 而非 logging

> 在 propagate_skip_from_edge 方法中新增了 print 陳述式，違反專案規範  （Backend Code Must Use Logging Instead of Print Statements）。print 會直接輸出到 stdout，無法被日誌系統收集，且可能造成效能問題。應改用 logging 模組，並在模組頂部宣告 logger。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0111

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:105`，距錨點 0 行）移除 source 參數傳遞可能造成功能回歸

> 原本會將 `options.source` 加入 Tinybird 查詢參數，但此 PR 移除了該邏輯。若前端或其他呼叫端仍會傳入 `source` 參數，將無法過濾來源，導致統計資料不正確。

請確認是否刻意移除，或應保留此功能。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## P0112

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0113

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行）download_webview2_offline_installer 改用 ureq::get 可能失去 proxy 支援

> 原本使用 `download(url)` 函式（可能包含 proxy 設定），現在改為直接呼叫 `ureq::get(url)`，這可能導致在需要 proxy 的環境下無法下載。建議使用 `base_ureq_agent()` 來建立 agent 並發送請求，以保持 proxy 支援。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`
