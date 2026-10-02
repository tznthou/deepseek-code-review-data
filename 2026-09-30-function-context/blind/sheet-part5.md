# 盲標單 5：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part5.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0401

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫，可能影響依賴它的服務初始化順序

> 原本 `await emailAddressService.init()` 是同步等待完成後才進行後續的 Promise.all，現在改成在 Promise.all 內與其他服務並行初始化。如果其他服務（如 newsletter service 或 email service）依賴 emailAddressService 初始化完成，可能會因為並行執行而產生競態條件。建議確認這些服務的依賴關係，若有必要，應保留 emailAddressService.init() 的 await 順序，或將依賴它的服務也放入同一個 Promise.all 中並確保順序。

finding 片段：`emailAddressService.init(),`

## P0402

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 0 行）使用 `deployment_id` 而非 `deployment.id` 可能導致型別不一致

> 原本傳遞 `deployment.id`，現在改為 `deployment_id`。需確認 `deployment_id` 的型別與 `create_flow_run_from_deployment` 預期的參數型別一致。如果 `deployment_id` 是字串而函式預期 UUID 物件，可能導致型別錯誤。

finding 片段：`deployment_id,`

## P0403

**GT**（rule）Test method missing test prefix

> The rule requires test methods to start with 'test' prefix, but the method 'verifyBookmarksShareNormalWebsiteReminders' does not follow this naming convention

GT 片段：`// https://mozilla.testrail.io/index.php?/cases/view/2864380 ⏎ func verifyBookmarksShareNormalWebsiteReminders() { ⏎ app.launch() ⏎ if #available(iOS 17, *) {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47`，距錨點 0 行）測試方法改名後可能不再被 XCTest 執行

> 將 `testBookmarksShareNormalWebsiteReminders` 改名為 `verifyBookmarksShareNormalWebsiteReminders`。XCTest 只會自動執行以 `test` 開頭的方法，因此改名後此測試將不再被包含在測試套件中，除非有另外透過 `testInvocations` 或 `allTests` 手動註冊。若此測試仍應執行，請保留 `test` 前綴；若刻意停用，建議改用 `XCTSkip` 或註解說明原因。

finding 片段：`func verifyBookmarksShareNormalWebsiteReminders() {`

## P0404

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 0 行）移除 noTimestamp 選項可能導致 token 包含 iat 欄位

> 原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免在 payload 中加入 `iat`（issued at）欄位，現在移除了該選項，因此產生的 token 會包含 `iat`。這可能影響 token 的驗證邏輯或與其他系統的相容性，但通常不會造成直接問題。若無特定理由，建議保留 `noTimestamp: true` 以維持原有行為。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0405

**GT**（func）Race condition: semaphore initialized after clients during startup

> The `_startup_event_semaphore` is initialized after the orchestration and events clients are created and started. This creates a race condition where Kubernetes pods detected during the client startup phase can trigger `_replicate_pod_event` calls before the semaphore exists. When `event_type` is `None` (startup scenario), the code checks `if _startup_event_semaphore is None` and raises a RuntimeError. However, pods may be detected immediately after clients start but before the semaphore initialization completes, causing the observer to crash with 'Startup event semaphore not initialized' errors during high pod count scenarios.

GT 片段：`@kopf.on.startup() ⏎ async def initialize_clients(logger: kopf.Logger, **kwargs: Any): ⏎ logger.info("Initializing clients") ⏎ global events_client`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:63`，距錨點 0 行）semaphore 初始化失敗可能導致 observer 啟動失敗

> 在 `initialize_clients` 中，如果 `settings.observer.startup_event_concurrency` 的值無效（例如小於 1），`asyncio.Semaphore` 會拋出 `ValueError`，導致 observer 啟動失敗。建議在建立 semaphore 前驗證設定值，或提供 fallback 值。

finding 片段：`_startup_event_semaphore = asyncio.Semaphore( ⏎ settings.observer.startup_event_concurrency ⏎ )`

## P0406

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:264`，距錨點 0 行）member 可能為 null 時 editor.setEditable 判斷有誤

> 原本的判斷是 `!!memberName && progress !== 'sending'`，現在改為 `!!member?.expertise && progress !== 'sending'`。如果 `member` 為 null，`member?.expertise` 會是 undefined，導致 `!!undefined` 為 false，編輯器會被設為不可編輯。但若使用者未登入（member 為 null），回覆表單可能仍應允許輸入（例如匿名回覆）。請確認此情境下的預期行為，並考慮使用 `member?.expertise != null` 或調整條件。

finding 片段：`editor.setEditable(!!member?.expertise && progress !== 'sending');`

## P0407

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 24 行）取得 identifier 的欄位從 "identifier" 改為 "bundle"，可能導致行為錯誤

> 原本從 config 物件中取得 "identifier" 欄位，現在改為取得 "bundle" 欄位。但 "bundle" 通常是一個物件，而非字串，因此 `as_str()` 會回傳 `None`，導致 `original_identifier` 永遠為 `None`。這可能影響後續依賴此值的邏輯（例如合併設定或驗證）。請確認此變更是否為預期，若不是，應改回 "identifier"。

finding 片段：`.and_then(|config| config.get("bundle"))`

## P0408

**GT**（func）Audit trail captures wrong previous status for rejected recurring bookings

> When rejecting recurring bookings, the system queries the booking status AFTER updating them to REJECTED rather than BEFORE. This causes the audit trail to incorrectly show the previous status as REJECTED instead of PENDING. The bug occurs because updatedRecurringBookings is queried after the updateMany operation completes, so all bookings already have status REJECTED. This results in audit logs showing nonsensical transitions like REJECTED→REJECTED, breaking the audit trail and making it impossible to determine the actual state change that occurred during rejection.

GT 片段：`const updatedRecurringBookings = await prisma.booking.findMany({ ⏎ where: { ⏎ uid: { ⏎ in: unconfirmedRecurringBookings.map((booking) => booking.uid),`

**finding**（`packages/trpc/server/routers/viewer/bookings/confirm.handler.ts:432`，距錨點 0 行）recurring 拒絕時 rejectedBookings 的 oldStatus 取自更新後的狀態

> 在 recurring 拒絕流程中，先執行 `prisma.booking.updateMany` 將狀態改為 REJECTED，然後再查詢這些預約並將 `oldStatus` 設為查詢到的 `status`（此時已是 REJECTED）。這會使 audit log 中的 `oldStatus` 錯誤地顯示為 REJECTED，而非原本的 PENDING。

建議在更新前先取得原始狀態，或直接使用已知的 PENDING（因為查詢條件已限定 `status: BookingStatus.PENDING`）。

finding 片段：`const updatedRecurringBookings = await prisma.booking.findMany({ ⏎ where: { ⏎ uid: { ⏎ in: unconfirmedRecurringBookings.map((booking) => booking.uid),`

## P0409

**GT**（func）Unnecessary re-rendering on every parameter update with same display name

> The DisplayName component removed the check that prevents re-rendering when the display name hasn't changed (line 50-51). This means that every time SetParametersAsync is called with a changed expression (even if it results in the same display name), the component will trigger a render. This causes performance degradation in scenarios with frequent parameter updates, such as forms with dynamic field expressions, leading to unnecessary DOM updates and potential flickering in the UI.

GT 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ _displayName = newDisplayName;`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:39`，距錨點 7 行）For 參數為 null 時拋出例外，可能導致頁面中斷

> 當 `For` 參數未提供時，元件會拋出 `InvalidOperationException`。這可能導致整個頁面渲染失敗，而不是僅顯示空白或預設內容。雖然測試中預期此行為，但對於生產應用程式，更友善的做法是記錄警告並渲染空內容，或提供預設顯示名稱。

