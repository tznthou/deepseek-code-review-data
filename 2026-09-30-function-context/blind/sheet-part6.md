# 盲標單 6：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part6.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0501

**GT**（func）Memory leak due to missing error message reply to client

> In parseSlotRangesOrReply, when slot range validation fails, the error message allocated by slotRangeArrayNormalizeAndValidate is freed with sdsfree(err) but never sent to the client via addReplyErrorSds. This causes two problems: the client receives no error message explaining why their command failed, making debugging difficult, and it breaks the expected behavior where addReplyErrorSds transfers ownership of the sds string. The original PR intended to always send validation errors to the client for proper error reporting.

GT 片段：`sds err = NULL; ⏎ if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots);`

**finding**（`src/cluster.c:2015`，距錨點 0 行）parseSlotRangesOrReply 錯誤路徑未回覆錯誤訊息

> 原本在 validateSlotRanges 失敗時會呼叫 addReplyErrorSds(c, err) 回覆錯誤，現在改為 sdsfree(err) 後直接回傳 NULL，未回覆任何錯誤給客戶端。這可能導致客戶端收到空回覆或連線中斷，而非明確的錯誤訊息。建議保留 addReplyErrorSds 或改為 addReplyError(c, err)。

finding 片段：`if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots); ⏎ return NULL;`

## P0502

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 15 行）移除 noTimestamp 選項可能導致 token 包含 iat 欄位

> 原本 `jwt.sign` 使用 `{noTimestamp: true}` 來避免在 payload 中加入 `iat`（issued at）欄位，現在移除了該選項，因此產生的 token 會包含 `iat`。這可能影響 token 的驗證邏輯或與其他系統的相容性，但通常不會造成直接問題。若無特定理由，建議保留 `noTimestamp: true` 以維持原有行為。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0503

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0504

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題

> 新增的 `SettingsTextFormatter` 使用 singleton 模式，但沒有明顯的必要性。如果這個類別只包含無狀態的方法，可以考慮使用靜態方法，避免不必要的 singleton。另外，如果未來加入狀態，需注意執行緒安全。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0505

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行）assert smtp is not None 可能被最佳化移除

> 新增的 `assert smtp is not None` 在 Python 最佳化模式（-O）下會被移除，且此處 smtp 必定不為 None，因為建構子已指派。此 assert 無實際作用，建議移除。

finding 片段：`assert smtp is not None`

## P0506

**GT**（func）Missing dependency in useEffect causes stale clamp detection

> The CommentContent component's useEffect hook has an empty dependency array, but it uses item.html to determine if content should be clamped. When a comment's HTML content changes (e.g., after an edit or when new data is loaded), the clamp detection won't re-run. This means the 'Show more' button may appear when it shouldn't or disappear when it should still be visible, creating a poor user experience. The dependency array should include item.html to ensure the clamp detection re-runs whenever the content changes.

GT 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 依賴陣列為空，可能無法正確偵測內容截斷

> `useEffect` 僅在掛載時執行一次，若 `item.html` 內容在掛載後變更（例如虛擬滾動重用元件），`isClamped` 可能不會更新。建議將 `item.html` 加入依賴陣列，或使用 ResizeObserver 監測內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0507

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 15 行）emailAddressService.init() 從同步呼叫改為 Promise.all 內的非同步呼叫，可能影響依賴它的服務初始化順序

> 原本 `await emailAddressService.init()` 是同步等待完成後才進行後續的 Promise.all，現在改成在 Promise.all 內與其他服務並行初始化。如果其他服務（如 newsletter service 或 email service）依賴 emailAddressService 初始化完成，可能會因為並行執行而產生競態條件。建議確認這些服務的依賴關係，若有必要，應保留 emailAddressService.init() 的 await 順序，或將依賴它的服務也放入同一個 Promise.all 中並確保順序。

finding 片段：`emailAddressService.init(),`

## P0508

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行）程式碼格式：`position` 參數間缺少空格

> `position(position.x,position.y)` 中逗號後缺少空格，與專案慣例不符。建議改為 `position(position.x, position.y)`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## P0509

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:117`，距錨點 26 行）使用 `||` 可能錯誤地將 0 或空字串顯示為 'None'

> 在 `Run Count` 欄位中，`{taskRun.run_count || 0}` 會將 `run_count` 為 0 時顯示為 0，這是正確的。但其他欄位如 `Cache Key` 使用 `{taskRun.cache_key || "None"}`，若 `cache_key` 為空字串（合法值），會顯示 'None'，可能造成誤導。建議改用 `??` 運算子來區分 `null`/`undefined` 與其他 falsy 值。

finding 片段：`<dd className="font-mono">{taskRun.cache_key || "None"}</dd>`

## P0510

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行）條件邏輯變更可能影響既有行為

> 原本條件為 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示即使沒有 pending invite，只要 `onboardingV3Enabled` 為 true，就會 redirect 到 `/onboarding/personal/settings`。這可能是預期行為，但需確認是否會影響其他流程。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) {`

## P0511

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）slot_buffer 分配後未檢查 malloc 失敗

> `slot_buffer = malloc(sizeof(int) * keys_result->numkeys);` 未檢查回傳值是否為 NULL。若記憶體不足，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議加入檢查：
```c
int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);
if (!slot_buffer) return INVALID_CLUSTER_SLOT;
```

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0512

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）未處理 ConversationVariableNotFoundError

