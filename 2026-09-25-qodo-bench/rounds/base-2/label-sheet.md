# 盲標單：finding 跟 GT 是不是同一個問題

判準（Martian）：**一個 code change 能同時修掉兩者**才算 `same`；同處、相關但講的是別的問題算 `partial`；否則 `no`。
本單刻意不含 confidence、severity。標在 `labels.csv`：`pair,label,note`。

## base-2:Ghost-1:1|Ghost-1#1

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行，候選管道 loc）scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失

> 原本 `scheduling.init()` 會傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，現在改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確呼叫 API。請確認 `scheduling.init()` 的實作是否已改為自行取得 URL，或此變更是否為預期行為。

finding 片段：`scheduling.init(),`

## base-2:Ghost-1:1|Ghost-1#2

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行，候選管道 loc）scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失

> 原本 `scheduling.init()` 會傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，現在改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確呼叫 API。請確認 `scheduling.init()` 的實作是否已改為自行取得 URL，或此變更是否為預期行為。

finding 片段：`scheduling.init(),`

## base-2:Ghost-1:1|Ghost-1#3

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行，候選管道 loc）scheduling.init() 呼叫方式變更可能導致 API URL 設定遺失

> 原本 `scheduling.init()` 會傳入 `apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true)`，現在改為無參數呼叫。若 `scheduling.init()` 內部依賴此參數來設定 API 端點，移除後可能導致排程服務無法正確呼叫 API。請確認 `scheduling.init()` 的實作是否已改為自行取得 URL，或此變更是否為預期行為。

finding 片段：`scheduling.init(),`

## base-2:Ghost-1:2|Ghost-1#1

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行，候選管道 loc）emailAddressService.init() 改為非同步呼叫可能影響相依服務初始化

> 原本 `await emailAddressService.init()` 是同步等待完成，現在改為在 `Promise.all` 中與其他服務並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 初始化完成，可能導致競態。請確認這些服務的初始化是否已處理相依性，或此變更是否安全。

finding 片段：`emailAddressService.init(),`

## base-2:Ghost-1:2|Ghost-1#2

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 15 行，候選管道 ident）emailAddressService.init() 改為非同步呼叫可能影響相依服務初始化

> 原本 `await emailAddressService.init()` 是同步等待完成，現在改為在 `Promise.all` 中與其他服務並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 初始化完成，可能導致競態。請確認這些服務的初始化是否已處理相依性，或此變更是否安全。

finding 片段：`emailAddressService.init(),`

## base-2:Ghost-1:2|Ghost-1#3

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行，候選管道 loc）emailAddressService.init() 改為非同步呼叫可能影響相依服務初始化

> 原本 `await emailAddressService.init()` 是同步等待完成，現在改為在 `Promise.all` 中與其他服務並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 初始化完成，可能導致競態。請確認這些服務的初始化是否已處理相依性，或此變更是否安全。

finding 片段：`emailAddressService.init(),`

## base-2:Ghost-10:1|Ghost-10#2

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103`，距錨點 0 行，候選管道 loc）輪詢 effect 缺少 confirmBlueskyHandleMutation 依賴，可能使用過時閉包

> useEffect 的依賴陣列僅包含 `account?.blueskyEnabled`, `account?.blueskyHandleConfirmed`, `confirmHandle`，但 `confirmHandle` 內部呼叫了 `confirmBlueskyHandleMutation.mutateAsync()`。若 mutation 函式在元件生命週期中因 queryClient 或 API 實例變更而更新，此 effect 不會重新執行，導致輪詢使用舊的 mutation 函式，可能造成請求發送到錯誤的 API 端點或使用過時的 token。建議將 `confirmBlueskyHandleMutation` 加入依賴陣列，或使用 ref 保存最新的 mutation 函式。

finding 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ `

## base-2:Ghost-10:2|Ghost-10#0

**GT**（rule）Strict mode disabled in TypeScript config

> The rule requires TypeScript configuration files to have 'strict' set to true in compilerOptions, but it was set to false

GT 片段：`/* Linting */ ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`apps/activitypub/tsconfig.json:18`，距錨點 0 行，候選管道 loc）關閉 TypeScript strict 模式可能隱藏型別錯誤

> 將 `strict` 從 true 改為 false 會降低型別安全性，可能導致未處理的 null/undefined 錯誤在編譯期未被發現。此變更應有充分理由，否則建議恢復 strict 並修正相關型別錯誤。

finding 片段：`"strict": false,`

## base-2:Ghost-10:3|Ghost-10#2

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107`，距錨點 0 行，候選管道 loc）輪詢失敗時呼叫 disableBlueskyMutation 可能觸發非預期的快取更新

> 當輪詢達到最大重試次數時，程式碼呼叫 `disableBlueskyMutation.mutateAsync()` 來停用 Bluesky。但 `disableBlueskyMutation` 的 onSuccess 會將快取中的 `blueskyEnabled` 設為 false，這可能與使用者原本的啟用意圖衝突。若使用者已成功啟用但 handle 確認失敗，此操作會將 UI 狀態改回未啟用，但後端可能仍處於啟用狀態，造成不一致。建議改為呼叫專用的取消或重設 API，或至少在停用前確認後端狀態。

finding 片段：`toast.error('Something went wrong, please try again.'); ⏎  ⏎ await disableBlueskyMutation.mutateAsync(); ⏎ setLoading(false);`