**失敗情境**：開發者忘記設定 `For` 參數，頁面直接崩潰。

**建議**：考慮改為記錄警告並渲染空字串，或提供可設定的預設值。

finding 片段：`if (For is null) ⏎ { ⏎ throw new InvalidOperationException($"{GetType()} requires a value for the " + ⏎ $"{nameof(For)} parameter.");`

## P0410

**GT**（func）Experimental V2 UI enabled by default

> The default value for v2_enabled is set to True, making the experimental V2 UI the default instead of the stable V1 UI. This is problematic because the PR description indicates V2 is experimental and should be opt-in. Users who upgrade will unexpectedly get the experimental UI by default, potentially encountering bugs, incomplete features, or breaking changes. The setting should default to False to maintain backward compatibility and allow users to explicitly opt into the experimental V2 UI.

GT 片段：`v2_enabled: bool = Field( ⏎ default=True, ⏎ description="Whether to serve the experimental V2 UI instead of the default V1 UI.", ⏎ )`

**finding**（`src/prefect/settings/models/server/ui.py:22`，距錨點 0 行）V2 UI 預設啟用可能導致未預期的行為變更

> 新增的 `v2_enabled` 設定預設為 `True`，這表示所有現有使用者升級後將預設使用實驗性的 V2 UI。若 V2 UI 尚未完全穩定或與現有功能不相容，可能造成使用者困擾。

**建議修法**：考慮將預設值設為 `False`，或提供明確的遷移指引。

finding 片段：`v2_enabled: bool = Field( ⏎ default=True, ⏎ description="Whether to serve the experimental V2 UI instead of the default V1 UI.", ⏎ )`

## P0411

**GT**（rule）Interface used instead of type

> The rule requires using 'type' keyword for type declarations, but the code uses 'interface' declaration instead

GT 片段：`interface TranslationMap extends Record<string, string | string[]> {}`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 6 行）缺少輔助函式的單元測試

> 新增的 `createTFunction`、`createUseTranslationMock`、`createTransMock` 等函式沒有對應的測試。建議補上單元測試，確保其行為符合預期，特別是參數處理和 fallback 邏輯。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0412

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行）notarize_inner 中 wait 參數的邏輯可能反轉

> 原本 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 在 `wait` 為 false 時，若 status 為 None 會進入成功分支；改為 `map_or(wait, ...)` 後，`wait` 為 false 且 status 為 None 時會進入失敗分支。這可能導致非等待模式下，若 notarytool 未回傳 status（例如剛提交尚未有狀態），程式會誤判為失敗。請確認此變更是否為預期行為。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## P0413

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:509`，距錨點 40 行）`source_static_path` 可能未定義導致 `NameError`

> `source_static_path` 在 `if v2_enabled` 為假時未被賦值，但此處直接使用 `str(source_static_path)`。若 `v2_enabled` 為假，將拋出 `NameError`。

**失敗情境**：使用 V1 UI 時，伺服器啟動即失敗。

**建議修法**：在條件判斷前先定義 `source_static_path` 的預設值，或將此邏輯移入對應分支。

finding 片段：`copy_directory(str(source_static_path), str(static_dir))`

## P0414

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2310`，距錨點 0 行）使用 shared.fields 與 shared.integers[1] 作為 HPEXPIREAT 參數，但未確認其初始化狀態

> shared.fields 在 createSharedObjects 中初始化，但 shared.integers[1] 是否已初始化需確認。若未初始化，可能導致傳播錯誤的指令。

失敗情境：若 shared.integers[1] 未正確初始化，傳播的 HPEXPIREAT 指令可能包含錯誤的參數。

建議修正：確認 shared.integers[1] 在 createSharedObjects 中已正確初始化，或改用其他方式建立整數物件。

finding 片段：`argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1];`

## P0415

**GT**（func）Memory leak due to missing error message reply to client

> In parseSlotRangesOrReply, when slot range validation fails, the error message allocated by slotRangeArrayNormalizeAndValidate is freed with sdsfree(err) but never sent to the client via addReplyErrorSds. This causes two problems: the client receives no error message explaining why their command failed, making debugging difficult, and it breaks the expected behavior where addReplyErrorSds transfers ownership of the sds string. The original PR intended to always send validation errors to the client for proper error reporting.

GT 片段：`sds err = NULL; ⏎ if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots);`

**finding**（`src/cluster.c:2015`，距錨點 0 行）parseSlotRangesOrReply 中錯誤訊息釋放方式變更可能造成記憶體洩漏

> 在 `parseSlotRangesOrReply` 中，原本在驗證失敗時使用 `addReplyErrorSds(c, err)` 將錯誤訊息傳給客戶端，該函式會負責釋放 `err`。現在改為 `sdsfree(err)` 後直接回傳 NULL，但沒有將錯誤訊息回覆給客戶端。這可能導致客戶端收到不明確的錯誤（例如只有 generic error），且若 `err` 為 NULL 時呼叫 `sdsfree` 可能不安全。

具體情境：
- 當 `slotRangeArrayNormalizeAndValidate` 回傳錯誤並設定 `err`，程式會釋放 `err` 但沒有回覆客戶端，客戶端可能只看到 generic error，難以除錯。
- 若 `err` 為 NULL（例如某些錯誤路徑未設定），`sdsfree(NULL)` 可能導致 crash（取決於實作）。

建議：保留 `addReplyErrorSds` 或明確回覆錯誤訊息，並確保 `err` 不為 NULL 再釋放。

finding 片段：`if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots); ⏎ return NULL;`

## P0416

**GT**（func）Incorrect Reader Mode URL handling in cancelEditMode

> The cancelEditMode function now incorrectly preserves reader mode URLs when canceling edit mode. The logic was changed from '&&' (AND) to '||' (OR), which means reader mode URLs will now be kept instead of being cleared. This breaks the expected behavior where reader mode URLs should be filtered out when canceling URL editing, potentially causing the address bar to display internal reader:// URLs to users instead of the original webpage URL.

GT 片段：`@MainActor ⏎ private func cancelEditMode(windowUUID: WindowUUID) { ⏎ var url = tabManager(for: windowUUID).selectedTab?.url ⏎ if let currentURL = url {`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485`，距錨點 0 行）cancelEditMode 條件變更可能導致非網頁 URL 被保留

> 原本條件為 `currentURL.isWebPage() && !currentURL.isReaderModeURL`，現在改為 `currentURL.isWebPage() || currentURL.isReaderModeURL`。這會讓非網頁但為閱讀模式 URL 的網址在取消編輯時被保留，可能導致網址列顯示不正確的內容。請確認此變更是否為移除 QR code 時的必要調整，若非必要請還原。

finding 片段：`url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`

## P0417

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:102`，距錨點 0 行）移除 source 過濾條件可能破壞既有 API 行為

> 原本 `options.source` 會被加入 tinybirdOptions（即使為空字串），但此 PR 刪除了該區塊。若前端或其他服務依賴 `source` 參數來過濾流量來源，升級後這些請求將不再帶有 `source` 參數，導致回傳未過濾的資料。請確認是否有其他呼叫端仍傳遞 `source`，並評估是否應保留此參數的傳遞。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## P0418

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行）scheduling.init() 移除了 apiUrl 參數，可能導致排程服務無法正確建構 API URL

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入了動態產生的 API URL，現在改成無參數呼叫。如果 scheduling 服務內部需要這個 URL 來進行 API 呼叫，移除後可能導致功能失效或使用錯誤的 URL。建議確認 scheduling.init() 的實作是否已改為自行取得 URL，或是否應保留此參數。

