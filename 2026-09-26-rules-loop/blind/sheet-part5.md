# 盲標單 5：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-26-rules-loop/blind/labels-part5.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0453

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## P0454

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試中使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，參數使用 `GenericComponent<int>`，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得組件名稱和完整名稱。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而不是 `GenericComponent<string>`。

**失敗情境**：執行此測試時，`preambleMarker.Assembly` 和 `preambleMarker.TypeName` 會是 `GenericComponent<int>` 的組件和型別名稱，但斷言期望的是 `GenericComponent<string>` 的名稱，因此測試會失敗。

**建議修法**：將斷言中的 `typeof(GenericComponent<string>)` 改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0455

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0456

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行）start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致

> 在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0457

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0458

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> 新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0459

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更允許 0 值，與文件描述不符

> 原本的驗證條件為 `value <= 0`，會拒絕 0 和負數；變更後改為 `value < 0`，允許 0 值。但屬性文件仍描述為「strictly positive value」，且錯誤訊息仍為「must be positive」。若設定為 0，可能導致保留檔案數為 0 的意外行為（例如刪除所有舊檔案）。建議維持 `value <= 0` 的驗證，或更新文件與錯誤訊息以允許 0。

finding 片段：`if (value < 0)`

## P0460

**GT**（func）Translation inconsistency for 'Enter your name' field across UI contexts

> The PR introduces an inconsistency in the Chinese translation for the 'Enter your name' input field. In portal.json line 71, it's translated as '输入您的名字' (enter your first name), which suggests only a first name is needed. However, based on the context of Ghost's user registration and profile system, and the fact that the 'Name' field itself should be '姓名' (full name), this creates a mismatch between what the label asks for ('名字' - first name) and what the system actually expects ('姓名' - full name). This can cause user confusion during registration and profile completion, potentially leading to incomplete or incorrectly formatted name entries.

GT 片段：`"Ends {offerEndDate}": "于{offerEndDate}结束", ⏎ "Enter code above": "在上方输入验证码", ⏎ "Enter your email address": "输入您的电子邮箱地址", ⏎ "Enter your name": "输入您的名字",`

**finding**（`ghost/i18n/locales/zh/portal.json:63`，距錨點 5 行）翻譯用語可能不符合繁體中文習慣

> 將「設定」改為「设置」，但「设置」是簡體中文用語。建議維持「設定」。

finding 片段：`"Email newsletter settings updated": "新闻信设置已更新",`

## P0461

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）TryGetValidatableTypeInfo 中 out 參數初始化位置調整

> 將 `validatableTypeInfo = null;` 從方法結尾移至開頭，行為不變，但可能降低可讀性。若無特殊原因，建議保留原位置。

finding 片段：`validatableTypeInfo = null;`

## P0462

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）React Scan 載入失敗時靜默降級，可能隱藏錯誤

> 當 `import('./scan')` 失敗時，`.catch` 回傳一個渲染 `null` 的元件，導致 devtools 完全不出現且沒有任何使用者可見的提示。雖然有 `console.error`，但在 production 環境中可能被忽略。建議在開發環境中顯示一個明顯的錯誤訊息，或至少保留錯誤狀態供後續處理。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0463

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:376`，距錨點 0 行）快取寫入時未處理 json.dumps 可能拋出的例外

> `json.dumps(subscription_plan)` 可能因為 `subscription_plan` 包含不可序列化的物件而拋出 `TypeError`。雖然 `SubscriptionPlan` 是 `TypedDict`，但實際值可能包含其他型別（例如 `datetime` 物件），導致序列化失敗。此例外會中斷整個 pipeline 的執行，且不會被外層的 `try` 捕捉（因為 `try` 只包住 `pipe.execute()`）。

**失敗情境**：如果 `subscription_plan` 中包含一個 `datetime` 物件，`json.dumps` 會拋出 `TypeError`，導致整個快取寫入失敗，且沒有記錄任何錯誤。

**建議修法**：將 `json.dumps` 移入 `try` 區塊，或使用 `default=str` 參數來處理不可序列化的物件。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0464

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2306`，距錨點 3 行）陣列越界：argv 宣告大小為 5，但存取 argv[5]

> 在 hincrbyfloatCommand 中，`robj *argv[5];` 宣告了大小為 5 的陣列，但後續指派了 6 個元素（argv[0] 到 argv[5]），導致寫入超出陣列邊界。這會造成 stack buffer overflow，可能導致程式崩潰或安全漏洞。

建議將陣列大小改為 6：`robj *argv[6];`

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## P0465

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）及 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式的資料，可能導致後續 API 呼叫失敗或產生難以除錯的錯誤。建議使用 Zod 或更完整的型別檢查來驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0466

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）日期計算可能因時區或 DST 造成 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的 timestamp 差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或跨越 DST 轉換，可能導致天數計算多一天或少一天，進而影響暖機限制。建議改用 UTC 日曆日差（例如將兩個日期轉為 UTC 日期字串後相減），或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0467

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）權限設定在寫入前執行，導致檔案權限錯誤

