# 盲標單：finding 跟 GT 是不是同一個問題

判準（Martian）：**一個 code change 能同時修掉兩者**才算 `same`；同處、相關但講的是別的問題算 `partial`；否則 `no`。
本單刻意不含 confidence、severity。標在 `labels.csv`：`pair,label,note`。

## base-1:Ghost-1:1|Ghost-1#1

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行，候選管道 loc）emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題

> 原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

finding 片段：`emailAddressService.init(),`

## base-1:Ghost-1:1|Ghost-1#2

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 15 行，候選管道 ident）emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題

> 原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

finding 片段：`emailAddressService.init(),`

## base-1:Ghost-1:1|Ghost-1#3

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行，候選管道 loc）emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題

> 原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

finding 片段：`emailAddressService.init(),`

## base-1:Ghost-1:2|Ghost-1#1

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行，候選管道 loc）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## base-1:Ghost-1:2|Ghost-1#2

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行，候選管道 loc）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## base-1:Ghost-1:2|Ghost-1#3

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行，候選管道 loc）scheduling.init() 移除 apiUrl 參數可能導致排程功能異常

> 原本 `scheduling.init({ apiUrl: urlUtils.urlFor('api', {type: 'admin'}, true) })` 傳入 API URL，現在改為無參數呼叫。若 scheduling 服務需要此 URL 來註冊 webhook 或進行 API 呼叫，移除後可能導致排程功能失效。建議確認 scheduling.init() 的實作是否已改用其他方式取得 URL，或此參數已不再需要。

finding 片段：`scheduling.init(),`

## base-1:Ghost-10:1|Ghost-10#0

**GT**（rule）Strict mode disabled in TypeScript config

> The rule requires TypeScript configuration files to have 'strict' set to true in compilerOptions, but it was set to false

GT 片段：`/* Linting */ ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`apps/activitypub/tsconfig.json:18`，距錨點 0 行，候選管道 loc）關閉 TypeScript strict 模式

> 將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更應有充分理由，否則應恢復為 `true` 並修正相關型別錯誤。

finding 片段：`"strict": false,`

## base-1:Ghost-10:2|Ghost-10#2

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:103`，距錨點 0 行，候選管道 loc）輪詢邏輯可能造成競態或重複請求

> 在 `useEffect` 中設置 `setInterval` 並在每次觸發時呼叫 `confirmHandle`，但 `confirmHandle` 內部使用 `confirmBlueskyHandleMutation.mutateAsync()`，若前一次請求尚未完成，可能導致重疊請求。此外，`retryCountRef` 在每次 effect 重新執行時重置為 0，若依賴項頻繁變化，可能導致輪詢次數超過預期。建議使用 `setTimeout` 遞迴或確保請求完成後再安排下一次。

finding 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ `

## base-1:Ghost-10:3|Ghost-10#2

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:107`，距錨點 0 行，候選管道 loc）輪詢失敗時自動停用 Bluesky 可能非預期

> 當輪詢達到最大次數時，程式碼會自動呼叫 `disableBlueskyMutation.mutateAsync()` 停用 Bluesky。這可能導致使用者在未明確同意的情況下被停用，且若停用失敗，錯誤未被處理。建議改為僅顯示錯誤訊息，讓使用者手動決定是否停用。

finding 片段：`toast.error('Something went wrong, please try again.'); ⏎  ⏎ await disableBlueskyMutation.mutateAsync(); ⏎ setLoading(false);`

## base-1:Ghost-10:4|Ghost-10#3

**GT**（func）Missing query invalidation after Bluesky handle confirmation causes stale following list

> The confirmBlueskyHandle mutation successfully updates the account cache but fails to invalidate the accountFollows query. When Bluesky is enabled via Bridgy Fed, the account automatically follows the brid.gy account. Both enableBluesky and disableBluesky mutations properly invalidate QUERY_KEYS.accountFollows('index', 'following') to refresh this list, but confirmBlueskyHandle does not. This means after the handle is confirmed, the UI won't show the brid.gy follow relationship until the user manually refreshes the page or navigates away and back. This is inconsistent with the established pattern in the codebase and creates a confusing user experience where the integration appears incomplete.

GT 片段：`onSuccess(blueskyHandle: string) { ⏎ // If the bluesky handle is empty then the handle was not confirmed ⏎ // so we don't need to update the cache ⏎ if (blueskyHandle === '') {`

**finding**（`apps/activitypub/src/hooks/use-activity-pub-queries.ts:2833`，距錨點 0 行，候選管道 loc）缺少 accountFollows 查詢的失效處理

> 在 `useConfirmBlueskyHandleMutationForUser` 的 `onSuccess` 中，註解提到缺少 `accountFollows` 查詢的失效處理。這可能導致相關資料不同步。建議補上對應的 `queryClient.invalidateQueries`。

finding 片段：`// Note: Missing invalidation of accountFollows query that should happen here`

## base-1:Ghost-11:3|Ghost-11#0

**GT**（rule）var used instead of const

> The rule requires that all variable declarations use let or const instead of var, but var was used to declare the newValues variable

GT 片段：`onSelect={() => { ⏎ if (isMultiSelect) { ⏎ var newValues = [...effectiveValues, option.value] as T[]; ⏎ if (field.maxSelections && newValues.length > field.maxSelections) {`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 2 行，候選管道 model_line）autoCloseOnSelect 在 multiselect 中可能造成非預期關閉

> 在 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { onClose?.(); }`，但此處呼叫的 `onClose` 可能只關閉 popover 而不會重置選取狀態，且與下方註解「For multiselect, don't close the popover to allow multiple selections」矛盾。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## base-1:Ghost-11:3|Ghost-11#4

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1134`，距錨點 0 行，候選管道 model_line）autoCloseOnSelect 在 multiselect 中可能造成非預期關閉