> `self._conversation_variable_updater.update(...)` 可能拋出 `ConversationVariableNotFoundError`，但此處未捕捉。若變數在資料庫中不存在，整個 workflow 會失敗。需確認此行為是否符合預期，或應記錄錯誤並繼續。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable)`

## P0513

**GT**（func）Token caching stores entire object instead of token string

> In the getToken method, when caching the JWT token, the code now stores the entire tokenData object (containing both 'token' and 'exp' properties) instead of just extracting the token string. This causes the returned token structure to be malformed as {token: {token: string, exp: number}, exp: number} instead of the expected {token: string, exp: number}. This will break any consumers of the Tinybird API (like the /api/tinybird/token endpoint and stats/tinybird.js) that expect a string token value, causing authentication failures when making requests to Tinybird pipes.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）_serverToken 型別不一致可能導致 JWT 驗證失敗

> 在 `getServerToken` 中，原本 `this._serverToken = tokenData.token` 儲存的是字串，但現在改為 `this._serverToken = tokenData` 儲存整個物件。然而，後續使用 `this._serverToken` 的地方（例如 `_isJWTExpired(this._serverToken)` 或回傳給呼叫端）仍預期它是字串。這會導致 `jwt.decode` 收到物件而非字串，可能拋出錯誤或回傳 null，進而使 token 永遠被視為過期，每次請求都重新產生 token，造成效能問題或功能失效。

建議：維持 `this._serverToken = tokenData.token`，或同步修改所有使用 `_serverToken` 的地方以處理物件型別。

finding 片段：`this._serverToken = tokenData;`

## P0514

**GT**（rule）Line length exceeds SwiftLint limit

> This added/modified line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextStudies = NSLocalizedString("Settings.detailTextStudies", value: "%@ may install and run studies from time to time.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focus\" or \"Firefox Klar\").")`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:203`，距錨點 2 行）新增的 V2 字串可能未被使用

> 新增了 `detailTextSendUsageDataV2`、`labelStudiesV2`、`detailTextStudiesV2` 等靜態屬性，但在這個 diff 中沒有看到任何使用它們的程式碼。如果這些字串是為了未來的功能預留，建議確認是否有對應的 PR 會使用它們，否則可能造成無用的程式碼。

finding 片段：`static let detailTextSendUsageDataV2 = NSLocalizedString("Settings.detailTextSendUsageData.v2", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for exampl`

## P0515

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行）單筆 booking 的 acceptedBookings 舊狀態硬編碼為 ACCEPTED

> 在非 recurring 的單筆 booking 確認流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 尚未更新，其狀態應為 PENDING（或先前的狀態）。這會導致 audit log 中的 `status.old` 永遠是 ACCEPTED，而非實際的舊狀態，造成 audit 資料不正確。

建議：在更新前先取得 booking 的舊狀態，例如從 `booking.status` 取得，並使用該值。

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## P0516

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:378`，距錨點 13 行）過度寬泛的例外處理可能隱藏真實錯誤

> 在解析 SSL_CERT_DIR 中的每個目錄時，使用 `catch` 捕捉所有例外並忽略，可能掩蓋了非預期的錯誤（例如 `Path.GetFullPath` 因權限不足或路徑格式錯誤而拋出的例外）。建議至少記錄例外資訊，或僅捕捉預期的例外類型（如 `ArgumentException`、`NotSupportedException`、`PathTooLongException`）。

finding 片段：`catch ⏎ { ⏎ // Ignore invalid directory entries in SSL_CERT_DIR ⏎ return false;`

## P0517

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 6 行）dev 模式下 versionCode 的 clamp 順序可能導致非預期結果

> 在 dev 模式下，程式先檢查 `version_code == 0` 和 `> 2100000000` 並回傳錯誤，然後才執行 `clamp(1, 2100000000)`。這表示如果 semver 計算出的 `version_code` 超過上限，dev 模式會直接失敗，而不是被 clamp 到上限。原本在 `tauri-build` 中的邏輯是先 clamp 再檢查，行為可能不一致。建議確認預期行為，並調整順序或移除重複檢查。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## P0518

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或未對齊

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 會將記憶體初始化為零，而 malloc 不會。若後續程式碼假設 slot stats 已歸零（例如 resetClusterStats() 可能只重置部分欄位），可能導致未定義行為或錯誤的統計數據。建議改回 zmalloc 或使用 zcalloc。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0519

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:93`，距錨點 7 行）指數成長公式在 `totalDays` 為 1 時會除以零

> 公式 `day / (this.#warmupConfig.totalDays - 1)` 在 `totalDays` 為 1 時會產生除以零的錯誤。目前預設值為 42，但若未來允許設定，需防範此狀況。

finding 片段：`day / (this.#warmupConfig.totalDays - 1)`

## P0520

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）未使用的 isLandscape 變數與未調整的約束條件

> 在 `setupSkeletonAddressBarsLayout` 中新增了 `isLandscape` 變數，但後續的約束條件並未使用它，且約束條件與原本相同，沒有針對橫向模式做任何調整。這可能表示程式碼不完整，或者該變數是多餘的。如果原本意圖是根據方向調整佈局，則需要補充對應的約束邏輯；否則應移除該變數以避免混淆。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0521

**GT**（rule）Line exceeds 110-character limit

> This newly added union member type definition is on a single line and exceeds the 110 character line-width limit mandated by Biome configuration.

GT 片段：`| { teamId: number; featureId: FeatureId; state: "enabled" | "disabled"; assignedBy: number; scope?: OptInFeatureScope }`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:264`，距錨點 20 行）setUserFeatureState 條件判斷反轉，導致 enabled/disabled 狀態不會被寫入

> 原本的邏輯是 `if (state === "inherit")` 才呼叫 `setUserFeatureState`，否則走 `assignedBy` 分支。但此 PR 將條件改為 `if (state !== "inherit")`，使得當 state 為 `enabled` 或 `disabled` 時，會進入原本處理 `inherit` 的 else 分支，而該分支會嘗試從 input 取得 `assignedBy`，但 input 型別中 `assignedBy` 是必要的，因此可能不會立即出錯，但邏輯完全相反。

**失敗情境**：使用者嘗試將功能設為 enabled 或 disabled 時，實際呼叫的是 `setUserFeatureState({ userId, featureId, state })`，但這個呼叫缺少 `assignedBy`，可能導致 repository 層錯誤或資料不一致。

**建議修法**：改回 `if (state === "inherit")`。

finding 片段：`if (state !== "inherit") { ⏎ await this.featuresRepository.setUserFeatureState({ userId, featureId, state }); ⏎ } else { ⏎ const { assignedBy } = input;`

## P0522

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）條件判斷邏輯反轉，導致鎖定版本解析錯誤

> 原本的條件 `lock.is_some() && crate_lock_packages.is_empty()` 在 lock 存在且 crate_lock_packages 為空時執行，但修改後變成 `lock.is_some() && !crate_lock_packages.is_empty()`，邏輯完全相反。這會導致當 lock 存在且 crate_lock_packages 有值時才進入此區塊，但此區塊的目的是在找不到 crate 時從 lock 中取得版本，因此應在 crate_lock_packages 為空時執行。此錯誤可能造成版本解析失敗或回傳錯誤版本。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0523

**GT**（func）Validation incorrectly rejects proactive triggers with automation_triggered_event_id

> The field_validator for automation_triggered_event_id prevents setting this field when triggering_event is None. However, proactive triggers (which have no triggering_event) still create automation.triggered events and need to link actions to them via automation_triggered_event_id. The code in triggers.py sets automation_triggered_event_id=primary_state_change_event_id for all actions including proactive triggers, causing Pydantic validation to fail at runtime. This breaks all proactive automations, which is a critical functional regression.

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行）field_validator 可能無法正確取得 triggering_event

> `validate_automation_triggered_event_id` 使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 包含已驗證的欄位，但若 `triggering_event` 在 `automation_triggered_event_id` 之後才被驗證，則可能尚未存在於 `info.data` 中，導致驗證失敗或誤判。

**失敗情境**：若欄位驗證順序導致 `triggering_event` 尚未被處理，則即使 `triggering_event` 實際存在，驗證器也可能拋出錯誤。

**建議修法**：改用 `info.data.get("triggering_event")` 或使用 `model_fields_set` 來檢查欄位是否已設定。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## P0524

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 8 行）getRecordings 呼叫缺少 await，可能回傳未解析的 Promise

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫移除了 `await`。若 `getRecordings` 是非同步方法（從其他端點如 `getVideoSessions` 使用 `await` 可推測），則回傳的 `recordings` 會是 Promise 物件而非實際資料，導致 API 回傳錯誤的資料型態或序列化失敗。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件，而非錄製陣列，可能造成客戶端解析錯誤或資料外洩。

**建議**：恢復 `await`，改為 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0525

**GT**（func）Thread safety violation calling @MainActor completion handler from background thread

> In the handleServerTrust method, when SSL/TLS certificate validation fails (guard else clause), the @MainActor-isolated completionHandler is called directly from the background dispatchQueue without using ensureMainThread wrapper. This violates Swift Concurrency's actor isolation and can cause runtime crashes or data races. The success path correctly wraps the completion call in ensureMainThread, but the failure path at line 1343 does not, creating inconsistent thread safety behavior.

GT 片段：`func handleServerTrust( ⏎ challenge: URLAuthenticationChallenge, ⏎ dispatchQueue: DispatchQueueInterface, ⏎ completionHandler: @escaping @MainActor (URLSession.AuthChallengeDisposition, URLCredential?) -> Void`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1339`，距錨點 0 行）handleServerTrust 中移除 ensureMainThread 可能導致 completionHandler 在背景執行緒呼叫

> 在 `handleServerTrust` 的 else 分支中，原本使用 `ensureMainThread` 來確保 `completionHandler` 在主執行緒執行，但修改後直接呼叫 `completionHandler(.performDefaultHandling, nil)`。由於此方法可能在背景執行緒（dispatchQueue.async）中執行，直接呼叫可能導致 UI 更新或狀態變更不在主執行緒，違反 @MainActor 隔離。建議保留 `ensureMainThread` 或改用 `DispatchQueue.main.async`。

finding 片段：`guard let trust = challenge.protectionSpace.serverTrust, ⏎ let cert = SecTrustCopyCertificateChain(trust) as? [SecCertificate], ⏎ self.profile.certStore.containsCertificate(cert[0], forOrigin: origin) ⏎ else {`

## P0526

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:231`，距錨點 16 行）輪詢邏輯變更：先 sleep 再檢查狀態，可能延遲最終結果

> 原本的輪詢迴圈先讀取 flow run 狀態，若未完成則 sleep；現在改為先 sleep 再讀取。這會導致即使 flow run 在第一次檢查前已完成，也會等待 `poll_interval` 秒後才回傳。

**失敗情境**：當 `timeout` 設定較小且 `poll_interval` 較大時，可能超過 timeout 才回傳，或延遲回傳已完成的结果。

**建議**：恢復先檢查再 sleep 的順序，或使用 `anyio.move_on_after` 搭配更精確的輪詢。

finding 片段：`await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

## P0527

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行）單一預約接受時 acceptedBookings 的 oldStatus 固定為 ACCEPTED

> 在非 recurring 的接受流程中，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時預約尚未更新，其狀態應為 PENDING（或先前的其他狀態）。這會導致 audit log 中記錄的狀態變更不正確（old 與 new 皆為 ACCEPTED）。

建議改為使用更新前的 `booking.status`，例如：
```ts
acceptedBookings = [{ oldStatus: booking.status, uid: booking.uid }];
```

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## P0528

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38`，距錨點 0 行）Redirect 方法可能使用 null 的 InteractiveRequestUrl

> 在 `Redirect` 方法中，原本的條件是 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null`，現在改為只檢查 `_tokenResult.InteractionOptions != null`。若 `InteractionOptions` 不為 null 但 `InteractiveRequestUrl` 為 null，則會呼叫 `_navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, ...)`，可能導致 null 參數例外。建議保留對 `InteractiveRequestUrl` 的 null 檢查，或確保兩者同時存在。

finding 片段：`if (_tokenResult.InteractionOptions != null) ⏎ { ⏎ _navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, _tokenResult.InteractionOptions); ⏎ }`

## P0529

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行）讀取 tauri.properties 失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或無法解析時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致在檔案遺失或格式錯誤時，版本碼意外重置，造成已發布的應用程式無法更新。建議在 `auto_increment_version_code` 為 true 且檔案不存在時，回傳錯誤或至少發出警告，而不是靜默重置。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0530

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 0 行）readerModeState 的 isEnabled 判斷反轉可能導致錯誤的遙測事件

> 原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會讓 `readerModeButtonTapped` 的 `isEnabled` 參數傳入相反的值，導致遙測數據錯誤。例如，當 Reader Mode 可用時，原本應記錄為 enabled，現在卻記錄為 disabled。請確認此變更是否為預期行為，若非必要請回復。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## P0531

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:26`，距錨點 11 行）建構子未驗證 code_executor 型別，可能導致執行期錯誤

> `CodeExecutorJinja2TemplateRenderer.__init__` 接受 `code_executor` 參數，但未驗證其是否為 `CodeExecutor` 的子類別。若傳入錯誤型別，呼叫 `execute_workflow_code_template` 時會拋出 `AttributeError`，且此錯誤未被包裝成 `TemplateRenderError`，可能造成難以除錯的例外。建議在建構子中檢查型別或使用更明確的型別提示。

finding 片段：`def __init__(self, code_executor: type[CodeExecutor] | None = None) -> None: ⏎ self._code_executor = code_executor or CodeExecutor`

## P0532

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行）移除 recurring seated bookings 的排序可能導致輸出順序不穩定

> 原本 `getOutputRecurringSeatedBookings` 會依開始時間排序，但此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳的預訂順序不固定，影響前端顯示或測試的穩定性。若排序不再需要，請確認呼叫端能接受任意順序；否則應保留排序。

finding 片段：`return transformed;`

## P0533

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:342`，距錨點 38 行）快取寫入使用 bulk_plans 而非 plans_to_cache，可能快取到無效資料

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，程式使用 `for tenant_id, subscription_plan in bulk_plans.items()` 來寫入快取，但 `bulk_plans` 是 `get_plan_bulk` 的回傳值，其中可能包含 `None`（若 `get_plan_bulk` 將無效 tenant 設為 `None`）。這會導致將 `None` 序列化為 JSON 字串 `"null"` 存入 Redis，之後讀取時會因驗證失敗而再次視為 cache miss，但已污染快取。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，程式將 `None` 寫入 Redis，下次讀取時 `json.loads` 得到 `None`，`validate_python` 失敗，該 tenant 永遠無法命中快取。

**建議**：改為迭代 `plans_to_cache`，或先過濾掉 `None` 值。

finding 片段：`for tenant_id, subscription_plan in bulk_plans.items(): ⏎ redis_key = cls._make_plan_cache_key(tenant_id) ⏎ # Serialize dict to JSON string ⏎ json_str = json.dumps(subscription_plan)`

## P0534

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 8 行）測試依賴真實網路，可能不穩定

> `captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或不穩定，導致測試逾時或失敗。

建議改用本地 HTML 字串或 `data:` URL 來避免外部依賴，或使用 `WKWebView` 的 `loadHTMLString` 方法。

finding 片段：`webView.load(URLRequest(url: url))`

## P0535

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 tool_call_response 的 content 是 `tool_responses.get(tool, agent_thought.observation)`，但此 PR 改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給使用者的工具回應內容變成工具的輸入參數，而非實際的觀察結果，造成資料錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，使用者看到的將是輸入參數而非工具輸出。

建議：改回使用 `tool_responses`，並移除不必要的 `str()` 轉換（若原本就是字串）。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0536

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 和 eventTypeId 的型別與格式。若呼叫端傳入錯誤型別（例如 schedule 不是二維陣列、eventTypeId 不是數字），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0537

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）導航順序調整可能影響測試穩定性

> 原本先執行 navigator.goto(NewTabScreen) 再點擊 Done，現在改為先點擊 Done 再執行 navigator.goto(NewTabScreen)。若點擊 Done 後畫面狀態改變，可能導致後續的 navigator.goto 失敗。請確認此調整是否為了解決特定問題，並確保測試仍能穩定通過。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0538

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68`，距錨點 15 行）confirmHandle 的錯誤處理可能導致未處理的 rejection

> `confirmHandle` 使用 `.then()` 但沒有 `.catch()`。若 `confirmBlueskyHandleMutation.mutateAsync()` 失敗（例如網路錯誤），會產生未處理的 Promise rejection。建議加入 `.catch()` 處理錯誤，或使用 try/catch。

finding 片段：`const confirmHandle = useCallback(() => { ⏎ confirmBlueskyHandleMutation.mutateAsync().then((handle) => { ⏎ if (handle) { ⏎ setHandleConfirmed(true);`

## P0539

**GT**（func）JSON schema validation uses non-normalized value

> The validation logic for jsonObject type validates jsonSchemaValue instead of normalizedJsonSchema. This is problematic because normalizedJsonSchema is computed earlier and correctly handles the case where an empty schema should be undefined. By validating jsonSchemaValue directly, the code validates the raw tempPayload value instead of the cleaned version. This inconsistency means that validation may pass but the wrong data could be saved, or validation may fail when it should succeed if the schema is empty but not yet normalized.

GT 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue) ⏎ if (schema?.type !== 'object') {`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:314`，距錨點 0 行）JSON Schema 驗證不完整，可能接受無效 schema

> 在 `handleConfirm` 中，對 JSON Schema 的驗證僅檢查 `schema?.type === 'object'`，但未驗證其他必要欄位（如 `properties` 是否存在、是否為物件等）。這可能讓使用者輸入如 `{"type": "object"}` 的 schema 通過驗證，但後續使用該 schema 的程式碼可能假設 `properties` 存在而導致錯誤。

**失敗情境**：使用者輸入 `{"type": "object"}` 並儲存，之後使用該變數時，程式碼嘗試存取 `schema.properties` 可能得到 `undefined`，進而引發錯誤。

**建議**：除了檢查 `type`，也應驗證 `properties` 是否存在且為物件，或使用更完整的 JSON Schema 驗證函式庫。

finding 片段：`if (schema?.type !== 'object') { ⏎ Toast.notify({ type: 'error', message: t('variableConfig.errorMsg.jsonSchemaMustBeObject', { ns: 'appDebug' }) }) ⏎ return ⏎ }`

## P0540

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 0 行）使用 jwt.decode 跳過簽章驗證可能接受被竄改的 token

> `_isJWTExpired` 原本使用 `jwt.verify` 來驗證 token 的簽章與有效性，現在改為 `jwt.decode` 僅解碼 payload 而不驗證簽章。這表示攻擊者若取得或猜測到 token，可以竄改 payload（例如延長 `exp`）而不被偵測，導致過期 token 被接受。雖然此 token 可能僅用於內部服務，但仍存在安全風險。

建議：若需驗證過期，應使用 `jwt.verify` 並捕捉 `TokenExpiredError` 來判斷是否過期，或至少使用 `jwt.verify` 的 `ignoreExpiration` 選項。

finding 片段：`const decoded = jwt.decode(token);`

## P0541

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:434`，距錨點 20 行）acceptedBookings 在 recurring 與非 recurring 流程中可能重複觸發事件

> 在 recurring 流程中，`fireBookingAcceptedEvent` 在更新前被呼叫；在非 recurring 流程中，則在更新後被呼叫。但非 recurring 流程中，`acceptedBookings` 的設定在 `fireBookingAcceptedEvent` 之前，且使用硬編碼的 ACCEPTED，可能導致事件觸發時機不一致。建議統一事件觸發的時機與資料來源。

finding 片段：`if (!recurringEventId) { ⏎ await fireBookingAcceptedEvent({ ⏎ actor, ⏎ acceptedBookings,`

## P0542

**GT**（func）Stream entries incorrectly marked as referenced when cgroups_ref is NULL

> When cgroups_ref is NULL (which occurs after DEBUG RELOAD with empty PEL), the function returns 1 indicating the entry IS referenced, when it should return 0 indicating it is NOT referenced. This inverted logic prevents XADD/XTRIM operations with the ACKED strategy from correctly deleting entries that have been fully acknowledged by all consumer groups. The result is a memory leak where stream entries accumulate unnecessarily because they are incorrectly protected from deletion even though no consumer group has them in their pending entry list.

GT 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1; ⏎ unsigned char buf[sizeof(streamID)]; ⏎ streamEncodeID(buf, id);`

**finding**（`src/t_stream.c:2708`，距錨點 0 行）streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能過度保留資料

> 新增的 `if (!s->cgroups_ref) return 1;` 在沒有 consumer group references 時回傳 1，表示該 entry 被引用。這可能導致在沒有 PEL 的情況下，stream 的 entry 永遠不會被刪除，造成記憶體洩漏或資料無法清理。

失敗情境：建立 stream 並建立 consumer group，但沒有任何 PEL 條目（例如所有訊息都已 ack），然後執行 XADD MAXLEN 或 XTRIM，預期會刪除舊 entry，但因為 `cgroups_ref` 為 NULL 而回傳 1，導致 entry 被保留。

建議：確認此修正是否為了解決特定 crash，並評估是否應回傳 0 或進行其他處理。

finding 片段：`if (!s->cgroups_ref) return 1;`

## P0543

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）`getWarmupLimit` 可能回傳 `Infinity`，呼叫端需能處理

> 當 `day > totalDays` 時，函式回傳 `Infinity`。若呼叫端未預期此值，可能導致後續計算（如 `Math.min`、陣列 slice 等）出現非預期行為。建議確認所有呼叫端都能正確處理 `Infinity`，或改回傳一個明確的哨兵值（例如 `emailCount` 或 `Number.MAX_SAFE_INTEGER`）。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0544

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）React Scan 載入失敗時回傳 null 元件可能造成非預期行為

> 在 catch 中回傳 `{ default: () => null }`，雖然有記錄錯誤，但回傳 null 元件可能導致 React 在渲染時出現問題（例如 Suspense 邊界無法正確處理）。建議改為回傳一個空的 Fragment 或明確的 fallback 元件。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0545

**GT**（rule）Use of expect() for fallible PathBuf-to-str conversion

> The code uses `.to_str().expect(...)`, which will panic on non-UTF8 paths. The rule requires fallible operations to return/propagate `Result` instead of panicking via `expect`/`unwrap`.

GT 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

**finding**（`crates/tauri-macos-sign/src/lib.rs:176`，距錨點 0 行）notarize_inner 中參數順序變更可能影響可讀性

> 在 `notarize_inner` 中，`app_bundle_path` 和 `zip_path` 的參數順序被調換，這可能只是為了可讀性，但需確認是否影響任何依賴此函數的程式碼（雖然此函數為私有，但可能被測試或內部呼叫）。

finding 片段：`app_bundle_path ⏎ .to_str() ⏎ .expect("failed to convert bundle_path to string"), ⏎ zip_path`

## P0546

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行）XCTWaiter.wait 的結果未檢查

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0547

**GT**（func）Closure wrapper loses @Sendable annotation causing concurrency safety violation

> The moreButtonAction parameter is marked as @Sendable @MainActor to ensure thread-safe access in Swift 6 concurrency mode. However, the wrappedAction closure that wraps this action drops the @Sendable annotation, only keeping @MainActor. This breaks the sendability guarantee required by Swift 6, potentially allowing non-Sendable types to be captured and accessed from multiple threads unsafely. In Swift 6 strict concurrency mode, this will cause compiler errors or runtime crashes when the closure captures non-Sendable state.

GT 片段：`func configure( ⏎ state: SectionHeaderConfiguration, ⏎ moreButtonAction: (@Sendable @MainActor (UIButton) -> Void)? = nil, ⏎ textColor: UIColor?,`

**finding**（`firefox-ios/Client/Frontend/Home/Homepage/SectionHeader/LabelButtonHeaderView.swift:106`，距錨點 0 行）閉包包裝可能造成不必要的 @MainActor 隔離

> 在 `configure` 方法中，新增了一個 `wrappedAction` 閉包來呼叫 `moreButtonAction`，並將其傳遞給 `ActionButtonViewModel`。此包裝可能只是為了滿足型別檢查，但若 `moreButtonAction` 本身已是 `@MainActor`，此包裝可能導致額外的隔離或效能影響。建議確認是否可以直接傳遞 `moreButtonAction`，或簡化此處的型別轉換。

finding 片段：`let wrappedAction: (@MainActor (UIButton) -> Void)? = { button in ⏎ moreButtonAction?(button) ⏎ }`

## P0548

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 5 行）FakeWKNavigationDelegate 可能無法捕捉 targetFrame

> 在 decidePolicyFor navigationAction 中，navigationAction.targetFrame 可能為 nil（例如新視窗或某些重定向），此時 capturedFrame 為 nil，導致測試失敗。建議處理 targetFrame 為 nil 的情況，或使用其他 delegate 方法。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0549

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:376`，距錨點 0 行）快取資料可能包含 None 值，導致 json.dumps 序列化失敗

> 在 get_plan_bulk_with_cache 中，從 get_plan_bulk 取得的 bulk_plans 可能包含值為 None 的項目（因為 get_plan_bulk 現在會將無效租戶設為 None）。在寫入快取時，程式碼直接對 subscription_plan 呼叫 json.dumps，但 None 不是有效的 JSON 序列化對象，會拋出 TypeError。這會導致整個 pipeline 失敗，且該例外被捕獲後僅記錄日誌，但快取寫入全部失敗。

建議在寫入快取前過濾掉 None 值，或將 None 轉換為其他表示（例如空字典或特殊標記）。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0550

**GT**（func）Missing type coercion for retries value causes potential type inconsistency

> The retries display removes the .toString() call that was present in the original PR, directly rendering taskRun.empirical_policy?.retries ?? "0". This creates a type inconsistency where the value could be either a number (when retries exists) or a string "0" (when it doesn't). While React can render both, this inconsistency violates the principle of uniform data handling and could cause issues in the component tree if parent or child components expect consistent string formatting for this field, or if the value is later used in string operations or comparisons.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retries</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retries ?? "0"}`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 10 行）使用 `||` 可能錯誤處理數值 0

> 在顯示 Retries 時使用 `{taskRun.empirical_policy?.retries ?? "0"}`，此處已使用 `??`，正確。但下方 Retry Jitter Factor 使用 `? ... : "None"`，若值為 0 會顯示「None」，可能不正確。建議改用 `??` 或明確檢查 null/undefined。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## P0551

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:149`，距錨點 0 行）`collect_task_run_inputs` 改為同步呼叫，可能阻塞事件迴圈

> 原本 `await collect_task_run_inputs(v)` 被改為 `collect_task_run_inputs(v)`，移除了 `await`。若 `collect_task_run_inputs` 是同步函式，此變更沒有問題；但若它內部包含非同步操作（例如資料庫查詢），則會導致 `RuntimeError` 或阻塞事件迴圈。

**失敗情境**：在非同步環境中呼叫 `arun_deployment` 且 `as_subflow=True` 時，若 `collect_task_run_inputs` 需要非同步執行，會拋出 `TypeError: object dict can't be used in 'await' expression` 或造成效能問題。

**建議**：確認 `collect_task_run_inputs` 的實作是否為同步；若非同步，應保留 `await`。

finding 片段：`k: collect_task_run_inputs(v) for k, v in parameters.items()`

## P0552

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1125`，距錨點 9 行）使用 var 宣告 newValues

> 在 inline 模式的 multiselect 分支中，`newValues` 使用 `var` 宣告，而其他類似處使用 `const`。這可能是筆誤，建議改為 `const` 以維持一致性並避免潛在的變數提升問題。

finding 片段：`var newValues = [...effectiveValues, option.value] as T[];`

## P0553

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:25`，距錨點 7 行）SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性

> SMTPClient 在建構時直接從全域 dify_config 讀取 SMTP_LOCAL_HOSTNAME，這使得 SMTPClient 與全域設定耦合，難以在測試中隔離或在不同設定下重用。建議將 local_hostname 作為建構子參數傳入，由呼叫端負責提供設定值。

finding 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

## P0554

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行）程式碼格式：`inner_size` 參數間多餘空白

> `inner_size(size.width,    size.height)` 中 `size.width` 與 `size.height` 之間有四個空格，與專案慣例不符。建議改為單一空格。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## P0555

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 3 行）AppContext.SetSwitch 參數值反轉可能導致測試失效

> 原本設定 `DisableThrowNavigationException` 為 `false`，但此處改為 `true`。若測試目的是驗證例外狀況，此變更可能使測試無法觸發預期的例外行為，導致測試失去意義。請確認此參數值是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0556

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致 `wait(for:)` 永遠等不到 expectation 被 fulfill，直到逾時。

應將 `expectation.fulfill()` 移回 `decisionHandler` 內，與其他測試保持一致。

finding 片段：`wait(for: [expectation]) ⏎ expectation.fulfill()`

## P0557

**GT**（func）Incorrect localized string reference in SettingsTextFormatter

> The formatStudiesText method references strings.detailTextStudies instead of strings.detailTextStudiesV2. This causes the formatter to display the old v1 Studies message ('%@ may install and run studies from time to time.') instead of the new v148 message ('%@ randomly selects users to test features, which improves quality for everyone.') that was added in this PR. The helper class was clearly intended to format the new v148 strings based on the PR context, but uses the wrong string constant.

GT 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行）使用 String(format:) 搭配本地化字串可能導致崩潰

> `SettingsTextFormatter` 中的 `formatStudiesText` 和 `formatRolloutsText` 使用 `String(format: strings.detailTextStudies, appName)`。`detailTextStudies` 和 `detailTextRollouts` 是本地化字串，其內容可能包含額外的格式說明符（例如翻譯後的字串可能包含 `%d` 或 `%2$@`），這會導致 `String(format:)` 在執行時期因參數數量不符而崩潰，或顯示錯誤的內容。建議改用 `String.localizedStringWithFormat` 或避免使用格式字串，直接使用字串插值或替換。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ } ⏎ `

## P0558

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行）`CFBundleTypeExtensions` 條件判斷可能相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，但這與預期相反：通常應該在有副檔名時才加入此鍵。若 `ext` 為空，則不應加入；若 `ext` 非空，則應加入。目前的寫法會導致有副檔名時反而沒有寫入 `CFBundleTypeExtensions`，可能影響檔案關聯功能。

建議：將條件改為 `!association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0559

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:202`，距錨點 0 行）fail() 中 action.triggered 事件使用了錯誤的 related 資源

> 在 `fail()` 方法中，`prefect.automation.action.triggered` 事件的 `related` 參數被設為 `self._resulting_related_resources`，而不是包含 triggering-event 和 automation-triggered-event 的 `related_resources`。這會導致該事件缺少與觸發事件及 automation 狀態變更事件的連結，破壞了此 PR 旨在建立的因果鏈。

**失敗情境**：當 action 失敗時，`action.triggered` 事件將不包含 `triggering-event` 或 `automation-triggered-event` 相關資源，使用者無法從該事件追溯到觸發來源。

**建議修法**：將 `related=self._resulting_related_resources` 改為 `related=related_resources`。

finding 片段：`related=self._resulting_related_resources,`

## P0560

**GT**（rule）new_click method missing must_use attribute

> The new_click method returns a TrayIconEvent that represents an important event which should not be ignored. Factory methods that create event objects should be marked with #[must_use] to prevent accidentally creating an event without handling it, which could lead to silent logic errors.

GT 片段：`/// Creates a new Click event with default values. ⏎ /// Useful for testing or creating mock events. ⏎ pub fn new_click(id: TrayIconId) -> Self { ⏎ TrayIconEvent::Click {`

**finding**（`crates/tauri/src/tray/mod.rs:140`，距錨點 0 行）new_click 方法使用硬編碼零值，可能導致測試或模擬事件不真實

> 新增的 `new_click` 方法將 `position`、`rect` 和 `size` 全部設為 0.0，這可能無法反映真實的點擊事件。若此方法用於測試或模擬，這些零值可能導致下游邏輯（例如判斷點擊位置是否在特定區域內）出現非預期行為。建議改為接受位置和矩形作為參數，或提供更合理的預設值。

finding 片段：`pub fn new_click(id: TrayIconId) -> Self { ⏎ TrayIconEvent::Click { ⏎ id, ⏎ position: PhysicalPosition { x: 0.0, y: 0.0 },`

## P0561

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖動的 prefix items

> `sortableKeys` 是從所有 `localKeyedValues` 取得，包含 prefix items（不可拖動）。這可能導致拖放時將項目移動到 prefix 區域，或將 prefix 項目當作拖放目標，造成排序混亂。應僅將可拖動項目的 key 傳入 `SortableContext`，或使用 `disabled` 屬性排除。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0562

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1746`，距錨點 19 行）fmterr 處理中若損壞大小超過限制，遺失原始錯誤訊息

> 在 `fmterr` 標籤中，當 `aof_load_broken` 啟用但損壞大小超過 `aof_load_broken_max_size` 時，僅記錄「AOF was not loaded because the size of the corrupted portion exceeds the configured limit」，但未包含原始格式錯誤的詳細資訊（如檔案名稱、錯誤位置）。這會讓使用者難以判斷損壞的具體原因。

建議在該分支中保留原有的「Bad file format reading the append only file」訊息，或至少包含檔案名稱與錯誤類型。

finding 片段：`} else { /* The size of the corrupted portion exceeds the configured limit. */ ⏎ serverLog(LL_WARNING, ⏎ "AOF was not loaded because the size of the corrupted portion " ⏎ "exceeds the configured limit. aof-load-broken is enabled and broken size '%lld' "`

## P0563

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行）SMTP 類別選擇邏輯可能改變非 TLS 與 TLS 模式的行為

> 原本程式碼根據 use_tls 和 opportunistic_tls 明確選擇 SMTP 或 SMTP_SSL，並在 opportunistic TLS 時先建立 SMTP 再呼叫 starttls。新程式碼使用三元運算子選擇類別，但條件 `(self.use_tls and not self.opportunistic_tls)` 在 use_tls=False 時會選擇 SMTP（正確），但在 use_tls=True 且 opportunistic_tls=True 時也會選擇 SMTP（正確），然而在 use_tls=True 且 opportunistic_tls=False 時選擇 SMTP_SSL（正確）。看似等價，但需注意原本在非 TLS 模式下（use_tls=False）直接建立 SMTP，新程式碼也相同。然而，原本在 opportunistic TLS 模式下，先建立 SMTP 後呼叫 ehlo(self.server)，新程式碼改為 ehlo(local_host)，其中 local_host 可能為空字串，這可能導致 HELO 命令使用空字串而非伺服器位址，違反 SMTP 規範。建議確認 local_host 為空時應回退為 self.server。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0564

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行）搜尋過濾與後端查詢重複，可能造成不一致

> 元件同時使用 `useSuspenseQuery` 的 `deferredSearch` 參數進行後端過濾，又在 `filteredData` 中進行前端過濾。這可能導致當後端過濾與前端過濾條件不同時，顯示的結果不一致。例如後端可能因為大小寫或模糊比對而回傳不同結果，前端又再過濾一次。

**失敗情境**：使用者輸入搜尋字串，後端回傳了符合的區塊文件，但前端過濾因為大小寫敏感而將某些結果排除，導致使用者看不到實際上符合的選項。

**建議**：統一過濾邏輯，要嘛完全依賴後端查詢，要嘛完全在前端過濾，避免雙重過濾造成混淆。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0565

**GT**（rule）Pydantic v1 Config class usage

> The rule requires data validation to use Pydantic v2 with ConfigDict(extra='forbid'), but this code uses Pydantic v1 'class Config' syntax with 'extra = allow' which permits undeclared fields

GT 片段：`class AgentThoughtValidation(BaseModel): ⏎ """ ⏎ Validation model for agent thought data before database persistence. ⏎ """`

**finding**（`api/core/agent/base_agent_runner.py:52`，距錨點 0 行）AgentThoughtValidation 模型未被使用

> 新增的 AgentThoughtValidation 類別似乎未被任何程式碼使用。這可能是為了未來的驗證而準備，但目前是死碼。

建議：若暫時不使用，可考慮移除或加上 TODO 註解說明用途。

finding 片段：`class AgentThoughtValidation(BaseModel): ⏎ """ ⏎ Validation model for agent thought data before database persistence. ⏎ """`

## P0566

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）回傳 `Infinity` 可能造成下游型別或比較問題

> 當暖機完成後，`getWarmupLimit` 回傳 `Infinity`。這可能導致下游程式碼在進行數值比較或計算時出現非預期行為，例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若下游直接使用該值進行算術運算，可能產生 `Infinity` 或 `NaN`。

**建議修法**：
回傳 `emailCount` 本身，或使用一個明確的哨兵值（例如 `Number.MAX_SAFE_INTEGER`），並在文件或型別中說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0567

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1725`，距錨點 2 行）valid_up_to 為 -1 時仍可能嘗試截斷

> 在 fmterr 處理中，若 `valid_up_to == -1`，程式僅記錄警告，但後續仍可能執行 `truncate(aof_filepath, valid_up_to)`，這會將檔案截斷至 -1 的位置，導致未定義行為或檔案損毀。建議在 `valid_up_to == -1` 時直接跳過截斷邏輯，並設定 ret 為 AOF_FAILED。

finding 片段：`if (valid_up_to == -1) { ⏎ serverLog(LL_WARNING,"Last valid command offset is invalid"); ⏎ } else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

## P0568

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行）測試依賴外部網路可能導致不穩定

> captureFrameAndOrigin 使用真實的 WKWebView 載入 https://example.com，這需要網路連線。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。建議改用本地 HTML 字串或攔截請求的方式，避免外部依賴。

finding 片段：`webView.load(URLRequest(url: url))`

## P0569

**GT**（rule）Error enum doesn't use thiserror

> The rule requires custom error enums to use #[derive(thiserror::Error)] with #[error(...)] attributes, but this Error enum manually implements Display and Error traits instead of using thiserror

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 38 行）Error::source() 未涵蓋所有可提供來源的變體

> 手動實作的 `source()` 僅回傳 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 的底層錯誤，但 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER` 等變體也包含底層錯誤，卻未回傳。這會讓使用 `Error::source()` 的錯誤鏈走訪中斷，影響錯誤診斷。建議為所有包含底層錯誤的變體實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## P0570

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:202`，距錨點 0 行）comment 中的引號變更可能影響翻譯工具

> `detailTextSendUsageData` 和 `detailTextStudies` 的 comment 從智慧引號（“ ”）改為直引號（" "）。這可能導致翻譯工具將這些 comment 視為不同，造成翻譯記憶庫不一致。建議確認此變更是否必要，並保持 comment 風格一致。

finding 片段：`static let detailTextSendUsageData = NSLocalizedString("Settings.detailTextSendUsageData", value: "Mozilla strives to collect only what we need to provide and improve %@ for everyone.", comment: "Description associated to the Send Usage Data toggle on main screen. %@ is the app name (for example \"F`

## P0571

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 40 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0572

**GT**（func）Inverted logic in servicing build validation

> The condition for servicing build validation has inverted logic - it triggers an error when AspNetCorePatchVersion equals '1' instead of when it does not equal '1'. This means the first servicing release (patch version 1) will incorrectly fail builds if package references changed, while subsequent servicing releases (patch version 2, 3, etc.) will incorrectly allow breaking changes to package references. The original intent was to allow package reference changes only for the first servicing release (version 10.0.1) but block them for later releases.

GT 片段：`<Error ⏎ Condition=" '$(IsServicingBuild)' == 'true' AND '@(UnusedBaselinePackageReference->Count())' != '0' AND '$(AspNetCorePatchVersion)' == '1'" ⏎ Code="BUILD002" ⏎ Text="Package references changed since the last release. This could be a breaking change and is not allowed in a servicing update. `

**finding**（`eng/targets/ResolveReferences.targets:211`，距錨點 0 行）條件式錯誤檢查可能過於寬鬆

> 在 `Error` 條件中新增 `AND '$(AspNetCorePatchVersion)' == '1'`，這表示只有當 patch 版本為 1 時才檢查未使用的基線套件參考。這可能導致後續 servicing 版本（patch > 1）跳過此檢查，增加風險。建議確認此條件是否應涵蓋所有 servicing 版本。

finding 片段：`Condition=" '$(IsServicingBuild)' == 'true' AND '@(UnusedBaselinePackageReference->Count())' != '0' AND '$(AspNetCorePatchVersion)' == '1'"`

## P0573

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行）hasPageActions 判斷可能使用錯誤的 stack

> 在 `updateToolbarLayout` 中，原本使用 `pageActionStack.arrangedSubviews.isEmpty` 來判斷是否有頁面動作，但被改為 `leadingPageActionStack.arrangedSubviews.isEmpty`。然而，分隔線的寬度應該取決於 trailing page actions 是否存在，而不是 leading page actions。這可能導致分隔線在 trailing page actions 存在但 leading page actions 為空時被隱藏。請確認此變更是否正確，若應使用 trailing stack，請改為 `trailingPageActionStack.arrangedSubviews.isEmpty`。

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## P0574

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:416`，距錨點 0 行）webhooksEnabled 為 false 時，promises 為空陣列，但後續仍會執行其他取消邏輯

> 當 `webhooksEnabled` 為 false 時，`promises` 為空陣列，`await Promise.all(promises)` 會立即完成，但後續的取消流程（如更新資料庫、發送郵件等）仍會執行。這可能符合預期，但需確認停用 webhook 是否也應停用其他副作用。

finding 片段：`const promises = webhooksEnabled ? webhooks.map((webhook) =>`

## P0575

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行）使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。如果使用者未在設定中提供 `name` 且 `ext` 為空，程式會 panic。雖然 schema 可能要求 `name` 或 `ext` 至少一個存在，但此處的變更增加了執行時錯誤的風險。建議保留原本的 fallback 邏輯，或改為更安全的處理方式。

finding 片段：`.expect("File association must have a name")`

## P0576

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行）createInvite 回傳錯誤的 token 欄位

> 在 `createInvite` 中，原本回傳 `token`（隨機產生的 token），但修改後回傳 `newToken.identifier`。`identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致回傳給客戶端的 token 不正確，邀請連結中的 token 也與資料庫中的 token 不一致，使用者將無法透過該 token 加入團隊。

建議改回傳 `token` 變數，或明確使用 `newToken.token`。

finding 片段：`token: newToken.identifier,`

## P0577

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:25`，距錨點 2 行）SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性

> SMTPClient 在建構時直接從全域 dify_config 讀取 SMTP_LOCAL_HOSTNAME，這使得 SMTPClient 與全域設定耦合，難以在測試中隔離或在不同設定下重用。建議將 local_hostname 作為建構子參數傳入，由呼叫端負責提供設定值。

finding 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

## P0578

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:325`，距錨點 0 行）Redis mget 長度不符時快取完全失效且例外被吞掉

> 在 `get_plan_bulk_with_cache` 中，若 `redis_client.mget(redis_keys)` 回傳的 list 長度與 `tenant_ids` 不符，程式會拋出例外，但該例外被外層的 `except Exception` 捕捉，僅記錄錯誤並將所有 tenant 設為 cache miss。這導致即使 Redis 正常運作，只要 mget 因任何原因回傳長度不符（例如 Redis 叢集節點變更），快取就會完全失效，且開發者難以察覺。

**失敗情境**：Redis 叢集在 mget 期間發生 failover，導致部分 key 遺失，回傳長度小於請求數量。此時所有 tenant 都會被視為 cache miss，直接呼叫 billing API，失去快取效益。

**建議**：不要將長度不符視為致命錯誤。可改為逐 key 檢查，或僅記錄警告並將缺失的 key 視為 miss。若必須拋出例外，應使用更精確的例外型別，並考慮重試機制。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## P0579

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 8 行）getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。如果 `getRecordings` 是非同步方法，則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這會導致 API 回傳錯誤的資料格式，且可能造成序列化問題。請確認 `getRecordings` 是否為 async，若是則必須加上 `await`。

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0580

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:25`，距錨點 3 行）SMTPClient 直接依賴全域 dify_config，降低可測試性與重用性

> SMTPClient 在建構時直接從全域 dify_config 讀取 SMTP_LOCAL_HOSTNAME，這使得 SMTPClient 與全域設定耦合，難以在測試中隔離或在不同設定下重用。建議將 local_hostname 作為建構子參數傳入，由呼叫端負責提供設定值。

finding 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

## P0581

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行）buildInviteLink 條件判斷反轉，導致邀請連結錯誤

> 原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，現在改為 `if (isOrgContext) { return teamInviteLink; }`。這會使得在組織情境下（isOrgContext 為 true）直接回傳 teamInviteLink，而沒有附加 getting started 路徑；反之在非組織情境下卻會附加 getting started 路徑。

失敗情境：組織團隊的邀請連結缺少必要的 onboarding 參數，使用者點擊後可能無法正確導向。

建議：恢復原本的條件判斷，或確認邏輯是否應為 `if (isOrgContext) { ... } else { return teamInviteLink; }`。

finding 片段：`if (isOrgContext) { ⏎ return teamInviteLink; ⏎ }`

## P0582

**GT**（func）Incorrect requestReschedule flag for seat cancellation webhooks

> The cancelAttendeeSeat function incorrectly sets requestReschedule to true when cancelling individual attendee seats, even though this is not a reschedule request. This flag should be false for regular seat cancellations and only true for actual reschedule requests. External webhook consumers receiving BOOKING_CANCELLED events will incorrectly interpret seat cancellations as reschedule requests, potentially triggering wrong automated workflows, email templates, or business logic in integrated systems.

GT 片段：`const payload: EventPayloadType = { ⏎ ...evt, ⏎ ...eventTypeInfo, ⏎ status: "CANCELLED",`

**finding**（`packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167`，距錨點 0 行）requestReschedule 在取消座位時固定為 true，可能不準確

> 在 `cancelAttendeeSeat` 中，payload 新增 `requestReschedule: true`，但此流程是取消座位，並非 request-reschedule 流程。若此 webhook 被下游用於判斷是否為 reschedule 請求，可能會誤判。建議確認此處的語意。

finding 片段：`requestReschedule: true,`

## P0583

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:13`，距錨點 0 行）全域 mock 行為變更可能影響未修改的測試

> 全域 mock 原本在沒有 namespace 時直接回傳 key，現在改為一律加上 namespace 前綴（若存在）。這會改變所有依賴全域 mock 的測試行為，可能導致大量測試失敗。建議先執行完整測試套件確認影響範圍，或考慮保留舊行為作為預設，僅在需要時才加上前綴。

finding 片段：`const fullKey = ns ? `${ns}.${key}` : key`

## P0584

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行）active_defrag_enabled 恢復為硬編碼 1，忽略原始設定

> 在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存到 `orig_active_defrag`，然後設為 0，但在 `emptyData` 之後卻直接設為 1，而不是恢復為 `orig_active_defrag`。如果原始設定為 0（例如使用者停用主動碎片整理），此函式會意外地啟用它，可能導致非預期的碎片整理行為。

失敗情境：使用者設定 `activedefrag no`，然後執行會觸發 `rdbLoadEmptyDbFunc` 的操作（例如複製同步），之後主動碎片整理會被意外啟用。

建議修改：
```c
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`server.active_defrag_enabled = 1;`

## P0585

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281`，距錨點 0 行）登出流程移除 SignOutSessionStateManager 後可能喪失 CSRF 防護

> 原本的登出驗證會同時檢查 HistoryEntryState 與 SignOutSessionStateManager，現在僅依賴 HistoryEntryState。若瀏覽器不支援 History API 或狀態遺失，ValidateSignOutRequestState() 可能回傳 false，導致登出失敗。此外，若攻擊者能操控 HistoryEntryState，可能繞過 CSRF 防護。建議確認 HistoryEntryState 的可靠性，或保留備援機制。

finding 片段：`if (!ValidateSignOutRequestState())`

## P0586

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:44`，距錨點 0 行）getUrlHistory 回傳型別變更可能導致呼叫端未處理 undefined 而發生錯誤

> 原本的程式碼在 `history` 為 falsy 時會回傳 `undefined`，但修改後直接回傳 `history`，型別從 `URLHistory | undefined` 變成 `URLHistory`。如果呼叫端沒有處理 `undefined` 的情況，可能會在執行時期嘗試存取 `history` 的屬性而拋出錯誤。建議確認所有呼叫端是否都有正確處理 `undefined`，或保留原本的條件判斷。

finding 片段：`const history = getDefaultUrlHistory(); ⏎ return history;`

## P0587

**GT**（func）Missing PreReleaseBrandingLabel for servicing builds

> The PreReleaseBrandingLabel configuration is missing the condition for 'servicing' builds. While the PreReleaseVersionLabel is set to 'servicing', there is no corresponding conditional assignment for PreReleaseBrandingLabel when PreReleaseVersionLabel equals 'servicing'. This means servicing builds will have an undefined or incorrect branding label, causing incorrect version strings in build outputs and package metadata. The original PR added this condition to properly support servicing releases.

GT 片段：`<PreReleaseVersionLabel>servicing</PreReleaseVersionLabel> ⏎ <!-- PreReleaseBrandingLabel is automatically calculated based on PreReleaseVersionLabel --> ⏎ <PreReleaseBrandingLabel Condition="'$(PreReleaseVersionLabel)' == 'alpha'">Alpha $(PreReleaseVersionIteration)</PreReleaseBrandingLabel> ⏎ <Pre`

**finding**（`eng/Versions.props:14`，距錨點 8 行）停用基準驗證可能隱藏套件參考變更

> ValidateBaseline 從 true 改為 false，這會停用對套件參考變更的驗證。在 servicing 更新中，這可能導致未預期的套件參考變更被合併，增加風險。建議確認此變更的必要性，或僅在特定條件下停用。

finding 片段：`<ValidateBaseline>false</ValidateBaseline>`

## P0588

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）骨架地址欄約束可能錯誤

> 在 `setupSkeletonAddressBars` 中，原本的約束是 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)`，但被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 與 rightSkeletonAddressBar 的 trailing 對齊，而不是與 leftSkeletonAddressBar 的 trailing 對齊，造成佈局錯誤。請確認此變更是否正確，若為筆誤應改回 `leftSkeletonAddressBar`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0589

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 7 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0590

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴邏輯與後端不一致

> 此處將 `config.version` 直接加在 endpointName 前面（例如 `v2_api_kpis`），但後端 `buildRequest` 是加在後面（`api_kpis_v2`）。若前端使用此函式產生的 URL，將呼叫不存在的 pipe，導致 API 錯誤。建議統一命名規則，例如改為 `${endpointName}_${config.version}`。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0591

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）cli.js 版本號與 tauri-cli 版本不一致

> 在 `crates/tauri-cli/metadata-v2.json` 中，`cli.js` 的版本從 `2.8.1` 更新為 `2.8.2`，但 `tauri-cli` 的版本在 `crates/tauri-cli/Cargo.toml` 中只更新到 `2.8.1`。這可能導致發布的 CLI 版本與 metadata 中記錄的版本不符，影響使用者或工具鏈的版本偵測。

建議確認 `cli.js` 的版本是否應與 `tauri-cli` 同步，或此處的版本號應為 `2.8.1`。

finding 片段：`"version": "2.8.2",`

## P0592

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 未驗證 schedule 結構，可能接受無效資料

> validateCreateScheduleInput 僅檢查 name 是否為非空字串，未驗證 schedule 是否為符合預期的陣列結構。若呼叫端傳入錯誤格式的 schedule，可能導致後續 API 請求失敗或產生未預期的行為。建議加入對 schedule 的型別檢查，例如確認其為二維陣列且元素包含 start 和 end。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0593

**GT**（rule）Broad exception catch (except Exception) added for tool_responses JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type. The new code introduces another broad `except Exception:` while parsing JSON observations.

GT 片段：`if observation_payload: ⏎ try: ⏎ tool_responses = json.loads(observation_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 19 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 tool_call_response 的 content 是 `tool_responses.get(tool, agent_thought.observation)`，但此 PR 改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給使用者的工具回應內容變成工具的輸入參數，而非實際的觀察結果，造成資料錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，使用者看到的將是輸入參數而非工具輸出。

建議：改回使用 `tool_responses`，並移除不必要的 `str()` 轉換（若原本就是字串）。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0594

**GT**（rule）Repository does not follow `Prisma<Entity>Repository` naming convention

> Rule 1 requires repository classes/files to follow the `Prisma<Entity>Repository.ts` pattern with matching exported class name. This repository is named `PermissionRepository` in `PermissionRepository.ts` (and not `PrismaPermissionRepository`).

GT 片段：`export class PermissionRepository implements IPermissionRepository {`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:205`，距錨點 7 行）Fallback 查詢的 orgId 過濾條件可能排除應包含的團隊

> 在 `getTeamsWithFallbackRoles` 的第一個 SELECT 中，orgId 過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`，同樣只包含組織本身及其直接子團隊。若使用者是組織成員，且目標團隊是更深層級的子團隊，則會被排除。

**失敗情境**：組織 A（id=1）有子團隊 B（parentId=1），B 有子團隊 C（parentId=B.id）。使用者是組織 A 的 ADMIN，查詢 `orgId=1` 時，團隊 C 不會被回傳。

**建議修法**：與 PBAC 查詢相同，需確認業務需求並調整條件以涵蓋所有後代團隊。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0595

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:177`，距錨點 22 行）related_resources 順序可能導致事件關聯不一致

> 在 `fail()` 和 `succeed()` 方法中，`related_resources` 先加入 `automation-triggered-event`，再加入 `triggering-event`。若下游依賴順序（例如測試或序列化），可能造成非預期行為。建議確認順序是否應為 `triggering-event` 在前，或明確文件化順序。

**失敗情境**：若事件消費者假設第一個 related resource 是 `triggering-event`，則會解析錯誤。

finding 片段：`if triggered_action.automation_triggered_event_id: ⏎ related_resources.append( ⏎ RelatedResource( ⏎ {`

## P0596

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 17 行）clusterDeleteKeysInUnownedSlots() 可能誤刪正在遷移中的 key

> 此函式會刪除所有不在自己 slot 中的 key，但未檢查 slot 是否正在進行 legacy 遷移（例如 MIGRATING 狀態）。雖然註解提到 atomic slot migration 安全，但 legacy 遷移中若節點是 migrating 狀態，刪除 key 可能導致資料遺失。建議增加對 migrating 狀態的檢查，或確認此函式僅在特定條件下呼叫。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## P0597

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行）參數名稱比對從 metadata.Name 改為 propertyName 可能影響既有功能

> 原本使用 `metadata.Name` 來比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或繫結名稱不同），可能導致找不到對應的參數，進而將描述套用到 RequestBody 或完全遺漏。建議確認此變更是否為預期行為，並補充相關測試。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0598

**GT**（func）Race condition in recurring booking acceptance audit logging

> For recurring bookings, the fireBookingAcceptedEvent function is called BEFORE the database updates the booking statuses to ACCEPTED. This creates a timing issue where the audit system may attempt to record or query booking information before the database transaction completes. The audit logs could reference bookings that are still in PENDING state, or in extreme cases the audit consumer might fail to find consistent booking data. This race condition can lead to inconsistent audit trails, failed audit log creation, or audit records that don't accurately reflect the database state at the time of acceptance.

GT 片段：`const teamId = await getTeamIdFromEventType({ ⏎ eventType: { ⏎ team: { id: eventType?.teamId ?? null }, ⏎ parentId: eventType?.parentId ?? null,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:263`，距錨點 5 行）recurring 接受時 acceptedBookings 的 oldStatus 可能不準確

> 在 recurring 接受流程中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 映射而來，其 `oldStatus` 取自 `booking.status`。但 `unconfirmedRecurringBookings` 的查詢條件是 `status: BookingStatus.PENDING`，因此 `oldStatus` 應為 PENDING。然而，若查詢條件未來變更，或存在其他狀態的預約，此處可能記錄錯誤。目前影響不大，但建議明確使用 `BookingStatus.PENDING` 或保留原始狀態。

finding 片段：`acceptedBookings = unconfirmedRecurringBookings.map((booking) => ({ ⏎ oldStatus: booking.status, ⏎ uid: booking.uid, ⏎ }));`

## P0599

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:56`，距錨點 29 行）Trans mock 未處理 components prop，可能導致依賴該 prop 的測試失敗

> `createTransMock` 回傳的 `Trans` 元件僅接收 `i18nKey` 和 `children`，但實際 react-i18next 的 `Trans` 元件常使用 `components` prop 來插入自訂元件。若元件使用 `<Trans i18nKey="..." components={{ trustSource: <TrustSource /> }} />`，此 mock 會忽略 `components`，導致渲染結果與實際不符，可能使測試無法正確驗證。建議在 `Trans` mock 中處理 `components` prop，例如將 `components` 中的元件渲染在對應位置。

finding 片段：`Trans: ({ i18nKey, children }: { ⏎ i18nKey: string ⏎ children?: React.ReactNode ⏎ }) => {`

## P0600

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，可能導致使用者無法知道是哪個新聞信。建議保留變數以提供完整資訊。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。"`