> 在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0468

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:247`，距錨點 0 行）reload_config 直接覆寫整個 ConfigMetadata 可能遺失未儲存的變更

> `reload_config` 函式直接將 `*config = load_config(...)` 的結果指派給傳入的 `&mut ConfigMetadata`。若在重新載入前有其他程式碼修改了 `config` 的某些欄位（例如透過 `merge_config_with`），這些變更會在重新載入時被覆蓋。建議先合併現有變更再重新載入，或明確區分唯讀與可變部分。

finding 片段：`pub fn reload_config( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

## P0469

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）回傳 Infinity 可能導致呼叫端未預期行為

> 當暖機天數超過 `totalDays` 時，`getWarmupLimit` 回傳 `Infinity`。若呼叫端將此值用於後續計算（例如分配郵件數量），可能產生非預期結果。建議回傳一個明確的數值（例如 `emailCount`）或定義一個特殊常數，並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0470

**GT**（func）Incorrect type conversion in generic component parameter assertion

> The test validates a generic component with an int type parameter but uses Convert.ToInt64 instead of Convert.ToInt32 to assert the parameter value. Since the parameter is defined as int (System.Int32) in GenericTestComponent<int>, this creates a type mismatch. The assertion compares a long (Int64) value to the expected int (Int32) value 42, which will cause the test to fail even though the component deserialization is working correctly. This breaks the validation logic for generic component parameters.

GT 片段：`var parameters = deserializedDescriptor.Parameters.ToDictionary(); ⏎ Assert.Single(parameters); ⏎ Assert.Contains("Value", parameters.Keys); ⏎ Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 0 行）參數值型別轉換脆弱，可能因文化特性失敗

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 long。然而，`parameters["Value"]` 的實際型別取決於反序列化過程，可能是 `JsonElement` 或其他型別。如果該值不是可直接轉換為 long 的型別（例如是 `JsonElement`），`Convert.ToInt64` 可能拋出例外或產生非預期結果。建議先確認參數值的實際型別，或使用更強健的轉換方式（例如 `Assert.IsType<JsonElement>(parameters["Value"])` 後再取得數值）。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0471

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0472

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1732`，距錨點 5 行）日誌訊息中使用了錯誤的變數名稱

> 在成功恢復的日誌中，程式使用了 `server.aof_load_broken_max_size`，但這個變數在 `server.h` 中定義為 `off_t aof_load_broken_max_size`，而日誌格式字串使用 `%lld`，並將變數強制轉型為 `long long`。這在大多數平台上可能沒問題，但嚴格來說 `off_t` 不一定是 `long long`，可能導致未定義行為或警告。

**建議**：使用 `%lld` 搭配明確的 `(long long)` 轉型，或改用 `%zu` 搭配 `size_t` 轉型。

finding 片段：`serverLog(LL_WARNING, ⏎ "AOF loaded anyway because aof-load-broken is enabled and " ⏎ "broken size '%lld' is less than aof-load-broken-max-size '%lld'", ⏎ (long long)(sb.st_size - valid_up_to), (long long)(server.aof_load_broken_max_size));`

## P0473

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:79`，距錨點 12 行）Popover 缺乏鍵盤無障礙支援

> 觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

finding 片段：`aria-label={`Show ${hiddenItems.length} more items`} ⏎ onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0474

**GT**（func）Missing type coercion for retries value causes potential type inconsistency

> The retries display removes the .toString() call that was present in the original PR, directly rendering taskRun.empirical_policy?.retries ?? "0". This creates a type inconsistency where the value could be either a number (when retries exists) or a string "0" (when it doesn't). While React can render both, this inconsistency violates the principle of uniform data handling and could cause issues in the component tree if parent or child components expect consistent string formatting for this field, or if the value is later used in string operations or comparisons.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retries</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retries ?? "0"}`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 10 行）retry_jitter_factor 為 0 時顯示 'None'

> 條件 `taskRun.empirical_policy?.retry_jitter_factor` 在值為 0 時為 falsy，因此會顯示 'None'，但 0 是有效的 jitter factor。建議改用 `typeof ... === 'number'` 或 `??` 來判斷。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## P0475

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 在 _propagate_skip_to_node 中，原本先 mark_edge_skipped 再 propagate_skip_from_edge，現在順序對調。若 propagate_skip_from_edge 內部依賴邊的 skipped 狀態（例如 analyze_edge_states 會檢查），則可能導致行為不同。需確認此變更是否為修正所需，並驗證遞迴邏輯仍正確。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0476

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）記憶體配置失敗未檢查

> `malloc` 的返回值未檢查，若配置失敗（回傳 NULL），後續寫入 `slot_buffer[j]` 會導致空指標解參考，造成程式崩潰。

**失敗情境**：在記憶體不足的環境下，`malloc` 回傳 NULL，程式將在寫入時崩潰。

**建議修法**：檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0477

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:376`，距錨點 0 行）json.dumps(subscription_plan) 可能失敗，導致快取寫入中斷

> 在 `get_plan_bulk_with_cache` 中，從 `get_plan_bulk` 取得的 `subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps` 預期可序列化的物件。若 `SubscriptionPlan` 包含非 JSON 相容的型別（例如 datetime、Decimal 等），`json.dumps` 會拋出 `TypeError`，導致整個 pipeline 執行失敗，且該例外被外層 `except` 捕捉後僅記錄日誌，不會寫入任何快取。

**失敗情境**：當 billing API 回傳的 `expiration_date` 是 ISO 格式字串而非整數時，`validate_python` 可能將其轉為 datetime 物件，此時 `json.dumps` 會失敗。

**建議**：在序列化前先將 `subscription_plan` 轉為純 dict（例如 `dict(subscription_plan)`），或使用 Pydantic 的 `model_dump()` 方法（若改用 BaseModel）。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0478

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateActionSpacing 中堆疊陣列重複加入 browserActionStack

> 在 `updateActionSpacing` 方法中，原本應包含 `trailingPageActionStack` 的陣列，卻重複加入了 `browserActionStack`，導致 `trailingPageActionStack` 未被納入動畫與間距更新。這可能造成頁面動作按鈕的動畫失效或間距不正確。

建議將第二個 `browserActionStack` 改為 `trailingPageActionStack`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0479

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0480

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0481

**GT**（rule）New/modified path resolution introduces panics/unwraps for fallible operations

> `resolve_dirs` uses `panic!` and `unwrap()` (`tauri.parent().unwrap()`) for fallible operations (project discovery/path parent resolution) instead of returning a `Result`, violating the rule to make failure explicit rather than panicking.

GT 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| { ⏎ let env_var_name = env_tauri_app_path().is_some().then(|| format!("`{ENV_TAURI_APP_PATH}`")); ⏎ panic!("Couldn't recognize the {} folder as a Tauri project. It must contain a `{}`, `{}` o`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:130`，距錨點 0 行）`resolve_dirs` 仍使用 `OnceLock` 全域快取，可能導致路徑解析錯誤

> `resolve_dirs` 內部使用 `TAURI_DIR.get_or_init` 與 `FRONTEND_DIR.get_or_init`，這兩個 `OnceLock` 是全域靜態變數。雖然函式回傳 `Dirs`，但實際上仍依賴全域狀態。若在同一個行程中，先以某個工作目錄呼叫 `resolve_dirs`，之後切換到另一個 Tauri 專案再呼叫，第二次呼叫會回傳第一次解析的結果，造成路徑錯誤。這在測試或嵌入式使用情境下特別危險。

建議：移除 `OnceLock`，改為每次呼叫都重新解析，或將 `Dirs` 的建立改為接受明確的基礎路徑參數，避免隱含的全域狀態。

finding 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| {`

## P0482

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:12`，距錨點 0 行）類別宣告的開頭大括號未換行

> 類別 `ServerComponentDeserializerTest` 的開頭大括號與類別宣告在同一行，違反 repo 規範  （Opening Braces Must Be on New Line (Allman Style)）。

建議將大括號移至下一行：
```csharp
public class ServerComponentDeserializerTest
{
```

finding 片段：`public class ServerComponentDeserializerTest ⏎ {`

## P0483

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

## P0484

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行）將 Remarks 指派給 Summary 可能改變語意

> 原本將 methodComment.Remarks 指派給 operation.Description，現在改為 operation.Summary。這可能改變 OpenAPI 文件中 remarks 的呈現位置，需確認是否符合預期。

finding 片段：`operation.Summary = remarks;`

## P0485

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）extractSlotFromKeysResult 在 cross-slot 時可能洩漏記憶體

> 在偵測到 cross-slot 時，函式會 `free(slot_buffer)` 後回傳 `CLUSTER_CROSSSLOT`，但若 `malloc` 失敗（回傳 NULL），則 `slot_buffer` 為 NULL，`free(NULL)` 是安全的，但後續的 `slot_buffer[j] = this_slot` 會對 NULL 指標寫入，造成 segmentation fault。

**失敗情境**：當記憶體不足導致 `malloc` 回傳 NULL 時，程式會崩潰。

**建議修法**：檢查 `malloc` 回傳值，若為 NULL 則回傳錯誤或改用 `zmalloc`（其會終止程式）。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0486

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行）orgId 過濾邏輯可能排除應包含的團隊

> 在 UNION 的第二部分，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})` 只檢查 org.id 或 child.id 等於 orgId，但未考慮 child.parentId 等於 orgId 的情況。這可能導致當 orgId 為父組織時，子團隊被錯誤排除。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## P0487

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:325`，距錨點 0 行）Redis mget 回傳值長度檢查可能誤判

> 在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## P0488

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）當 genericCalendarSuffixes 為空陣列時，Prisma 查詢包含 `AND: undefined`

> 在 `findNextSubscriptionBatch` 方法中，`AND` 條件被設置為 `genericCalendarSuffixes?.length ? ... : undefined`。當 `genericCalendarSuffixes` 為空陣列或未提供時，`AND` 將為 `undefined`。雖然 Prisma 通常會忽略 `undefined` 的條件，但這可能導致生成的 SQL 包含不必要的 `AND` 子句，影響查詢效能或可讀性。建議在建構 where 物件時，僅在需要時才加入 `AND` 屬性，例如使用條件展開。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0489

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:27`，距錨點 2 行）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## P0490

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）權限設定在寫入前執行，導致檔案權限錯誤

> 在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0491

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行）truncate 失敗後仍可能繼續執行

> 若 `truncate` 失敗，程式記錄警告後並未設定 `ret` 或跳轉到錯誤處理，而是繼續執行後續的 `lseek` 與 `loaded_ok` 流程，可能導致 AOF 檔案未正確截斷但伺服器仍以成功狀態載入。建議在 `truncate` 失敗時設定 `ret = AOF_FAILED` 並跳轉到 cleanup。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0492

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0493

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）版本更新不一致：metadata-v2.json 中的 cli.js 版本與 package.json 不一致

> 在 `crates/tauri-cli/metadata-v2.json` 中，`cli.js` 的版本從 `2.8.1` 更新為 `2.8.2`，但 `packages/cli/package.json` 中的版本也從 `2.8.1` 更新為 `2.8.2`。然而，`metadata-v2.json` 中的 `tauri` 欄位仍為 `2.8.2`，而 `crates/tauri/Cargo.toml` 已更新為 `2.8.3`。這可能導致 metadata 與實際版本不符。建議檢查 `metadata-v2.json` 中的 `tauri` 欄位是否應同步更新為 `2.8.3`。

finding 片段：`"version": "2.8.2",`

## P0494

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0495

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:49`，距錨點 3 行）validateCreateScheduleInput 回傳型別未嚴格驗證

> 函式回傳型別為 CreateScheduleInput，但僅透過型別斷言 (as CreateScheduleInput) 轉換，未實際驗證 schedule 與 eventTypeId 的型別。這可能導致呼叫端誤以為輸入已通過驗證，但實際上可能包含無效資料。建議使用型別守衛或 Zod schema 來確保型別安全。

finding 片段：`return data as CreateScheduleInput;`

## P0496

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行）RequestBody.Description 設定時機變更可能影響既有行為

> 原本在處理 propertyComment.Examples 之前就設定 `operation.RequestBody.Description = description`，現在移到處理 Examples 之後。若 Examples 處理過程中發生例外或提前 continue，可能導致 Description 未被設定。建議確認此變更不會造成描述遺失。

finding 片段：`operation.RequestBody.Description = description;`

## P0497

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0498

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:12`，距錨點 0 行）類別宣告縮排不一致

> 在 block-scoped namespace 內，類別宣告的縮排不一致：`public class ServerComponentDeserializerTest` 前面有 4 個空格，但後續成員的縮排似乎未相應調整。這可能導致程式碼可讀性問題。

**建議修法**：如果改回 file-scoped namespace，此問題自然解決；否則應確保所有成員縮排一致。

finding 片段：`public class ServerComponentDeserializerTest ⏎ {`

## P0499

**GT**（func）Translation inconsistency for 'Enter your name' field across UI contexts

> The PR introduces an inconsistency in the Chinese translation for the 'Enter your name' input field. In portal.json line 71, it's translated as '输入您的名字' (enter your first name), which suggests only a first name is needed. However, based on the context of Ghost's user registration and profile system, and the fact that the 'Name' field itself should be '姓名' (full name), this creates a mismatch between what the label asks for ('名字' - first name) and what the system actually expects ('姓名' - full name). This can cause user confusion during registration and profile completion, potentially leading to incomplete or incorrectly formatted name entries.

GT 片段：`"Ends {offerEndDate}": "于{offerEndDate}结束", ⏎ "Enter code above": "在上方输入验证码", ⏎ "Enter your email address": "输入您的电子邮箱地址", ⏎ "Enter your name": "输入您的名字",`

**finding**（`ghost/i18n/locales/zh/portal.json:58`，距錨點 10 行）翻譯用語可能不符合繁體中文習慣

> 將「偏好設定」改為「偏好设置」，但「设置」是簡體中文用語，繁體中文通常使用「設定」。建議維持「偏好設定」或改為「偏好設置」需確認目標受眾。

finding 片段：`"Didn't mean to do this? Manage your preferences <button>here</button>.": "操作有误？可以在<button>这里</button>修改您的偏好设置。",`

## P0500

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0501

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0502

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）extractSlotFromKeysResult 迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會多執行一次，當 `j == numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體（配置大小為 `numkeys` 個 int）。此外，`argv[keys_result->keys[j].pos]` 也會讀取超出 `keys_result->keys` 陣列範圍的記憶體。

**失敗情境**：當 `numkeys > 0` 時，最後一次迭代會造成 heap buffer overflow，可能導致程式崩潰或任意程式碼執行。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0503

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖曳的 prefix items，可能導致索引錯亂

> `sortableKeys` 使用 `localKeyedValues.map((item) => item.key)` 取得所有項目的 key，但其中包含不可拖曳的 prefix items（`canMove` 為 false）。當拖曳一般項目時，dnd-kit 的排序策略會考慮所有項目，可能導致計算出的 `over.id` 對應到 prefix item，進而使 `newIndex` 指向錯誤位置。建議只將可拖曳項目的 key 傳入 `SortableContext`，或使用 `disabled` 屬性排除 prefix items。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0504

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:350`，距錨點 15 行）快取寫入時使用了錯誤的變數 bulk_plans 而非 plans_to_cache

> 在 Step 3 的快取寫入迴圈中，程式碼遍歷的是 `bulk_plans.items()`，但 `bulk_plans` 是從 `get_plan_bulk` 回傳的完整字典，而 `plans_to_cache` 才是經過篩選、只包含需要快取的項目。這會導致即使某個 tenant 的 plan 驗證失敗（在 `get_plan_bulk` 中被設為 `None`），仍然會被寫入快取，造成快取中存有無效資料。

**失敗情境**：假設 `get_plan_bulk` 回傳 `{'tenant-1': valid_plan, 'tenant-2': None}`，則 `plans_to_cache` 只包含 `tenant-1`，但迴圈會將 `tenant-2` 也寫入快取，值為 `None`。下次讀取快取時，`json.loads('null')` 會得到 `None`，然後 `subscription_adapter.validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**建議修法**：將迴圈改為遍歷 `plans_to_cache.items()`。

finding 片段：`for tenant_id, subscription_plan in bulk_plans.items():`

## P0505

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0506

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）使用 endsWith 過濾可能誤排除合法日曆

> 目前使用 `endsWith` 來排除 externalId 結尾為特定後綴的日曆。若使用者擁有一個自訂日曆，其 externalId 恰好以這些後綴結尾（例如 `mygroup@group.calendar.google.com`），則會被錯誤排除。建議改用更精確的比對方式，例如正規表示式或直接比對完整 ID 模式，或至少確認 Google 日曆 ID 的格式保證這些後綴只出現在通用日曆中。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0507

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行）updateAccessibility 中誤用 browserActionStack 取代 trailingPageActionStack

> 在 updateAccessibility 方法中，原本應該加入 trailingPageActionStack 的 arrangedSubviews，但重構後誤改為 browserActionStack，導致 browserActionStack 的子視圖被重複加入，而 trailingPageActionStack 的子視圖未被處理。這可能造成無障礙元素重複或缺失，影響 VoiceOver 等輔助功能。

建議修正為：
```swift
let stacks = browserActionStack.arrangedSubviews +
             navigationActionStack.arrangedSubviews +
             leadingPageActionStack.arrangedSubviews +
             trailingPageActionStack.arrangedSubviews
```

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## P0508

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 18 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0509

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖身完成後回傳 Infinity 可能導致呼叫端未預期行為

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接使用此值進行數學運算或與其他數值比較，可能產生非預期結果。例如，若呼叫端將此值傳入 `Math.min` 或作為陣列索引，可能導致錯誤。建議回傳 `emailCount`（表示無限制）或定義明確的常數，並確認所有呼叫端都能正確處理。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0510

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行）使用 propertyName 取代 metadata.Name 可能影響參數匹配

> 原本使用 metadata.Name 來尋找 operation.Parameters 中的參數，現在改為 propertyName。若 metadata.Name 與 propertyName 不同，可能導致找不到參數而將描述套用到 RequestBody。需確認此變更符合預期。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0511

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 而非 logging

> 在生產程式碼中使用 `print` 違反專案規範  ，應改用 `logging` 模組。這會導致輸出不受日誌系統控制，且可能洩漏敏感資訊。建議移除該行或改用 `logger.debug`。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0512

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The new test method does not include the required '// Arrange', '// Act', and '// Assert' (or '// Act & Assert') comments to delineate phases per the AAA pattern.

GT 片段：`[Fact] ⏎ public async Task SupportsRouteParametersFromControllers() ⏎ { ⏎ var source = """`

**finding**（`src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:100`，距錨點 1 行）測試方法缺少 Arrange-Act-Assert 註解

> 新增的測試方法 SupportsRouteParametersFromControllers 未包含明確的 // Arrange、// Act、// Assert 註解，違反專案規範  。建議加入結構化註解以提升可讀性。

finding 片段：`[Fact] ⏎ public async Task SupportsRouteParametersFromControllers() ⏎ {`

## P0513

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）直接存取 process.env 判斷 webhook 是否啟用

> 在 handleCancelBooking.ts 中直接使用 `process.env.ENABLE_WEBHOOKS !== "false"` 來決定是否發送 webhook，違反  （環境變數不應在非設定程式碼中直接存取）。這會降低可測試性，且可能因環境變數未正確設定而導致行為不一致。建議將此判斷移至設定模組或透過依賴注入傳入。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0514

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 minimal 模式下的 setLoading(false) 可能導致 UI 狀態不一致

> 在 minimal 模式成功後，原本會呼叫 setLoading(false) 來關閉載入狀態，但此變更移除了該呼叫。若 loading 狀態未在其他地方重設，可能導致按鈕持續顯示載入中。建議確認 loading 狀態的生命週期，或保留此呼叫。

finding 片段：`setSuccess(true);`

## P0515

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行）run_count 使用 `||` 可能錯誤處理 falsy 值

> `taskRun.run_count || 0` 會將 0、空字串、NaN 等 falsy 值都顯示為 0。若 run_count 可能為空字串或 null，顯示 0 可能誤導使用者。建議改用 `taskRun.run_count ?? 0` 或明確檢查 null/undefined。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## P0516

**GT**（rule）Unused import in new component

> The rule requires that all staged files pass 'biome lint --error-on-warnings' before commit. The code imports 'useEffect' from React but never uses it, which triggers a linting warning that should have been caught and fixed by the pre-commit hook.

GT 片段：`import useMediaQuery from "@calcom/lib/hooks/useMediaQuery"; ⏎ import { Badge } from "@calcom/ui/components/badge"; ⏎ import { Button } from "@calcom/ui/components/button"; ⏎ import { Popover, PopoverContent, PopoverTrigger } from "@calcom/ui/components/popover";`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:42`，距錨點 35 行）items 陣列在 useMemo 依賴中可能導致不必要的重新計算

> useMemo 的依賴陣列包含 items，但 items 是從 props 傳入的陣列。如果父元件每次 render 都建立新的陣列（例如在 UserListTable 中使用 map 產生），則 useMemo 會失效，導致每次 render 都重新 slice。這可能造成效能影響，尤其是在大型表格中。建議使用 useMemo 時考慮 items 的參考穩定性，或使用 useRef 保存上一次的 items 並進行淺比較。

finding 片段：`const { visibleItems, hiddenItems } = useMemo( ⏎ () => ({ ⏎ visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0517

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）屬性 badge 合併權重與群組標記，可能影響可讀性

> 原本權重以獨立 badge 顯示，現在合併到 label 中，例如 'Value 80% (group)'，可能讓使用者難以快速區分權重與群組狀態。建議保留分離的 badge 或使用更明確的視覺區分。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0518

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這會導致同一事件在不同 webhook 版本中收到不同的預設值，可能造成下游系統誤判。建議統一預設值，或明確在 DTO 中必填此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0519

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）sortableKeys 未使用 useMemo，可能導致不必要的重新渲染

> `sortableKeys` 在每次 render 時重新建立陣列，若 `localKeyedValues` 未變，仍會產生新陣列參考，可能觸發 `SortableContext` 的重新渲染。建議使用 `useMemo` 包裹。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0520

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）skeleton address bar 的 leading 約束可能誤接至 rightSkeletonAddressBar

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)` 被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 錯誤地對齊到右側 skeleton bar 的 trailing，造成佈局錯亂。

請確認此變更是否為預期；若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0521

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）屬性 badge 合併權重與群組標記可能降低可讀性

> 原本權重以獨立 badge 顯示，群組以橘色 badge 區分，現在合併為單一 label（例如 "Value 80% (group)"），可能讓使用者難以快速區分。建議保留視覺區分，或提供 tooltip 說明。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0522

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1115`，距錨點 0 行）extractSlotFromKeysResult 中 free 位置不當導致記憶體洩漏

> 在 cross-slot 偵測到時，函式會 `free(slot_buffer)` 並回傳 `CLUSTER_CROSSSLOT`，但若迴圈正常結束，`free(slot_buffer)` 在迴圈外執行，這部分正確。然而，若在迴圈中發生 cross-slot，`free` 後直接回傳，但 `slot_buffer` 可能包含未初始化的值（若 `malloc` 成功但迴圈未完全填滿），但這不影響 free。真正的問題是：若 `malloc` 失敗（未檢查），則 `slot_buffer` 為 NULL，後續寫入會 crash。建議在 malloc 失敗時直接回傳 `INVALID_CLUSTER_SLOT`，並確保所有路徑都釋放記憶體。

finding 片段：`free(slot_buffer); ⏎ return CLUSTER_CROSSSLOT;`

## P0523

**GT**（func）Incorrect sequence validation for multiple generic components

> The test validates deserialization of multiple closed generic components but checks that both descriptors have sequence number 0 instead of verifying that the second descriptor has sequence number 1. Component descriptors in a collection must have sequential ordering starting from 0, and this test should verify the second component has sequence 1. This incorrect assertion fails to validate proper sequence ordering, which is critical for component initialization and rendering order in Blazor.

GT 片段：`var secondDescriptor = descriptors[1]; ⏎ Assert.Equal(typeof(GenericTestComponent<string>).FullName, secondDescriptor.ComponentType.FullName); ⏎ Assert.Equal(0, secondDescriptor.Sequence);`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 18 行）參數值型別轉換脆弱，可能因文化特性失敗

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 long。然而，`parameters["Value"]` 的實際型別取決於反序列化過程，可能是 `JsonElement` 或其他型別。如果該值不是可直接轉換為 long 的型別（例如是 `JsonElement`），`Convert.ToInt64` 可能拋出例外或產生非預期結果。建議先確認參數值的實際型別，或使用更強健的轉換方式（例如 `Assert.IsType<JsonElement>(parameters["Value"])` 後再取得數值）。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0524

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試中使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，元件是以 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同（例如 `GenericComponent`1[[System.Int32]]` vs `GenericComponent`1[[System.String]]`）。建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0525

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）使用 expect 可能導致 panic

> 在 write_and_make_executable 中，使用 fs::set_permissions 和 fs::write 並以 map_err 處理錯誤，但沒有使用 expect 或 unwrap。然而，函式簽名回傳 Result<(), FileWriteError>，但內部可能因為其他原因 panic？實際上沒有直接使用 expect，但建議確認所有可能的錯誤都被妥善處理。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0526

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0527

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）slot 可能未初始化即被使用

> 在 `extractKeysAndSlot` 中，原本 `*slot` 會先被設為 `INVALID_CLUSTER_SLOT`，但修改後只有當 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 `*slot`。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能導致未初始化變數被使用。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT`，或確保所有呼叫者都已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0528

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯變更可能不符合繁體中文習慣

> 將「新聞信」改為「邮件通讯」等用語，可能不符合繁體中文使用者的習慣。建議確認目標受眾，若為繁體中文使用者，應保留原有用語。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。"`

## P0529

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0530

**GT**（func）Missing error logging in TanStack devtools lazy import

> The TanStackDevtoolsLoader silently swallows import errors without logging them, making it impossible to debug why the devtools fail to load. This creates an inconsistent error handling pattern compared to the ReactScanLoader (in the same PR), which properly logs errors with console.error before returning a fallback component. When developers encounter issues with TanStack devtools not appearing, they will have no visibility into whether it's due to an import failure, missing dependencies, or other issues.

GT 片段：`const TanStackDevtoolsWrapper = lazy(() => ⏎ import('./devtools').then(module => ({ ⏎ default: module.TanStackDevtoolsWrapper, ⏎ })).catch(() => {`

**finding**（`web/app/components/devtools/tanstack/loader.tsx:10`，距錨點 0 行）TanStack Devtools 載入失敗時完全吞掉錯誤，無任何 log

> 在 `lazy` 的 `catch` 中，僅回傳 `{ default: () => null }`，沒有記錄任何錯誤。這使得動態載入失敗時完全無法追蹤，不利於除錯。建議至少加入 `console.error` 記錄錯誤，或使用其他 logging 機制。

finding 片段：`return { default: () => null }`

## P0531

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）使用 malloc/free 而非 zmalloc/zfree

> 新增的 `malloc` 與 `free` 呼叫違反專案規範  ，應使用 `zmalloc` 與 `zfree` 以利記憶體追蹤。

**建議修法**：將 `malloc` 改為 `zmalloc`，`free` 改為 `zfree`。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0532

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0533

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行）新增的 v147 結構體可能未被使用

> 在 `String` 擴展中新增了 `struct v147`，其中包含原本屬於 `InactiveTabs` 的本地化字串。但這些字串在程式碼中已不再被引用（因為相關視圖已刪除），可能成為死代碼。若確認不再需要，應一併移除；若仍需要保留以供未來使用，建議加上註解說明。

finding 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString(`

## P0534

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 原本的驗證條件為 `if (value <= 0)`，會拒絕 0 或負數。變更後為 `if (value < 0)`，允許 0 值。但屬性文件說明為「strictly positive value」，且錯誤訊息仍為「must be positive」，因此允許 0 可能違反設計意圖。若設定為 0，可能導致保留檔案數為 0，造成所有日誌檔案被刪除或無法保留任何檔案。建議確認此變更是否為預期，若非預期應改回 `<= 0`。

finding 片段：`if (value < 0)`

## P0535

**GT**（rule）Single underscore include guard used

> The rule requires header files to use include guards with double underscores at the start (e.g., __FILENAME_H), but the code uses a single underscore prefix instead (_REDIS_H)

GT 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

**finding**（`src/server.h:15`，距錨點 0 行）變更 include guard 巨集名稱可能影響外部程式碼

> 將 `__REDIS_H` 改為 `_REDIS_H` 可能導致與其他使用相同 guard 的程式碼衝突，或破壞依賴舊巨集名稱的條件編譯。雖然影響不大，但建議確認此變更的必要性。

finding 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

## P0536

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 0 行）狀態欄位名稱依 posture 切換可能導致資料遺失

> 當 posture 從 Reactive 切換到 Proactive 時，欄位名稱從 `trigger.expect` 改為 `trigger.after`，但原本在 `trigger.expect` 中的值不會自動轉移到 `trigger.after`，可能導致使用者已選擇的狀態遺失。建議在切換時同步值或使用相同欄位名稱。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0537

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:66`，距錨點 11 行）方法開頭括號未換行，違反 Allman 風格

> `TryGetValidatableParameterInfo` 方法的開頭括號從新行移至與方法簽名同一行，違反專案規範  （Opening Braces Must Be on New Line）。建議將 `{` 移至下一行。

finding 片段：`public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) {`

## P0538

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0539

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）新增 console.log 違反前端禁止 console 語句規範

> 在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，違反   規範。應移除或改用適當的 logging 機制。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0540

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12`，距錨點 17 行）Storybook 全域 QueryClient 可能導致測試間狀態污染

> `queryClient` 在模組頂層建立，且 `createTestRouter` 內部又建立新的 `QueryClient` 但未使用。全域 `queryClient` 會被所有 story 共用，若某個 story 的快取資料被修改，可能影響其他 story 的渲染結果，導致測試不穩定。建議在每個 decorator 中建立新的 `QueryClient`，或使用 `QueryClientProvider` 的 `key` prop 強制重新掛載。

finding 片段：`const queryClient = new QueryClient({ ⏎ defaultOptions: { ⏎ queries: { ⏎ retry: false,`

## P0541

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 未釋放

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0542

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）toolbar.leadingAnchor 約束對象可能錯誤

> 在 setupToolbarLayout 中，原本 toolbar.leadingAnchor 是與 leftSkeletonAddressBar.trailingAnchor 對齊，但重構後改為與 rightSkeletonAddressBar.trailingAnchor 對齊。這可能導致工具欄在骨架畫面期間位置錯誤，特別是在滑動分頁時。

建議確認此變更是否為預期行為，若不是，應改回 leftSkeletonAddressBar.trailingAnchor。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0543

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行）get_plan_bulk 將無效租戶設為 None，可能導致下游型別錯誤

> 在 `get_plan_bulk` 中，當 `validate_python` 失敗時，程式碼將 `results[tenant_id]` 設為 `None`。但函式的回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（例如 `get_plan_bulk_with_cache`）預期每個值都是 `SubscriptionPlan`。若下游程式碼直接存取 `result[tenant_id]['plan']`，會遇到 `TypeError: 'NoneType' object is not subscriptable`。

**失敗情境**：當某個租戶的 billing API 回傳格式錯誤時，該租戶在結果中為 `None`，而呼叫端未檢查 `None` 就使用，導致執行時期錯誤。

**建議**：不要將無效租戶放入結果字典，或將回傳型別改為 `dict[str, SubscriptionPlan | None]` 並要求呼叫端處理 `None`。

finding 片段：`results[tenant_id] = None`

## P0544

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）extractKeysAndSlot 中 slot 未初始化可能導致未定義行為

> 在 `extractKeysAndSlot` 中，原本 `*slot = INVALID_CLUSTER_SLOT;` 被移除，改為僅在 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 slot。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能未初始化，導致未定義行為。建議保留 `*slot = INVALID_CLUSTER_SLOT;` 的初始化，或確保所有呼叫者都先初始化 slot。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0545

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行）直接使用 ureq::get 可能未套用平台憑證設定

> 在 `download_webview2_offline_installer` 中，直接呼叫 `ureq::get(url)` 而非使用 `base_ureq_agent()`，這可能導致此請求未使用系統憑證，與 PR 目的不一致。建議改用 `base_ureq_agent().get(url)` 以確保一致性。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## P0546

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:376`，距錨點 0 行）json.dumps 無法序列化 SubscriptionPlan (TypedDict)

> 在 `get_plan_bulk_with_cache` 中，`subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps(subscription_plan)` 會嘗試直接序列化該物件。TypedDict 在執行時是普通的 dict，但此處的 `subscription_plan` 是從 `subscription_adapter.validate_python(plan_dict)` 回傳的，其型別為 `SubscriptionPlan`，實際上是一個 dict，因此 `json.dumps` 應該可以正常運作。然而，如果 `validate_python` 回傳的物件不是純 dict（例如是 Pydantic model 或其他自訂型別），則會拋出 `TypeError`。建議先將 `subscription_plan` 轉換為 dict 再序列化，例如 `json.dumps(dict(subscription_plan))`。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0547

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）使用 propertyName 取代 metadata.Name 可能影響參數比對

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 可能不同（例如 metadata 名稱經過轉換），此變更可能導致找不到對應的 operation parameter，進而將描述套用到 RequestBody 而非參數。建議確認兩者在此情境下是否恆等。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0548

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:49`，距錨點 0 行）validateCreateScheduleInput 回傳型別未嚴格驗證

> 函式回傳型別為 CreateScheduleInput，但僅透過型別斷言 (as CreateScheduleInput) 轉換，未實際驗證 schedule 與 eventTypeId 的型別。這可能導致呼叫端誤以為輸入已通過驗證，但實際上可能包含無效資料。建議使用型別守衛或 Zod schema 來確保型別安全。

finding 片段：`return data as CreateScheduleInput;`

## P0549

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 19 行）start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致

> 在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0550

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行）新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用

> 檔案中定義的 Schedule 型別未加上 export，但後續的 CreateScheduleHandlerReturn 等型別使用了它。若其他檔案需要直接使用 Schedule，將無法匯入。建議將 Schedule 加上 export，或確認其僅供內部使用。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0551

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0552

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 回傳型別可能包含 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但現在直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，則此函式可能回傳 undefined，與宣告的回傳型別 URLHistory 不符。請確認呼叫端是否能處理 undefined，或調整型別定義。

finding 片段：`return history;`

## P0553

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0554

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）數字輸入使用 parseInt 而非 Number，可能導致非預期結果

> 在 `work-pool-status-trigger-fields.tsx` 中，Threshold 欄位的 `onChange` 使用 `parseInt(e.target.value)`，而其他元件（如 `custom-trigger-fields.tsx`、`deployment-status-trigger-fields.tsx`、`work-queue-status-trigger-fields.tsx`）使用 `Number(e.target.value)`。`parseInt` 會解析字串直到遇到非數字字元，例如輸入 "10abc" 會得到 10，而 `Number` 會得到 NaN。這可能導致使用者輸入無效值時，表單狀態不一致。建議統一使用 `Number`，並考慮加入驗證。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0555

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）條件判斷變更可能影響無 key 命令的處理

> 原本的條件 `num_keys > 0` 改為 `num_keys >= 0`，這使得 `num_keys == 0` 的命令也會進入此分支。雖然目前僅在 `pcmd->slot == CLUSTER_CROSSSLOT` 時執行操作，但若未來在此分支新增其他邏輯，可能會影響無 key 命令。此外，`num_keys == 0` 時 `pcmd->slot` 可能為 `INVALID_CLUSTER_SLOT`，不會觸發 cross-slot 處理，但條件變更本身可能隱含意圖改變。

**建議**：確認此變更是否必要，若僅為處理 cross-slot，可保留 `num_keys > 0` 並在內部檢查 `pcmd->slot == CLUSTER_CROSSSLOT`。

finding 片段：`} else if (num_keys >= 0) {`

## P0556

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行）新增的 `v147` 結構未標記為 `public`，且可能包含無效的本地化鍵

> 此 PR 刪除了 `String.TabsTray.InactiveTabs` 中的本地化字串，但在 `String.TabsTray` 下新增了一個 `v147` 結構，內容與被刪除的字串完全相同。然而，該結構沒有 `public` 修飾詞，且其名稱 `v147` 似乎只是版本標記，並非有意義的命名空間。這可能導致其他模組無法存取這些字串，且若這些鍵已不再使用，保留它們會造成混淆。

**失敗情境**：若有其他程式碼嘗試透過 `String.TabsTray.v147.TabsTrayInactiveTabsSectionClosedAccessibilityTitle` 存取，會因為 `v147` 不是 `public` 而編譯失敗。

**建議修法**：確認這些字串是否仍被使用。若已不再使用，應完全刪除；若仍需保留，應將其放在適當的 `public` 結構中，並使用有意義的名稱。

finding 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

## P0557

**GT**（rule）Unused import: Skeleton

> `Skeleton` is imported but never used in this file, which violates the rule requiring unused imports to be removed.

GT 片段：`import { Skeleton } from "@/components/ui/skeleton";`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:6`，距錨點 0 行）未使用的匯入：Skeleton

> 檔案中匯入了 `Skeleton` 元件，但在程式碼中並未使用。這可能違反  （未使用的匯入應自動移除），並增加 bundle 大小。建議移除未使用的匯入。

finding 片段：`import { Skeleton } from "@/components/ui/skeleton";`

## P0558

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）truncate 後未更新 AOF 檔案大小相關的狀態

> truncate 成功後，程式僅將檔案描述子 seek 到結尾，但未更新 server 中可能記錄的 AOF 檔案大小或 offset 等狀態。這可能導致後續 AOF 寫入時發生錯誤或覆蓋。建議檢查是否有相關狀態需要更新。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0559

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行）RequestBody.Description 設定位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在 if 區塊開頭，現在移到範例處理之後。若 `propertyComment.Examples` 存在但 `content` 為 null，會執行 `continue`，導致 `Description` 不會被設定。建議確認此情境是否會發生，或將 Description 設定保持在區塊開頭。

finding 片段：`operation.RequestBody.Description = description;`

## P0560

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 18 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}> ⏎ <Badge variant="gray">+{hiddenItems.length}</Badge> ⏎ </Button>`

## P0561

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行）run_count 顯示邏輯可能將 0 顯示為 0，但原本可能顯示 '0'

> 原本的程式碼在 `run_count` 不為 null/undefined 時顯示其值，否則不顯示。新程式碼改為 `{taskRun.run_count || 0}`，這會將 `run_count` 為 0 或 null/undefined 時都顯示為 0。若 `run_count` 為 0，原本會顯示 0，新程式碼也顯示 0，差異不大；但若 `run_count` 為 null，原本不顯示，新程式碼顯示 0，可能造成誤導。建議改為 `{taskRun.run_count ?? 'None'}` 以維持一致性。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## P0562

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:27`，距錨點 0 行）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## P0563

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0564

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0565

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`