> 在 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { onClose?.(); }`，但此處呼叫的 `onClose` 可能只關閉 popover 而不會重置選取狀態，且與下方註解「For multiselect, don't close the popover to allow multiple selections」矛盾。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

## base-1:Ghost-11:4|Ghost-11#2

**GT**（func）Missing handleClose call in single-select mode prevents search input cleanup

> In the unselected options section for single-select mode, the code calls setOpen(false) but fails to call handleClose(), unlike the multiselect path which properly calls handleClose() when autoCloseOnSelect is enabled. This means when a user selects a single option, the popover closes but the search input state is never cleared, causing the next time the popover opens to show stale search results and filtered options from the previous interaction. The handleClose() function is responsible for clearing the search input and triggering the onClose callback, both of which are now skipped in single-select scenarios.

GT 片段：`} else { ⏎ onChange([option.value] as T[]); ⏎ setOpen(false); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1271`，距錨點 4 行，候選管道 model_line）autoCloseOnSelect 在 multiselect 中可能造成非預期關閉

> 在另一個 multiselect 的 onSelect 處理中，新增了 `if (field.autoCloseOnSelect) { handleClose(); }`，但此處呼叫的 `handleClose` 會同時重置搜尋輸入並呼叫 `onClose`，可能導致 popover 關閉且搜尋被清空。若 `autoCloseOnSelect` 為 true，使用者選取一個選項後 popover 會立即關閉，無法連續選取多個值，可能不符合 multiselect 的預期行為。建議確認此設計是否為預期，或改為在達到 maxSelections 時才關閉。

finding 片段：`if (field.autoCloseOnSelect) { ⏎ handleClose(); ⏎ }`

## base-1:Ghost-12:1|Ghost-12#2

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 0 行，候選管道 loc）JWT 驗證改為 decode 導致簽章未驗證

> `_isJWTExpired` 從 `jwt.verify` 改為 `jwt.decode`，這會跳過簽章驗證。攻擊者可以偽造一個帶有未來 `exp` 的 token，通過過期檢查，進而使用無效的 token 存取 Tinybird API。建議改回 `jwt.verify`，或在 `_isJWTExpired` 中明確驗證簽章。

finding 片段：`const decoded = jwt.decode(token);`

## base-1:Ghost-12:1|Ghost-12#3

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 17 行，候選管道 ident）JWT 驗證改為 decode 導致簽章未驗證

> `_isJWTExpired` 從 `jwt.verify` 改為 `jwt.decode`，這會跳過簽章驗證。攻擊者可以偽造一個帶有未來 `exp` 的 token，通過過期檢查，進而使用無效的 token 存取 Tinybird API。建議改回 `jwt.verify`，或在 `_isJWTExpired` 中明確驗證簽章。

finding 片段：`const decoded = jwt.decode(token);`

## base-1:Ghost-12:2|Ghost-12#1

**GT**（func）Token caching stores entire object instead of token string

> In the getToken method, when caching the JWT token, the code now stores the entire tokenData object (containing both 'token' and 'exp' properties) instead of just extracting the token string. This causes the returned token structure to be malformed as {token: {token: string, exp: number}, exp: number} instead of the expected {token: string, exp: number}. This will break any consumers of the Tinybird API (like the /api/tinybird/token endpoint and stats/tinybird.js) that expect a string token value, causing authentication failures when making requests to Tinybird pipes.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行，候選管道 loc）_serverToken 型別變更可能導致後續使用錯誤

> `_serverToken` 原本存 token 字串，現在改存整個 token 物件（包含 `token` 和 `exp`）。若其他程式碼仍預期 `_serverToken` 是字串，可能導致型別錯誤或功能失效。請確認所有使用 `_serverToken` 的地方都已更新。

finding 片段：`this._serverToken = tokenData;`

## base-1:Ghost-12:2|Ghost-12#4

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行，候選管道 loc）_serverToken 型別變更可能導致後續使用錯誤

> `_serverToken` 原本存 token 字串，現在改存整個 token 物件（包含 `token` 和 `exp`）。若其他程式碼仍預期 `_serverToken` 是字串，可能導致型別錯誤或功能失效。請確認所有使用 `_serverToken` 的地方都已更新。

finding 片段：`this._serverToken = tokenData;`

## base-1:Ghost-12:3|Ghost-12#2

**GT**（func）JWT signature validation bypassed in token expiration check

> The _isJWTExpired method now uses jwt.decode() instead of jwt.verify() to check token expiration. While jwt.verify() validates the token's signature and ensures it hasn't been tampered with, jwt.decode() only decodes the token without any cryptographic validation. This creates a security vulnerability where expired, tampered, or forged tokens could be accepted as valid. An attacker could potentially modify token claims (like extending expiration or changing site_uuid in scopes) and the system would accept the malicious token, bypassing authentication controls for Tinybird API access.

GT 片段：`_isJWTExpired(token, bufferSeconds = 300) { ⏎ try { ⏎ const decoded = jwt.decode(token); ⏎ if (typeof decoded !== 'object' || !decoded.exp) {`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 15 行，候選管道 ident）JWT 簽署移除 noTimestamp 可能影響 token 格式

> `jwt.sign` 原本有 `{noTimestamp: true}`，現在移除後 token 會包含 `iat` 欄位。若 Tinybird 端對 token 格式有特定要求，可能導致驗證失敗。建議確認 Tinybird 是否接受帶有 `iat` 的 token。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## base-1:Ghost-12:3|Ghost-12#3

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 0 行，候選管道 loc）JWT 簽署移除 noTimestamp 可能影響 token 格式

> `jwt.sign` 原本有 `{noTimestamp: true}`，現在移除後 token 會包含 `iat` 欄位。若 Tinybird 端對 token 格式有特定要求，可能導致驗證失敗。建議確認 Tinybird 是否接受帶有 `iat` 的 token。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## base-1:Ghost-13:1|Ghost-13#1

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行，候選管道 loc）版本前綴順序與後端不一致

> 前端 `getStatEndpointUrl` 將 `config.version` 放在 endpointName 之前（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是放在之後（`${pipeName}_${version}`）。例如 version='v2'、endpointName='api_kpis' 時，前端會呼叫 `v2_api_kpis`，後端會呼叫 `api_kpis_v2`，導致 404。請統一為後端的 `api_kpis_v2` 格式。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## base-1:Ghost-13:3|Ghost-13#2

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:102`，距錨點 0 行，候選管道 loc）移除 source 參數傳遞可能影響現有功能

> 原本有將 `options.source` 加入 tinybirdOptions 的邏輯（允許空字串代表 Direct traffic），但此 PR 移除了該區塊。若前端仍會傳送 `source` 參數，則後端將不再將其傳遞給 Tinybird，可能導致 source 過濾失效。請確認是否有其他地方處理 source，或是有意移除。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## base-1:Ghost-2:1|Ghost-2#2

**GT**（func）Editor editability incorrectly depends on member expertise instead of name

> The Form component determines whether the editor should be editable by checking `member?.expertise` instead of `memberName` (which is derived from `member?.name`). According to the comment and the original logic, the editor should be disabled only when the member doesn't have a name or when submitting. Expertise is optional metadata, but name is required for posting. This bug prevents users without expertise from typing in the comment editor, even though they have a valid name and should be allowed to comment.

GT 片段：`useEffect(() => { ⏎ if (!editor) { ⏎ return; ⏎ }`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:264`，距錨點 0 行，候選管道 loc）member 可能為 null 時存取 member.expertise 可能拋出錯誤

> 在 `editor.setEditable(!!member?.expertise && progress !== 'sending')` 中，若 `member` 為 null，`member?.expertise` 會回傳 undefined，`!!undefined` 為 false，因此不會拋出錯誤。但此處邏輯與原本使用 `memberName` 不同，可能導致編輯器在成員沒有 expertise 時被設為不可編輯，即使成員有名字。建議確認此行為是否符合預期，或改用 `member?.name` 或同時檢查兩者。

finding 片段：`editor.setEditable(!!member?.expertise && progress !== 'sending');`

## base-1:Ghost-2:2|Ghost-2#1

**GT**（func）Missing optional chaining causes runtime error when openForm is undefined

> The code accesses `openForm.in_reply_to_snippet` without optional chaining, but openForm can be undefined when rendering certain forms (like the main comment form). The original code correctly used `openForm?.in_reply_to_snippet` with optional chaining. This will cause a "Cannot read property 'in_reply_to_snippet' of undefined" runtime error when the FormWrapper is rendered without an openForm prop, crashing the component.

GT 片段：`let openStyles = ''; ⏎ if (isOpen) { ⏎ const isReplyToReply = !!openForm.in_reply_to_snippet; ⏎ openStyles = isReplyToReply ? 'pl-[1px] pt-[68px] sm:pl-[44px] sm:pt-[56px]' : 'pl-[1px] pt-[48px] sm:pl-[44px] sm:pt-[40px]';`

**finding**（`apps/comments-ui/src/components/content/forms/form.tsx:313`，距錨點 0 行，候選管道 loc）openForm 可能為 null 時直接存取 in_reply_to_snippet 可能拋出錯誤

> 在 `const isReplyToReply = !!openForm.in_reply_to_snippet;` 中，若 `openForm` 為 null 或 undefined，則會拋出 TypeError。原本程式碼使用 `openForm?.in_reply_to_snippet` 可選串連，此變更移除了安全保護。建議保留可選串連或確保 openForm 永遠不為 null。

finding 片段：`const isReplyToReply = !!openForm.in_reply_to_snippet;`

## base-1:Ghost-2:3|Ghost-2#3

**GT**（func）Reply threading broken for nested comments due to incorrect in_reply_to_id

> The submit function uses `parent.id` as `in_reply_to_id` instead of `openForm.in_reply_to_id`. For nested replies (replying to a reply), these values differ: `openForm.in_reply_to_id` points to the specific comment being replied to, while `parent.id` points to the top-level parent comment. Using `parent.id` breaks the reply chain, causing nested replies to be incorrectly threaded to the wrong comment. This destroys the conversation hierarchy and makes it impossible to track which comment a user is actually replying to in multi-level discussions.

GT 片段：`const submit = useCallback(async ({html}) => { ⏎ // Send comment to server ⏎ await dispatchAction('addReply', { ⏎ parent: parent,`

**finding**（`apps/comments-ui/src/components/content/forms/reply-form.tsx:30`，距錨點 0 行，候選管道 loc）in_reply_to_id 改為 parent.id 可能影響回覆邏輯

> 將 `in_reply_to_id` 從 `openForm.in_reply_to_id` 改為 `parent.id`，可能改變回覆的目標。若 `openForm.in_reply_to_id` 原本可能指向不同的父評論（例如回覆回覆），此變更可能導致回覆錯誤。建議確認 parent 是否永遠為正確的回覆目標。

finding 片段：`in_reply_to_id: parent.id,`

## base-1:Ghost-3:1|Ghost-3#1

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:102`，距錨點 0 行，候選管道 loc）日期過濾條件從「<」改為「<=」可能納入今天的郵件

> 原本使用 `created_at:<今天日期` 排除今天的郵件，但改為 `created_at:<=今天日期` 後，會包含今天建立的郵件。這可能導致 #getHighestCount 回傳今天的郵件數量，進而讓暖機上限膨脹，甚至造成無限成長。建議維持原本的 `<` 運算子，或明確排除今天的郵件。

finding 片段：`filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,`

## base-1:Ghost-3:3|Ghost-3#2

**GT**（func）High-volume threshold boundary applies wrong scaling factor at 400k

> The condition uses `>=` instead of `>` when checking if lastCount qualifies for high-volume capping at exactly 400,000 emails. According to the documented scaling table, 400k should use the 2× multiplier from the thresholds array, but with this bug it immediately applies the high-volume cap of 1.2× or +75k absolute increase. For a site hitting exactly 400k messages, this means getting a limit of 480k (1.2×) or 475k (+75k) instead of the expected 800k (2×). This creates a significant bottleneck at a critical growth milestone and breaks the documented warmup progression.

GT 片段：`// For high volume senders (400k+), cap the increase at 20% or 75k absolute ⏎ if (lastCount >= WARMUP_SCALING_TABLE.highVolume.threshold) { ⏎ const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 0 行，候選管道 loc）高流量分支的計算可能導致上限下降

> 在 `lastCount >= 400000` 時，回傳 `Math.min(scaledIncrease, absoluteIncrease)`。其中 `scaledIncrease = Math.ceil(lastCount * 1.2)`，`absoluteIncrease = lastCount + 75000`。當 `lastCount` 大於 375000 時，`absoluteIncrease` 會小於 `scaledIncrease`，因此回傳 `lastCount + 75000`。這可能導致暖機上限的成長幅度低於預期，但仍在合理範圍內。建議確認此行為是否符合產品需求。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## base-1:Ghost-3:3|Ghost-3#3

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 5 行，候選管道 loc）高流量分支的計算可能導致上限下降

> 在 `lastCount >= 400000` 時，回傳 `Math.min(scaledIncrease, absoluteIncrease)`。其中 `scaledIncrease = Math.ceil(lastCount * 1.2)`，`absoluteIncrease = lastCount + 75000`。當 `lastCount` 大於 375000 時，`absoluteIncrease` 會小於 `scaledIncrease`，因此回傳 `lastCount + 75000`。這可能導致暖機上限的成長幅度低於預期，但仍在合理範圍內。建議確認此行為是否符合產品需求。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## base-1:Ghost-4:1|Ghost-4#0

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 18 行，候選管道 ident）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行適當消毒，攻擊者可注入惡意腳本，導致儲存型 XSS 攻擊。請確認 `item.html` 的來源已受信任且經過消毒（例如使用 DOMPurify），或改用安全的渲染方式。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## base-1:Ghost-4:1|Ghost-4#5

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 20 行，候選管道 ident）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接渲染 `item.html`。若評論內容未在伺服器端或客戶端進行適當消毒，攻擊者可注入惡意腳本，導致儲存型 XSS 攻擊。請確認 `item.html` 的來源已受信任且經過消毒（例如使用 DOMPurify），或改用安全的渲染方式。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## base-1:Ghost-4:2|Ghost-4#0

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行，候選管道 loc）useEffect 依賴陣列缺少 item.html，可能導致判斷不準確

> `useEffect` 僅在掛載時執行一次，但 `item.html` 可能因資料更新而改變。若內容變更，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示與否不正確。建議將 `item.html` 加入依賴陣列，或在內容變更時重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## base-1:Ghost-4:2|Ghost-4#1

**GT**（func）Missing dependency in useEffect causes stale clamp detection

> The CommentContent component's useEffect hook has an empty dependency array, but it uses item.html to determine if content should be clamped. When a comment's HTML content changes (e.g., after an edit or when new data is loaded), the clamp detection won't re-run. This means the 'Show more' button may appear when it shouldn't or disappear when it should still be visible, creating a poor user experience. The dependency array should include item.html to ensure the clamp detection re-runs whenever the content changes.

GT 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行，候選管道 loc）useEffect 依賴陣列缺少 item.html，可能導致判斷不準確

> `useEffect` 僅在掛載時執行一次，但 `item.html` 可能因資料更新而改變。若內容變更，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示與否不正確。建議將 `item.html` 加入依賴陣列，或在內容變更時重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## base-1:Ghost-4:2|Ghost-4#5

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 2 行，候選管道 loc）useEffect 依賴陣列缺少 item.html，可能導致判斷不準確

> `useEffect` 僅在掛載時執行一次，但 `item.html` 可能因資料更新而改變。若內容變更，`isClamped` 狀態不會重新計算，導致「Show more」按鈕顯示與否不正確。建議將 `item.html` 加入依賴陣列，或在內容變更時重新檢查。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## base-1:Ghost-5:1|Ghost-5#2

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行，候選管道 loc）移除 setLoading(false) 可能導致 minimal 模式永遠顯示 loading 狀態

> 在 minimal 模式下，送出成功後原本會呼叫 setLoading(false) 來停止 loading 動畫，但此 PR 移除了該行。若 loading 狀態沒有在其他地方被重設，使用者會看到無限的 loading 指示。請確認是否有其他機制（例如元件 unmount 或 effect）會重設 loading，否則應保留此行。

finding 片段：`setSuccess(true);`

## base-1:Ghost-5:2|Ghost-5#0

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行，候選管道 ident）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## base-1:Ghost-5:2|Ghost-5#1

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行，候選管道 loc）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## base-1:Ghost-5:3|Ghost-5#3

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行，候選管道 loc）email.trim() 可能改變原本的驗證行為

> 在提交時對 email 進行 trim 是合理的，但需確認驗證邏輯（isValidEmail）是否也應該使用 trim 後的值，否則可能出現前後不一致。例如使用者輸入前後有空白的 email，驗證可能通過但提交的是 trim 後的值，或反之。

finding 片段：`onSubmit({email: email.trim()});`

## base-1:Ghost-6:1|Ghost-6#1

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15`，距錨點 0 行，候選管道 loc）排程條件反轉導致重複排程

> 原本條件 `!hasScheduled.processOutbox` 在未排程時才排程，現在改為 `hasScheduled.processOutbox`，變成已排程時才排程。這會導致：
1. 首次呼叫時 `hasScheduled.processOutbox` 為 false，不會排程。
2. 若之後某次呼叫時 `hasScheduled.processOutbox` 被設為 true（例如手動設定或未來程式碼變更），則會重複排程。
建議改回 `!hasScheduled.processOutbox`。

finding 片段：`if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`

## base-1:Ghost-6:2|Ghost-6#0

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 1 行，候選管道 loc）config 值未驗證，可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，但未驗證其型別或內容。若 config 值為空字串、0、false 等 falsy 值，則條件為 false，不會建立 outbox；若為任意 truthy 值（例如 'false' 字串），則會建立 outbox。建議明確驗證該值是否為有效的 email 或布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## base-1:Ghost-6:2|Ghost-6#2

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 0 行，候選管道 loc）config 值未驗證，可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，但未驗證其型別或內容。若 config 值為空字串、0、false 等 falsy 值，則條件為 false，不會建立 outbox；若為任意 truthy 值（例如 'false' 字串），則會建立 outbox。建議明確驗證該值是否為有效的 email 或布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## base-1:Ghost-6:3|Ghost-6#1

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11`，距錨點 0 行，候選管道 loc）config 值未驗證，可能導致排程邏輯錯誤

> `config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，若 config 值為空字串或未定義，則不會排程；若為任意 truthy 值（例如 'false' 字串），則會排程。建議明確驗證該值是否為有效的 email 或布林值。

finding 片段：`if (!config.get('memberWelcomeEmailTestInbox')) {`

## base-1:Ghost-7:1|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 0 行，候選管道 loc）重新命名檔案時混入非預期的格式變更

> 此檔案除了更新 require 路徑外，還移除了所有行尾分號，並將部分 require 陳述式的引號從單引號改為雙引號。這與專案中其他檔案的風格不一致，且可能違反 ESLint 規則。建議只保留必要的路徑變更，避免混入格式調整。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## base-1:Ghost-7:1|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行，候選管道 ident）重新命名檔案時混入非預期的格式變更

> 此檔案除了更新 require 路徑外，還移除了所有行尾分號，並將部分 require 陳述式的引號從單引號改為雙引號。這與專案中其他檔案的風格不一致，且可能違反 ESLint 規則。建議只保留必要的路徑變更，避免混入格式調整。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## base-1:Ghost-7:2|Ghost-7#0

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 0 行，候選管道 loc）require 路徑大小寫變更可能導致部署問題

> 檔案從 `MembersAPI.js` 重新命名為 `members-api.js`，但此處的 require 路徑也改為小寫。在大小寫敏感的檔案系統（如 Linux）上，如果部署時未正確處理檔案名稱大小寫，可能導致模組找不到。建議確認 CI/CD 流程能正確處理大小寫變更。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## base-1:Ghost-7:2|Ghost-7#1

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 12 行，候選管道 ident）require 路徑大小寫變更可能導致部署問題

> 檔案從 `MembersAPI.js` 重新命名為 `members-api.js`，但此處的 require 路徑也改為小寫。在大小寫敏感的檔案系統（如 Linux）上，如果部署時未正確處理檔案名稱大小寫，可能導致模組找不到。建議確認 CI/CD 流程能正確處理大小寫變更。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## base-1:Ghost-8:1|Ghost-8#2

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行，候選管道 loc）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## base-1:Ghost-8:1|Ghost-8#6

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行，候選管道 loc）翻譯中遺漏變數 {newsletterName}

> 翻譯字串 `"{memberEmail} will no longer receive {newsletterName} newsletter."` 的譯文從 `"{memberEmail}将不会再收到{newsletterName}的新闻信。"` 改為 `"{memberEmail}将不会再收到新闻信。"`，遺漏了 `{newsletterName}` 變數。這可能導致顯示時缺少新聞信名稱，或造成變數替換錯誤。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## base-1:Ghost-8:3|Ghost-8#1

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行，候選管道 loc）「Name」翻譯從「名字」改為「名稱」可能造成不一致

> 在 portal.json 中，`"Name"` 的翻譯從 `"名字"` 改為 `"名稱"`。但在同檔案的 `"Jamie Larson": "阿宇"` 和 `"jamie@example.com": "ayu@example.com"` 等範例中，可能仍使用「名字」的語境。此外，ghost.json 中 `"Name"` 的翻譯也改為 `"名字"`，可能造成不一致。請確認此變更是否為預期。

finding 片段：`"Name": "名称",`

## base-1:Ghost-9:1|Ghost-9#0

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行，候選管道 loc）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-1:Ghost-9:1|Ghost-9#1

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行，候選管道 ident）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-1:Ghost-9:1|Ghost-9#2

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行，候選管道 loc）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-1:Ghost-9:1|Ghost-9#3

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行，候選管道 loc）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## base-1:Ghost-9:2|Ghost-9#0

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行，候選管道 ident）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:2|Ghost-9#1

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行，候選管道 loc）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:2|Ghost-9#2

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行，候選管道 ident）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:2|Ghost-9#3

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行，候選管道 ident）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:3|Ghost-9#0

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 17 行，候選管道 ident）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## base-1:Ghost-9:3|Ghost-9#1

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 5 行，候選管道 loc）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## base-1:Ghost-9:3|Ghost-9#2

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 18 行，候選管道 ident）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## base-1:Ghost-9:4|Ghost-9#0

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行，候選管道 ident）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:4|Ghost-9#1

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行，候選管道 loc）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:4|Ghost-9#2

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行，候選管道 ident）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:Ghost-9:4|Ghost-9#3

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行，候選管道 ident）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## base-1:aspnetcore-1:1|aspnetcore-1#2

**GT**（func）Browser navigation uses Forward() instead of Back() breaking test flow

> In the RedirectEnhancedGetToInternal test, after clicking a link that redirects from /redirect to /scroll-to-hash, the test attempts to verify that browser back navigation works correctly. However, the code calls Browser.Navigate().Forward() instead of Browser.Navigate().Back(). Since there is no forward history (the browser just navigated forward to the current page), Forward() does nothing and the browser remains at /scroll-to-hash. The subsequent assertions expect the browser to be back at /redirect with the "Redirections" heading, but it's still at the redirected page, causing the test to fail. The comment explicitly states "See that 'back' takes you to the place from before the redirection" but the code does the opposite action.

GT 片段：`// See that 'back' takes you to the place from before the redirection ⏎ Browser.Navigate().Forward(); ⏎ Browser.Equal("Redirections", () => _originalH1Element.Text); ⏎ Assert.EndsWith("/subdir/redirect", Browser.Url);`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:113`，距錨點 0 行，候選管道 loc）瀏覽器導航方向可能錯誤

> 在測試 `RedirectEnhancedGetToInternal` 中，原本使用 `Browser.Navigate().Back()` 來驗證返回上一頁，但此 PR 改為 `Browser.Navigate().Forward()`。若測試情境是驗證「返回」行為，使用 Forward 可能導致測試失敗或驗證錯誤的頁面。請確認此變更是否為預期，或是否應保留 Back。

finding 片段：`Browser.Navigate().Forward();`

## base-1:aspnetcore-1:2|aspnetcore-1#0

**GT**（rule）MSTest attribute in xUnit project

> The rule requires test projects to consistently use the xUnit framework, but the test method uses MSTest's [TestMethod] attribute instead of xUnit's [Fact] attribute

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException()`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 2 行，候選管道 loc）AppContext.SetSwitch 參數值可能相反

> 在測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 中，原本設定 `DisableThrowNavigationException` 為 `false`，但此 PR 改為 `true`。若測試目的是驗證「不拋出例外」的行為，設定為 `true` 可能導致測試情境與預期相反，進而無法正確驗證。請確認此變更是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-1:aspnetcore-1:2|aspnetcore-1#3

**GT**（func）Navigation exception test disables the exception mechanism it's meant to test

> The NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException test is designed to verify that NavigationException thrown during circular redirects doesn't become an unobserved task exception. The test name, comments, and logic all indicate it should test the exception handling behavior. However, the AppContext switch is set to true, which enables DisableThrowNavigationException, preventing NavigationException from being thrown at all. This fundamentally breaks the test's purpose - it can't validate exception handling behavior when exceptions are disabled. The test navigates to a circular redirect page that relies on NavigationException being thrown and properly handled, but with the switch enabled, the navigation manager uses a different code path that doesn't throw exceptions, making the test validate nothing meaningful.

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 0 行，候選管道 loc）AppContext.SetSwitch 參數值可能相反

> 在測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 中，原本設定 `DisableThrowNavigationException` 為 `false`，但此 PR 改為 `true`。若測試目的是驗證「不拋出例外」的行為，設定為 `true` 可能導致測試情境與預期相反，進而無法正確驗證。請確認此變更是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-1:aspnetcore-1:2|aspnetcore-1#6

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 3 行，候選管道 loc）AppContext.SetSwitch 參數值可能相反

> 在測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 中，原本設定 `DisableThrowNavigationException` 為 `false`，但此 PR 改為 `true`。若測試目的是驗證「不拋出例外」的行為，設定為 `true` 可能導致測試情境與預期相反，進而無法正確驗證。請確認此變更是否正確。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## base-1:aspnetcore-10:1|aspnetcore-10#2

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行，候選管道 loc）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 原本的驗證條件為 `if (value <= 0)`，會拒絕 0 或負數。變更後為 `if (value < 0)`，允許 0 值。但屬性文件說明為「strictly positive value」，且錯誤訊息仍為「must be positive」，因此允許 0 可能違反設計意圖。若設定為 0，可能導致保留檔案數為 0，造成所有日誌檔案被刪除或無法保留任何檔案。建議確認此變更是否為預期，若非預期應改回 `<= 0`。

finding 片段：`if (value < 0)`

## base-1:aspnetcore-10:2|aspnetcore-10#1

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47`，距錨點 0 行，候選管道 loc）BackgroundQueueSize 驗證條件變更可能拒絕 0 值

> 原本的驗證條件為 `if (value < 0)`，允許 0 值。變更後為 `if (value <= 0)`，拒絕 0 值。但屬性文件說明為「maximum size of the background log message queue or null for no limit」，且錯誤訊息仍為「must be non-negative」，因此拒絕 0 可能違反設計意圖。若設定為 0，可能代表不允許任何佇列，但此處可能導致無法設定為 0。建議確認此變更是否為預期，若非預期應改回 `< 0`。

finding 片段：`if (value <= 0)`

## base-1:aspnetcore-10:3|aspnetcore-10#3

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行，候選管道 loc）TryGetValidatableTypeInfo 中 out 參數初始化位置移動

> 原本在方法最後才設定 `validatableTypeInfo = null`，現在移到方法開頭。這在功能上可能沒有差異，因為 out 參數在方法內必須賦值，但移動位置可能影響可讀性或與其他程式碼的互動。建議確認此變更是否為預期，並確保所有路徑都有正確賦值。

finding 片段：`validatableTypeInfo = null;`

## base-1:aspnetcore-10:4|aspnetcore-10#0

**GT**（rule）Method brace on same line

> The rule requires opening braces to appear on a new line after method declarations, but this method has its opening brace on the same line as the declaration (K&R style).

GT 片段：`[Experimental("ASP0029", UrlFormat = "https://aka.ms/aspnet/analyzer/{0}")] ⏎ public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) { ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:66`，距錨點 0 行，候選管道 loc）TryGetValidatableParameterInfo 方法格式調整

> 方法簽名從多行改為單行，且大括號位置改變。這僅為格式調整，不影響功能。

finding 片段：`public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) {`

## base-1:aspnetcore-10:4|aspnetcore-10#3

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:66`，距錨點 11 行，候選管道 ident）TryGetValidatableParameterInfo 方法格式調整

> 方法簽名從多行改為單行，且大括號位置改變。這僅為格式調整，不影響功能。

finding 片段：`public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) {`

## base-1:aspnetcore-2:2|aspnetcore-2#3

**GT**（func）Race condition from premature TaskCompletionSource recreation

> The _receiveTcs TaskCompletionSource is recreated before checking if the buffer is zero-sized, creating a race condition in the WebSocketWrapper's ReceiveAsync implementation. When a zero-byte read occurs (buffer.Count == 0), the method returns early with the result but the TCS has already been reset. This means if another thread or the background task tries to set a result on the now-recreated TCS while this zero-byte read is in progress, it will affect the next receive operation rather than completing the current one. This breaks the synchronization contract and can cause message loss or out-of-order receives in the stateful reconnection test scenarios where WebSocket message sequencing is critical.

GT 片段：`public override async Task<WebSocketReceiveResult> ReceiveAsync(ArraySegment<byte> buffer, CancellationToken cancellationToken) ⏎ { ⏎ var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:408`，距錨點 0 行，候選管道 loc）`_receiveTcs` 重設時機變更可能影響測試行為

> 在 `WebSocketWrapper.ReceiveAsync` 中，原本在處理零位元組讀取後才重設 `_receiveTcs`，現在改為在 await 後立即重設。這可能導致在零位元組讀取時，新的 `_receiveTcs` 被建立，但後續的 `SetReceiveResult` 可能設定到新的 TCS 上，而測試預期的是舊的 TCS。需要確認此變更是否會造成測試不穩定或失敗。

finding 片段：`var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously); ⏎ // Handle zero-byte reads ⏎ if (buffer.Count == 0)`

## base-1:aspnetcore-2:3|aspnetcore-2#1

**GT**（func）Incorrect boolean operator in regex validation

> The test assertion uses AND (&&) operator instead of OR (||) when checking if the log message matches either the old or new CSP error pattern. This causes the test to fail because a log message cannot simultaneously match both regex patterns - they represent different browser error message formats. The original intent was to accept either format, but the AND operator requires both patterns to match at the same time, which is impossible. This will cause the test to fail even when receiving a valid CSP error message in either format.

GT 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

**finding**（`src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107`，距錨點 0 行，候選管道 model_line）測試斷言使用 `Assert.True` 搭配兩個 Regex 的 AND 條件，可能降低可讀性

> 原本使用 `Assert.Matches` 檢查單一 Regex，現在改為 `Assert.True` 並同時檢查兩個 Regex 是否都匹配。這可能導致當訊息只符合其中一個 Regex 時，錯誤訊息不夠明確。建議改用 `Assert.Matches` 分別檢查，或使用 `Assert.True` 時提供更詳細的失敗訊息。

finding 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

## base-1:aspnetcore-2:3|aspnetcore-2#4

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The modified test method does not contain explicit '// Arrange', '// Act', and '// Assert' (or '// Act & Assert') comments to delineate phases, violating the required AAA comment pattern.

GT 片段：`public void EmbeddingServerAppInsideIframe_WithCompressionEnabled_Fails() ⏎ { ⏎ ... ⏎ Assert.True(`

**finding**（`src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107`，距錨點 0 行，候選管道 model_line）測試斷言使用 `Assert.True` 搭配兩個 Regex 的 AND 條件，可能降低可讀性

> 原本使用 `Assert.Matches` 檢查單一 Regex，現在改為 `Assert.True` 並同時檢查兩個 Regex 是否都匹配。這可能導致當訊息只符合其中一個 Regex 時，錯誤訊息不夠明確。建議改用 `Assert.Matches` 分別檢查，或使用 `Assert.True` 時提供更詳細的失敗訊息。

finding 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

## base-1:aspnetcore-3:1|aspnetcore-3#1

**GT**（func）Case-insensitive path comparison on Unix breaks certificate directory detection

> The SSL_CERT_DIR validation logic uses StringComparison.OrdinalIgnoreCase when comparing Unix file paths. On Unix systems, file paths are case-sensitive, so '/home/user/certs' and '/home/user/Certs' are different directories. This case-insensitive comparison will incorrectly match different directories, causing the tool to report that the certificate directory is already configured when it's not, preventing proper certificate trust setup and leaving certificates untrusted.

GT 片段：`try ⏎ { ⏎ return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase); ⏎ }`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行，候選管道 loc）路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含

> 在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## base-1:aspnetcore-3:1|aspnetcore-3#2

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 10 行，候選管道 ident）路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含

> 在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## base-1:aspnetcore-3:1|aspnetcore-3#4

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行，候選管道 loc）路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含

> 在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## base-1:aspnetcore-3:3|aspnetcore-3#3

**GT**（func）Incorrect event level causes important certificate warnings to be suppressed in non-verbose mode

> When verbose mode is not enabled, the event listener is configured with EventLevel.LogAlways instead of the intended EventLevel.Critical. EventLevel.LogAlways (value 0) actually means all events are enabled, not just critical ones. The original PR intended to show only Critical events in non-verbose mode to suppress routine logging. This bug causes all certificate-related events including verbose debug messages to be displayed in non-verbose mode, flooding users with unnecessary output and making it harder to identify actual problems. This breaks the intended user experience where only critical information should be shown by default.

GT 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

**finding**（`src/Tools/dotnet-dev-certs/src/Program.cs:134`，距錨點 0 行，候選管道 loc）非 verbose 模式下啟用 LogAlways 可能輸出過多資訊

> 原本只有在 verbose 模式才會啟用事件監聽器，現在非 verbose 模式也會啟用並設定為 `EventLevel.LogAlways`。這可能導致原本只在 verbose 下顯示的 LogAlways 事件（如事件 110、114）在一般執行時也輸出，造成資訊過載。需確認這是否為預期行為。

finding 片段：`else ⏎ { ⏎ listener.EnableEvents(CertificateManager.Log, System.Diagnostics.Tracing.EventLevel.LogAlways); ⏎ }`

## base-1:aspnetcore-3:4|aspnetcore-3#0

**GT**（rule）Traditional constructor instead of primary

> The NssDb class uses traditional constructor syntax with repetitive parameter-to-field assignments when primary constructor syntax would be more concise

GT 片段：`private sealed class NssDb ⏎ { ⏎ private readonly string _path; ⏎ private readonly bool _isFirefox;`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:994`，距錨點 0 行，候選管道 loc）NssDb 類別改寫為傳統屬性，可能違反專案慣例

> 原本的 `NssDb` 使用 primary constructor 與自動實作屬性，現在改為傳統的唯讀屬性與建構子。若專案中普遍使用 primary constructor 或自動實作屬性，此改動可能降低一致性。建議確認專案慣例，若無特殊原因，可保留原本寫法。

finding 片段：`private sealed class NssDb ⏎ { ⏎ private readonly string _path; ⏎ private readonly bool _isFirefox;`

## base-1:aspnetcore-4:1|aspnetcore-4#0

**GT**（rule）Traditional namespace declaration used

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`namespace Microsoft.AspNetCore.Components.Forms ⏎ { ⏎ /// <summary> ⏎ /// Displays the display name for a specified field, reading from <see cref="DisplayAttribute"/>`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 30 行，候選管道 ident）DisplayName 元件在 For 參數變更時可能不會更新顯示名稱

> 在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱。然而，如果 `For` 表達式相同但底層模型屬性的顯示名稱因動態變更（例如資源檔更新或屬性變更）而改變，元件不會重新渲染。這可能導致顯示名稱過時。建議在每次 `SetParametersAsync` 時都重新計算，或提供一個方法來強制更新。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## base-1:aspnetcore-4:1|aspnetcore-4#1

**GT**（func）Unnecessary re-rendering on every parameter update with same display name

> The DisplayName component removed the check that prevents re-rendering when the display name hasn't changed (line 50-51). This means that every time SetParametersAsync is called with a changed expression (even if it results in the same display name), the component will trigger a render. This causes performance degradation in scenarios with frequent parameter updates, such as forms with dynamic field expressions, leading to unnecessary DOM updates and potential flickering in the UI.

GT 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ _displayName = newDisplayName;`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 0 行，候選管道 loc）DisplayName 元件在 For 參數變更時可能不會更新顯示名稱

> 在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱。然而，如果 `For` 表達式相同但底層模型屬性的顯示名稱因動態變更（例如資源檔更新或屬性變更）而改變，元件不會重新渲染。這可能導致顯示名稱過時。建議在每次 `SetParametersAsync` 時都重新計算，或提供一個方法來強制更新。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## base-1:aspnetcore-4:2|aspnetcore-4#2

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 16 行，候選管道 ident）Hot Reload 時未清除顯示名稱快取

> 在靜態建構函式中，當 Hot Reload 的 MetadataUpdateSupported 為 true 時，訂閱了 OnDeltaApplied 事件並呼叫 ClearCache。但 ClearCache 只清除了 `_memberInfoCache`，沒有清除 `_displayNameCache`。這可能導致在 Hot Reload 後顯示名稱仍然使用舊的快取值。建議在 ClearCache 中同時清除兩個快取。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## base-1:aspnetcore-4:2|aspnetcore-4#3

**GT**（func）Incomplete cache clearing during hot reload causes stale display names

> The ClearCache method only clears _memberInfoCache but fails to clear _displayNameCache (line 85). During hot reload scenarios when metadata updates occur, the HotReloadManager triggers ClearCache to ensure fresh metadata is loaded. However, with _displayNameCache not being cleared, the component will continue to display stale display names from cached MemberInfo objects even after the attributes have been modified in code. This breaks the hot reload functionality for DisplayAttribute and DisplayNameAttribute changes, requiring developers to restart the application to see attribute changes take effect.

GT 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 0 行，候選管道 loc）Hot Reload 時未清除顯示名稱快取

> 在靜態建構函式中，當 Hot Reload 的 MetadataUpdateSupported 為 true 時，訂閱了 OnDeltaApplied 事件並呼叫 ClearCache。但 ClearCache 只清除了 `_memberInfoCache`，沒有清除 `_displayNameCache`。這可能導致在 Hot Reload 後顯示名稱仍然使用舊的快取值。建議在 ClearCache 中同時清除兩個快取。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## base-1:aspnetcore-4:3|aspnetcore-4#2

**GT**（func）Missing display name caching causes performance degradation

> The GetDisplayName(MemberInfo) method in ExpressionMemberAccessor no longer uses the _displayNameCache dictionary to cache display names (lines 53-74). Instead, it performs reflection operations (GetCustomAttribute) on every call. Since this method is called frequently during component rendering and the DisplayName component can be used extensively throughout forms, this creates a significant performance bottleneck. The cache was specifically designed to avoid repeated reflection calls, and its removal will cause measurable slowdowns in forms with many DisplayName components.

GT 片段：`public static string GetDisplayName(MemberInfo member) ⏎ { ⏎ ArgumentNullException.ThrowIfNull(member); ⏎ var displayAttribute = member.GetCustomAttribute<DisplayAttribute>();`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:44`，距錨點 9 行，候選管道 ident）GetMemberInfo 方法可能拋出不明確的例外

> 當表達式不是 MemberExpression 時，會拋出 ArgumentException，但訊息中使用了 `accessorBody.GetType().Name`，這可能不夠明確。建議提供更具體的錯誤訊息，例如包含表達式的實際內容。

finding 片段：`throw new ArgumentException( ⏎ $"The provided expression contains a {accessorBody.GetType().Name} which is not supported. " + ⏎ $"Only simple member accessors (fields, properties) of an object are supported.");`

## base-1:aspnetcore-5:1|aspnetcore-5#3

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行，候選管道 loc）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## base-1:aspnetcore-5:1|aspnetcore-5#7

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行，候選管道 ident）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## base-1:aspnetcore-5:2|aspnetcore-5#0

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行，候選管道 loc）命名空間與類別縮排變更可能造成不必要的 diff

> 此變更將原本的 file-scoped namespace 改為 block-scoped namespace，並調整類別縮排。這與專案中其他測試檔案的風格可能不一致，且增加了 diff 的噪音。若無特殊原因，建議維持原本的 file-scoped namespace 寫法。

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ { ⏎ public class ServerComponentDeserializerTest ⏎ {`

## base-1:aspnetcore-6:1|aspnetcore-6#2

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:38`，距錨點 0 行，候選管道 loc）Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException

> 原本的程式碼在 `_tokenResult.InteractionOptions != null && _tokenResult.InteractiveRequestUrl != null` 時才呼叫 NavigateToLogin，否則使用 `_tokenResult.RedirectUrl!`。修改後，當 `InteractionOptions != null` 但 `InteractiveRequestUrl` 為 null 時，會直接傳遞 null 給 NavigateToLogin，可能導致 NullReferenceException。建議保留 null 檢查或提供替代邏輯。

finding 片段：`if (_tokenResult.InteractionOptions != null) ⏎ { ⏎ _navigation.NavigateToLogin(_tokenResult.InteractiveRequestUrl, _tokenResult.InteractionOptions); ⏎ }`

## base-1:aspnetcore-6:2|aspnetcore-6#0

**GT**（rule）Missing ConfigureAwait(false) on Task.Yield

> The rule requires all await expressions in library code (non-test, non-sample projects) to use .ConfigureAwait(false) to avoid capturing the synchronization context, but the await Task.Yield() expression at line 291 omits it.

GT 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 0 行，候選管道 loc）新增的 Task.Yield() 可能改變登出流程的時序

> 在 ProcessLogOut 中新增 `await Task.Yield();` 會讓出執行緒，可能導致後續的 AuthenticationState 取得延遲，或與其他非同步操作產生競態。若此變更非為了解決特定問題，建議移除；若為必要，請補充說明原因並確保測試涵蓋此情境。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## base-1:aspnetcore-6:2|aspnetcore-6#1

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 6 行，候選管道 ident）新增的 Task.Yield() 可能改變登出流程的時序

> 在 ProcessLogOut 中新增 `await Task.Yield();` 會讓出執行緒，可能導致後續的 AuthenticationState 取得延遲，或與其他非同步操作產生競態。若此變更非為了解決特定問題，建議移除；若為必要，請補充說明原因並確保測試涵蓋此情境。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield();`

## base-1:aspnetcore-7:1|aspnetcore-7#0

**GT**（rule）Missing braces in for loop

> The rule requires all control flow statements (if, else, for, foreach, while, do-while) to use curly braces even for single-line bodies, but the inner for loop omits curly braces

GT 片段：`for (const [initializerIdentifier, componentIdentifiers] of Object.entries(jsComponentInitializers)) { ⏎ const initializerFunc = DotNet.findJSFunction(initializerIdentifier, 0) as JSComponentInitializerCallback; ⏎ for (const componentIdentifier of componentIdentifiers) ⏎ initializerFunc(componentIde`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 4 行，候選管道 loc）hasInitializedJsComponents 全域旗標可能導致初始化被跳過

> `hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## base-1:aspnetcore-7:1|aspnetcore-7#1

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 10 行，候選管道 ident）hasInitializedJsComponents 全域旗標可能導致初始化被跳過

> `hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## base-1:aspnetcore-7:1|aspnetcore-7#2

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 2 行，候選管道 loc）hasInitializedJsComponents 全域旗標可能導致初始化被跳過

> `hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## base-1:aspnetcore-7:2|aspnetcore-7#1

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 7 行，候選管道 ident）多渲染器情境下 manager 被覆寫但未處理舊 manager

> 當 `currentRendererId !== rendererId` 時，程式會直接覆寫 `manager` 與 `currentRendererId`，但未對舊的 `manager` 做任何處理。雖然註解提到舊的 manager 已失效，但若舊渲染器仍存活（例如同時存在多個電路），可能導致舊渲染器的後續呼叫使用到錯誤的 manager。

建議確認此情境是否可能發生，若可能，應考慮以 Map 管理多個 manager，或明確禁止多渲染器同時啟用。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## base-1:aspnetcore-7:2|aspnetcore-7#2

**GT**（func）Missing parameter update causes stale data on circuit restart

> The assignment `jsComponentParametersByIdentifier = jsComponentParameters;` has been removed from the re-enabling logic. When a circuit restarts and `enableJSRootComponents` is called again with new parameters, the global `jsComponentParametersByIdentifier` is not updated. This causes the application to continue using stale parameters from the previous circuit. The `DynamicRootComponent` class constructor and methods rely on `jsComponentParametersByIdentifier` to retrieve component parameter definitions, so they will operate with outdated metadata after a circuit restart.

GT 片段：`// When the same renderer type re-enables (e.g., circuit restart or new circuit on same page), ⏎ // accept the new manager. The old manager's DotNetObjectReference is no longer valid anyway ⏎ // because the old circuit is gone. We don't dispose the old manager - doing so would cause ⏎ // JSDisconnec`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 0 行，候選管道 loc）多渲染器情境下 manager 被覆寫但未處理舊 manager

> 當 `currentRendererId !== rendererId` 時，程式會直接覆寫 `manager` 與 `currentRendererId`，但未對舊的 `manager` 做任何處理。雖然註解提到舊的 manager 已失效，但若舊渲染器仍存活（例如同時存在多個電路），可能導致舊渲染器的後續呼叫使用到錯誤的 manager。

建議確認此情境是否可能發生，若可能，應考慮以 Map 管理多個 manager，或明確禁止多渲染器同時啟用。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## base-1:aspnetcore-8:1|aspnetcore-8#1

**GT**（func）Remarks overwrite Summary instead of Description in XML comment transformation

> When XML remarks are present, they are incorrectly assigned to operation.Summary instead of operation.Description. This causes the remarks to overwrite the summary that was set earlier in the code (line 374). The XML documentation model distinguishes between summary (brief description) and remarks (detailed notes), and they should map to different OpenAPI fields. This bug causes the loss of the summary information when remarks are present, resulting in incorrect OpenAPI documentation where remarks replace the intended summary.

GT 片段：`if (methodComment.Remarks is { } remarks) ⏎ { ⏎ operation.Summary = remarks; ⏎ }`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:382`，距錨點 0 行，候選管道 loc）將 remarks 寫入 Summary 可能改變既有 API 文件行為

> 原本 `operation.Description = remarks;` 改為 `operation.Summary = remarks;`。這會將 `<remarks>` 的內容放到 OpenAPI 的 `summary` 欄位，而非 `description`。若既有使用者依賴 `description` 來顯示備註，此變更會造成文件內容遺失或錯置。建議確認此變更是否符合預期，或考慮同時設定兩者。

finding 片段：`operation.Summary = remarks;`

## base-1:aspnetcore-8:2|aspnetcore-8#2

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行，候選管道 loc）使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或序列化名稱），可能找不到對應的參數。建議確認兩者是否永遠相同，或保留原本的比對方式。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## base-1:aspnetcore-8:2|aspnetcore-8#3

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行，候選管道 ident）使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或序列化名稱），可能找不到對應的參數。建議確認兩者是否永遠相同，或保留原本的比對方式。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## base-1:aspnetcore-8:3|aspnetcore-8#2

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行，候選管道 ident）RequestBody.Description 設定位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在 if 區塊開頭，現在移到範例處理之後。若 `propertyComment.Examples` 存在但 `content` 為 null，會執行 `continue`，導致 `Description` 不會被設定。建議確認此情境是否會發生，或將 Description 設定保持在區塊開頭。

finding 片段：`operation.RequestBody.Description = description;`

## base-1:aspnetcore-8:3|aspnetcore-8#3

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行，候選管道 loc）RequestBody.Description 設定位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在 if 區塊開頭，現在移到範例處理之後。若 `propertyComment.Examples` 存在但 `content` 為 null，會執行 `continue`，導致 `Description` 不會被設定。建議確認此情境是否會發生，或將 Description 設定保持在區塊開頭。

finding 片段：`operation.RequestBody.Description = description;`

## base-1:aspnetcore-9:1|aspnetcore-9#2

**GT**（func）Missing PreReleaseBrandingLabel for servicing builds

> The PreReleaseBrandingLabel configuration is missing the condition for 'servicing' builds. While the PreReleaseVersionLabel is set to 'servicing', there is no corresponding conditional assignment for PreReleaseBrandingLabel when PreReleaseVersionLabel equals 'servicing'. This means servicing builds will have an undefined or incorrect branding label, causing incorrect version strings in build outputs and package metadata. The original PR added this condition to properly support servicing releases.

GT 片段：`<PreReleaseVersionLabel>servicing</PreReleaseVersionLabel> ⏎ <!-- PreReleaseBrandingLabel is automatically calculated based on PreReleaseVersionLabel --> ⏎ <PreReleaseBrandingLabel Condition="'$(PreReleaseVersionLabel)' == 'alpha'">Alpha $(PreReleaseVersionIteration)</PreReleaseBrandingLabel> ⏎ <Pre`

**finding**（`eng/Versions.props:14`，距錨點 8 行，候選管道 ident）停用 ValidateBaseline 可能隱藏套件參考變更

> 將 `ValidateBaseline` 從 `true` 改為 `false` 會關閉基線驗證，可能導致未預期的套件參考變更在 servicing 更新中被忽略。建議確認此變更的必要性，或僅在特定條件下停用。

finding 片段：`<ValidateBaseline>false</ValidateBaseline>`

## base-1:cal.com-1:1|cal.com-1#2

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行，候選管道 ident）orgId 型別轉換可能導致 SQL 錯誤

> 在 SQL 查詢中使用 `${orgId}::bigint`，但 orgId 是 number | undefined。若 orgId 為 undefined，會產生 `undefined::bigint`，在 PostgreSQL 中會導致語法錯誤。應使用 Prisma 的參數化查詢或明確處理 undefined。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## base-1:cal.com-1:2|cal.com-1#2

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行，候選管道 loc）orgId 過濾邏輯可能排除應包含的團隊

> 在 UNION 的第二部分，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})` 只檢查 org.id 或 child.id 等於 orgId，但未考慮 child.parentId 等於 orgId 的情況。這可能導致當 orgId 為父組織時，子團隊被錯誤排除。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## base-1:cal.com-1:3|cal.com-1#2

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行，候選管道 ident）orgId 為 null 時的行為不一致

> 在 getTeamsWithPBACPermissions 中，orgId 參數型別為 number | null，但 SQL 條件使用 `${orgId}::bigint IS NULL`。若 orgId 為 null，會產生 `null::bigint`，在 PostgreSQL 中可能被視為 NULL，但行為依賴於資料庫。建議明確處理 null 與 undefined。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## base-1:cal.com-1:5|cal.com-1#3

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行，候選管道 loc）isCurrentUser 判斷邏輯變更可能導致權限繞過

> 原本 isCurrentUser 僅在 filters.userIds 長度為 1 且等於 user.id 時為 true，現在改為 includes(user.id)。若 filters.userIds 包含多個 ID 且包含 user.id，則 isCurrentUser 為 true，可能允許使用者存取其他使用者的 booking。需確認此變更是否符合預期。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## base-1:cal.com-10:1|cal.com-10#1

**GT**（func）Incorrect booking status in audit trail for single booking acceptance

> When accepting a single (non-recurring) booking, the audit log incorrectly records the previous status as ACCEPTED instead of the actual original status (typically PENDING). This occurs because the acceptedBookings array is populated with BookingStatus.ACCEPTED as the oldStatus instead of booking.status. As a result, audit logs will show incorrect status transitions like ACCEPTED→ACCEPTED rather than the correct PENDING→ACCEPTED, making it impossible to track the actual booking lifecycle and potentially causing compliance issues with audit requirements.

GT 片段：`updatedBookings.push(updatedBooking); ⏎ acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:411`，距錨點 0 行，候選管道 loc）單筆接受時 oldStatus 硬編碼為 ACCEPTED，可能記錄錯誤的 audit log

> 在 `handleConfirmation` 中，當 `recurringEventId` 不存在時，`acceptedBookings` 被設定為 `[{ oldStatus: BookingStatus.ACCEPTED, uid: booking.uid }]`。但此時 booking 的實際狀態可能是 `PENDING` 或其他非 `ACCEPTED` 狀態，這會導致 audit log 中的 `oldStatus` 不正確。

建議從資料庫查詢 booking 的實際狀態，或使用先前已取得的 `booking.status`。

finding 片段：`acceptedBookings = [ ⏎ { ⏎ oldStatus: BookingStatus.ACCEPTED, ⏎ uid: booking.uid,`

## base-1:cal.com-10:4|cal.com-10#0

**GT**（rule）Line exceeds 110 character width

> The rule requires all TypeScript/JavaScript files to use a maximum line width of 110 characters, but this type declaration exceeds this limit at 172 characters

GT 片段：`private helper: AuditActionServiceHelper<typeof RejectedAuditActionService.latestFieldsSchema, typeof RejectedAuditActionService.storedDataSchema>;`

**finding**（`packages/features/booking-audit/lib/actions/RejectedAuditActionService.ts:19`，距錨點 18 行，候選管道 ident）RejectedAuditActionService 的 fieldsSchemaV1 變更可能導致既有資料無法解析

> `fieldsSchemaV1` 中的 `rejectionReason` 從 `StringChangeSchema` 改為 `z.string().nullable()`，且 `status` 改為 `BookingStatusChangeSchema`。這可能導致已儲存的 audit log 資料（使用舊 schema）在讀取時解析失敗。

需要確認是否有 migration 或相容性處理。

finding 片段：`const fieldsSchemaV1 = z.object({ ⏎ rejectionReason: z.string().nullable(), ⏎ status: BookingStatusChangeSchema, ⏎ });`

## base-1:cal.com-10:5|cal.com-10#3

**GT**（func）Race condition in recurring booking acceptance audit logging

> For recurring bookings, the fireBookingAcceptedEvent function is called BEFORE the database updates the booking statuses to ACCEPTED. This creates a timing issue where the audit system may attempt to record or query booking information before the database transaction completes. The audit logs could reference bookings that are still in PENDING state, or in extreme cases the audit consumer might fail to find consistent booking data. This race condition can lead to inconsistent audit trails, failed audit log creation, or audit records that don't accurately reflect the database state at the time of acceptance.

GT 片段：`const teamId = await getTeamIdFromEventType({ ⏎ eventType: { ⏎ team: { id: eventType?.teamId ?? null }, ⏎ parentId: eventType?.parentId ?? null,`

**finding**（`packages/features/bookings/lib/handleConfirmation.ts:263`，距錨點 5 行，候選管道 loc）fireBookingAcceptedEvent 在 recurring 分支中可能使用錯誤的 oldStatus

> 在 recurring 分支中，`acceptedBookings` 是從 `unconfirmedRecurringBookings` 取得，其 `oldStatus` 為 `booking.status`。但 `unconfirmedRecurringBookings` 查詢的條件是 `status: BookingStatus.PENDING`，因此 `oldStatus` 會是 `PENDING`，這可能是正確的。然而，若之後有其他狀態的 booking 被包含進來，則可能不正確。

建議確認查詢條件是否涵蓋所有需要更新的 booking。

finding 片段：`acceptedBookings = unconfirmedRecurringBookings.map((booking) => ({ ⏎ oldStatus: booking.status, ⏎ uid: booking.uid, ⏎ }));`
