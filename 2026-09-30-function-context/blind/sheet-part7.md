# 盲標單 7：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part7.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0601

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:53`，距錨點 0 行）sortHosts 函式在移動時 priority 排序方向被反轉

> 在 `isRRWeightsEnabled` 為 true 且權重相同時，原本的程式碼回傳 `priorityB - priorityA`（降冪），但移動後變成 `priorityA - priorityB`（升冪）。這會導致主持人排序結果相反，可能影響輪流主持（round-robin）的權重分配。請改回 `priorityB - priorityA`。

finding 片段：`return priorityA - priorityB;`

## P0602

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2304`，距錨點 1 行）手動傳播指令時未處理 alsoPropagate 的失敗情況

> alsoPropagate 可能因為記憶體不足或其他原因失敗，但程式碼未檢查其回傳值。若傳播失敗，可能導致主從資料不一致。

失敗情境：在記憶體不足或網路異常時，HSET 或 HPEXPIREAT 未能正確傳播到 AOF 或複本。

建議修正：檢查 alsoPropagate 的回傳值，若失敗則進行適當處理（如記錄錯誤或回傳錯誤給客戶端）。

finding 片段：`alsoPropagate(c->db->id, c->argv, c->argc, PROPAGATE_AOF|PROPAGATE_REPL);`

## P0603

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 10 行）getRecordings 呼叫缺少 await，可能回傳未解析的 Promise

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫移除了 `await`。若 `getRecordings` 是非同步方法（從其他端點如 `getVideoSessions` 使用 `await` 可推測），則回傳的 `recordings` 會是 Promise 物件而非實際資料，導致 API 回傳錯誤的資料型態或序列化失敗。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件，而非錄製陣列，可能造成客戶端解析錯誤或資料外洩。

**建議**：恢復 `await`，改為 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0604

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34`，距錨點 9 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致 `wait(for:)` 永遠等不到 expectation 被 fulfill，直到逾時。

應將 `expectation.fulfill()` 移回 `decisionHandler` 內，與其他測試保持一致。

finding 片段：`wait(for: [expectation]) ⏎ expectation.fulfill()`

## P0605

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）未處理 ConversationVariableNotFoundError

> `self._conversation_variable_updater.update(...)` 可能拋出 `ConversationVariableNotFoundError`，但此處未捕捉。若變數在資料庫中不存在，整個 workflow 會失敗。需確認此行為是否符合預期，或應記錄錯誤並繼續。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable)`

## P0606

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）檔案寫入前設定權限可能導致失敗

> 在 `write_and_make_executable` 中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會回傳錯誤，導致函式失敗。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0607

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，但此處傳入的參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。根據 HSETEX 語法，正確順序應為 `HSETEX key [KEEPTTL] FIELDS num field value`，因此 `shared.keepttl` 應在 `shared.fields` 之前，但此處 `shared.keepttl` 在 `shared.fields` 之後，可能導致複寫指令格式錯誤。

失敗情境：當主節點執行 HINCRBYFLOAT 時，複本會收到錯誤格式的 HSETEX 指令，導致複寫中斷或資料不一致。

建議修正：調整參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0608

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 6 行）重複的客戶端過濾導致選取項目可能無法顯示

> `useSuspenseQuery` 的查詢參數中已經包含了 `name: { like_: deferredSearch }` 的過濾條件，但又在 `filteredData` 中對 `data` 進行了一次 `toLowerCase().includes()` 的客戶端過濾。這會造成兩個問題：
1. 伺服器端過濾可能因為大小寫或部分匹配規則不同，導致某些符合條件的項目被客戶端過濾掉。
2. 當 `selectedBlockDocumentId` 對應的項目不在 `filteredData` 中時（例如使用者選取後清除搜尋字串，但資料尚未重新載入），`selectedBlockDocument` 會是 `undefined`，導致 combobox 顯示 placeholder 而非已選取的名稱。

建議移除客戶端過濾，直接使用 `data` 作為顯示清單，並依賴伺服器端過濾。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0609

**GT**（func）Missing PreReleaseBrandingLabel for servicing builds

> The PreReleaseBrandingLabel configuration is missing the condition for 'servicing' builds. While the PreReleaseVersionLabel is set to 'servicing', there is no corresponding conditional assignment for PreReleaseBrandingLabel when PreReleaseVersionLabel equals 'servicing'. This means servicing builds will have an undefined or incorrect branding label, causing incorrect version strings in build outputs and package metadata. The original PR added this condition to properly support servicing releases.

GT 片段：`<PreReleaseVersionLabel>servicing</PreReleaseVersionLabel> ⏎ <!-- PreReleaseBrandingLabel is automatically calculated based on PreReleaseVersionLabel --> ⏎ <PreReleaseBrandingLabel Condition="'$(PreReleaseVersionLabel)' == 'alpha'">Alpha $(PreReleaseVersionIteration)</PreReleaseBrandingLabel> ⏎ <Pre`

**finding**（`eng/Versions.props:14`，距錨點 8 行）ValidateBaseline 設為 false 可能隱藏套件參考變更

> 將 `ValidateBaseline` 從 `true` 改為 `false`，這會停用基線驗證，可能導致未預期的套件參考變更被忽略。在 servicing 更新中，這可能允許破壞性變更進入發行版本。建議確認此變更的必要性，並考慮僅在特定條件下停用。

finding 片段：`<ValidateBaseline>false</ValidateBaseline>`