## base-2:Ghost-10:4|Ghost-10#2

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:119`，距錨點 2 行，候選管道 loc）輪詢 effect 未清理進行中的 mutation，可能導致記憶體洩漏或狀態更新於已卸載元件

> useEffect 的回傳函式僅清除 interval，但若 interval 觸發的 `confirmHandle()` 正在進行非同步請求，元件卸載後該請求仍可能完成並呼叫 `setHandleConfirmed` 或觸發 mutation 的 onSuccess，造成對已卸載元件的狀態更新。建議使用 AbortController 或追蹤 mounted 狀態，並在清理時取消進行中的請求。

finding 片段：`return () => clearInterval(confirmHandleInterval);`

## base-2:Ghost-10:5|Ghost-10#1

**GT**（func）Missing error handling in Bluesky enable function leaves UI in perpetual loading state

> The handleEnable function removes the try-catch block that was wrapping the enableBlueskyMutation call. When the API call fails (network error, server error, etc.), the loading state is never reset to false, leaving the user stuck with a spinning loader and no way to retry. This is inconsistent with the handleDisable function which properly handles errors. The bug causes a poor user experience where users must refresh the page to recover from any API failure.

GT 片段：`const handleEnable = async () => { ⏎ if (!account?.avatarUrl) { ⏎ setIsEditingProfile(true); ⏎ } else {`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:32`，距錨點 18 行，候選管道 ident）初始 loading 狀態依賴 account 資料，可能導致閃爍或錯誤的載入指示

> `useState` 的初始值使用 `account?.blueskyEnabled && !account?.blueskyHandleConfirmed`，但 `account` 在首次渲染時可能尚未載入（undefined），因此初始 loading 為 false。當 account 載入後，useEffect 會根據條件設定 loading，但這可能造成短暫的 UI 閃爍。建議將初始 loading 設為 true，並在 account 載入後再決定是否顯示載入狀態。

finding 片段：`const [loading, setLoading] = useState(() => account?.blueskyEnabled && !account?.blueskyHandleConfirmed);`

## base-2:Ghost-10:6|Ghost-10#3

**GT**（func）Missing query invalidation after Bluesky handle confirmation causes stale following list

> The confirmBlueskyHandle mutation successfully updates the account cache but fails to invalidate the accountFollows query. When Bluesky is enabled via Bridgy Fed, the account automatically follows the brid.gy account. Both enableBluesky and disableBluesky mutations properly invalidate QUERY_KEYS.accountFollows('index', 'following') to refresh this list, but confirmBlueskyHandle does not. This means after the handle is confirmed, the UI won't show the brid.gy follow relationship until the user manually refreshes the page or navigates away and back. This is inconsistent with the established pattern in the codebase and creates a confusing user experience where the integration appears incomplete.

GT 片段：`onSuccess(blueskyHandle: string) { ⏎ // If the bluesky handle is empty then the handle was not confirmed ⏎ // so we don't need to update the cache ⏎ if (blueskyHandle === '') {`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833`，距錨點 0 行，候選管道 loc）confirmBlueskyHandle mutation 缺少 accountFollows 查詢的失效處理

> 在 `useConfirmBlueskyHandleMutationForUser` 的 onSuccess 中，程式碼註解指出缺少 accountFollows 查詢的失效。若 handle 確認後會影響帳號的追蹤關係（例如自動追蹤 brid.gy 帳號），則未失效該查詢可能導致 UI 顯示過時的追蹤狀態。建議加入對應的 query invalidation。

finding 片段：`// Note: Missing invalidation of accountFollows query that should happen here`

## base-2:Ghost-10:8|Ghost-10#4

**GT**（rule）Missing semicolon after type alias declaration

> The `BlueskyDetails` type alias declaration is not terminated with a semicolon, relying on ASI. The codebase rule requires explicit semicolons at the end of statements.

GT 片段：`type BlueskyDetails = { ⏎ blueskyEnabled: boolean; ⏎ blueskyHandleConfirmed: boolean; ⏎ blueskyHandle: string | null;`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2725`，距錨點 0 行，候選管道 loc）BlueskyDetails 型別未匯出，可能限制重用性

> `BlueskyDetails` 型別定義在檔案內部但未匯出，若其他模組需要此型別則無法使用。建議匯出以提升可維護性。

finding 片段：`type BlueskyDetails = { ⏎ blueskyEnabled: boolean; ⏎ blueskyHandleConfirmed: boolean; ⏎ blueskyHandle: string | null;`

## base-2:Ghost-11:3|Ghost-11#0

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 2 行，候選管道 model_line）autoCloseOnSelect 關閉時未清除搜尋輸入

> 在 multiselect 的 onSelect 中，當 `autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但 `onClose` 的實作（handleClose）會清除搜尋輸入（setSearchInput('')），然而此處直接呼叫 onClose 而非 handleClose，可能導致搜尋輸入未清除。建議統一使用 handleClose 或確保 onClose 有清除邏輯。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## base-2:Ghost-11:3|Ghost-11#4

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 0 行，候選管道 model_line）autoCloseOnSelect 關閉時未清除搜尋輸入

> 在 multiselect 的 onSelect 中，當 `autoCloseOnSelect` 為 true 時呼叫 `onClose?.()`，但 `onClose` 的實作（handleClose）會清除搜尋輸入（setSearchInput('')），然而此處直接呼叫 onClose 而非 handleClose，可能導致搜尋輸入未清除。建議統一使用 handleClose 或確保 onClose 有清除邏輯。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## base-2:Ghost-12:1|Ghost-12#1

**GT**（func）Token caching stores entire object instead of token string

> In the getToken method, when caching the JWT token, the code now stores the entire tokenData object (containing both 'token' and 'exp' properties) instead of just extracting the token string. This causes the returned token structure to be malformed as {token: {token: string, exp: number}, exp: number} instead of the expected {token: string, exp: number}. This will break any consumers of the Tinybird API (like the /api/tinybird/token endpoint and stats/tinybird.js) that expect a string token value, causing authentication failures when making requests to Tinybird pipes.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行，候選管道 loc）_serverToken 儲存整個 tokenData 物件，可能導致後續使用錯誤

> 在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`。這會讓 `_serverToken` 變成一個物件而非 token 字串。後續程式碼若直接使用 `this._serverToken` 作為 token 字串（例如在 HTTP header 中），將導致驗證失敗。請確認所有使用 `_serverToken` 的地方，並修正為儲存 `tokenData.token`。

finding 片段：`this._serverToken = tokenData;`

## base-2:Ghost-12:1|Ghost-12#4

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行，候選管道 loc）_serverToken 儲存整個 tokenData 物件，可能導致後續使用錯誤

> 在 `getServerToken` 方法中，原本 `this._serverToken = tokenData.token;` 改為 `this._serverToken = tokenData;`。這會讓 `_serverToken` 變成一個物件而非 token 字串。後續程式碼若直接使用 `this._serverToken` 作為 token 字串（例如在 HTTP header 中），將導致驗證失敗。請確認所有使用 `_serverToken` 的地方，並修正為儲存 `tokenData.token`。

finding 片段：`this._serverToken = tokenData;`

## base-2:Ghost-12:2|Ghost-12#2

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 15 行，候選管道 ident）移除 noTimestamp 選項可能導致 JWT 產生時間戳，影響過期判斷

> 在 `_generateToken` 中，`jwt.sign` 原本有 `{noTimestamp: true}` 選項，現在被移除。這會讓 JWT 包含 `iat`（issued at）欄位。如果 Tinybird 端驗證時預期沒有 `iat`，可能導致 token 被拒絕。另外，`_isJWTExpired` 改用 `jwt.decode` 後，若 token 沒有 `exp` 欄位（因為 `noTimestamp` 移除後可能仍無 `exp`？），會回傳 true，造成 token 永遠被視為過期。請確認 Tinybird 對 JWT 的要求，並確保 `exp` 欄位正確設定。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## base-2:Ghost-12:2|Ghost-12#3

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 0 行，候選管道 loc）移除 noTimestamp 選項可能導致 JWT 產生時間戳，影響過期判斷

> 在 `_generateToken` 中，`jwt.sign` 原本有 `{noTimestamp: true}` 選項，現在被移除。這會讓 JWT 包含 `iat`（issued at）欄位。如果 Tinybird 端驗證時預期沒有 `iat`，可能導致 token 被拒絕。另外，`_isJWTExpired` 改用 `jwt.decode` 後，若 token 沒有 `exp` 欄位（因為 `noTimestamp` 移除後可能仍無 `exp`？），會回傳 true，造成 token 永遠被視為過期。請確認 Tinybird 對 JWT 的要求，並確保 `exp` 欄位正確設定。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## base-2:Ghost-12:3|Ghost-12#2

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 0 行，候選管道 loc）使用 jwt.decode 而非 jwt.verify 可能導致安全性問題

> 在 `_isJWTExpired` 中，原本使用 `jwt.verify` 驗證 token 的簽名和有效性，現在改為 `jwt.decode`。`jwt.decode` 只解碼 payload，不驗證簽名，因此攻擊者可以偽造 token 並通過過期檢查。這可能導致未授權的存取。請改回使用 `jwt.verify`，並處理可能的驗證錯誤。

finding 片段：`const decoded = jwt.decode(token);`

## base-2:Ghost-12:3|Ghost-12#3

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 17 行，候選管道 ident）使用 jwt.decode 而非 jwt.verify 可能導致安全性問題

> 在 `_isJWTExpired` 中，原本使用 `jwt.verify` 驗證 token 的簽名和有效性，現在改為 `jwt.decode`。`jwt.decode` 只解碼 payload，不驗證簽名，因此攻擊者可以偽造 token 並通過過期檢查。這可能導致未授權的存取。請改回使用 `jwt.verify`，並處理可能的驗證錯誤。

finding 片段：`const decoded = jwt.decode(token);`

## base-2:Ghost-13:1|Ghost-13#1

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行，候選管道 loc）版本前綴組合方式與後端不一致

> 前端將 `config.version` 直接加在 `endpointName` 前面（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是加在後面（`${pipeName}_${version}`）。若同時使用前端與後端，會產生不同的端點名稱（例如前端 `v2_api_kpis` vs 後端 `api_kpis_v2`），導致請求失敗。

建議統一命名規則，例如都使用後綴方式。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## base-2:Ghost-13:2|Ghost-13#2

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:105`，距錨點 0 行，候選管道 loc）移除 source 參數傳遞可能造成功能回歸

> 原本會將 `options.source` 加入 Tinybird 查詢參數，但此 PR 移除了該邏輯。若前端或其他呼叫端仍會傳入 `source` 參數，將無法過濾來源，導致統計資料不正確。

請確認是否刻意移除，或應保留此功能。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## base-2:Ghost-2:1|Ghost-2#2

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:264`，距錨點 0 行，候選管道 loc）編輯器可編輯性改依賴 expertise，可能導致有姓名但無 expertise 的成員無法編輯

> 原本 `editor.setEditable(!!memberName && progress !== 'sending')` 改為 `editor.setEditable(!!member?.expertise && progress !== 'sending')`。若成員有姓名但 expertise 為 null（例如一般使用者），編輯器將無法編輯，即使他們有權限發表留言。這可能造成功能回歸。建議改回使用 memberName 或同時檢查兩者。

finding 片段：`editor.setEditable(!!member?.expertise && progress !== 'sending');`

## base-2:Ghost-2:2|Ghost-2#3

**GT**（func）Reply threading broken for nested comments due to incorrect in_reply_to_id

> The submit function uses `parent.id` as `in_reply_to_id` instead of `openForm.in_reply_to_id`. For nested replies (replying to a reply), these values differ: `openForm.in_reply_to_id` points to the specific comment being replied to, while `parent.id` points to the top-level parent comment. Using `parent.id` breaks the reply chain, causing nested replies to be incorrectly threaded to the wrong comment. This destroys the conversation hierarchy and makes it impossible to track which comment a user is actually replying to in multi-level discussions.

GT 片段：`const submit = useCallback(async ({html}) => { ⏎ // Send comment to server ⏎ await dispatchAction('addReply', { ⏎ parent: parent,`

**finding**（`apps/comments-ui/src/components/content/forms/reply-form.tsx:30`，距錨點 0 行，候選管道 loc）in_reply_to_id 改為 parent.id 可能影響巢狀回覆

> 原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。若 openForm 代表回覆某則回覆（巢狀回覆），則 in_reply_to_id 應指向被回覆的回覆 ID，而非最上層 parent 的 ID。這可能導致回覆串結構錯誤。請確認 openForm 的語意：若 openForm 是針對特定回覆，則應保留原本的 `openForm.in_reply_to_id`。

finding 片段：`in_reply_to_id: parent.id,`

## base-2:Ghost-2:3|Ghost-2#1

**GT**（func）Missing optional chaining causes runtime error when openForm is undefined

> The code accesses `openForm.in_reply_to_snippet` without optional chaining, but openForm can be undefined when rendering certain forms (like the main comment form). The original code correctly used `openForm?.in_reply_to_snippet` with optional chaining. This will cause a "Cannot read property 'in_reply_to_snippet' of undefined" runtime error when the FormWrapper is rendered without an openForm prop, crashing the component.

GT 片段：`let openStyles = ''; ⏎ if (isOpen) { ⏎ const isReplyToReply = !!openForm.in_reply_to_snippet; ⏎ openStyles = isReplyToReply ? 'pl-[1px] pt-[68px] sm:pl-[44px] sm:pt-[56px]' : 'pl-[1px] pt-[48px] sm:pl-[44px] sm:pt-[40px]';`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:313`，距錨點 0 行，候選管道 loc）移除 openForm 的 optional chaining 可能導致錯誤

> 原本 `const isReplyToReply = !!openForm?.in_reply_to_snippet;` 改為 `const isReplyToReply = !!openForm.in_reply_to_snippet;`。若 openForm 可能為 null 或 undefined，則會拋出 TypeError。請確認 openForm 在此處是否保證存在。

finding 片段：`const isReplyToReply = !!openForm.in_reply_to_snippet;`

## base-2:Ghost-3:1|Ghost-3#0

**GT**（rule）Non-strict inequality operator used

> The rule requires using strict equality operators (=== or !==) for all comparisons, but the code uses != instead of !== to check if count is null

GT 片段：`const count = result.data[0].get('csd_email_count'); ⏎ return count != null ? count : 0;`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:101`，距錨點 10 行，候選管道 ident）findPage 的呼叫方式可能與實際模型 API 不符

> 程式碼將 `findOne` 改為 `findPage`，但 `findPage` 通常需要 `page` 參數，且回傳結構可能包含 `meta`。此處僅傳入 `filter`、`order`、`limit`，可能導致執行時錯誤或無法取得正確資料。建議確認 `findPage` 的實際簽名，或改用 `findAll` 搭配 `limit`。

finding 片段：`const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC', ⏎ limit: 1`

## base-2:Ghost-3:1|Ghost-3#1

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:101`，距錨點 0 行，候選管道 loc）findPage 的呼叫方式可能與實際模型 API 不符

> 程式碼將 `findOne` 改為 `findPage`，但 `findPage` 通常需要 `page` 參數，且回傳結構可能包含 `meta`。此處僅傳入 `filter`、`order`、`limit`，可能導致執行時錯誤或無法取得正確資料。建議確認 `findPage` 的實際簽名，或改用 `findAll` 搭配 `limit`。

finding 片段：`const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC', ⏎ limit: 1`

## base-2:Ghost-3:1|Ghost-3#3

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:101`，距錨點 30 行，候選管道 ident）findPage 的呼叫方式可能與實際模型 API 不符

> 程式碼將 `findOne` 改為 `findPage`，但 `findPage` 通常需要 `page` 參數，且回傳結構可能包含 `meta`。此處僅傳入 `filter`、`order`、`limit`，可能導致執行時錯誤或無法取得正確資料。建議確認 `findPage` 的實際簽名，或改用 `findAll` 搭配 `limit`。

finding 片段：`const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC', ⏎ limit: 1`

## base-2:Ghost-3:3|Ghost-3#1

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:102`，距錨點 0 行，候選管道 loc）日期過濾條件從 `<` 改為 `<=` 可能包含今日資料

> 原本使用 `created_at:<今天` 排除今日建立的郵件，改為 `<=` 後會包含今日建立的郵件。這可能導致 `#getHighestCount` 取得今日的資料，進而影響暖機限制的計算。若今日已有大量寄送，可能造成限制過高。建議確認此變更是否為預期行為。

finding 片段：`filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,`

## base-2:Ghost-3:4|Ghost-3#2

**GT**（func）High-volume threshold boundary applies wrong scaling factor at 400k

> The condition uses `>=` instead of `>` when checking if lastCount qualifies for high-volume capping at exactly 400,000 emails. According to the documented scaling table, 400k should use the 2× multiplier from the thresholds array, but with this bug it immediately applies the high-volume cap of 1.2× or +75k absolute increase. For a site hitting exactly 400k messages, this means getting a limit of 480k (1.2×) or 475k (+75k) instead of the expected 800k (2×). This creates a significant bottleneck at a critical growth milestone and breaks the documented warmup progression.

GT 片段：`// For high volume senders (400k+), cap the increase at 20% or 75k absolute ⏎ if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold) { ⏎ const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 0 行，候選管道 loc）高流量上限的計算可能與註解不符

> 註解寫「cap the increase at 20% or 75k absolute」，但程式碼使用 `Math.ceil(lastCount * maxScale)` 計算 scaledIncrease，其中 `maxScale` 為 1.2，代表增加 20%，但 `Math.ceil` 可能導致增加超過 20%。此外，`absoluteIncrease` 是 `lastCount + maxAbsoluteIncrease`，但 `Math.min` 比較的是 scaledIncrease 與 absoluteIncrease，而非增加量。若 lastCount 很大，scaledIncrease 可能遠大於 absoluteIncrease，導致實際增加量超過 75k。建議重新檢視此邏輯。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## base-2:Ghost-3:4|Ghost-3#3

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 5 行，候選管道 loc）高流量上限的計算可能與註解不符

> 註解寫「cap the increase at 20% or 75k absolute」，但程式碼使用 `Math.ceil(lastCount * maxScale)` 計算 scaledIncrease，其中 `maxScale` 為 1.2，代表增加 20%，但 `Math.ceil` 可能導致增加超過 20%。此外，`absoluteIncrease` 是 `lastCount + maxAbsoluteIncrease`，但 `Math.min` 比較的是 scaledIncrease 與 absoluteIncrease，而非增加量。若 lastCount 很大，scaledIncrease 可能遠大於 absoluteIncrease，導致實際增加量超過 75k。建議重新檢視此邏輯。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## base-2:Ghost-4:1|Ghost-4#0

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 18 行，候選管道 ident）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> 此處直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`。若後端在儲存評論時未對 HTML 進行嚴格消毒（例如允許 `<script>` 或事件屬性），攻擊者可在評論中注入惡意腳本，當管理員查看評論列表時觸發 XSS。

**建議**：確認後端已使用如 DOMPurify 等函式庫進行消毒，或在前端渲染前先消毒。若後端已消毒，請在程式碼中註明並確保涵蓋所有可能路徑。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## base-2:Ghost-4:1|Ghost-4#5

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 20 行，候選管道 ident）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> 此處直接使用 `dangerouslySetInnerHTML` 渲染 `item.html`。若後端在儲存評論時未對 HTML 進行嚴格消毒（例如允許 `<script>` 或事件屬性），攻擊者可在評論中注入惡意腳本，當管理員查看評論列表時觸發 XSS。

**建議**：確認後端已使用如 DOMPurify 等函式庫進行消毒，或在前端渲染前先消毒。若後端已消毒，請在程式碼中註明並確保涵蓋所有可能路徑。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## base-2:Ghost-4:2|Ghost-4#0

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行，候選管道 loc）CommentContent 的截斷偵測不會在內容變更時重新計算

> `useEffect` 的依賴陣列為空，僅在掛載時執行一次。若 `item.html` 在元件生命週期內發生變化（例如從 API 取得更新），`isClamped` 不會重新計算，可能導致「Show more」按鈕顯示錯誤。

**建議**：將 `item.html` 加入依賴陣列，或在內容更新時觸發重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## base-2:Ghost-4:2|Ghost-4#1

**GT**（func）Missing dependency in useEffect causes stale clamp detection

> The CommentContent component's useEffect hook has an empty dependency array, but it uses item.html to determine if content should be clamped. When a comment's HTML content changes (e.g., after an edit or when new data is loaded), the clamp detection won't re-run. This means the 'Show more' button may appear when it shouldn't or disappear when it should still be visible, creating a poor user experience. The dependency array should include item.html to ensure the clamp detection re-runs whenever the content changes.

GT 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行，候選管道 loc）CommentContent 的截斷偵測不會在內容變更時重新計算

> `useEffect` 的依賴陣列為空，僅在掛載時執行一次。若 `item.html` 在元件生命週期內發生變化（例如從 API 取得更新），`isClamped` 不會重新計算，可能導致「Show more」按鈕顯示錯誤。

**建議**：將 `item.html` 加入依賴陣列，或在內容更新時觸發重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## base-2:Ghost-4:2|Ghost-4#5

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 2 行，候選管道 loc）CommentContent 的截斷偵測不會在內容變更時重新計算

> `useEffect` 的依賴陣列為空，僅在掛載時執行一次。若 `item.html` 在元件生命週期內發生變化（例如從 API 取得更新），`isClamped` 不會重新計算，可能導致「Show more」按鈕顯示錯誤。

**建議**：將 `item.html` 加入依賴陣列，或在內容更新時觸發重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## base-2:Ghost-5:1|Ghost-5#2

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行，候選管道 loc）移除 setLoading(false) 可能導致 loading 狀態卡住

> 在 minimal 模式下，成功送出表單後原本會呼叫 setLoading(false) 來結束載入狀態，但此 PR 移除了該呼叫。若 submit 函式在成功後沒有在其他地方將 loading 設為 false，UI 可能會永遠顯示載入中。請確認 submit 函式的實作，或保留此呼叫。

finding 片段：`setSuccess(true);`

## base-2:Ghost-5:2|Ghost-5#0

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行，候選管道 ident）getUrlHistory 回傳型別可能變為 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但修改後直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，此函式現在會回傳 undefined，可能導致呼叫端出現錯誤。請確認呼叫端是否能處理 undefined，或保留原本的條件判斷。

finding 片段：`return history;`

## base-2:Ghost-5:2|Ghost-5#1

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行，候選管道 loc）getUrlHistory 回傳型別可能變為 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但修改後直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，此函式現在會回傳 undefined，可能導致呼叫端出現錯誤。請確認呼叫端是否能處理 undefined，或保留原本的條件判斷。

finding 片段：`return history;`

## base-2:Ghost-5:3|Ghost-5#3

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行，候選管道 loc）email trim 可能改變原本行為

> 在提交時對 email 進行 trim 是合理的，但需確認後端是否已處理 trim，以及是否會影響其他依賴原始輸入的邏輯。

finding 片段：`onSubmit({email: email.trim()});`

## base-2:Ghost-6:1|Ghost-6#1

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15`，距錨點 0 行，候選管道 loc）排程條件反轉導致重複排程或永不排程

> 原本的條件 `!hasScheduled.processOutbox` 在尚未排程時才排程，修改後變成 `hasScheduled.processOutbox`，這會導致：
1. 若 `hasScheduled.processOutbox` 為 false（尚未排程），則不會排程，功能失效。
2. 若為 true（已排程），則每次呼叫都會重複排程，造成多個重複的 job。
建議改回 `!hasScheduled.processOutbox`，或在排程後正確設定旗標。

finding 片段：`if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`

## base-2:Ghost-6:2|Ghost-6#0

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 1 行，候選管道 loc）config 值型別不一致可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 在測試中設定為字串（如 `'test-inbox@example.com'`）或空字串，但此處直接作為布林條件使用。若 config 值為空字串，則為 falsy，行為正確；但若為非空字串，則為 truthy，會觸發歡迎郵件。然而，若 config 值為布林 `true` 或 `false`，則行為可能與預期不同。建議明確檢查 config 值是否為非空字串，或統一使用布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## base-2:Ghost-6:2|Ghost-6#2

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 0 行，候選管道 loc）config 值型別不一致可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 在測試中設定為字串（如 `'test-inbox@example.com'`）或空字串，但此處直接作為布林條件使用。若 config 值為空字串，則為 falsy，行為正確；但若為非空字串，則為 truthy，會觸發歡迎郵件。然而，若 config 值為布林 `true` 或 `false`，則行為可能與預期不同。建議明確檢查 config 值是否為非空字串，或統一使用布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## base-2:Ghost-6:3|Ghost-6#0

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342`，距錨點 2 行，候選管道 loc）條件邏輯變更可能導致非預期來源觸發歡迎郵件

> 原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，修改後為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。這表示只要 config 有值，無論來源為何都會觸發歡迎郵件，即使來源不在允許清單中。若 config 用於測試收件匣，可能導致所有來源（如 import、admin）都寄送歡迎郵件，與預期不符。建議保留來源檢查：`welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`。

finding 片段：`if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## base-2:Ghost-6:3|Ghost-6#2

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:342`，距錨點 0 行，候選管道 loc）條件邏輯變更可能導致非預期來源觸發歡迎郵件

> 原本條件為 `this._labsService.isSet('welcomeEmails') && WELCOME_EMAIL_SOURCES.includes(source)`，修改後為 `welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)`。這表示只要 config 有值，無論來源為何都會觸發歡迎郵件，即使來源不在允許清單中。若 config 用於測試收件匣，可能導致所有來源（如 import、admin）都寄送歡迎郵件，與預期不符。建議保留來源檢查：`welcomeEmailConfig && WELCOME_EMAIL_SOURCES.includes(source)`。

finding 片段：`if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## base-2:Ghost-7:1|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行，候選管道 loc）require 陳述式移除分號

> 此檔案中多個 require 陳述式移除了行尾分號（例如 `const {Router} = require('express')`），與專案其他檔案的風格不一致。若專案有 ESLint 規則強制分號，可能導致 CI 失敗。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## base-2:Ghost-7:1|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行，候選管道 ident）require 陳述式移除分號

> 此檔案中多個 require 陳述式移除了行尾分號（例如 `const {Router} = require('express')`），與專案其他檔案的風格不一致。若專案有 ESLint 規則強制分號，可能導致 CI 失敗。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## base-2:Ghost-7:2|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:9`，距錨點 0 行，候選管道 loc）require 路徑大小寫變更可能導致 macOS/Windows 解析失敗

> 路徑從 `./services/MemberBREADService` 改為 `./services/member-bread-service`，但實際檔案名稱已改為 `member-bread-service.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

finding 片段：`const MemberBREADService = require('./services/member-bread-service')`

## base-2:Ghost-7:2|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:9`，距錨點 9 行，候選管道 ident）require 路徑大小寫變更可能導致 macOS/Windows 解析失敗

> 路徑從 `./services/MemberBREADService` 改為 `./services/member-bread-service`，但實際檔案名稱已改為 `member-bread-service.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

finding 片段：`const MemberBREADService = require('./services/member-bread-service')`

## base-2:Ghost-7:3|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:18`，距錨點 8 行，候選管道 ident）require 路徑大小寫變更可能導致 macOS/Windows 解析失敗

> 路徑從 `../../email-suppression-list/EmailSuppressionList` 改為 `../../email-suppression-list/email-suppression-list`，但實際檔案名稱已改為 `email-suppression-list.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

finding 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list');`

## base-2:Ghost-7:3|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:18`，距錨點 0 行，候選管道 loc）require 路徑大小寫變更可能導致 macOS/Windows 解析失敗

> 路徑從 `../../email-suppression-list/EmailSuppressionList` 改為 `../../email-suppression-list/email-suppression-list`，但實際檔案名稱已改為 `email-suppression-list.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

finding 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list');`

## base-2:Ghost-7:4|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:19`，距錨點 9 行，候選管道 ident）require 路徑大小寫變更可能導致 macOS/Windows 解析失敗

> 路徑從 `../../lib/magic-link/MagicLink` 改為 `../../lib/magic-link/magic-link`，但實際檔案名稱已改為 `magic-link.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

finding 片段：`const MagicLink = require('../../lib/magic-link/magic-link');`

## base-2:Ghost-7:4|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:19`，距錨點 0 行，候選管道 loc）require 路徑大小寫變更可能導致 macOS/Windows 解析失敗

> 路徑從 `../../lib/magic-link/MagicLink` 改為 `../../lib/magic-link/magic-link`，但實際檔案名稱已改為 `magic-link.js`。在大小寫不敏感的檔案系統上，若舊檔案未刪除，可能解析到舊檔或產生衝突。

finding 片段：`const MagicLink = require('../../lib/magic-link/magic-link');`

## base-2:Ghost-7:5|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行，候選管道 loc）require 陳述式移除分號可能違反 ESLint 規則

> 此檔案中多個 require 陳述式移除了行尾分號，若專案使用 ESLint 的 `semi` 規則，可能導致 lint 失敗。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## base-2:Ghost-7:5|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行，候選管道 ident）require 陳述式移除分號可能違反 ESLint 規則

> 此檔案中多個 require 陳述式移除了行尾分號，若專案使用 ESLint 的 `semi` 規則，可能導致 lint 失敗。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## base-2:Ghost-8:2|Ghost-8#2

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行，候選管道 loc）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，但原文仍包含該變數。這可能導致使用者看不到具體的新聞信名稱，影響理解。建議保留變數。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## base-2:Ghost-8:2|Ghost-8#6

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行，候選管道 loc）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，但原文仍包含該變數。這可能導致使用者看不到具體的新聞信名稱，影響理解。建議保留變數。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## base-2:Ghost-8:3|Ghost-8#1

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行，候選管道 loc）「Name」翻譯不一致

> 在 portal.json 中，「Name」被改為「名稱」，但在 ghost.json 中仍為「名字」。這可能導致不同頁面顯示不一致。建議統一。

finding 片段：`"Name": "名称",`

## base-2:Ghost-9:1|Ghost-9#0

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行，候選管道 loc）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-2:Ghost-9:1|Ghost-9#1

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行，候選管道 ident）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-2:Ghost-9:1|Ghost-9#2

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行，候選管道 loc）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-2:Ghost-9:1|Ghost-9#3

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行，候選管道 loc）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-2:Ghost-9:2|Ghost-9#0

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行，候選管道 ident）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-2:Ghost-9:2|Ghost-9#1

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行，候選管道 loc）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-2:Ghost-9:2|Ghost-9#2

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行，候選管道 ident）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-2:Ghost-9:2|Ghost-9#3

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行，候選管道 ident）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-2:aspnetcore-1:1|aspnetcore-1#2

**GT**（func）Browser navigation uses Forward() instead of Back() breaking test flow

> In the RedirectEnhancedGetToInternal test, after clicking a link that redirects from /redirect to /scroll-to-hash, the test attempts to verify that browser back navigation works correctly. However, the code calls Browser.Navigate().Forward() instead of Browser.Navigate().Back(). Since there is no forward history (the browser just navigated forward to the current page), Forward() does nothing and the browser remains at /scroll-to-hash. The subsequent assertions expect the browser to be back at /redirect with the "Redirections" heading, but it's still at the redirected page, causing the test to fail. The comment explicitly states "See that 'back' takes you to the place from before the redirection" but the code does the opposite action.

GT 片段：`// See that 'back' takes you to the place from before the redirection ⏎ Browser.Navigate().Forward(); ⏎ Browser.Equal("Redirections", () => _originalH1Element.Text); ⏎ Assert.EndsWith("/subdir/redirect", Browser.Url);`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:113`，距錨點 0 行，候選管道 loc）測試中將 Back() 改為 Forward() 可能導致測試失效

> 在 `RedirectEnhancedGetToInternal` 測試中，原本使用 `Browser.Navigate().Back()` 來驗證返回上一頁的行為，但此 PR 將其改為 `Browser.Navigate().Forward()`。這可能導致測試無法正確驗證預期的瀏覽器歷史記錄行為，甚至可能因為沒有可前進的歷史記錄而拋出例外。建議確認此變更的意圖，並確保測試仍能有效驗證重定向後返回的功能。

finding 片段：`Browser.Navigate().Forward();`

## base-2:aspnetcore-1:2|aspnetcore-1#0

**GT**（rule）MSTest attribute in xUnit project

> The rule requires test projects to consistently use the xUnit framework, but the test method uses MSTest's [TestMethod] attribute instead of xUnit's [Fact] attribute

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException()`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 2 行，候選管道 loc）AppContext 開關值反轉可能導致測試無法觸發預期行為

> 在 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 測試中，`AppContext.SetSwitch` 的第二個參數從 `false` 改為 `true`。此開關名稱暗示其用途是「停用拋出導航例外」，若設為 `true` 可能導致測試無法觸發原本要驗證的例外情境，使測試失去意義。建議確認此變更是否為刻意調整，並檢查測試是否仍能有效驗證目標行為。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-2:aspnetcore-1:2|aspnetcore-1#3

**GT**（func）Navigation exception test disables the exception mechanism it's meant to test

> The NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException test is designed to verify that NavigationException thrown during circular redirects doesn't become an unobserved task exception. The test name, comments, and logic all indicate it should test the exception handling behavior. However, the AppContext switch is set to true, which enables DisableThrowNavigationException, preventing NavigationException from being thrown at all. This fundamentally breaks the test's purpose - it can't validate exception handling behavior when exceptions are disabled. The test navigates to a circular redirect page that relies on NavigationException being thrown and properly handled, but with the switch enabled, the navigation manager uses a different code path that doesn't throw exceptions, making the test validate nothing meaningful.

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 0 行，候選管道 loc）AppContext 開關值反轉可能導致測試無法觸發預期行為

> 在 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 測試中，`AppContext.SetSwitch` 的第二個參數從 `false` 改為 `true`。此開關名稱暗示其用途是「停用拋出導航例外」，若設為 `true` 可能導致測試無法觸發原本要驗證的例外情境，使測試失去意義。建議確認此變更是否為刻意調整，並檢查測試是否仍能有效驗證目標行為。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-2:aspnetcore-1:2|aspnetcore-1#6

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 3 行，候選管道 loc）AppContext 開關值反轉可能導致測試無法觸發預期行為

> 在 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 測試中，`AppContext.SetSwitch` 的第二個參數從 `false` 改為 `true`。此開關名稱暗示其用途是「停用拋出導航例外」，若設為 `true` 可能導致測試無法觸發原本要驗證的例外情境，使測試失去意義。建議確認此變更是否為刻意調整，並檢查測試是否仍能有效驗證目標行為。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-2:aspnetcore-1:3|aspnetcore-1#1

**GT**（func）Stale element reference captured before navigation in test initialization

> In the InitializeAsync method, _originalH1Element is captured by calling Browser.Exists(By.TagName("h1")) before navigating to the test page. This captures an element from whatever page the browser was previously on (from a prior test), then the Navigate() call loads the /redirect page. The stored element reference now points to a detached DOM node from the old page, making it stale. When test methods later access _originalH1Element.Text, they will encounter StaleElementReferenceException or get incorrect values because the element belongs to a different page's DOM that no longer exists in the browser.

GT 片段：`public override async Task InitializeAsync() ⏎ { ⏎ await base.InitializeAsync(); ⏎ _originalH1Element = Browser.Exists(By.TagName("h1"));`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:32`，距錨點 0 行，候選管道 loc）Navigate 呼叫順序變更可能影響測試初始化

> 在 `InitializeAsync` 中，原本先 `Navigate` 再取得 `_originalH1Element`，現在改為先取得元素再 `Navigate`。這可能導致 `_originalH1Element` 在頁面尚未載入時就被取得，進而影響後續測試。建議確認此變更是否會造成元素找不到或狀態不一致的問題。

finding 片段：`_originalH1Element = Browser.Exists(By.TagName("h1")); ⏎ Navigate($"{ServerPathBase}/redirect");`

## base-2:aspnetcore-10:1|aspnetcore-10#2

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行，候選管道 loc）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 驗證條件從 `if (value <= 0)` 改為 `if (value < 0)`，這將允許 `RetainedFileCountLimit = 0`。但文件描述為「strictly positive value」，且 0 可能導致未定義行為（例如保留 0 個檔案）。建議確認此變更是否為預期，若非預期應改回 `<= 0`。

finding 片段：`if (value < 0)`

## base-2:aspnetcore-10:2|aspnetcore-10#1

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47`，距錨點 0 行，候選管道 loc）BackgroundQueueSize 驗證條件變更可能禁止 0 值

> 驗證條件從 `if (value < 0)` 改為 `if (value <= 0)`，這將禁止 `BackgroundQueueSize = 0`。但文件描述為「null for no limit」，且 0 可能被視為合法值（例如表示不排隊）。建議確認此變更是否為預期，若非預期應改回 `< 0`。

finding 片段：`if (value <= 0)`

## base-2:aspnetcore-10:3|aspnetcore-10#3

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行，候選管道 loc）TryGetValidatableTypeInfo 中 out 參數初始化位置調整

> 將 `validatableTypeInfo = null;` 從方法結尾移至開頭，行為不變，但可能降低可讀性。若無特殊原因，建議保留原位置。

finding 片段：`validatableTypeInfo = null;`

## base-2:aspnetcore-2:1|aspnetcore-2#5

**GT**（rule）Async test method name missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`public async Task CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser(HttpTransportType transportType, string protocolName)`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92`，距錨點 1 行，候選管道 loc）新增 QuarantinedTest 可能掩蓋真實回歸

> 在 `CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser` 測試上新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`，表示該測試已知不穩定而被隔離。隔離測試會降低 CI 對真實回歸的敏感度，若問題根源未解決，可能導致相關功能在未來被破壞而無人察覺。建議確認 issue #59991 的狀態，並在修復後移除隔離屬性。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`

## base-2:aspnetcore-2:1|aspnetcore-2#6

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not include explicit AAA structure comments ('// Arrange', '// Act', '// Assert' or '// Act & Assert'), violating the test readability rule.

GT 片段：`public async Task CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser(HttpTransportType transportType, string protocolName) ⏎ { ⏎ using (StartVerifiableLog()) ⏎ {`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:92`，距錨點 1 行，候選管道 loc）新增 QuarantinedTest 可能掩蓋真實回歸

> 在 `CanSendAndReceiveUserMessagesFromMultipleConnectionsWithSameUser` 測試上新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`，表示該測試已知不穩定而被隔離。隔離測試會降低 CI 對真實回歸的敏感度，若問題根源未解決，可能導致相關功能在未來被破壞而無人察覺。建議確認 issue #59991 的狀態，並在修復後移除隔離屬性。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/59991")]`

## base-2:aspnetcore-2:2|aspnetcore-2#7

**GT**（rule）Async test method name missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`public async Task CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral(HttpTransportType transportType, string protocolName)`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188`，距錨點 1 行，候選管道 loc）新增 QuarantinedTest 可能掩蓋真實回歸

> 在 `CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral` 測試上新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`，表示該測試已知不穩定而被隔離。隔離測試會降低 CI 對真實回歸的敏感度，若問題根源未解決，可能導致相關功能在未來被破壞而無人察覺。建議確認 issue #63582 的狀態，並在修復後移除隔離屬性。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`

## base-2:aspnetcore-2:2|aspnetcore-2#8

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not include explicit AAA structure comments ('// Arrange', '// Act', '// Assert' or '// Act & Assert'), violating the test readability rule.

GT 片段：`public async Task CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral(HttpTransportType transportType, string protocolName) ⏎ { ⏎ using (StartVerifiableLog()) ⏎ {`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:188`，距錨點 1 行，候選管道 loc）新增 QuarantinedTest 可能掩蓋真實回歸

> 在 `CanSendAndReceiveUserMessagesUserNameWithPatternIsTreatedAsLiteral` 測試上新增 `[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`，表示該測試已知不穩定而被隔離。隔離測試會降低 CI 對真實回歸的敏感度，若問題根源未解決，可能導致相關功能在未來被破壞而無人察覺。建議確認 issue #63582 的狀態，並在修復後移除隔離屬性。

finding 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/issues/63582")]`

## base-2:aspnetcore-2:3|aspnetcore-2#3

**GT**（func）Race condition from premature TaskCompletionSource recreation

> The _receiveTcs TaskCompletionSource is recreated before checking if the buffer is zero-sized, creating a race condition in the WebSocketWrapper's ReceiveAsync implementation. When a zero-byte read occurs (buffer.Count == 0), the method returns early with the result but the TCS has already been reset. This means if another thread or the background task tries to set a result on the now-recreated TCS while this zero-byte read is in progress, it will affect the next receive operation rather than completing the current one. This breaks the synchronization contract and can cause message loss or out-of-order receives in the stateful reconnection test scenarios where WebSocket message sequencing is critical.

GT 片段：`public override async Task<WebSocketReceiveResult> ReceiveAsync(ArraySegment<byte> buffer, CancellationToken cancellationToken) ⏎ { ⏎ var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409`，距錨點 0 行，候選管道 model_line）WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設時機變更可能影響後續讀取

> 將 `_receiveTcs = new(...)` 從零位元組讀取處理之後移到之前，確保每次呼叫 `ReceiveAsync` 都會建立新的 TaskCompletionSource。這修正了先前在零位元組讀取時未重設 `_receiveTcs` 的潛在問題，但需確認此變更不會影響連續讀取的語意。建議檢視相關測試是否涵蓋零位元組讀取情境。

finding 片段：`_receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

## base-2:aspnetcore-3:1|aspnetcore-3#1

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行，候選管道 loc）SSL_CERT_DIR 路徑比較可能因符號連結或大小寫敏感檔案系統而誤判

> 使用 `Path.GetFullPath` 進行字串比較，但未解析符號連結。若 `SSL_CERT_DIR` 中的路徑包含符號連結，或檔案系統大小寫敏感（如 Linux），可能導致已包含的目錄被誤判為未包含，進而錯誤地設定 `sawTrustFailure = true`。建議使用 `Path.GetFullPath` 後再以 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `LinkTarget` 來處理符號連結，或改用 `Path.TrimEndingDirectorySeparator` 後進行 Ordinal 比較（Linux 上大小寫敏感）。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## base-2:aspnetcore-3:1|aspnetcore-3#2

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 10 行，候選管道 ident）SSL_CERT_DIR 路徑比較可能因符號連結或大小寫敏感檔案系統而誤判

> 使用 `Path.GetFullPath` 進行字串比較，但未解析符號連結。若 `SSL_CERT_DIR` 中的路徑包含符號連結，或檔案系統大小寫敏感（如 Linux），可能導致已包含的目錄被誤判為未包含，進而錯誤地設定 `sawTrustFailure = true`。建議使用 `Path.GetFullPath` 後再以 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `LinkTarget` 來處理符號連結，或改用 `Path.TrimEndingDirectorySeparator` 後進行 Ordinal 比較（Linux 上大小寫敏感）。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## base-2:aspnetcore-3:1|aspnetcore-3#4

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行，候選管道 loc）SSL_CERT_DIR 路徑比較可能因符號連結或大小寫敏感檔案系統而誤判

> 使用 `Path.GetFullPath` 進行字串比較，但未解析符號連結。若 `SSL_CERT_DIR` 中的路徑包含符號連結，或檔案系統大小寫敏感（如 Linux），可能導致已包含的目錄被誤判為未包含，進而錯誤地設定 `sawTrustFailure = true`。建議使用 `Path.GetFullPath` 後再以 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `LinkTarget` 來處理符號連結，或改用 `Path.TrimEndingDirectorySeparator` 後進行 Ordinal 比較（Linux 上大小寫敏感）。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## base-2:aspnetcore-3:2|aspnetcore-3#1

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:379`，距錨點 4 行，候選管道 model_line）catch 區塊過於寬鬆，可能隱藏非預期錯誤

> `catch` 區塊捕獲所有例外並回傳 false，可能隱藏非預期的錯誤（如 `Path.GetFullPath` 因權限不足拋出 `SecurityException`）。建議至少記錄例外或僅捕獲預期的例外類型（如 `ArgumentException`、`NotSupportedException`）。

finding 片段：`catch ⏎ { ⏎ // Ignore invalid directory entries in SSL_CERT_DIR ⏎ return false;`

## base-2:aspnetcore-3:2|aspnetcore-3#2

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:379`，距錨點 14 行，候選管道 ident）catch 區塊過於寬鬆，可能隱藏非預期錯誤

> `catch` 區塊捕獲所有例外並回傳 false，可能隱藏非預期的錯誤（如 `Path.GetFullPath` 因權限不足拋出 `SecurityException`）。建議至少記錄例外或僅捕獲預期的例外類型（如 `ArgumentException`、`NotSupportedException`）。

finding 片段：`catch ⏎ { ⏎ // Ignore invalid directory entries in SSL_CERT_DIR ⏎ return false;`

## base-2:aspnetcore-3:2|aspnetcore-3#4

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:379`，距錨點 4 行，候選管道 model_line）catch 區塊過於寬鬆，可能隱藏非預期錯誤

> `catch` 區塊捕獲所有例外並回傳 false，可能隱藏非預期的錯誤（如 `Path.GetFullPath` 因權限不足拋出 `SecurityException`）。建議至少記錄例外或僅捕獲預期的例外類型（如 `ArgumentException`、`NotSupportedException`）。

finding 片段：`catch ⏎ { ⏎ // Ignore invalid directory entries in SSL_CERT_DIR ⏎ return false;`

## base-2:aspnetcore-3:3|aspnetcore-3#3

**GT**（func）Incorrect event level causes important certificate warnings to be suppressed in non-verbose mode

> When verbose mode is not enabled, the event listener is configured with EventLevel.LogAlways instead of the intended EventLevel.Critical. EventLevel.LogAlways (value 0) actually means all events are enabled, not just critical ones. The original PR intended to show only Critical events in non-verbose mode to suppress routine logging. This bug causes all certificate-related events including verbose debug messages to be displayed in non-verbose mode, flooding users with unnecessary output and making it harder to identify actual problems. This breaks the intended user experience where only critical information should be shown by default.

GT 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

**finding**（`src/Tools/dotnet-dev-certs/src/Program.cs:127`，距錨點 7 行，候選管道 ident）事件監聽器生命週期變更可能影響其他輸出

> 將 `ReporterEventListener` 的建立移至條件外，並在非 verbose 模式下啟用 `LogAlways` 等級。這可能導致原本僅在 verbose 模式下輸出的 `LogAlways` 事件（如 `UnixSuggestSettingEnvironmentVariable`）現在也會在一般模式輸出，可能造成非預期的輸出變化。建議確認所有 `LogAlways` 事件是否都適合在非 verbose 模式顯示。

finding 片段：`var listener = new ReporterEventListener(reporter); ⏎ if (verbose.HasValue()) ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.Verbose);`

## base-2:aspnetcore-4:1|aspnetcore-4#1

**GT**（func）Unnecessary re-rendering on every parameter update with same display name

> The DisplayName component removed the check that prevents re-rendering when the display name hasn't changed (line 50-51). This means that every time SetParametersAsync is called with a changed expression (even if it results in the same display name), the component will trigger a render. This causes performance degradation in scenarios with frequent parameter updates, such as forms with dynamic field expressions, leading to unnecessary DOM updates and potential flickering in the UI.

GT 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ _displayName = newDisplayName;`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 0 行，候選管道 loc）當 `For` 參數未變更時，元件不會重新渲染，導致顯示名稱可能過期

> 在 `SetParametersAsync` 中，只有當 `For != _previousFieldAccessor` 時才會重新計算並渲染。如果父元件重新渲染但傳入相同的 `For` 表達式，且顯示名稱的來源（例如資源檔或屬性）已變更，此元件不會更新。例如，若使用本地化且使用者切換語言，但 `For` 表達式相同，顯示名稱將保持舊語言。建議移除條件判斷，或在每次 `SetParametersAsync` 時都重新計算並渲染。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## base-2:aspnetcore-4:2|aspnetcore-4#2

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 16 行，候選管道 ident）Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不一致

> `ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。若在 Hot Reload 期間修改了屬性的 `DisplayAttribute` 或 `DisplayNameAttribute`，`_displayNameCache` 仍保留舊值，導致顯示名稱錯誤。建議同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## base-2:aspnetcore-4:2|aspnetcore-4#3

**GT**（func）Incomplete cache clearing during hot reload causes stale display names

> The ClearCache method only clears _memberInfoCache but fails to clear _displayNameCache (line 85). During hot reload scenarios when metadata updates occur, the HotReloadManager triggers ClearCache to ensure fresh metadata is loaded. However, with _displayNameCache not being cleared, the component will continue to display stale display names from cached MemberInfo objects even after the attributes have been modified in code. This breaks the hot reload functionality for DisplayAttribute and DisplayNameAttribute changes, requiring developers to restart the application to see attribute changes take effect.

GT 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 0 行，候選管道 loc）Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不一致

> `ClearCache` 方法僅清除 `_memberInfoCache`，未清除 `_displayNameCache`。若在 Hot Reload 期間修改了屬性的 `DisplayAttribute` 或 `DisplayNameAttribute`，`_displayNameCache` 仍保留舊值，導致顯示名稱錯誤。建議同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## base-2:aspnetcore-5:1|aspnetcore-5#3

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行，候選管道 loc）ClientMode 測試中使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，元件是以 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同（例如 `GenericComponent`1[[System.Int32]]` vs `GenericComponent`1[[System.String]]`）。建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## base-2:aspnetcore-5:1|aspnetcore-5#7

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行，候選管道 ident）ClientMode 測試中使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，元件是以 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同（例如 `GenericComponent`1[[System.Int32]]` vs `GenericComponent`1[[System.String]]`）。建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## base-2:aspnetcore-5:2|aspnetcore-5#1

**GT**（func）Incorrect type conversion in generic component parameter assertion

> The test validates a generic component with an int type parameter but uses Convert.ToInt64 instead of Convert.ToInt32 to assert the parameter value. Since the parameter is defined as int (System.Int32) in GenericTestComponent<int>, this creates a type mismatch. The assertion compares a long (Int64) value to the expected int (Int32) value 42, which will cause the test to fail even though the component deserialization is working correctly. This breaks the validation logic for generic component parameters.

GT 片段：`var parameters = deserializedDescriptor.Parameters.ToDictionary(); ⏎ Assert.Single(parameters); ⏎ Assert.Contains("Value", parameters.Keys); ⏎ Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 0 行，候選管道 loc）參數值型別轉換脆弱，可能因文化特性失敗

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 long。然而，`parameters["Value"]` 的實際型別取決於反序列化過程，可能是 `JsonElement` 或其他型別。如果該值不是可直接轉換為 long 的型別（例如是 `JsonElement`），`Convert.ToInt64` 可能拋出例外或產生非預期結果。建議先確認參數值的實際型別，或使用更強健的轉換方式（例如 `Assert.IsType<JsonElement>(parameters["Value"])` 後再取得數值）。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## base-2:aspnetcore-5:2|aspnetcore-5#2

**GT**（func）Incorrect sequence validation for multiple generic components

> The test validates deserialization of multiple closed generic components but checks that both descriptors have sequence number 0 instead of verifying that the second descriptor has sequence number 1. Component descriptors in a collection must have sequential ordering starting from 0, and this test should verify the second component has sequence 1. This incorrect assertion fails to validate proper sequence ordering, which is critical for component initialization and rendering order in Blazor.

GT 片段：`var secondDescriptor = descriptors[1]; ⏎ Assert.Equal(typeof(GenericTestComponent<string>).FullName, secondDescriptor.ComponentType.FullName); ⏎ Assert.Equal(0, secondDescriptor.Sequence);`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 18 行，候選管道 ident）參數值型別轉換脆弱，可能因文化特性失敗

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 將參數值轉換為 long。然而，`parameters["Value"]` 的實際型別取決於反序列化過程，可能是 `JsonElement` 或其他型別。如果該值不是可直接轉換為 long 的型別（例如是 `JsonElement`），`Convert.ToInt64` 可能拋出例外或產生非預期結果。建議先確認參數值的實際型別，或使用更強健的轉換方式（例如 `Assert.IsType<JsonElement>(parameters["Value"])` 後再取得數值）。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## base-2:aspnetcore-5:3|aspnetcore-5#3

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行，候選管道 loc）ClientMode 測試中未驗證 Descriptor 內容

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，僅驗證了 preamble marker 的 Assembly 與 TypeName，但未驗證 descriptor 的內容（例如參數定義與值）。這可能導致測試涵蓋不足，無法確保序列化與反序列化的正確性。建議參考其他測試（如 ServerMode 測試）增加對 descriptor 的驗證。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## base-2:aspnetcore-5:3|aspnetcore-5#7

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行，候選管道 ident）ClientMode 測試中未驗證 Descriptor 內容

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，僅驗證了 preamble marker 的 Assembly 與 TypeName，但未驗證 descriptor 的內容（例如參數定義與值）。這可能導致測試涵蓋不足，無法確保序列化與反序列化的正確性。建議參考其他測試（如 ServerMode 測試）增加對 descriptor 的驗證。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## base-2:aspnetcore-5:4|aspnetcore-5#1

**GT**（func）Incorrect type conversion in generic component parameter assertion

> The test validates a generic component with an int type parameter but uses Convert.ToInt64 instead of Convert.ToInt32 to assert the parameter value. Since the parameter is defined as int (System.Int32) in GenericTestComponent<int>, this creates a type mismatch. The assertion compares a long (Int64) value to the expected int (Int32) value 42, which will cause the test to fail even though the component deserialization is working correctly. This breaks the validation logic for generic component parameters.

GT 片段：`var parameters = deserializedDescriptor.Parameters.ToDictionary(); ⏎ Assert.Single(parameters); ⏎ Assert.Contains("Value", parameters.Keys); ⏎ Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 0 行，候選管道 loc）使用 Convert.ToInt64 可能隱藏型別資訊

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64` 將參數值轉換為 long，但未驗證參數值的原始型別。這可能導致測試無法偵測到反序列化過程中型別資訊的遺失或錯誤。建議先斷言參數值的型別（例如 `Assert.IsType<JsonElement>(parameters["Value"])`），再進行數值比較。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## base-2:aspnetcore-5:4|aspnetcore-5#2

**GT**（func）Incorrect sequence validation for multiple generic components

> The test validates deserialization of multiple closed generic components but checks that both descriptors have sequence number 0 instead of verifying that the second descriptor has sequence number 1. Component descriptors in a collection must have sequential ordering starting from 0, and this test should verify the second component has sequence 1. This incorrect assertion fails to validate proper sequence ordering, which is critical for component initialization and rendering order in Blazor.

GT 片段：`var secondDescriptor = descriptors[1]; ⏎ Assert.Equal(typeof(GenericTestComponent<string>).FullName, secondDescriptor.ComponentType.FullName); ⏎ Assert.Equal(0, secondDescriptor.Sequence);`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 18 行，候選管道 ident）使用 Convert.ToInt64 可能隱藏型別資訊

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64` 將參數值轉換為 long，但未驗證參數值的原始型別。這可能導致測試無法偵測到反序列化過程中型別資訊的遺失或錯誤。建議先斷言參數值的型別（例如 `Assert.IsType<JsonElement>(parameters["Value"])`），再進行數值比較。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## base-2:aspnetcore-6:1|aspnetcore-6#0

**GT**（rule）Missing ConfigureAwait(false) on Task.Yield

> The rule requires all await expressions in library code (non-test, non-sample projects) to use .ConfigureAwait(false) to avoid capturing the synchronization context, but the await Task.Yield() expression at line 291 omits it.

GT 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 0 行，候選管道 loc）新增的 Task.Yield() 可能造成非預期的非同步行為

> 在 ProcessLogOut 中新增 `await Task.Yield();` 可能改變執行流程，特別是在驗證登出狀態後、取得驗證狀態前。此舉可能引入競態條件或延遲，且未提供明確理由。建議移除或提供詳細說明，並確保有對應測試涵蓋此行為。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## base-2:aspnetcore-6:1|aspnetcore-6#1

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 6 行，候選管道 ident）新增的 Task.Yield() 可能造成非預期的非同步行為

> 在 ProcessLogOut 中新增 `await Task.Yield();` 可能改變執行流程，特別是在驗證登出狀態後、取得驗證狀態前。此舉可能引入競態條件或延遲，且未提供明確理由。建議移除或提供詳細說明，並確保有對應測試涵蓋此行為。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## base-2:aspnetcore-6:2|aspnetcore-6#2

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38`，距錨點 0 行，候選管道 loc）Redirect 方法中可能使用 null 的 InteractiveRequestUrl

> 在 `Redirect()` 方法中，條件從 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 改為僅檢查 `_tokenResult.InteractionOptions != null`，然後在 else 分支中使用 `_tokenResult.InteractiveRequestUrl!`。若 `InteractiveRequestUrl` 為 null，將導致 NullReferenceException。建議保留 null 檢查或確保該屬性在 InteractionOptions 存在時必定非 null。

finding 片段：`if (_tokenResult.InteractionOptions != null) ⏎ { ⏎ _navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, _tokenResult.InteractionOptions); ⏎ }`

## base-2:aspnetcore-6:3|aspnetcore-6#1

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281`，距錨點 0 行，候選管道 loc）移除 SignOutSessionStateManager 後，登出狀態驗證邏輯可能不完整

> 原本的登出流程會同時檢查 HistoryEntryState 和 SignOutSessionStateManager，現在僅依賴 HistoryEntryState。若某些用戶端或情境未正確設定 HistoryEntryState，可能導致登出驗證失敗或安全漏洞。建議確認所有登出路徑都已更新為使用 HistoryEntryState。

finding 片段：`if (!ValidateSignOutRequestState()) ⏎ { ⏎ Log.LogoutOperationInitiatedExternally(Logger); ⏎ Navigation.NavigateTo(ApplicationPaths.LogOutFailedPath, AuthenticationNavigationOptions with { HistoryEntryState = "The logout was not initiated from within the page." });`

## base-2:aspnetcore-7:1|aspnetcore-7#0

**GT**（rule）Missing braces in for loop

> The rule requires all control flow statements (if, else, for, foreach, while, do-while) to use curly braces even for single-line bodies, but the inner for loop omits curly braces

GT 片段：`for (const [initializerIdentifier, componentIdentifiers] of Object.entries(jsComponentInitializers)) { ⏎ const initializerFunc = DotNet.findJSFunction(initializerIdentifier, 0) as JSComponentInitializerCallback; ⏎ for (const componentIdentifier of componentIdentifiers) ⏎ initializerFunc(componentIde`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 4 行，候選管道 loc）hasInitializedJsComponents 可能導致不同 renderer 類型初始化被跳過

> 當同一頁面存在多個不同 renderer 類型（例如 Server 與 WebAssembly）且都嘗試啟用 JS root components 時，第一個 renderer 會設定 hasInitializedJsComponents = true，導致第二個 renderer 的初始化被跳過。這可能造成第二個 renderer 的 JS 元件無法正確初始化。建議將 hasInitializedJsComponents 改為以 rendererId 為鍵的集合，或改為在每次 enableJSRootComponents 呼叫時都執行初始化（若初始化是冪等的）。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## base-2:aspnetcore-7:1|aspnetcore-7#1

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 10 行，候選管道 ident）hasInitializedJsComponents 可能導致不同 renderer 類型初始化被跳過

> 當同一頁面存在多個不同 renderer 類型（例如 Server 與 WebAssembly）且都嘗試啟用 JS root components 時，第一個 renderer 會設定 hasInitializedJsComponents = true，導致第二個 renderer 的初始化被跳過。這可能造成第二個 renderer 的 JS 元件無法正確初始化。建議將 hasInitializedJsComponents 改為以 rendererId 為鍵的集合，或改為在每次 enableJSRootComponents 呼叫時都執行初始化（若初始化是冪等的）。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## base-2:aspnetcore-7:1|aspnetcore-7#2

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 2 行，候選管道 loc）hasInitializedJsComponents 可能導致不同 renderer 類型初始化被跳過

> 當同一頁面存在多個不同 renderer 類型（例如 Server 與 WebAssembly）且都嘗試啟用 JS root components 時，第一個 renderer 會設定 hasInitializedJsComponents = true，導致第二個 renderer 的初始化被跳過。這可能造成第二個 renderer 的 JS 元件無法正確初始化。建議將 hasInitializedJsComponents 改為以 rendererId 為鍵的集合，或改為在每次 enableJSRootComponents 呼叫時都執行初始化（若初始化是冪等的）。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## base-2:aspnetcore-8:1|aspnetcore-8#1

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行，候選管道 loc）將 remarks 指派給 Summary 可能改變既有 API 文件語意

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。在 OpenAPI 中，Summary 與 Description 有不同用途：Summary 通常較簡短，Description 較詳細。若既有 XML 註解中 `<remarks>` 內容較長，此變更可能導致產生的 OpenAPI 文件不符合預期。建議確認此變更為有意為之，並考慮是否應同時設定兩者或保留原行為。

finding 片段：`operation.Summary = remarks;`

## base-2:aspnetcore-8:2|aspnetcore-8#2

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444`，距錨點 5 行，候選管道 loc）metadata 為 null 時跳過處理可能遺失部分 XML 註解

> 新增 `metadata is not null` 條件後，當 `parameterDescription.ModelMetadata` 為 null 時會直接跳過整個區塊。若此情況在實際執行中可能發生（例如某些參數沒有對應的 ModelMetadata），則原本可能套用的 XML 註解將不再套用。建議確認此行為是否符合預期，或考慮在 null 時採取其他處理方式。

finding 片段：`if (metadata is not null ⏎ && metadata.MetadataKind == ModelMetadataKind.Property`

## base-2:aspnetcore-8:3|aspnetcore-8#2

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行，候選管道 loc）使用 propertyName 取代 metadata.Name 可能影響參數比對

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 可能不同（例如 metadata 名稱經過轉換），此變更可能導致找不到對應的 operation parameter，進而將描述套用到 RequestBody 而非參數。建議確認兩者在此情境下是否恆等。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## base-2:aspnetcore-8:3|aspnetcore-8#3

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行，候選管道 ident）使用 propertyName 取代 metadata.Name 可能影響參數比對

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 可能不同（例如 metadata 名稱經過轉換），此變更可能導致找不到對應的 operation parameter，進而將描述套用到 RequestBody 而非參數。建議確認兩者在此情境下是否恆等。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## base-2:aspnetcore-8:4|aspnetcore-8#2

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行，候選管道 ident）RequestBody.Description 指派位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在處理範例之前，現在移到範例處理之後。若 `propertyComment.Examples` 存在且解析失敗，原本仍會設定 Description，現在則可能不會。建議確認此順序變更是否會造成行為差異。

finding 片段：`operation.RequestBody.Description = description;`

## base-2:aspnetcore-8:4|aspnetcore-8#3

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行，候選管道 loc）RequestBody.Description 指派位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在處理範例之前，現在移到範例處理之後。若 `propertyComment.Examples` 存在且解析失敗，原本仍會設定 Description，現在則可能不會。建議確認此順序變更是否會造成行為差異。

finding 片段：`operation.RequestBody.Description = description;`

## base-2:aspnetcore-9:2|aspnetcore-9#2

**GT**（func）Missing PreReleaseBrandingLabel for servicing builds

> The PreReleaseBrandingLabel configuration is missing the condition for 'servicing' builds. While the PreReleaseVersionLabel is set to 'servicing', there is no corresponding conditional assignment for PreReleaseBrandingLabel when PreReleaseVersionLabel equals 'servicing'. This means servicing builds will have an undefined or incorrect branding label, causing incorrect version strings in build outputs and package metadata. The original PR added this condition to properly support servicing releases.

GT 片段：`<PreReleaseVersionLabel>servicing</PreReleaseVersionLabel> ⏎ <!-- PreReleaseBrandingLabel is automatically calculated based on PreReleaseVersionLabel --> ⏎ <PreReleaseBrandingLabel Condition="'$(PreReleaseVersionLabel)' == 'alpha'">Alpha $(PreReleaseVersionIteration)</PreReleaseBrandingLabel> ⏎ <Pre`

**finding**（`eng/Versions.props:14`，距錨點 8 行，候選管道 ident）停用基準驗證可能隱藏套件參考變更

> 將 `ValidateBaseline` 從 `true` 改為 `false`，這會停用對基準套件參考的驗證。在 servicing 更新中，這可能允許未預期的套件參考變更進入發行版本，增加相容性風險。建議確認此變更的必要性，並考慮僅在特定條件下停用。

finding 片段：`<ValidateBaseline>false</ValidateBaseline>`

## base-2:aspnetcore-9:3|aspnetcore-9#3

**GT**（func）Inverted logic in servicing build validation

> The condition for servicing build validation has inverted logic - it triggers an error when AspNetCorePatchVersion equals '1' instead of when it does not equal '1'. This means the first servicing release (patch version 1) will incorrectly fail builds if package references changed, while subsequent servicing releases (patch version 2, 3, etc.) will incorrectly allow breaking changes to package references. The original intent was to allow package reference changes only for the first servicing release (version 10.0.1) but block them for later releases.

GT 片段：`<Error ⏎ Condition=" '$(IsServicingBuild)' == 'true' AND '@(UnusedBaselinePackageReference->Count())' != '0' AND '$(AspNetCorePatchVersion)' == '1'" ⏎ Code="BUILD002" ⏎ Text="Package references changed since the last release. This could be a breaking change and is not allowed in a servicing update. `

**finding**（`eng/targets/ResolveReferences.targets:211`，距錨點 0 行，候選管道 loc）條件新增 `AspNetCorePatchVersion == '1'` 可能過度限制錯誤檢查

> 在錯誤條件中新增 `AND '$(AspNetCorePatchVersion)' == '1'`，這表示只有當 patch 版本為 1 時才會檢查未使用的基準套件參考。若未來 patch 版本增加，此檢查將被跳過，可能導致未預期的套件參考變更未被發現。建議確認此限制是否為有意為之，並考慮使用更通用的條件。

finding 片段：`Condition=" '$(IsServicingBuild)' == 'true' AND '@(UnusedBaselinePackageReference->Count())' != '0' AND '$(AspNetCorePatchVersion)' == '1'"`

## base-2:cal.com-1:1|cal.com-1#2

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行，候選管道 ident）orgId 型別轉換可能導致索引失效與全表掃描

> 在 SQL 查詢中使用 `${orgId}::bigint` 進行型別轉換，可能導致資料庫無法使用 Team.id 上的索引，造成全表掃描。當 orgId 為 null 時，條件 `(${orgId}::bigint IS NULL OR ...)` 會使整個條件恆真，但資料庫仍可能對 Team 表進行全表掃描。建議改為在應用程式層處理 null 情況，例如使用條件式查詢或將 orgId 作為參數傳遞，避免在 SQL 中進行型別轉換。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## base-2:cal.com-1:2|cal.com-1#3

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:117`，距錨點 27 行，候選管道 ident）權限邏輯變更可能導致資料外洩或功能回歸

> 原本僅 ADMIN/OWNER 角色可查看的預訂，現在改為任何具有 booking.read 權限的使用者皆可查看。若 PBAC 權限設定不當，可能導致未授權使用者存取他人預訂資料。此外，若 PermissionCheckService 回傳空陣列，則所有查詢分支都會被跳過，可能導致使用者看不到自己的預訂。建議確認 booking.read 權限的預設設定，並確保使用者至少能查看自己的預訂。

finding 片段：`const teamIdsWithBookingPermission = await permissionCheckService.getTeamIdsWithPermission({ ⏎ userId: user.id, ⏎ permission: "booking.read", ⏎ fallbackRoles,`

## base-2:cal.com-1:3|cal.com-1#3

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行，候選管道 loc）isCurrentUser 判斷邏輯變更可能導致權限繞過

> 原本 `isCurrentUser` 僅在 `filters.userIds.length === 1 && user.id === filters.userIds[0]` 時為 true，現在改為 `filters.userIds.includes(user.id)`。這表示若 userIds 陣列包含目前使用者 ID 及其他使用者 ID，則 `isCurrentUser` 會為 true，可能繞過後續的權限檢查。建議確認此變更是否符合預期，並確保不會造成未授權存取。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## base-2:cal.com-1:4|cal.com-1#1

**GT**（func）orgId parameter not propagated in getTeamIdsWithPermission

> The method getTeamIdsWithPermission accepts an orgId parameter to scope permission checks to a specific organization, but it fails to pass this parameter to the underlying getTeamIdsWithPermissions method. This causes organization scoping to be ignored when checking single permissions, allowing users to potentially access teams from all organizations instead of only the specified one. The bug breaks the core security feature introduced in this PR where organization-scoped permission checks were meant to restrict access based on orgId.

GT 片段：`async getTeamIdsWithPermission({ ⏎ userId, ⏎ permission, ⏎ fallbackRoles,`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222`，距錨點 0 行，候選管道 loc）getTeamIdsWithPermission 未傳遞 orgId 參數

> 在 `getTeamIdsWithPermission` 方法中，呼叫 `this.getTeamIdsWithPermissions` 時未傳遞 `orgId` 參數，導致 orgId 過濾功能在單一權限查詢中失效。建議補上 `orgId` 參數。

finding 片段：`return this.getTeamIdsWithPermissions({ userId, permissions: [permission], fallbackRoles });`

## base-2:cal.com-10:1|cal.com-10#1

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行，候選管道 loc）單筆 booking 的 oldStatus 被硬編碼為 ACCEPTED

> 在 `handleConfirmation` 中，當 `recurringEventId` 不存在時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態，這會導致 audit log 中的 `oldStatus` 不正確。

**失敗情境**：當一個 pending booking 被確認時，audit log 會記錄 `oldStatus: ACCEPTED` 而不是 `PENDING`，造成資料錯誤。

**建議**：從資料庫中取得 booking 的實際狀態，例如在更新前先查詢 `booking.status`，並使用該值作為 `oldStatus`。

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## base-2:cal.com-10:2|cal.com-10#3

**GT**（func）Race condition in recurring booking acceptance audit logging

> For recurring bookings, the fireBookingAcceptedEvent function is called BEFORE the database updates the booking statuses to ACCEPTED. This creates a timing issue where the audit system may attempt to record or query booking information before the database transaction completes. The audit logs could reference bookings that are still in PENDING state, or in extreme cases the audit consumer might fail to find consistent booking data. This race condition can lead to inconsistent audit trails, failed audit log creation, or audit records that don't accurately reflect the database state at the time of acceptance.

GT 片段：`const teamId = await getTeamIdFromEventType({ ⏎ eventType: { ⏎ team: { id: eventType?.teamId ?? null }, ⏎ parentId: eventType?.parentId ?? null,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:263`，距錨點 5 行，候選管道 loc）recurring bookings 的 oldStatus 可能不正確

> 在處理 recurring bookings 時，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 映射而來，其 `oldStatus` 取自 `booking.status`。然而，在呼叫 `fireBookingAcceptedEvent` 之前，這些 bookings 尚未被更新，因此 `oldStatus` 應為 `PENDING`。但若 `unconfirmedRecurringBookings` 查詢的條件是 `status: BookingStatus.PENDING`，則 `oldStatus` 會是 `PENDING`，這部分正確。但需確認查詢條件是否包含其他狀態，例如 `ACCEPTED` 但尚未確認的 bookings。

**失敗情境**：如果查詢條件包含了非 `PENDING` 的 bookings，則 `oldStatus` 可能不正確。

**建議**：確認查詢條件僅包含 `PENDING` 狀態，或明確指定 `oldStatus` 為 `PENDING`。

finding 片段：`acceptedBookings = unconfirmedRecurringBookings.map((booking) => ({ ⏎ oldStatus: booking.status, ⏎ uid: booking.uid, ⏎ }));`

## base-2:cal.com-10:4|cal.com-10#0

**GT**（rule）Line exceeds 110 character width

> The rule requires all TypeScript/JavaScript files to use a maximum line width of 110 characters, but this type declaration exceeds this limit at 172 characters

GT 片段：`private helper: AuditActionServiceHelper<typeof RejectedAuditActionService.latestFieldsSchema, typeof RejectedAuditActionService.storedDataSchema>;`

**finding**（`packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19`，距錨點 18 行，候選管道 ident）RejectedAuditActionService 的 schema 變更可能影響既有資料

> `fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，這表示不再追蹤 rejectionReason 的變更（old/new），而只記錄最終值。這可能影響既有 audit log 的顯示或遷移邏輯。

**失敗情境**：如果既有資料中 `rejectionReason` 是以 `{ old, new }` 格式儲存，新的 schema 解析會失敗。

**建議**：確認資料庫中既有資料的格式，並提供遷移或相容性處理。

finding 片段：`const fieldsSchemaV1 = z.object({ ⏎ rejectionReason: z.string().nullable(), ⏎ status: BookingStatusChangeSchema, ⏎ });`

## base-2:cal.com-10:5|cal.com-10#1

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行，候選管道 loc）單筆 booking 的 oldStatus 硬編碼可能導致測試覆蓋不足

> 在測試中，可能沒有覆蓋到單筆 booking 確認時 `oldStatus` 不為 `ACCEPTED` 的情境，導致此錯誤未被發現。

**建議**：新增測試案例，驗證當 booking 狀態為 `PENDING` 時，audit log 的 `oldStatus` 為 `PENDING`。

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## base-2:cal.com-11:1|cal.com-11#3

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行，候選管道 loc）requestReschedule 預設值不一致可能導致下游誤判

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true` 作為預設值，但在 `BookingWebhookFactory` 中則使用 `params.requestReschedule ?? false`。這表示當呼叫端未明確傳入此欄位時，不同版本的 webhook payload 會得到相反的布林值。若下游系統依賴此欄位判斷是否為 reschedule 流程，可能造成行為不一致。建議統一預設值（例如皆為 false），或在所有呼叫點明確傳入。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## base-2:cal.com-11:2|cal.com-11#0

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行，候選管道 loc）新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";` 來決定是否發送 webhook。若部署環境未設定此變數，則 `webhooksEnabled` 為 true，行為不變；但若設定為 "false"，則所有取消相關的 webhook 都會被靜默停用，且沒有 log 記錄。這可能導致生產環境中 webhook 意外失效。建議確認此環境變數的用途與部署設定，並考慮在停用時輸出警告 log。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## base-2:cal.com-12:1|cal.com-12#2

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行，候選管道 loc）使用 teamMembers 取代 filteredMembers 可能顯示未過濾的成員

> 原本使用 `filteredMembers` 來顯示成員，現在改為 `teamMembers`。若 `filteredMembers` 是根據搜尋條件或權重過濾後的結果，直接使用 `teamMembers` 會顯示所有成員，導致 UI 行為改變。請確認此變更是否為預期，或應保留 `filteredMembers`。

finding 片段：`{teamMembers.map((member) => (`

## base-2:cal.com-12:2|cal.com-12#1

**GT**（func）Double-wrapping data structure causes matching members to be ignored

> The useTeamMembersWithSegment hook wraps the matchingTeamMembersWithResult in an extra layer when it already has a 'result' property from the trpc query. The trpc query returns { result, troubleshooter, mainWarnings, fallbackWarnings }, but the code creates { result: { result: ... } } by conditionally wrapping it again. This causes useProcessTeamMembersData to receive an incorrectly nested structure where matchingTeamMembersWithResult.result contains an object instead of an array, breaking the segment-based member filtering logic and causing the app to show all team members instead of only those matching the attribute segment.

GT 片段：`const { teamMembers, localWeightsInitialValues } = useProcessTeamMembersData({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:28`，距錨點 0 行，候選管道 loc）傳遞給 useProcessTeamMembersData 的 matchingTeamMembersWithResult 型別可能不符

> 在 `useTeamMembersWithSegment` 中，將 `matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult` 傳給 `useProcessTeamMembersData`。若 `matchingTeamMembersWithResult` 的型別與 `useProcessTeamMembersData` 預期的 `matchingTeamMembersWithResult` 參數型別不一致，可能導致執行時期錯誤或型別錯誤。請確認型別定義。

finding 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

## base-2:cal.com-12:2|cal.com-12#4

**GT**（rule）Line exceeds 110 character limit (Biome formatting rule)

> The added line appears to exceed the configured 110 character line width requirement, violating the repo's Biome formatting standards.

GT 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:28`，距錨點 0 行，候選管道 loc）傳遞給 useProcessTeamMembersData 的 matchingTeamMembersWithResult 型別可能不符

> 在 `useTeamMembersWithSegment` 中，將 `matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult` 傳給 `useProcessTeamMembersData`。若 `matchingTeamMembersWithResult` 的型別與 `useProcessTeamMembersData` 預期的 `matchingTeamMembersWithResult` 參數型別不一致，可能導致執行時期錯誤或型別錯誤。請確認型別定義。

finding 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

## base-2:cal.com-13:2|cal.com-13#2

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行，候選管道 loc）moduleLoader 的 token 可能設定錯誤

> `moduleLoader` 的 `token` 屬性被設定為 `moduleToken`，但其他模組（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token。這可能導致容器在取得服務時使用錯誤的 token。請確認 `moduleLoader.token` 應該是要回傳哪一個 token。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## base-2:cal.com-13:3|cal.com-13#3

**GT**（func）FeatureOptInService creates isolated containers breaking dependency sharing

> The getFeatureOptInService() function creates a fresh DI container on every call, which then loads its dependencies including FeaturesRepository into that isolated container. This breaks the expected dependency injection pattern where services should share repository instances. When code calls both getFeaturesRepository() and getFeatureOptInService(), they each create separate containers with separate FeaturesRepository instances, leading to inconsistent cached state and duplicated database connections. The FeatureOptInService's repository will have different cached data than repositories retrieved elsewhere, causing unpredictable behavior in feature flag resolution.

GT 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 0 行，候選管道 loc）每次呼叫都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService()` 每次呼叫都會建立新的容器並載入模組，這可能導致不必要的效能開銷，且若服務內部有狀態（例如快取），每次取得都會是全新的實例。建議考慮使用單例模式或模組層級的容器。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## base-2:cal.com-13:3|cal.com-13#4

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token);`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 3 行，候選管道 loc）每次呼叫都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService()` 每次呼叫都會建立新的容器並載入模組，這可能導致不必要的效能開銷，且若服務內部有狀態（例如快取），每次取得都會是全新的實例。建議考慮使用單例模式或模組層級的容器。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## base-2:cal.com-13:4|cal.com-13#1

**GT**（func）Container created on every function call breaks singleton pattern

> The getFeaturesRepository() function now creates a new DI container instance on every invocation instead of reusing a module-level singleton container. This causes each call to return a different FeaturesRepository instance with its own PrismaClient connection, breaking the singleton pattern. This leads to database connection pool exhaustion and inconsistent cached state across repository instances, as FeaturesRepository maintains an internal cache for features (line 34 in features.repository.ts checks FeaturesRepository.featuresCache).

GT 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 0 行，候選管道 loc）每次呼叫都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository()` 每次呼叫都會建立新的容器並載入模組，這可能導致不必要的效能開銷，且若 repository 內部有狀態（例如快取），每次取得都會是全新的實例。建議考慮使用單例模式或模組層級的容器。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## base-2:cal.com-13:4|cal.com-13#5

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 3 行，候選管道 loc）每次呼叫都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository()` 每次呼叫都會建立新的容器並載入模組，這可能導致不必要的效能開銷，且若 repository 內部有狀態（例如快取），每次取得都會是全新的實例。建議考慮使用單例模式或模組層級的容器。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## base-2:cal.com-14:1|cal.com-14#3

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行，候選管道 loc）listFeaturesForUser 過濾條件寫反，導致回傳 globalEnabled 為 false 的功能

> 在 `listFeaturesForUser` 中，原本的過濾條件是 `.filter((state) => state.globalEnabled)`，但此 PR 改成了 `.filter((state) => !state.globalEnabled)`。這會讓使用者看不到任何全域啟用的功能，反而看到被停用的功能，完全違反預期行為。

**失敗情境**：當某功能在 flags 中 `enabled: true` 時，使用者呼叫 `listFeaturesForUser` 將不會看到該功能；反之，若 `enabled: false`，反而會出現在列表中。

**建議**：改回 `.filter((state) => state.globalEnabled)`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## base-2:cal.com-14:3|cal.com-14#0

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:4`，距錨點 0 行，候選管道 loc）未使用的常數 UNUSED_CONSTANT 應移除

> 新增的 `UNUSED_CONSTANT` 常數未被使用，且註解也表明這是應該被 lint 抓到的。這會造成程式碼雜訊，並可能讓 CI 的 lint 檢查失敗。

**建議**：移除該常數及其註解。

finding 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

## base-2:cal.com-15:1|cal.com-15#1

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:19`，距錨點 0 行，候選管道 loc）Slot.userIds 型別從 number[] 改為 string[] 可能造成執行時期錯誤

> 原本 `@calcom/trpc/server/routers/viewer/slots/types` 中的 `Slot.userIds` 型別為 `number[]`，但此處新定義為 `string[]`。若實際 API 回傳的 userIds 是數字陣列，使用此型別的程式碼（例如將 userIds 傳入需要 number 的函式）會在執行時期發生型別不符的錯誤。建議確認 API 實際回傳型別，若為 number[] 則應改回 `number[]`，或使用 union type 並進行轉換。

finding 片段：`userIds?: string[];`

## base-2:cal.com-15:2|cal.com-15#0

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行，候選管道 ident）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-2:cal.com-15:2|cal.com-15#3

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行，候選管道 ident）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-2:cal.com-15:2|cal.com-15#4

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行，候選管道 ident）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-2:cal.com-15:2|cal.com-15#6

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行，候選管道 ident）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-2:cal.com-15:2|cal.com-15#7

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行，候選管道 ident）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-2:cal.com-15:3|cal.com-15#0

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-2:cal.com-15:3|cal.com-15#3

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行，候選管道 ident）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-2:cal.com-15:3|cal.com-15#4

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-2:cal.com-15:3|cal.com-15#6

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-2:cal.com-15:3|cal.com-15#7

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-2:cal.com-16:1|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 10 行，候選管道 ident）getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫被移除了 `await`。若 `getRecordings` 是非同步方法（從測試中 `jest.spyOn(calVideoService, "getRecordings").mockResolvedValue([])` 可推測其回傳 Promise），則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這將導致 API 回傳錯誤的資料型態，前端可能無法正確解析。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件（序列化後可能變成空物件或拋出錯誤），而非錄音列表。

**建議修法**：恢復 `await`，確保取得實際資料：
```ts
const recordings = await this.calVideoService.getRecordings(bookingUid);
```

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-2:cal.com-16:1|cal.com-16#2

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 0 行，候選管道 loc）getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫被移除了 `await`。若 `getRecordings` 是非同步方法（從測試中 `jest.spyOn(calVideoService, "getRecordings").mockResolvedValue([])` 可推測其回傳 Promise），則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這將導致 API 回傳錯誤的資料型態，前端可能無法正確解析。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件（序列化後可能變成空物件或拋出錯誤），而非錄音列表。

**建議修法**：恢復 `await`，確保取得實際資料：
```ts
const recordings = await this.calVideoService.getRecordings(bookingUid);
```

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-2:cal.com-16:1|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 8 行，候選管道 ident）getRecordings 呼叫缺少 await，可能回傳 Promise 而非資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫被移除了 `await`。若 `getRecordings` 是非同步方法（從測試中 `jest.spyOn(calVideoService, "getRecordings").mockResolvedValue([])` 可推測其回傳 Promise），則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這將導致 API 回傳錯誤的資料型態，前端可能無法正確解析。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件（序列化後可能變成空物件或拋出錯誤），而非錄音列表。

**建議修法**：恢復 `await`，確保取得實際資料：
```ts
const recordings = await this.calVideoService.getRecordings(bookingUid);
```

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-2:cal.com-16:2|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 0 行，候選管道 loc）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 錄音端點（GET /:bookingUid/recordings）的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。讀取錄音應僅需讀取權限，改為寫入權限可能導致只有具備寫入權限的角色才能存取，或意外允許具有寫入權限但無讀取權限的角色存取。

**失敗情境**：一個僅被授予讀取權限的 API key 將無法存取錄音，而一個僅有寫入權限的 key 卻能讀取錄音，這可能違反最小權限原則。

**建議修法**：若此端點僅供讀取，應維持 `BOOKING_READ`；若確實需要寫入權限，請在 PR 描述中說明原因。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-2:cal.com-16:2|cal.com-16#2

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 10 行，候選管道 ident）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 錄音端點（GET /:bookingUid/recordings）的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。讀取錄音應僅需讀取權限，改為寫入權限可能導致只有具備寫入權限的角色才能存取，或意外允許具有寫入權限但無讀取權限的角色存取。

**失敗情境**：一個僅被授予讀取權限的 API key 將無法存取錄音，而一個僅有寫入權限的 key 卻能讀取錄音，這可能違反最小權限原則。

**建議修法**：若此端點僅供讀取，應維持 `BOOKING_READ`；若確實需要寫入權限，請在 PR 描述中說明原因。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-2:cal.com-16:2|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行，候選管道 ident）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 錄音端點（GET /:bookingUid/recordings）的 `@Permissions` 從 `BOOKING_READ` 改為 `BOOKING_WRITE`。讀取錄音應僅需讀取權限，改為寫入權限可能導致只有具備寫入權限的角色才能存取，或意外允許具有寫入權限但無讀取權限的角色存取。

**失敗情境**：一個僅被授予讀取權限的 API key 將無法存取錄音，而一個僅有寫入權限的 key 卻能讀取錄音，這可能違反最小權限原則。

**建議修法**：若此端點僅供讀取，應維持 `BOOKING_READ`；若確實需要寫入權限，請在 PR 描述中說明原因。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-2:cal.com-16:3|cal.com-16#0

**GT**（rule）Types package imports from features

> The rule requires that lower-level packages do not import from higher-level packages. The platform types package should not import from the features package as this violates the dependency hierarchy.

GT 片段：`import { ApiProperty } from "@nestjs/swagger"; ⏎ import { Type } from "class-transformer"; ⏎ import { IsEnum, ValidateNested, IsNumber, IsString, IsOptional, IsUrl } from "class-validator"; ⏎ import { SUCCESS_STATUS, ERROR_STATUS } from "@calcom/platform-constants";`

**finding**（`packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6`，距錨點 0 行，候選管道 loc）新增未使用的 import BookingRepository

> 此檔案新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在檔案中並未使用。這可能是誤加的 import，會造成 lint 警告或增加不必要的相依性。

**建議修法**：移除此 import。

finding 片段：`import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`

## base-2:cal.com-2:1|cal.com-2#1

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:588`，距錨點 0 行，候選管道 loc）hasPendingInviteByUserId 的 accepted 條件寫反

> 方法名稱為 hasPendingInviteByUserId，但查詢條件為 `accepted: true`，這會回傳「已接受邀請」的 membership，而非 pending（未接受）。這導致呼叫端判斷完全相反：有 pending invite 的使用者不會被 redirect，沒有 pending invite 的使用者反而會被 redirect。

失敗情境：使用者註冊後有 pending team invite，呼叫此方法會回傳 false，因此不會 redirect 到 personal onboarding，與 PR 目的相反。

建議修正：將 `accepted: true` 改為 `accepted: false`。

finding 片段：`accepted: true,`

## base-2:cal.com-2:3|cal.com-2#0

**GT**（rule）Single quotes instead of double quotes

> The rule requires using double quotes for all strings in TypeScript/JavaScript files, but single quotes were used for the empty string assignment.

GT 片段：`const userEmail = session.user.email || '';`

**finding**（`apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30`，距錨點 5 行，候選管道 loc）redirect 條件可能過於寬鬆，導致非預期跳轉

> 新增的 redirect 條件為 `if (hasPendingInvite)`，但 `hasPendingInviteByUserId` 目前因 accepted 條件錯誤而回傳「有已接受邀請」的使用者。即使修正為 accepted: false，此條件仍會將所有有 pending invite 的使用者直接導向 personal onboarding，可能跳過原本 getting-started 頁面應提供的其他資訊或步驟。需要確認產品邏輯是否預期如此。

建議：確認 redirect 的觸發條件是否應包含其他限制（例如 onboardingV3 flag），或與 `checkOnboardingRedirect` 的邏輯保持一致。

finding 片段：`const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId: session.user.id }); ⏎ if (hasPendingInvite) { ⏎ return redirect("/onboarding/personal/settings"); ⏎ }`

## base-2:cal.com-2:3|cal.com-2#3

**GT**（rule）Line exceeds 110 character width

> Biome formatting requires a max line width of 110 characters. This newly added line appears to exceed that limit and should be wrapped across multiple lines.

GT 片段：`const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId: session.user.id });`

**finding**（`apps/web/app/(use-page-wrapper)/onboarding/getting-started/page.tsx:30`，距錨點 0 行，候選管道 loc）redirect 條件可能過於寬鬆，導致非預期跳轉

> 新增的 redirect 條件為 `if (hasPendingInvite)`，但 `hasPendingInviteByUserId` 目前因 accepted 條件錯誤而回傳「有已接受邀請」的使用者。即使修正為 accepted: false，此條件仍會將所有有 pending invite 的使用者直接導向 personal onboarding，可能跳過原本 getting-started 頁面應提供的其他資訊或步驟。需要確認產品邏輯是否預期如此。

建議：確認 redirect 的觸發條件是否應包含其他限制（例如 onboardingV3 flag），或與 `checkOnboardingRedirect` 的邏輯保持一致。

finding 片段：`const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId: session.user.id }); ⏎ if (hasPendingInvite) { ⏎ return redirect("/onboarding/personal/settings"); ⏎ }`

## base-2:cal.com-2:5|cal.com-2#2

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行，候選管道 loc）條件由 AND 改為 OR，可能改變既有行為

> 原本的條件是 `pendingInvite && onboardingV3Enabled`，現在改為 `hasPendingInvite || onboardingV3Enabled`。這表示只要 onboardingV3Enabled 為 true，即使沒有 pending invite，也會 redirect 到 personal onboarding。這可能不是預期行為，因為原本需要兩者同時成立。

失敗情境：使用者沒有 pending invite，但 onboardingV3 flag 開啟，現在會被強制導向 personal onboarding，可能跳過其他 onboarding 流程。

建議：確認是否應維持 AND 條件，或明確說明為何改為 OR。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) {`

## base-2:cal.com-3:1|cal.com-3#2

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行，候選管道 loc）`update` 方法缺少 `select`，回傳物件缺少 `references` 與 `workflowReminders`

> 在 `handleCancelBooking.ts` 中，`bookingRepository.updateIncludeWorkflowRemindersAndReferences` 被呼叫後，回傳值被 push 到 `updatedBookings`，後續程式碼會存取 `updatedBooking.references` 與 `updatedBooking.workflowReminders`。但 `BookingRepository.update` 方法（第 1512 行）沒有指定 `select`，因此回傳的 `Booking` 物件不會包含這兩個關聯欄位，導致執行時錯誤。

建議在 `update` 方法中加入與 `updateIncludeWorkflowRemindersAndReferences` 相同的 `select`，或直接改用 `updateIncludeWorkflowRemindersAndReferences`。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## base-2:cal.com-3:2|cal.com-3#3

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:98`，距錨點 0 行，候選管道 loc）移除 `locale` 欄位導致取消流程中 `organizer.locale` 可能為 undefined

> `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但 `handleCancelBooking.ts` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。若 `findByIdOrThrow` 使用此 select，回傳的 organizer 將沒有 `locale` 屬性，可能導致執行時錯誤或 fallback 行為不如預期。

請確認 `findByIdOrThrow` 是否使用此 select，並考慮保留 `locale` 欄位或調整取消流程的處理。

finding 片段：`createdDate: true, ⏎ trialEndsAt: true, ⏎ completedOnboarding: true, ⏎ timeFormat: true,`

## base-2:cal.com-3:5|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:497`，距錨點 0 行，候選管道 model_line）`gte` 條件從 `new Date()` 改為 `bookingToDelete.startTime` 可能改變行為

> 在取消後續 recurring bookings 時，原本的 `gte: new Date()` 被改為 `gte: bookingToDelete.startTime`。這可能導致取消的 bookings 集合不同：如果 `bookingToDelete.startTime` 早於目前時間，會包含過去已發生的 bookings；如果晚於目前時間，則可能遺漏應取消的 bookings。

請確認此變更是否符合預期，並考慮是否應保留原本的 `new Date()` 或使用其他條件。

finding 片段：`startTime: { ⏎ gte: bookingToDelete.startTime, ⏎ },`

## base-2:cal.com-3:6|cal.com-3#2

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1502`，距錨點 0 行，候選管道 loc）`updateMany` 方法缺少回傳值

> `updateMany` 方法沒有回傳 `count`，但介面 `IBookingRepository` 定義回傳 `Promise<{ count: number }>`。雖然目前呼叫端未使用回傳值，但型別不一致可能導致未來誤用。

建議回傳 `this.prismaClient.booking.updateMany` 的結果。

finding 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

## base-2:cal.com-4:1|cal.com-4#4

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行，候選管道 loc）getDisplayEmail 正規表達式可能誤刪合法 email 中的加號後綴

> `getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 來移除後綴，但此模式會匹配任何 email 中長度為 25 的加號後綴，而不僅限於 OAuth 後綴。例如 `user+abcdefghijklmnopqrstuvwxyz@example.com` 會被錯誤地轉換為 `user@example.com`，導致顯示錯誤的 email。建議使用更精確的模式，例如僅匹配已知的 OAuth 後綴格式，或使用更嚴格的邊界條件（如 `$` 或 `@` 前）。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## base-2:cal.com-4:2|cal.com-4#2

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行，候選管道 loc）移除排序邏輯可能導致回傳順序不穩定

> 在 `getOutputRecurringSeatedBookings` 中，原本依 `start` 時間排序的邏輯被移除，直接回傳 `transformed`。這可能導致 API 回傳的訂位順序不穩定，影響前端顯示或測試的可靠性。若排序是有意移除，請確認是否有其他機制保證順序；否則建議保留排序。

finding 片段：`return transformed;`

## base-2:cal.com-4:3|cal.com-4#0

**GT**（rule）Handler logic mixed in schema file

> The rule requires that schema and handler logic are separated into different files. However, the schema file `booking.output.ts` now contains a handler method `cleanEmailForDisplay()` that performs email validation and transformation logic, mixing schema definition with handler logic in the same file.

GT 片段：`// Validate and clean email for display purposes ⏎ static cleanEmailForDisplay(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

**finding**（`packages/platform/types/bookings/2024-08-13/outputs/booking.output.ts:32`，距錨點 27 行，候選管道 ident）新增必填欄位可能造成 API 相容性問題

> 在 `BookingAttendee`、`BookingHost`、`ReassignedToDto` 等類別中新增 `displayEmail` 欄位，且未標記為可選（`@IsOptional()`）。這會使 API 回應的 schema 將該欄位列為必填，可能導致既有用戶端在解析回應時因缺少該欄位而失敗。若此欄位為新增且應向後相容，建議標記為可選或提供預設值。

finding 片段：`@ApiProperty({ type: String, example: "john@example.com", description: "Clean email for display purposes" }) ⏎ @IsString() ⏎ @Expose() ⏎ displayEmail!: string;`

## base-2:cal.com-5:1|cal.com-5#2

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行，候選管道 loc）URL 前綴解析可能產生錯誤的顯示結果

> 在解析 bookingUrl 以取得前綴時，程式碼直接使用 `url.hostname` 並忽略 port，且未處理子路徑可能包含使用者名稱以外的情況。例如，若 bookingUrl 為 `https://cal.com/team/event-slug`，前綴會是 `https://cal.com/team/`，但實際應為 `https://cal.com/`。此外，若 bookingUrl 包含 port（如 `https://localhost:3000/user/slug`），顯示結果會缺少 port。建議改為使用 `url.origin` 並搭配已知的使用者名稱來建構前綴，或直接顯示完整 URL 的一部分。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ // Get path without the last segment (slug) ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug`

## base-2:cal.com-5:4|cal.com-5#3

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1125`，距錨點 0 行，候選管道 model_line）複製按鈕未使用 bookingUrl 欄位

> 在 copyBtn 的事件處理中，仍使用手動建構的 URL，而非優先使用 `eventType.bookingUrl`。這可能導致複製的連結與實際的 bookingUrl 不一致。建議與其他處理一致，使用 `eventType.bookingUrl ||` 的 fallback 模式。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## base-2:cal.com-6:1|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行，候選管道 loc）回傳的 token 改為 identifier，導致邀請 token 錯誤

> 原本回傳 `token`（隨機產生的邀請 token），現在改為 `newToken.identifier`（即 `invite-link-for-teamId-${teamId}`）。這會讓 API 回傳的 `token` 欄位不再是實際的邀請 token，而是 identifier，導致客戶端使用此 token 時無法正確加入團隊。

失敗情境：呼叫 `POST /v2/teams/:teamId/invite` 後，回應中的 `data.token` 會是 `invite-link-for-teamId-123`，而非隨機 token。若客戶端將此值用於邀請連結或驗證，將無法運作。

建議：應回傳 `newToken.token`（實際的隨機 token），而不是 `newToken.identifier`。

finding 片段：`token: newToken.identifier,`

## base-2:cal.com-6:1|cal.com-6#3

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行，候選管道 loc）回傳的 token 改為 identifier，導致邀請 token 錯誤

> 原本回傳 `token`（隨機產生的邀請 token），現在改為 `newToken.identifier`（即 `invite-link-for-teamId-${teamId}`）。這會讓 API 回傳的 `token` 欄位不再是實際的邀請 token，而是 identifier，導致客戶端使用此 token 時無法正確加入團隊。

失敗情境：呼叫 `POST /v2/teams/:teamId/invite` 後，回應中的 `data.token` 會是 `invite-link-for-teamId-123`，而非隨機 token。若客戶端將此值用於邀請連結或驗證，將無法運作。

建議：應回傳 `newToken.token`（實際的隨機 token），而不是 `newToken.identifier`。

finding 片段：`token: newToken.identifier,`

## base-2:cal.com-6:2|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行，候選管道 loc）buildInviteLink 的條件判斷反轉，導致邀請連結錯誤

> 原本 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會讓非組織情境（一般團隊）的邀請連結變成 `/teams?token=...`，而組織情境反而會進入後續的 getting started 路徑，與預期相反。

失敗情境：當 `isOrgContext` 為 false（一般團隊）時，原本應回傳包含 getting started 路徑的連結，現在卻回傳 `/teams?token=...`，導致使用者點擊後無法正確導向。

建議：應改回 `if (!isOrgContext)` 或確認邏輯是否正確。

finding 片段：`if (isOrgContext) {`

## base-2:cal.com-6:2|cal.com-6#3

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行，候選管道 ident）buildInviteLink 的條件判斷反轉，導致邀請連結錯誤

> 原本 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會讓非組織情境（一般團隊）的邀請連結變成 `/teams?token=...`，而組織情境反而會進入後續的 getting started 路徑，與預期相反。

失敗情境：當 `isOrgContext` 為 false（一般團隊）時，原本應回傳包含 getting started 路徑的連結，現在卻回傳 `/teams?token=...`，導致使用者點擊後無法正確導向。

建議：應改回 `if (!isOrgContext)` 或確認邏輯是否正確。

finding 片段：`if (isOrgContext) {`

## base-2:cal.com-6:3|cal.com-6#1

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行，候選管道 loc）角色裝飾器使用 TEAM_MEMBER，但測試期望非管理員被拒絕

> 控制器使用 `@Roles("TEAM_MEMBER")`，這表示任何團隊成員（包括 MEMBER）都可以呼叫此端點。但 E2E 測試中，非管理員成員（role: MEMBER）預期會收到 403。這可能表示角色檢查邏輯有誤，或測試與實作不一致。

失敗情境：若實際部署後，非管理員成員可以成功建立邀請連結，則可能違反權限設計。

建議：確認此端點應允許哪些角色。若僅允許管理員，應改為 `@Roles("TEAM_ADMIN")` 或類似角色；若允許所有成員，則測試應調整為預期 200。

finding 片段：`@Roles("TEAM_MEMBER")`

## base-2:cal.com-6:4|cal.com-6#0

**GT**（rule）Direct import from features package

> The rule requires apps/api/v2 to import from @calcom/platform-libraries instead of directly from @calcom/features, but the code imports TeamService directly from @calcom/features/ee/teams/services/teamService

GT 片段：`import { TeamService } from "@calcom/features/ee/teams/services/teamService";`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38`，距錨點 17 行，候選管道 ident）缺少對 teamId 的權限檢查

> 控制器直接呼叫 `TeamService.createInvite(teamId)`，但未檢查目前使用者是否為該團隊的成員或管理員。雖然有 `RolesGuard`，但 `@Roles("TEAM_MEMBER")` 可能只檢查全域角色，而非針對特定團隊的成員資格。

失敗情境：若使用者是某個團隊的成員，但嘗試對另一個團隊的 `teamId` 建立邀請，可能成功（若角色檢查僅基於全域角色）。

建議：在服務層或控制器中加入團隊成員資格驗證，確保使用者有權限對該團隊進行操作。

finding 片段：`const result = await TeamService.createInvite(teamId);`

## base-2:cal.com-6:4|cal.com-6#1

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38`，距錨點 3 行，候選管道 loc）缺少對 teamId 的權限檢查

> 控制器直接呼叫 `TeamService.createInvite(teamId)`，但未檢查目前使用者是否為該團隊的成員或管理員。雖然有 `RolesGuard`，但 `@Roles("TEAM_MEMBER")` 可能只檢查全域角色，而非針對特定團隊的成員資格。

失敗情境：若使用者是某個團隊的成員，但嘗試對另一個團隊的 `teamId` 建立邀請，可能成功（若角色檢查僅基於全域角色）。

建議：在服務層或控制器中加入團隊成員資格驗證，確保使用者有權限對該團隊進行操作。

finding 片段：`const result = await TeamService.createInvite(teamId);`

## base-2:cal.com-7:2|cal.com-7#2

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行，候選管道 loc）AND 條件設為 undefined 可能導致 Prisma 查詢問題

> 當 genericCalendarSuffixes 為空或未提供時，AND 被設為 undefined。Prisma 通常會忽略 undefined 的條件，但某些版本或嚴格模式下可能拋出型別錯誤。建議改用條件展開（例如 ...(genericCalendarSuffixes?.length ? { AND: [...] } : {})）以避免傳入 undefined。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## base-2:cal.com-8:1|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 18 行，候選管道 ident）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}> ⏎ <Badge variant="gray">+{hiddenItems.length}</Badge> ⏎ </Button>`

## base-2:cal.com-8:1|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 2 行，候選管道 model_line）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}> ⏎ <Badge variant="gray">+{hiddenItems.length}</Badge> ⏎ </Button>`

## base-2:cal.com-8:1|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 19 行，候選管道 ident）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。但 PopoverContent 預設可能渲染在 Portal 中，與觸發按鈕不在同一 DOM 階層，當滑鼠從按鈕移向 PopoverContent 時，可能會先觸發按鈕的 mouseleave 而關閉 Popover，造成閃爍或無法點擊內容。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制，或使用 CSS 的 hover 搭配 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}> ⏎ <Badge variant="gray">+{hiddenItems.length}</Badge> ⏎ </Button>`

## base-2:cal.com-8:2|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:79`，距錨點 12 行，候選管道 ident）Popover 缺乏鍵盤無障礙支援

> 觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

finding 片段：`aria-label={`Show ${hiddenItems.length} more items`} ⏎ onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-2:cal.com-8:2|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:79`，距錨點 8 行，候選管道 ident）Popover 缺乏鍵盤無障礙支援

> 觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

finding 片段：`aria-label={`Show ${hiddenItems.length} more items`} ⏎ onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-2:cal.com-8:2|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:79`，距錨點 13 行，候選管道 ident）Popover 缺乏鍵盤無障礙支援

> 觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

finding 片段：`aria-label={`Show ${hiddenItems.length} more items`} ⏎ onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-2:cal.com-8:3|cal.com-8#2

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行，候選管道 loc）屬性 badge 合併權重與群組標記可能降低可讀性

> 原本權重以獨立 badge 顯示，群組以橘色 badge 區分，現在合併為單一 label（例如 "Value 80% (group)"），可能讓使用者難以快速區分。建議保留視覺區分，或提供 tooltip 說明。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## base-2:cal.com-8:4|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:44`，距錨點 24 行，候選管道 ident）maxVisible 為 0 或負數時行為未定義

> 若 maxVisible 傳入 0 或負數，visibleItems 會是空陣列，hiddenItems 會包含所有項目，但 UI 仍會顯示 +N 按鈕，可能造成困惑。建議加上 prop 驗證或限制最小值為 1。

finding 片段：`visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## base-2:cal.com-9:1|cal.com-9#2

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:53`，距錨點 0 行，候選管道 loc）sortHosts 函式在移動時被意外修改，priority 比較方向反轉

> 在 `isRRWeightsEnabled` 為 true 且 weight 相同時，原本的排序是 `priorityB - priorityA`（降冪），但移動後變成 `priorityA - priorityB`（升冪）。這會導致主持人排序結果相反，可能影響 round-robin 權重分配。請改回 `priorityB - priorityA`。

finding 片段：`return priorityA - priorityB;`

## base-2:cal.com-9:3|cal.com-9#3

**GT**（func）Missing module resolution in dynamic import causes team assignment tab to fail

> The EventTeamAssignmentTab dynamic import is missing the `.then((mod) => mod)` module resolution that all other tab imports use. This inconsistency will cause the dynamic import to not properly extract the default export, resulting in the team assignment tab failing to render correctly. When users navigate to the team assignment tab for event types, they will encounter a blank screen or rendering error because the component cannot be properly loaded.

GT 片段：`const EventTeamAssignmentTab = dynamic(() => import("./tabs/assignment/EventTeamAssignmentTabWebWrapper"));`

**finding**（`apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52`，距錨點 9 行，候選管道 ident）動態 import 路徑改為相對路徑，可能導致建置或執行時錯誤

> 多個 dynamic import 從絕對 alias 改為相對路徑（如 `./tabs/setup/EventSetupTabWebWrapper`）。若目標檔案不存在或路徑錯誤，會在執行時才拋出錯誤。請確認所有相對路徑皆正確，並考慮保留 alias 以利維護。

finding 片段：`const EventSetupTab = dynamic( ⏎ () => import("./tabs/setup/EventSetupTabWebWrapper").then((mod) => mod), ⏎ { loading: () => null } ⏎ );`

## base-2:dify-1:1|dify-1#0

**GT**（rule）Legacy typing imports instead modern syntax

> The rule requires using Python 3.12+ modern type syntax (set[tuple[str, ...]] instead of Set[Tuple[str, ...]]), but the code imports and uses legacy typing module classes Set and Tuple

GT 片段：`from collections.abc import Mapping, Sequence ⏎ from typing import TYPE_CHECKING, Any, Set, Tuple ⏎ ... ⏎ def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行，候選管道 loc）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行期錯誤或型別檢查失敗。建議確認呼叫端型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## base-2:dify-1:1|dify-1#1

**GT**（func）Type mismatch in blocks_variable_output prevents variable blocking

> The blocks_variable_output method compares a Sequence (assigned_variable_selector) directly against a set of tuples (variable_selectors), but fails to convert the Sequence to a tuple first. This type mismatch causes the 'in' check to always return False, meaning the Variable Assigner node will never properly block streaming output of conversation variables. As a result, the response coordinator will incorrectly allow streaming to proceed before conversation variables are updated, violating the intended synchronization logic and potentially showing stale variable values to users.

GT 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool: ⏎ """ ⏎ Check if this Variable Assigner node blocks the output of specific variables. ⏎ Returns True if this node updates any of the requested conversation variables.`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行，候選管道 loc）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行期錯誤或型別檢查失敗。建議確認呼叫端型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## base-2:dify-1:2|dify-1#3

**GT**（func）Test uses list equality instead of tuple conversion for event selector

> The test compares event.selector (which is a Sequence[str]) with a list literal using ==. While this might work in some cases due to Python's sequence equality, it's fragile and inconsistent with the pattern used elsewhere in the codebase. The original code correctly converted to tuple for comparison (tuple(event.selector) == ('conversation', 'conv_var')). This change breaks the filtering logic and will likely cause the test to fail to properly identify conversation variable chunk events, leading to false test failures.

GT 片段：`conv_var_chunk_events = [ ⏎ event ⏎ for event in events ⏎ if isinstance(event, NodeRunStreamChunkEvent) and event.selector == ["conversation", "conv_var"]`

**finding**（`api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75`，距錨點 4 行，候選管道 loc）測試假設所有 chunk 事件的值都等於輸入查詢，可能過於嚴格

> 測試中 `assert all(event.chunk == input_query for event in conv_var_chunk_events)` 假設每個 chunk 事件的值都完全等於輸入查詢。若串流過程中有分段或格式變化，此斷言可能失敗。建議改為檢查最終累積值或至少包含輸入查詢。

finding 片段：`assert all(event.chunk == input_query for event in conv_var_chunk_events), ( ⏎ "Expected streamed conversation variable value to match the input query" ⏎ )`

## base-2:dify-10:1|dify-10#1

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:376`，距錨點 0 行，候選管道 loc）json.dumps 無法序列化 SubscriptionPlan (TypedDict)

> 在 `get_plan_bulk_with_cache` 中，`subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps(subscription_plan)` 會嘗試直接序列化該物件。TypedDict 在執行時是普通的 dict，但此處的 `subscription_plan` 是從 `subscription_adapter.validate_python(plan_dict)` 回傳的，其型別為 `SubscriptionPlan`，實際上是一個 dict，因此 `json.dumps` 應該可以正常運作。然而，如果 `validate_python` 回傳的物件不是純 dict（例如是 Pydantic model 或其他自訂型別），則會拋出 `TypeError`。建議先將 `subscription_plan` 轉換為 dict 再序列化，例如 `json.dumps(dict(subscription_plan))`。

finding 片段：`json_str = json.dumps(subscription_plan)`

## base-2:dify-10:1|dify-10#3

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行，候選管道 loc）json.dumps 無法序列化 SubscriptionPlan (TypedDict)

> 在 `get_plan_bulk_with_cache` 中，`subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps(subscription_plan)` 會嘗試直接序列化該物件。TypedDict 在執行時是普通的 dict，但此處的 `subscription_plan` 是從 `subscription_adapter.validate_python(plan_dict)` 回傳的，其型別為 `SubscriptionPlan`，實際上是一個 dict，因此 `json.dumps` 應該可以正常運作。然而，如果 `validate_python` 回傳的物件不是純 dict（例如是 Pydantic model 或其他自訂型別），則會拋出 `TypeError`。建議先將 `subscription_plan` 轉換為 dict 再序列化，例如 `json.dumps(dict(subscription_plan))`。

finding 片段：`json_str = json.dumps(subscription_plan)`

## base-2:dify-10:2|dify-10#2

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行，候選管道 loc）get_plan_bulk 將驗證失敗的租戶設為 None，可能導致下游錯誤

> 在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼將 `results[tenant_id]` 設為 `None`。這可能導致呼叫端在後續處理時遇到 `None` 值而發生錯誤，因為原本的契約是回傳 `dict[str, SubscriptionPlan]`，且 `SubscriptionPlan` 不包含 `None`。建議改為跳過該租戶（不加入 results），或記錄錯誤後重新拋出例外，讓呼叫端決定如何處理。

finding 片段：`results[tenant_id] = None`

## base-2:dify-10:3|dify-10#1

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:325`，距錨點 40 行，候選管道 ident）Redis mget 回傳值長度檢查可能誤判

> 在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## base-2:dify-10:3|dify-10#2

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:325`，距錨點 31 行，候選管道 ident）Redis mget 回傳值長度檢查可能誤判

> 在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## base-2:dify-10:3|dify-10#4

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:325`，距錨點 0 行，候選管道 loc）Redis mget 回傳值長度檢查可能誤判

> 在 `get_plan_bulk_with_cache` 中，程式碼檢查 `len(cached_values) != len(tenant_ids)` 並拋出例外。但 Redis 的 `mget` 在鍵不存在時會回傳 `None`，因此長度應該永遠等於輸入的鍵數量。這個檢查可能永遠不會觸發，但若 Redis client 實作有問題，拋出例外會導致整個快取讀取失敗並 fallback 到 API，這可能是可接受的。然而，更穩健的做法是直接處理 `None` 值，而不是依賴長度檢查。

finding 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

## base-2:dify-11:1|dify-11#3

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行，候選管道 loc）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 tool_call_response 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具的輸入參數，而非實際的觀察結果，造成語意完全錯誤，可能嚴重影響 agent 的決策。

失敗情境：當 agent 呼叫工具並獲得觀察結果後，歷史訊息中的工具回應會顯示輸入參數，模型將無法得知工具執行的實際結果，導致後續推理錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-2:dify-11:1|dify-11#4

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行，候選管道 ident）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 tool_call_response 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具的輸入參數，而非實際的觀察結果，造成語意完全錯誤，可能嚴重影響 agent 的決策。

失敗情境：當 agent 呼叫工具並獲得觀察結果後，歷史訊息中的工具回應會顯示輸入參數，模型將無法得知工具執行的實際結果，導致後續推理錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-2:dify-11:1|dify-11#5

**GT**（rule）Broad exception catch (except Exception) added for tool_responses JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type. The new code introduces another broad `except Exception:` while parsing JSON observations.

GT 片段：`if observation_payload: ⏎ try: ⏎ tool_responses = json.loads(observation_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 19 行，候選管道 ident）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 tool_call_response 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具的輸入參數，而非實際的觀察結果，造成語意完全錯誤，可能嚴重影響 agent 的決策。

失敗情境：當 agent 呼叫工具並獲得觀察結果後，歷史訊息中的工具回應會顯示輸入參數，模型將無法得知工具執行的實際結果，導致後續推理錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-2:dify-11:5|dify-11#1

**GT**（func）Swapped answer price unit values causing incorrect billing calculations

> In the create_agent_thought method, the answer_unit_price and answer_price_unit values are swapped. The answer_unit_price is initialized to Decimal('0.001') instead of Decimal(0), while answer_price_unit is initialized to Decimal(0) instead of Decimal('0.001'). This mirrors the correct initialization pattern used for message_unit_price and message_price_unit but with reversed values. This will cause incorrect pricing calculations when computing the total cost of agent responses, potentially leading to billing discrepancies or revenue loss.

GT 片段：`answer="", ⏎ observation="", ⏎ answer_token=0, ⏎ answer_unit_price=Decimal("0.001"),`

**finding**（`api/core/agent/base_agent_runner.py:319`，距錨點 3 行，候選管道 loc）create_agent_thought 中 message_unit_price 和 answer_unit_price 的預設值可能不合理

> 在 `create_agent_thought` 中，`message_unit_price` 設為 `Decimal(0)`，`answer_unit_price` 設為 `Decimal("0.001")`，而 `message_price_unit` 設為 `Decimal("0.001")`，`answer_price_unit` 設為 `Decimal(0)`。這些值可能與實際計費邏輯不符，且與模型定義的預設值不一致。

失敗情境：若後續計算總價時使用這些值，可能導致金額錯誤。

建議：確認這些預設值是否符合業務邏輯，並與模型定義保持一致。

finding 片段：`message_unit_price=Decimal(0), ⏎ message_price_unit=Decimal("0.001"), ⏎ message_files=json.dumps(messages_ids) if messages_ids else "", ⏎ answer="",`

## base-2:dify-11:5|dify-11#2

**GT**（func）Type mismatch in total_price initialization breaks Decimal arithmetic

> The total_price field is initialized with integer 0 instead of Decimal(0), creating a type inconsistency. The MessageAgentThought model defines total_price as Mapped[Decimal | None] expecting a Decimal type, and other price fields (message_unit_price, answer_unit_price, etc.) are correctly initialized with Decimal types. This inconsistency will cause type errors during price calculations when the system attempts to perform Decimal arithmetic operations (addition, multiplication) between Decimal and int types, potentially breaking billing computations or causing runtime exceptions.

GT 片段：`answer_price_unit=Decimal(0), ⏎ tokens=0, ⏎ total_price=0, ⏎ position=self.agent_thought_count + 1,`

**finding**（`api/core/agent/base_agent_runner.py:319`，距錨點 7 行，候選管道 ident）create_agent_thought 中 message_unit_price 和 answer_unit_price 的預設值可能不合理

> 在 `create_agent_thought` 中，`message_unit_price` 設為 `Decimal(0)`，`answer_unit_price` 設為 `Decimal("0.001")`，而 `message_price_unit` 設為 `Decimal("0.001")`，`answer_price_unit` 設為 `Decimal(0)`。這些值可能與實際計費邏輯不符，且與模型定義的預設值不一致。

失敗情境：若後續計算總價時使用這些值，可能導致金額錯誤。

建議：確認這些預設值是否符合業務邏輯，並與模型定義保持一致。

finding 片段：`message_unit_price=Decimal(0), ⏎ message_price_unit=Decimal("0.001"), ⏎ message_files=json.dumps(messages_ids) if messages_ids else "", ⏎ answer="",`

## base-2:dify-12:1|dify-12#1

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行，候選管道 loc）notlike 未指定 escape 參數，跳脫失效

> 在 `case "not contains"` 分支中，呼叫 `json_field.notlike(f"%{escaped_value}%")` 時未傳入 `escape="\\"`。這會導致資料庫將跳脫後的反斜線視為一般字元，而非跳脫字元，因此 `%` 和 `_` 仍會被當作萬用字元，造成查詢結果錯誤。

**失敗情境**：當使用者搜尋包含 `%` 或 `_` 的字串時，`not contains` 條件會錯誤地排除或包含不應匹配的記錄。

**建議**：加上 `escape="\\"` 參數，與其他分支保持一致。

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## base-2:dify-12:3|dify-12#3

**GT**（func）Keyword trimming logic may break escape sequences

> The workflow app service trims the keyword to 30 characters and then applies escape_like_pattern(). However, this creates a subtle bug: if a backslash character appears exactly at position 30, the trim could split an escape sequence that the user intended. More critically, if special characters appear in positions 28-30, they'll be included in the escaped output, but any context around them will be lost, potentially creating malformed escape sequences. The trimming should occur AFTER escaping to preserve the integrity of the escape sequences, or better yet, the escaping should be done before any string manipulation.

GT 片段：`# Escape special characters in keyword to prevent SQL injection via LIKE wildcards ⏎ keyword_trimmed = keyword[:30] ⏎ escaped_keyword = escape_like_pattern(keyword_trimmed) ⏎ keyword_like_val = f"%{escaped_keyword}%"`

**finding**（`api/services/workflow_app_service.py:94`，距錨點 0 行，候選管道 loc）移除 unicode_escape 可能改變既有行為

> 原本的程式碼使用 `keyword[:30].encode('unicode_escape').decode('utf-8')` 來處理關鍵字，這會將非 ASCII 字元轉換為 `\uXXXX` 形式。新的程式碼直接使用 `escape_like_pattern`，不再進行 unicode 轉義。這可能導致對非 ASCII 字元的搜尋行為改變，尤其是當資料庫中的 JSON 欄位以 unicode 轉義儲存時。

**失敗情境**：如果 WorkflowRun.inputs 或 outputs 中的 JSON 是以 unicode 轉義儲存（例如 `\u4e2d\u6587`），則搜尋中文字串時可能無法匹配。

**建議**：確認 JSON 欄位的儲存格式，若需要保留 unicode 轉義，應在跳脫前先進行轉換。

finding 片段：`keyword_like_val = f"%{escaped_keyword}%"`

## base-2:dify-12:4|dify-12#2

**GT**（func）Incorrect escape character in IRIS vector database LIKE query

> The IRIS vector database implementation escapes special characters using backslash (via escape_like_pattern which produces \%, \_, \\) but then specifies ESCAPE '|' in the SQL query instead of ESCAPE '\'. This mismatch causes the database to look for the wrong escape character - it will treat | as the escape character while the string contains backslash escapes. As a result, the escaped special characters won't be properly interpreted, allowing SQL wildcards to remain active and causing search queries with special characters to produce incorrect results or security vulnerabilities.

GT 片段：`escaped_query = escape_like_pattern(query) ⏎ query_pattern = f"%{escaped_query}%" ⏎ sql = f""" ⏎ SELECT TOP {top_k} id, text, meta`

**finding**（`api/core/rag/datasource/vdb/iris/iris_vector.py:298`，距錨點 0 行，候選管道 loc）IRIS 的 ESCAPE 子句使用 '|' 但跳脫函式使用反斜線

> 在 IRIS 的 LIKE 查詢中，使用了 `ESCAPE '|'`，但 `escape_like_pattern` 函式是使用反斜線作為跳脫字元。這會導致跳脫字元不一致：函式將 `%` 跳脫為 `\%`，但資料庫期望的跳脫字元是 `|`，因此 `\%` 不會被正確解析。

**失敗情境**：當查詢包含 `%` 或 `_` 時，IRIS 可能將 `\%` 視為兩個字元（反斜線和 `%`），導致匹配失敗或錯誤匹配。

**建議**：要麼修改 `escape_like_pattern` 以支援自訂跳脫字元，要麼在呼叫前將跳脫後的字串中的反斜線替換為 `|`。

finding 片段：`WHERE text LIKE ? ESCAPE '|'`

## base-2:dify-13:1|dify-13#0

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行，候選管道 loc）start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致

> 在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## base-2:dify-13:1|dify-13#1

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行，候選管道 loc）start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致

> 在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## base-2:dify-13:1|dify-13#2

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 19 行，候選管道 ident）start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致

> 在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## base-2:dify-13:2|dify-13#0

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行，候選管道 loc）使用 print 輸出日誌，應改用 logging

> 在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-2:dify-13:2|dify-13#1

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行，候選管道 loc）使用 print 輸出日誌，應改用 logging

> 在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-2:dify-13:2|dify-13#2

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 20 行，候選管道 ident）使用 print 輸出日誌，應改用 logging

> 在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-2:dify-13:3|dify-13#0

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行，候選管道 ident）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 在 _propagate_skip_to_node 中，原本先 mark_edge_skipped 再 propagate_skip_from_edge，現在順序對調。若 propagate_skip_from_edge 內部依賴邊的 skipped 狀態（例如 analyze_edge_states 會檢查），則可能導致行為不同。需確認此變更是否為修正所需，並驗證遞迴邏輯仍正確。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## base-2:dify-13:3|dify-13#1

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行，候選管道 ident）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 在 _propagate_skip_to_node 中，原本先 mark_edge_skipped 再 propagate_skip_from_edge，現在順序對調。若 propagate_skip_from_edge 內部依賴邊的 skipped 狀態（例如 analyze_edge_states 會檢查），則可能導致行為不同。需確認此變更是否為修正所需，並驗證遞迴邏輯仍正確。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## base-2:dify-13:3|dify-13#2

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行，候選管道 loc）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 在 _propagate_skip_to_node 中，原本先 mark_edge_skipped 再 propagate_skip_from_edge，現在順序對調。若 propagate_skip_from_edge 內部依賴邊的 skipped 狀態（例如 analyze_edge_states 會檢查），則可能導致行為不同。需確認此變更是否為修正所需，並驗證遞迴邏輯仍正確。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## base-2:dify-2:1|dify-2#0

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:139`，距錨點 0 行，候選管道 loc）回傳值 True 應為 true

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但在 JavaScript/TypeScript 中應為 `true`。這會導致呼叫端若依賴此回傳值判斷是否成功，將得到 ReferenceError（若未定義 True）或非預期的 truthy 值。

建議改為 `return true`。

finding 片段：`return True`

## base-2:dify-2:1|dify-2#1

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:139`，距錨點 0 行，候選管道 loc）回傳值 True 應為 true

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但在 JavaScript/TypeScript 中應為 `true`。這會導致呼叫端若依賴此回傳值判斷是否成功，將得到 ReferenceError（若未定義 True）或非預期的 truthy 值。

建議改為 `return true`。

finding 片段：`return True`

## base-2:dify-2:2|dify-2#2

**GT**（func）JSON schema cleared for all variable types, not just jsonObject

> The payloadToSave logic removes the json_schema field whenever isSchemaEmpty is true, regardless of the variable type. The original code correctly checked `tempPayload.type === InputVarType.jsonObject && isSchemaEmpty`. By removing the type check, if a user switches from jsonObject type to another type (like textInput) and the schema happens to be empty, the json_schema field gets cleared even though it should be preserved during the transition. This causes data loss when users change variable types back and forth.

GT 片段：`// if the input type is jsonObject and the schema is empty as determined by `isJsonSchemaEmpty`, ⏎ // remove the `json_schema` field from the payload by setting its value to `undefined`. ⏎ const payloadToSave = isSchemaEmpty ⏎ ? { ...tempPayload, json_schema: undefined }`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:255`，距錨點 0 行，候選管道 loc）payloadToSave 可能意外移除 json_schema

> 在 handleConfirm 中，若 isSchemaEmpty 為 true，則將 json_schema 設為 undefined。但此邏輯套用於所有型別，而不僅限於 jsonObject。若其他型別（如 string、number）的 tempPayload 中殘留了 json_schema 欄位（例如使用者先選 jsonObject 再切換型別），此變更會將該欄位移除，可能導致非預期的資料遺失。

建議僅在 type === InputVarType.jsonObject 時才進行此正規化。

finding 片段：`const payloadToSave = isSchemaEmpty ⏎ ? { ...tempPayload, json_schema: undefined } ⏎ : tempPayload`

## base-2:dify-2:2|dify-2#4

**GT**（rule）Dead store / unused variable `normalizedJsonSchema`

> SonarJS no-dead-store is enforced at error level. `normalizedJsonSchema` is assigned but never used afterwards, making it a dead store and a lint violation.

GT 片段：`const jsonSchemaValue = tempPayload.json_schema ⏎ const isSchemaEmpty = isJsonSchemaEmpty(jsonSchemaValue) ⏎ const normalizedJsonSchema = isSchemaEmpty ? undefined : jsonSchemaValue`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:255`，距錨點 4 行，候選管道 loc）payloadToSave 可能意外移除 json_schema

> 在 handleConfirm 中，若 isSchemaEmpty 為 true，則將 json_schema 設為 undefined。但此邏輯套用於所有型別，而不僅限於 jsonObject。若其他型別（如 string、number）的 tempPayload 中殘留了 json_schema 欄位（例如使用者先選 jsonObject 再切換型別），此變更會將該欄位移除，可能導致非預期的資料遺失。

建議僅在 type === InputVarType.jsonObject 時才進行此正規化。

finding 片段：`const payloadToSave = isSchemaEmpty ⏎ ? { ...tempPayload, json_schema: undefined } ⏎ : tempPayload`

## base-2:dify-2:3|dify-2#3

**GT**（func）JSON schema validation uses non-normalized value

> The validation logic for jsonObject type validates jsonSchemaValue instead of normalizedJsonSchema. This is problematic because normalizedJsonSchema is computed earlier and correctly handles the case where an empty schema should be undefined. By validating jsonSchemaValue directly, the code validates the raw tempPayload value instead of the cleaned version. This inconsistency means that validation may pass but the wrong data could be saved, or validation may fail when it should succeed if the schema is empty but not yet normalized.

GT 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue) ⏎ if (schema?.type !== 'object') {`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:314`，距錨點 0 行，候選管道 loc）JSON Schema 驗證僅檢查 type 為 object，未驗證完整結構

> 在 handleConfirm 的 jsonObject 分支中，僅檢查 schema.type === 'object'，但未驗證 schema 是否符合 JSON Schema 規範（例如 properties 是否為物件、required 是否為陣列等）。若後端依賴 schema 的完整性，可能導致後續處理錯誤。

建議使用 JSON Schema 驗證函式庫（如 ajv）進行完整驗證，或至少檢查必要欄位。

finding 片段：`if (schema?.type !== 'object') { ⏎ Toast.notify({ type: 'error', message: t('variableConfig.errorMsg.jsonSchemaMustBeObject', { ns: 'appDebug' }) }) ⏎ return ⏎ }`

## base-2:dify-3:1|dify-3#1

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:37`，距錨點 0 行，候選管道 loc）render_template 可能回傳 None，導致後續 len() 拋出 TypeError

> 在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 中 `result` 鍵的值為 `None`，則方法會直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，對 `None` 呼叫 `len()` 會拋出 `TypeError`，且此例外未被捕捉，導致節點以未處理例外失敗，而非回傳明確的錯誤訊息。

**失敗情境**：當模板渲染結果為空（例如模板僅包含註解或空白控制）時，`execute_workflow_code_template` 可能回傳 `{'result': None}`，觸發此問題。

**建議修法**：在 `render_template` 中，若 `rendered` 為 `None`，應拋出 `TemplateRenderError`，例如：
```python
if rendered is None:
    raise TemplateRenderError("Template render result is None.")
```
或將型別檢查改為：
```python
if not isinstance(rendered, str):
    raise TemplateRenderError("Template render result must be a string.")
```

finding 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

## base-2:dify-4:1|dify-4#0

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行，候選管道 loc）Session 未正確關閉，可能導致連線洩漏

> 在 `ConversationVariableUpdaterImpl.update` 中，`session = Session(db.engine)` 建立的 session 在方法結束後沒有被關閉。若 `session.commit()` 拋出例外，session 不會被釋放，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保 session 關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## base-2:dify-4:1|dify-4#4

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行，候選管道 loc）Session 未正確關閉，可能導致連線洩漏

> 在 `ConversationVariableUpdaterImpl.update` 中，`session = Session(db.engine)` 建立的 session 在方法結束後沒有被關閉。若 `session.commit()` 拋出例外，session 不會被釋放，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保 session 關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## base-2:dify-4:2|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行，候選管道 loc）在迴圈內呼叫 flush，可能造成不必要的資料庫往返

> `self._conversation_variable_updater.flush()` 在 for 迴圈內被呼叫，若有多個 conversation variables 需要更新，會導致多次 flush。建議將 flush 移到迴圈外，在所有 update 完成後只呼叫一次。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## base-2:dify-4:2|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行，候選管道 loc）在迴圈內呼叫 flush，可能造成不必要的資料庫往返

> `self._conversation_variable_updater.flush()` 在 for 迴圈內被呼叫，若有多個 conversation variables 需要更新，會導致多次 flush。建議將 flush 移到迴圈外，在所有 update 完成後只呼叫一次。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## base-2:dify-4:3|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:34`，距錨點 4 行，候選管道 loc）conversation_id 缺失時靜默跳過，可能導致資料不一致

> 在 `ConversationVariablePersistenceLayer.on_event` 中，若 `conversation_id` 為 `None`，則直接 `return`，沒有記錄任何警告或錯誤。在非 debugger 情境下，這可能導致 conversation variable 更新被靜默丟棄，造成資料不一致。建議至少記錄 warning log，或考慮拋出例外。

finding 片段：`conversation_id = self.graph_runtime_state.system_variable.conversation_id ⏎ if conversation_id is None: ⏎ return`

## base-2:dify-4:3|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:34`，距錨點 18 行，候選管道 ident）conversation_id 缺失時靜默跳過，可能導致資料不一致

> 在 `ConversationVariablePersistenceLayer.on_event` 中，若 `conversation_id` 為 `None`，則直接 `return`，沒有記錄任何警告或錯誤。在非 debugger 情境下，這可能導致 conversation variable 更新被靜默丟棄，造成資料不一致。建議至少記錄 warning log，或考慮拋出例外。

finding 片段：`conversation_id = self.graph_runtime_state.system_variable.conversation_id ⏎ if conversation_id is None: ⏎ return`

## base-2:dify-4:4|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 0 行，候選管道 loc）selector 長度檢查可能不完整

> `if len(selector) < 2:` 只檢查 selector 至少有兩個元素，但未驗證 selector[0] 是否為合法的 conversation variable node ID。若 selector[0] 不是 `CONVERSATION_VARIABLE_NODE_ID`，後續 `continue` 會跳過，但這可能掩蓋其他問題。建議增加更明確的驗證或 log。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## base-2:dify-4:4|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 12 行，候選管道 ident）selector 長度檢查可能不完整

> `if len(selector) < 2:` 只檢查 selector 至少有兩個元素，但未驗證 selector[0] 是否為合法的 conversation variable node ID。若 selector[0] 不是 `CONVERSATION_VARIABLE_NODE_ID`，後續 `continue` 會跳過，但這可能掩蓋其他問題。建議增加更明確的驗證或 log。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## base-2:dify-5:1|dify-5#0

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行，候選管道 loc）新增的 console.log 可能洩漏批次輸入資料

> 在生產程式碼中新增了 `console.log('Checking batch inputs:', { dataLength: data.length, headerData })`，這會將使用者上傳的批次輸入資料（至少包含標頭列）輸出到瀏覽器主控台。如果資料包含敏感資訊（例如個人資料），可能造成隱私外洩。建議移除這行 console.log，或改用適當的日誌機制（如 debug 級別且不輸出資料內容）。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## base-2:dify-5:2|dify-5#3

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行，候選管道 loc）數字輸入的 type 從 'number' 改為 'text' 可能破壞數字驗證

> 原本 `<Input type="number" ...>` 改為 `<Input type="text" ...>`，這會讓瀏覽器不再限制輸入為數字，使用者可以輸入任意文字。如果後端預期收到數字，可能導致型別錯誤或驗證失敗。建議保留 `type="number"`，或明確說明為何需要改為文字輸入（例如為了自訂格式），並確保有適當的驗證。

finding 片段：`type="text"`

## base-2:dify-5:3|dify-5#1

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行，候選管道 loc）當 max_length 未定義時，長度檢查失效

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在改為直接使用 `varItem.max_length`。如果 `varItem.max_length` 是 `undefined`，則 `item[varIndex].length > undefined` 會是 `false`（因為 `undefined` 會被轉成 `NaN`，任何比較都為 false），導致長度檢查永遠不會觸發，可能允許超長輸入。建議保留預設值，或明確處理 `max_length` 未定義的情況（例如視為無限制）。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## base-2:dify-5:3|dify-5#4

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行，候選管道 loc）當 max_length 未定義時，長度檢查失效

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在改為直接使用 `varItem.max_length`。如果 `varItem.max_length` 是 `undefined`，則 `item[varIndex].length > undefined` 會是 `false`（因為 `undefined` 會被轉成 `NaN`，任何比較都為 false），導致長度檢查永遠不會觸發，可能允許超長輸入。建議保留預設值，或明確處理 `max_length` 未定義的情況（例如視為無限制）。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## base-2:dify-6:1|dify-6#0

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行，候選管道 loc）重構後 opportunistic TLS 連線建立方式可能與原本不同

> 原本在 opportunistic TLS 模式下，會先建立非 SSL 的 SMTP 連線，然後呼叫 ehlo、starttls、再 ehlo。重構後，連線建立改為根據條件選擇 SMTP_SSL 或 SMTP，但 opportunistic TLS 模式仍使用 SMTP（非 SSL），因此行為看似相同。然而，原本的程式碼在建立 SMTP 連線時沒有傳入 local_hostname，而新程式碼傳入了 local_hostname（可能為空字串或 None）。如果 local_hostname 為空字串，smtplib 可能將其視為有效的主機名稱，導致 HELO/EHLO 命令使用空字串，可能被伺服器拒絕。建議確認 smtplib 對空字串的處理，並考慮在 local_hostname 為空時不傳遞該參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-2:dify-6:1|dify-6#1

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行，候選管道 loc）重構後 opportunistic TLS 連線建立方式可能與原本不同

> 原本在 opportunistic TLS 模式下，會先建立非 SSL 的 SMTP 連線，然後呼叫 ehlo、starttls、再 ehlo。重構後，連線建立改為根據條件選擇 SMTP_SSL 或 SMTP，但 opportunistic TLS 模式仍使用 SMTP（非 SSL），因此行為看似相同。然而，原本的程式碼在建立 SMTP 連線時沒有傳入 local_hostname，而新程式碼傳入了 local_hostname（可能為空字串或 None）。如果 local_hostname 為空字串，smtplib 可能將其視為有效的主機名稱，導致 HELO/EHLO 命令使用空字串，可能被伺服器拒絕。建議確認 smtplib 對空字串的處理，並考慮在 local_hostname 為空時不傳遞該參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-2:dify-6:1|dify-6#2

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行，候選管道 loc）重構後 opportunistic TLS 連線建立方式可能與原本不同

> 原本在 opportunistic TLS 模式下，會先建立非 SSL 的 SMTP 連線，然後呼叫 ehlo、starttls、再 ehlo。重構後，連線建立改為根據條件選擇 SMTP_SSL 或 SMTP，但 opportunistic TLS 模式仍使用 SMTP（非 SSL），因此行為看似相同。然而，原本的程式碼在建立 SMTP 連線時沒有傳入 local_hostname，而新程式碼傳入了 local_hostname（可能為空字串或 None）。如果 local_hostname 為空字串，smtplib 可能將其視為有效的主機名稱，導致 HELO/EHLO 命令使用空字串，可能被伺服器拒絕。建議確認 smtplib 對空字串的處理，並考慮在 local_hostname 為空時不傳遞該參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-2:dify-6:1|dify-6#3

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行，候選管道 loc）重構後 opportunistic TLS 連線建立方式可能與原本不同

> 原本在 opportunistic TLS 模式下，會先建立非 SSL 的 SMTP 連線，然後呼叫 ehlo、starttls、再 ehlo。重構後，連線建立改為根據條件選擇 SMTP_SSL 或 SMTP，但 opportunistic TLS 模式仍使用 SMTP（非 SSL），因此行為看似相同。然而，原本的程式碼在建立 SMTP 連線時沒有傳入 local_hostname，而新程式碼傳入了 local_hostname（可能為空字串或 None）。如果 local_hostname 為空字串，smtplib 可能將其視為有效的主機名稱，導致 HELO/EHLO 命令使用空字串，可能被伺服器拒絕。建議確認 smtplib 對空字串的處理，並考慮在 local_hostname 為空時不傳遞該參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-2:dify-6:2|dify-6#0

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行，候選管道 loc）assert smtp is not None 可能不是必要的

> 新增的 assert smtp is not None 在連線建立後立即執行，但 smtp 變數在 try 區塊內被賦值，且型別標註為 smtplib.SMTP | None。由於連線建立函式不會回傳 None，此 assert 可能永遠不會觸發，但若未來修改導致可能為 None，assert 在最佳化模式下會被移除，無法提供保護。建議移除或改為明確的型別檢查。

finding 片段：`assert smtp is not None`

## base-2:dify-6:2|dify-6#1

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:32`，距錨點 0 行，候選管道 loc）assert smtp is not None 可能不是必要的

> 新增的 assert smtp is not None 在連線建立後立即執行，但 smtp 變數在 try 區塊內被賦值，且型別標註為 smtplib.SMTP | None。由於連線建立函式不會回傳 None，此 assert 可能永遠不會觸發，但若未來修改導致可能為 None，assert 在最佳化模式下會被移除，無法提供保護。建議移除或改為明確的型別檢查。

finding 片段：`assert smtp is not None`

## base-2:dify-6:2|dify-6#2

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:32`，距錨點 7 行，候選管道 ident）assert smtp is not None 可能不是必要的

> 新增的 assert smtp is not None 在連線建立後立即執行，但 smtp 變數在 try 區塊內被賦值，且型別標註為 smtplib.SMTP | None。由於連線建立函式不會回傳 None，此 assert 可能永遠不會觸發，但若未來修改導致可能為 None，assert 在最佳化模式下會被移除，無法提供保護。建議移除或改為明確的型別檢查。

finding 片段：`assert smtp is not None`

## base-2:dify-6:2|dify-6#3

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行，候選管道 loc）assert smtp is not None 可能不是必要的

> 新增的 assert smtp is not None 在連線建立後立即執行，但 smtp 變數在 try 區塊內被賦值，且型別標註為 smtplib.SMTP | None。由於連線建立函式不會回傳 None，此 assert 可能永遠不會觸發，但若未來修改導致可能為 None，assert 在最佳化模式下會被移除，無法提供保護。建議移除或改為明確的型別檢查。

finding 片段：`assert smtp is not None`

## base-2:dify-7:1|dify-7#0

**GT**（rule）Interface used instead of type

> The rule requires using 'type' keyword for type declarations, but the code uses 'interface' declaration instead

GT 片段：`interface TranslationMap extends Record<string, string | string[]> {}`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 6 行，候選管道 ident）createTFunction 未處理 returnObjects 選項

> 舊的全域 mock 在 `options.returnObjects` 為真時會回傳陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`），但新的 `createTFunction` 完全沒有處理這個選項，而是將 `returnObjects` 視為一般參數，導致回傳字串（例如 `key:{"returnObjects":true}`）。這可能造成依賴此行為的測試失敗。

建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects) {
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
}
```

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-2:dify-7:1|dify-7#1

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 29 行，候選管道 ident）createTFunction 未處理 returnObjects 選項

> 舊的全域 mock 在 `options.returnObjects` 為真時會回傳陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`），但新的 `createTFunction` 完全沒有處理這個選項，而是將 `returnObjects` 視為一般參數，導致回傳字串（例如 `key:{"returnObjects":true}`）。這可能造成依賴此行為的測試失敗。

建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects) {
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
}
```

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-2:dify-7:1|dify-7#2

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行，候選管道 loc）createTFunction 未處理 returnObjects 選項

> 舊的全域 mock 在 `options.returnObjects` 為真時會回傳陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`），但新的 `createTFunction` 完全沒有處理這個選項，而是將 `returnObjects` 視為一般參數，導致回傳字串（例如 `key:{"returnObjects":true}`）。這可能造成依賴此行為的測試失敗。

建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects) {
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
}
```

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-2:dify-7:1|dify-7#3

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行，候選管道 loc）createTFunction 未處理 returnObjects 選項

> 舊的全域 mock 在 `options.returnObjects` 為真時會回傳陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`），但新的 `createTFunction` 完全沒有處理這個選項，而是將 `returnObjects` 視為一般參數，導致回傳字串（例如 `key:{"returnObjects":true}`）。這可能造成依賴此行為的測試失敗。

建議在 `createTFunction` 中加入對 `returnObjects` 的處理，例如：
```typescript
if (options?.returnObjects) {
  return [`${fullKey}-feature-1`, `${fullKey}-feature-2`]
}
```

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-2:dify-8:1|dify-8#0

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行，候選管道 ident）React Scan 載入失敗時靜默降級，可能隱藏錯誤

> 當 `import('./scan')` 失敗時，`.catch` 回傳一個渲染 `null` 的元件，導致 devtools 完全不出現且沒有任何使用者可見的提示。雖然有 `console.error`，但在 production 環境中可能被忽略。建議在開發環境中顯示一個明顯的錯誤訊息，或至少保留錯誤狀態供後續處理。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## base-2:dify-8:1|dify-8#4

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行，候選管道 loc）React Scan 載入失敗時靜默降級，可能隱藏錯誤

> 當 `import('./scan')` 失敗時，`.catch` 回傳一個渲染 `null` 的元件，導致 devtools 完全不出現且沒有任何使用者可見的提示。雖然有 `console.error`，但在 production 環境中可能被忽略。建議在開發環境中顯示一個明顯的錯誤訊息，或至少保留錯誤狀態供後續處理。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## base-2:dify-8:2|dify-8#2

**GT**（func）Missing error logging in TanStack devtools lazy import

> The TanStackDevtoolsLoader silently swallows import errors without logging them, making it impossible to debug why the devtools fail to load. This creates an inconsistent error handling pattern compared to the ReactScanLoader (in the same PR), which properly logs errors with console.error before returning a fallback component. When developers encounter issues with TanStack devtools not appearing, they will have no visibility into whether it's due to an import failure, missing dependencies, or other issues.

GT 片段：`const TanStackDevtoolsWrapper = lazy(() => ⏎ import('./devtools').then(module => ({ ⏎ default: module.TanStackDevtoolsWrapper, ⏎ })).catch(() => {`

**finding**（`web/app/components/devtools/tanstack/loader.tsx:9`，距錨點 0 行，候選管道 loc）TanStack devtools 載入失敗時完全吞掉錯誤

> `.catch(() => { return { default: () => null } })` 沒有記錄任何錯誤，若動態載入失敗，開發者將無法得知原因。建議至少加上 `console.error` 或類似的錯誤記錄。

finding 片段：`.catch(() => { ⏎ return { default: () => null } ⏎ })`

## base-2:dify-9:1|dify-9#1

**GT**（func）Query parameter naming collision between plugin page and marketplace

> The plugin page context changed from 'category' to 'tab' query parameter (line 71), but the marketplace useActivePluginType still uses 'tab' instead of 'category' (line 23 in atoms.ts). This creates a naming collision where both components try to control the same 'tab' URL query parameter for different purposes. When users navigate between the plugin page tabs and marketplace categories, the URL state will conflict causing incorrect active states and navigation issues. The marketplace should use 'category' parameter while the plugin page uses 'tab' parameter to maintain their independent states.

GT 片段：`export function useActivePluginType() { ⏎ return useQueryState('tab', marketplaceSearchParamsParsers.category) ⏎ }`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:43`，距錨點 20 行，候選管道 ident）布林邏輯變更可能導致搜尋模式判斷錯誤

> 原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在變成 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。這會反轉當 `searchMode` 為 null/undefined 時的預設行為：原本不在集合中的分類會進入搜尋模式，現在變成在集合中的分類才會進入搜尋模式。請確認此變更是否為預期，否則可能導致 marketplace 在非搜尋情境下錯誤顯示搜尋模式。

finding 片段：`|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`

## base-2:dify-9:1|dify-9#2

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:43`，距錨點 0 行，候選管道 loc）布林邏輯變更可能導致搜尋模式判斷錯誤

> 原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在變成 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!`。這會反轉當 `searchMode` 為 null/undefined 時的預設行為：原本不在集合中的分類會進入搜尋模式，現在變成在集合中的分類才會進入搜尋模式。請確認此變更是否為預期，否則可能導致 marketplace 在非搜尋情境下錯誤顯示搜尋模式。

finding 片段：`|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`

## base-2:dify-9:2|dify-9#0

**GT**（rule）Any type used for selector parameter

> The rule requires using specific types instead of 'any' annotations. The selector parameter uses 'any' instead of a proper function type signature.

GT 片段：`export function usePluginPageContext(selector: any) { ⏎ return useContextSelector(PluginPageContext, selector) ⏎ }`

**finding**（`web/app/components/plugins/plugin-page/context.tsx:51`，距錨點 0 行，候選管道 loc）selector 型別放寬為 any 喪失型別安全

> `usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會讓呼叫端可以傳入任何值，失去編譯時期的型別檢查。若傳入非函式，`useContextSelector` 可能拋出錯誤或產生非預期行為。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => unknown`。

finding 片段：`export function usePluginPageContext(selector: any) {`

## base-2:firefox-ios-1:1|firefox-ios-1#2

**GT**（func）Inconsistent format specifier documentation in RolloutsSettingMessage comment

> The comment for RolloutsSettingMessage incorrectly documents the format specifier as '%1$@' (positional format) while the actual value string uses '%@' (simple format). This mismatch creates confusion for localization teams and could lead to incorrect translations, as translators may attempt to use positional formatting based on the comment when the string implementation doesn't support it. The comment should match the actual format specifier used in the value field.

GT 片段：`public static let RolloutsSettingMessage = MZLocalizedString( ⏎ key: "Settings.Rollouts.Message.v148", ⏎ tableName: "Settings", ⏎ value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.",`

**finding**（`firefox-ios/Shared/Strings.swift:6260`，距錨點 0 行，候選管道 loc）Rollouts 訊息字串使用 %@ 但 comment 標示 %1$@，可能導致格式錯誤

> `RolloutsSettingMessage` 的 value 使用 `%@`，但 comment 中說明為 `%1$@`。在 iOS 的 `String(format:)` 中，`%@` 與 `%1$@` 皆可接受，但若其他語言翻譯時依 comment 使用位置參數，可能造成格式不一致。建議統一使用 `%@` 或 `%1$@`，並更新 comment。

finding 片段：`value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", ⏎ comment: "A short description that explains that Mozilla may change features remotely. %1$@ is the app name (e.g. Firefox).")`

## base-2:firefox-ios-1:2|firefox-ios-1#0

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行，候選管道 loc）SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2

> `formatStudiesText` 方法使用 `strings.detailTextStudies`，但此 PR 新增了 `detailTextStudiesV2`，且新的 Studies 標題與訊息皆已更新。若 UI 應顯示新版文字，此處應改用 `detailTextStudiesV2`，否則使用者會看到舊的說明。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

## base-2:firefox-ios-1:2|firefox-ios-1#1

**GT**（func）Incorrect localized string reference in SettingsTextFormatter

> The formatStudiesText method references strings.detailTextStudies instead of strings.detailTextStudiesV2. This causes the formatter to display the old v1 Studies message ('%@ may install and run studies from time to time.') instead of the new v148 message ('%@ randomly selects users to test features, which improves quality for everyone.') that was added in this PR. The helper class was clearly intended to format the new v148 strings based on the PR context, but uses the wrong string constant.

GT 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行，候選管道 loc）SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2

> `formatStudiesText` 方法使用 `strings.detailTextStudies`，但此 PR 新增了 `detailTextStudiesV2`，且新的 Studies 標題與訊息皆已更新。若 UI 應顯示新版文字，此處應改用 `detailTextStudiesV2`，否則使用者會看到舊的說明。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

## base-2:firefox-ios-1:2|firefox-ios-1#4

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行，候選管道 loc）SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2

> `formatStudiesText` 方法使用 `strings.detailTextStudies`，但此 PR 新增了 `detailTextStudiesV2`，且新的 Studies 標題與訊息皆已更新。若 UI 應顯示新版文字，此處應改用 `detailTextStudiesV2`，否則使用者會看到舊的說明。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

## base-2:firefox-ios-1:2|firefox-ios-1#5

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行，候選管道 loc）SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2

> `formatStudiesText` 方法使用 `strings.detailTextStudies`，但此 PR 新增了 `detailTextStudiesV2`，且新的 Studies 標題與訊息皆已更新。若 UI 應顯示新版文字，此處應改用 `detailTextStudiesV2`，否則使用者會看到舊的說明。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

## base-2:firefox-ios-1:2|firefox-ios-1#6

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 5 行，候選管道 loc）SettingsTextFormatter 使用舊版 detailTextStudies 而非 V2

> `formatStudiesText` 方法使用 `strings.detailTextStudies`，但此 PR 新增了 `detailTextStudiesV2`，且新的 Studies 標題與訊息皆已更新。若 UI 應顯示新版文字，此處應改用 `detailTextStudiesV2`，否則使用者會看到舊的說明。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

## base-2:firefox-ios-1:3|firefox-ios-1#3

**GT**（func）Linter exclusion points to wrong message key version

> The linter configuration exclusion was updated to reference 'Settings.Studies.Message.v148' but the original PR added this key to exclude quotes validation for the v136 message. Since the PR adds new v148 strings with similar content containing quotes, the exclusion should have remained as v136 to maintain the existing exclusion, or both versions should be excluded. This change will cause the linter to fail validation on the v136 string that legitimately needs the exclusion, while potentially missing issues in the new v148 string.

GT 片段：`"quotes": { ⏎ "enabled": true, ⏎ "exclusions": [ ⏎ "firefox-ios.xliff:Settings.Studies.Message.v148"`

**finding**（`.github/l10n/linter_config_ios.json:8`，距錨點 0 行，候選管道 loc）Linter 排除規則可能過於寬鬆

> 新增的排除規則 `"firefox-ios.xliff:Settings.Studies.Message.v148"` 僅針對特定 key，但若未來有其他類似格式問題，可能需要逐一排除。建議確認此排除是否必要，或改用更精確的規則。

finding 片段：`"exclusions": [ ⏎ "firefox-ios.xliff:Settings.Studies.Message.v148" ⏎ ]`

## base-2:firefox-ios-10:1|firefox-ios-10#1

**GT**（func）Test completes without waiting for async image download

> The test was converted from async to synchronous but the expectation and wait statement were removed. This causes the test to complete immediately without waiting for the asynchronous image download callback to execute. The XCTAssert statements inside the completion handler will never be verified, resulting in false positive test passes even if the image download fails or produces incorrect results. This is a critical testing bug that undermines test reliability.

GT 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ guard let imageData = try? dataFor(type: assetType) else {`

**finding**（`BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27`，距錨點 0 行，候選管道 loc）移除 expectation 可能導致測試提前結束

> 在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `expectation` 等待非同步下載完成，但現在移除了 `exp.fulfill()` 與 `await fulfillment`，且測試方法改為同步。這可能導致測試在非同步回呼執行前就結束，無法驗證下載結果，甚至可能造成測試通過但實際上未測試到任何內容。建議保留 expectation 或改用 async/await 等待非同步操作完成。

finding 片段：`siteDownloader.downloadImage(with: mockedURL, options: [.processor(SVGImageProcessor())]) { result in ⏎ switch result { ⏎ case .success(let result): ⏎ XCTAssertEqual(result.originalData, imageData)`

## base-2:firefox-ios-10:3|firefox-ios-10#3

**GT**（func）Async test assertion never verified due to missing expectation

> The test was updated to use @Sendable closures for Swift 6 concurrency compliance, but the expectation and wait statements were removed. The test now completes immediately without waiting for the asynchronous requestMediaCapturePermission callback. The XCTAssertEqual inside the decisionHandler closure will never execute, causing the test to always pass even when the media capture permission logic is broken. This is particularly problematic because this test validates critical permission handling behavior.

GT 片段：`func testRequestMediaCaptureSuccess() { ⏎ let subject = createSubject(isActive: true) ⏎ let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt)`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38`，距錨點 0 行，候選管道 model_line）移除 expectation 可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，原本使用 expectation 等待 decision handler 被呼叫，但現在移除了 `expectation.fulfill()` 與 `wait(for:)`。這可能導致測試在 handler 執行前就結束，無法驗證決策結果。建議保留 expectation 或改用 async/await。

finding 片段：`let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ }`

## base-2:firefox-ios-10:4|firefox-ios-10#0

**GT**（rule）Missing Mozilla Public License header

> The rule requires that every .swift file begins with the exact Mozilla Public License header comment block at the top of the file. This file is missing the required header entirely.

GT 片段：`import ContentBlockingGenerator ⏎ @main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行，候選管道 loc）nonisolated(unsafe) 可能隱藏執行緒安全問題

> 使用 `nonisolated(unsafe)` 標註靜態屬性，表示開發者已確認其執行緒安全性，但若 `ContentBlockerGenerator` 並非執行緒安全，可能導致資料競爭。建議確認該類別的執行緒安全性，或改用其他同步機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## base-2:firefox-ios-10:4|firefox-ios-10#4

**GT**（func）Unsafe concurrency annotation on non-thread-safe static property

> The static generator property is marked with nonisolated(unsafe) despite the comment explicitly stating 'ContentBlockerGenerator is not thread safe'. This annotation bypasses Swift 6's concurrency safety checks and allows the non-thread-safe ContentBlockerGenerator to be accessed from multiple isolation domains without protection. This creates a potential data race condition where multiple threads could access the generator simultaneously, leading to undefined behavior, crashes, or data corruption. The unsafe annotation should only be used when the developer can guarantee thread safety through other means, which the comment explicitly contradicts.

GT 片段：`@main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行，候選管道 loc）nonisolated(unsafe) 可能隱藏執行緒安全問題

> 使用 `nonisolated(unsafe)` 標註靜態屬性，表示開發者已確認其執行緒安全性，但若 `ContentBlockerGenerator` 並非執行緒安全，可能導致資料競爭。建議確認該類別的執行緒安全性，或改用其他同步機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## base-2:firefox-ios-10:4|firefox-ios-10#5

**GT**（rule）Static property missing explicit access control modifier

> Rule 11 requires explicit access control on properties/methods. The modified static property `generator` is declared without an explicit access modifier (e.g., `private`, `internal`, `public`).

GT 片段：`// FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行，候選管道 loc）nonisolated(unsafe) 可能隱藏執行緒安全問題

> 使用 `nonisolated(unsafe)` 標註靜態屬性，表示開發者已確認其執行緒安全性，但若 `ContentBlockerGenerator` 並非執行緒安全，可能導致資料競爭。建議確認該類別的執行緒安全性，或改用其他同步機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## base-2:firefox-ios-11:1|firefox-ios-11#2

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行，候選管道 loc）updateActionSpacing 中堆疊陣列重複加入 browserActionStack

> 在 `updateActionSpacing` 方法中，原本應包含 `trailingPageActionStack` 的陣列，卻重複加入了 `browserActionStack`，導致 `trailingPageActionStack` 未被納入動畫與間距更新。這可能造成頁面動作按鈕的動畫失效或間距不正確。

建議將第二個 `browserActionStack` 改為 `trailingPageActionStack`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## base-2:firefox-ios-11:2|firefox-ios-11#3

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行，候選管道 loc）骨架位址列約束可能誤用 rightSkeletonAddressBar

> 在 `setupSkeletonAddressBars` 中，`toolbar.leadingAnchor` 被約束到 `rightSkeletonAddressBar.trailingAnchor`，但根據前後文，此處應為 `leftSkeletonAddressBar.trailingAnchor`。這可能導致工具列在滑動分頁時位置錯誤。

建議改為 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## base-2:firefox-ios-11:3|firefox-ios-11#0

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行，候選管道 loc）使用已棄用的 statusBarOrientation API

> `UIApplication.shared.statusBarOrientation` 在 iOS 13 已棄用，建議改用 `view.window?.windowScene?.interfaceOrientation` 或 `traitCollection.verticalSizeClass` 來判斷方向。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## base-2:firefox-ios-11:3|firefox-ios-11#4

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行，候選管道 loc）使用已棄用的 statusBarOrientation API

> `UIApplication.shared.statusBarOrientation` 在 iOS 13 已棄用，建議改用 `view.window?.windowScene?.interfaceOrientation` 或 `traitCollection.verticalSizeClass` 來判斷方向。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## base-2:firefox-ios-12:1|firefox-ios-12#0

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行，候選管道 ident）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:1|firefox-ios-12#1

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 19 行，候選管道 ident）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:1|firefox-ios-12#2

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行，候選管道 loc）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:1|firefox-ios-12#7

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行，候選管道 loc）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:1|firefox-ios-12#8

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行，候選管道 ident）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:1|firefox-ios-12#9

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行，候選管道 ident）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:1|firefox-ios-12#10

**GT**（rule）Missing // MARK: section organization

> The new Swift file defines multiple logical sections (nested delegate type, static helper function) but includes no `// MARK:` comments to delineate them, violating the required section organization rule.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 31 行，候選管道 ident）XCTestExpectation 使用錯誤，可能導致測試永遠等待或提前結束

> 在 `captureFrameAndOrigin` 中，`XCTestExpectation` 被建立後，於 `FakeWKNavigationDelegate` 的 `decidePolicyFor` 中被 fulfill。然而，`XCTWaiter.wait(for:timeout:)` 是同步阻塞的，且 expectation 的 fulfill 發生在 delegate 回呼中，這可能導致測試永遠等待，因為 delegate 回呼可能發生在 waiter 開始等待之前，或者根本不會發生（例如網路請求失敗）。此外，在 `WKUIHandlerTests` 中，測試方法又建立了另一個 expectation 並在 decisionHandler 中 fulfill，但這個 expectation 從未被等待，而是直接呼叫 `wait(for: [expectation])`，這會造成測試永遠等待，因為 expectation 永遠不會被 fulfill。

建議：
1. 移除 `captureFrameAndOrigin` 中的 expectation 與 waiter，改為使用非同步測試方法（例如 `async`/`await` 或 `XCTestExpectation` 搭配 `waitForExpectations`）。
2. 在測試方法中，正確建立 expectation，並在 decisionHandler 中 fulfill，然後使用 `waitForExpectations(timeout:)` 等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## base-2:firefox-ios-12:2|firefox-ios-12#3

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:53`，距錨點 0 行，候選管道 loc）測試中的 expectation 未正確等待，可能導致測試永遠掛起

> 在 `testRequestMediaCaptureSuccess` 中，建立了 `expectation` 並在 decisionHandler 中呼叫 `expectation.fulfill()`，但之後直接呼叫 `wait(for: [expectation])`，而沒有使用 `waitForExpectations(timeout:)`。這會導致測試永遠等待，因為 `wait(for:)` 是 XCTestCase 的方法，它會等待所有傳入的 expectation 被 fulfill，但這裡的 expectation 從未被 fulfill（因為 decisionHandler 可能不會被呼叫，或者呼叫時機不正確）。

建議：使用 `waitForExpectations(timeout: 5.0)` 來等待，並確保 decisionHandler 一定會被呼叫。

finding 片段：`wait(for: [expectation])`

## base-2:firefox-ios-12:3|firefox-ios-12#1

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 17 行，候選管道 ident）測試依賴真實網路與外部服務，可能導致不穩定或離線失敗

> `captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試無法取得 frame 與 origin，進而失敗。此外，即使網路可用，外部服務的回應時間與內容可能變動，造成測試不穩定。

建議：使用本地測試伺服器或注入 mock 的 `WKNavigationAction` 來提供 frame 與 origin，避免依賴外部網路。

finding 片段：`webView.load(URLRequest(url: url))`

## base-2:firefox-ios-12:3|firefox-ios-12#2

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行，候選管道 loc）測試依賴真實網路與外部服務，可能導致不穩定或離線失敗

> `captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試無法取得 frame 與 origin，進而失敗。此外，即使網路可用，外部服務的回應時間與內容可能變動，造成測試不穩定。

建議：使用本地測試伺服器或注入 mock 的 `WKNavigationAction` 來提供 frame 與 origin，避免依賴外部網路。

finding 片段：`webView.load(URLRequest(url: url))`

## base-2:firefox-ios-12:3|firefox-ios-12#7

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行，候選管道 loc）測試依賴真實網路與外部服務，可能導致不穩定或離線失敗

> `captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試無法取得 frame 與 origin，進而失敗。此外，即使網路可用，外部服務的回應時間與內容可能變動，造成測試不穩定。

建議：使用本地測試伺服器或注入 mock 的 `WKNavigationAction` 來提供 frame 與 origin，避免依賴外部網路。

finding 片段：`webView.load(URLRequest(url: url))`

## base-2:firefox-ios-12:3|firefox-ios-12#8

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 20 行，候選管道 ident）測試依賴真實網路與外部服務，可能導致不穩定或離線失敗

> `captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試無法取得 frame 與 origin，進而失敗。此外，即使網路可用，外部服務的回應時間與內容可能變動，造成測試不穩定。

建議：使用本地測試伺服器或注入 mock 的 `WKNavigationAction` 來提供 frame 與 origin，避免依賴外部網路。

finding 片段：`webView.load(URLRequest(url: url))`

## base-2:firefox-ios-12:3|firefox-ios-12#9

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 8 行，候選管道 ident）測試依賴真實網路與外部服務，可能導致不穩定或離線失敗

> `captureFrameAndOrigin` 使用 `webView.load(URLRequest(url: url))` 載入 `https://example.com`，這需要實際的網路連線。在 CI 環境或離線狀態下，此請求可能失敗或逾時，導致測試無法取得 frame 與 origin，進而失敗。此外，即使網路可用，外部服務的回應時間與內容可能變動，造成測試不穩定。

建議：使用本地測試伺服器或注入 mock 的 `WKNavigationAction` 來提供 frame 與 origin，避免依賴外部網路。

finding 片段：`webView.load(URLRequest(url: url))`

## base-2:firefox-ios-12:4|firefox-ios-12#3

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38`，距錨點 5 行，候選管道 model_line）強制解包 URL 可能導致測試崩潰

> 在呼叫 `WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!)` 時，使用了強制解包。雖然 URL 字串是硬編碼且有效，但若未來修改為變數，可能引入崩潰風險。建議使用 `guard let url = URL(string: ...) else { XCTFail(); return }` 來處理。

finding 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

## base-2:firefox-ios-12:4|firefox-ios-12#4

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38`，距錨點 0 行，候選管道 model_line）強制解包 URL 可能導致測試崩潰

> 在呼叫 `WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!)` 時，使用了強制解包。雖然 URL 字串是硬編碼且有效，但若未來修改為變數，可能引入崩潰風險。建議使用 `guard let url = URL(string: ...) else { XCTFail(); return }` 來處理。

finding 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

## base-2:firefox-ios-12:4|firefox-ios-12#5

**GT**（rule）Force unwrap of URL initializer in tests (second occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38`，距錨點 0 行，候選管道 model_line）強制解包 URL 可能導致測試崩潰

> 在呼叫 `WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!)` 時，使用了強制解包。雖然 URL 字串是硬編碼且有效，但若未來修改為變數，可能引入崩潰風險。建議使用 `guard let url = URL(string: ...) else { XCTFail(); return }` 來處理。

finding 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

## base-2:firefox-ios-12:4|firefox-ios-12#6

**GT**（rule）Force unwrap of URL initializer in tests (third occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:38`，距錨點 0 行，候選管道 model_line）強制解包 URL 可能導致測試崩潰

> 在呼叫 `WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!)` 時，使用了強制解包。雖然 URL 字串是硬編碼且有效，但若未來修改為變數，可能引入崩潰風險。建議使用 `guard let url = URL(string: ...) else { XCTFail(); return }` 來處理。

finding 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

## base-2:firefox-ios-13:1|firefox-ios-13#1

**GT**（func）Incorrect logical operator in tearDown causing theme reset to be skipped for all iPad tests

> The tearDown method uses OR (||) instead of AND (&&) when checking if the test should skip theme reset. This causes the theme reset to be skipped for ALL tests running on iPad devices, not just the testSelectBottomPlacement test. The original intent was to skip theme reset only when BOTH conditions are true (the test is testSelectBottomPlacement AND it's running on iPad), but the current code skips it when EITHER condition is true. This will leave the theme in Dark mode after any test runs on iPad, potentially affecting subsequent tests that expect Light theme.

GT 片段：`override func tearDown() async throws { ⏎ if #available(iOS 17.0, *) { ⏎ if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there.`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29`，距錨點 0 行，候選管道 loc）tearDown 提前 return 可能略過清理與父類別 tearDown

> 在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立時直接 `return`，導致後續的 `app.terminate()` 與 `try await super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的獨立性。建議改為使用 `if` 條件包住 `switchThemeToDarkOrLight`，而不是提前 return，確保清理邏輯總會執行。

finding 片段：`if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there. ⏎ return ⏎ } else {`

## base-2:firefox-ios-13:2|firefox-ios-13#0

**GT**（rule）Test method missing test prefix

> The rule requires test methods to start with 'test' prefix, but the method 'verifyBookmarksShareNormalWebsiteReminders' does not follow this naming convention

GT 片段：`// https://mozilla.testrail.io/index.php?/cases/view/2864380 ⏎ func verifyBookmarksShareNormalWebsiteReminders() { ⏎ app.launch() ⏎ if #available(iOS 17, *) {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47`，距錨點 0 行，候選管道 loc）測試方法改名後失去 test 前綴，可能不再被 XCTest 執行

> 方法 `testBookmarksShareNormalWebsiteReminders` 被改名為 `verifyBookmarksShareNormalWebsiteReminders`，但 XCTest 只會自動執行以 `test` 開頭的方法。若沒有其他機制（例如手動呼叫或使用 `XCTestCase` 的 `testInvocations` 覆寫），此測試將不再被執行，等同於被停用。建議保留 `test` 前綴，或確認此方法是否由其他測試輔助呼叫。

finding 片段：`func verifyBookmarksShareNormalWebsiteReminders() {`

## base-2:firefox-ios-13:3|firefox-ios-13#2

**GT**（func）Insufficient timeout for paste permission dialog causing test flakiness

> The timeout for the 'Allow Paste' permission dialog button was reduced from 1.5 seconds to 0.5 seconds. This is too short for the iOS permission dialog to appear and be interactable, especially on slower devices or under load. The tapIfExists method waits for the element to exist within the specified timeout before attempting to tap it. A 0.5 second timeout may cause the test to miss the permission dialog entirely, preventing the paste action from completing and causing subsequent assertions to fail when the URL is not populated in the address bar.

GT 片段：`urlBar.pressWithRetry(duration: 2.0, element: pasteAction) ⏎ mozWaitForElementToExist(app.tables["Context Menu"]) ⏎ pasteAction.waitAndTap() ⏎ springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471`，距錨點 0 行，候選管道 loc）貼上後處理系統提示的時機可能不穩定

> 新增 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 來處理 iOS 的貼上權限提示。但此提示可能延遲出現，0.5 秒的等待時間可能不足，導致測試偶發失敗。建議增加等待時間或使用更可靠的等待機制（例如 `mozWaitForElementToExist`）。

finding 片段：`springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

## base-2:firefox-ios-2:1|firefox-ios-2#1

**GT**（func）Missing try keyword in async throws method call

> The IpadOnlyTestCase.setUp() method is marked as 'async throws' but calls 'await super.setUp()' without the 'try' keyword. Since BaseTestCase.setUp() is declared as 'async throws', this means any errors thrown by the parent setUp will not be properly propagated and will instead cause a compilation error or runtime crash. This breaks the error handling contract for all iPad-specific test cases that inherit from IpadOnlyTestCase, potentially causing test suite failures or silent test skips.

GT 片段：`class IpadOnlyTestCase: BaseTestCase { ⏎ override func setUp() async throws { ⏎ specificForPlatform = .pad ⏎ if iPad() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508`，距錨點 0 行，候選管道 model_line）IpadOnlyTestCase 中呼叫 super.setUp() 缺少 try await

> 在 IpadOnlyTestCase 的 setUp() 中，呼叫 `super.setUp()` 時未加上 `try await`，但父類別的 setUp() 已改為 async throws。這會導致編譯錯誤，或若編譯器允許，則可能造成非同步呼叫未正確等待。建議改為 `try await super.setUp()`。

finding 片段：`await super.setUp()`

## base-2:firefox-ios-3:1|firefox-ios-3#1

**GT**（func）Incorrect async Task wrapper breaks MainActor isolation in onboarding action handler

> The onActionTap closure is wrapped in a Task block without ensuring MainActor isolation. The OnboardingFlowViewModel expects this closure to be @MainActor isolated, but Task {} creates a new async context that may execute on a different executor. This causes the completion handler and handleAction calls to potentially run off the main thread, leading to concurrency violations and potential crashes when UI updates occur. The original code directly called onboardingService.handleAction which maintained proper MainActor isolation.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in ⏎ guard let onboardingService = self?.onboardingService else { return } ⏎ Task { ⏎ onboardingService.handleAction(`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行，候選管道 loc）onActionTap 閉包內使用 Task 可能造成執行順序不確定

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會讓 handleAction 的執行延後到非同步佇列，可能改變原本的同步執行順序。若 handleAction 內部有依賴呼叫順序的邏輯（例如更新 UI 或狀態），可能導致行為不一致。建議確認 handleAction 是否必須在原本的同步上下文中執行，或改用 MainActor.assumeIsolated 等方式保留同步性。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## base-2:firefox-ios-3:1|firefox-ios-3#6

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行，候選管道 loc）onActionTap 閉包內使用 Task 可能造成執行順序不確定

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會讓 handleAction 的執行延後到非同步佇列，可能改變原本的同步執行順序。若 handleAction 內部有依賴呼叫順序的邏輯（例如更新 UI 或狀態），可能導致行為不一致。建議確認 handleAction 是否必須在原本的同步上下文中執行，或改用 MainActor.assumeIsolated 等方式保留同步性。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## base-2:firefox-ios-3:4|firefox-ios-3#7

**GT**（rule）Protocol property missing explicit access control modifier

> The modified protocol requirement does not include an explicit access control modifier (e.g., `internal`/`public`). The rule requires explicit access control on properties/methods based on intended scope.

GT 片段：`var onLoadingStateChanged: (@MainActor @Sendable () -> Void)? { get set }`

**finding**（`firefox-ios/Client/Frontend/Browser/TabScrollController/TabProviderAdapter.swift:14`，距錨點 0 行，候選管道 model_line）onLoadingStateChanged 加上 @Sendable 可能限制賦值

> onLoadingStateChanged 屬性型別新增 @Sendable，但此屬性可能被賦予捕獲非 Sendable 值的閉包。若賦值的閉包捕獲了非 Sendable 物件，編譯器會報錯，迫使呼叫端修改。建議確認此閉包是否真的需要跨 actor 傳遞，若無必要可移除 @Sendable。

finding 片段：`var onLoadingStateChanged: (@MainActor @Sendable () -> Void)?`

## base-2:firefox-ios-4:1|firefox-ios-4#2

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行，候選管道 loc）測試斷言對象可能錯誤

> 原本測試在選擇 Light 主題後，檢查 `lightThemeView` 的值是否為 "1"。修改後改為檢查 `darkThemeView` 的值，但變數名稱仍為 `lightIsSelected`，且後續選擇 Dark 主題的斷言可能未同步調整。這可能導致測試無法正確驗證主題選擇，或產生誤導性的測試結果。建議確認此修改是否為預期行為，並同步更新變數名稱與後續斷言。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## base-2:firefox-ios-4:2|firefox-ios-4#3

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行，候選管道 loc）測試步驟順序調整可能影響穩定性

> 原本先執行 `navigator.goto(NewTabScreen)` 再點擊 "Done" 按鈕，修改後順序對調。若 "Done" 按鈕的點擊會觸發畫面跳轉，先點擊可能導致後續 `navigator.goto(NewTabScreen)` 失敗或行為不符預期。建議確認此順序調整是否為修正既有問題，並確保測試仍能穩定通過。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## base-2:firefox-ios-5:1|firefox-ios-5#1

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行，候選管道 loc）scrollToTab 的 toIndex 可能越界

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，回傳的 `toIndex` 為 `state.tabs.count`，但陣列索引應為 `count - 1`。這會導致滾動到不存在的索引，可能造成 collection view 崩潰或滾動到錯誤位置。

建議改為 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## base-2:firefox-ios-5:2|firefox-ios-5#3

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行，候選管道 loc）新增的 v147 結構體可能造成重複定義

> 在 `String.TabsTray` 中新增了 `struct v147`，其中包含與先前刪除的 `InactiveTabs` 結構體相同的靜態屬性。若專案中其他地方已存在 `v147` 結構體，或未來版本更新時可能衝突。建議確認此結構體名稱的唯一性，或考慮使用更明確的名稱。

finding 片段：`struct v147 {`

## base-2:firefox-ios-6:1|firefox-ios-6#0

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27`，距錨點 0 行，候選管道 loc）使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效

> 在測試方法 `testRequestAuthorization` 中，原本使用 `XCTAssertTrue` 進行斷言，但此 PR 改為使用 Swift 標準函式 `assert`。`assert` 在 release 建置（`-O` 或 `-Ounchecked`）中會被編譯器移除，導致測試永遠通過，無法驗證行為。建議改回 `XCTAssertTrue` 或使用 `XCTAssert`。

finding 片段：`assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

## base-2:firefox-ios-6:3|firefox-ios-6#1

**GT**（func）Incorrect tearDown order in StoriesFeedDiffableDataSourceTests

> The tearDown method calls super.tearDown() before cleaning up test dependencies. In XCTest, super.tearDown() should be called after cleaning up resources to ensure proper cleanup order. Calling super.tearDown() first can cause issues when the parent class attempts to access or clean up resources that are about to be deallocated. The DependencyHelperMock().reset() and collectionView/diffableDataSource cleanup should happen before calling the parent's tearDown to prevent potential crashes or state inconsistencies between tests.

GT 片段：`override func tearDown() async throws { ⏎ try await super.tearDown() ⏎ diffableDataSource = nil ⏎ collectionView = nil`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Frontend/StoriesFeed/StoriesFeedDiffableDataSourceTests.swift:16`，距錨點 12 行，候選管道 ident）setUp 中呼叫 super.setUp() 的順序可能影響測試狀態

> 在 `StoriesFeedDiffableDataSourceTests` 的 `setUp` 中，原本先呼叫 `super.setUpWithError()` 再進行設定，現在改為先呼叫 `try await super.setUp()` 再進行設定。若 `super.setUp()` 會重置某些狀態，可能影響後續設定。建議確認 `XCTestCase` 的 `setUp` 是否會影響測試環境，或考慮將 `super.setUp()` 放在設定之後。

finding 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ collectionView = UICollectionView(frame: .zero, collectionViewLayout: UICollectionViewFlowLayout())`

## base-2:firefox-ios-7:1|firefox-ios-7#3

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:26`，距錨點 0 行，候選管道 loc）throttle 方法中 lastExecutionTime 更新順序錯誤

> 在 throttle 方法中，原本先檢查時間間隔再更新 lastExecutionTime，現在改成先更新 lastExecutionTime 再檢查。這會導致每次呼叫都更新時間戳，使得節流條件永遠無法滿足（除非 threshold <= 0），節流功能失效。

失敗情境：假設 threshold = 1 秒，連續快速呼叫 throttle 兩次，第一次呼叫後 lastExecutionTime 設為現在，第二次呼叫時，因為 lastExecutionTime 剛被更新，時間間隔小於 threshold，所以不會執行 completion，但 lastExecutionTime 又被更新，導致後續呼叫永遠被節流。

建議：將 lastExecutionTime = Date() 移回 guard 檢查之後。

finding 片段：`lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return }`

## base-2:firefox-ios-7:2|firefox-ios-7#1

**GT**（func）Thread safety violation calling @MainActor completion handler from background thread

> In the handleServerTrust method, when SSL/TLS certificate validation fails (guard else clause), the @MainActor-isolated completionHandler is called directly from the background dispatchQueue without using ensureMainThread wrapper. This violates Swift Concurrency's actor isolation and can cause runtime crashes or data races. The success path correctly wraps the completion call in ensureMainThread, but the failure path at line 1343 does not, creating inconsistent thread safety behavior.

GT 片段：`func handleServerTrust( ⏎ challenge: URLAuthenticationChallenge, ⏎ dispatchQueue: DispatchQueueInterface, ⏎ completionHandler: @escaping @MainActor (URLSession.AuthChallengeDisposition, URLCredential?) -> Void`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343`，距錨點 0 行，候選管道 loc）直接呼叫 completionHandler 可能違反執行緒安全

> 在 handleServerTrust 中，原本使用 ensureMainThread 來確保 completionHandler 在主執行緒上執行，現在改成直接呼叫 completionHandler。但 handleServerTrust 是在 dispatchQueue.async 中執行的，該佇列可能是背景佇列，因此 completionHandler 可能在背景執行緒被呼叫，而 completionHandler 被標記為 @MainActor，這可能導致執行緒安全問題或 runtime crash。

失敗情境：當憑證不在信任清單中時，completionHandler 會在背景執行緒被呼叫，若 completionHandler 內部存取 UI 或 main actor 隔離的狀態，可能導致資料競爭或 crash。

建議：保留 ensureMainThread 包裝，或確保 dispatchQueue 是 main queue。

finding 片段：`completionHandler(.performDefaultHandling, nil)`

## base-2:firefox-ios-8:1|firefox-ios-8#0

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行，候選管道 loc）bootstrapDependencies 標記 @MainActor 但未標記 async，呼叫端需 await

> `bootstrapDependencies` 被標記為 `@MainActor`，但未標記為 `async`。在 Swift 中，從非 async 上下文呼叫 @MainActor 方法需要 await，但從 async 上下文呼叫則不需要。然而，此方法內部有同步的 MainActor 隔離操作，若從非 MainActor 執行緒呼叫會導致執行緒不安全。建議將方法標記為 `async`，或確保所有呼叫端都在 MainActor 上。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## base-2:firefox-ios-8:4|firefox-ios-8#1

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行，候選管道 loc）非 @MainActor 類別中呼叫 @MainActor 方法可能導致編譯錯誤

> `LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 方法中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 await，但方法已改為 async @MainActor），可能導致編譯錯誤。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## base-2:firefox-ios-8:5|firefox-ios-8#1

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29`，距錨點 9 行，候選管道 ident）tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor

> `tearDown` 中呼叫 `AppContainer.shared.reset()`，該方法可能也是 @MainActor，但類別未標記 @MainActor，可能導致編譯錯誤。

finding 片段：`AppContainer.shared.reset()`

## base-2:firefox-ios-9:1|firefox-ios-9#3

**GT**（func）Wrong display view type for reader mode action

> The handleShowReaderModeAction function sets the wrong displayView type when the user taps the reader mode button. Instead of setting displayView to '.readerMode' (which would show the reader mode view), it's set to '.readerModeLongPressAction' (which is meant for long-press actions). This causes the wrong UI component to be displayed when users try to activate reader mode, breaking the core reader mode functionality and showing an incorrect action sheet instead of the reader view.

GT 片段：`@MainActor ⏎ private static func handleShowReaderModeAction(state: BrowserViewControllerState, ⏎ action: GeneralBrowserAction) -> BrowserViewControllerState { ⏎ return BrowserViewControllerState(`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566`，距錨點 0 行，候選管道 loc）displayView 從 .readerMode 改為 .readerModeLongPressAction，可能顯示錯誤畫面

> 在 `handleShowReaderModeLongPressAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這會導致長按閱讀模式按鈕時，畫面顯示錯誤的視圖（可能是長按選單而非閱讀模式）。請確認此變更是否為預期行為，若非預期請還原。

finding 片段：`displayView: .readerModeLongPressAction,`

## base-2:firefox-ios-9:2|firefox-ios-9#1

**GT**（func）Incorrect Reader Mode URL handling in cancelEditMode

> The cancelEditMode function now incorrectly preserves reader mode URLs when canceling edit mode. The logic was changed from '&&' (AND) to '||' (OR), which means reader mode URLs will now be kept instead of being cleared. This breaks the expected behavior where reader mode URLs should be filtered out when canceling URL editing, potentially causing the address bar to display internal reader:// URLs to users instead of the original webpage URL.

GT 片段：`@MainActor ⏎ private func cancelEditMode(windowUUID: WindowUUID) { ⏎ var url = tabManager(for: windowUUID).selectedTab?.url ⏎ if let currentURL = url {`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485`，距錨點 0 行，候選管道 loc）cancelEditMode 中的 URL 判斷條件由 AND 改為 OR，可能導致非預期行為

> 在 `cancelEditMode` 中，原本條件為 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓閱讀模式 URL 也被視為有效 URL 而保留，可能導致取消編輯時 URL 欄顯示閱讀模式 URL，而非預期的空白或一般 URL。請確認此變更是否為預期行為。

finding 片段：`url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`

## base-2:firefox-ios-9:3|firefox-ios-9#2

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 0 行，候選管道 loc）isReaderModeEnabled 的布林值邏輯反轉，可能導致遙測資料錯誤

> 原本 `case .available: true` 與 `default: false`，現在改為 `case .available: false` 與 `default: true`。這會讓閱讀模式按鈕的遙測事件記錄錯誤的啟用狀態，影響數據分析。請確認此變更是否為預期行為。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## base-2:prefect-1:1|prefect-1#2

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 38 行，候選管道 ident）移除 strict=True 可能掩蓋 zip 長度不一致

> 在 `_fetch_work_pools_parallel` 中，原本使用 `zip(pool_names_list, results, strict=True)` 會在兩者長度不一致時拋出 `ValueError`。移除 `strict=True` 後，若 `results` 長度小於 `pool_names_list`，多餘的 pool 名稱會被靜默忽略，導致部分 work pool 的資訊缺失且沒有警告。這可能造成生成的 SDK 不完整。建議保留 `strict=True`，或明確處理長度不一致的情況。

finding 片段：`for name, result in zip(pool_names_list, results):`

## base-2:prefect-1:1|prefect-1#3

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行，候選管道 loc）移除 strict=True 可能掩蓋 zip 長度不一致

> 在 `_fetch_work_pools_parallel` 中，原本使用 `zip(pool_names_list, results, strict=True)` 會在兩者長度不一致時拋出 `ValueError`。移除 `strict=True` 後，若 `results` 長度小於 `pool_names_list`，多餘的 pool 名稱會被靜默忽略，導致部分 work pool 的資訊缺失且沒有警告。這可能造成生成的 SDK 不完整。建議保留 `strict=True`，或明確處理長度不一致的情況。

finding 片段：`for name, result in zip(pool_names_list, results):`

## base-2:prefect-1:2|prefect-1#2

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 0 行，候選管道 loc）對 base_job_template['variables'] 的型別假設可能導致錯誤

> 在 `_fetch_work_pool` 中，原本有檢查 `variables` 是否為 dict，現在直接賦值給 `job_vars_schema`。如果 `base_job_template['variables']` 不是 dict（例如是 list 或 None），後續使用 `job_vars_schema` 的地方（如 `WorkPoolInfo` 的建構或後續處理）可能會拋出型別錯誤。建議保留型別檢查，或明確處理非 dict 的情況。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## base-2:prefect-1:2|prefect-1#3

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 37 行，候選管道 ident）對 base_job_template['variables'] 的型別假設可能導致錯誤

> 在 `_fetch_work_pool` 中，原本有檢查 `variables` 是否為 dict，現在直接賦值給 `job_vars_schema`。如果 `base_job_template['variables']` 不是 dict（例如是 list 或 None），後續使用 `job_vars_schema` 的地方（如 `WorkPoolInfo` 的建構或後續處理）可能會拋出型別錯誤。建議保留型別檢查，或明確處理非 dict 的情況。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## base-2:prefect-1:3|prefect-1#1

**GT**（func）Incorrect deployment filtering breaks full-name matching

> The deployment filtering logic checks `dep.name not in deployment_names` instead of checking `full_name not in deployment_names`. This causes the filter to incorrectly evaluate when users specify deployment names in 'flow-name/deployment-name' format. When a user provides a full deployment name like 'my-flow/production', the code checks if 'production' (the short name) is in the list containing 'my-flow/production', which fails, causing the deployment to enter the fallback matching logic unnecessarily. This breaks the fast-path check and could lead to incorrect filtering behavior where deployments are included or excluded inappropriately.

GT 片段：`# If filtering by deployment name, check the full name matches ⏎ full_name = f"{flow_name}/{dep.name}" ⏎ if deployment_names and dep.name not in deployment_names: ⏎ # Only include if the full name matches (filter was by name parts)`

**finding**（`src/prefect/_sdk/fetcher.py:397`，距錨點 0 行，候選管道 loc）部署名稱過濾邏輯可能錯誤

> 原本的條件是 `full_name not in deployment_names`，現在改為 `dep.name not in deployment_names`。這可能導致當使用者指定完整名稱（如 `flow-name/deployment-name`）時，過濾邏輯無法正確匹配，因為 `dep.name` 只包含部署名稱部分。建議確認 `deployment_names` 的內容格式，並使用正確的比較方式。

finding 片段：`if deployment_names and dep.name not in deployment_names:`

## base-2:prefect-10:1|prefect-10#0

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行，候選管道 loc）關閉 TypeScript strict 模式會降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用所有嚴格型別檢查，包括 `strictNullChecks`、`strictFunctionTypes` 等，可能導致未處理的 null/undefined 錯誤、錯誤的型別推斷，並隱藏潛在的執行時期錯誤。這通常不是一個可接受的變更，除非有明確的技術原因。建議恢復為 `true`，並修正任何因此產生的型別錯誤。

finding 片段：`"strict": false,`

## base-2:prefect-10:2|prefect-10#3

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行，候選管道 loc）數字輸入使用 parseInt 而非 Number，可能導致非預期結果

> 在 `work-pool-status-trigger-fields.tsx` 中，Threshold 欄位的 `onChange` 使用 `parseInt(e.target.value)`，而其他元件（如 `custom-trigger-fields.tsx`、`deployment-status-trigger-fields.tsx`、`work-queue-status-trigger-fields.tsx`）使用 `Number(e.target.value)`。`parseInt` 會解析字串直到遇到非數字字元，例如輸入 "10abc" 會得到 10，而 `Number` 會得到 NaN。這可能導致使用者輸入無效值時，表單狀態不一致。建議統一使用 `Number`，並考慮加入驗證。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## base-2:prefect-10:3|prefect-10#4

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `custom-trigger-fields.tsx` but does not add a corresponding `custom-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const CustomTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" }); ⏎ return (`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:16`，距錨點 0 行，候選管道 loc）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## base-2:prefect-10:4|prefect-10#2

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:27`，距錨點 2 行，候選管道 loc）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## base-2:prefect-10:4|prefect-10#5

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:27`，距錨點 0 行，候選管道 loc）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## base-2:prefect-10:5|prefect-10#6

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `work-pool-status-trigger-fields.tsx` but does not add a corresponding `work-pool-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const WorkPoolStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:28`，距錨點 0 行，候選管道 loc）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## base-2:prefect-10:6|prefect-10#7

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `work-queue-status-trigger-fields.tsx` but does not add a corresponding `work-queue-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const WorkQueueStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-queue-status-trigger-fields.tsx:28`，距錨點 0 行，候選管道 loc）切換 posture 時未清除 trigger.within 欄位

> 當使用者從 Proactive 切換回 Reactive 時，`trigger.within` 欄位會被隱藏，但其值仍保留在表單狀態中。這可能導致提交時包含不必要的 `within` 值，或造成驗證錯誤。建議在 posture 變更時，使用 `useEffect` 或 `setValue` 清除 `trigger.within`。

finding 片段：`const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

## base-2:prefect-11:1|prefect-11#2

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:132`，距錨點 5 行，候選管道 loc）semaphore 未初始化時直接拋出 RuntimeError 可能中斷事件處理

> 在 `_replicate_pod_event` 中，若 `_startup_event_semaphore` 為 `None`，會直接 `raise RuntimeError`。但此函式可能在任何事件到達時被呼叫，而 `initialize_clients` 不一定已執行（例如啟動順序問題或測試情境）。這會導致事件處理失敗，且錯誤可能被 kopf 框架吞掉，造成事件遺失。建議改為 fallback 行為（例如不限制並發）或延遲初始化。

finding 片段：`if _startup_event_semaphore is None: ⏎ raise RuntimeError("Startup event semaphore not initialized")`

## base-2:prefect-11:3|prefect-11#1

**GT**（func）Race condition: semaphore initialized after clients during startup

> The `_startup_event_semaphore` is initialized after the orchestration and events clients are created and started. This creates a race condition where Kubernetes pods detected during the client startup phase can trigger `_replicate_pod_event` calls before the semaphore exists. When `event_type` is `None` (startup scenario), the code checks `if _startup_event_semaphore is None` and raises a RuntimeError. However, pods may be detected immediately after clients start but before the semaphore initialization completes, causing the observer to crash with 'Startup event semaphore not initialized' errors during high pod count scenarios.

GT 片段：`@kopf.on.startup() ⏎ async def initialize_clients(logger: kopf.Logger, **kwargs: Any): ⏎ logger.info("Initializing clients") ⏎ global events_client`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:47`，距錨點 3 行，候選管道 loc）全域 semaphore 變數可能造成測試或多次初始化問題

> `_startup_event_semaphore` 是模組層級全域變數，在 `initialize_clients` 中賦值。若該函式被多次呼叫（例如測試或重新初始化），舊的 semaphore 會被覆蓋，可能導致並發控制失效或資源洩漏。建議考慮使用單例模式或確保只初始化一次。

finding 片段：`_startup_event_semaphore: asyncio.Semaphore | None = None`

## base-2:prefect-12:3|prefect-12#1

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行，候選管道 loc）run_count 使用 `||` 可能錯誤處理 falsy 值

> `taskRun.run_count || 0` 會將 0、空字串、NaN 等 falsy 值都顯示為 0。若 run_count 可能為空字串或 null，顯示 0 可能誤導使用者。建議改用 `taskRun.run_count ?? 0` 或明確檢查 null/undefined。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## base-2:prefect-12:4|prefect-12#2

**GT**（func）Missing type coercion for retries value causes potential type inconsistency

> The retries display removes the .toString() call that was present in the original PR, directly rendering taskRun.empirical_policy?.retries ?? "0". This creates a type inconsistency where the value could be either a number (when retries exists) or a string "0" (when it doesn't). While React can render both, this inconsistency violates the principle of uniform data handling and could cause issues in the component tree if parent or child components expect consistent string formatting for this field, or if the value is later used in string operations or comparisons.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retries</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retries ?? "0"}`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 10 行，候選管道 ident）retry_jitter_factor 為 0 時顯示 'None'

> 條件 `taskRun.empirical_policy?.retry_jitter_factor` 在值為 0 時為 falsy，因此會顯示 'None'，但 0 是有效的 jitter factor。建議改用 `typeof ... === 'number'` 或 `??` 來判斷。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## base-2:prefect-12:4|prefect-12#3

**GT**（func）Incorrect truthy check for retry_jitter_factor hides valid zero values

> The retry_jitter_factor check was changed from an explicit null/undefined check to a simple truthy check. This is a critical bug because a jitter factor of 0 is a valid configuration value (meaning no randomness in retry delays), but the truthy check treats 0 as falsy and displays "None" instead. This misrepresents the actual task configuration to users, making them think no jitter factor is set when it's actually configured to 0. The original PR correctly distinguished between 'not set' (null/undefined) and 'set to zero' (0), but this change breaks that distinction.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retry Jitter Factor</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retry_jitter_factor`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 0 行，候選管道 loc）retry_jitter_factor 為 0 時顯示 'None'

> 條件 `taskRun.empirical_policy?.retry_jitter_factor` 在值為 0 時為 falsy，因此會顯示 'None'，但 0 是有效的 jitter factor。建議改用 `typeof ... === 'number'` 或 `??` 來判斷。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## base-2:prefect-13:1|prefect-13#2

**GT**（func）Removed HTML5 min validation from concurrency limit input

> The concurrency limit input field previously had `min={0}` attribute (HTML5 validation) to prevent negative numbers from being entered. This attribute was removed in this PR change. While the Zod schema still validates that the value must be >= 0, users now lose immediate feedback when trying to enter negative values. They can type a negative number like `-5` and only discover it's invalid after clicking Save, rather than being prevented from entering it in the first place. This degrades the user experience by removing client-side validation that provides instant feedback.

GT 片段：`<Input ⏎ {...field} ⏎ type="number" ⏎ placeholder="Unlimited"`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:114`，距錨點 0 行，候選管道 loc）並行限制輸入可能產生 NaN

> 在 onChange 處理中，`Number(value)` 若 value 為空字串或非數字字串（例如使用者輸入 'e' 或 '-'），會得到 `NaN`。這會導致表單提交時將 NaN 傳送到 API，可能造成後端驗證錯誤或資料不一致。建議在轉換前檢查 value 是否為空或非數字，或使用 `Number.isNaN` 驗證。

finding 片段：`field.onChange(value === "" ? null : Number(value));`

## base-2:prefect-13:2|prefect-13#1

**GT**（func）Description field incorrectly trims whitespace

> The work pool edit form now calls .trim() on the description before saving (line 42). This removes any intentional leading or trailing whitespace that users may want to preserve in their work pool descriptions, such as indented text or formatting for markdown. The original PR correctly converted empty strings to null using `||`, but the added .trim() operation inappropriately modifies user input. This breaks the principle of preserving user data as-is unless there's a specific business requirement.

GT 片段：`const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool( ⏎ { ⏎ name: workPool.name,`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:43`，距錨點 0 行，候選管道 loc）表單提交錯誤處理不完整

> handleSubmit 中呼叫 updateWorkPool 時，僅在 onError 中顯示 toast，但未處理可能出現的同步錯誤（例如 updateWorkPool 拋出例外）。若 updateWorkPool 本身拋出錯誤，將導致未捕捉的 Promise rejection。建議將呼叫包在 try/catch 中，或確保 updateWorkPool 不會拋出同步錯誤。

finding 片段：`updateWorkPool( ⏎ { ⏎ name: workPool.name, ⏎ workPool: {`

## base-2:prefect-2:1|prefect-2#2

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:202`，距錨點 0 行，候選管道 loc）action.triggered 事件使用了錯誤的 related 參數

> 在 `fail` 方法中，`action.triggered` 事件的 `related` 參數被指派為 `self._resulting_related_resources`，而非建構好的 `related_resources`。這會導致該事件缺少 `automation-triggered-event` 和 `triggering-event` 關聯資源，違反此 PR 的目標。

失敗情境：當 action 失敗時，`action.triggered` 事件將無法連結回 automation.triggered 事件，使用者無法追蹤觸發來源。

建議：將 `related` 改為 `related_resources`。

finding 片段：`related=self._resulting_related_resources,`

## base-2:prefect-2:2|prefect-2#2

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:213`，距錨點 1 行，候選管道 model_line）action.failed 事件使用了錯誤的 related 參數

> 在 `fail` 方法中，`action.failed` 事件的 `related` 參數被指派為 `related_resources`，但此變數是從 `self._resulting_related_resources` 複製後再加入 automation-triggered-event 與 triggering-event。然而，`self._resulting_related_resources` 可能已包含 triggering-event（若先前已加入），導致重複。

失敗情境：當 action 失敗時，`action.failed` 事件可能包含重複的 triggering-event 關聯資源，造成資料不一致。

建議：確認 `self._resulting_related_resources` 的內容，避免重複加入 triggering-event。

finding 片段：`related=related_resources,`

## base-2:prefect-2:5|prefect-2#1

**GT**（func）Incorrect automation_triggered_event_id for state-specific actions

> When actions_on_trigger or actions_on_resolve are executed, they should be linked to their specific triggered_event.id or resolved_event.id respectively. However, the code incorrectly uses primary_state_change_event_id (which always prefers Triggered over Resolved) for both types of actions. This breaks the tracing chain for actions_on_resolve - they will reference the wrong event ID when only a Resolved state change occurs, making it impossible to correctly trace the action back to the automation.resolved event that actually prompted it.

GT 片段：`# Conditionally add in actions that fire on specific trigger states ⏎ if TriggerState.Triggered in firing.trigger_states: ⏎ triggered_event = state_change_events[TriggerState.Triggered] ⏎ source_actions += [`

**finding**（`src/prefect/server/events/triggers.py:442`，距錨點 16 行，候選管道 ident）primary_state_change_event 選擇邏輯可能選錯事件

> 當 automation 同時觸發 Triggered 和 Resolved 狀態時，`primary_state_change_event` 會優先選擇 Triggered 事件。但若 Triggered 事件不存在（例如僅 Resolved），則會選擇 Resolved 事件。然而，若兩者皆存在，但實際觸發 action 的是 Resolved 事件（例如 `actions_on_resolve`），則 action 事件會錯誤地連結到 Triggered 事件。

失敗情境：當 automation 同時觸發 Triggered 和 Resolved，且 action 是定義在 `actions_on_resolve` 中時，action 事件會連結到錯誤的 automation.triggered 事件。

建議：根據 action 的來源（`actions`、`actions_on_trigger`、`actions_on_resolve`）選擇對應的 state change event，而非統一使用 primary。

finding 片段：`primary_state_change_event = state_change_events.get( ⏎ TriggerState.Triggered ⏎ ) or state_change_events.get(TriggerState.Resolved)`

## base-2:prefect-2:6|prefect-2#1

**GT**（func）Incorrect automation_triggered_event_id for state-specific actions

> When actions_on_trigger or actions_on_resolve are executed, they should be linked to their specific triggered_event.id or resolved_event.id respectively. However, the code incorrectly uses primary_state_change_event_id (which always prefers Triggered over Resolved) for both types of actions. This breaks the tracing chain for actions_on_resolve - they will reference the wrong event ID when only a Resolved state change occurs, making it impossible to correctly trace the action back to the automation.resolved event that actually prompted it.

GT 片段：`# Conditionally add in actions that fire on specific trigger states ⏎ if TriggerState.Triggered in firing.trigger_states: ⏎ triggered_event = state_change_events[TriggerState.Triggered] ⏎ source_actions += [`

**finding**（`src/prefect/server/events/triggers.py:442`，距錨點 16 行，候選管道 ident）state_change_events 可能缺少對應鍵

> 在 `act` 函式中，`state_change_events` 是根據 `firing.trigger_states` 建立的字典。若 `firing.trigger_states` 不包含 `TriggerState.Triggered` 或 `TriggerState.Resolved`，則 `state_change_events.get(TriggerState.Triggered)` 或 `state_change_events.get(TriggerState.Resolved)` 可能回傳 `None`。雖然程式碼使用 `or` 來處理，但若兩者皆為 `None`，則 `primary_state_change_event_id` 會是 `None`，這可能導致後續 action 事件缺少 automation-triggered-event 關聯。

失敗情境：當 automation 觸發條件不包含 Triggered 或 Resolved 狀態時，action 事件將無法連結到 automation.triggered 事件。

建議：確認 `firing.trigger_states` 是否保證包含至少一個狀態，或明確處理兩者皆無的情況。

finding 片段：`primary_state_change_event = state_change_events.get( ⏎ TriggerState.Triggered ⏎ ) or state_change_events.get(TriggerState.Resolved)`

## base-2:prefect-3:1|prefect-3#1

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 0 行，候選管道 loc）拖放索引計算未考慮 prefixItems，可能導致項目錯位

> `handleDragEnd` 使用 `localKeyedValues` 的索引來呼叫 `moveItem`，但 `moveItem` 預期的是「可移動項目」的索引（已扣除 prefixItems）。當陣列有 prefixItems 時，`localKeyedValues` 包含所有項目，而 `moveItem` 內部可能使用 `getCanMoveForIndex` 或直接操作索引，導致拖放後項目順序錯誤。

建議：在 `handleDragEnd` 中先計算可移動項目的索引，或修改 `moveItem` 使其接受原始索引並在內部處理 prefixItems 偏移。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## base-2:prefect-3:1|prefect-3#2

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 13 行，候選管道 ident）拖放索引計算未考慮 prefixItems，可能導致項目錯位

> `handleDragEnd` 使用 `localKeyedValues` 的索引來呼叫 `moveItem`，但 `moveItem` 預期的是「可移動項目」的索引（已扣除 prefixItems）。當陣列有 prefixItems 時，`localKeyedValues` 包含所有項目，而 `moveItem` 內部可能使用 `getCanMoveForIndex` 或直接操作索引，導致拖放後項目順序錯誤。

建議：在 `handleDragEnd` 中先計算可移動項目的索引，或修改 `moveItem` 使其接受原始索引並在內部處理 prefixItems 偏移。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## base-2:prefect-3:2|prefect-3#1

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行，候選管道 ident）SortableContext 包含不可拖曳項目，可能導致拖放行為異常

> `sortableKeys` 包含所有項目的 key，包括 prefixItems（不可拖曳）。雖然 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled` 屬性設為 `!canMove`，但將不可拖曳項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳可移動項目時，不可移動項目仍被視為潛在目標。

建議：僅將可移動項目的 key 傳入 SortableContext，或確認 dnd-kit 對 disabled 項目的處理符合預期。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## base-2:prefect-3:2|prefect-3#2

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行，候選管道 loc）SortableContext 包含不可拖曳項目，可能導致拖放行為異常

> `sortableKeys` 包含所有項目的 key，包括 prefixItems（不可拖曳）。雖然 `SchemaFormInputArrayItem` 中 `useSortable` 的 `disabled` 屬性設為 `!canMove`，但將不可拖曳項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳可移動項目時，不可移動項目仍被視為潛在目標。

建議：僅將可移動項目的 key 傳入 SortableContext，或確認 dnd-kit 對 disabled 項目的處理符合預期。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## base-2:prefect-4:2|prefect-4#3

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179`，距錨點 2 行，候選管道 loc）建立失敗時錯誤訊息不明確

> 在 `onError` 回呼中，錯誤訊息固定為 "Unknown error while creating block."，未使用 API 回傳的錯誤訊息。這會讓使用者無法得知失敗原因。

建議：從 `err` 中提取可讀的錯誤訊息，或至少記錄完整的錯誤物件。

finding 片段：`onError: (err) => { ⏎ const message = "Unknown error while creating block."; ⏎ toast.error(message); ⏎ console.error(message, err);`

## base-2:prefect-4:3|prefect-4#0

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行，候選管道 loc）搜尋功能可能失效

> `filteredData` 使用 `deferredSearch` 進行前端過濾，但 `useSuspenseQuery` 的查詢參數中也使用了 `deferredSearch` 進行後端過濾。這可能導致前端過濾與後端過濾不一致，或前端過濾重複執行。

建議：移除前端過濾，完全依賴後端查詢；或移除後端過濾，只在前端過濾。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## base-2:prefect-4:3|prefect-4#1

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 6 行，候選管道 ident）搜尋功能可能失效

> `filteredData` 使用 `deferredSearch` 進行前端過濾，但 `useSuspenseQuery` 的查詢參數中也使用了 `deferredSearch` 進行後端過濾。這可能導致前端過濾與後端過濾不一致，或前端過濾重複執行。

建議：移除前端過濾，完全依賴後端查詢；或移除後端過濾，只在前端過濾。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## base-2:prefect-4:4|prefect-4#0

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行，候選管道 loc）前端過濾可能造成效能問題

> 當 `data` 很大時，每次 `deferredSearch` 變化都會重新過濾整個陣列。雖然有 `useMemo`，但若資料量龐大，仍可能造成效能瓶頸。

建議：考慮使用後端分頁或虛擬化列表。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## base-2:prefect-4:4|prefect-4#1

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 6 行，候選管道 ident）前端過濾可能造成效能問題

> 當 `data` 很大時，每次 `deferredSearch` 變化都會重新過濾整個陣列。雖然有 `useMemo`，但若資料量龐大，仍可能造成效能瓶頸。

建議：考慮使用後端分頁或虛擬化列表。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## base-2:prefect-4:5|prefect-4#3

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161`，距錨點 13 行，候選管道 ident）驗證錯誤時未顯示錯誤訊息

> 當 `validateForm` 回傳錯誤時，程式碼僅 `return`，未向使用者顯示任何錯誤訊息。使用者可能不知道表單驗證失敗。

建議：在驗證失敗時顯示錯誤訊息，例如使用 toast 或表單錯誤提示。

finding 片段：`await validateForm({ schema: values }); ⏎ if (errors.length > 0) { ⏎ return; ⏎ }`

## base-2:prefect-5:1|prefect-5#0

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行，候選管道 ident）子字串比對可能誤判非前綴路徑

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，而非檢查路徑是否以 bucket_folder 開頭。若 bucket_folder 為 'data/'，而 path 為 'metadata/file.txt'，則 'data/' 存在於 'metadata/' 中，導致錯誤地跳過前綴添加，產生錯誤路徑。建議改為 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較前綴。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-2:prefect-5:1|prefect-5#1

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行，候選管道 loc）子字串比對可能誤判非前綴路徑

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串比對，而非檢查路徑是否以 bucket_folder 開頭。若 bucket_folder 為 'data/'，而 path 為 'metadata/file.txt'，則 'data/' 存在於 'metadata/' 中，導致錯誤地跳過前綴添加，產生錯誤路徑。建議改為 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較前綴。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-2:prefect-5:2|prefect-5#0

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 0 行，候選管道 loc）跨欄位驗證使用 field_validator 可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中使用 `info.data.get("bucket")` 進行跨欄位驗證，但 `field_validator` 的 `info.data` 僅包含已驗證的欄位，且欄位驗證順序不保證 bucket 已先驗證。若 bucket 欄位尚未驗證，`info.data.get("bucket")` 可能回傳 None，導致驗證失效。應改用 `model_validator` 進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## base-2:prefect-5:2|prefect-5#1

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 23 行，候選管道 ident）跨欄位驗證使用 field_validator 可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中使用 `info.data.get("bucket")` 進行跨欄位驗證，但 `field_validator` 的 `info.data` 僅包含已驗證的欄位，且欄位驗證順序不保證 bucket 已先驗證。若 bucket 欄位尚未驗證，`info.data.get("bucket")` 可能回傳 None，導致驗證失效。應改用 `model_validator` 進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## base-2:prefect-5:3|prefect-5#0

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行，候選管道 ident）路徑比對未考慮正規化

> `self.bucket_folder` 可能包含尾隨斜線，而 `path` 可能未正規化（例如包含多餘斜線或相對路徑）。直接使用 `in` 或 `startswith` 可能無法正確處理。建議先將兩者正規化（例如使用 `PurePosixPath`）再比較。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-2:prefect-5:3|prefect-5#1

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行，候選管道 loc）路徑比對未考慮正規化

> `self.bucket_folder` 可能包含尾隨斜線，而 `path` 可能未正規化（例如包含多餘斜線或相對路徑）。直接使用 `in` 或 `startswith` 可能無法正確處理。建議先將兩者正規化（例如使用 `PurePosixPath`）再比較。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-2:prefect-6:1|prefect-6#1

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:133`，距錨點 14 行，候選管道 ident）`get_or_create_client` 回傳值未正確處理

> `get_or_create_client` 可能回傳一個 tuple `(client, context_manager)`，但程式碼只取第一個元素並指派給 `client`。如果回傳的 client 是透過 context manager 建立的，則在函式結束後可能無法正確關閉，導致資源洩漏。建議確認 `get_or_create_client` 的實作，並使用 `async with` 或確保 client 生命週期正確。

finding 片段：`client, _ = get_or_create_client(client)`

## base-2:prefect-6:2|prefect-6#0

**GT**（rule）Missing sync wrapper for async function

> The public API function run_deployment is now just an alias to the async-only arun_deployment function, lacking a proper sync compatibility wrapper. This forces users to always use asyncio.run() or similar async context managers in synchronous code.

GT 片段：`# Alias for backwards compatibility ⏎ run_deployment = arun_deployment`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 0 行，候選管道 loc）`run_deployment` 別名導致同步呼叫失效

> `run_deployment = arun_deployment` 使得 `run_deployment` 成為 async 函式。原本使用 `@sync_compatible` 裝飾器時，同步呼叫會自動執行；現在同步呼叫會回傳 coroutine 而不會執行，導致既有同步程式碼失效。建議保留一個同步包裝函式，或使用 `@async_dispatch` 裝飾器來處理同步/非同步分派。

finding 片段：`run_deployment = arun_deployment`

## base-2:prefect-6:2|prefect-6#3

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 4 行，候選管道 loc）`run_deployment` 別名導致同步呼叫失效

> `run_deployment = arun_deployment` 使得 `run_deployment` 成為 async 函式。原本使用 `@sync_compatible` 裝飾器時，同步呼叫會自動執行；現在同步呼叫會回傳 coroutine 而不會執行，導致既有同步程式碼失效。建議保留一個同步包裝函式，或使用 `@async_dispatch` 裝飾器來處理同步/非同步分派。

finding 片段：`run_deployment = arun_deployment`

## base-2:prefect-6:3|prefect-6#1

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:149`，距錨點 0 行，候選管道 loc）移除 `await` 可能導致未完成的 coroutine

> 原本 `await collect_task_run_inputs(v)` 被改為 `collect_task_run_inputs(v)`，如果該函式是 async，則會回傳 coroutine 物件而不會執行，導致 `task_inputs` 中包含未完成的 coroutine，後續使用時可能出錯。建議確認 `collect_task_run_inputs` 是否為 async，若是則應保留 `await`。

finding 片段：`k: collect_task_run_inputs(v) for k, v in parameters.items()`

## base-2:prefect-6:4|prefect-6#2

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 0 行，候選管道 loc）使用 `deployment_id` 而非 `deployment.id` 可能導致錯誤

> 原本使用 `deployment.id`，現在改為 `deployment_id`。如果 `deployment_id` 是從名稱解析而來，且解析失敗時可能為 `None`，則會傳遞 `None` 給 API，導致錯誤。建議確認 `deployment_id` 在此處一定有效。

finding 片段：`deployment_id,`

## base-2:prefect-6:5|prefect-6#2

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:231`，距錨點 16 行，候選管道 ident）輪詢順序變更可能影響 timeout 行為

> 原本先讀取 flow run 再 sleep，現在改為先 sleep 再讀取。這會導致即使 timeout 為 0，也會先 sleep 一次，可能延遲回傳。建議確認此變更是否符合預期。

finding 片段：`await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

## base-2:prefect-6:5|prefect-6#3

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:231`，距錨點 0 行，候選管道 loc）輪詢順序變更可能影響 timeout 行為

> 原本先讀取 flow run 再 sleep，現在改為先 sleep 再讀取。這會導致即使 timeout 為 0，也會先 sleep 一次，可能延遲回傳。建議確認此變更是否符合預期。

finding 片段：`await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

## base-2:prefect-7:1|prefect-7#1

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:42`，距錨點 0 行，候選管道 loc）使用 hash() 產生 advisory lock key 在跨行程間不穩定

> `hash(str(trigger.id))` 在 Python 中對字串的 hash 值會因行程而異（除非設定 PYTHONHASHSEED=0）。這會導致不同 worker 行程對同一個 trigger 計算出不同的 lock key，使得 advisory lock 無法序列化，競態條件仍然存在。

建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉換為整數，確保跨行程一致。

finding 片段：`lock_key = hash(str(trigger.id)) % (2**63)`

## base-2:prefect-7:2|prefect-7#1

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:38`，距錨點 0 行，候選管道 loc）SQLite 未實作 advisory lock，競態仍可能發生

> 函式僅在 dialect 為 postgresql 時取得 advisory lock，SQLite 則直接跳過。雖然 SQLite 的寫入序列化可能降低機率，但無法完全避免競態（例如兩個交易都先讀取再寫入）。若系統支援 SQLite，此修復不完整。

建議在 SQLite 上使用其他機制（如樂觀鎖或應用層級的分散式鎖），或明確限制此修復僅適用於 PostgreSQL。

finding 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

## base-2:prefect-7:3|prefect-7#0

**GT**（rule）Logger uses direct logging.getLogger

> The rule requires logger instances to be created using the pattern `logger: "logging.Logger" = get_logger("module_name")` but this code uses direct `logging.getLogger()` call without proper type annotation or using the standard get_logger utility

GT 片段：`import logging ⏎ logger = logging.getLogger(__name__)`

**finding**（`src/prefect/server/events/triggers.py:73`，距錨點 0 行，候選管道 loc）logger 取得方式變更可能破壞既有日誌配置

> 原本使用 `get_logger(__name__)` 取得 logger，現在改為 `logging.getLogger(__name__)`。若專案中 `get_logger` 有特殊設定（例如設定 propagate、handler 或 level），此變更可能導致日誌行為不一致。

建議確認 `get_logger` 的實作，若無特殊需求則可接受，但需注意一致性。

finding 片段：`logger = logging.getLogger(__name__)`

## base-2:prefect-8:1|prefect-8#1

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:458`，距錨點 4 行，候選管道 model_line）變數作用域錯誤可能導致 NameError

> 在 `create_ui_app` 中，`source_static_path` 和 `static_subpath` 在 `if v2_enabled:` 區塊內賦值，但後續程式碼（如 `static_dir = ... or str(static_subpath)` 和 `copy_directory(str(source_static_path), ...)`）在區塊外使用這些變數。如果 `v2_enabled` 的值不是布林值（例如設定檔中設為字串 `"false"`），則條件判斷可能不如預期，導致變數未賦值而拋出 `NameError`。建議在 `if` 之前先設定預設值，或將變數初始化為 `None` 並在後續檢查。

finding 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

## base-2:prefect-8:2|prefect-8#3

**GT**（func）Experimental V2 UI enabled by default

> The default value for v2_enabled is set to True, making the experimental V2 UI the default instead of the stable V1 UI. This is problematic because the PR description indicates V2 is experimental and should be opt-in. Users who upgrade will unexpectedly get the experimental UI by default, potentially encountering bugs, incomplete features, or breaking changes. The setting should default to False to maintain backward compatibility and allow users to explicitly opt into the experimental V2 UI.

GT 片段：`v2_enabled: bool = Field( ⏎ default=True, ⏎ description="Whether to serve the experimental V2 UI instead of the default V1 UI.", ⏎ )`

**finding**（`src/prefect/settings/models/server/ui.py:22`，距錨點 0 行，候選管道 loc）預設啟用 V2 UI 可能造成非預期的行為變更

> 新增的 `v2_enabled` 設定預設為 `True`，這會讓所有現有使用者在升級後自動切換到實驗性的 V2 UI。如果 V2 UI 尚未完全穩定或與某些功能不相容，可能導致使用者遇到問題。建議將預設值設為 `False`，並在文件或發布說明中明確告知如何啟用。

finding 片段：`v2_enabled: bool = Field( ⏎ default=True, ⏎ description="Whether to serve the experimental V2 UI instead of the default V1 UI.", ⏎ )`

## base-2:prefect-8:3|prefect-8#0

**GT**（rule）Direct logging.getLogger() call used

> The rule requires loggers to be instantiated using the pattern `logger: "logging.Logger" = get_logger("module_name")` instead of direct `logging.getLogger()` calls

GT 片段：`# Log which UI version is being served ⏎ if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

**finding**（`src/prefect/server/api/server.py:530`，距錨點 0 行，候選管道 model_line）日誌訊息可能造成混淆

> 在 `create_ui_static_subpath` 中，當 `v2_enabled` 為真時，會記錄 "Serving experimental V2 UI"。但此函式主要負責複製靜態檔案，實際提供服務的邏輯可能在別處。若此日誌在多個地方出現，可能讓使用者誤解。建議將日誌移至實際處理請求的地方，或調整訊息內容。

finding 片段：`if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

## base-2:prefect-9:1|prefect-9#1

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:12`，距錨點 17 行，候選管道 ident）Storybook 全域 QueryClient 可能導致測試間狀態污染

> `queryClient` 在模組頂層建立，且 `createTestRouter` 內部又建立新的 `QueryClient` 但未使用。全域 `queryClient` 會被所有 story 共用，若某個 story 的快取資料被修改，可能影響其他 story 的渲染結果，導致測試不穩定。建議在每個 decorator 中建立新的 `QueryClient`，或使用 `QueryClientProvider` 的 `key` prop 強制重新掛載。

finding 片段：`const queryClient = new QueryClient({ ⏎ defaultOptions: { ⏎ queries: { ⏎ retry: false,`

## base-2:prefect-9:2|prefect-9#2

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行，候選管道 loc）缺少錯誤處理，查詢失敗時元件會直接拋出錯誤

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 ErrorBoundary 包覆，整個應用程式可能崩潰。建議在元件外層加入 ErrorBoundary，或在查詢選項中設定 `retry` 與 `onError` 處理。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## base-2:prefect-9:3|prefect-9#2

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:27`，距錨點 4 行，候選管道 loc）連結缺少可存取性標籤

> 連結內容只有圖示和流程名稱，但圖示可能無法被螢幕閱讀器正確讀取，建議加入 `aria-label` 或 `title` 屬性，提供更明確的描述。

finding 片段：`<Link ⏎ to="/flows/flow/$id" ⏎ params={{ id: flow.id }} ⏎ className="flex items-center gap-1"`

## base-2:redis-1:2|redis-1#0

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行，候選管道 loc）validateStoredKeyConversion 函式未被使用

> 新增的 `validateStoredKeyConversion` 函式在整個 diff 中沒有被呼叫。這可能是為了除錯或驗證而加入，但若未使用，會造成 dead code，且可能隱藏潛在問題。建議移除或實際使用它來驗證 keyFromStoredKey 回呼的正確性。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) { ⏎ return extracted != NULL;`

## base-2:redis-1:3|redis-1#2

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:913`，距錨點 0 行，候選管道 loc）dictSetKeyAtLink 中對 addedKey 的使用可能不一致

> 在 `dictSetKeyAtLink` 中，當 `*link == NULL` 時，使用 `addedKey` 來呼叫 `dictFindLink`，但 `addedKey` 是經過 `keyDup` 處理後的 key，可能與原始 `key` 不同。若 `keyDup` 會改變 key 的內容或型別，可能導致查找失敗或錯誤。建議確認此處應使用原始 `key` 還是 `addedKey`，並確保一致性。

finding 片段：`if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL); ⏎ }`

## base-2:redis-2:1|redis-2#1

**GT**（func）Incorrect comparison logic causes false negatives when comparing slot ranges

> The slotRangeArrayIsEqual function checks if the number of ranges are equal before normalizing and merging adjacent ranges. This causes the function to incorrectly return false (0) when comparing two slot range arrays that represent the same slots but have different numbers of ranges before merging. For example, comparing [1000-1001, 1002-1003] (2 ranges) with [1000-1003] (1 range) will return false even though they represent the same slots after merging. This breaks the task lookup functionality in asmLookupTaskBySlotRangeArray, preventing correct task identification when slot ranges are specified in different but equivalent formats.

GT 片段：`int slotRangeArrayIsEqual(slotRangeArray *slots1, slotRangeArray *slots2) { ⏎ if (slots1->num_ranges != slots2->num_ranges) return 0; ⏎ slotRangeArraySortAndMerge(slots1); ⏎ slotRangeArraySortAndMerge(slots2);`

**finding**（`src/cluster.c:1867`，距錨點 9 行，候選管道 ident）slotRangeArraySortAndMerge 合併邏輯可能錯誤處理重疊範圍

> 在 `slotRangeArraySortAndMerge` 中，合併條件僅檢查 `slots->ranges[idx].end + 1 == slots->ranges[i].start`，但未處理重疊範圍（例如 `0-10` 與 `5-15`）。若輸入包含重疊範圍，排序後 `idx` 指向的範圍可能與後續範圍重疊，但因為條件不成立，重疊範圍不會被合併，導致後續驗證可能誤判為合法（或產生未定義行為）。

**失敗情境**：呼叫 `slotRangeArrayNormalizeAndValidate` 時傳入包含重疊範圍的陣列（例如 `0-10 5-15`），排序後 `idx=0` 指向 `0-10`，`i=1` 指向 `5-15`，條件 `10+1 == 5` 不成立，因此兩個範圍都保留。後續驗證迴圈會檢查每個範圍的 start/end 是否在合法範圍內，但不會檢查重疊，因此可能通過驗證，導致後續邏輯假設範圍不重疊而產生錯誤。

**建議修法**：在合併時同時處理重疊與相鄰情況，例如將條件改為 `slots->ranges[idx].end + 1 >= slots->ranges[i].start`，並更新 end 為兩者最大值。同時在註解中明確說明重疊範圍的處理方式。

finding 片段：`if (slots->ranges[idx].end + 1 == slots->ranges[i].start) ⏎ slots->ranges[idx].end = slots->ranges[i].end;`

## base-2:redis-2:3|redis-2#2

**GT**（func）Memory leak due to missing error message reply to client

> In parseSlotRangesOrReply, when slot range validation fails, the error message allocated by slotRangeArrayNormalizeAndValidate is freed with sdsfree(err) but never sent to the client via addReplyErrorSds. This causes two problems: the client receives no error message explaining why their command failed, making debugging difficult, and it breaks the expected behavior where addReplyErrorSds transfers ownership of the sds string. The original PR intended to always send validation errors to the client for proper error reporting.

GT 片段：`sds err = NULL; ⏎ if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots);`

**finding**（`src/cluster.c:2015`，距錨點 0 行，候選管道 loc）parseSlotRangesOrReply 錯誤路徑可能遺漏錯誤訊息

> 在 `parseSlotRangesOrReply` 中，原本在 `validateSlotRanges` 失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但修改後僅執行 `sdsfree(err)` 並釋放 slots，未回覆任何錯誤。這可能導致客戶端在輸入無效的 slot range 時收到空回覆或連線中斷，而非明確的錯誤訊息。

**失敗情境**：客戶端執行 `CLUSTER MIGRATION IMPORT` 指令並提供無效的 slot range（例如 start > end），`slotRangeArrayNormalizeAndValidate` 回傳 C_ERR 並設定 err，但函式未將 err 回覆給客戶端，客戶端可能無法得知錯誤原因。

**建議修法**：在錯誤路徑中保留 `addReplyErrorSds(c, err)`，或改為 `addReplyError(c, err)` 後再釋放 err。

finding 片段：`if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots); ⏎ return NULL;`

## base-2:redis-3:1|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行，候選管道 loc）迴圈邊界錯誤導致堆積緩衝區溢位

> 在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 僅配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成堆積緩衝區溢位。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之後的記憶體，可能導致未定義行為。

**失敗情境**：當命令包含至少一個 key 時，每次呼叫此函式都會觸發溢位，可能導致程式崩潰或安全漏洞。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## base-2:redis-3:1|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行，候選管道 loc）迴圈邊界錯誤導致堆積緩衝區溢位

> 在 `extractSlotFromKeysResult` 中，迴圈條件為 `j <= keys_result->numkeys`，但 `slot_buffer` 僅配置了 `keys_result->numkeys` 個元素。當 `j == keys_result->numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體，造成堆積緩衝區溢位。此外，`argv[keys_result->keys[j].pos]` 在 `j == numkeys` 時也會讀取 `keys` 陣列之後的記憶體，可能導致未定義行為。

**失敗情境**：當命令包含至少一個 key 時，每次呼叫此函式都會觸發溢位，可能導致程式崩潰或安全漏洞。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## base-2:redis-3:2|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）記憶體配置失敗未檢查

> `malloc` 的返回值未檢查，若配置失敗（回傳 NULL），後續寫入 `slot_buffer[j]` 會導致空指標解參考，造成程式崩潰。

**失敗情境**：在記憶體不足的環境下，`malloc` 回傳 NULL，程式將在寫入時崩潰。

**建議修法**：檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-2:redis-3:2|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）記憶體配置失敗未檢查

> `malloc` 的返回值未檢查，若配置失敗（回傳 NULL），後續寫入 `slot_buffer[j]` 會導致空指標解參考，造成程式崩潰。

**失敗情境**：在記憶體不足的環境下，`malloc` 回傳 NULL，程式將在寫入時崩潰。

**建議修法**：檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-2:redis-3:3|redis-3#3

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行，候選管道 loc）slot 可能未初始化

> 在 `extractKeysAndSlot` 中，原本的程式碼在 `num_keys >= 0` 時會將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，但修改後僅在 `num_keys > 0` 時呼叫 `extractSlotFromKeysResult` 來設定 `*slot`。若 `num_keys == 0`，`*slot` 將不會被設定，可能保留呼叫者傳入的未初始化值，導致後續使用時出現未定義行為。

**失敗情境**：當命令沒有 key 時，`*slot` 可能包含垃圾值，若後續程式碼依賴此值判斷 slot，可能造成錯誤。

**建議修法**：在 `num_keys == 0` 時明確將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，或確保呼叫者已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## base-2:redis-3:4|redis-3#2

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行，候選管道 loc）條件判斷變更可能影響無 key 命令的處理

> 原本的條件 `num_keys > 0` 改為 `num_keys >= 0`，這使得 `num_keys == 0` 的命令也會進入此分支。雖然目前僅在 `pcmd->slot == CLUSTER_CROSSSLOT` 時執行操作，但若未來在此分支新增其他邏輯，可能會影響無 key 命令。此外，`num_keys == 0` 時 `pcmd->slot` 可能為 `INVALID_CLUSTER_SLOT`，不會觸發 cross-slot 處理，但條件變更本身可能隱含意圖改變。

**建議**：確認此變更是否必要，若僅為處理 cross-slot，可保留 `num_keys > 0` 並在內部檢查 `pcmd->slot == CLUSTER_CROSSSLOT`。

finding 片段：`} else if (num_keys >= 0) {`

## base-2:redis-4:1|redis-4#0

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行，候選管道 loc）clusterCommonInit 使用 malloc 可能導致記憶體洩漏

> clusterCommonInit 使用 `malloc` 配置 `server.cluster_slot_stats`，但原本在 server.c 中使用 `zmalloc`。若後續有對應的釋放邏輯使用 `zfree`，則混用配置器可能導致記憶體洩漏或未定義行為。建議改用 `zmalloc` 以保持一致。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## base-2:redis-4:1|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行，候選管道 ident）clusterCommonInit 使用 malloc 可能導致記憶體洩漏

> clusterCommonInit 使用 `malloc` 配置 `server.cluster_slot_stats`，但原本在 server.c 中使用 `zmalloc`。若後續有對應的釋放邏輯使用 `zfree`，則混用配置器可能導致記憶體洩漏或未定義行為。建議改用 `zmalloc` 以保持一致。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## base-2:redis-4:2|redis-4#0

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2139`，距錨點 0 行，候選管道 loc）clusterCommonInit 呼叫 resetClusterStats 可能使用未初始化的記憶體

> clusterCommonInit 在配置 `server.cluster_slot_stats` 後立即呼叫 `resetClusterStats()`，但若 `resetClusterStats` 會讀取該記憶體內容（例如先讀取再寫入），則可能讀到未初始化的值。建議確認 `resetClusterStats` 的實作是否只寫入而不讀取，或改用 `zcalloc` 配置。

finding 片段：`resetClusterStats();`

## base-2:redis-4:3|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 3 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 可能誤刪正在遷移的 slot 資料

> clusterDeleteKeysInUnownedSlots 在判斷是否刪除時，僅檢查 `clusterIsMySlot(i)` 和 `getImportingSlotSource(i)`，但未檢查是否正在匯出（migrating）該 slot。若節點正在匯出 slot，且該 slot 仍有本地資料，則可能被誤刪。建議加入 `getMigratingSlotDest(i)` 的檢查。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i)) ⏎ {`

## base-2:redis-4:3|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 0 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 可能誤刪正在遷移的 slot 資料

> clusterDeleteKeysInUnownedSlots 在判斷是否刪除時，僅檢查 `clusterIsMySlot(i)` 和 `getImportingSlotSource(i)`，但未檢查是否正在匯出（migrating）該 slot。若節點正在匯出 slot，且該 slot 仍有本地資料，則可能被誤刪。建議加入 `getMigratingSlotDest(i)` 的檢查。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i)) ⏎ {`

## base-2:redis-4:5|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2160`，距錨點 10 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 的日誌訊息可能誤導

> 日誌訊息寫「Deleting keys in the slot.」但未說明原因，且可能與 clusterClaimUnassignedSlots 的日誌混淆。建議增加更具體的上下文，例如 slot 的擁有者資訊。

finding 片段：`serverLog(LL_NOTICE, "I have keys for slot %d, but the slot is " ⏎ "assigned to another node. " ⏎ "Deleting keys in the slot.", i);`

## base-2:redis-4:5|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2160`，距錨點 3 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 的日誌訊息可能誤導

> 日誌訊息寫「Deleting keys in the slot.」但未說明原因，且可能與 clusterClaimUnassignedSlots 的日誌混淆。建議增加更具體的上下文，例如 slot 的擁有者資訊。

finding 片段：`serverLog(LL_NOTICE, "I have keys for slot %d, but the slot is " ⏎ "assigned to another node. " ⏎ "Deleting keys in the slot.", i);`

## base-2:redis-4:6|redis-4#2

**GT**（func）ASM cron runs before cluster state update causing stale state issues

> The serverCron() function now calls asmCron() before clusterCron(). This is problematic because clusterCron() contains the call to clusterUpdateState() which updates the cluster's operational state (CLUSTER_OK vs CLUSTER_FAIL). ASM (Atomic Slot Migration) operations depend on having an accurate view of the cluster state to make correct migration decisions. By executing asmCron() first, migration tasks may operate on stale cluster state information from the previous iteration, potentially leading to incorrect slot migration decisions, failed migrations, or data consistency issues during cluster rebalancing operations.

GT 片段：`if (server.cluster_enabled) { ⏎ asmCron(); ⏎ clusterCron(); ⏎ }`

**finding**（`src/server.c:1658`，距錨點 0 行，候選管道 loc）asmCron 與 clusterCron 的呼叫順序可能影響行為

> 原本 asmCron 在 clusterCron 內部呼叫，現在移至 serverCron 中並在 clusterCron 之前呼叫。若 asmCron 依賴 clusterCron 更新後的狀態，則可能導致行為差異。建議確認 asmCron 的相依性。

finding 片段：`asmCron(); ⏎ clusterCron();`

## base-2:redis-5:1|redis-5#0

**GT**（rule）Direct malloc_usable_size instead of zmalloc_size

> The rule requires all memory operations to use Redis zmalloc wrappers (zmalloc_size) instead of direct libc functions (malloc_usable_size)

GT 片段：`/* All kv-objects has at least kvobj header and embedded key */ ⏎ size_t asize = malloc_usable_size((void *)o);`

**finding**（`src/object.c:1239`，距錨點 22 行，候選管道 ident）quicklist 抽樣平均計算可能低估記憶體使用量

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount` 來計算平均每個元素的實際大小，但此 PR 改為 `elesize/samples`。由於 `samples` 是抽樣的節點數，而 `elecount` 是抽樣節點中的元素總數，兩者通常不相等。若每個節點包含多個元素，`samples` 會小於 `elecount`，導致平均大小被高估；反之若節點數多於元素數（例如空節點），則可能低估。這會使 `MEMORY USAGE` 回報不準確的數值。建議改回使用 `elecount` 作為分母，或明確計算每個節點的平均元素數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-2:redis-5:1|redis-5#1

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 抽樣平均計算可能低估記憶體使用量

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount` 來計算平均每個元素的實際大小，但此 PR 改為 `elesize/samples`。由於 `samples` 是抽樣的節點數，而 `elecount` 是抽樣節點中的元素總數，兩者通常不相等。若每個節點包含多個元素，`samples` 會小於 `elecount`，導致平均大小被高估；反之若節點數多於元素數（例如空節點），則可能低估。這會使 `MEMORY USAGE` 回報不準確的數值。建議改回使用 `elecount` 作為分母，或明確計算每個節點的平均元素數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-2:redis-5:1|redis-5#4

**GT**（func）Unused variable 'elecount' causes build failure with -Werror

> The variable 'elecount' is declared and incremented in the QUICKLIST encoding branch (line 1236: 'elecount += node->count') but is never used after the PR changed the calculation from 'elesize/elecount' to 'elesize/samples'. This creates an unused-but-set variable which triggers compiler warnings under -Wall (enabled in Makefile) and causes build failures when compiling with -Werror flag. This violates AGENTS.MD Rule #4 which requires the codebase to compile without warnings when REDIS_CFLAGS="-Werror" is enabled.

GT 片段：`size_t elesize = 0, elecount = 0, samples = 0; ⏎ ... ⏎ if (o->encoding == OBJ_ENCODING_QUICKLIST) { ⏎ quicklist *ql = o->ptr;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 抽樣平均計算可能低估記憶體使用量

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount` 來計算平均每個元素的實際大小，但此 PR 改為 `elesize/samples`。由於 `samples` 是抽樣的節點數，而 `elecount` 是抽樣節點中的元素總數，兩者通常不相等。若每個節點包含多個元素，`samples` 會小於 `elecount`，導致平均大小被高估；反之若節點數多於元素數（例如空節點），則可能低估。這會使 `MEMORY USAGE` 回報不準確的數值。建議改回使用 `elecount` 作為分母，或明確計算每個節點的平均元素數。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-2:redis-5:2|redis-5#2

**GT**（func）Variable shadowing breaks sampling consistency for STREAM objects

> A local `samples` variable is declared at line 1319 within the OBJ_STREAM branch, shadowing the outer `samples` variable declared at line 1214. This prevents the outer samples counter from being updated during stream memory calculation. While this doesn't break the stream calculation itself, it violates the function's sampling design pattern where the outer `samples` variable tracks total sampling across all object type branches. This inconsistency could lead to unexpected behavior if the function logic is modified to check or use the outer samples counter after processing.

GT 片段：`raxStart(&ri,s->rax); ⏎ raxSeek(&ri,"^",NULL,0); ⏎ size_t lpsize = 0; ⏎ size_t samples = 0;`

**finding**（`src/object.c:1330`，距錨點 10 行，候選管道 ident）stream listpack 估算可能高估記憶體使用量

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 來估算所有 listpack 的總大小，但此 PR 改為 `lpsize * s->rax->numele`。這可能導致高估，因為最後一個 listpack 可能尚未滿，且其大小可能與平均不同。原本的 `-1` 可能是為了排除最後一個 listpack 的影響，或考慮到其他因素。建議確認此變更的意圖，並確保估算值不會明顯偏離實際記憶體使用量。

finding 片段：`asize += lpsize * s->rax->numele;`

## base-2:redis-5:2|redis-5#3

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行，候選管道 loc）stream listpack 估算可能高估記憶體使用量

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 來估算所有 listpack 的總大小，但此 PR 改為 `lpsize * s->rax->numele`。這可能導致高估，因為最後一個 listpack 可能尚未滿，且其大小可能與平均不同。原本的 `-1` 可能是為了排除最後一個 listpack 的影響，或考慮到其他因素。建議確認此變更的意圖，並確保估算值不會明顯偏離實際記憶體使用量。

finding 片段：`asize += lpsize * s->rax->numele;`

## base-2:redis-6:1|redis-6#1

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1961`，距錨點 0 行，候選管道 loc）active_defrag_enabled 恢復為硬編碼 1，未使用原始值

> 在 rdbLoadEmptyDbFunc 中，程式碼先將 server.active_defrag_enabled 儲存於 orig_active_defrag，但在 emptyData 呼叫後卻直接設定為 1，而非恢復為 orig_active_defrag。若原始值為 0（例如使用者明確停用 active defrag），此函式會意外啟用 active defrag，導致行為不一致。

失敗情境：當使用者在設定檔中設定 activedefrag no，且 replica 進行同步時，此函式會將 active_defrag_enabled 設為 1，之後 active defrag 可能被觸發，造成不必要的效能影響或潛在錯誤。

建議修改：
```c
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`/* Restore the original active defragmentation setting. */ ⏎ server.active_defrag_enabled = 1;`

## base-2:redis-6:1|redis-6#4

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1961`，距錨點 0 行，候選管道 loc）active_defrag_enabled 恢復為硬編碼 1，未使用原始值

> 在 rdbLoadEmptyDbFunc 中，程式碼先將 server.active_defrag_enabled 儲存於 orig_active_defrag，但在 emptyData 呼叫後卻直接設定為 1，而非恢復為 orig_active_defrag。若原始值為 0（例如使用者明確停用 active defrag），此函式會意外啟用 active defrag，導致行為不一致。

失敗情境：當使用者在設定檔中設定 activedefrag no，且 replica 進行同步時，此函式會將 active_defrag_enabled 設為 1，之後 active defrag 可能被觸發，造成不必要的效能影響或潛在錯誤。

建議修改：
```c
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`/* Restore the original active defragmentation setting. */ ⏎ server.active_defrag_enabled = 1;`

## base-2:redis-6:2|redis-6#3

**GT**（func）Inverted reply discard logic causes test infrastructure failure

> The condition for discarding replies is inverted - replies are discarded when count is NOT a multiple of frequency (!=), rather than when it IS a multiple (==). This causes the test to read and discard replies at the wrong times, leading to a buffer overflow of unread replies. The discard_replies_every helper is called throughout the test suite after batches of Redis commands to prevent reply buffer buildup. With this bug, replies accumulate in the buffer instead of being cleared, causing test hangs or failures when the client tries to send new commands with a full reply buffer.

GT 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

**finding**（`tests/unit/memefficiency.tcl:70`，距錨點 0 行，候選管道 loc）discard_replies_every 輔助函式邏輯錯誤：只在 count 為 frequency 的倍數時丟棄回覆

> 函式 `discard_replies_every` 的條件 `if {$count % $frequency != 0}` 表示當 count 不是 frequency 的倍數時才執行丟棄，這與函式名稱和原本的意圖相反。原本的程式碼是在 count 為 10000 的倍數時丟棄 10000 個回覆，但新函式卻在 count 不是倍數時丟棄，導致回覆未被正確丟棄，可能造成測試客戶端緩衝區累積過多資料，影響測試穩定性。

失敗情境：在測試迴圈中，當 count 達到 10000 的倍數時，不會丟棄任何回覆，而其他時候卻丟棄 10000 個回覆，導致客戶端讀取錯誤的回覆或記憶體耗盡。

建議修改：
```tcl
proc discard_replies_every {rd count frequency discard_num} {
    if {$count % $frequency == 0} {
        for {set k 0} {$k < $discard_num} {incr k} {
            $rd read ; # Discard replies
        }
    }
}
```

finding 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

## base-2:redis-6:3|redis-6#2

**GT**（func）Stream entries incorrectly marked as referenced when cgroups_ref is NULL

> When cgroups_ref is NULL (which occurs after DEBUG RELOAD with empty PEL), the function returns 1 indicating the entry IS referenced, when it should return 0 indicating it is NOT referenced. This inverted logic prevents XADD/XTRIM operations with the ACKED strategy from correctly deleting entries that have been fully acknowledged by all consumer groups. The result is a memory leak where stream entries accumulate unnecessarily because they are incorrectly protected from deletion even though no consumer group has them in their pending entry list.

GT 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1; ⏎ unsigned char buf[sizeof(streamID)]; ⏎ streamEncodeID(buf, id);`

**finding**（`src/t_stream.c:2707`，距錨點 0 行，候選管道 loc）streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1，可能導致記憶體洩漏或錯誤保留

> 新增的 null 檢查 `if (!s->cgroups_ref) return 1;` 表示當 stream 沒有 consumer groups 時，函式直接回傳 1（視為被引用）。這可能導致呼叫者認為 entry 被引用而無法刪除，造成記憶體洩漏或資料保留過久。

失敗情境：當一個 stream 沒有 consumer groups，且執行 XTRIM 或 MAXLEN 刪除舊 entry 時，此函式回傳 1，導致 entry 被保留，無法正確修剪。

建議：確認此行為是否符合預期。若無 cgroups 時 entry 不應被視為引用，應回傳 0；若此為刻意設計（例如保守處理），應加入註解說明。

finding 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1;`

## base-2:redis-7:1|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1725`，距錨點 2 行，候選管道 loc）valid_up_to 為 -1 時仍可能嘗試截斷

> 在 `fmterr` 處理中，若 `valid_up_to == -1`，程式只記錄警告，但之後仍會繼續執行到 `ret = AOF_FAILED` 並跳至 cleanup，不會嘗試截斷。然而，若 `valid_up_to` 為 -1 但 `server.aof_load_broken` 為真，且 `sb.st_size - valid_up_to` 小於限制（實際上會是很大的正數），條件 `(size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size` 可能意外成立，導致對檔案進行截斷。建議在 `valid_up_to == -1` 時直接跳過截斷邏輯，或明確檢查 `valid_up_to >= 0`。

finding 片段：`if (valid_up_to == -1) { ⏎ serverLog(LL_WARNING,"Last valid command offset is invalid"); ⏎ } else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

## base-2:redis-7:2|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行，候選管道 loc）截斷後未更新 AOF 檔案大小或相關狀態

> 呼叫 `truncate(aof_filepath, valid_up_to)` 後，程式僅將 `server.aof_fd` 的檔案偏移移至結尾，但未更新 `sb.st_size` 或其他可能快取的檔案大小資訊。若後續程式依賴 `sb.st_size` 或 AOF 檔案大小來判斷載入進度，可能產生不一致。建議在截斷後重新取得檔案狀態，或確保所有相關變數同步更新。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## base-2:redis-7:4|redis-7#2

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1830`，距錨點 11 行，候選管道 ident）AOF_BROKEN_RECOVERED 在非最後檔案時被視為致命錯誤，但日誌訊息仍稱「truncated」

> 在 `loadAppendOnlyFiles` 中，若 `ret == AOF_BROKEN_RECOVERED` 且不是最後一個檔案，程式會記錄「Fatal error: the truncated file is not the last file」。此處的「truncated」可能造成混淆，因為實際上是格式錯誤後自動截斷。建議調整日誌訊息以區分兩種情況。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## base-2:redis-7:5|redis-7#0

**GT**（rule）Single underscore include guard used

> The rule requires header files to use include guards with double underscores at the start (e.g., __FILENAME_H), but the code uses a single underscore prefix instead (_REDIS_H)

GT 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

**finding**（`src/server.h:15`，距錨點 0 行，候選管道 loc）變更 include guard 巨集名稱可能影響外部程式碼

> 將 `__REDIS_H` 改為 `_REDIS_H` 可能導致與其他使用相同 guard 的程式碼衝突，或破壞依賴舊巨集名稱的條件編譯。雖然影響不大，但建議確認此變更的必要性。

finding 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

## base-2:redis-8:1|redis-8#1

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）記憶體洩漏：argv[2] 未釋放

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## base-2:redis-8:1|redis-8#3

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）記憶體洩漏：argv[2] 未釋放

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## base-2:redis-8:1|redis-8#4

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）記憶體洩漏：argv[2] 未釋放

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);`，但在 `alsoPropagate` 之後沒有呼叫 `decrRefCount(argv[2])`。這會導致每次執行此路徑時洩漏一個 string object 的記憶體。建議在 `alsoPropagate` 之後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## base-2:redis-8:2|redis-8#2

**GT**（func）Off-by-one error in field expiration comparison

> The expiration check uses strict greater-than (>) instead of greater-than-or-equal (>=) when comparing expiredAt with commandTimeSnapshot(). This causes fields that expire at exactly the current timestamp to be incorrectly treated as expired. In high-frequency operations, this can lead to premature field expiration and data loss, especially affecting the HINCRBYFLOAT operation's ability to preserve field TTL correctly.

GT 片段：`if (*expiredAt > (uint64_t) commandTimeSnapshot()) ⏎ return GETF_OK;`

**finding**（`src/t_hash.c:742`，距錨點 0 行，候選管道 loc）邊界條件變更：>= 改為 > 可能影響過期判斷

> 原本的判斷是 `if (expiredAt >= (uint64_t) commandTimeSnapshot())`，現在改為 `if (*expiredAt > (uint64_t) commandTimeSnapshot())`。這表示當 `expiredAt` 等於當前時間時，原本會被視為未過期，現在會被視為已過期。這可能導致在時間邊界上的行為差異，例如欄位剛好在同一毫秒過期時，原本可能回傳值，現在會回傳過期。需要確認此變更是否為預期行為，並考慮是否應保留 `>=` 以維持原有語意。

finding 片段：`if (*expiredAt > (uint64_t) commandTimeSnapshot()) ⏎ return GETF_OK;`

## base-2:redis-9:1|redis-9#0

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行，候選管道 loc）rewriteClientCommandVector 參數數量與格式可能不正確

> `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，第一個參數 `6` 表示新 argv 的元素數量，但實際傳入的參數有 7 個（hsetex, key, keepttl, fields, 1, field, value）。這可能導致指令向量建構錯誤，進而影響複寫內容。請確認 `rewriteClientCommandVector` 的實作，並修正參數數量。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## base-2:redis-9:1|redis-9#1

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2571`，距錨點 11 行，候選管道 ident）rewriteClientCommandVector 參數數量與格式可能不正確

> `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，第一個參數 `6` 表示新 argv 的元素數量，但實際傳入的參數有 7 個（hsetex, key, keepttl, fields, 1, field, value）。這可能導致指令向量建構錯誤，進而影響複寫內容。請確認 `rewriteClientCommandVector` 的實作，並修正參數數量。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## base-2:redis-9:1|redis-9#2

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2571`，距錨點 0 行，候選管道 loc）rewriteClientCommandVector 參數數量與格式可能不正確

> `rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, shared.fields, shared.integers[1], c->argv[2], newobj)` 中，第一個參數 `6` 表示新 argv 的元素數量，但實際傳入的參數有 7 個（hsetex, key, keepttl, fields, 1, field, value）。這可能導致指令向量建構錯誤，進而影響複寫內容。請確認 `rewriteClientCommandVector` 的實作，並修正參數數量。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## base-2:redis-9:2|redis-9#0

**GT**（rule）Helper function missing static keyword

> The rule requires that helper functions used only within a single source file should be declared with the 'static' keyword to limit their visibility to that compilation unit. The function addHashFieldToReply is only used within t_hash.c but is declared without 'static', making it unnecessarily visible to other compilation units.

GT 片段：`GetFieldRes addHashFieldToReply(client *c, kvobj *o, sds field, int hfeFlags) { ⏎ if (o == NULL) { ⏎ addReplyNull(c); ⏎ return GETF_NOT_FOUND;`

**finding**（`src/t_hash.c:2571`，距錨點 5 行，候選管道 loc）HSETEX 指令格式可能不正確

> HSETEX 的語法為 `HSETEX key [EX seconds|PX milliseconds|EXAT unix-time|PXAT unix-time|KEEPTTL] [FIELDS numfields field value [field value ...]]`。此處使用 `shared.integers[1]` 作為 FIELDS 的數量，但未確認 `shared.integers[1]` 是否為字串 "1"。若該共享整數物件不是 "1"，將導致複寫指令格式錯誤。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## base-2:redis-9:2|redis-9#1

**GT**（func）HINCRBYFLOAT removes field expiration time locally on master

> The hincrbyfloatCommand function is missing the HASH_SET_KEEP_TTL flag when calling hashTypeSet. While the replication command correctly uses KEEPTTL to preserve field TTL for replicas and AOF, the local execution on the master immediately removes any existing field expiration time. This creates an inconsistency where the field loses its TTL on the master but the replicated HSETEX command attempts to keep it. The test at line 1987 expects field f1 to retain its TTL after HINCRBYFLOAT, but this bug causes the TTL to be cleared locally.

GT 片段：`char buf[MAX_LONG_DOUBLE_CHARS]; ⏎ int len = ld2string(buf,sizeof(buf),value,LD_STR_HUMAN); ⏎ new = sdsnewlen(buf,len); ⏎ hashTypeSet(c->db, o,c->argv[2]->ptr,new,HASH_SET_TAKE_VALUE);`

**finding**（`src/t_hash.c:2571`，距錨點 11 行，候選管道 ident）HSETEX 指令格式可能不正確

> HSETEX 的語法為 `HSETEX key [EX seconds|PX milliseconds|EXAT unix-time|PXAT unix-time|KEEPTTL] [FIELDS numfields field value [field value ...]]`。此處使用 `shared.integers[1]` 作為 FIELDS 的數量，但未確認 `shared.integers[1]` 是否為字串 "1"。若該共享整數物件不是 "1"，將導致複寫指令格式錯誤。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## base-2:redis-9:2|redis-9#2

**GT**（func）Incorrect argument count in rewriteClientCommandVector causes malformed replication

> The rewriteClientCommandVector call passes 6 as the argument count, but actually provides 7 arguments (HSETEX, key, KEEPTTL, FIELDS, 1, field, value). This mismatch causes the replication command to be truncated, omitting the final argument (the new field value). Replicas and AOF will receive an incomplete HSETEX command missing the field value, leading to command execution failures on replicas, replication inconsistencies, and potential data corruption. The test expects the replication stream to contain a complete HSETEX command with all arguments.

GT 片段：`robj *newobj; ⏎ newobj = createRawStringObject(buf,len); ⏎ rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

**finding**（`src/t_hash.c:2571`，距錨點 0 行，候選管道 loc）HSETEX 指令格式可能不正確

> HSETEX 的語法為 `HSETEX key [EX seconds|PX milliseconds|EXAT unix-time|PXAT unix-time|KEEPTTL] [FIELDS numfields field value [field value ...]]`。此處使用 `shared.integers[1]` 作為 FIELDS 的數量，但未確認 `shared.integers[1]` 是否為字串 "1"。若該共享整數物件不是 "1"，將導致複寫指令格式錯誤。

finding 片段：`rewriteClientCommandVector(c, 6, shared.hsetex, c->argv[1], shared.keepttl, ⏎ shared.fields, shared.integers[1], c->argv[2], newobj);`

## base-2:tauri-1:1|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 6 行，候選管道 ident）自動遞增 versionCode 存在競態條件

> 在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## base-2:tauri-1:1|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 0 行，候選管道 loc）自動遞增 versionCode 存在競態條件

> 在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## base-2:tauri-1:1|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 12 行，候選管道 ident）自動遞增 versionCode 存在競態條件

> 在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## base-2:tauri-1:1|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 40 行，候選管道 ident）自動遞增 versionCode 存在競態條件

> 在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## base-2:tauri-1:1|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 9 行，候選管道 ident）自動遞增 versionCode 存在競態條件

> 在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## base-2:tauri-1:1|tauri-1#5

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 7 行，候選管道 ident）自動遞增 versionCode 存在競態條件

> 在 `generate_tauri_properties` 中，讀取 `tauri.properties` 取得 `last_version_code` 後直接加 1 寫回，但讀取與寫入之間沒有鎖定或原子操作。若同時執行多個 build（例如 CI 平行建置），可能導致多個 build 讀到相同的 `last_version_code`，產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移至單一進程中處理。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## base-2:tauri-1:2|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 6 行，候選管道 ident）讀取 tauri.properties 失敗時靜默回退為 1

> 當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式會靜默地將 `new_version_code` 設為 1。這可能導致在檔案暫時無法讀取時意外重置版本碼，造成版本碼倒退。建議區分檔案不存在與其他錯誤：若檔案不存在，可視為首次建置；若為其他錯誤，應回報錯誤。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

## base-2:tauri-1:2|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 0 行，候選管道 loc）讀取 tauri.properties 失敗時靜默回退為 1

> 當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式會靜默地將 `new_version_code` 設為 1。這可能導致在檔案暫時無法讀取時意外重置版本碼，造成版本碼倒退。建議區分檔案不存在與其他錯誤：若檔案不存在，可視為首次建置；若為其他錯誤，應回報錯誤。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

## base-2:tauri-1:2|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 12 行，候選管道 ident）讀取 tauri.properties 失敗時靜默回退為 1

> 當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式會靜默地將 `new_version_code` 設為 1。這可能導致在檔案暫時無法讀取時意外重置版本碼，造成版本碼倒退。建議區分檔案不存在與其他錯誤：若檔案不存在，可視為首次建置；若為其他錯誤，應回報錯誤。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

## base-2:tauri-1:2|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 40 行，候選管道 ident）讀取 tauri.properties 失敗時靜默回退為 1

> 當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式會靜默地將 `new_version_code` 設為 1。這可能導致在檔案暫時無法讀取時意外重置版本碼，造成版本碼倒退。建議區分檔案不存在與其他錯誤：若檔案不存在，可視為首次建置；若為其他錯誤，應回報錯誤。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

## base-2:tauri-1:2|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 9 行，候選管道 ident）讀取 tauri.properties 失敗時靜默回退為 1

> 當 `std::fs::read_to_string` 失敗（例如檔案不存在或權限不足）時，程式會靜默地將 `new_version_code` 設為 1。這可能導致在檔案暫時無法讀取時意外重置版本碼，造成版本碼倒退。建議區分檔案不存在與其他錯誤：若檔案不存在，可視為首次建置；若為其他錯誤，應回報錯誤。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

## base-2:tauri-1:3|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:643`，距錨點 13 行，候選管道 ident）解析 versionCode 失敗時靜默回退為 1

> 若 `tauri.properties` 中的 `tauri.android.versionCode` 值不是有效的 `u32`（例如被手動修改或損壞），解析會失敗並回退為 1。這可能導致版本碼意外重置。建議在解析失敗時回報錯誤，或至少記錄警告。

finding 片段：`.and_then(|s| s.trim().parse::<u32>().ok())`

## base-2:tauri-1:3|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:643`，距錨點 0 行，候選管道 loc）解析 versionCode 失敗時靜默回退為 1

> 若 `tauri.properties` 中的 `tauri.android.versionCode` 值不是有效的 `u32`（例如被手動修改或損壞），解析會失敗並回退為 1。這可能導致版本碼意外重置。建議在解析失敗時回報錯誤，或至少記錄警告。

finding 片段：`.and_then(|s| s.trim().parse::<u32>().ok())`

## base-2:tauri-1:3|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:643`，距錨點 5 行，候選管道 loc）解析 versionCode 失敗時靜默回退為 1

> 若 `tauri.properties` 中的 `tauri.android.versionCode` 值不是有效的 `u32`（例如被手動修改或損壞），解析會失敗並回退為 1。這可能導致版本碼意外重置。建議在解析失敗時回報錯誤，或至少記錄警告。

finding 片段：`.and_then(|s| s.trim().parse::<u32>().ok())`

## base-2:tauri-1:3|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:643`，距錨點 33 行，候選管道 ident）解析 versionCode 失敗時靜默回退為 1

> 若 `tauri.properties` 中的 `tauri.android.versionCode` 值不是有效的 `u32`（例如被手動修改或損壞），解析會失敗並回退為 1。這可能導致版本碼意外重置。建議在解析失敗時回報錯誤，或至少記錄警告。

finding 片段：`.and_then(|s| s.trim().parse::<u32>().ok())`

## base-2:tauri-1:3|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:643`，距錨點 2 行，候選管道 loc）解析 versionCode 失敗時靜默回退為 1

> 若 `tauri.properties` 中的 `tauri.android.versionCode` 值不是有效的 `u32`（例如被手動修改或損壞），解析會失敗並回退為 1。這可能導致版本碼意外重置。建議在解析失敗時回報錯誤，或至少記錄警告。

finding 片段：`.and_then(|s| s.trim().parse::<u32>().ok())`

## base-2:tauri-1:4|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行，候選管道 ident）saturating_add 可能導致版本碼停在最大值

> 使用 `saturating_add(1)` 在 `last_version_code` 已達 `u32::MAX` 時會停留在最大值，但 Android 的 `versionCode` 上限為 2100000000。若 `tauri.properties` 中的值已達上限，遞增後會超過限制，但此處未檢查。建議在遞增後檢查是否超過 2100000000，若超過則回報錯誤。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-2:tauri-1:4|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）saturating_add 可能導致版本碼停在最大值

> 使用 `saturating_add(1)` 在 `last_version_code` 已達 `u32::MAX` 時會停留在最大值，但 Android 的 `versionCode` 上限為 2100000000。若 `tauri.properties` 中的值已達上限，遞增後會超過限制，但此處未檢查。建議在遞增後檢查是否超過 2100000000，若超過則回報錯誤。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-2:tauri-1:4|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行，候選管道 loc）saturating_add 可能導致版本碼停在最大值

> 使用 `saturating_add(1)` 在 `last_version_code` 已達 `u32::MAX` 時會停留在最大值，但 Android 的 `versionCode` 上限為 2100000000。若 `tauri.properties` 中的值已達上限，遞增後會超過限制，但此處未檢查。建議在遞增後檢查是否超過 2100000000，若超過則回報錯誤。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-2:tauri-1:4|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行，候選管道 ident）saturating_add 可能導致版本碼停在最大值

> 使用 `saturating_add(1)` 在 `last_version_code` 已達 `u32::MAX` 時會停留在最大值，但 Android 的 `versionCode` 上限為 2100000000。若 `tauri.properties` 中的值已達上限，遞增後會超過限制，但此處未檢查。建議在遞增後檢查是否超過 2100000000，若超過則回報錯誤。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-2:tauri-1:4|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）saturating_add 可能導致版本碼停在最大值

> 使用 `saturating_add(1)` 在 `last_version_code` 已達 `u32::MAX` 時會停留在最大值，但 Android 的 `versionCode` 上限為 2100000000。若 `tauri.properties` 中的值已達上限，遞增後會超過限制，但此處未檢查。建議在遞增後檢查是否超過 2100000000，若超過則回報錯誤。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-2:tauri-1:5|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 22 行，候選管道 ident）dev 模式下的 versionCode 計算順序可能導致非預期結果

> 在 `dev` 模式下，程式先檢查 `version_code` 是否為 0 或超過上限，然後才進行 `clamp(1, 2100000000)`。若原始 `version_code` 超過上限，會先觸發錯誤，但若原始值為 0，則會通過檢查後被 clamp 為 1。這與先前在 `tauri-build` 中的行為一致，但建議確認此順序是否符合預期。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## base-2:tauri-1:5|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 6 行，候選管道 ident）dev 模式下的 versionCode 計算順序可能導致非預期結果

> 在 `dev` 模式下，程式先檢查 `version_code` 是否為 0 或超過上限，然後才進行 `clamp(1, 2100000000)`。若原始 `version_code` 超過上限，會先觸發錯誤，但若原始值為 0，則會通過檢查後被 clamp 為 1。這與先前在 `tauri-build` 中的行為一致，但建議確認此順序是否符合預期。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## base-2:tauri-1:5|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 0 行，候選管道 loc）dev 模式下的 versionCode 計算順序可能導致非預期結果

> 在 `dev` 模式下，程式先檢查 `version_code` 是否為 0 或超過上限，然後才進行 `clamp(1, 2100000000)`。若原始 `version_code` 超過上限，會先觸發錯誤，但若原始值為 0，則會通過檢查後被 clamp 為 1。這與先前在 `tauri-build` 中的行為一致，但建議確認此順序是否符合預期。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## base-2:tauri-1:5|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 24 行，候選管道 ident）dev 模式下的 versionCode 計算順序可能導致非預期結果

> 在 `dev` 模式下，程式先檢查 `version_code` 是否為 0 或超過上限，然後才進行 `clamp(1, 2100000000)`。若原始 `version_code` 超過上限，會先觸發錯誤，但若原始值為 0，則會通過檢查後被 clamp 為 1。這與先前在 `tauri-build` 中的行為一致，但建議確認此順序是否符合預期。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## base-2:tauri-1:5|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 6 行，候選管道 ident）dev 模式下的 versionCode 計算順序可能導致非預期結果

> 在 `dev` 模式下，程式先檢查 `version_code` 是否為 0 或超過上限，然後才進行 `clamp(1, 2100000000)`。若原始 `version_code` 超過上限，會先觸發錯誤，但若原始值為 0，則會通過檢查後被 clamp 為 1。這與先前在 `tauri-build` 中的行為一致，但建議確認此順序是否符合預期。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## base-2:tauri-1:6|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:680`，距錨點 34 行，候選管道 ident）寫入 tauri.properties 時未處理檔案不存在以外的錯誤

> 寫入 `tauri.properties` 時使用 `write`，若目錄不存在或權限不足會回傳錯誤，但錯誤訊息僅為「failed to write tauri.properties」，未包含路徑或更詳細的上下文。建議使用 `with_context` 加入路徑資訊。

finding 片段：`write(&app_tauri_properties_path, app_tauri_properties_content) ⏎ .context("failed to write tauri.properties")?;`

## base-2:tauri-1:6|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:680`，距錨點 16 行，候選管道 ident）寫入 tauri.properties 時未處理檔案不存在以外的錯誤

> 寫入 `tauri.properties` 時使用 `write`，若目錄不存在或權限不足會回傳錯誤，但錯誤訊息僅為「failed to write tauri.properties」，未包含路徑或更詳細的上下文。建議使用 `with_context` 加入路徑資訊。

finding 片段：`write(&app_tauri_properties_path, app_tauri_properties_content) ⏎ .context("failed to write tauri.properties")?;`

## base-2:tauri-1:6|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:680`，距錨點 0 行，候選管道 loc）寫入 tauri.properties 時未處理檔案不存在以外的錯誤

> 寫入 `tauri.properties` 時使用 `write`，若目錄不存在或權限不足會回傳錯誤，但錯誤訊息僅為「failed to write tauri.properties」，未包含路徑或更詳細的上下文。建議使用 `with_context` 加入路徑資訊。

finding 片段：`write(&app_tauri_properties_path, app_tauri_properties_content) ⏎ .context("failed to write tauri.properties")?;`

## base-2:tauri-1:6|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:680`，距錨點 34 行，候選管道 ident）寫入 tauri.properties 時未處理檔案不存在以外的錯誤

> 寫入 `tauri.properties` 時使用 `write`，若目錄不存在或權限不足會回傳錯誤，但錯誤訊息僅為「failed to write tauri.properties」，未包含路徑或更詳細的上下文。建議使用 `with_context` 加入路徑資訊。

finding 片段：`write(&app_tauri_properties_path, app_tauri_properties_content) ⏎ .context("failed to write tauri.properties")?;`

## base-2:tauri-1:7|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:633`，距錨點 3 行，候選管道 loc）generate_tauri_properties 未處理 version 為 None 的情況

> 若 `tauri_config.version` 為 `None`，函式不會產生任何內容，但也不會回報錯誤。這可能導致 `tauri.properties` 缺少必要的 `versionName` 和 `versionCode`，進而影響 Android 建置。建議確認 `version` 是否為必要欄位，若為必要則應在缺失時回報錯誤。

finding 片段：`if let Some(version) = tauri_config.version.as_ref() {`

## base-2:tauri-1:7|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:633`，距錨點 2 行，候選管道 loc）generate_tauri_properties 未處理 version 為 None 的情況

> 若 `tauri_config.version` 為 `None`，函式不會產生任何內容，但也不會回報錯誤。這可能導致 `tauri.properties` 缺少必要的 `versionName` 和 `versionCode`，進而影響 Android 建置。建議確認 `version` 是否為必要欄位，若為必要則應在缺失時回報錯誤。

finding 片段：`if let Some(version) = tauri_config.version.as_ref() {`

## base-2:tauri-1:7|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:633`，距錨點 15 行，候選管道 ident）generate_tauri_properties 未處理 version 為 None 的情況

> 若 `tauri_config.version` 為 `None`，函式不會產生任何內容，但也不會回報錯誤。這可能導致 `tauri.properties` 缺少必要的 `versionName` 和 `versionCode`，進而影響 Android 建置。建議確認 `version` 是否為必要欄位，若為必要則應在缺失時回報錯誤。

finding 片段：`if let Some(version) = tauri_config.version.as_ref() {`

## base-2:tauri-1:7|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:633`，距錨點 12 行，候選管道 ident）generate_tauri_properties 未處理 version 為 None 的情況

> 若 `tauri_config.version` 為 `None`，函式不會產生任何內容，但也不會回報錯誤。這可能導致 `tauri.properties` 缺少必要的 `versionName` 和 `versionCode`，進而影響 Android 建置。建議確認 `version` 是否為必要欄位，若為必要則應在缺失時回報錯誤。

finding 片段：`if let Some(version) = tauri_config.version.as_ref() {`

## base-2:tauri-1:7|tauri-1#5

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:633`，距錨點 4 行，候選管道 loc）generate_tauri_properties 未處理 version 為 None 的情況

> 若 `tauri_config.version` 為 `None`，函式不會產生任何內容，但也不會回報錯誤。這可能導致 `tauri.properties` 缺少必要的 `versionName` 和 `versionCode`，進而影響 Android 建置。建議確認 `version` 是否為必要欄位，若為必要則應在缺失時回報錯誤。

finding 片段：`if let Some(version) = tauri_config.version.as_ref() {`

## base-2:tauri-10:1|tauri-10#0

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行，候選管道 loc）window_features 中 size 與 position 的處理順序變更可能影響視窗初始位置

> 原本先處理 position 再處理 size，現在順序對調。在部分平台上，設定 size 後再設定 position 可能導致視窗位置被重置或偏移。建議確認此變更是否為預期行為，並在相關平台上測試。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## base-2:tauri-10:1|tauri-10#2

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行，候選管道 loc）window_features 中 size 與 position 的處理順序變更可能影響視窗初始位置

> 原本先處理 position 再處理 size，現在順序對調。在部分平台上，設定 size 後再設定 position 可能導致視窗位置被重置或偏移。建議確認此變更是否為預期行為，並在相關平台上測試。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## base-2:tauri-10:2|tauri-10#3

**GT**（func）Changed window naming pattern breaks window label consistency

> The window label format for dynamically created windows has been changed from "new-{number}" to "new-window-{number}". This breaks the established naming convention and will cause any code that attempts to retrieve or manipulate these windows using the expected label format to fail. For example, code trying to access "new-0" or "new-1" will not find the windows, as they are now named "new-window-0" and "new-window-1". This affects window management, event handling, and any window lookup operations that depend on the label pattern.

GT 片段：`let number = created_window_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed); ⏎ let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"),`

**finding**（`examples/api/src-tauri/src/lib.rs:84`，距錨點 3 行，候選管道 loc）on_new_window 移至桌面平台專屬區塊可能導致非桌面平台行為不一致

> 原本 on_new_window 在所有平台都會設定，現在僅在桌面平台（desktop）設定。若其他平台需要處理新視窗，可能導致功能缺失。請確認此變更是否為預期。

finding 片段：`.on_new_window(move |url, features| {`

## base-2:tauri-10:2|tauri-10#5

**GT**（rule）New code uses unwrap() on fallible operations

> Added code introduces multiple `unwrap()` calls on fallible operations (`parse().unwrap()`, `set_title(...).unwrap()`, and `build().unwrap()`), which violates the rule prohibiting panics/unwraps in favor of explicit error handling via `Result`.

GT 片段：`let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"), ⏎ tauri::WebviewUrl::External("about:blank".parse().unwrap()),`

**finding**（`examples/api/src-tauri/src/lib.rs:84`，距錨點 5 行，候選管道 loc）on_new_window 移至桌面平台專屬區塊可能導致非桌面平台行為不一致

> 原本 on_new_window 在所有平台都會設定，現在僅在桌面平台（desktop）設定。若其他平台需要處理新視窗，可能導致功能缺失。請確認此變更是否為預期。

finding 片段：`.on_new_window(move |url, features| {`

## base-2:tauri-11:2|tauri-11#1

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行，候選管道 loc）鏡像 URL 可能遺失路徑

> `generate_github_mirror_url_from_base` 移除了 `cdn.set_path(github_url)` 呼叫，改為直接回傳 `cdn.to_string()`。這可能導致鏡像 URL 不再包含原始 GitHub URL 的路徑，使得下載請求指向錯誤的資源。需確認此變更是否為預期行為，或是否應保留路徑設定。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## base-2:tauri-11:3|tauri-11#3

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行，候選管道 loc）條件反轉可能改變行為

> `crate_version` 中的條件由 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。此修正可能正確（原本邏輯可能有誤），但需確認是否會影響依賴版本解析。建議補充測試或說明。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## base-2:tauri-12:1|tauri-12#0

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯相反

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（即一般情況），該 key 不會被加入，使得 macOS 無法正確關聯副檔名。應改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-2:tauri-12:1|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行，候選管道 loc）CFBundleTypeExtensions 條件判斷邏輯相反

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（即一般情況），該 key 不會被加入，使得 macOS 無法正確關聯副檔名。應改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-2:tauri-12:1|tauri-12#3

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯相反

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（即一般情況），該 key 不會被加入，使得 macOS 無法正確關聯副檔名。應改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-2:tauri-12:1|tauri-12#4

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯相反

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（即一般情況），該 key 不會被加入，使得 macOS 無法正確關聯副檔名。應改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-2:tauri-12:2|tauri-12#0

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行，候選管道 loc）使用 expect 可能導致 panic

> 原本 `name` 為 None 時會 fallback 到 `ext[0]`，現在改用 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空（例如僅使用 content types 的關聯），程式會 panic。建議保留原本的 fallback 邏輯或提供更安全的處理。

finding 片段：`.expect("File association must have a name")`

## base-2:tauri-12:2|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行，候選管道 ident）使用 expect 可能導致 panic

> 原本 `name` 為 None 時會 fallback 到 `ext[0]`，現在改用 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空（例如僅使用 content types 的關聯），程式會 panic。建議保留原本的 fallback 邏輯或提供更安全的處理。

finding 片段：`.expect("File association must have a name")`

## base-2:tauri-12:2|tauri-12#3

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行，候選管道 loc）使用 expect 可能導致 panic

> 原本 `name` 為 None 時會 fallback 到 `ext[0]`，現在改用 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空（例如僅使用 content types 的關聯），程式會 panic。建議保留原本的 fallback 邏輯或提供更安全的處理。

finding 片段：`.expect("File association must have a name")`

## base-2:tauri-12:2|tauri-12#4

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行，候選管道 loc）使用 expect 可能導致 panic

> 原本 `name` 為 None 時會 fallback 到 `ext[0]`，現在改用 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空（例如僅使用 content types 的關聯），程式會 panic。建議保留原本的 fallback 邏輯或提供更安全的處理。

finding 片段：`.expect("File association must have a name")`

## base-2:tauri-13:1|tauri-13#3

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行，候選管道 loc）notarize_inner 中 submit_output.status 的判斷邏輯可能反轉

> 在 `notarize_inner` 函式中，原本的條件 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。這會改變當 `status` 為 `None` 時的行為：原本在 `wait` 為 false 時會進入 if 區塊，現在則變成 `wait` 為 true 時才會進入。這可能導致在非等待模式下，即使沒有狀態也不會執行後續的 notarization 邏輯，或在等待模式下錯誤地執行。請確認此變更是否符合預期，並補充對應的測試。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## base-2:tauri-13:2|tauri-13#2

**GT**（func）Swapped source and destination in ditto archive command

> The arguments to the ditto command are reversed: zip_path appears before app_bundle_path, when ditto expects the source (app_bundle_path) before the destination (zip_path). This will cause ditto to fail when attempting to create the notarization archive, as it tries to compress a non-existent zip file into the app bundle directory. The command format should be 'ditto -c -k --keepParent --sequesterRsrc <source> <destination>', but the current order attempts '<destination> <source>', breaking the entire notarization workflow.

GT 片段：`let zip_args = vec![ ⏎ "-c", ⏎ "-k", ⏎ "--keepParent",`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行，候選管道 model_line）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序由原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。雖然 `ditto` 的語法通常允許來源和目標互換，但若路徑包含特殊字元或符號連結，可能導致非預期的行為。建議確認此變更的必要性，並在 macOS 上進行測試。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## base-2:tauri-13:2|tauri-13#7

**GT**（rule）Use of expect() for fallible PathBuf-to-str conversion

> The code uses `.to_str().expect(...)`, which will panic on non-UTF8 paths. The rule requires fallible operations to return/propagate `Result` instead of panicking via `expect`/`unwrap`.

GT 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行，候選管道 model_line）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序由原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。雖然 `ditto` 的語法通常允許來源和目標互換，但若路徑包含特殊字元或符號連結，可能導致非預期的行為。建議確認此變更的必要性，並在 macOS 上進行測試。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## base-2:tauri-2:1|tauri-2#0

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行，候選管道 ident）權限設定在寫入前執行，導致檔案權限錯誤

> 在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-2:tauri-2:1|tauri-2#2

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行，候選管道 loc）權限設定在寫入前執行，導致檔案權限錯誤

> 在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-2:tauri-2:1|tauri-2#4

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行，候選管道 ident）權限設定在寫入前執行，導致檔案權限錯誤

> 在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-2:tauri-2:2|tauri-2#1

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行，候選管道 loc）linuxdeploy 下載 URL 使用錯誤的架構變數

> 原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為 `arch`。若 `arch` 為 i686，則會下載不存在的 i686 版本，導致下載失敗。應保留 `linuxdeploy_arch`。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## base-2:tauri-2:2|tauri-2#3

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行，候選管道 loc）linuxdeploy 下載 URL 使用錯誤的架構變數

> 原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為 `arch`。若 `arch` 為 i686，則會下載不存在的 i686 版本，導致下載失敗。應保留 `linuxdeploy_arch`。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## base-2:tauri-2:4|tauri-2#1

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 0 行，候選管道 loc）gtk 外掛腳本存在時仍會覆寫

> 原本邏輯是當 `gtk` 檔案不存在時才下載，但修改後變成當檔案存在時才寫入內嵌腳本。這會導致已存在的檔案被覆寫，可能不是預期行為。應改為 `if !gtk.exists()`。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## base-2:tauri-2:4|tauri-2#3

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 4 行，候選管道 loc）gtk 外掛腳本存在時仍會覆寫

> 原本邏輯是當 `gtk` 檔案不存在時才下載，但修改後變成當檔案存在時才寫入內嵌腳本。這會導致已存在的檔案被覆寫，可能不是預期行為。應改為 `if !gtk.exists()`。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## base-2:tauri-3:1|tauri-3#1

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行，候選管道 loc）錯誤處理變更可能導致錯誤類型混淆

> 在 do_parse_toml 中，原本使用 ConfigError::FormatToml 來封裝 toml 解析錯誤，但現在改為 ConfigError::FormatJson，並將 toml 錯誤轉為 serde_json::Error。這可能導致錯誤訊息不準確，且呼叫端若依賴錯誤類型來區分格式，將無法正確處理。建議保留 ConfigError::FormatToml 或新增專用錯誤變體。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## base-2:tauri-3:2|tauri-3#0

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行，候選管道 ident）Display 實作中 Flatpak 的大小寫不一致

> 在 Display for BundleType 中，Flatpak 被輸出為 "Flatpak"（首字母大寫），而其他變體如 "nsis"、"app"、"dmg" 皆為小寫。這可能導致序列化或顯示時的不一致。建議改為 "flatpak" 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-2:tauri-3:2|tauri-3#2

**GT**（func）Case mismatch between BundleType serialization and deserialization for Flatpak

> The Display implementation for BundleType::Flatpak returns "Flatpak" with capital 'F', while the Deserialize implementation expects lowercase "flatpak". This creates a serialization round-trip bug where serializing a Flatpak bundle type and then deserializing it will fail. Any code that serializes bundle configurations to strings (for CLI output, config files, or API responses) and then attempts to parse them back will encounter deserialization errors. This inconsistency breaks the expected behavior that Display and Deserialize should be compatible with each other.

GT 片段：`impl Display for BundleType { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ write!( ⏎ f,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 0 行，候選管道 loc）Display 實作中 Flatpak 的大小寫不一致

> 在 Display for BundleType 中，Flatpak 被輸出為 "Flatpak"（首字母大寫），而其他變體如 "nsis"、"app"、"dmg" 皆為小寫。這可能導致序列化或顯示時的不一致。建議改為 "flatpak" 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-2:tauri-3:2|tauri-3#3

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行，候選管道 ident）Display 實作中 Flatpak 的大小寫不一致

> 在 Display for BundleType 中，Flatpak 被輸出為 "Flatpak"（首字母大寫），而其他變體如 "nsis"、"app"、"dmg" 皆為小寫。這可能導致序列化或顯示時的不一致。建議改為 "flatpak" 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-2:tauri-4:1|tauri-4#2

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行，候選管道 loc）JSON 設定檔不再進行 schema 驗證

> 原本的條件 `config_path.extension() == Some(OsStr::new("json")) || config_path.extension() == Some(OsStr::new("json5"))` 被改為 `config_path.extension() == Some(OsStr::new("json")) && config_path.extension() == Some(OsStr::new("json5"))`。這使得條件永遠為 false（因為副檔名不可能同時是 json 和 json5），導致所有 JSON 設定檔都跳過 schema 驗證。這會讓無效的設定檔被接受，可能造成後續執行錯誤或安全問題。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## base-2:tauri-4:2|tauri-4#3

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行，候選管道 loc）merge_with 不再合併設定，可能破壞預期行為

> 原本的程式碼會將合併後的結果反序列化回 `config_metadata.inner`，但現在改為將 `merge_config` 存入 `extensions`。這可能導致 `inner` 未更新，使後續使用 `inner` 的程式碼讀到舊值，或依賴 `inner` 的邏輯失效。需要確認此變更是否為預期，並檢查所有使用 `config_metadata.inner` 的地方。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## base-2:tauri-4:3|tauri-4#0

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 24 行，候選管道 ident）original_identifier 提取錯誤的欄位

> 原本從 `config` 物件中取得 `identifier`，現在改為取得 `bundle`。這可能導致 `original_identifier` 的值不正確，影響後續依賴此值的邏輯（例如重新載入時的檢查）。需要確認此變更是否為預期。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-2:tauri-4:3|tauri-4#1

**GT**（func）Incorrect field path for extracting original bundle identifier

> The code attempts to extract the original identifier from the 'bundle' field instead of the root-level 'identifier' field. Since 'bundle' is an object (not a string), the `.as_str()` call will always fail, causing `original_identifier` to always be None. This breaks the ability to track and report which config file overwrites the bundle identifier, as the `find_bundle_identifier_overwriter()` method relies on comparing against the original identifier value.

GT 片段：`let original_identifier = config ⏎ .as_object() ⏎ .and_then(|config| config.get("bundle")) ⏎ .and_then(|id| id.as_str())`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 0 行，候選管道 loc）original_identifier 提取錯誤的欄位

> 原本從 `config` 物件中取得 `identifier`，現在改為取得 `bundle`。這可能導致 `original_identifier` 的值不正確，影響後續依賴此值的邏輯（例如重新載入時的檢查）。需要確認此變更是否為預期。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-2:tauri-4:3|tauri-4#4

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 23 行，候選管道 ident）original_identifier 提取錯誤的欄位

> 原本從 `config` 物件中取得 `identifier`，現在改為取得 `bundle`。這可能導致 `original_identifier` 的值不正確，影響後續依賴此值的邏輯（例如重新載入時的檢查）。需要確認此變更是否為預期。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-2:tauri-4:4|tauri-4#0

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:151`，距錨點 2 行，候選管道 loc）使用 OnceLock 快取 validator 可能導致記憶體洩漏

> `config_schema_validator` 使用 `OnceLock` 快取 `jsonschema::Validator`，但該 validator 可能包含大量資料且不會被釋放。若此函式在長時間執行的程序中被多次呼叫，可能造成不必要的記憶體佔用。不過，由於 validator 通常只建立一次，影響可能有限。

finding 片段：`static CONFIG_SCHEMA_VALIDATOR: OnceLock<jsonschema::Validator> = OnceLock::new();`

## base-2:tauri-4:4|tauri-4#4

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:151`，距錨點 1 行，候選管道 loc）使用 OnceLock 快取 validator 可能導致記憶體洩漏

> `config_schema_validator` 使用 `OnceLock` 快取 `jsonschema::Validator`，但該 validator 可能包含大量資料且不會被釋放。若此函式在長時間執行的程序中被多次呼叫，可能造成不必要的記憶體佔用。不過，由於 validator 通常只建立一次，影響可能有限。

finding 片段：`static CONFIG_SCHEMA_VALIDATOR: OnceLock<jsonschema::Validator> = OnceLock::new();`

## base-2:tauri-5:1|tauri-5#4

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行，候選管道 loc）Dirs 結構體持有 &'static Path 可能造成懸垂指標

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但實際值是從 `OnceLock<PathBuf>` 中取得的參考。雖然目前 `OnceLock` 只會被初始化一次，但若未來程式碼在 `resolve_dirs()` 之後再次呼叫 `TAURI_DIR.set(...)` 或 `FRONTEND_DIR.set(...)`（例如在測試或重設邏輯中），舊的 `Dirs` 實例將持有指向已釋放記憶體的懸垂指標。建議改為持有 `PathBuf` 或使用 `Arc<Path>` 來確保生命週期安全。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## base-2:tauri-5:3|tauri-5#2

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:247`，距錨點 4 行，候選管道 loc）reload_config 直接覆寫整個 ConfigMetadata 可能遺失未儲存的變更

> `reload_config` 函式直接將 `*config = load_config(...)` 的結果指派給傳入的 `&mut ConfigMetadata`。若在重新載入前有其他程式碼修改了 `config` 的某些欄位（例如透過 `merge_config_with`），這些變更會在重新載入時被覆蓋。建議先合併現有變更再重新載入，或明確區分唯讀與可變部分。

finding 片段：`pub fn reload_config( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

## base-2:tauri-5:3|tauri-5#5

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:247`，距錨點 0 行，候選管道 loc）reload_config 直接覆寫整個 ConfigMetadata 可能遺失未儲存的變更

> `reload_config` 函式直接將 `*config = load_config(...)` 的結果指派給傳入的 `&mut ConfigMetadata`。若在重新載入前有其他程式碼修改了 `config` 的某些欄位（例如透過 `merge_config_with`），這些變更會在重新載入時被覆蓋。建議先合併現有變更再重新載入，或明確區分唯讀與可變部分。

finding 片段：`pub fn reload_config( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

## base-2:tauri-6:3|tauri-6#1

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:46`，距錨點 3 行，候選管道 loc）強制轉型為 AppCompatActivity 可能導致 ClassCastException

> 在建構子中 `(activity as AppCompatActivity)` 直接轉型，如果傳入的 Activity 不是 AppCompatActivity（例如使用非 AppCompat 主題），會拋出 ClassCastException。雖然 Tauri 通常使用 AppCompatActivity，但建議使用更安全的方式取得 OnBackPressedDispatcher，例如使用 `activity.onBackPressedDispatcher`（需要 androidx.activity 擴展）。

finding 片段：`(activity as AppCompatActivity).onBackPressedDispatcher.addCallback(activity, callback)`

## base-2:tauri-6:4|tauri-6#0

**GT**（rule）Needless borrow and dereference pattern

> The code creates an unnecessary reference and then immediately dereferences it, which clippy detects as redundant code that should be simplified

GT 片段：`let handle = _api.register_android_plugin("app.tauri", "AppPlugin")?; ⏎ let handle_ref = &handle; ⏎ _app.manage(AppPlugin(*handle_ref));`

**finding**（`crates/tauri/src/app/plugin.rs:148`，距錨點 8 行，候選管道 ident）AppPlugin 結構體未使用可能導致 dead_code 警告

> 新增的 `AppPlugin` 結構體僅在 Android 上使用，但未看到實際使用的地方（可能在其他檔案中）。如果未使用，Rust 編譯器會發出 dead_code 警告。建議確認是否有使用，或加上 `#[allow(dead_code)]`。

finding 片段：`pub(crate) struct AppPlugin<R: Runtime>(pub crate::plugin::PluginHandle<R>);`

## base-2:tauri-7:1|tauri-7#1

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:52`，距錨點 0 行，候選管道 loc）generate_github_alternative_url 不再使用替代 URL

> 原本函式會產生替代的 GitHub 鏡像 URL（例如處理 GitHub 下載失敗時），但現在直接忽略 `_alt_url` 並回傳原始 `url`。這可能導致原本依賴鏡像 URL 的錯誤處理或效能優化失效。請確認此變更是否為預期行為，並檢查是否有其他程式碼依賴此函式回傳替代 URL。

finding 片段：`.map(|_alt_url| { ⏎ ( ⏎ ureq::Agent::config_builder() ⏎ .user_agent(BUNDLER_USER_AGENT)`

## base-2:tauri-7:2|tauri-7#0

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:120`，距錨點 0 行，候選管道 loc）移除 Sha256 的 Windows 條件編譯限制

> 原本 `HashAlgorithm::Sha256` 僅在 Windows 上可用，現在移除 `#[cfg(target_os = "windows")]` 後，所有平台皆可使用。這可能是有意為之（例如其他平台也需要 SHA256），但需確認非 Windows 平台是否有對應的依賴與測試。

finding 片段：`Sha256,`

## base-2:tauri-8:1|tauri-8#1

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行，候選管道 loc）MouseButtonState 的 From 轉換邏輯被反轉

> 在 `impl From<tray_icon::MouseButtonState> for MouseButtonState` 中，原本 `Up` 對應 `Up`、`Down` 對應 `Down`，但此變更將其反轉為 `Up` 對應 `Down`、`Down` 對應 `Up`。這會導致所有依賴此轉換的程式碼（例如處理 tray icon 點擊事件）接收到相反的按鈕狀態，造成行為錯誤。請恢復原本的對應關係。

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## base-2:tauri-8:2|tauri-8#1

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:22`，距錨點 9 行，候選管道 ident）MouseButtonState 的預設值可能語意錯誤

> `MouseButtonState` 的 `#[default]` 被標記在 `Up` 變體上，但註解寫著 `Up` 代表「滑鼠按鍵按下」，`Down` 代表「滑鼠按鍵釋放」。通常預設值應為「釋放」狀態（即 `Down`），但此處卻設為 `Up`（按下）。請確認預設值是否符合預期，若否請將 `#[default]` 移至 `Down`。

finding 片段：`#[derive(Default, Clone, Copy, PartialEq, Eq, Debug, Serialize)] ⏎ pub enum MouseButtonState { ⏎ /// Mouse button pressed. ⏎ #[default]`

## base-2:tauri-8:3|tauri-8#0

**GT**（rule）new_click method missing must_use attribute

> The new_click method returns a TrayIconEvent that represents an important event which should not be ignored. Factory methods that create event objects should be marked with #[must_use] to prevent accidentally creating an event without handling it, which could lead to silent logic errors.

GT 片段：`/// Creates a new Click event with default values. ⏎ /// Useful for testing or creating mock events. ⏎ pub fn new_click(id: TrayIconId) -> Self { ⏎ TrayIconEvent::Click {`

**finding**（`crates/tauri/src/tray/mod.rs:140`，距錨點 0 行，候選管道 loc）new_click 方法使用硬編碼的零值，可能不適用於所有情境

> 新增的 `new_click` 方法將位置、矩形和尺寸都設為 0.0，這在測試或 mock 情境可能足夠，但若被用於實際事件處理，可能導致下游邏輯誤判。建議在文件或命名上明確標示此方法僅供測試使用，或考慮提供更靈活的建構方式。

finding 片段：`pub fn new_click(id: TrayIconId) -> Self { ⏎ TrayIconEvent::Click { ⏎ id, ⏎ position: PhysicalPosition { x: 0.0, y: 0.0 },`