finding 片段：`scheduling.init(),`

## P0419

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 0 行）gtk 腳本存在時仍會覆寫，可能導致非預期更新

> 原本的邏輯是當 `gtk` 檔案不存在時才下載並寫入，但此 PR 改為當檔案存在時仍使用 `include_bytes!` 的內容覆寫。這可能導致使用者自訂的腳本被覆蓋，或造成不必要的寫入。

建議保留原本的 `if !gtk.exists()` 條件，或明確說明覆寫意圖。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0420

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行）回傳 `Infinity` 可能造成下游型別或比較問題

> 當暖機完成後，`getWarmupLimit` 回傳 `Infinity`。這可能導致下游程式碼在進行數值比較或計算時出現非預期行為，例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若下游直接使用該值進行算術運算，可能產生 `Infinity` 或 `NaN`。

**建議修法**：
回傳 `emailCount` 本身，或使用一個明確的哨兵值（例如 `Number.MAX_SAFE_INTEGER`），並在文件或型別中說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0421

**GT**（func）Missing error source for Plist variant breaks error chain

> The Error::source() implementation is missing a case for Error::Plist, which wraps a plist::Error. This breaks error chain propagation when plist parsing or writing fails. The Plist variant is used for reading and writing application configuration files and provisioning profiles, making it one of the most commonly encountered errors. Without proper error source propagation, debugging tools and error context mechanisms lose access to the underlying plist parsing errors, making it difficult to diagnose configuration file issues.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:64`，距錨點 16 行）Display 實作與原本 thiserror 格式不完全一致

> 原本 `thiserror` 的 `#[error("{context} {path}: {error}")]` 會直接使用 `path` 的 Display，但手動實作改為 `path.display()`，兩者輸出可能不同（例如 `PathBuf` 的 Display 與 `path.display()` 通常相同，但若 path 包含非 UTF-8 字元，`display()` 會使用替代字元）。建議確認是否可接受。

finding 片段：`Error::Plist { context, path, error } => write!(f, "{} {}: {}", context, path.display(), error),`

## P0422

**GT**（func）Lost `this` context in displayGuests mapping causes runtime error

> In the `getOutputBooking` method at line 171, the code passes `this.getDisplayEmail` directly to the `map` function without binding the `this` context. This causes a runtime error because when `getDisplayEmail` is invoked inside the `map` callback, `this` will be `undefined`, resulting in "Cannot read property 'replace' of undefined" or similar errors. The arrow function `(guest: string) => this.getDisplayEmail(guest)` was removed, which was necessary to preserve the `this` binding. This will break all bookings that have guests.

GT 片段：`if ( ⏎ bookingTransformed.bookingFieldsResponses?.guests && ⏎ Array.isArray(bookingTransformed.bookingFieldsResponses.guests) ⏎ ) {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:165`，距錨點 0 行）displayGuests 的 map 回呼可能遺失 this 綁定

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail);` 直接傳遞 `this.getDisplayEmail` 作為回呼，但 `getDisplayEmail` 是實例方法，若其內部依賴 `this`（目前沒有），未來修改可能導致錯誤。此外，在其他方法中使用了箭頭函式包裝，此處不一致。

**建議**：統一使用箭頭函式，例如 `.map((guest: string) => this.getDisplayEmail(guest))`，以避免潛在的 `this` 綁定問題。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## P0423

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）使用 parseInt 可能導致 NaN 或非預期結果

> 在 Threshold 輸入的 onChange 中使用 `parseInt(e.target.value)`，若輸入為空字串或非數字字元，`parseInt` 會回傳 `NaN`，可能導致表單值變成 `NaN`。其他元件（如 custom-trigger-fields.tsx）使用 `Number(e.target.value)`，行為較一致且可預期。建議改為 `Number(e.target.value)` 或加入驗證。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0424

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行）重複的客戶端過濾導致選取項目可能無法顯示

> `useSuspenseQuery` 的查詢參數中已經包含了 `name: { like_: deferredSearch }` 的過濾條件，但又在 `filteredData` 中對 `data` 進行了一次 `toLowerCase().includes()` 的客戶端過濾。這會造成兩個問題：
1. 伺服器端過濾可能因為大小寫或部分匹配規則不同，導致某些符合條件的項目被客戶端過濾掉。
2. 當 `selectedBlockDocumentId` 對應的項目不在 `filteredData` 中時（例如使用者選取後清除搜尋字串，但資料尚未重新載入），`selectedBlockDocument` 會是 `undefined`，導致 combobox 顯示 placeholder 而非已選取的名稱。

建議移除客戶端過濾，直接使用 `data` 作為顯示清單，並依賴伺服器端過濾。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0425

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2571`，距錨點 0 行）HINCRBYFLOAT 複寫為 HSETEX KEEPTTL 可能遺失欄位 TTL

> 原程式碼使用 `HASH_SET_KEEP_TTL` 保留欄位 TTL，但複寫指令改為 `HSETEX KEEPTTL`。若 `HSETEX KEEPTTL` 的實作在欄位不存在時不會設定 TTL，則複本上原本沒有 TTL 的欄位將維持無 TTL，但主節點上該欄位可能因 `HINCRBYFLOAT` 而獲得 TTL（例如原本有 TTL 的欄位被更新後，TTL 應保留）。需確認 `HSETEX KEEPTTL` 在欄位不存在時的行為是否與 `HASH_SET_KEEP_TTL` 一致。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0426

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）變更標記邊為跳過的順序可能導致競態條件