## P0610

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46`，距錨點 3 行）強制轉型為 AppCompatActivity 可能導致 ClassCastException

> 在建構子中直接 `(activity as AppCompatActivity)`，若傳入的 Activity 不是 AppCompatActivity（例如使用非 AppCompat 主題），會拋出 ClassCastException。建議檢查型別或改用 ComponentActivity。

finding 片段：`(activity as AppCompatActivity).onBackPressedDispatcher.addCallback(activity, callback)`

## P0611

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 7 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0612

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作

> 原本 `scheduling.init()` 會傳入 `apiUrl` 參數，用於建構排程服務所需的 API URL。移除後，排程服務可能無法正確取得 API 位址，導致排程任務失敗或無法觸發。建議確認 `scheduling.init()` 是否已改為從其他來源取得 API URL，或此參數是否已不再需要。

finding 片段：`scheduling.init(),`

## P0613

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）extractKeysAndSlot 可能留下未初始化的 *slot

> 在 `extractKeysAndSlot` 中，原本 `*slot = INVALID_CLUSTER_SLOT;` 被移除，改為僅在 `num_keys > 0` 時設定 `*slot`。若 `num_keys == 0` 或 `num_keys < 0`，`*slot` 將保持呼叫者傳入的未初始化值，可能導致後續使用未定義行為。

建議在函式開頭初始化 `*slot = INVALID_CLUSTER_SLOT;`，或確保所有呼叫者在呼叫前已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0614

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行）直接使用 ureq::get 未套用系統憑證設定

> 在 `download_webview2_offline_installer` 中，改用 `ureq::get(url)` 而非透過 `base_ureq_agent()` 建立的 agent，這可能導致在啟用 platform-certs feature 時，此請求未使用系統憑證，造成 TLS 驗證失敗。建議改用 `base_ureq_agent().get(url)` 以確保一致性。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## P0615

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行）使用子字串比對判斷路徑前綴，可能誤判

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，若 `bucket_folder` 出現在路徑中間而非開頭，會錯誤地視為已前綴而直接返回，導致路徑不正確。例如 `bucket_folder='data/'`，`path='my_data/file.txt'` 會誤判。應改為檢查 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0616

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行）條件判斷邏輯可能錯誤：`||` 改為 `&&` 導致 JSON 檔案不再進行 schema 驗證

> 原本條件為 `config_path.extension() == Some(OsStr::new("json")) || config_path.extension() == Some(OsStr::new("json5"))`，現在改為 `&&`。這使得只有當副檔名同時等於 "json" 和 "json5"（不可能）時才會進入驗證區塊，實際上等於永遠不驗證。這可能導致 JSON 設定檔不再進行 schema 驗證，喪失原本的檢查功能。請確認是否為預期行為，若不是，應改回 `||`。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## P0617

**GT**（func）Missing try keyword in async throws method call

> The IpadOnlyTestCase.setUp() method is marked as 'async throws' but calls 'await super.setUp()' without the 'try' keyword. Since BaseTestCase.setUp() is declared as 'async throws', this means any errors thrown by the parent setUp will not be properly propagated and will instead cause a compilation error or runtime crash. This breaks the error handling contract for all iPad-specific test cases that inherit from IpadOnlyTestCase, potentially causing test suite failures or silent test skips.

GT 片段：`class IpadOnlyTestCase: BaseTestCase { ⏎ override func setUp() async throws { ⏎ specificForPlatform = .pad ⏎ if iPad() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508`，距錨點 0 行）IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try

> 在 `IpadOnlyTestCase` 的 `setUp` 中，`super.setUp()` 現在是 `async throws`，但呼叫處沒有加上 `try`，會導致編譯錯誤。請改為 `try await super.setUp()`。

finding 片段：`await super.setUp()`

## P0618

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）SMTP 類別選擇邏輯可能改變非 TLS 與 TLS 模式的行為

> 原本程式碼根據 use_tls 和 opportunistic_tls 明確選擇 SMTP 或 SMTP_SSL，並在 opportunistic TLS 時先建立 SMTP 再呼叫 starttls。新程式碼使用三元運算子選擇類別，但條件 `(self.use_tls and not self.opportunistic_tls)` 在 use_tls=False 時會選擇 SMTP（正確），但在 use_tls=True 且 opportunistic_tls=True 時也會選擇 SMTP（正確），然而在 use_tls=True 且 opportunistic_tls=False 時選擇 SMTP_SSL（正確）。看似等價，但需注意原本在非 TLS 模式下（use_tls=False）直接建立 SMTP，新程式碼也相同。然而，原本在 opportunistic TLS 模式下，先建立 SMTP 後呼叫 ehlo(self.server)，新程式碼改為 ehlo(local_host)，其中 local_host 可能為空字串，這可能導致 HELO 命令使用空字串而非伺服器位址，違反 SMTP 規範。建議確認 local_host 為空時應回退為 self.server。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0619

**GT**（func）Incomplete cache clearing during hot reload causes stale display names

> The ClearCache method only clears _memberInfoCache but fails to clear _displayNameCache (line 85). During hot reload scenarios when metadata updates occur, the HotReloadManager triggers ClearCache to ensure fresh metadata is loaded. However, with _displayNameCache not being cleared, the component will continue to display stale display names from cached MemberInfo objects even after the attributes have been modified in code. This breaks the hot reload functionality for DisplayAttribute and DisplayNameAttribute changes, requiring developers to restart the application to see attribute changes take effect.

GT 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 0 行）Hot Reload 時未清除顯示名稱快取

> `ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。如果 Hot Reload 期間屬性的顯示名稱屬性發生變更，`_displayNameCache` 可能返回舊值。

**失敗情境**：開發者在 Hot Reload 中修改了屬性的 `[Display]` 屬性，但由於 `_displayNameCache` 未清除，元件仍顯示舊名稱。

**建議**：在 `ClearCache` 中同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0620

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:34`，距錨點 4 行）conversation_id 取得方式與既有邏輯不同，可能導致行為差異

> 此處使用 `self.graph_runtime_state.system_variable.conversation_id`，而舊邏輯是從 variable pool 取得 `["sys", "conversation_id"]`。若 system_variable 的 conversation_id 與 variable pool 中的不一致，可能造成更新到錯誤的 conversation。需確認兩者來源是否一致。

finding 片段：`conversation_id = self.graph_runtime_state.system_variable.conversation_id`

## P0621

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:202`，距錨點 1 行）comment 中的引號變更可能影響翻譯工具

> `detailTextSendUsageData` 和 `detailTextStudies` 的 comment 從智慧引號（“ ”）改為直引號（" "）。這可能導致翻譯工具將這些 comment 視為不同，造成翻譯記憶庫不一致。建議確認此變更是否必要，並保持 comment 風格一致。

finding 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

## P0622

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:203`，距錨點 1 行）新增的 V2 字串可能未被使用

> 新增了 `detailTextSendUsageDataV2`、`labelStudiesV2`、`detailTextStudiesV2` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

finding 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

## P0623

**GT**（func）Insufficient timeout for paste permission dialog causing test flakiness

> The timeout for the 'Allow Paste' permission dialog button was reduced from 1.5 seconds to 0.5 seconds. This is too short for the iOS permission dialog to appear and be interactable, especially on slower devices or under load. The tapIfExists method waits for the element to exist within the specified timeout before attempting to tap it. A 0.5 second timeout may cause the test to miss the permission dialog entirely, preventing the paste action from completing and causing subsequent assertions to fail when the URL is not populated in the address bar.

GT 片段：`urlBar.pressWithRetry(duration: 2.0, element: pasteAction) ⏎ mozWaitForElementToExist(app.tables["Context Menu"]) ⏎ pasteAction.waitAndTap() ⏎ springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471`，距錨點 0 行）貼上權限彈窗處理可能不穩定

> 新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 使用固定 0.5 秒等待，若系統彈窗出現較慢，可能無法點擊，導致後續驗證失敗。建議使用更可靠的等待機制，例如 `mozWaitForElementToExist` 或增加重試邏輯。

finding 片段：`springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

## P0624

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行）合併設定時不再更新 inner，改為存入 extensions，可能影響後續使用

> 原本 `merge_with` 會將合併後的結果反序列化回 `config_metadata.inner`，現在改為將 `merge_config` 存入 `extensions`。這可能導致後續程式碼若直接讀取 `inner` 會拿到未合併的設定，造成行為不一致。請確認所有使用 `inner` 的地方是否已改為從 extensions 取得合併結果，或此變更是否為預期。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## P0625

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試中使用了錯誤的泛型型別進行驗證

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，渲染的元件型別是 `GenericComponent<int>`（`typeof(GenericComponent<int>)`），但後續驗證 preamble marker 時卻使用了 `GenericComponent<string>` 的組件名稱與完整名稱：
```csharp
Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly);
Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);
```
這會導致測試失敗，因為實際序列化的型別資訊應為 `GenericComponent<int>`。建議將這兩行改為使用 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0626

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2571`，距錨點 11 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，此處傳入 6 個參數，但 `HSETEX` 指令的語法為 `HSETEX key [NX|XX] [KEEPTTL] [EX|PX|EXAT|PXAT] FIELDS num field value [field value ...]`。目前建構的指令為 `HSETEX key KEEPTTL FIELDS 1 field value`，缺少 TTL 選項，可能導致語法錯誤或行為不符預期。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0627

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）local_hostname 參數傳遞空字串可能導致 SMTP 連線失敗

> 程式碼使用 `local_host or None` 將空字串轉為 None，但 smtplib.SMTP 的 local_hostname 參數若為 None，會使用 socket.getfqdn() 取得本機主機名稱。若設定 SMTP_LOCAL_HOSTNAME 為空字串，原本意圖可能是使用預設值，但傳遞 None 會觸發 getfqdn()，可能導致 DNS 查詢延遲或失敗。建議明確處理空字串，例如直接傳遞 local_host（若為空字串則由 smtplib 自行處理）或設定為 None 前先檢查。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0628

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行）getDisplayEmail 正規表達式可能誤刪合法 email 中的加號部分

> `getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除 CUID 後綴，但此模式會匹配任何 email 中出現的 `+` 後接 25 個英數字元的片段。若使用者的 email 本身包含加號（例如 `user+tag@example.com`），且 `tag` 恰好為 25 個英數字元，則該部分會被錯誤移除，導致顯示錯誤的 email。

**失敗情境**：使用者 email 為 `john+abcdefghijklmnopqrstuvwxyz12345@example.com`（加號後 25 個字元），`getDisplayEmail` 會回傳 `john@example.com`，而非原始 email。

**建議**：改為更精確的比對，例如僅在 email 的 local part 中比對 CUID 格式（如 `/\+[a-zA-Z0-9]{25}@/`），或使用已知的 CUID 產生規則來驗證。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## P0629

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 1 行）FakeWKNavigationDelegate 可能無法捕捉 targetFrame

> 在 decidePolicyFor navigationAction 中，navigationAction.targetFrame 可能為 nil（例如新視窗或某些重定向），此時 capturedFrame 為 nil，導致測試失敗。建議處理 targetFrame 為 nil 的情況，或使用其他 delegate 方法。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0630

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行）路徑前綴檢查未考慮正規化

> 即使改用 `startswith`，若 `path` 未正規化（例如包含 `./` 或 `../`），可能仍會誤判。建議先將 `path` 轉為 `PurePosixPath` 並正規化後再比較前綴。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0631

**GT**（func）Double-wrapping data structure causes matching members to be ignored

> The useTeamMembersWithSegment hook wraps the matchingTeamMembersWithResult in an extra layer when it already has a 'result' property from the trpc query. The trpc query returns { result, troubleshooter, mainWarnings, fallbackWarnings }, but the code creates { result: { result: ... } } by conditionally wrapping it again. This causes useProcessTeamMembersData to receive an incorrectly nested structure where matchingTeamMembersWithResult.result contains an object instead of an array, breaking the segment-based member filtering logic and causing the app to show all team members instead of only those matching the attribute segment.

GT 片段：`const { teamMembers, localWeightsInitialValues } = useProcessTeamMembersData({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:28`，距錨點 0 行）傳遞給 useProcessTeamMembersData 的 matchingTeamMembersWithResult 型別可能不符

> `useProcessTeamMembersData` 期望 `matchingTeamMembersWithResult` 為 `{ result: TeamMemberDto[] | null }`，但此處傳入的是 `matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult`。當 `matchingTeamMembersWithResult` 為 undefined 時，會傳入 undefined，可能導致型別錯誤或執行時期問題。

**失敗情境**：當查詢未啟用或尚未回傳時，`matchingTeamMembersWithResult` 為 undefined，傳入 undefined 可能導致 `useProcessTeamMembersData` 內部存取 `matchingTeamMembersWithResult?.result` 時出錯。

**建議**：確保傳入的物件符合型別，或調整 `useProcessTeamMembersData` 的參數型別以接受 undefined。

finding 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

## P0632

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）HPEXPIREAT 傳播時建立的 argv[2] 字串物件未釋放，造成記憶體洩漏

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);` 並傳遞給 `alsoPropagate`。但 `alsoPropagate` 不會取得物件的所有權，呼叫後此物件不會被釋放。每次執行具有過期時間的 HINCRBYFLOAT 都會洩漏一個 robj，長期下來可能導致記憶體耗盡。

建議在 `alsoPropagate` 呼叫後立即 `decrRefCount(argv[2]);`，或改用其他方式建立暫時物件（例如使用 stack 上的 robj 或直接傳遞字串）。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0633

**GT**（func）Incorrect initialization order in test setup

> In FeatureFlaggedTestSuite.setUp(), the method calls setUpApp() before setUpExperimentVariables(). However, setUpApp() (line 42-44) directly uses jsonFileName and featureName properties that are initialized by setUpExperimentVariables(). This means setUpApp() will be called with nil or uninitialized values, causing addLaunchArgument() to receive invalid parameters. This breaks the experiment/feature flag configuration for all tests inheriting from FeatureFlaggedTestSuite, resulting in tests running with incorrect or missing feature flags.

GT 片段：`override func setUp() async throws { ⏎ continueAfterFailure = false ⏎ setUpApp()  // Called before setUpExperimentVariables ⏎ setUpExperimentVariables()  // Sets jsonFileName and featureName`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48`，距錨點 0 行）setUp 中呼叫順序變更可能影響測試行為

> 原本 `setUpExperimentVariables()` 在 `setUpApp()` 之前呼叫，現在順序對調。若 `setUpApp()` 依賴實驗變數已設定，可能導致測試行為改變。請確認此順序變更是有意且安全的。

finding 片段：`setUpApp() ⏎ setUpExperimentVariables()`

## P0634

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 38 行）移除 strict=True 可能導致 zip 靜默截斷

> 在 `_fetch_work_pools_parallel` 中，原本使用 `zip(pool_names_list, results, strict=True)` 確保兩個序列長度一致。移除 `strict=True` 後，若 `pool_names_list` 和 `results` 長度不同，zip 會靜默截斷到較短的長度，導致部分 work pool 的結果被忽略，且不會有任何錯誤提示。這可能造成 SDK 資料不完整，且難以偵錯。建議保留 `strict=True`，或明確處理長度不一致的情況。

finding 片段：`for name, result in zip(pool_names_list, results):`

## P0635

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:44`，距錨點 24 行）maxVisible 未限制最小值，可能導致顯示異常

> maxVisible 是外部傳入的 prop，若傳入負數或 0，visibleItems 會是空陣列，而 hiddenItems 會包含所有項目，導致只顯示 +N 的 badge，但點開 popover 後所有項目都在隱藏區。建議加上 maxVisible 的最小值限制（例如 Math.max(1, maxVisible)）。

finding 片段：`visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0636

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15`，距錨點 0 行）排程條件反轉，可能導致重複排程或未排程

> 原本的條件 `!hasScheduled.processOutbox` 在尚未排程時才進行排程，但修改後變成 `hasScheduled.processOutbox`，導致只有在已排程時才會再次排程，造成重複排程；若尚未排程則永遠不會排程。

失敗情境：當 `hasScheduled.processOutbox` 為 false 時，函式直接回傳 false，不會呼叫 `jobsService.addJob`，因此歡迎郵件排程永遠不會被建立。

建議改回 `!hasScheduled.processOutbox`。

finding 片段：`if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`

## P0637

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，其他變體都輸出小寫（如 "deb"、"rpm"），但新增的 `Flatpak` 輸出 "Flatpak"（首字母大寫）。這可能導致序列化或比對時出現不一致，例如在產生 bundle 檔名或與其他工具互動時。建議改為 "flatpak"。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0638

**GT**（func）JSON schema cleared for all variable types, not just jsonObject

> The payloadToSave logic removes the json_schema field whenever isSchemaEmpty is true, regardless of the variable type. The original code correctly checked `tempPayload.type === InputVarType.jsonObject && isSchemaEmpty`. By removing the type check, if a user switches from jsonObject type to another type (like textInput) and the schema happens to be empty, the json_schema field gets cleared even though it should be preserved during the transition. This causes data loss when users change variable types back and forth.

GT 片段：`// if the input type is jsonObject and the schema is empty as determined by `isJsonSchemaEmpty`, ⏎ // remove the `json_schema` field from the payload by setting its value to `undefined`. ⏎ const payloadToSave = isSchemaEmpty ⏎ ? { ...tempPayload, json_schema: undefined }`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:255`，距錨點 0 行）空 schema 設定為 undefined 可能與後端預期不符

> 在 `handleConfirm` 中，若 schema 為空，會將 `json_schema` 設為 `undefined` 後傳給 `onConfirm`。這可能導致後端收到缺少 `json_schema` 欄位的 payload，若後端預期該欄位存在（即使是空字串），可能造成錯誤。建議確認後端 API 對 `json_schema` 的處理方式，或改為傳送空字串。

finding 片段：`const payloadToSave = isSchemaEmpty ⏎ ? { ...tempPayload, json_schema: undefined } ⏎ : tempPayload`

## P0639

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）回傳 `Infinity` 可能造成下游型別或比較問題

> 當暖機完成後，`getWarmupLimit` 回傳 `Infinity`。這可能導致下游程式碼在進行數值比較或計算時出現非預期行為，例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若下游直接使用該值進行算術運算，可能產生 `Infinity` 或 `NaN`。

**建議修法**：
回傳 `emailCount` 本身，或使用一個明確的哨兵值（例如 `Number.MAX_SAFE_INTEGER`），並在文件或型別中說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0640

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）`getWarmupLimit` 可能回傳 `Infinity`，呼叫端需能處理

> 當 `day > totalDays` 時，函式回傳 `Infinity`。若呼叫端未預期此值，可能導致後續計算（如 `Math.min`、陣列 slice 等）出現非預期行為。建議確認所有呼叫端都能正確處理 `Infinity`，或改回傳一個明確的哨兵值（例如 `emailCount` 或 `Number.MAX_SAFE_INTEGER`）。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0641

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 驗證條件從 `value <= 0` 改為 `value < 0`，這表示 `value = 0` 現在會被接受。但屬性文件仍描述為「strictly positive value」，且錯誤訊息仍為「must be positive」。若 0 值被允許，可能導致保留檔案數為 0 的意外行為（例如不保留任何檔案），或與其他邏輯衝突。請確認此變更是否為預期，並更新文件與錯誤訊息以反映實際允許的範圍。

finding 片段：`if (value < 0)`

## P0642

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:75`，距錨點 4 行）Popover 內容無法透過鍵盤操作

> PopoverTrigger 使用 Button 元件，但未提供 onKeyDown 或 focus 管理，鍵盤使用者無法開啟或瀏覽 popover 內容。建議加入適當的鍵盤事件處理（例如 Enter/Space 開啟、Escape 關閉），並確保焦點能移至 popover 內。

finding 片段：`<PopoverTrigger asChild> ⏎ <Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0"`

## P0643

**GT**（rule）Default export used in non-page/layout component file

> Rule allows default exports only in Next.js page/layout files. This component wrapper file exports a default export, violating the named-export requirement.

GT 片段：`export default EventLimitsTabWebWrapper;`

**finding**（`apps/web/modules/event-types/components/tabs/limits/EventLimitsTabWebWrapper.tsx:8`，距錨點 0 行）檔案缺少結尾換行

> 檔案最後一行 `export default EventLimitsTabWebWrapper;` 沒有換行符號，可能導致某些工具或 linter 警告。建議補上換行。

finding 片段：`export default EventLimitsTabWebWrapper;`

## P0644

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:417`，距錨點 0 行）新增的 SettingsTextFormatter 可能未被使用

> `SettingsTextFormatter` 類別被新增，但在此 diff 中未看到任何使用它的程式碼。如果沒有其他地方使用，這將是死代碼，增加維護負擔。建議確認是否有後續 PR 會使用，或考慮延後加入。

finding 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ `

## P0645

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:85`，距錨點 6 行）Popover 內容的滑鼠離開處理可能導致閃爍

> PopoverContent 的 onMouseLeave 直接關閉 popover，但若滑鼠在 trigger 與 content 之間移動時，可能因事件順序造成 popover 意外關閉。建議加入延遲關閉或使用 hover intent 邏輯。

finding 片段：`<PopoverContent ⏎ side="bottom" ⏎ align="start" ⏎ className="w-fit p-2"`

## P0646

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）自動遞增時未檢查 versionCode 上限

> 當 `auto_increment_version_code` 為 true 時，直接使用 `saturating_add(1)`，但未檢查是否超過 Google Play 的 2100000000 上限。若已達上限，`saturating_add` 會停留在 2100000000，可能導致上傳失敗。

建議：在遞增後檢查上限，若超過則報錯。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

## P0647

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1841`，距錨點 0 行）loadAppendOnlyFiles 中對 AOF_BROKEN_RECOVERED 的處理不一致

> 在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且 `last_file` 為 false 時，程式碼會將 `ret` 設為 `AOF_FAILED` 並記錄錯誤，但之後的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 條件中又包含了 `AOF_BROKEN_RECOVERED`，這可能導致非最後一個檔案被錯誤接受。

建議移除該條件中的 `ret == AOF_BROKEN_RECOVERED`，或明確處理此情況。

finding 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

## P0648

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行）命名空間與類別宣告格式變更可能不必要

> 此檔案從 file-scoped namespace（`namespace Microsoft.AspNetCore.Components.Server.Circuits;`）改為 block-scoped namespace，並將類別宣告移至大括號內，但縮排未隨之調整（類別內成員仍維持原縮排）。這可能是無意的格式變更，且與專案其他檔案的風格不一致。建議確認此變更是否必要，若無必要請還原；若必要，請調整縮排以符合規範。

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ { ⏎ public class ServerComponentDeserializerTest ⏎ {`

## P0649

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:44`，距錨點 0 行）BackgroundQueueSize 驗證條件變更可能禁止 0 值

> 驗證條件從 `value < 0` 改為 `value <= 0`，這表示 `value = 0` 現在會拋出例外。但錯誤訊息仍為「must be non-negative」，且文件未明確說明 0 的意義（可能代表無佇列或無限制）。若 0 值原本是合法設定，此變更會破壞向後相容性。請確認意圖並更新文件與錯誤訊息。

finding 片段：`if (value <= 0)`

## P0650

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。如果使用者未在設定中提供 `name` 且 `ext` 為空，程式會 panic。雖然 schema 可能要求 `name` 或 `ext` 至少一個存在，但此處的變更增加了執行時錯誤的風險。建議保留原本的 fallback 邏輯，或改為更安全的處理方式。

finding 片段：`.expect("File association must have a name")`

## P0651

**GT**（func）Incorrect event level causes important certificate warnings to be suppressed in non-verbose mode

> When verbose mode is not enabled, the event listener is configured with EventLevel.LogAlways instead of the intended EventLevel.Critical. EventLevel.LogAlways (value 0) actually means all events are enabled, not just critical ones. The original PR intended to show only Critical events in non-verbose mode to suppress routine logging. This bug causes all certificate-related events including verbose debug messages to be displayed in non-verbose mode, flooding users with unnecessary output and making it harder to identify actual problems. This breaks the intended user experience where only critical information should be shown by default.

GT 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

**finding**（`src/Tools/dotnet-dev-certs/src/Program.cs:134`，距錨點 0 行）非 verbose 模式下啟用 LogAlways 可能導致過多輸出

> 在非 verbose 模式下，將事件監聽器設為 `EventLevel.LogAlways` 會顯示所有 LogAlways 等級的事件。這可能包括原本設計為僅在 verbose 模式顯示的訊息，導致輸出過於冗長。建議確認所有 LogAlways 事件是否都適合在一般模式下顯示，或考慮使用更精確的過濾。

finding 片段：`listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways);`

## P0652

**GT**（func）Case mismatch between BundleType serialization and deserialization for Flatpak

> The Display implementation for BundleType::Flatpak returns "Flatpak" with capital 'F', while the Deserialize implementation expects lowercase "flatpak". This creates a serialization round-trip bug where serializing a Flatpak bundle type and then deserializing it will fail. Any code that serializes bundle configurations to strings (for CLI output, config files, or API responses) and then attempts to parse them back will encounter deserialization errors. This inconsistency breaks the expected behavior that Display and Deserialize should be compatible with each other.

GT 片段：`impl Display for BundleType { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ write!( ⏎ f,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 0 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，其他變體都輸出小寫（如 "deb"、"rpm"），但新增的 `Flatpak` 輸出 "Flatpak"（首字母大寫）。這可能導致序列化或比對時出現不一致，例如在產生 bundle 檔名或與其他工具互動時。建議改為 "flatpak"。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0653

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）檔案寫入前設定權限可能導致失敗

> 在 `write_and_make_executable` 中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會回傳錯誤，導致函式失敗。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0654

**GT**（rule）Legacy typing imports instead modern syntax

> The rule requires using Python 3.12+ modern type syntax (set[tuple[str, ...]] instead of Set[Tuple[str, ...]]), but the code imports and uses legacy typing module classes Set and Tuple

GT 片段：`from collections.abc import Mapping, Sequence ⏎ from typing import TYPE_CHECKING, Any, Set, Tuple ⏎ ... ⏎ def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行）型別標註使用 `Set` 與 `Tuple`，與專案慣用的 `set` 和 `tuple` 不一致

> 此處使用 `typing.Set` 和 `typing.Tuple`，但專案其他部分（如 `collections.abc` 的引入）傾向使用內建泛型。建議改用 `set` 和 `tuple` 以維持一致性。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## P0655

**GT**（func）Incorrect event level causes important certificate warnings to be suppressed in non-verbose mode

> When verbose mode is not enabled, the event listener is configured with EventLevel.LogAlways instead of the intended EventLevel.Critical. EventLevel.LogAlways (value 0) actually means all events are enabled, not just critical ones. The original PR intended to show only Critical events in non-verbose mode to suppress routine logging. This bug causes all certificate-related events including verbose debug messages to be displayed in non-verbose mode, flooding users with unnecessary output and making it harder to identify actual problems. This breaks the intended user experience where only critical information should be shown by default.

GT 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

**finding**（`src/Tools/dotnet-dev-certs/src/Program.cs:134`，距錨點 0 行）EventSource 監聽器預設啟用 LogAlways 可能影響效能

> 在非 verbose 模式下，程式碼現在會以 `EventLevel.LogAlways` 啟用事件監聽器，這可能導致大量事件被處理，影響效能。雖然 `LogAlways` 層級的事件通常較少，但若未來新增更多此層級事件，可能造成不必要的負擔。建議確認此變更的必要性，或考慮使用更精確的過濾條件。

finding 片段：`listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways);`

## P0656

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 為 null 時 SQL 條件可能導致錯誤結果

> 在 `getTeamsWithPBACPermissions` 的 SQL 中，條件 `AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})` 使用 `::bigint` 轉型。若 `orgId` 為 `null`，`${orgId}::bigint` 會是 `NULL::bigint`，`NULL IS NULL` 為 true，因此條件成立，不會過濾。但若 `orgId` 為 `undefined`，Prisma 的 `$queryRaw` 可能將其轉為 `NULL` 或產生錯誤。此外，若 `orgId` 為 0 或負數，條件可能意外匹配。建議明確處理 `orgId` 為 null/undefined 的情況，例如使用 Prisma 的條件式查詢或先判斷再決定是否加入條件。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0657

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行）新增 console.log 可能洩漏使用者批次資料

> 在 `checkBatchInputs` 函式開頭新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`。這會將使用者上傳的批次資料（包含標頭）輸出到瀏覽器主控台，可能包含敏感資訊（如使用者輸入的變數名稱或內容）。

**失敗情境**：使用者在公用電腦上操作，或使用開發者工具時，可能無意中暴露資料。

**建議**：移除這行 `console.log`，或改用適當的 logging 機制（如 debug level 且不輸出資料內容）。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## P0658

**GT**（func）Missing optional chaining causes runtime error when openForm is undefined

> The code accesses `openForm.in_reply_to_snippet` without optional chaining, but openForm can be undefined when rendering certain forms (like the main comment form). The original code correctly used `openForm?.in_reply_to_snippet` with optional chaining. This will cause a "Cannot read property 'in_reply_to_snippet' of undefined" runtime error when the FormWrapper is rendered without an openForm prop, crashing the component.

GT 片段：`let openStyles = ''; ⏎ if (isOpen) { ⏎ const isReplyToReply = !!openForm.in_reply_to_snippet; ⏎ openStyles = isReplyToReply ? 'pl-[1px] pt-[68px] sm:pl-[44px] sm:pt-[56px]' : 'pl-[1px] pt-[48px] sm:pl-[44px] sm:pt-[40px]';`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:313`，距錨點 0 行）openForm 可能為 null 時存取 in_reply_to_snippet 會拋錯

> 原本使用 `openForm?.in_reply_to_snippet` 可選串連，現在改為 `openForm.in_reply_to_snippet`。若 `openForm` 可能為 null 或 undefined，此處會拋出 TypeError。請確認 `openForm` 在此情境下是否保證非空，否則應保留可選串連或加入防護。

finding 片段：`const isReplyToReply = !!openForm.in_reply_to_snippet;`

## P0659

**GT**（func）FeatureOptInService creates isolated containers breaking dependency sharing

> The getFeatureOptInService() function creates a fresh DI container on every call, which then loads its dependencies including FeaturesRepository into that isolated container. This breaks the expected dependency injection pattern where services should share repository instances. When code calls both getFeaturesRepository() and getFeatureOptInService(), they each create separate containers with separate FeaturesRepository instances, leading to inconsistent cached state and duplicated database connections. The FeatureOptInService's repository will have different cached data than repositories retrieved elsewhere, causing unpredictable behavior in feature flag resolution.

GT 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 0 行）每次呼叫 getFeatureOptInService 都建立新容器與新服務實例

> `getFeatureOptInService` 每次呼叫都會建立新的 DI 容器並載入模組，這可能導致效能浪費，且若服務內部有狀態（例如快取），狀態不會被共享。建議考慮使用單例模式或模組層級的容器快取。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## P0660

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）`expect` 取代 fallback 可能導致 panic

> 原本的程式碼在 `name` 為 `None` 時會 fallback 到 `association.ext[0].0`，但現在改為 `expect("File association must have a name")`。如果使用者未提供 `name` 且 `ext` 為空（或 `ext` 的第一個元素不存在），程式會 panic。這會讓建置流程直接崩潰，且錯誤訊息不夠明確。

建議：保留原本的 fallback 邏輯，或改用更安全的處理方式，例如在 `ext` 為空時使用預設名稱或回傳錯誤。

finding 片段：`.expect("File association must have a name")`

## P0661

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:52`，距錨點 0 行）sortHosts 函式邏輯與原始版本不一致

> 在遷移 sortHosts 函式時，原本在 HostEditDialogs.tsx 中的實作在 `isRRWeightsEnabled` 為 true 且權重相同時回傳 `priorityB - priorityA`，但新版本回傳 `priorityA - priorityB`，導致排序方向相反。這可能影響依權重排序的主持人清單。

建議：確認此變更是否為預期，若非預期請修正為 `priorityB - priorityA`。

finding 片段：`if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else { ⏎ return weightB - weightA;`

## P0662

**GT**（rule）Missing // MARK: section organization

> The new Swift file defines multiple logical sections (nested delegate type, static helper function) but includes no `// MARK:` comments to delineate them, violating the required section organization rule.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 10 行）FakeWKNavigationDelegate 可能無法捕捉 targetFrame

> 在 decidePolicyFor navigationAction 中，navigationAction.targetFrame 可能為 nil（例如新視窗或某些重定向），此時 capturedFrame 為 nil，導致測試失敗。建議處理 targetFrame 為 nil 的情況，或使用其他 delegate 方法。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0663

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 40 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0664

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:93`，距錨點 0 行）指數成長公式在 `totalDays` 為 1 時會除以零

> 公式 `day / (this.#warmupConfig.totalDays - 1)` 在 `totalDays` 為 1 時會產生除以零的錯誤。目前預設值為 42，但若未來允許設定，需防範此狀況。

finding 片段：`day / (this.#warmupConfig.totalDays - 1)`

## P0665

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 改為非同步呼叫可能影響相依服務

> 原本 `emailAddressService.init()` 是同步呼叫（前面有 `await`），現在改為在 `Promise.all` 中非同步執行。若其他服務（如 newsletter 或 email service）依賴 email address service 初始化完成，可能導致競態條件。建議確認這些服務是否已正確處理非同步初始化。

finding 片段：`emailAddressService.init(),`

## P0666

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:93`，距錨點 0 行）指數成長公式在 `totalDays` 為 1 時會除以零

> 公式 `day / (this.#warmupConfig.totalDays - 1)` 在 `totalDays` 為 1 時會產生除以零的錯誤。目前預設值為 42，但若未來允許設定，需防範此狀況。

finding 片段：`day / (this.#warmupConfig.totalDays - 1)`

## P0667

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行）stream 的 listpack 數量計算可能多算一個

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 計算 listpack 的總大小，現在改為 `lpsize * s->rax->numele`。但 `s->rax->numele` 是 radix tree 中的元素數量，而 listpack 的數量可能與元素數量不同。若 radix tree 中的每個元素對應一個 listpack，則 listpack 數量應為 `numele`，但若最後一個 listpack 是部分填充的，則可能不應計入平均。此變更可能導致記憶體估算偏高。建議確認 stream 的資料結構，並根據實際 listpack 數量計算。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0668

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:253`，距錨點 0 行）reload_config 直接覆寫整個 ConfigMetadata 可能遺失未重新載入的欄位

> `reload_config` 現在直接以 `*config = load_config(...)` 覆寫整個結構。若 `load_config` 在解析過程中因某些原因未能完整填入所有欄位（例如新增的欄位在舊版設定檔中不存在），可能導致原本存在於 `config` 中的值被清除。建議確認 `load_config` 是否保證完整重建所有欄位，或改為僅更新必要的部分。

finding 片段：`*config = load_config(merge_configs, true, target, tauri_dir)?;`

## P0669

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2571`，距錨點 0 行）複寫指令參數順序可能錯誤

> `rewriteClientCommandVector` 的參數順序為 `(c, argc, ...)`，但此處傳入的參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。根據 HSETEX 語法，正確順序應為 `HSETEX key [KEEPTTL] FIELDS num field value`，因此 `shared.keepttl` 應在 `shared.fields` 之前，但此處 `shared.keepttl` 在 `shared.fields` 之後，可能導致複寫指令格式錯誤。

失敗情境：當主節點執行 HINCRBYFLOAT 時，複本會收到錯誤格式的 HSETEX 指令，導致複寫中斷或資料不一致。

建議修正：調整參數順序為 `shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj`。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## P0670

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）未使用的 isLandscape 變數與未調整的約束條件

> 在 `setupSkeletonAddressBarsLayout` 中新增了 `isLandscape` 變數，但後續的約束條件並未使用它，且約束條件與原本相同，沒有針對橫向模式做任何調整。這可能表示程式碼不完整，或者該變數是多餘的。如果原本意圖是根據方向調整佈局，則需要補充對應的約束邏輯；否則應移除該變數以避免混淆。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0671

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行）工具回應內容誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 ToolPromptMessage 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具呼叫的回應內容變成工具的輸入參數，而非實際的輸出結果，造成對話歷史中工具回應錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史訊息中的工具回應會顯示輸入參數而非輸出，導致後續 LLM 判斷錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0672

**GT**（rule）Trailing whitespace on line 11

> The rule requires that all staged TypeScript files pass 'biome lint --error-on-warnings' before commit, but line 11 contains trailing whitespace that would trigger a linting warning

GT 片段：`effectiveEnabled: boolean; ⏎ // Auto-opt-in flags for UI to show checkbox state ⏎ orgAutoOptIn: boolean; ⏎ teamAutoOptIns: boolean[];`

**finding**（`packages/features/feature-opt-in/services/IFeatureOptInService.ts:11`，距錨點 0 行）多餘的空白

> 在 `orgAutoOptIn: boolean;` 後面有多餘的空白，雖然不影響功能，但建議移除。

finding 片段：`orgAutoOptIn: boolean;`

## P0673

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:58`，距錨點 0 行）generate_github_alternative_url 不再回傳替代 URL

> 原本函式會回傳替代的鏡像 URL（alt_url），但修改後改為回傳原始 URL（url.to_owned()）。這可能導致 GitHub 下載失敗時無法使用鏡像，或與函式名稱及呼叫端預期不符。請確認此變更是否為刻意行為，並檢查呼叫端是否仍依賴替代 URL。

finding 片段：`url.to_owned()`

## P0674

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `useEffect` 僅在元件掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 重新取得資料）。若內容長度改變，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0675

**GT**（func）High-volume threshold boundary applies wrong scaling factor at 400k

> The condition uses `>=` instead of `>` when checking if lastCount qualifies for high-volume capping at exactly 400,000 emails. According to the documented scaling table, 400k should use the 2× multiplier from the thresholds array, but with this bug it immediately applies the high-volume cap of 1.2× or +75k absolute increase. For a site hitting exactly 400k messages, this means getting a limit of 480k (1.2×) or 475k (+75k) instead of the expected 800k (2×). This creates a significant bottleneck at a critical growth milestone and breaks the documented warmup progression.

GT 片段：`// For high volume senders (400k+), cap the increase at 20% or 75k absolute ⏎ if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold) { ⏎ const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 0 行）高流量分支可能導致目標上限低於當前值

> 在 `#getTargetLimit` 中，當 `lastCount >= 400_000` 時，計算 `scaledIncrease = Math.ceil(lastCount * 1.2)` 和 `absoluteIncrease = lastCount + 75_000`，然後取兩者最小值。但若 `lastCount` 接近 400,000，例如 400,000，則 `scaledIncrease = 480,000`，`absoluteIncrease = 475,000`，回傳 475,000，仍高於 400,000。但若 `lastCount` 為 500,000，則回傳 575,000，高於 500,000。然而，若 `lastCount` 為 400,000 且 `maxAbsoluteIncrease` 較小（例如 50,000），則可能回傳低於 `lastCount` 的值，導致目標上限倒退。目前設定下，`lastCount=400,000` 時回傳 475,000，仍高於 400,000，但若未來調整參數，可能出現倒退。建議明確確保回傳值至少為 `lastCount`，例如使用 `Math.max(lastCount, Math.min(scaledIncrease, absoluteIncrease))`。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## P0676

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:132`，距錨點 5 行）semaphore 可能未初始化而導致 RuntimeError

> `_startup_event_semaphore` 在 `initialize_clients` 中才被賦值，但 `_replicate_pod_event` 在 `event_type is None` 時直接使用它。若 `initialize_clients` 尚未被呼叫（例如啟動順序問題）或初始化失敗，`_startup_event_semaphore` 為 `None`，此處會拋出 `RuntimeError`，可能中斷事件處理。建議在 `_replicate_pod_event` 中對 semaphore 為 `None` 的情況提供更明確的處理（例如等待初始化完成或記錄錯誤後跳過），或確保初始化必定先於任何事件處理。

finding 片段：`if _startup_event_semaphore is None: ⏎ raise RuntimeError("Startup event semaphore not initialized")`

## P0677

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 19 行）XCTWaiter.wait 的結果未檢查

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0678

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）多個變數時重複 flush，可能造成效能問題

> 在 `for item in updated_variables:` 迴圈內，每次 `update` 後都呼叫 `flush()`。若有多個 conversation variable 被更新，會造成多次資料庫操作。建議將 `flush()` 移到迴圈外，或讓 `update` 累積變更後一次 flush。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0679

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行）Session 未關閉，可能導致連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但沒有呼叫 `close()` 或使用 context manager。每次呼叫都會建立新的 session，若未正確關閉，可能耗盡資料庫連線池。建議使用 `with Session(db.engine) as session:` 或確保在 finally 中關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## P0680

**GT**（rule）Missing trailing newline at end of file

> Biome formatting conventions require LF line endings and proper file termination. This file is missing the final newline, as indicated by the diff marker.

GT 片段：`export default EventRecurringWebWrapper; ⏎ \ No newline at end of file`

**finding**（`apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8`，距錨點 0 行）檔案缺少結尾換行

> 檔案最後一行 `export default EventRecurringWebWrapper;` 沒有換行符號，可能導致某些工具或 linter 警告。建議補上換行。

finding 片段：`export default EventRecurringWebWrapper;`

## P0681

**GT**（rule）Non-strict inequality operator used

> The rule requires using strict equality operators (=== or !==) for all comparisons, but the code uses != instead of !== to check if count is null

GT 片段：`const count = result.data[0].get('csd_email_count'); ⏎ return count != null ? count : 0;`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:101`，距錨點 10 行）`findPage` 回傳值可能未定義 `data` 屬性，導致執行時期錯誤

> `#getHighestCount` 改為呼叫 `findPage` 後，直接存取 `result.data.length`。若 `findPage` 的實作在某些情況下（例如資料庫錯誤、回傳格式不符）未提供 `data` 陣列，將拋出 `TypeError`。建議先檢查 `result` 與 `result.data` 是否存在，或使用選用鏈結（`result?.data?.length`）並提供預設值。

finding 片段：`const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC', ⏎ limit: 1`

## P0682

**GT**（func）Unused isPending variable causes no loading state during data fetch

> The component destructures isPending from useTeamMembersHook but never uses it to show a loading state to users. When assignRRMembersUsingSegment is enabled and the component fetches matching team members from the server, users see stale or incomplete data without any indication that fresh data is loading. This creates a poor user experience where the UI appears unresponsive during network requests, and users may make decisions based on outdated team member information before the segment filtering completes.

GT 片段：`const { teamMembers, localWeightsInitialValues, isPending } = useTeamMembersHook({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ teamId,`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:128`，距錨點 0 行）isPending 未用於載入狀態

> 從 `useTeamMembersHook` 解構出 `isPending`，但未在 UI 中使用。當資料載入中時，使用者可能看到舊資料或空白，且無法得知載入狀態。

**建議**：使用 `isPending` 來顯示載入指示器或停用相關按鈕。

finding 片段：`const { teamMembers, localWeightsInitialValues, isPending } = useTeamMembersHook({`

## P0683

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 輸出日誌

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將訊息輸出到標準輸出，可能污染正式環境的日誌或影響效能。建議改用 logging 模組，並設定適當的日誌層級。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0684

**GT**（func）Async test assertion never verified due to missing expectation

> The test was updated to use @Sendable closures for Swift 6 concurrency compliance, but the expectation and wait statements were removed. The test now completes immediately without waiting for the asynchronous requestMediaCapturePermission callback. The XCTAssertEqual inside the decisionHandler closure will never execute, causing the test to always pass even when the media capture permission logic is broken. This is particularly problematic because this test validates critical permission handling behavior.

GT 片段：`func testRequestMediaCaptureSuccess() { ⏎ let subject = createSubject(isActive: true) ⏎ let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt)`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:35`，距錨點 0 行）移除 expectation 可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，原本使用 `expectation` 等待 decision handler 被呼叫，但修改後移除了 expectation 的建立與等待，且未使用 `wait(for:)`。這可能導致測試方法在非同步回呼執行前就返回，使得測試永遠通過，無法驗證實際行為。建議保留 expectation 或改用 `wait(for:)` 來等待非同步操作。

finding 片段：`func testRequestMediaCaptureSuccess() { ⏎ let subject = createSubject(isActive: true) ⏎  ⏎ let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in`

## P0685

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 6 行）搜尋過濾與後端查詢重複，可能造成不一致

> 元件同時使用 `useSuspenseQuery` 的 `deferredSearch` 參數進行後端過濾，又在 `filteredData` 中進行前端過濾。這可能導致當後端過濾與前端過濾條件不同時，顯示的結果不一致。例如後端可能因為大小寫或模糊比對而回傳不同結果，前端又再過濾一次。

**失敗情境**：使用者輸入搜尋字串，後端回傳了符合的區塊文件，但前端過濾因為大小寫敏感而將某些結果排除，導致使用者看不到實際上符合的選項。

**建議**：統一過濾邏輯，要嘛完全依賴後端查詢，要嘛完全在前端過濾，避免雙重過濾造成混淆。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0686

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行）Popover 的 hover 與 click 互動可能導致無法關閉

> 在桌面端，Popover 的開啟由 onMouseEnter 觸發，關閉由 onMouseLeave 觸發。但 Popover 本身也受 onOpenChange 控制，當使用者點擊 trigger 按鈕時，Popover 會切換 open 狀態，但 mouse enter/leave 事件可能不會如預期觸發，導致 popover 卡在開啟狀態。建議移除自訂的 mouse enter/leave 處理，改用 Popover 內建的 hover 模式（例如設定 trigger="hover"），或明確處理 click 與 hover 的狀態轉換。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0687

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）當 max_length 未定義時，長度檢查可能失效

> 在 `varItem.max_length` 為 `undefined` 時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果為 `false`，因此不會觸發錯誤。這可能導致使用者提交超長文字，造成後端處理問題或資料截斷。建議在 max_length 未定義時，使用合理的預設值或明確跳過檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0688

**GT**（rule）Default export used in non-page/layout component file

> Rule allows default exports only in Next.js page/layout files. This component wrapper file exports a default export, violating the named-export requirement.

GT 片段：`export default EventRecurringWebWrapper;`

**finding**（`apps/web/modules/event-types/components/tabs/recurring/EventRecurringWebWrapper.tsx:8`，距錨點 0 行）檔案缺少結尾換行

> 檔案最後一行 `export default EventRecurringWebWrapper;` 沒有換行符號，可能導致某些工具或 linter 警告。建議補上換行。

finding 片段：`export default EventRecurringWebWrapper;`

## P0689

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:13`，距錨點 0 行）全域 mock 行為變更可能影響未修改的測試

> 全域 mock 原本在沒有 namespace 時直接回傳 key，現在改為一律加上 namespace 前綴（若存在）。這會改變所有依賴全域 mock 的測試行為，可能導致大量測試失敗。建議先執行完整測試套件確認影響範圍，或考慮保留舊行為作為預設，僅在需要時才加上前綴。

finding 片段：`const fullKey = ns ? `${ns}.${key}` : key`

## P0690

**GT**（func）Race condition: semaphore initialized after clients during startup

> The `_startup_event_semaphore` is initialized after the orchestration and events clients are created and started. This creates a race condition where Kubernetes pods detected during the client startup phase can trigger `_replicate_pod_event` calls before the semaphore exists. When `event_type` is `None` (startup scenario), the code checks `if _startup_event_semaphore is None` and raises a RuntimeError. However, pods may be detected immediately after clients start but before the semaphore initialization completes, causing the observer to crash with 'Startup event semaphore not initialized' errors during high pod count scenarios.

GT 片段：`@kopf.on.startup() ⏎ async def initialize_clients(logger: kopf.Logger, **kwargs: Any): ⏎ logger.info("Initializing clients") ⏎ global events_client`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:63`，距錨點 0 行）semaphore 初始化可能失敗但未處理

> `asyncio.Semaphore(settings.observer.startup_event_concurrency)` 若 `startup_event_concurrency` 為負數或非整數（例如設定錯誤），會拋出 `ValueError` 或 `TypeError`，導致 `initialize_clients` 失敗。建議在初始化時驗證設定值，或提供更明確的錯誤訊息。

finding 片段：`_startup_event_semaphore = asyncio.Semaphore( ⏎ settings.observer.startup_event_concurrency ⏎ )`

## P0691

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行）linuxdeploy 下載 URL 中的 arch 變數可能錯誤

> 在 `prepare_tools` 中，原本的 linuxdeploy 下載 URL 使用 `linuxdeploy_arch`（其中 i686 被替換為 i383），但此 PR 將其改為直接使用 `arch`。這可能導致在 i686 架構下下載錯誤的檔案（i686 而非 i383），造成後續執行失敗。

建議確認 `linuxdeploy` 的實際發布架構命名，並保留原本的 `linuxdeploy_arch` 邏輯。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0692

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 0 行）dev 模式下 versionCode 的 clamp 順序可能導致非預期結果

> 在 dev 模式下，程式先檢查 `version_code == 0` 和 `> 2100000000` 並回傳錯誤，然後才執行 `clamp(1, 2100000000)`。這表示如果 semver 計算出的 `version_code` 超過上限，dev 模式會直接失敗，而不是被 clamp 到上限。原本在 `tauri-build` 中的邏輯是先 clamp 再檢查，行為可能不一致。建議確認預期行為，並調整順序或移除重複檢查。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## P0693

**GT**（func）Unsafe concurrency annotation on non-thread-safe static property

> The static generator property is marked with nonisolated(unsafe) despite the comment explicitly stating 'ContentBlockerGenerator is not thread safe'. This annotation bypasses Swift 6's concurrency safety checks and allows the non-thread-safe ContentBlockerGenerator to be accessed from multiple isolation domains without protection. This creates a potential data race condition where multiple threads could access the generator simultaneously, leading to undefined behavior, crashes, or data corruption. The unsafe annotation should only be used when the developer can guarantee thread safety through other means, which the comment explicitly contradicts.

GT 片段：`@main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏資料競爭

> 將 `generator` 標記為 `nonisolated(unsafe)` 表示開發者手動保證其執行緒安全，但註解中明確指出 `ContentBlockerGenerator` 並非執行緒安全。若此靜態屬性被多個執行緒同時存取，可能導致資料競爭或未定義行為。建議確認 `ContentBlockerGenerator.factory()` 的回傳值是否真的不可變且內部狀態安全，或考慮使用鎖定、actor 或其他同步機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0694

**GT**（func）Experimental V2 UI enabled by default

> The default value for v2_enabled is set to True, making the experimental V2 UI the default instead of the stable V1 UI. This is problematic because the PR description indicates V2 is experimental and should be opt-in. Users who upgrade will unexpectedly get the experimental UI by default, potentially encountering bugs, incomplete features, or breaking changes. The setting should default to False to maintain backward compatibility and allow users to explicitly opt into the experimental V2 UI.

GT 片段：`v2_enabled: bool = Field( ⏎ default=True, ⏎ description="Whether to serve the experimental V2 UI instead of the default V1 UI.", ⏎ )`

**finding**（`src/prefect/settings/models/server/ui.py:22`，距錨點 0 行）V2 UI 預設啟用可能導致未建置時服務失敗

> 新增的 `v2_enabled` 設定預設為 `True`，但 V2 UI 的靜態檔案只有在執行建置步驟（如 Docker 建置或 CI 中的 `npm run build`）後才會存在。若使用者直接從原始碼安裝或未執行建置，伺服器啟動時會嘗試複製不存在的 `src/prefect/server/ui-v2` 目錄，導致 `FileNotFoundError` 或服務無法提供 UI。

**失敗情境**：開發者以 `pip install -e .` 安裝後直接執行 `prefect server start`，未先建置 V2 UI，此時 `source_static_path` 指向不存在的目錄，`copy_directory` 將拋出例外。

**建議**：將預設值改為 `False`，或加入檢查：若 V2 目錄不存在則自動回退至 V1，並記錄警告。

finding 片段：`v2_enabled: bool = Field( ⏎ default=True, ⏎ description="Whether to serve the experimental V2 UI instead of the default V1 UI.", ⏎ )`

## P0695

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:100`，距錨點 0 行）移除 userSelect 中的 locale 可能導致取消流程缺少 locale

> 在 `userSelect` 中移除了 `locale: true`，但取消流程中 `handler` 會使用 `organizer.locale` 來取得翻譯：`const tOrganizer = await getTranslation(organizer.locale ?? "en", "common");`。若 `UserRepository.findByIdOrThrow` 使用此 `userSelect`，則回傳的 organizer 物件將沒有 `locale` 屬性，導致 `organizer.locale` 為 `undefined`，最終 fallback 到 `"en"`，可能造成非英語使用者的通知或錯誤訊息語言不正確。建議確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 locale 則應保留，或改用其他方式取得。

finding 片段：`completedOnboarding: true, ⏎ timeFormat: true,`

## P0696

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行）merge_with 中移除了對合併後設定的反序列化，可能導致後續使用到過期資料

> 原本的程式碼會將合併後的 JSON 值反序列化回 `Config` 結構並更新 `config_metadata.inner`。修改後僅將合併設定插入 `extensions`，但 `inner` 並未更新。這可能導致後續使用 `config_metadata.inner` 時取得的是未合併的舊設定，造成行為不一致。

建議保留反序列化步驟，或明確說明為何不再需要更新 `inner`。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## P0697

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32`，距錨點 18 行）useState 初始化依賴 account 可能導致狀態不同步

> `const [loading, setLoading] = useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed);` 使用 lazy initializer，但 `account` 可能在元件掛載後才載入，導致初始 loading 狀態不正確。若 `account` 初始為 undefined，loading 會是 false，之後 account 載入後，useEffect 會設定 loading，但可能造成閃爍。建議在 account 載入後再根據其值設定 loading，或使用 useEffect 同步。

finding 片段：`const [loading, setLoading] = useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed);`

## P0698

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:342`，距錨點 23 行）快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，程式使用 `for tenant_id, subscription_plan in bulk_plans.items()` 來寫入快取，但 `bulk_plans` 是 `get_plan_bulk` 的回傳值，其中可能包含 `None`（若 `get_plan_bulk` 將無效 tenant 設為 `None`）。這會導致將 `None` 序列化為 JSON 字串 `"null"` 存入 Redis，之後讀取時會因驗證失敗而再次視為 cache miss，但已污染快取。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，程式將 `None` 寫入 Redis，下次讀取時 `json.loads` 得到 `None`，`validate_python` 失敗，該 tenant 永遠無法命中快取。

**建議**：改為迭代 `plans_to_cache`，或先過濾掉 `None` 值。

finding 片段：`for tenant_id, subscription_plan in bulk_plans.items(): ⏎ redis_key = cls._make_plan_cache_key(tenant_id) ⏎ # Serialize dict to JSON string ⏎ json_str = json.dumps(subscription_plan)`

## P0699

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:462`，距錨點 0 行）V2 啟用時仍使用 V1 的 static_subpath

> 在 `v2_enabled` 為 True 時，`static_subpath` 仍被指派為 `prefect.__ui_static_subpath__`（V1 的路徑），而非 `prefect.__ui_v2_static_subpath__`。這會導致 `create_ui_static_subpath` 將 V2 的靜態檔案複製到 V1 的子目錄，可能覆蓋 V1 檔案或造成路徑衝突。

**失敗情境**：當使用者設定 `PREFECT_SERVER_UI_V2_ENABLED=true` 且未設定 `PREFECT_UI_STATIC_DIRECTORY` 時，伺服器會將 V2 檔案複製到 `server/ui_build`（V1 的動態目錄），而 V1 的靜態檔案可能仍存在，導致服務內容混亂或找不到正確資源。

**建議**：將 `static_subpath` 指派為 `prefect.__ui_v2_static_subpath__`。

finding 片段：`static_subpath = prefect.__ui_static_subpath__`

## P0700

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1727`，距錨點 0 行）aof-load-broken-max-size 為 0 時可能導致截斷邏輯失效

> 當 `aof-load-broken-max-size` 設定為 0 時，條件 `(size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size` 永遠為 false，因此不會截斷，但程式仍會記錄警告並繼續執行。這可能讓使用者誤以為已啟用自動修復，但實際上未生效。建議在設定為 0 時視為停用此功能。

finding 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`