> 原本先標記邊為跳過再遞迴傳播，現在改為先遞迴傳播再標記。若遞迴過程中依賴邊的狀態，可能讀到未更新的狀態。需要確認 `propagate_skip_from_edge` 是否會讀取該邊的狀態，以及此變更是否會影響其他並行操作。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0427

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:378`，距錨點 3 行）過度寬泛的例外處理可能隱藏真實錯誤

> 在解析 SSL_CERT_DIR 中的每個目錄時，使用 `catch` 捕捉所有例外並忽略，可能掩蓋了非預期的錯誤（例如 `Path.GetFullPath` 因權限不足或路徑格式錯誤而拋出的例外）。建議至少記錄例外資訊，或僅捕捉預期的例外類型（如 `ArgumentException`、`NotSupportedException`、`PathTooLongException`）。

finding 片段：`catch ⏎ { ⏎ // Ignore invalid directory entries in SSL_CERT_DIR ⏎ return false;`

## P0428

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2304`，距錨點 1 行）手動傳播指令時未處理 alsoPropagate 的失敗情況

> alsoPropagate 可能因為記憶體不足或其他原因失敗，但程式碼未檢查其回傳值。若傳播失敗，可能導致主從資料不一致。

失敗情境：在記憶體不足或網路異常時，HSET 或 HPEXPIREAT 未能正確傳播到 AOF 或複本。

建議修正：檢查 alsoPropagate 的回傳值，若失敗則進行適當處理（如記錄錯誤或回傳錯誤給客戶端）。

finding 片段：`alsoPropagate(c->db->id, c->argv, c->argc, PROPAGATE_AOF|PROPAGATE_REPL);`

## P0429

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:85`，距錨點 7 行）Popover 內容的滑鼠離開處理可能導致閃爍

> PopoverContent 的 onMouseLeave 直接關閉 popover，但若滑鼠在 trigger 與 content 之間移動時，可能因事件順序造成 popover 意外關閉。建議加入延遲關閉或使用 hover intent 邏輯。

finding 片段：`<PopoverContent ⏎ side="bottom" ⏎ align="start" ⏎ className="w-fit p-2"`

## P0430

**GT**（func）Removed HTML5 min validation from concurrency limit input

> The concurrency limit input field previously had `min={0}` attribute (HTML5 validation) to prevent negative numbers from being entered. This attribute was removed in this PR change. While the Zod schema still validates that the value must be >= 0, users now lose immediate feedback when trying to enter negative values. They can type a negative number like `-5` and only discover it's invalid after clicking Save, rather than being prevented from entering it in the first place. This degrades the user experience by removing client-side validation that provides instant feedback.

GT 片段：`<Input ⏎ {...field} ⏎ type="number" ⏎ placeholder="Unlimited"`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112`，距錨點 0 行）並行限制輸入未驗證數值範圍與整數

> 在 `onChange` 中直接將輸入轉為 `Number(value)`，但未檢查是否為負數、非整數或超出合理範圍。若使用者輸入 `-5` 或 `2.5`，表單會通過驗證並將無效值傳送給 API，可能導致後端錯誤或非預期行為。建議在 zod schema 中增加 `.int().nonnegative()` 驗證，或在此處進行檢查。

finding 片段：`onChange={(e) => { ⏎ const value = e.target.value; ⏎ field.onChange(value === "" ? null : Number(value)); ⏎ }}`

## P0431

**GT**（func）Public Error enum missing #[non_exhaustive] attribute

> The Error enum is public and should be marked with #[non_exhaustive] per repository Rule #9. This attribute allows adding new error variants in future versions without breaking downstream code that matches on the enum. Without it, adding any new error variant becomes a breaking change, as exhaustive pattern matches in user code will fail to compile. This is especially critical since the PR explicitly mentions this is a 'potentially breaking change' and exports a custom Error enum.

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:20`，距錨點 0 行）Error 型別移除 thiserror 衍生可能破壞下游 API

> 原本 `Error` 使用 `thiserror::Error` 衍生，現在改為手動實作 `Display` 和 `std::error::Error`。這可能影響下游依賴此 crate 的程式碼，例如使用 `thiserror` 的 `#[from]` 或依賴 `Error` 的特定 trait 實作。此外，手動實作的 `source()` 方法未包含所有變體（如 `Plist`、`X509Certificate` 等），可能導致錯誤鏈不完整。建議確認此變更是否為有意為之，並考慮提供向後相容的實作。

finding 片段：`#[derive(Debug)] ⏎ pub enum Error {`

## P0432

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:5`，距錨點 0 行）未使用的常數 UNUSED_CONSTANT 應移除

> 新增的 `UNUSED_CONSTANT` 常數未被使用，且其值為字串，可能只是測試用途。這會觸發 lint 警告，並增加不必要的程式碼。

**建議修法**：刪除此常數。

finding 片段：`const UNUSED_CONSTANT = "this-should-be-removed";`

## P0433

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:47`，距錨點 2 行）getUrlHistory 回傳型別可能為 undefined

> 在 `getUrlHistory` 中，原本的寫法會在 `history` 存在時回傳 `history`，否則繼續執行後面的邏輯。修改後直接 `return history;`，但 `getDefaultUrlHistory()` 的回傳型別可能是 `URLHistory | undefined`（從函式定義推斷）。如果 `history` 為 `undefined`，則此函式會回傳 `undefined`，而呼叫端可能預期一定拿到陣列，導致後續處理出錯。建議檢查 `getDefaultUrlHistory` 的回傳型別，並在必要時提供預設值或調整型別。

finding 片段：`return history;`

## P0434

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行）使用子字串比對判斷路徑前綴，可能誤判

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，若 `bucket_folder` 出現在路徑中間而非開頭，會錯誤地視為已前綴而直接返回，導致路徑不正確。例如 `bucket_folder='data/'`，`path='my_data/file.txt'` 會誤判。應改為檢查 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0435

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行）validateCreateScheduleInput 驗證不足

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0436

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 未驗證 schedule 結構，可能接受無效資料

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 是否為符合預期的陣列結構。若呼叫端傳入錯誤格式的 schedule，可能導致後續 API 請求失敗或產生未預期的行為。建議加入對 schedule 的型別檢查，例如確認其為二維陣列且元素包含 start 和 end。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0437

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0438

**GT**（rule）Force unwrap of URL initializer in tests (third occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行）testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤

> 在 testRequestMediaCaptureSuccess 中，decisionHandler 閉包內沒有呼叫 expectation.fulfill()，而是在呼叫 subject.webView(...) 之後直接呼叫 expectation.fulfill()。這會導致測試在 decisionHandler 被呼叫前就完成等待，無法驗證 decisionHandler 是否被呼叫及其內容。若 decisionHandler 從未被呼叫，測試仍會通過，失去測試意義。

建議將 expectation.fulfill() 移回 decisionHandler 閉包內，並移除多餘的 expectation.fulfill()。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0439

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 tool_call_response 的 content 是 `tool_responses.get(tool, agent_thought.observation)`，但此 PR 改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給使用者的工具回應內容變成工具的輸入參數，而非實際的觀察結果，造成資料錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，使用者看到的將是輸入參數而非工具輸出。

建議：改回使用 `tool_responses`，並移除不必要的 `str()` 轉換（若原本就是字串）。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0440

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email trim 可能改變原本行為，需確認是否符合預期

> 在 submitHandler 中將 email 加上 `.trim()`，這會移除前後空白。如果原本的驗證邏輯允許前後空白，這可能改變行為。建議確認 email 驗證邏輯是否已處理 trim，或此變更是否為預期。

finding 片段：`onSubmit({email: email.trim()});`

## P0441

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 21 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0442

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行）Stream listpack 估算邏輯變更可能導致記憶體高估

> 在 `kvobjComputeSize` 中，原本的估算方式是 `lpsize * (s->rax->numele-1)` 再加上最後一個 listpack 的實際大小，現在改為 `lpsize * s->rax->numele` 後又加上最後一個 listpack 的大小。這會導致最後一個 listpack 被重複計算，造成記憶體使用量高估。

具體情境：當 stream 中的元素數量超過 sample_size 時，程式會先計算前 N 個 listpack 的平均大小，然後乘以總數 `numele`，接著又加上最後一個 listpack 的實際大小。但平均大小已經包含了最後一個 listpack 的貢獻，因此最後一個 listpack 被算了兩次。

建議改回 `lpsize * (s->rax->numele-1)`，或調整邏輯以避免重複計算。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0443

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行）Storybook 中 queryClient 來源不一致

> `createTestRouter` 內建立新的 `QueryClient` 並放入 router context，但 decorator 使用模組層級的 `queryClient` 包裹 `QueryClientProvider`。這可能導致 `useSuspenseQuery` 使用 decorator 提供的 client，而 router context 中的 client 未被使用，造成快取行為不一致或測試時資料無法正確隔離。建議統一使用同一個 queryClient，或明確指定 provider 的 client 與 router context 相同。

finding 片段：`context: { queryClient: new QueryClient() },`

## P0444

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 10 行）clusterDeleteKeysInUnownedSlots 中 clusterDelKeysInSlot 的參數可能導致資料遺失

> 在 clusterDeleteKeysInUnownedSlots 中呼叫 `clusterDelKeysInSlot(i, 0)`。第二個參數的語意需要確認：若為 `save` 旗標，傳 0 可能表示不保存，但若為其他語意（例如是否為 async），可能導致錯誤。請檢查 clusterDelKeysInSlot 的定義，確保傳入正確的參數。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## P0445

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）自動遞增時未檢查 versionCode 上限

> 當 `auto_increment_version_code` 為 true 時，直接使用 `saturating_add(1)`，但未檢查是否超過 Google Play 的 2100000000 上限。若已達上限，`saturating_add` 會停留在 2100000000，可能導致上傳失敗。

建議：在遞增後檢查上限，若超過則報錯。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

## P0446

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11`，距錨點 0 行）config 值可能為空字串時仍會嘗試排程

> `config.get('memberWelcomeEmailTestInbox')` 若回傳空字串，`!config.get(...)` 為 true，因此會進入排程邏輯。但空字串可能代表未設定，不應排程。建議明確檢查 config 值是否為有效字串（非空）。

失敗情境：若 config 設定為空字串，且 `hasScheduled.processOutbox` 為 false（假設條件修正後），仍會排程，但實際上不應發送歡迎郵件。

finding 片段：`if (!config.get('memberWelcomeEmailTestInbox')) {`

## P0447

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1105`，距錨點 29 行）autoCloseOnSelect 在 inline 模式未呼叫 onClose

> 在 inline 模式（`inline={true}`）的 `SelectOptionsPopover` 中，當 `field.autoCloseOnSelect` 為 true 且為 multiselect 時，程式碼呼叫了 `onClose?.()`，但 `onClose` 是從 props 傳入的，在 `Filters` 元件中 inline 模式的 `onClose` 會設定 `setAddFilterOpen(false)` 並清除 `selectedFieldKeyForOptions`。然而，在 `SelectOptionsPopover` 的 inline 分支中，`onClose` 被呼叫後，外層的 `Popover` 可能不會正確關閉，因為 inline 模式沒有自己的 `open` state 控制。這可能導致 popover 無法關閉或狀態不同步。建議確認 inline 模式下 autoCloseOnSelect 的關閉邏輯是否正確。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## P0448

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行）getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分

> `getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 CUID 後綴，但此模式會匹配任何 email 中加號後緊接 25 個英數字的片段。例如 `user+abcdefghijklmnopqrstuvwxyz@example.com` 會被錯誤地移除加號及後續字元，導致顯示錯誤的 email。建議使用更精確的模式，例如僅在 `@` 前匹配 CUID 格式（如 `/\+[a-zA-Z0-9]{25}(?=@)/`），或改用其他方式（如從資料庫取得原始 email）。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## P0449

**GT**（func）Missing dependency in useEffect causes stale clamp detection

> The CommentContent component's useEffect hook has an empty dependency array, but it uses item.html to determine if content should be clamped. When a comment's HTML content changes (e.g., after an edit or when new data is loaded), the clamp detection won't re-run. This means the 'Show more' button may appear when it shouldn't or disappear when it should still be visible, creating a poor user experience. The dependency array should include item.html to ensure the clamp detection re-runs whenever the content changes.

GT 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 重新取得資料）。若內容長度改變，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0450

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 6 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0451

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行）XCTWaiter 使用方式錯誤，導致測試必定逾時

> `XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0452

**GT**（func）Token caching stores entire object instead of token string

> In the getToken method, when caching the JWT token, the code now stores the entire tokenData object (containing both 'token' and 'exp' properties) instead of just extracting the token string. This causes the returned token structure to be malformed as {token: {token: string, exp: number}, exp: number} instead of the expected {token: string, exp: number}. This will break any consumers of the Tinybird API (like the /api/tinybird/token endpoint and stats/tinybird.js) that expect a string token value, causing authentication failures when making requests to Tinybird pipes.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）`_serverToken` 型態不一致可能導致下游錯誤

> `_serverToken` 原本存的是字串（`tokenData.token`），現在改存整個 `tokenData` 物件。但 `getToken` 回傳的 `token` 欄位型態仍標示為 `string`，且其他使用 `getToken` 的程式碼可能預期收到字串。若下游直接將 `token` 用於 HTTP header 或字串操作，會得到 `[object Object]` 或錯誤。建議確認所有呼叫端，或改回存字串並另外保存 exp。

finding 片段：`this._serverToken = tokenData;`

## P0453

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 1 行）config 值型別不一致可能導致條件判斷錯誤

> `config.get('memberWelcomeEmailTestInbox')` 在測試中被設定為字串（如 'test-inbox@example.com'）或空字串，但在程式碼中直接作為布林條件使用。若 config 值為空字串，`welcomeEmailConfig` 為 falsy，但 `WELCOME_EMAIL_SOURCES.includes(source)` 仍可能為 true，導致非預期建立 outbox。建議明確檢查 config 值是否為非空字串，或統一型別。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0454

**GT**（func）Incorrect async Task wrapper breaks MainActor isolation in onboarding action handler

> The onActionTap closure is wrapped in a Task block without ensuring MainActor isolation. The OnboardingFlowViewModel expects this closure to be @MainActor isolated, but Task {} creates a new async context that may execute on a different executor. This causes the completion handler and handleAction calls to potentially run off the main thread, leading to concurrency violations and potential crashes when UI updates occur. The original code directly called onboardingService.handleAction which maintained proper MainActor isolation.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in ⏎ guard let onboardingService = self?.onboardingService else { return } ⏎ Task { ⏎ onboardingService.handleAction(`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行）將 @MainActor 閉包包在 Task 中可能造成非預期執行緒切換

> 原本 `onActionTap` 閉包標註為 `@MainActor`，直接呼叫 `onboardingService.handleAction`。修改後將呼叫包在 `Task { ... }` 中，但 `Task` 預設會繼承當前 actor context，若呼叫端已在 MainActor 上，則仍會在 MainActor 執行；然而若呼叫端不在 MainActor，則會切換到背景執行緒，可能導致 UI 操作或狀態更新不在主執行緒。建議明確使用 `Task { @MainActor in ... }` 或保留原本的直接呼叫。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0455

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:211`，距錨點 18 行）`deployment_id` 可能為 `None`，傳入 `create_flow_run_from_deployment` 可能導致型別錯誤

> 在 `name` 不是 UUID 且無法解析為 UUID 時，`deployment_id` 保持為 `None`。後續呼叫 `client.create_flow_run_from_deployment(deployment_id, ...)` 時，若該函式預期 `deployment_id` 為 `UUID` 型別，則可能拋出 `TypeError` 或驗證錯誤。

**失敗情境**：使用者傳入非 UUID 且非合法 UUID 字串的部署名稱（例如 `"my-flow/my-deployment"`），且該名稱無法透過 `read_deployment_by_name` 解析時，`deployment_id` 為 `None`，導致 API 呼叫失敗。

**建議**：在呼叫前檢查 `deployment_id` 是否為 `None`，或改用 `deployment.id`（從 `read_deployment_by_name` 取得的物件）作為參數。

finding 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id,`

## P0456

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題

> 新增的 `SettingsTextFormatter` 使用 singleton 模式，但沒有明顯的必要性。如果這個類別只包含無狀態的方法，可以考慮使用靜態方法，避免不必要的 singleton。另外，如果未來加入狀態，需注意執行緒安全。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0457

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行）讀取 tauri.properties 失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0458

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）讀取失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或解析失敗時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致意外重置版本碼，尤其是在檔案被誤刪或格式錯誤時，造成 Google Play 上傳失敗。

建議：在無法讀取時發出警告或錯誤，或提供明確的 fallback 策略。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0459

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 19 行）未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗

> `XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0460

**GT**（func）Incorrect localized string reference in SettingsTextFormatter

> The formatStudiesText method references strings.detailTextStudies instead of strings.detailTextStudiesV2. This causes the formatter to display the old v1 Studies message ('%@ may install and run studies from time to time.') instead of the new v148 message ('%@ randomly selects users to test features, which improves quality for everyone.') that was added in this PR. The helper class was clearly intended to format the new v148 strings based on the PR context, but uses the wrong string constant.

GT 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 5 行）SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題

> 新增的 `SettingsTextFormatter` 使用 singleton 模式，但沒有明顯的必要性。如果這個類別只包含無狀態的方法，可以考慮使用靜態方法，避免不必要的 singleton。另外，如果未來加入狀態，需注意執行緒安全。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0461

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179`，距錨點 2 行）錯誤處理中使用 `console.error` 可能洩漏敏感資訊

> 在 `onError` 和 `catch` 區塊中，使用 `console.error` 記錄錯誤物件。如果錯誤物件包含敏感資訊（例如 API 回應中的詳細資料），可能會在瀏覽器主控台中暴露。建議使用結構化記錄或僅記錄錯誤訊息，避免輸出完整物件。

finding 片段：`onError: (err) => { ⏎ const message = "Unknown error while creating block."; ⏎ toast.error(message); ⏎ console.error(message, err);`

## P0462

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行）未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗

> `XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0463

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 0 行）FakeWKNavigationDelegate 可能無法捕捉 targetFrame

> 在 decidePolicyFor navigationAction 中，navigationAction.targetFrame 可能為 nil（例如新視窗或某些重定向），此時 capturedFrame 為 nil，導致測試失敗。建議處理 targetFrame 為 nil 的情況，或使用其他 delegate 方法。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0464

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）SSL_CERT_DIR 解析時未處理 Path.GetFullPath 可能擲回的例外

> 在解析現有 SSL_CERT_DIR 時，程式碼對每個目錄呼叫 `Path.GetFullPath(dir)`，但僅以 `catch` 捕捉例外並回傳 false。然而，`Path.GetFullPath` 可能因無效路徑字元、過長路徑或權限問題擲回 `ArgumentException`、`PathTooLongException`、`SecurityException` 等。若例外發生，該目錄會被忽略，可能導致誤判憑證目錄已存在或未存在。建議明確捕捉特定例外並記錄，或先驗證路徑格式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0465

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行）Slot 型別中 userIds 型別可能不正確

> 原本從 @calcom/trpc/server/routers/viewer/slots/types 匯入的 Slot 型別中，userIds 為 number[]，但此處新定義的 Slot 型別將 userIds 設為 string[]。若實際 API 回傳的 userIds 為 number[]，則使用此型別的程式碼（例如將 userIds 轉為字串或進行數值運算）會出現型別錯誤或執行期錯誤。建議確認 API 實際回傳型別，若為 number[] 則應修正為 number[]。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## P0466

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）天數計算 off-by-one：第一天就被當成 day 1

> `#getDaysSinceFirstEmail` 使用 `Math.ceil` 計算經過天數，導致在暖機開始當天（day 0）就會得到 day 1。這會使暖機進度提前一天，例如在第一天就套用 day 1 的 limit（237），而不是 day 0 的 200。

**失敗情境**：
- 使用者在 2024-01-15 12:00 建立第一封 email，並在 2024-01-15 13:00 呼叫 `getWarmupLimit`。
- `#getDaysSinceFirstEmail` 會計算 `(Date.now() - firstEmailTime) / (1000*60*60*24)` ≈ 0.0417，`Math.ceil` 後得到 1。
- `getWarmupLimit` 會回傳 day 1 的 limit（237），而不是 day 0 的 200。

**建議修法**：
改用 `Math.floor` 來計算天數，讓 day 0 代表第一天。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0467

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 5 行）高流量分支可能導致目標上限低於當前值

> 在 `#getTargetLimit` 中，當 `lastCount >= 400_000` 時，計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 和 `absoluteIncrease = lastCount + 75_000`，然後取兩者最小值。但若 `lastCount` 接近 400,000，例如 400,000，則 `scaledIncrease = 480,000`，`absoluteIncrease = 475,000`，回傳 475,000，仍高於 400,000。但若 `lastCount` 為 500,000，則回傳 575,000，高於 500,000。然而，若 `lastCount` 為 400,000 且 `maxAbsoluteIncrease` 較小（例如 50,000），則可能回傳低於 `lastCount` 的值，導致目標上限倒退。目前設定下，`lastCount=400,000` 時回傳 475,000，仍高於 400,000，但若未來調整參數，可能出現倒退。建議明確確保回傳值至少為 `lastCount`，例如使用 `Math.max(lastCount, Math.min(scaledIncrease, absoluteIncrease))`。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## P0468

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）`CFBundleTypeExtensions` 條件判斷可能相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，但這與預期相反：通常應該在有副檔名時才加入此鍵。若 `ext` 為空，則不應加入；若 `ext` 非空，則應加入。目前的寫法會導致有副檔名時反而沒有寫入 `CFBundleTypeExtensions`，可能影響檔案關聯功能。

建議：將條件改為 `!association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0469

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript strict 模式

> 將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更與新增的元件無直接關聯，且會影響整個專案。建議恢復為 `true`，並修正任何因 strict 模式而產生的型別錯誤。

finding 片段：`"strict": false,`

## P0470

**GT**（rule）Missing ConfigureAwait(false) on Task.Yield

> The rule requires all await expressions in library code (non-test, non-sample projects) to use .ConfigureAwait(false) to avoid capturing the synchronization context, but the await Task.Yield() expression at line 291 omits it.

GT 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:291`，距錨點 0 行）新增的 Task.Yield() 可能造成不必要的延遲

> 在取得 AuthenticationState 前加入 await Task.Yield()，可能是為了避免同步阻塞，但若呼叫端已非同步，此舉可能增加延遲。建議確認其必要性，或改用 ConfigureAwait(false) 以提升效能。

finding 片段：`await Task.Yield();`

## P0471

**GT**（rule）Static property missing explicit access control modifier

> Rule 11 requires explicit access control on properties/methods. The modified static property `generator` is declared without an explicit access modifier (e.g., `private`, `internal`, `public`).

GT 片段：`// FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏資料競爭

> 將 `generator` 標記為 `nonisolated(unsafe)` 表示開發者手動保證其執行緒安全，但註解中明確指出 `ContentBlockerGenerator` 並非執行緒安全。若此靜態屬性被多個執行緒同時存取，可能導致資料競爭或未定義行為。建議確認 `ContentBlockerGenerator.factory()` 的回傳值是否真的不可變且內部狀態安全，或考慮使用鎖定、actor 或其他同步機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0472

**GT**（rule）Non-strict inequality operator used

> The rule requires using strict equality operators (=== or !==) for all comparisons, but the code uses != instead of !== to check if count is null

GT 片段：`const count = result.data[0].get('csd_email_count'); ⏎ return count != null ? count : 0;`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:111`，距錨點 0 行）`get` 方法可能不存在於回傳的資料物件

> `result.data[0].get('csd_email_count')` 假設 `data` 陣列中的元素具有 `get` 方法。若 `findPage` 回傳的是純物件而非模型實例，將導致錯誤。建議確認 `findPage` 的回傳型別，或改用屬性存取（如 `result.data[0].csd_email_count`）。

finding 片段：`const count = result.data[0].get('csd_email_count');`

## P0473

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖動的 prefix items

> `sortableKeys` 是從所有 `localKeyedValues` 取得，包含 prefix items（不可拖動）。這可能導致拖放時將項目移動到 prefix 區域，或將 prefix 項目當作拖放目標，造成排序混亂。應僅將可拖動項目的 key 傳入 `SortableContext`，或使用 `disabled` 屬性排除。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0474

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 37 行）移除型別檢查可能導致非 dict 值被指派給 job_vars_schema

> 原本的程式碼會檢查 `base_job_template["variables"]` 是否為 dict，若不是則不指派。移除檢查後，若 `variables` 的值不是 dict（例如是字串或 None），`job_vars_schema` 會被指派為該值，後續使用時可能發生型別錯誤。

建議保留型別檢查，或明確處理非 dict 的情況。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## P0475

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 錄音端點原本使用 `@Permissions([BOOKING_READ])`，現在改為 `@Permissions([BOOKING_WRITE])`。讀取錄音應只需要讀取權限，改為寫入權限可能讓具有寫入權限但無讀取權限的使用者也能存取錄音，造成權限擴張。除非有特殊原因，否則應維持 `BOOKING_READ`。

finding 片段：`@Permissions([BOOKING_WRITE])`

## P0476

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）scheduling.init() 移除了 apiUrl 參數，可能導致排程服務無法正確建構 API URL

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入了動態產生的 API URL，現在改成無參數呼叫。如果 scheduling 服務內部需要這個 URL 來進行 API 呼叫，移除後可能導致功能失效或使用錯誤的 URL。建議確認 scheduling.init() 的實作是否已改為自行取得 URL，或是否應保留此參數。

finding 片段：`scheduling.init(),`

## P0477

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確

> Unix 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，可能將不同大小寫的目錄視為相同，導致誤判。例如 `/home/user/.dotnet/corefx/cryptography/x509stores/ca` 與 `/HOME/USER/.DOTNET/...` 會被視為相同，但實際上可能指向不同位置。建議在 Unix 上使用 `StringComparison.Ordinal`，或根據作業系統選擇比較方式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0478

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）write_and_make_executable 中先設定權限再寫入檔案，可能導致權限設定失敗或檔案內容被覆蓋

> 在 `write_and_make_executable` 函式中，原本的順序是先寫入檔案再設定權限，但此 PR 將其反轉為先設定權限再寫入。這會造成兩個問題：
1. 如果 `fs::set_permissions` 失敗（例如檔案不存在），函式會回傳錯誤，但此時檔案尚未寫入，可能導致後續流程中斷。
2. 如果 `fs::write` 成功，它會以預設權限建立或覆蓋檔案，使得先前設定的 0o770 權限失效，最終檔案權限可能不是預期的 0o770。

建議恢復原本的順序：先 `fs::write`，再 `fs::set_permissions`。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0479

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:417`，距錨點 1 行）新增的 SettingsTextFormatter 可能未被使用

> `SettingsTextFormatter` 類別被新增，但在此 diff 中未看到任何使用它的程式碼。如果沒有其他地方使用，這將是死代碼，增加維護負擔。建議確認是否有後續 PR 會使用，或考慮延後加入。

finding 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ `

## P0480

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）CFBundleTypeExtensions 條件判斷邏輯相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，這與預期相反。當副檔名清單為空時，不應插入該鍵；反之，當有副檔名時才應插入。目前的行為會導致所有有副檔名的關聯都不會寫入 `CFBundleTypeExtensions`，使得 macOS 無法正確建立檔案關聯。

建議改為 `if !association.ext.is_empty() { ... }`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0481

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行）Popover 的 hover 與 click 互動可能導致無法關閉

> 在桌面端，Popover 的開啟由 onMouseEnter 觸發，關閉由 onMouseLeave 觸發。但 Popover 本身也受 onOpenChange 控制，當使用者點擊 trigger 按鈕時，Popover 會切換 open 狀態，但 mouse enter/leave 事件可能不會如預期觸發，導致 popover 卡在開啟狀態。建議移除自訂的 mouse enter/leave 處理，改用 Popover 內建的 hover 模式（例如設定 trigger="hover"），或明確處理 click 與 hover 的狀態轉換。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0482

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2571`，距錨點 0 行）複寫指令未包含 TTL 參數，可能無法保留過期時間

> `HSETEX` 指令若未指定 TTL 選項，可能預設為不設定過期時間，導致複本上欄位 TTL 遺失。需確認 `HSETEX` 在僅有 `KEEPTTL` 而無 TTL 選項時的行為。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0483

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行）validateStoredKeyConversion 未使用，可能導致錯誤的 keyFromStoredKey 未被偵測

> 新增的 `validateStoredKeyConversion` 函式從未被呼叫。若 dict type 的 `keyFromStoredKey` 回呼有誤（例如回傳 NULL 或錯誤指標），將導致後續雜湊或比較作業出錯，且難以除錯。

**建議**：在 dict 初始化或首次使用時呼叫此驗證函式，或移除該函式以避免 dead code。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) { ⏎ return extracted != NULL;`

## P0484

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈條件錯誤導致 heap buffer overflow

> 在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 只配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成 heap buffer overflow。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之外的元素，可能導致越界讀取。

失敗情境：當命令包含至少一個 key 時，迴圈會多執行一次，寫入 `slot_buffer[numkeys]`，可能破壞 heap 中相鄰的資料，甚至導致程式崩潰或被利用。

建議修正：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0485

**GT**（func）Missing @MainActor annotation in EditBookmarkViewModelTests

> The EditBookmarkViewModelTests class is missing the @MainActor annotation that was added in the PR for Swift 6 concurrency compliance. This test class uses UI components (UITableView) and interacts with MainActor-isolated types. Without the @MainActor annotation, the tests may experience data races or undefined behavior when accessing MainActor-isolated properties, particularly since the setUp and tearDown methods are now async and the test methods interact with UI components. This violates Swift 6 concurrency requirements and can lead to runtime crashes or unpredictable test behavior.

GT 片段：`class EditBookmarkViewModelTests: XCTestCase { ⏎ let folder = MockFxBookmarkNode(type: .folder, ⏎ guid: "1235", ⏎ position: 1,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Library/Bookmarks/EditBookmarkViewModelTests.swift:11`，距錨點 0 行）移除 @MainActor 可能導致測試在非主執行緒執行

> 原本類別標註為 `@MainActor`，但此次 diff 移除了該標註。若測試方法涉及 UI 或非執行緒安全的屬性，可能導致不穩定。建議確認是否真的需要移除，或改為在個別方法上標註。

finding 片段：`class EditBookmarkViewModelTests: XCTestCase {`

## P0486

**GT**（func）Incorrect deployment filtering breaks full-name matching

> The deployment filtering logic checks `dep.name not in deployment_names` instead of checking `full_name not in deployment_names`. This causes the filter to incorrectly evaluate when users specify deployment names in 'flow-name/deployment-name' format. When a user provides a full deployment name like 'my-flow/production', the code checks if 'production' (the short name) is in the list containing 'my-flow/production', which fails, causing the deployment to enter the fallback matching logic unnecessarily. This breaks the fast-path check and could lead to incorrect filtering behavior where deployments are included or excluded inappropriately.

GT 片段：`# If filtering by deployment name, check the full name matches ⏎ full_name = f"{flow_name}/{dep.name}" ⏎ if deployment_names and dep.name not in deployment_names: ⏎ # Only include if the full name matches (filter was by name parts)`

**finding**（`src/prefect/_sdk/fetcher.py:397`，距錨點 0 行）部署名稱過濾邏輯變更可能導致錯誤排除

> 原本的條件是 `if deployment_names and full_name not in deployment_names:`，現在改為 `if deployment_names and dep.name not in deployment_names:`。這會導致當使用者指定完整名稱（如 `flow-name/deployment-name`）時，`dep.name` 只包含部署名稱部分，因此永遠不會等於完整名稱，造成所有部署都被排除。

建議改回使用 `full_name` 進行比對，或明確處理完整名稱與短名稱的比對邏輯。

finding 片段：`if deployment_names and dep.name not in deployment_names:`

## P0487

**GT**（func）Validation incorrectly rejects proactive triggers with automation_triggered_event_id

> The field_validator for automation_triggered_event_id prevents setting this field when triggering_event is None. However, proactive triggers (which have no triggering_event) still create automation.triggered events and need to link actions to them via automation_triggered_event_id. The code in triggers.py sets automation_triggered_event_id=primary_state_change_event_id for all actions including proactive triggers, causing Pydantic validation to fail at runtime. This breaks all proactive automations, which is a critical functional regression.

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:774`，距錨點 0 行）field_validator 使用 info.data 可能無法取得其他欄位值

> 在 Pydantic v2 中，`field_validator` 的 `info.data` 僅包含已驗證的欄位，若 `triggering_event` 在 `automation_triggered_event_id` 之後定義，則 `info.data.get("triggering_event")` 可能為 `None`，導致驗證錯誤。建議改用 `model_validator` 或確認欄位順序。

**失敗情境**：若模型欄位順序變更，或使用 `model_construct` 跳過驗證，可能誤報錯誤。

finding 片段：`def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists.""" ⏎ if v is not None and info.data.get("triggering_event") is None: ⏎ raise ValueError(`

## P0488

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）CFBundleTypeExtensions 條件判斷邏輯相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，這與預期相反。當副檔名清單為空時，不應插入該鍵；反之，當有副檔名時才應插入。目前的行為會導致所有有副檔名的關聯都不會寫入 `CFBundleTypeExtensions`，使得 macOS 無法正確建立檔案關聯。

建議改為 `if !association.ext.is_empty() { ... }`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0489

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行）clusterCommonInit 使用 malloc 而非 zmalloc 分配 cluster_slot_stats

> 在 clusterCommonInit 中，`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));` 使用了標準 malloc，而非 Redis 慣用的 zmalloc。這會導致記憶體分配未納入 Redis 的記憶體統計，且無法在 OOM 時觸發 Redis 的錯誤處理。建議改用 `zmalloc`。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0490

**GT**（rule）Direct logging.getLogger() call used

> The rule requires loggers to be instantiated using the pattern `logger: "logging.Logger" = get_logger("module_name")` instead of direct `logging.getLogger()` calls

GT 片段：`# Log which UI version is being served ⏎ if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

**finding**（`src/prefect/server/api/server.py:509`，距錨點 20 行）`source_static_path` 可能未定義導致 `NameError`

> `source_static_path` 在 `if v2_enabled` 為假時未被賦值，但此處直接使用 `str(source_static_path)`。若 `v2_enabled` 為假，將拋出 `NameError`。

**失敗情境**：使用 V1 UI 時，伺服器啟動即失敗。

**建議修法**：在條件判斷前先定義 `source_static_path` 的預設值，或將此邏輯移入對應分支。

finding 片段：`copy_directory(str(source_static_path), str(static_dir))`

## P0491

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）malloc 失敗未處理，可能導致 null pointer dereference

> `slot_buffer = malloc(sizeof(int) * keys_result->numkeys);` 沒有檢查回傳值。若記憶體配置失敗，`slot_buffer` 為 NULL，後續 `slot_buffer[j] = this_slot;` 會寫入 NULL 位址，造成程式崩潰。

失敗情境：在記憶體不足或 `numkeys` 極大時，malloc 可能失敗，導致伺服器 crash。

建議修正：檢查 malloc 回傳值，若為 NULL 則回傳錯誤或改用 stack allocation（若 numkeys 有上限）。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0492

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 12 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## P0493

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter.wait 的結果未檢查

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0494

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行）Popover 內容的 hover 處理可能造成閃爍

> PopoverContent 上也設定了 onMouseEnter 和 onMouseLeave，當滑鼠從 trigger 移動到 popover 內容時，可能會因為 mouseleave 觸發關閉，然後 mouseenter 又開啟，造成閃爍。建議使用 Popover 的 hover 模式或設定適當的 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0495

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 1 行）testRequestMediaCaptureSuccess 的 expectation 邏輯錯誤

> 在 testRequestMediaCaptureSuccess 中，decisionHandler 閉包內沒有呼叫 expectation.fulfill()，而是在呼叫 subject.webView(...) 之後直接呼叫 expectation.fulfill()。這會導致測試在 decisionHandler 被呼叫前就完成等待，無法驗證 decisionHandler 是否被呼叫及其內容。若 decisionHandler 從未被呼叫，測試仍會通過，失去測試意義。

建議將 expectation.fulfill() 移回 decisionHandler 閉包內，並移除多餘的 expectation.fulfill()。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## P0496

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）當 SMTP_LOCAL_HOSTNAME 為空字串時，local_hostname 傳入 None 可能導致非預期行為

> 程式碼使用 `local_host or None`，若設定為空字串，則傳入 None。smtplib 在建構時若 local_hostname 為 None，會自動使用 socket.getfqdn()，這可能與預期不符（預期不覆寫時應使用預設行為，但 None 可能觸發不同的行為）。建議明確處理空字串，例如僅在設定非空時才傳遞 local_hostname 參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0497

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 5 行）使用 String(format:) 搭配本地化字串可能導致崩潰

> `SettingsTextFormatter` 中的 `formatStudiesText` 和 `formatRolloutsText` 使用 `String(format: strings.detailTextStudies, appName)`。`detailTextStudies` 和 `detailTextRollouts` 是本地化字串，其內容可能包含額外的格式說明符（例如翻譯後的字串可能包含 `%d` 或 `%2$@`），這會導致 `String(format:)` 在執行時期因參數數量不符而崩潰，或顯示錯誤的內容。建議改用 `String.localizedStringWithFormat` 或避免使用格式字串，直接使用字串插值或替換。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ } ⏎ `

## P0498

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:50`，距錨點 18 行）Popover 在觸控裝置上無法透過 hover 開啟

> LimitedBadges 的 Popover 僅透過 onMouseEnter/onMouseLeave 控制開啟，且 handleMouseEnter 在 isMobile 為 true 時直接 return，因此觸控裝置（如手機、平板）的使用者無法看到隱藏的 badges。建議改為點擊觸發（例如使用 PopoverTrigger 的 onClick），或提供明確的點擊目標。

finding 片段：`const handleMouseEnter = useCallback(() => { ⏎ if (!isMobile) { ⏎ setIsOpen(true); ⏎ }`

## P0499

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 `{newsletterName}` 變數，可能導致使用者無法知道是哪個新聞信。建議保留變數以提供完整資訊。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0500

**GT**（func）Incorrect operation order causes potential data loss during cluster verification

> The verifyClusterConfigWithData() function executes clusterDeleteKeysInUnownedSlots() before clusterClaimUnassignedSlots(). This reverses the intended logic: the function should first claim ownership of unassigned slots that contain keys (preventing orphaned data), then delete keys from slots that are genuinely owned by other nodes. With this bug, keys in unassigned slots may be incorrectly deleted before the node has a chance to claim ownership, resulting in permanent data loss during cluster startup or recovery scenarios.

GT 片段：`/* Delete keys in unowned slots */ ⏎ clusterDeleteKeysInUnownedSlots(); ⏎ /* Take over slots that we have keys for, but are assigned to no one. */ ⏎ clusterClaimUnassignedSlots();`

**finding**（`src/cluster.c:2212`，距錨點 0 行）verifyClusterConfigWithData() 中 clusterClaimUnassignedSlots() 可能覆蓋既有設定

> clusterClaimUnassignedSlots() 會將所有有 key 但無主的 slot 指派給自己，但未檢查是否已有其他節點正在進行遷移或設定。這可能導致叢集狀態不一致。建議在 claim 前檢查 slot 是否處於特殊狀態，或增加日誌記錄。

finding 片段：`clusterClaimUnassignedSlots();`
