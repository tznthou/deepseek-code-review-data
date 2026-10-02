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

## base-1:cal.com-11:1|cal.com-11#3

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行，候選管道 loc）requestReschedule 預設值不一致

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這會導致同一事件在不同 webhook 版本中收到不同的預設值，可能造成下游系統誤判。建議統一預設值，或明確在 DTO 中必填此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## base-1:cal.com-11:2|cal.com-11#0

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行，候選管道 loc）新增 ENABLE_WEBHOOKS 環境變數可能意外停用 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，則 `webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），則會意外停用所有取消 booking 的 webhook，可能導致下游系統收不到通知。建議確認此環境變數名稱是否專用，或改用更明確的名稱，並在文件中說明。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## base-1:cal.com-11:4|cal.com-11#1

**GT**（func）Incorrect requestReschedule flag for seat cancellation webhooks

> The cancelAttendeeSeat function incorrectly sets requestReschedule to true when cancelling individual attendee seats, even though this is not a reschedule request. This flag should be false for regular seat cancellations and only true for actual reschedule requests. External webhook consumers receiving BOOKING_CANCELLED events will incorrectly interpret seat cancellations as reschedule requests, potentially triggering wrong automated workflows, email templates, or business logic in integrated systems.

GT 片段：`const payload: EventPayloadType = { ⏎ ...evt, ⏎ ...eventTypeInfo, ⏎ status: "CANCELLED",`

**finding**（`packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167`，距錨點 0 行，候選管道 loc）requestReschedule 硬編碼為 true

> 在取消座位（cancelAttendeeSeat）流程中，`requestReschedule` 被硬編碼為 `true`。這可能不正確，因為取消座位不一定代表要求重新排程。建議確認此處的業務邏輯，若取消座位僅是取消單一與會者，應設為 `false`。

finding 片段：`requestReschedule: true,`

## base-1:cal.com-12:1|cal.com-12#2

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行，候選管道 loc）搜尋過濾功能失效：渲染改用 teamMembers 而非 filteredMembers

> 原本使用 `filteredMembers` 來渲染成員列表，以支援搜尋過濾功能。此變更改為直接使用 `teamMembers`，導致搜尋輸入不會影響顯示的成員列表。請確認此變更是否為預期行為；若非預期，應保留 `filteredMembers` 的過濾邏輯。

finding 片段：`{teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))} ⏎ {teamMembers.length === 0 && (`

## base-1:cal.com-12:3|cal.com-12#1

**GT**（func）Double-wrapping data structure causes matching members to be ignored

> The useTeamMembersWithSegment hook wraps the matchingTeamMembersWithResult in an extra layer when it already has a 'result' property from the trpc query. The trpc query returns { result, troubleshooter, mainWarnings, fallbackWarnings }, but the code creates { result: { result: ... } } by conditionally wrapping it again. This causes useProcessTeamMembersData to receive an incorrectly nested structure where matchingTeamMembersWithResult.result contains an object instead of an array, breaking the segment-based member filtering logic and causing the app to show all team members instead of only those matching the attribute segment.

GT 片段：`const { teamMembers, localWeightsInitialValues } = useProcessTeamMembersData({ ⏎ initialTeamMembers, ⏎ assignRRMembersUsingSegment, ⏎ matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:16`，距錨點 9 行，候選管道 ident）查詢條件可能不正確：teamId 為 0 時仍可能啟用查詢

> 查詢的 `enabled` 條件為 `assignRRMembersUsingSegment && !!queryValue && !!teamId`，但傳入的 `teamId` 可能為 0（例如未選擇團隊時），此時 `!!teamId` 為 false，查詢不會執行。然而，在 `useQuery` 的參數中使用了 `teamId: teamId || 0`，若 `teamId` 為 0 且查詢被啟用（例如其他條件為真），則會以 teamId=0 進行查詢，可能導致非預期結果。請確認此邏輯是否符合預期。

finding 片段：`teamId: teamId || 0, ⏎ attributesQueryValue: queryValue as AttributesQueryValue, ⏎ _enablePerf: true,`

## base-1:cal.com-12:4|cal.com-12#5

**GT**（rule）Missing trailing newline at end of file

> The diff indicates the file has no trailing newline ("\ No newline at end of file"), which violates standard formatting expectations enforced by formatters/linters.

GT 片段：`};\ No newline at end of file`

**finding**（`packages/platform/atoms/event-types/hooks/useTeamMembersWithSegmentPlatform.tsx:107`，距錨點 2 行，候選管道 loc）檔案結尾缺少換行符號

> 檔案結尾缺少換行符號，可能導致某些工具或 diff 顯示異常。建議在最後一行加上換行。

finding 片段：`}; ⏎ \ No newline at end of file`

## base-1:cal.com-13:2|cal.com-13#3

**GT**（func）FeatureOptInService creates isolated containers breaking dependency sharing

> The getFeatureOptInService() function creates a fresh DI container on every call, which then loads its dependencies including FeaturesRepository into that isolated container. This breaks the expected dependency injection pattern where services should share repository instances. When code calls both getFeaturesRepository() and getFeatureOptInService(), they each create separate containers with separate FeaturesRepository instances, leading to inconsistent cached state and duplicated database connections. The FeatureOptInService's repository will have different cached data than repositories retrieved elsewhere, causing unpredictable behavior in feature flag resolution.

GT 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 0 行，候選管道 loc）每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## base-1:cal.com-13:2|cal.com-13#4

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token);`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 3 行，候選管道 loc）每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## base-1:cal.com-13:3|cal.com-13#1

**GT**（func）Container created on every function call breaks singleton pattern

> The getFeaturesRepository() function now creates a new DI container instance on every invocation instead of reusing a module-level singleton container. This causes each call to return a different FeaturesRepository instance with its own PrismaClient connection, breaking the singleton pattern. This leads to database connection pool exhaustion and inconsistent cached state across repository instances, as FeaturesRepository maintains an internal cache for features (line 34 in features.repository.ts checks FeaturesRepository.featuresCache).

GT 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 0 行，候選管道 loc）每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## base-1:cal.com-13:3|cal.com-13#5

**GT**（rule）Line exceeds 110 character limit (Biome)

> This newly added line appears to exceed the 110 character line-width limit required by the Biome formatting rules.

GT 片段：`return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 3 行，候選管道 loc）每次呼叫 getFeaturesRepository 都建立新容器，可能造成效能與狀態問題

> `getFeaturesRepository` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的 repository 實例，增加不必要的開銷。如果 repository 內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## base-1:cal.com-13:4|cal.com-13#2

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行，候選管道 loc）moduleLoader 的 token 可能與綁定 token 不一致

> 在 `moduleLoader` 中，`token` 被設定為 `moduleToken`，但 `bindModuleToClassOnToken` 的 `token` 參數是 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。這可能導致使用 `moduleLoader.token` 來取得實例時，實際上是取得模組 token 而非服務 token，造成型別或實例錯誤。建議確認 `moduleLoader.token` 應該回傳服務 token 還是模組 token，並保持一致性。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## base-1:cal.com-14:1|cal.com-14#3

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行，候選管道 loc）listFeaturesForUser 過濾條件邏輯錯誤

> 在 `listFeaturesForUser` 方法中，原本的過濾條件是 `state.globalEnabled`，但此 PR 將其改為 `!state.globalEnabled`。這會導致只回傳全域停用的功能，而全域啟用的功能反而被排除。這與方法的文件說明「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」完全相反。

**失敗情境**：當使用者呼叫此方法時，所有全域啟用的功能都不會出現在結果中，而全域停用的功能卻會出現。這將導致使用者介面顯示錯誤的功能列表，或讓使用者無法看到應該可用的功能。

**建議修法**：將條件改回 `state.globalEnabled`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## base-1:cal.com-14:2|cal.com-14#0

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:4`，距錨點 0 行，候選管道 loc）未使用的常數 UNUSED_CONSTANT

> 新增的常數 `UNUSED_CONSTANT` 沒有被任何地方使用，且其名稱暗示這是故意留下的未使用程式碼。這會觸發 lint 警告（如 no-unused-vars），並增加不必要的維護負擔。

**建議修法**：移除該常數及其註解。

finding 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

## base-1:cal.com-15:1|cal.com-15#1

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行，候選管道 loc）Slot.userIds 型別從 number[] 改為 string[]，可能導致下游型別錯誤

> 原本在 @calcom/trpc/server/routers/viewer/slots/types.ts 中，Slot.userIds 的型別是 number[]，但此處新定義的 Slot.userIds 為 string[]。這可能導致使用此型別的下游程式碼（例如 apps/web/test/lib/getSchedule/expects.ts）在編譯或執行時出現型別不符的錯誤。請確認實際資料型別，若為 number[] 應修正為 number[]，或若確實為 string[] 則需同步更新所有使用處。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## base-1:cal.com-15:2|cal.com-15#0

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#3

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行，候選管道 ident）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#4

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#6

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:2|cal.com-15#7

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行，候選管道 loc）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## base-1:cal.com-15:4|cal.com-15#0

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#3

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#4

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#6

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 38 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-15:4|cal.com-15#7

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行，候選管道 ident）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## base-1:cal.com-16:1|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 10 行，候選管道 ident）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-1:cal.com-16:1|cal.com-16#2

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 0 行，候選管道 loc）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-1:cal.com-16:1|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 8 行，候選管道 ident）getRecordings 呼叫缺少 await，導致回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。這會讓 `recordings` 變數成為一個 Promise 物件，而不是實際的錄音資料陣列。當回傳給客戶端時，JSON 序列化會得到 `{}` 或非預期的內容，造成 API 回應錯誤。

**失敗情境**：任何呼叫此端點的請求都會收到錯誤的資料格式。

**建議修正**：改回 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## base-1:cal.com-16:2|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 0 行，候選管道 loc）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-1:cal.com-16:2|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:216`，距錨點 19 行，候選管道 ident）錄音端點權限從 BOOKING_READ 改為 BOOKING_WRITE，可能過度授權

> 此端點是讀取錄音資料，但權限從 `BOOKING_READ` 改為 `BOOKING_WRITE`。這代表只有具備寫入權限的 API key 才能存取錄音，而原本具有讀取權限的 key 將無法使用。這可能破壞向後相容性，且不符合最小權限原則。

**失敗情境**：使用僅有 `BOOKING_READ` 權限的 API key 呼叫此端點會得到 403，但預期應該允許讀取。

**建議修正**：維持 `BOOKING_READ` 權限，除非有明確理由需要寫入權限。

finding 片段：`@Permissions([BOOKING_WRITE])`

## base-1:cal.com-16:3|cal.com-16#1

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 21 行，候選管道 ident）逐字稿端點的 guard 順序可能影響錯誤回應

> 在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## base-1:cal.com-16:3|cal.com-16#3

**GT**（func）Incorrect guard execution order breaks authorization

> The transcripts endpoint has guards in wrong order: @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard). NestJS executes guards left-to-right, so BookingPbacGuard runs first. However, BookingPbacGuard requires request.user to be populated by ApiAuthGuard (which extracts the authenticated user from the token). Since BookingPbacGuard runs before ApiAuthGuard, request.user will be undefined, causing BookingPbacGuard to throw UnauthorizedException even for valid authenticated requests. All requests to this endpoint will fail with 401 Unauthorized.

GT 片段：`@Get("/:bookingUid/transcripts") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_READ]) ⏎ @UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 0 行，候選管道 loc）逐字稿端點的 guard 順序可能影響錯誤回應

> 在 `getBookingTranscripts` 端點，guard 順序從原本的 `BookingUidGuard` 改為 `BookingPbacGuard, ApiAuthGuard, BookingUidGuard`。若 `BookingPbacGuard` 在 `ApiAuthGuard` 之前執行，未驗證的請求可能會先被 Pbac 拒絕，導致回應 403 而非 401。這可能影響 API 的語意一致性。

**失敗情境**：未帶 token 的請求可能收到 403 而非預期的 401。

**建議修正**：確認 guard 執行順序是否符合預期，通常 `ApiAuthGuard` 應在最前面以正確回傳 401。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## base-1:cal.com-2:1|cal.com-2#1

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:588`，距錨點 0 行，候選管道 loc）hasPendingInviteByUserId 的 accepted 條件寫反

> 方法名稱是 hasPendingInviteByUserId，但查詢條件為 `accepted: true`，這會回傳「已接受」的邀請，而非「待處理」的邀請。這導致呼叫端（onboarding 頁面與 checkOnboardingRedirect）在用戶有已接受邀請時誤判為有 pending invite，進而錯誤 redirect。應改為 `accepted: false`。

finding 片段：`accepted: true,`

## base-1:cal.com-2:2|cal.com-2#2

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行，候選管道 loc）條件由 AND 改為 OR 可能改變既有流程

> 原本只有在同時有 pending invite 且 onboarding-v3 啟用時才導向 personal/settings，現在改成任一條件成立即導向。若 onboarding-v3 啟用但用戶沒有 pending invite，原本會繼續其他流程，現在會直接導向 personal/settings。請確認此行為變更是否符合預期。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) {`

## base-1:cal.com-3:1|cal.com-3#2

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1502`，距錨點 0 行，候選管道 loc）updateMany 未回傳 { count }，與介面不符

> `BookingRepository.updateMany` 的實作呼叫 `this.prismaClient.booking.updateMany` 後沒有回傳結果，但介面 `IBookingRepository` 定義此方法應回傳 `Promise<{ count: number }>`。這會導致呼叫端（例如 `handleCancelBooking` 中的 `await bookingRepository.updateMany(...)`）取得 `undefined`，若後續程式碼依賴回傳值（例如檢查更新筆數）將發生錯誤。

建議：在實作中回傳 `await this.prismaClient.booking.updateMany(...)` 的結果，或調整介面定義。

finding 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

## base-1:cal.com-3:2|cal.com-3#3

**GT**（func）Missing locale field causes translation failure in cancellation flow

> The 'userSelect' object used by UserRepository.findById (and subsequently findByIdOrThrow) no longer includes the 'locale' field. However, in handleCancelBooking.ts, the code calls 'getTranslation(organizer.locale ?? "en", "common")' which expects the locale property on the organizer object. Since locale is now undefined, the translation will always fall back to 'en' regardless of the user's actual locale preference, causing cancellation emails and notifications to be sent in the wrong language for non-English users.

GT 片段：`const userSelect = { ⏎ id: true, ⏎ username: true, ⏎ name: true,`

**finding**（`packages/features/users/repositories/UserRepository.ts:98`，距錨點 0 行，候選管道 loc）移除 userSelect 中的 locale 欄位可能導致取消流程錯誤

> `UserRepository` 的 `userSelect` 移除了 `locale` 欄位，但在 `handleCancelBooking` 中仍使用 `organizer.locale`（例如 `getTranslation(organizer.locale ?? "en", "common")`）。若 `findByIdOrThrow` 使用此 `userSelect`，回傳的 organizer 物件將缺少 `locale`，導致 `organizer.locale` 為 `undefined`，可能觸發錯誤或使用錯誤的預設語言。

建議：確認 `findByIdOrThrow` 是否使用此 `userSelect`，若需要 `locale` 則應保留該欄位，或改用其他方式取得。

finding 片段：`createdDate: true, ⏎ trialEndsAt: true, ⏎ completedOnboarding: true, ⏎ timeFormat: true,`

## base-1:cal.com-3:3|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:500`，距錨點 0 行，候選管道 loc）updateMany 呼叫未處理回傳值，可能掩蓋錯誤

> 在 `handleCancelBooking` 中，`await bookingRepository.updateMany(...)` 的結果未被使用。若 `updateMany` 實作未正確回傳（如前述 blocker），此處不會察覺錯誤。此外，即使回傳 `{ count }`，也應檢查是否更新了預期的筆數，以確保取消操作成功。

建議：檢查回傳的 `count` 是否符合預期，並在不符合時記錄錯誤或拋出例外。

finding 片段：`await bookingRepository.updateMany({ ⏎ where: { ⏎ recurringEventId, ⏎ startTime: {`

## base-1:cal.com-3:4|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:513`，距錨點 0 行，候選管道 loc）findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能遺漏時區處理

> 在 `handleCancelBooking` 中，`findManyIncludeWorkflowRemindersAndReferences` 的 `where` 條件使用 `gte: bookingToDelete.startTime`，但 `bookingToDelete.startTime` 是 Date 物件，可能包含時區資訊。若資料庫儲存的是 UTC，而此處傳入的 Date 未正確轉換，可能導致查詢結果不正確。

建議：確認 `bookingToDelete.startTime` 的時區處理，必要時使用 UTC 時間進行比較。

finding 片段：`const allUpdatedBookings = await bookingRepository.findManyIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ recurringEventId: bookingToDelete.recurringEventId, ⏎ startTime: {`

## base-1:cal.com-3:5|cal.com-3#1

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:546`，距錨點 30 行，候選管道 ident）updateIncludeWorkflowRemindersAndReferences 的 where 條件改為 uid 可能影響行為

> 原本的 `prisma.booking.update` 使用 `where: uid ? { uid } : { id }`，現在改為固定使用 `uid: bookingToDelete.uid`。若 `bookingToDelete.uid` 為空或未定義，將導致查詢失敗。雖然 `bookingToDelete` 應有 uid，但此變更可能影響某些邊界情況。

建議：確認 `bookingToDelete.uid` 一定存在，或保留原本的條件邏輯。

finding 片段：`const updatedBooking = await bookingRepository.updateIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ uid: bookingToDelete.uid, ⏎ },`

## base-1:cal.com-3:6|cal.com-3#2

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行，候選管道 loc）update 方法未使用 select，可能回傳過多資料

> `BookingRepository.update` 方法直接呼叫 `this.prismaClient.booking.update` 而未指定 `select`，可能回傳完整的 Booking 物件，包含不必要的關聯資料，影響效能。若呼叫端只需要部分欄位，建議加入 `select` 參數。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## base-1:cal.com-4:1|cal.com-4#4

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行，候選管道 loc）getDisplayEmail 正規表示式可能誤刪合法郵件中的加號標籤

> `getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除加號後 25 個字元。此模式假設所有加號後綴都是 CUID，但合法郵件地址（如 `user+tag@example.com`）中的加號標籤也會被移除，導致顯示錯誤。例如 `john+notes@example.com` 會變成 `john@example.com`。建議改用更精確的 CUID 格式（例如 `/\+[a-z0-9]{25}$/` 並檢查是否為 CUID），或僅在已知為 OAuth 產生的郵件時才移除。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## base-1:cal.com-4:2|cal.com-4#1

**GT**（func）Lost `this` context in displayGuests mapping causes runtime error

> In the `getOutputBooking` method at line 171, the code passes `this.getDisplayEmail` directly to the `map` function without binding the `this` context. This causes a runtime error because when `getDisplayEmail` is invoked inside the `map` callback, `this` will be `undefined`, resulting in "Cannot read property 'replace' of undefined" or similar errors. The arrow function `(guest: string) => this.getDisplayEmail(guest)` was removed, which was necessary to preserve the `this` binding. This will break all bookings that have guests.

GT 片段：`if ( ⏎ bookingTransformed.bookingFieldsResponses?.guests && ⏎ Array.isArray(bookingTransformed.bookingFieldsResponses.guests) ⏎ ) {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169`，距錨點 0 行，候選管道 model_line）displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## base-1:cal.com-4:2|cal.com-4#5

**GT**（rule）Line(s) exceed the 110 character line width requirement

> The added assignment line is longer than the 110 character limit required by the Biome formatting rules for TS/JS files.

GT 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:169`，距錨點 2 行，候選管道 model_line）displayGuests 的 map 回呼可能因 this 為 undefined 而拋錯

> 在 `getOutputBooking` 中，`bookingTransformed.bookingFieldsResponses.guests.map(this.getDisplayEmail)` 直接傳遞 `this.getDisplayEmail` 作為回呼。在 JavaScript 嚴格模式（TypeScript 預設）下，傳遞的函式內 `this` 會是 `undefined`，導致執行時拋出 `TypeError: Cannot read properties of undefined (reading 'replace')`。建議改為 `map((guest) => this.getDisplayEmail(guest))` 或綁定 `this`。

finding 片段：`bookingTransformed.bookingFieldsResponses.displayGuests = bookingTransformed.bookingFieldsResponses.guests.map( ⏎ this.getDisplayEmail ⏎ );`

## base-1:cal.com-4:3|cal.com-4#2

**GT**（func）Recurring seated bookings returned in wrong order

> In the `getOutputRecurringSeatedBookings` method at line 424, the sort operation that orders bookings chronologically by start time has been removed. The original code sorted bookings with `.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())` to ensure they are returned in chronological order. Without this sorting, recurring bookings will be returned in an arbitrary order (based on how they were stored in the database or map), which breaks the expected API contract and will confuse clients expecting chronological ordering of recurring events.

GT 片段：`async getOutputRecurringSeatedBookings(bookingsIds: number[], showAttendees: boolean) { ⏎ const databaseBookings = await this.bookingsRepository.getByIdsWithAttendeesWithBookingSeatAndUserAndEvent(bookingsIds); ⏎ const bookingsMap = new Map(databaseBookings.map(booking => [booking.id, booking])); ⏎ `

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:424`，距錨點 0 行，候選管道 loc）移除排序可能改變既有 API 行為

> `getOutputRecurringSeatedBookings` 原本會依 `start` 時間排序回傳的預訂，此 PR 移除了排序邏輯，直接回傳 `transformed`。這可能導致 API 回傳順序不穩定，影響依賴排序的客戶端。若無明確理由，建議保留排序。

finding 片段：`return transformed;`

## base-1:cal.com-4:4|cal.com-4#6

**GT**（rule）JSON formatting deviates from expected formatter output (indentation removed)

> The PR introduces improperly indented JSON (the 'required' key is moved to column 1). This indicates the JSON was not kept formatted per the repository’s formatting/lint-staged expectations (Biome format for JSON).

GT 片段：`-        "required": [ ⏎ +"required": [`

**finding**（`docs/api-reference/v2/openapi.json:31729`，距錨點 2 行，候選管道 model_line）OpenAPI 文件縮排不一致

> 在 `docs/api-reference/v2/openapi.json` 中，`required` 陣列的縮排從原本的 8 空格變成 0 空格，與其他屬性不一致。雖然不影響 JSON 解析，但可能造成維護上的困擾。建議修正縮排。

finding 片段：`"required": [ ⏎ "id", ⏎ "name", ⏎ "email",`

## base-1:cal.com-5:1|cal.com-5#2

**GT**（func）URL prefix displays protocol in read-only text field causing visual corruption

> The URL prefix display now incorrectly includes the protocol (https://) in the read-only portion of the booking URL field. The code returns '${url.protocol}//${url.hostname}${prefix}' which results in displaying 'https://cal.com/username/' as the prefix instead of just 'cal.com/username/'. This creates a confusing UI where the protocol appears in the grey read-only section, while users can still edit the slug portion, making the full URL construction unclear and potentially breaking user understanding of how the URL is formed.

GT 片段：`{(() => { ⏎ // Parse bookingUrl to get domain prefix (e.g., "i.cal.com/" or "cal.com/username/") ⏎ if (props.bookingUrl) { ⏎ try {`

**finding**（`companion/components/event-type-detail/tabs/BasicsTab.tsx:261`，距錨點 0 行，候選管道 loc）bookingUrl 解析邏輯可能產生錯誤的顯示前綴

> 在解析 bookingUrl 以取得顯示前綴時，程式碼使用 `url.hostname` 而非 `url.host`，這會忽略埠號。若 bookingUrl 包含非標準埠（例如開發環境），顯示的連結將不正確。此外，若 bookingUrl 為相對路徑或格式不符，`new URL` 會拋出例外，但 catch 區塊僅回退到 `cal.com/${props.username}/`，可能與實際網域不符。建議使用 `url.host` 並考慮更完整的錯誤處理。

finding 片段：`const url = new URL(props.bookingUrl); ⏎ // Get path without the last segment (slug) ⏎ const pathParts = url.pathname.split("/").filter(Boolean); ⏎ pathParts.pop(); // Remove slug`

## base-1:cal.com-5:3|cal.com-5#3

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1125`，距錨點 0 行，候選管道 model_line）複製連結功能未使用 bookingUrl，可能導致不一致

> 在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接 `https://cal.com/${username}/${slug}`，而未使用 `eventType.bookingUrl`。這與其他地方的修改不一致，可能導致使用者複製到舊格式的連結。建議統一使用 `eventType.bookingUrl` 或提供一致的 fallback。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## base-1:cal.com-6:1|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行，候選管道 loc）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## base-1:cal.com-6:1|cal.com-6#3

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行，候選管道 loc）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## base-1:cal.com-6:2|cal.com-6#2

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行，候選管道 loc）buildInviteLink 條件判斷反轉

> 原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

finding 片段：`if (isOrgContext) {`

## base-1:cal.com-6:2|cal.com-6#3

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行，候選管道 ident）buildInviteLink 條件判斷反轉

> 原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

finding 片段：`if (isOrgContext) {`

## base-1:cal.com-6:3|cal.com-6#1

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行，候選管道 loc）缺少團隊成員資格驗證

> 控制器使用 `@Roles("TEAM_MEMBER")` 來限制角色，但未驗證使用者是否為該團隊的成員。任何具有 TEAM_MEMBER 角色的使用者（可能是其他團隊的成員）都可以對任意 teamId 建立邀請。應在服務層或控制器中加入團隊成員資格檢查，例如確認使用者與 teamId 的關聯。

finding 片段：`@Roles("TEAM_MEMBER")`

## base-1:cal.com-6:4|cal.com-6#6

**GT**（rule）Line exceeds Biome configured line width

> The codebase formatting rule specifies a 110 character line width. This added line is clearly longer than 110 characters (chained call with long template literal), violating the configured formatting constraints.

GT 片段：`+      const first = await request(app.getHttpServer()).post(`/v2/teams/${team.id}/invite`).expect(200);`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:68`，距錨點 7 行，候選管道 model_line）測試可能因 token 不一致而失敗

> 測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會因為 token 回傳為 identifier 而失敗。此外，非管理員和非成員的測試預期 403，但若控制器未檢查團隊成員資格，這些測試可能不會通過。

finding 片段：`expect(response.body.data.inviteLink).toContain(response.body.data.token);`

## base-1:cal.com-7:1|cal.com-7#2

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行，候選管道 loc）使用 endsWith 過濾可能誤排除合法日曆

> 目前使用 `endsWith` 來排除 externalId 結尾為特定後綴的日曆。若使用者擁有一個自訂日曆，其 externalId 恰好以這些後綴結尾（例如 `mygroup@group.calendar.google.com`），則會被錯誤排除。建議改用更精確的比對方式，例如正規表示式或直接比對完整 ID 模式，或至少確認 Google 日曆 ID 的格式保證這些後綴只出現在通用日曆中。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## base-1:cal.com-8:1|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行，候選管道 ident）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:1|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行，候選管道 model_line）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:1|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行，候選管道 ident）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:2|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行，候選管道 ident）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:2|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 1 行，候選管道 model_line）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:2|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行，候選管道 ident）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## base-1:cal.com-8:3|cal.com-8#2

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行，候選管道 loc）屬性 badge 合併權重與群組標記，可能影響可讀性

> 原本權重以獨立 badge 顯示，現在合併到 label 中，例如 'Value 80% (group)'，可能讓使用者難以快速區分權重與群組狀態。建議保留分離的 badge 或使用更明確的視覺區分。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## base-1:cal.com-8:4|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行，候選管道 ident）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:4|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行，候選管道 loc）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:4|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行，候選管道 ident）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:5|cal.com-8#1

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行，候選管道 ident）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:5|cal.com-8#3

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行，候選管道 loc）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-8:5|cal.com-8#4

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 23 行，候選管道 ident）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## base-1:cal.com-9:1|cal.com-9#2

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:53`，距錨點 0 行，候選管道 loc）sortHosts 函式在移動時被意外修改，priority 比較方向反轉

> 在將 `sortHosts` 從 `HostEditDialogs.tsx` 移至 `hostGroupUtils.ts` 時，原本的 `return priorityB - priorityA;` 被改成了 `return priorityA - priorityB;`（在 `isRRWeightsEnabled` 為 true 且權重相等時）。這會反轉優先權排序，可能導致主機選擇錯誤。

**失敗情境**：當啟用 RR 權重且兩個主機權重相同時，優先權較低（數值較大）的主機會被排在前面，違反預期。

**建議**：將該行改回 `return priorityB - priorityA;`，與原始邏輯一致。

finding 片段：`return priorityA - priorityB;`

## base-1:dify-1:1|dify-1#0

**GT**（rule）Legacy typing imports instead modern syntax

> The rule requires using Python 3.12+ modern type syntax (set[tuple[str, ...]] instead of Set[Tuple[str, ...]]), but the code imports and uses legacy typing module classes Set and Tuple

GT 片段：`from collections.abc import Mapping, Sequence ⏎ from typing import TYPE_CHECKING, Any, Set, Tuple ⏎ ... ⏎ def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行，候選管道 loc）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## base-1:dify-1:1|dify-1#1

**GT**（func）Type mismatch in blocks_variable_output prevents variable blocking

> The blocks_variable_output method compares a Sequence (assigned_variable_selector) directly against a set of tuples (variable_selectors), but fails to convert the Sequence to a tuple first. This type mismatch causes the 'in' check to always return False, meaning the Variable Assigner node will never properly block streaming output of conversation variables. As a result, the response coordinator will incorrectly allow streaming to proceed before conversation variables are updated, violating the intended synchronization logic and potentially showing stale variable values to users.

GT 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool: ⏎ """ ⏎ Check if this Variable Assigner node blocks the output of specific variables. ⏎ Returns True if this node updates any of the requested conversation variables.`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行，候選管道 loc）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## base-1:dify-1:2|dify-1#3

**GT**（func）Test uses list equality instead of tuple conversion for event selector

> The test compares event.selector (which is a Sequence[str]) with a list literal using ==. While this might work in some cases due to Python's sequence equality, it's fragile and inconsistent with the pattern used elsewhere in the codebase. The original code correctly converted to tuple for comparison (tuple(event.selector) == ('conversation', 'conv_var')). This change breaks the filtering logic and will likely cause the test to fail to properly identify conversation variable chunk events, leading to false test failures.

GT 片段：`conv_var_chunk_events = [ ⏎ event ⏎ for event in events ⏎ if isinstance(event, NodeRunStreamChunkEvent) and event.selector == ["conversation", "conv_var"]`

**finding**（`api/tests/unit_tests/core/workflow/graph_engine/test_streaming_conversation_variables.py:75`，距錨點 4 行，候選管道 loc）測試假設所有 chunk 事件的值都等於輸入值，可能過於嚴格

> 測試中 `assert all(event.chunk == input_query for event in conv_var_chunk_events)` 假設每個 chunk 事件的值都完全等於輸入字串。若串流實作將輸入拆分成多個 chunk（例如逐字元），此斷言將失敗。建議改為驗證串接後的值等於輸入值，或放寬為檢查事件存在且值非空。

finding 片段：`assert all(event.chunk == input_query for event in conv_var_chunk_events), ( ⏎ "Expected streamed conversation variable value to match the input query" ⏎ )`

## base-1:dify-10:1|dify-10#2

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行，候選管道 loc）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## base-1:dify-10:1|dify-10#4

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:292`，距錨點 33 行，候選管道 ident）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## base-1:dify-10:2|dify-10#1

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:370`，距錨點 0 行，候選管道 loc）Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲

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

## base-1:dify-10:2|dify-10#3

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:370`，距錨點 10 行，候選管道 ident）Redis 故障時仍嘗試寫入快取，可能造成不必要的延遲

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

## base-1:dify-11:1|dify-11#3

**GT**（func）Tool responses replaced with tool inputs in agent history organization

> In the organize_agent_history method, when building ToolPromptMessage objects, the content is incorrectly populated from tool_inputs dictionary instead of tool_responses dictionary. This means the LLM will receive the tool's input parameters as if they were the tool's output/response. For example, if a tool was called with {"query": "weather in NYC"}, the agent history would show this input dict as the tool's response instead of the actual weather data. This breaks the agent's ability to learn from previous tool executions and will cause incorrect context to be passed to subsequent LLM calls.

GT 片段：`tool_call_response.append( ⏎ ToolPromptMessage( ⏎ content=str(tool_inputs.get(tool, agent_thought.observation)), ⏎ name=tool,`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 0 行，候選管道 loc）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-1:dify-11:1|dify-11#4

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行，候選管道 ident）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-1:dify-11:1|dify-11#5

**GT**（rule）Broad exception catch (except Exception) added for tool_responses JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type. The new code introduces another broad `except Exception:` while parsing JSON observations.

GT 片段：`if observation_payload: ⏎ try: ⏎ tool_responses = json.loads(observation_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 19 行，候選管道 ident）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後變成 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致回傳給模型的工具回應內容變成工具輸入，而非實際的觀察結果，可能造成模型產生錯誤的後續行為。

失敗情境：當 agent_thought 同時包含 tool_input 與 observation 時，歷史訊息中的工具回應會是輸入內容而非輸出，模型可能誤解工具執行結果。

建議改回使用 `tool_responses`，並保留原本的 fallback 邏輯。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## base-1:dify-11:3|dify-11#0

**GT**（rule）Pydantic v1 Config class usage

> The rule requires data validation to use Pydantic v2 with ConfigDict(extra='forbid'), but this code uses Pydantic v1 'class Config' syntax with 'extra = allow' which permits undeclared fields

GT 片段：`class AgentThoughtValidation(BaseModel): ⏎ """ ⏎ Validation model for agent thought data before database persistence. ⏎ """`

**finding**（`api/core/agent/base_agent_runner.py:64`，距錨點 0 行，候選管道 loc）Pydantic 模型使用舊版 Config 語法

> AgentThoughtValidation 使用 class Config 設定 extra = "allow"，但若專案已升級至 Pydantic v2，應改用 model_config = ConfigDict(extra='allow')。目前註解也提到此點，但未修正。

建議確認 Pydantic 版本，若為 v2 則改用新語法。

finding 片段：`class Config: ⏎ extra = "allow"  # Pydantic v1 syntax - should use ConfigDict(extra='forbid')`

## base-1:dify-12:2|dify-12#1

**GT**（func）Missing escape parameter in 'not contains' metadata filter

> In the metadata filtering logic for dataset retrieval, the 'not contains' case applies escape_like_pattern() to escape special characters but fails to specify the escape='\' parameter in the notlike() call. This renders the escaping ineffective - the database won't interpret the backslash escapes correctly, allowing special characters like %, _, and \ to be treated as SQL wildcards instead of literal characters. This creates a SQL injection vulnerability through LIKE wildcards and causes incorrect query results when filtering metadata that contains these special characters.

GT 片段：`case "not contains": ⏎ escaped_value = escape_like_pattern(str(value)) ⏎ filters.append(json_field.notlike(f"%{escaped_value}%"))`

**finding**（`api/core/rag/retrieval/dataset_retrieval.py:1207`，距錨點 0 行，候選管道 loc）notlike 未傳入 escape 參數，跳脫失效

> 在 `case "not contains"` 分支中，`json_field.notlike(f"%{escaped_value}%")` 沒有傳入 `escape="\\"`。這會導致跳脫字元被視為一般字元，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元，造成搜尋結果不正確，且可能被用於繞過預期的過濾邏輯。

finding 片段：`filters.append(json_field.notlike(f"%{escaped_value}%"))`

## base-1:dify-12:3|dify-12#2

**GT**（func）Incorrect escape character in IRIS vector database LIKE query

> The IRIS vector database implementation escapes special characters using backslash (via escape_like_pattern which produces \%, \_, \\) but then specifies ESCAPE '|' in the SQL query instead of ESCAPE '\'. This mismatch causes the database to look for the wrong escape character - it will treat | as the escape character while the string contains backslash escapes. As a result, the escaped special characters won't be properly interpreted, allowing SQL wildcards to remain active and causing search queries with special characters to produce incorrect results or security vulnerabilities.

GT 片段：`escaped_query = escape_like_pattern(query) ⏎ query_pattern = f"%{escaped_query}%" ⏎ sql = f""" ⏎ SELECT TOP {top_k} id, text, meta`

**finding**（`api/core/rag/datasource/vdb/iris/iris_vector.py:298`，距錨點 0 行，候選管道 loc）IRIS 的 LIKE 查詢使用 ESCAPE '|' 但跳脫函式使用反斜線

> 程式碼使用 `escape_like_pattern` 跳脫，該函式以反斜線作為跳脫字元，但 SQL 中指定 `ESCAPE '|'`，兩者不一致。這會導致跳脫字元不被識別，使用者輸入的 `%` 或 `_` 仍會被當作萬用字元。應將 ESCAPE 子句改為 `ESCAPE '\\'` 或修改跳脫函式以使用 `|`。

finding 片段：`WHERE text LIKE ? ESCAPE '|'`

## base-1:dify-13:1|dify-13#0

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行，候選管道 loc）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-1:dify-13:1|dify-13#1

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行，候選管道 loc）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## base-1:dify-2:1|dify-2#0

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行，候選管道 loc）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## base-1:dify-2:1|dify-2#1

**GT**（func）JSON schema not normalized before storage

> In the handleJSONSchemaChange callback, the code stores the raw user input value directly instead of the normalized JSON.stringify(v, null, 2) version. This means that if a user enters compact JSON like {"type":"object"}, it will be stored as-is rather than being formatted consistently. This breaks the intended behavior where all JSON schemas should be stored in a standardized pretty-printed format with 2-space indentation. When the schema is later retrieved and displayed, it may have inconsistent formatting, and downstream consumers expecting normalized JSON may encounter issues.

GT 片段：`try { ⏎ const v = JSON.parse(value) ⏎ handlePayloadChange('json_schema')(value) ⏎ return True`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行，候選管道 loc）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## base-1:dify-2:2|dify-2#3

**GT**（func）JSON schema validation uses non-normalized value

> The validation logic for jsonObject type validates jsonSchemaValue instead of normalizedJsonSchema. This is problematic because normalizedJsonSchema is computed earlier and correctly handles the case where an empty schema should be undefined. By validating jsonSchemaValue directly, the code validates the raw tempPayload value instead of the cleaned version. This inconsistency means that validation may pass but the wrong data could be saved, or validation may fail when it should succeed if the schema is empty but not yet normalized.

GT 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue) ⏎ if (schema?.type !== 'object') {`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:311`，距錨點 0 行，候選管道 loc）jsonSchemaValue 型別檢查不完整，可能跳過驗證

> 在 handleConfirm 中，驗證 JSON Schema 的條件為 `typeof jsonSchemaValue === 'string'`。但 tempPayload.json_schema 的型別可能是物件（例如從 API 載入時），此時若為物件，則不會進行 JSON.parse 和 type 檢查，直接通過驗證。這可能導致非 object 型別的 schema 被儲存。

建議改為：若 jsonSchemaValue 不是字串，先將其轉為字串（例如 JSON.stringify）再進行解析與驗證，或明確處理物件型別。

finding 片段：`if (!isSchemaEmpty && typeof jsonSchemaValue === 'string') { ⏎ try { ⏎ const schema = JSON.parse(jsonSchemaValue)`

## base-1:dify-3:1|dify-3#1

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:37`，距錨點 0 行，候選管道 loc）render_template 可能回傳 None，導致後續 len() 拋出 TypeError

> 在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 缺少 `'result'` 鍵，`rendered` 會是 `None`，函式直接回傳 `None`。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，會拋出 `TypeError: object of type 'NoneType' has no len()`，且此例外未被捕捉，導致節點執行失敗且無明確錯誤訊息。建議在回傳前檢查 `rendered` 是否為 `None`，若為 `None` 則拋出 `TemplateRenderError`。

finding 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

## base-1:dify-4:1|dify-4#0

**GT**（rule）Session without context manager usage

> The rule requires all database sessions to use 'with Session(db.engine, expire_on_commit=False) as session:' pattern for proper resource management, but the code creates a session without a context manager and never closes it

GT 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 0 行，候選管道 loc）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## base-1:dify-4:1|dify-4#4

**GT**（rule）ConversationVariable query missing tenant_id filter

> The SELECT against the tenant-scoped ConversationVariable table is filtered by id and conversation_id only, with no tenant_id predicate. This violates the requirement that tenant-scoped queries must include tenant_id scoping to prevent cross-tenant data access.

GT 片段：`stmt = select(ConversationVariable).where( ⏎ ConversationVariable.id == variable.id, ConversationVariable.conversation_id == conversation_id ⏎ )`

**finding**（`api/services/conversation_variable_updater.py:18`，距錨點 2 行，候選管道 loc）Session 未關閉，可能造成連線洩漏

> `update` 方法中建立了 `Session(db.engine)`，但在方法結束時沒有呼叫 `session.close()`。若 `session.commit()` 拋出例外，session 不會被關閉；即使正常執行，session 也會殘留直到被垃圾回收，可能導致資料庫連線池耗盡。建議使用 `with Session(db.engine) as session:` 或 `try/finally` 確保關閉。

finding 片段：`session = Session(db.engine) ⏎ row = session.scalar(stmt) ⏎ if not row: ⏎ raise ConversationVariableNotFoundError("conversation variable not found in the database")`

## base-1:dify-4:2|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行，候選管道 loc）在迴圈內呼叫 flush，且 flush 為空實作

> `on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## base-1:dify-4:2|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行，候選管道 loc）在迴圈內呼叫 flush，且 flush 為空實作

> `on_event` 中對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。但 `ConversationVariableUpdaterImpl.flush` 目前是空實作（pass），因此 flush 沒有實際效果。若未來 flush 實作批次提交，此處在迴圈內呼叫會導致多次提交，降低效能。建議將 flush 移到迴圈外，或明確 flush 的語義。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## base-1:dify-4:4|dify-4#1

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 0 行，候選管道 loc）selector 長度檢查可能不完整

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## base-1:dify-4:4|dify-4#3

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 12 行，候選管道 ident）selector 長度檢查可能不完整

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## base-1:dify-5:1|dify-5#0

**GT**（rule）Console.log in production frontend code

> The rule requires that production frontend code should not contain console statements (console.log, console.warn, console.error) and should use proper logging mechanisms instead

GT 片段：`const headerData = data[0] ⏎ console.log('Checking batch inputs:', { dataLength: data.length, headerData }) ⏎ let isMapVarName = true`

**finding**（`web/app/components/share/text-generation/index.tsx:199`，距錨點 0 行，候選管道 loc）console.log 可能洩漏使用者輸入資料

> 新增的 `console.log` 會將批次輸入的資料（包含使用者提供的內容）輸出到瀏覽器主控台。這可能導致敏感資訊外洩，且不應存在於正式程式碼中。

建議移除該行。

finding 片段：`console.log('Checking batch inputs:', { dataLength: data.length, headerData })`

## base-1:dify-5:2|dify-5#1

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行，候選管道 loc）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## base-1:dify-5:2|dify-5#4

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行，候選管道 loc）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## base-1:dify-5:3|dify-5#3

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行，候選管道 loc）數字輸入框類型從 number 改為 text 可能影響驗證

> 將數字輸入框的 `type` 從 `number` 改為 `text`，可能導致瀏覽器不再自動驗證數字格式，且行動裝置可能顯示不同的鍵盤。若此變更非刻意為之，建議保留 `type="number"`。

finding 片段：`type="text"`

## base-1:dify-6:1|dify-6#0

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:1|dify-6#1

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:28`，距錨點 4 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:1|dify-6#2

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:1|dify-6#3

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行，候選管道 loc）local_hostname 參數可能傳入空字串而非 None

> 在 `smtp = (smtplib.SMTP_SSL if ... else smtplib.SMTP)(..., local_hostname=local_host or None)` 中，當 `local_host` 為空字串時，`local_host or None` 會得到 `None`，看似正確。但若 `local_host` 為非空字串，則傳入該字串。然而，smtplib 的 `local_hostname` 參數若為空字串，可能導致連線失敗或行為異常。建議明確處理：若設定值為空字串，則傳入 `None`；否則傳入設定值。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## base-1:dify-6:2|dify-6#0

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行，候選管道 loc）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## base-1:dify-6:2|dify-6#1

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:32`，距錨點 0 行，候選管道 loc）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## base-1:dify-6:2|dify-6#3

**GT**（func）Redundant empty string to None conversion defeats purpose of hostname override

> After converting None to empty string on line 25, the code then converts empty string back to None using `local_host or None` when passing to the SMTP constructor. This double conversion defeats the entire purpose of the SMTP_LOCAL_HOSTNAME feature. When a user explicitly sets SMTP_LOCAL_HOSTNAME to an empty string (perhaps to force default behavior), this logic will pass None to smtplib instead of respecting the user's configuration. The redundant `or None` should be removed, and the initial conversion to empty string is also problematic as explained in the previous issue.

GT 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

**finding**（`api/libs/smtp.py:32`，距錨點 3 行，候選管道 loc）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## base-1:dify-7:1|dify-7#1

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 27 行，候選管道 ident）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-1:dify-7:1|dify-7#2

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 0 行，候選管道 loc）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-1:dify-7:1|dify-7#3

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:12`，距錨點 0 行，候選管道 loc）createTFunction 對 options 的處理可能與實際 react-i18next 不一致

> `createTFunction` 在建構 `fullKey` 時，若 `options` 存在但沒有 `ns` 屬性，會使用 `defaultNs` 或直接使用 `key`。然而，實際 react-i18next 的 `t` 函數在沒有 `ns` 時，會使用預設 namespace（通常是 `translation`），而不是直接回傳 key。這可能導致測試中斷言與實際行為不符。建議確認此 mock 的預期行為，並考慮加入對 `defaultNs` 的處理。

finding 片段：`const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## base-1:dify-7:2|dify-7#1

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 15 行，候選管道 ident）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## base-1:dify-7:2|dify-7#2

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 3 行，候選管道 loc）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## base-1:dify-7:2|dify-7#3

**GT**（func）Missing returnObjects support breaks production components and tests

> The new `createTFunction` implementation in `web/test/i18n-mock.ts` does not handle the `returnObjects` option that was supported in the original global mock. The original implementation in `vitest.setup.ts` returned an array when `options?.returnObjects` was true, but the new implementation ignores this option entirely. This breaks production components like `web/app/components/billing/pricing/plans/self-hosted-plan-item/list/index.tsx` which uses `t('plans.${plan}.features', { ns: 'billing', returnObjects: true }) as string[]` and then calls `.map()` on the result, expecting an array. Without this support, the function returns a string instead of an array, causing runtime errors when the code attempts to iterate over the features. While some tests have local mocks that handle this, any test relying on the global mock's `returnObjects` behavior will fail.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:24`，距錨點 0 行，候選管道 loc）序列化 params 時未處理 returnObjects 選項

> 全域 mock 原本有處理 `options.returnObjects`，回傳陣列。新的 `createTFunction` 沒有處理此選項，可能導致依賴此行為的測試失敗。建議在 helper 中加入對 `returnObjects` 的支援，或確認沒有測試使用此功能。

finding 片段：`const params = { ...options } ⏎ delete params.ns ⏎ const suffix = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''`

## base-1:dify-8:1|dify-8#0

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行，候選管道 ident）React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊

> 當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## base-1:dify-8:1|dify-8#4

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行，候選管道 loc）React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊

> 當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## base-1:dify-8:2|dify-8#4

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行，候選管道 loc）TanStack Devtools 載入失敗時完全靜默

> catch 區塊僅回傳空元件，沒有任何錯誤記錄。這使得在開發環境中若動態 import 失敗，開發者將無法得知原因，增加除錯困難。建議至少加入 `console.error` 或使用 Sentry 記錄錯誤。

finding 片段：`}).catch(() => { ⏎ return { default: () => null } ⏎ }),`

## base-1:dify-9:1|dify-9#2

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:43`，距錨點 0 行，候選管道 loc）移除否定運算子可能反轉搜尋模式判斷

> 在 `useMarketplaceSearchMode` 中，原本 `!(PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType))` 改為 `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)`，移除了否定運算子。這會導致當 activePluginType 屬於 PLUGIN_CATEGORY_WITH_COLLECTIONS 時，原本應為非搜尋模式，現在卻會被視為搜尋模式，反之亦然。請確認此變更是否為預期行為，若非預期，請恢復否定運算子。

finding 片段：`|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`

## base-1:dify-9:2|dify-9#1

**GT**（func）Query parameter naming collision between plugin page and marketplace

> The plugin page context changed from 'category' to 'tab' query parameter (line 71), but the marketplace useActivePluginType still uses 'tab' instead of 'category' (line 23 in atoms.ts). This creates a naming collision where both components try to control the same 'tab' URL query parameter for different purposes. When users navigate between the plugin page tabs and marketplace categories, the URL state will conflict causing incorrect active states and navigation issues. The marketplace should use 'category' parameter while the plugin page uses 'tab' parameter to maintain their independent states.

GT 片段：`export function useActivePluginType() { ⏎ return useQueryState('tab', marketplaceSearchParamsParsers.category) ⏎ }`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:23`，距錨點 0 行，候選管道 loc）query key 從 'category' 改為 'tab' 可能破壞既有連結

> `useActivePluginType` 的 query key 從 `'category'` 改為 `'tab'`。若使用者已將帶有 `?category=...` 的網址加入書籤或分享，升級後這些連結將不再生效，可能導致使用者看到非預期的分類。建議考慮保留舊 key 的相容性，或確認此變更為可接受的 breaking change。

finding 片段：`return useQueryState('tab', marketplaceSearchParamsParsers.category)`

## base-1:dify-9:2|dify-9#2

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:23`，距錨點 17 行，候選管道 ident）query key 從 'category' 改為 'tab' 可能破壞既有連結

> `useActivePluginType` 的 query key 從 `'category'` 改為 `'tab'`。若使用者已將帶有 `?category=...` 的網址加入書籤或分享，升級後這些連結將不再生效，可能導致使用者看到非預期的分類。建議考慮保留舊 key 的相容性，或確認此變更為可接受的 breaking change。

finding 片段：`return useQueryState('tab', marketplaceSearchParamsParsers.category)`

## base-1:dify-9:3|dify-9#0

**GT**（rule）Any type used for selector parameter

> The rule requires using specific types instead of 'any' annotations. The selector parameter uses 'any' instead of a proper function type signature.

GT 片段：`export function usePluginPageContext(selector: any) { ⏎ return useContextSelector(PluginPageContext, selector) ⏎ }`

**finding**（`web/app/components/plugins/plugin-page/context.tsx:51`，距錨點 0 行，候選管道 loc）selector 參數型別從函式放寬為 any，喪失型別安全

> `usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。這會讓呼叫端可以傳入任意值，若傳入非函式，`useContextSelector` 可能拋出錯誤或產生非預期行為。建議保留原本的函式型別，或使用更精確的泛型。

finding 片段：`export function usePluginPageContext(selector: any) {`

## base-1:firefox-ios-1:1|firefox-ios-1#2

**GT**（func）Inconsistent format specifier documentation in RolloutsSettingMessage comment

> The comment for RolloutsSettingMessage incorrectly documents the format specifier as '%1$@' (positional format) while the actual value string uses '%@' (simple format). This mismatch creates confusion for localization teams and could lead to incorrect translations, as translators may attempt to use positional formatting based on the comment when the string implementation doesn't support it. The comment should match the actual format specifier used in the value field.

GT 片段：`public static let RolloutsSettingMessage = MZLocalizedString( ⏎ key: "Settings.Rollouts.Message.v148", ⏎ tableName: "Settings", ⏎ value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.",`

**finding**（`firefox-ios/Shared/Strings.swift:6260`，距錨點 0 行，候選管道 loc）格式佔位符不一致可能導致執行時期錯誤

> 在 `RolloutsSettingMessage` 的 value 中使用了 `%@`，但 comment 中說明為 `%1$@`。若翻譯人員依照 comment 使用 `%1$@`，則在執行時期使用 `String(format:)` 時，若只傳入一個參數，`%1$@` 是合法的（指定第一個參數），但若程式碼預期使用 `%@` 而翻譯使用 `%1$@`，可能導致格式字串與參數不匹配。建議統一使用 `%@` 或 `%1$@`，並確保所有翻譯遵循相同格式。

finding 片段：`value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", ⏎ comment: "A short description that explains that Mozilla may change features remotely. %1$@ is the app name (e.g. Firefox)."`

## base-1:firefox-ios-1:2|firefox-ios-1#0

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行，候選管道 loc）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## base-1:firefox-ios-1:2|firefox-ios-1#1

**GT**（func）Incorrect localized string reference in SettingsTextFormatter

> The formatStudiesText method references strings.detailTextStudies instead of strings.detailTextStudiesV2. This causes the formatter to display the old v1 Studies message ('%@ may install and run studies from time to time.') instead of the new v148 message ('%@ randomly selects users to test features, which improves quality for everyone.') that was added in this PR. The helper class was clearly intended to format the new v148 strings based on the PR context, but uses the wrong string constant.

GT 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ }`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 5 行，候選管道 loc）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## base-1:firefox-ios-1:2|firefox-ios-1#4

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行，候選管道 loc）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## base-1:firefox-ios-1:2|firefox-ios-1#5

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行，候選管道 loc）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## base-1:firefox-ios-1:2|firefox-ios-1#6

**GT**（rule）SettingsTextFormatter should be marked final

> The helper singleton class is not designed for inheritance but is declared as a non-final class. Per the rule, such classes must be marked `final` to prevent unintended subclassing and enable compiler optimizations.

GT 片段：`class SettingsTextFormatter {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行，候選管道 loc）新增的 SettingsTextFormatter 類別未被使用

> 新增的 `SettingsTextFormatter` 類別提供了 `formatStudiesText` 和 `formatRolloutsText` 方法，但在這個 diff 中沒有看到任何呼叫點。如果這個類別是為了未來使用，建議先不要加入，或加入對應的使用程式碼。此外，`shared` 單例若未被使用，會造成不必要的記憶體佔用。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## base-1:firefox-ios-10:1|firefox-ios-10#1

**GT**（func）Test completes without waiting for async image download

> The test was converted from async to synchronous but the expectation and wait statement were removed. This causes the test to complete immediately without waiting for the asynchronous image download callback to execute. The XCTAssert statements inside the completion handler will never be verified, resulting in false positive test passes even if the image download fails or produces incorrect results. This is a critical testing bug that undermines test reliability.

GT 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ guard let imageData = try? dataFor(type: assetType) else {`

**finding**（`BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:27`，距錨點 0 行，候選管道 loc）測試改為同步後未等待非同步完成，可能導致測試提前結束或無法驗證結果

> 在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，移除了 `await fulfillment(of: [exp], timeout: 2.0)`，且未使用 `wait(for:timeout:)`。`downloadImage` 的回呼是非同步的，測試方法現在是同步的，因此測試會在回呼執行前就返回，導致測試永遠通過（即使回呼中有 XCTFail 也不會被執行）。建議保留 expectation 並使用 `wait(for:timeout:)` 等待。

finding 片段：`siteDownloader.downloadImage(with: mockedURL, options: [.processor(SVGImageProcessor())]) { result in`

## base-1:firefox-ios-10:2|firefox-ios-10#3

**GT**（func）Async test assertion never verified due to missing expectation

> The test was updated to use @Sendable closures for Swift 6 concurrency compliance, but the expectation and wait statements were removed. The test now completes immediately without waiting for the asynchronous requestMediaCapturePermission callback. The XCTAssertEqual inside the decisionHandler closure will never execute, causing the test to always pass even when the media capture permission logic is broken. This is particularly problematic because this test validates critical permission handling behavior.

GT 片段：`func testRequestMediaCaptureSuccess() { ⏎ let subject = createSubject(isActive: true) ⏎ let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt)`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 0 行，候選管道 loc）測試未等待非同步決策處理器，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，移除了 expectation 的建立與 `wait(for:)`，但 `requestMediaCapturePermission` 可能非同步呼叫決策處理器。測試方法現在是同步的，可能在處理器執行前就返回，導致斷言未被執行。建議保留 expectation 並等待。

finding 片段：`subject.requestMediaCapturePermission(decisionHandler: decisionHandler)`

## base-1:firefox-ios-10:4|firefox-ios-10#0

**GT**（rule）Missing Mozilla Public License header

> The rule requires that every .swift file begins with the exact Mozilla Public License header comment block at the top of the file. This file is missing the required header entirely.

GT 片段：`import ContentBlockingGenerator ⏎ @main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行，候選管道 loc）使用 nonisolated(unsafe) 可能隱藏執行緒安全問題

> `nonisolated(unsafe)` 標註表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 實例並非執行緒安全，可能導致資料競爭。建議確認其內部狀態或改為隔離。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## base-1:firefox-ios-10:4|firefox-ios-10#4

**GT**（func）Unsafe concurrency annotation on non-thread-safe static property

> The static generator property is marked with nonisolated(unsafe) despite the comment explicitly stating 'ContentBlockerGenerator is not thread safe'. This annotation bypasses Swift 6's concurrency safety checks and allows the non-thread-safe ContentBlockerGenerator to be accessed from multiple isolation domains without protection. This creates a potential data race condition where multiple threads could access the generator simultaneously, leading to undefined behavior, crashes, or data corruption. The unsafe annotation should only be used when the developer can guarantee thread safety through other means, which the comment explicitly contradicts.

GT 片段：`@main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行，候選管道 loc）使用 nonisolated(unsafe) 可能隱藏執行緒安全問題

> `nonisolated(unsafe)` 標註表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 實例並非執行緒安全，可能導致資料競爭。建議確認其內部狀態或改為隔離。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## base-1:firefox-ios-10:4|firefox-ios-10#5

**GT**（rule）Static property missing explicit access control modifier

> Rule 11 requires explicit access control on properties/methods. The modified static property `generator` is declared without an explicit access modifier (e.g., `private`, `internal`, `public`).

GT 片段：`// FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行，候選管道 loc）使用 nonisolated(unsafe) 可能隱藏執行緒安全問題

> `nonisolated(unsafe)` 標註表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 實例並非執行緒安全，可能導致資料競爭。建議確認其內部狀態或改為隔離。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## base-1:firefox-ios-11:1|firefox-ios-11#2

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:329`，距錨點 0 行，候選管道 loc）updateActionStack 的 stacks 合併誤將 pageActionStack 改為 browserActionStack

> 在 `updateActionStack` 方法中，原本合併 `browserActionStack`、`navigationActionStack`、`leadingPageActionStack`、`pageActionStack` 的 arrangedSubviews，但此 PR 將最後一項改為 `browserActionStack`，導致 `trailingPageActionStack`（原 `pageActionStack`）的 arrangedSubviews 未被納入。這會使後續的動畫或可視性更新遺漏 trailing page actions，可能造成 UI 不一致或動畫失效。

建議改回 `trailingPageActionStack.arrangedSubviews`。

finding 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

## base-1:firefox-ios-11:2|firefox-ios-11#3

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行，候選管道 loc）skeleton address bar 的 leading 約束可能誤接至 rightSkeletonAddressBar

> 在 `setupSkeletonAddressBarsLayout` 中，原本 `toolbar.leadingAnchor.constraint(equalTo: leftSkeletonAddressBar.trailingAnchor)` 被改為 `toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor)`。這可能導致 toolbar 的 leading 錯誤地對齊到右側 skeleton bar 的 trailing，造成佈局錯亂。

請確認此變更是否為預期；若非預期，應改回 `leftSkeletonAddressBar.trailingAnchor`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## base-1:firefox-ios-11:3|firefox-ios-11#1

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行，候選管道 loc）hasPageActions 判斷誤用 leadingPageActionStack

> 在 `updateToolbarLayout` 中，原本 `let hasPageActions = !pageActionStack.arrangedSubviews.isEmpty` 被改為 `!leadingPageActionStack.arrangedSubviews.isEmpty`。但此處的 `hasPageActions` 應代表 trailing page actions 是否存在，以決定 divider 寬度。若 leading 和 trailing page actions 不同時存在，可能導致 divider 顯示錯誤。

建議改回 `!trailingPageActionStack.arrangedSubviews.isEmpty`。

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## base-1:firefox-ios-11:4|firefox-ios-11#0

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行，候選管道 loc）使用已棄用的 statusBarOrientation API

> 新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## base-1:firefox-ios-11:4|firefox-ios-11#4

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行，候選管道 loc）使用已棄用的 statusBarOrientation API

> 新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## base-1:firefox-ios-12:1|firefox-ios-12#3

**GT**（func）Test expectation fulfilled after wait causes timeout

> The expectation.fulfill() call was moved outside the decisionHandler closure and placed after the wait() call. This creates a logic error where the test waits for an expectation that will never be fulfilled by the decision handler. The expectation is only fulfilled after the wait times out, causing the test to always fail with a timeout error rather than validating the actual permission decision behavior.

GT 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ let expectation = expectation(description: "Wait for the decision handler to be called")`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 1 行，候選管道 model_line）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## base-1:firefox-ios-12:1|firefox-ios-12#4

**GT**（rule）Force unwrap of URL initializer in tests

> SwiftLint commonly forbids force-unwrapping. The test code force-unwraps the result of `URL(string:)` via `!` in newly added lines.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行，候選管道 model_line）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## base-1:firefox-ios-12:1|firefox-ios-12#5

**GT**（rule）Force unwrap of URL initializer in tests (second occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行，候選管道 model_line）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## base-1:firefox-ios-12:1|firefox-ios-12#6

**GT**（rule）Force unwrap of URL initializer in tests (third occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 4 行，候選管道 model_line）expectation 使用錯誤導致測試可能永遠等待或提前通過

> 在 `testRequestMediaCaptureSuccess` 中，`decisionHandler` 內沒有呼叫 `expectation.fulfill()`，而是在呼叫 `subject.webView(...)` 之後直接呼叫 `expectation.fulfill()`。這會造成兩種問題：
1. 如果 `decisionHandler` 從未被呼叫，測試仍會因為手動 fulfill 而通過，失去驗證效果。
2. 如果 `decisionHandler` 在 `wait(for:)` 之後才被呼叫，測試可能已經結束，導致非同步 callback 在測試結束後執行，可能造成 crash 或未定義行為。

建議將 `expectation.fulfill()` 移回 `decisionHandler` 內，並移除多餘的 `expectation.fulfill()`。

finding 片段：`let decisionHandler = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt) ⏎ } ⏎ `

## base-1:firefox-ios-12:2|firefox-ios-12#1

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 16 行，候選管道 ident）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## base-1:firefox-ios-12:2|firefox-ios-12#2

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 3 行，候選管道 loc）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## base-1:firefox-ios-12:2|firefox-ios-12#7

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 3 行，候選管道 loc）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## base-1:firefox-ios-12:2|firefox-ios-12#8

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 19 行，候選管道 ident）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## base-1:firefox-ios-12:2|firefox-ios-12#9

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 7 行，候選管道 ident）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## base-1:firefox-ios-12:3|firefox-ios-12#0

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行，候選管道 ident）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## base-1:firefox-ios-12:3|firefox-ios-12#1

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 19 行，候選管道 ident）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## base-1:firefox-ios-12:3|firefox-ios-12#2

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行，候選管道 loc）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## base-1:firefox-ios-12:3|firefox-ios-12#7

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行，候選管道 loc）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## base-1:firefox-ios-12:3|firefox-ios-12#8

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 22 行，候選管道 ident）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## base-1:firefox-ios-12:3|firefox-ios-12#9

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行，候選管道 ident）XCTWaiter 的結果未檢查，可能掩蓋逾時錯誤

> `XCTWaiter.wait(for:timeout:)` 的回傳值（`XCTWaiter.Result`）被忽略。如果等待逾時，`delegate.capturedFrame` 或 `capturedOrigin` 可能為 nil，函式會回傳 nil，但測試中只會以 `XCTFail` 處理，沒有提供逾時的詳細資訊。這使得除錯困難。

建議檢查 waiter 的結果，並在逾時或失敗時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## base-1:firefox-ios-12:4|firefox-ios-12#0

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 5 行，候選管道 loc）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## base-1:firefox-ios-12:4|firefox-ios-12#1

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 0 行，候選管道 loc）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## base-1:firefox-ios-12:4|firefox-ios-12#2

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 21 行，候選管道 ident）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## base-1:firefox-ios-12:4|firefox-ios-12#8

**GT**（rule）Missing explicit access control on class members

> Rule requires explicit access control modifiers. The added properties and methods (`expect`, `capturedFrame`, `capturedOrigin`, `init`, and `webView(...)`) have no explicit `private/internal` modifiers (defaulting to `internal`).

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 1 行，候選管道 loc）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## base-1:firefox-ios-12:4|firefox-ios-12#10

**GT**（rule）Missing // MARK: section organization

> The new Swift file defines multiple logical sections (nested delegate type, static helper function) but includes no `// MARK:` comments to delineate them, violating the required section organization rule.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 10 行，候選管道 ident）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## base-1:firefox-ios-13:1|firefox-ios-13#1

**GT**（func）Incorrect logical operator in tearDown causing theme reset to be skipped for all iPad tests

> The tearDown method uses OR (||) instead of AND (&&) when checking if the test should skip theme reset. This causes the theme reset to be skipped for ALL tests running on iPad devices, not just the testSelectBottomPlacement test. The original intent was to skip theme reset only when BOTH conditions are true (the test is testSelectBottomPlacement AND it's running on iPad), but the current code skips it when EITHER condition is true. This will leave the theme in Dark mode after any test runs on iPad, potentially affecting subsequent tests that expect Light theme.

GT 片段：`override func tearDown() async throws { ⏎ if #available(iOS 17.0, *) { ⏎ if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there.`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29`，距錨點 0 行，候選管道 loc）tearDown 提前 return 可能略過 app.terminate() 與 super.tearDown()

> 在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立時直接 `return`，導致後續的 `app.terminate()` 與 `try await super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的隔離性。建議改為使用 `if` 條件包住主題切換，而不是直接 return，確保清理邏輯總會執行。

finding 片段：`if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there. ⏎ return ⏎ } else {`

## base-1:firefox-ios-13:2|firefox-ios-13#0

**GT**（rule）Test method missing test prefix

> The rule requires test methods to start with 'test' prefix, but the method 'verifyBookmarksShareNormalWebsiteReminders' does not follow this naming convention

GT 片段：`// https://mozilla.testrail.io/index.php?/cases/view/2864380 ⏎ func verifyBookmarksShareNormalWebsiteReminders() { ⏎ app.launch() ⏎ if #available(iOS 17, *) {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ShareLongPressTests.swift:47`，距錨點 0 行，候選管道 loc）測試方法改名後失去 test 前綴，可能不再被 XCTest 執行

> 方法 `testBookmarksShareNormalWebsiteReminders` 被改名為 `verifyBookmarksShareNormalWebsiteReminders`，但 XCTest 只會自動執行以 `test` 開頭的方法。若此方法原本是測試案例，改名後將不再被執行，導致測試覆蓋率下降。建議保留 `test` 前綴，或確認此方法已改為輔助方法並有對應的測試呼叫。

finding 片段：`func verifyBookmarksShareNormalWebsiteReminders() {`

## base-1:firefox-ios-13:3|firefox-ios-13#2

**GT**（func）Insufficient timeout for paste permission dialog causing test flakiness

> The timeout for the 'Allow Paste' permission dialog button was reduced from 1.5 seconds to 0.5 seconds. This is too short for the iOS permission dialog to appear and be interactable, especially on slower devices or under load. The tapIfExists method waits for the element to exist within the specified timeout before attempting to tap it. A 0.5 second timeout may cause the test to miss the permission dialog entirely, preventing the paste action from completing and causing subsequent assertions to fail when the URL is not populated in the address bar.

GT 片段：`urlBar.pressWithRetry(duration: 2.0, element: pasteAction) ⏎ mozWaitForElementToExist(app.tables["Context Menu"]) ⏎ pasteAction.waitAndTap() ⏎ springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:471`，距錨點 0 行，候選管道 loc）tapIfExists 使用固定 timeout 可能不穩定

> 新增的 `springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)` 使用固定 0.5 秒等待系統提示出現。在慢速 CI 或裝置上，提示可能延遲出現，導致 tapIfExists 找不到按鈕而失敗。建議使用較長的 timeout 或改用 `mozWaitForElementToExist` 搭配條件點擊。

finding 片段：`springboard.buttons["Allow Paste"].tapIfExists(timeout: 0.5)`

## base-1:firefox-ios-2:1|firefox-ios-2#1

**GT**（func）Missing try keyword in async throws method call

> The IpadOnlyTestCase.setUp() method is marked as 'async throws' but calls 'await super.setUp()' without the 'try' keyword. Since BaseTestCase.setUp() is declared as 'async throws', this means any errors thrown by the parent setUp will not be properly propagated and will instead cause a compilation error or runtime crash. This breaks the error handling contract for all iPad-specific test cases that inherit from IpadOnlyTestCase, potentially causing test suite failures or silent test skips.

GT 片段：`class IpadOnlyTestCase: BaseTestCase { ⏎ override func setUp() async throws { ⏎ specificForPlatform = .pad ⏎ if iPad() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508`，距錨點 0 行，候選管道 model_line）IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try

> 在 IpadOnlyTestCase 的 setUp 方法中，`super.setUp()` 現在是 async throws，但呼叫時沒有加上 `try`。這會導致編譯錯誤：`Call can throw but is not marked with 'try'`。

建議改為 `try await super.setUp()`。

finding 片段：`await super.setUp()`

## base-1:firefox-ios-2:2|firefox-ios-2#2

**GT**（func）Incorrect initialization order in test setup

> In FeatureFlaggedTestSuite.setUp(), the method calls setUpApp() before setUpExperimentVariables(). However, setUpApp() (line 42-44) directly uses jsonFileName and featureName properties that are initialized by setUpExperimentVariables(). This means setUpApp() will be called with nil or uninitialized values, causing addLaunchArgument() to receive invalid parameters. This breaks the experiment/feature flag configuration for all tests inheriting from FeatureFlaggedTestSuite, resulting in tests running with incorrect or missing feature flags.

GT 片段：`override func setUp() async throws { ⏎ continueAfterFailure = false ⏎ setUpApp()  // Called before setUpExperimentVariables ⏎ setUpExperimentVariables()  // Sets jsonFileName and featureName`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/FeatureFlaggedTestBase.swift:48`，距錨點 0 行，候選管道 loc）setUp 中 setUpApp() 與 setUpExperimentVariables() 順序變更可能影響測試

> 原本的順序是先呼叫 `setUpExperimentVariables()` 再呼叫 `setUpApp()`，但變更後順序顛倒。如果 `setUpApp()` 依賴於實驗變數的設定（例如 launch arguments 中包含實驗變數），則可能導致測試行為不正確。

建議確認此順序變更是否為有意為之，若無必要請恢復原順序。

finding 片段：`setUpApp() ⏎ setUpExperimentVariables()`

## base-1:firefox-ios-3:1|firefox-ios-3#1

**GT**（func）Incorrect async Task wrapper breaks MainActor isolation in onboarding action handler

> The onActionTap closure is wrapped in a Task block without ensuring MainActor isolation. The OnboardingFlowViewModel expects this closure to be @MainActor isolated, but Task {} creates a new async context that may execute on a different executor. This causes the completion handler and handleAction calls to potentially run off the main thread, leading to concurrency violations and potential crashes when UI updates occur. The original code directly called onboardingService.handleAction which maintained proper MainActor isolation.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in ⏎ guard let onboardingService = self?.onboardingService else { return } ⏎ Task { ⏎ onboardingService.handleAction(`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行，候選管道 loc）將 onActionTap 閉包內容包在 Task 中可能改變執行順序與錯誤處理

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使得 handleAction 的執行變成非同步，可能導致呼叫端預期的同步行為失效。例如，若 handleAction 內部有需要立即完成的狀態更新，或 completion 需要在特定時序被呼叫，延遲可能造成 UI 不一致。此外，Task 中未處理可能的錯誤（如 handleAction 拋錯），可能導致錯誤被吞掉。建議確認 handleAction 是否為非同步設計，或考慮使用 Task { @MainActor in ... } 並明確處理錯誤。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## base-1:firefox-ios-3:1|firefox-ios-3#6

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行，候選管道 loc）將 onActionTap 閉包內容包在 Task 中可能改變執行順序與錯誤處理

> 原本 onActionTap 閉包直接呼叫 onboardingService.handleAction，現在改為在 Task 中執行。這會使得 handleAction 的執行變成非同步，可能導致呼叫端預期的同步行為失效。例如，若 handleAction 內部有需要立即完成的狀態更新，或 completion 需要在特定時序被呼叫，延遲可能造成 UI 不一致。此外，Task 中未處理可能的錯誤（如 handleAction 拋錯），可能導致錯誤被吞掉。建議確認 handleAction 是否為非同步設計，或考慮使用 Task { @MainActor in ... } 並明確處理錯誤。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## base-1:firefox-ios-3:3|firefox-ios-3#0

**GT**（rule）UI constants not in UX struct

> The rule requires UI constants and magic numbers to be organized within a dedicated nested UX struct, but the button size constant (40) is hardcoded directly in the constraint definitions instead of being defined in a private struct UX.

GT 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

**finding**（`firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192`，距錨點 0 行，候選管道 loc）移除 UX.buttonSize 常數改為魔法數字 40

> 原本使用 UX.buttonSize 常數，現在直接寫死為 40。這降低了可讀性與可維護性，若未來需要調整按鈕大小，需修改多處。建議保留常數或使用有意義的名稱。

finding 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

## base-1:firefox-ios-4:1|firefox-ios-4#2

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行，候選管道 loc）測試斷言可能指向錯誤的 UI 元素

> 在 `testCheckSystemThemeChanges` 中，原本檢查 `lightThemeView` 的 value，現在改為檢查 `darkThemeView`。但變數名稱仍為 `lightIsSelected`，且後續的 XCTAssertEqual 預期值為 "1"。如果 `darkThemeView` 的 value 在選取 Light mode 後不是 "1"，測試將失敗。需要確認此變更是否為刻意修正（例如原本的 identifier 有誤），否則可能造成測試不穩定或誤報。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## base-1:firefox-ios-4:2|firefox-ios-4#3

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行，候選管道 loc）測試步驟順序調整可能影響穩定性

> 在 `testDisableTopSitesSettingsRemovesSection` 中，原本先 `navigator.goto(NewTabScreen)` 再點擊 "Done"，現在改為先點擊 "Done" 再 `navigator.goto(NewTabScreen)`。如果 "Done" 按鈕在當前畫面不存在或不可點擊，可能導致測試失敗。需要確認此調整是否為了解決特定問題，並驗證在各種裝置與狀態下仍能穩定執行。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## base-1:firefox-ios-5:1|firefox-ios-5#1

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行，候選管道 loc）off-by-one 錯誤：滾動索引超出陣列範圍

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，原本回傳 `state.tabs.count - 1`，但此 PR 改為 `state.tabs.count`。這會導致 `toIndex` 等於陣列長度，超出有效索引範圍（最後一個索引應為 `count - 1`）。後續在 `TabDisplayView.scrollToTab` 中會使用此索引建立 `IndexPath(row:section:)`，可能造成滾動到不存在的 cell，甚至觸發越界例外。

建議改回 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## base-1:firefox-ios-5:2|firefox-ios-5#2

**GT**（func）Incorrect section index after inactive tabs removal

> The scrollToTab method hardcodes section index as 1, which was correct when there were two sections (inactive tabs at section 0 and regular tabs at section 1). After removing inactive tabs, there is only one section (section 0), so this will cause scroll operations to fail or crash when trying to access a non-existent section. This affects all scroll-to-tab functionality including selecting tabs, undoing tab closures, and panel switching. The TabDisplayDiffableDataSource now only creates a single section `.tabs`, but this scroll method wasn't updated accordingly.

GT 片段：`private func scrollToTab(_ scrollState: TabsPanelState.ScrollState) { ⏎ let indexPath = IndexPath(row: scrollState.toIndex, section: 1) ⏎ // Piping this into main thread let the collection view finish its layout process ⏎ DispatchQueue.main.async {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172`，距錨點 0 行，候選管道 loc）滾動目標 section 固定為 1，但現在只有一個 section

> 在 `scrollToTab` 中，原本根據 `scrollState.isInactiveTabSection` 決定 section 為 0 或 1，現在直接寫死為 1。但移除 inactive tabs 後，collection view 只有一個 section（index 0），因此 `IndexPath(row:section:1)` 會指向不存在的 section，導致滾動功能失效。

建議將 section 改為 0。

finding 片段：`let indexPath = IndexPath(row: scrollState.toIndex, section: 1)`

## base-1:firefox-ios-5:3|firefox-ios-5#3

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行，候選管道 loc）新增的 v147 結構體可能未被使用

> 在 `String` 擴展中新增了 `struct v147`，其中包含原本屬於 `InactiveTabs` 的本地化字串。但這些字串在程式碼中已不再被引用（因為相關視圖已刪除），可能成為死代碼。若確認不再需要，應一併移除；若仍需要保留以供未來使用，建議加上註解說明。

finding 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString(`

## base-1:firefox-ios-6:1|firefox-ios-6#0

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27`，距錨點 0 行，候選管道 loc）使用 assert 取代 XCTAssertTrue 會使測試在 release 建置中失效

> 在測試方法中，將 `XCTAssertTrue` 改為 `assert` 會導致斷言在 release 建置（`-O` 或 `-Ounchecked`）中被編譯器移除，使得測試永遠通過，無法驗證行為。此外，`assert` 失敗時會直接 crash 而非記錄測試失敗，破壞 XCTest 的報告機制。

建議改回 `XCTAssertTrue`，並保留原本的訊息參數。

finding 片段：`assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

## base-1:firefox-ios-7:1|firefox-ios-7#2

**GT**（func）ensureMainThread generic function loses return value when dispatched asynchronously

> The generic ensureMainThread<T> function was modified to return T? but has a critical flaw: when not on the main thread, it dispatches the work asynchronously to main queue and immediately returns nil, discarding the actual computation result. This breaks any caller that depends on the return value, as they will always receive nil when called from background threads. The function's contract promises to return the work result but fails to do so in the async dispatch path.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行，候選管道 loc）ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理

> `ensureMainThread<T>` 現在在非主執行緒時會回傳 `nil`，但呼叫端可能預期它會同步等待或總是有值。這可能導致呼叫端在未檢查 `nil` 的情況下強制解包，造成執行時期錯誤。建議確認所有呼叫端都正確處理了 `nil`，或考慮提供非同步版本。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## base-1:firefox-ios-7:1|firefox-ios-7#4

**GT**（rule）Public ensureMainThread<T> lacks documentation comment

> A new/modified public API was introduced/changed without an accompanying triple-slash documentation comment describing its purpose/parameters/return value.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? {`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行，候選管道 loc）ensureMainThread 泛型版本在非主執行緒時回傳 nil，可能導致呼叫端未處理

> `ensureMainThread<T>` 現在在非主執行緒時會回傳 `nil`，但呼叫端可能預期它會同步等待或總是有值。這可能導致呼叫端在未檢查 `nil` 的情況下強制解包，造成執行時期錯誤。建議確認所有呼叫端都正確處理了 `nil`，或考慮提供非同步版本。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## base-1:firefox-ios-7:2|firefox-ios-7#3

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:25`，距錨點 0 行，候選管道 loc）throttle 方法中 lastExecutionTime 更新順序改變可能影響節流邏輯

> 原本 `lastExecutionTime` 在 guard 之後才更新，現在移到 guard 之前。這可能導致在 threshold 條件不滿足時也更新了時間，影響後續呼叫的節流判斷。請確認此變更是否為預期行為。

finding 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

## base-1:firefox-ios-7:3|firefox-ios-7#1

**GT**（func）Thread safety violation calling @MainActor completion handler from background thread

> In the handleServerTrust method, when SSL/TLS certificate validation fails (guard else clause), the @MainActor-isolated completionHandler is called directly from the background dispatchQueue without using ensureMainThread wrapper. This violates Swift Concurrency's actor isolation and can cause runtime crashes or data races. The success path correctly wraps the completion call in ensureMainThread, but the failure path at line 1343 does not, creating inconsistent thread safety behavior.

GT 片段：`func handleServerTrust( ⏎ challenge: URLAuthenticationChallenge, ⏎ dispatchQueue: DispatchQueueInterface, ⏎ completionHandler: @escaping @MainActor (URLSession.AuthChallengeDisposition, URLCredential?) -> Void`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/Extensions/BrowserViewController+WebViewDelegates.swift:1343`，距錨點 0 行，候選管道 loc）移除 ensureMainThread 包裝可能導致 completionHandler 在非主執行緒被呼叫

> 原本使用 `ensureMainThread` 確保 `completionHandler` 在主執行緒執行，現在直接呼叫。若此處原本可能在背景執行緒，則可能違反 `@MainActor` 隔離。請確認此函式是否總是在主執行緒被呼叫。

finding 片段：`completionHandler(.performDefaultHandling, nil)`

## base-1:firefox-ios-8:2|firefox-ios-8#1

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:17`，距錨點 0 行，候選管道 loc）非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題

> `LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 `await`，但該方法現在是 async 且 @MainActor）。這可能導致編譯錯誤或執行緒問題。建議將測試類別標記為 `@MainActor`，並確保呼叫方式正確。

finding 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

## base-1:firefox-ios-8:6|firefox-ios-8#1

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:28`，距錨點 8 行，候選管道 ident）tearDown 中呼叫 @MainActor 方法可能導致執行緒問題

> `tearDown` 中呼叫 `DependencyHelperMock().reset()` 未加 `await`，但 `reset` 可能也是 @MainActor 隔離。若測試類別未標記 @MainActor，可能導致編譯錯誤或執行緒問題。建議檢查 `reset` 的隔離屬性，並在必要時加上 `await` 或將類別標記為 @MainActor。

finding 片段：`override func tearDown() async throws { ⏎ AppContainer.shared.reset() ⏎ UserDefaults.standard.removeObject(forKey: PrefsKeys.NimbusUserEnabledFeatureTestsOverride) ⏎ profile = nil`

## base-1:firefox-ios-8:10|firefox-ios-8#0

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行，候選管道 loc）bootstrapDependencies 標記為 @MainActor 但未處理非主執行緒呼叫

> `bootstrapDependencies` 被標記為 `@MainActor`，但方法內部仍有 `DispatchQueue.main.sync` 的舊程式碼被移除，改為直接在主執行緒上執行。這可能導致在非主執行緒呼叫時發生問題。建議確認所有呼叫點都在主執行緒上，或保留適當的執行緒處理。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## base-1:firefox-ios-9:1|firefox-ios-9#3

**GT**（func）Wrong display view type for reader mode action

> The handleShowReaderModeAction function sets the wrong displayView type when the user taps the reader mode button. Instead of setting displayView to '.readerMode' (which would show the reader mode view), it's set to '.readerModeLongPressAction' (which is meant for long-press actions). This causes the wrong UI component to be displayed when users try to activate reader mode, breaking the core reader mode functionality and showing an incorrect action sheet instead of the reader view.

GT 片段：`@MainActor ⏎ private static func handleShowReaderModeAction(state: BrowserViewControllerState, ⏎ action: GeneralBrowserAction) -> BrowserViewControllerState { ⏎ return BrowserViewControllerState(`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/State/BrowserViewControllerState.swift:566`，距錨點 0 行，候選管道 loc）displayView 從 .readerMode 改為 .readerModeLongPressAction 可能造成錯誤畫面顯示

> 在 `handleShowReaderModeLongPressAction` 中，原本設定 `displayView: .readerMode`，但此 PR 將其改為 `.readerModeLongPressAction`。這可能導致長按閱讀模式按鈕時顯示錯誤的畫面，或造成狀態不一致。請確認此變更是否為筆誤，若不是，請提供對應的測試與說明。

finding 片段：`displayView: .readerModeLongPressAction,`

## base-1:firefox-ios-9:2|firefox-ios-9#1

**GT**（func）Incorrect Reader Mode URL handling in cancelEditMode

> The cancelEditMode function now incorrectly preserves reader mode URLs when canceling edit mode. The logic was changed from '&&' (AND) to '||' (OR), which means reader mode URLs will now be kept instead of being cleared. This breaks the expected behavior where reader mode URLs should be filtered out when canceling URL editing, potentially causing the address bar to display internal reader:// URLs to users instead of the original webpage URL.

GT 片段：`@MainActor ⏎ private func cancelEditMode(windowUUID: WindowUUID) { ⏎ var url = tabManager(for: windowUUID).selectedTab?.url ⏎ if let currentURL = url {`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:485`，距錨點 0 行，候選管道 loc）cancelEditMode 中的 URL 判斷邏輯反轉，可能導致編輯模式取消時 URL 遺失

> 原本的條件是 `(currentURL.isWebPage() && !currentURL.isReaderModeURL)`，現在改為 `(currentURL.isWebPage() || currentURL.isReaderModeURL)`。這會讓非網頁 URL（例如 about:blank）或閱讀模式 URL 也被保留，可能導致取消編輯時工具列顯示錯誤的 URL。請確認此變更的意圖，並補充測試。

finding 片段：`url = (currentURL.isWebPage() || currentURL.isReaderModeURL) ? url : nil`

## base-1:firefox-ios-9:3|firefox-ios-9#2

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 0 行，候選管道 loc）isReaderModeEnabled 的布林值反轉，可能導致遙測記錄錯誤

> 原本 `case .available: true`、`default: false`，現在改為 `case .available: false`、`default: true`。這會讓閱讀模式按鈕的遙測事件記錄錯誤的啟用狀態。請確認此變更是否為筆誤，若不是，請提供對應的測試與說明。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## base-1:firefox-ios-9:4|firefox-ios-9#0

**GT**（rule）Missing private modifier on gleanWrapper

> The rule requires that properties have explicit access control modifiers with 'private' for implementation details. The gleanWrapper property lacks the 'private' modifier, exposing an internal implementation detail that should not be accessible outside the struct.

GT 片段：`struct ToolbarTelemetry { ⏎ let gleanWrapper: GleanWrapper ⏎ init(gleanWrapper: GleanWrapper = DefaultGleanWrapper()) { ⏎ self.gleanWrapper = gleanWrapper`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/ToolbarTelemetry.swift:9`，距錨點 0 行，候選管道 loc）gleanWrapper 屬性從 private 改為 internal，可能破壞封裝

> 將 `private let gleanWrapper` 改為 `let gleanWrapper` 會讓外部可以存取此屬性，可能不是必要的變更。如果只是為了測試，建議使用其他方式（例如依賴注入或測試專用的 init）。

finding 片段：`let gleanWrapper: GleanWrapper`

## base-1:prefect-1:1|prefect-1#1

**GT**（func）Incorrect deployment filtering breaks full-name matching

> The deployment filtering logic checks `dep.name not in deployment_names` instead of checking `full_name not in deployment_names`. This causes the filter to incorrectly evaluate when users specify deployment names in 'flow-name/deployment-name' format. When a user provides a full deployment name like 'my-flow/production', the code checks if 'production' (the short name) is in the list containing 'my-flow/production', which fails, causing the deployment to enter the fallback matching logic unnecessarily. This breaks the fast-path check and could lead to incorrect filtering behavior where deployments are included or excluded inappropriately.

GT 片段：`# If filtering by deployment name, check the full name matches ⏎ full_name = f"{flow_name}/{dep.name}" ⏎ if deployment_names and dep.name not in deployment_names: ⏎ # Only include if the full name matches (filter was by name parts)`

**finding**（`src/prefect/_sdk/fetcher.py:397`，距錨點 0 行，候選管道 loc）部署名稱過濾邏輯變更可能導致錯誤匹配

> 原本的過濾條件是 `full_name not in deployment_names`，現在改為 `dep.name not in deployment_names`。這會導致當使用者指定完整名稱（例如 `my-flow/production`）時，`dep.name` 只包含 `production`，因此永遠不會匹配，使得過濾失效。建議改回使用 `full_name` 進行比對，或同時檢查 `full_name` 和 `dep.name`。

finding 片段：`if deployment_names and dep.name not in deployment_names:`

## base-1:prefect-1:2|prefect-1#3

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行，候選管道 loc）移除 `strict=True` 可能掩蓋 zip 長度不匹配

> 原本使用 `zip(pool_names_list, results, strict=True)` 會在長度不一致時拋出 `ValueError`，現在移除 `strict=True` 後，若 `pool_names_list` 和 `results` 長度不同，多餘的元素會被靜默忽略，可能導致部分工作池未被處理且無任何警告。建議保留 `strict=True` 或手動檢查長度。

finding 片段：`for name, result in zip(pool_names_list, results):`

## base-1:prefect-1:3|prefect-1#2

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 0 行，候選管道 loc）簡化後的變數賦值可能引入型別不一致

> 原本檢查 `variables` 是否為 dict 後才賦值，現在直接賦值 `job_vars_schema = base_job_template["variables"]`。若 `variables` 不是 dict（例如是 list 或其他型別），後續使用 `job_vars_schema` 時可能發生型別錯誤。建議保留型別檢查或確保上游資料型別正確。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## base-1:prefect-1:3|prefect-1#3

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 37 行，候選管道 ident）簡化後的變數賦值可能引入型別不一致

> 原本檢查 `variables` 是否為 dict 後才賦值，現在直接賦值 `job_vars_schema = base_job_template["variables"]`。若 `variables` 不是 dict（例如是 list 或其他型別），後續使用 `job_vars_schema` 時可能發生型別錯誤。建議保留型別檢查或確保上游資料型別正確。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## base-1:prefect-10:1|prefect-10#0

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行，候選管道 loc）關閉 TypeScript strict 模式將大幅降低型別安全

> 將 `strict` 從 `true` 改為 `false` 會停用多項關鍵的型別檢查（如 `strictNullChecks`、`strictFunctionTypes` 等），可能導致未處理的 `null`/`undefined` 錯誤在編譯期無法被發現，增加 runtime 錯誤風險。此變更與 PR 的主要功能無關，且會影響整個專案的型別安全。建議恢復為 `true`，若有必要可針對特定檔案使用 `// @ts-ignore` 或調整型別定義，而非全域關閉。

finding 片段：`"strict": false,`

## base-1:prefect-10:2|prefect-10#1

**GT**（func）Empty lines not filtered in Expected Events textarea

> In the CustomTriggerFields component, the onChange handler for the Expected Events textarea fails to filter out empty or whitespace-only lines. When users press Enter multiple times or leave blank lines between events, these empty strings are included in the events array sent to the trigger configuration. This will cause backend validation failures or create malformed automation triggers that expect empty event names, leading to automations that never fire correctly.

GT 片段：`onChange={(e) => { ⏎ const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined); ⏎ }}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38`，距錨點 0 行，候選管道 loc）Expected Events 欄位可能將空陣列轉換為 undefined

> 在 `onChange` 中，當使用者清空 textarea 時，`e.target.value.split("\n")` 會得到 `[""]`，`lines.length > 0` 為 true，因此 `field.onChange([""])` 會將值設為包含一個空字串的陣列，而非預期的 `undefined` 或空陣列。這可能導致表單驗證或後續處理出現非預期行為。建議改為：`const lines = e.target.value.split("\n").filter(line => line.trim() !== ""); field.onChange(lines.length > 0 ? lines : undefined);`

finding 片段：`const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined);`

## base-1:prefect-10:3|prefect-10#3

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行，候選管道 loc）Threshold 欄位使用 parseInt 而非 Number，可能導致非預期結果

> `parseInt(e.target.value)` 會將輸入轉為整數，若使用者輸入小數（如 1.5）會被截斷為 1，且若輸入為空字串或非數字字串，`parseInt` 會回傳 `NaN`，可能導致表單驗證失敗或提交錯誤資料。其他元件（如 `custom-trigger-fields.tsx`）使用 `Number(e.target.value)`，行為較一致且能正確處理小數。建議改為 `Number(e.target.value)`。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## base-1:prefect-10:4|prefect-10#2

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 0 行，候選管道 loc）Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證

> 當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## base-1:prefect-10:4|prefect-10#5

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 3 行，候選管道 loc）Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證

> 當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## base-1:prefect-11:2|prefect-11#1

**GT**（func）Race condition: semaphore initialized after clients during startup

> The `_startup_event_semaphore` is initialized after the orchestration and events clients are created and started. This creates a race condition where Kubernetes pods detected during the client startup phase can trigger `_replicate_pod_event` calls before the semaphore exists. When `event_type` is `None` (startup scenario), the code checks `if _startup_event_semaphore is None` and raises a RuntimeError. However, pods may be detected immediately after clients start but before the semaphore initialization completes, causing the observer to crash with 'Startup event semaphore not initialized' errors during high pod count scenarios.

GT 片段：`@kopf.on.startup() ⏎ async def initialize_clients(logger: kopf.Logger, **kwargs: Any): ⏎ logger.info("Initializing clients") ⏎ global events_client`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:63`，距錨點 0 行，候選管道 loc）Semaphore 初始化可能失敗或未涵蓋所有啟動路徑

> `_startup_event_semaphore` 在 `initialize_clients` 中初始化，但若該函式未被呼叫或初始化失敗，後續 `_replicate_pod_event` 會拋出 `RuntimeError`。此外，若 `settings.observer.startup_event_concurrency` 為 0 或負數，`asyncio.Semaphore` 會拋出 `ValueError`，導致啟動失敗。建議在初始化時驗證設定值，並考慮提供預設值或 fallback。

finding 片段：`_startup_event_semaphore = asyncio.Semaphore( ⏎ settings.observer.startup_event_concurrency ⏎ )`

## base-1:prefect-11:3|prefect-11#2

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:132`，距錨點 5 行，候選管道 loc）Semaphore 未初始化時拋出 RuntimeError 可能中斷事件處理

> 在 `_replicate_pod_event` 中，若 `_startup_event_semaphore` 為 `None`，會拋出 `RuntimeError`。這可能發生在 `initialize_clients` 尚未完成或未呼叫時，導致 kopf handler 失敗並可能影響整個 observer 的穩定性。建議改為記錄警告並跳過 semaphore 限制，或確保初始化順序。

finding 片段：`if _startup_event_semaphore is None: ⏎ raise RuntimeError("Startup event semaphore not initialized")`

## base-1:prefect-11:4|prefect-11#2

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:129`，距錨點 8 行，候選管道 ident）Semaphore 僅在 event_type 為 None 時使用，可能無法涵蓋所有啟動事件

> Semaphore 僅在 `event_type is None` 的分支中使用，但啟動時可能還有其他事件類型（如 `ADDED`）也需要限制並發。若啟動時大量 `ADDED` 事件同時觸發，仍可能造成 API 過載。建議確認啟動期間所有事件類型都應受 semaphore 限制。

finding 片段：`if event_type is None: ⏎ if orchestration_client is None: ⏎ raise RuntimeError("Orchestration client not initialized") ⏎ if _startup_event_semaphore is None:`

## base-1:prefect-12:3|prefect-12#1

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行，候選管道 loc）使用 `||` 處理數字 0 會錯誤顯示 'None'

> 在顯示 `run_count` 時使用 `taskRun.run_count || 0`，若 `run_count` 為 0（合法值），則會顯示 0，但若 `run_count` 為 null 或 undefined，也會顯示 0，可能無法區分。建議使用 `??` 運算子：`taskRun.run_count ?? 0`。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## base-1:prefect-13:1|prefect-13#2

**GT**（func）Removed HTML5 min validation from concurrency limit input

> The concurrency limit input field previously had `min={0}` attribute (HTML5 validation) to prevent negative numbers from being entered. This attribute was removed in this PR change. While the Zod schema still validates that the value must be >= 0, users now lose immediate feedback when trying to enter negative values. They can type a negative number like `-5` and only discover it's invalid after clicking Save, rather than being prevented from entering it in the first place. This degrades the user experience by removing client-side validation that provides instant feedback.

GT 片段：`<Input ⏎ {...field} ⏎ type="number" ⏎ placeholder="Unlimited"`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112`，距錨點 0 行，候選管道 loc）並行限制輸入未驗證，可能送出負數或非整數值

> 在 `onChange` 中直接將輸入轉為 `Number`，但未檢查是否為有效整數或正數。若使用者輸入 `-5` 或 `2.5`，表單會接受並在提交時送出，可能導致 API 錯誤或非預期的行為。建議在 zod schema 中加入 `.int().positive()` 驗證，或在 `onChange` 中過濾無效值。

finding 片段：`onChange={(e) => { ⏎ const value = e.target.value; ⏎ field.onChange(value === "" ? null : Number(value)); ⏎ }}`

## base-1:prefect-13:2|prefect-13#1

**GT**（func）Description field incorrectly trims whitespace

> The work pool edit form now calls .trim() on the description before saving (line 42). This removes any intentional leading or trailing whitespace that users may want to preserve in their work pool descriptions, such as indented text or formatting for markdown. The original PR correctly converted empty strings to null using `||`, but the added .trim() operation inappropriately modifies user input. This breaks the principle of preserving user data as-is unless there's a specific business requirement.

GT 片段：`const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool( ⏎ { ⏎ name: workPool.name,`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:41`，距錨點 1 行，候選管道 loc）表單提交時未檢查欄位是否變更，可能造成不必要的 API 呼叫

> 即使使用者未修改任何欄位，點擊 Save 仍會呼叫 `updateWorkPool`。這可能導致不必要的網路請求，並在 API 端產生無意義的更新。建議使用 `form.formState.isDirty` 來判斷是否真的需要提交，或在提交前比較初始值。

finding 片段：`const handleSubmit = (data: WorkPoolEditFormValues) => { ⏎ const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool(`

## base-1:prefect-2:1|prefect-2#2

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:202`，距錨點 0 行，候選管道 loc）fail 方法中 action.triggered 事件的 related 指派錯誤

> 在 `fail` 方法中，建立 `prefect.automation.action.triggered` 事件時，`related` 參數被指派為 `self._resulting_related_resources`，而非包含 triggering-event 和 automation-triggered-event 的 `related_resources`。這會導致 action.triggered 事件缺少應有的相關資源，破壞事件追蹤鏈。

失敗情境：當 action 失敗時，發出的 `prefect.automation.action.triggered` 事件將不包含任何相關資源，使用者無法從該事件追溯到觸發事件或 automation.triggered 事件。

建議修法：將該事件的 `related` 參數改為 `related_resources`。

finding 片段：`related=self._resulting_related_resources,`

## base-1:prefect-2:2|prefect-2#0

**GT**（rule）Cross-field validation uses field validator

> The rule requires cross-field validation to use @model_validator decorator, but the code uses @field_validator which accesses unvalidated fields via info.data, causing order-dependent validation issues

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行，候選管道 loc）欄位驗證器依賴欄位順序，可能因未來調整而失效

> `validate_automation_triggered_event_id` 驗證器使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 僅包含已驗證的欄位，因此若 `triggering_event` 欄位在 `automation_triggered_event_id` 之後定義，驗證器將無法取得其值，導致驗證失效。

失敗情境：若未來有人調整欄位順序，將 `triggering_event` 移到 `automation_triggered_event_id` 之後，則即使 `triggering_event` 為 None，驗證器也不會拋出錯誤，允許不一致的資料。

建議修法：改用 `model_validator` 或在驗證器中直接從 `info.data` 以外的來源取得 `triggering_event`，或使用 `@model_validator(mode='after')` 進行跨欄位驗證。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## base-1:prefect-2:2|prefect-2#3

**GT**（func）Validation incorrectly rejects proactive triggers with automation_triggered_event_id

> The field_validator for automation_triggered_event_id prevents setting this field when triggering_event is None. However, proactive triggers (which have no triggering_event) still create automation.triggered events and need to link actions to them via automation_triggered_event_id. The code in triggers.py sets automation_triggered_event_id=primary_state_change_event_id for all actions including proactive triggers, causing Pydantic validation to fail at runtime. This breaks all proactive automations, which is a critical functional regression.

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行，候選管道 loc）欄位驗證器依賴欄位順序，可能因未來調整而失效

> `validate_automation_triggered_event_id` 驗證器使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 僅包含已驗證的欄位，因此若 `triggering_event` 欄位在 `automation_triggered_event_id` 之後定義，驗證器將無法取得其值，導致驗證失效。

失敗情境：若未來有人調整欄位順序，將 `triggering_event` 移到 `automation_triggered_event_id` 之後，則即使 `triggering_event` 為 None，驗證器也不會拋出錯誤，允許不一致的資料。

建議修法：改用 `model_validator` 或在驗證器中直接從 `info.data` 以外的來源取得 `triggering_event`，或使用 `@model_validator(mode='after')` 進行跨欄位驗證。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## base-1:prefect-3:1|prefect-3#1

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 0 行，候選管道 loc）拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## base-1:prefect-3:1|prefect-3#2

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 13 行，候選管道 ident）拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## base-1:prefect-3:2|prefect-3#1

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行，候選管道 ident）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## base-1:prefect-3:2|prefect-3#2

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行，候選管道 loc）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## base-1:prefect-4:1|prefect-4#0

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73`，距錨點 2 行，候選管道 loc）客戶端過濾可能導致已選取的區塊文件無法顯示

> `filteredData` 使用 `deferredSearch` 進行客戶端過濾，但 `selectedBlockDocument` 是從 `filteredData` 中尋找。若使用者選取了一個區塊文件後，輸入的搜尋字串與該文件名稱不符，則 `selectedBlockDocument` 會變成 `undefined`，導致觸發器顯示「Select a block...」而非已選取的名稱。

**失敗情境**：使用者選取了名為 `my_block_0` 的區塊文件，然後在搜尋框中輸入 `xyz`，此時 `filteredData` 為空，`selectedBlockDocument` 為 `undefined`，觸發器顯示佔位文字，但實際上仍有選取值。

**建議**：`selectedBlockDocument` 應從原始 `data` 中尋找，而非 `filteredData`。

finding 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

## base-1:prefect-4:1|prefect-4#1

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:73`，距錨點 0 行，候選管道 loc）客戶端過濾可能導致已選取的區塊文件無法顯示

> `filteredData` 使用 `deferredSearch` 進行客戶端過濾，但 `selectedBlockDocument` 是從 `filteredData` 中尋找。若使用者選取了一個區塊文件後，輸入的搜尋字串與該文件名稱不符，則 `selectedBlockDocument` 會變成 `undefined`，導致觸發器顯示「Select a block...」而非已選取的名稱。

**失敗情境**：使用者選取了名為 `my_block_0` 的區塊文件，然後在搜尋框中輸入 `xyz`，此時 `filteredData` 為空，`selectedBlockDocument` 為 `undefined`，觸發器顯示佔位文字，但實際上仍有選取值。

**建議**：`selectedBlockDocument` 應從原始 `data` 中尋找，而非 `filteredData`。

finding 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

## base-1:prefect-4:3|prefect-4#3

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:179`，距錨點 2 行，候選管道 loc）錯誤處理中重複的錯誤訊息與不必要的 console.error

> 在 `onError` 回呼中，錯誤訊息被設定為固定的「Unknown error while creating block.」，並使用 `console.error` 記錄。這可能導致使用者看到不明確的錯誤訊息，且開發者難以從日誌中區分錯誤來源。

**建議**：使用 `err.message` 或伺服器回傳的錯誤訊息來提供更具體的錯誤資訊，並考慮使用結構化日誌。

finding 片段：`onError: (err) => { ⏎ const message = "Unknown error while creating block."; ⏎ toast.error(message); ⏎ console.error(message, err);`

## base-1:prefect-4:4|prefect-4#0

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行，候選管道 loc）搜尋過濾同時在伺服器端與客戶端進行，可能導致不一致

> 查詢參數中已包含 `name: { like_: deferredSearch }`，但又在客戶端使用 `filteredData` 進行過濾。這可能導致不必要的客戶端計算，且若伺服器端過濾邏輯與客戶端不同（例如大小寫處理），可能出現不一致的結果。

**建議**：移除客戶端過濾，完全依賴伺服器端過濾，或確保兩者邏輯一致。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## base-1:prefect-4:4|prefect-4#1

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 6 行，候選管道 ident）搜尋過濾同時在伺服器端與客戶端進行，可能導致不一致

> 查詢參數中已包含 `name: { like_: deferredSearch }`，但又在客戶端使用 `filteredData` 進行過濾。這可能導致不必要的客戶端計算，且若伺服器端過濾邏輯與客戶端不同（例如大小寫處理），可能出現不一致的結果。

**建議**：移除客戶端過濾，完全依賴伺服器端過濾，或確保兩者邏輯一致。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## base-1:prefect-5:1|prefect-5#0

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行，候選管道 ident）bucket_folder 檢查過於寬鬆，可能跳過必要的前綴處理

> 在 `_resolve_path` 中，使用 `if self.bucket_folder and self.bucket_folder in path:` 來判斷路徑是否已包含 bucket_folder。這個檢查只要路徑中任何位置出現 bucket_folder 字串就會成立，即使 bucket_folder 出現在路徑中間或檔名中，也會錯誤地直接返回原始路徑，導致最終儲存路徑缺少必要的前綴。

例如，若 bucket_folder 為 `results/`，而傳入路徑為 `myresults/file.txt`，則 `self.bucket_folder in path` 為 True，函式會直接返回 `myresults/file.txt`，但正確行為應是加上前綴成為 `results/myresults/file.txt`。

建議改為檢查路徑是否以 bucket_folder 開頭（例如使用 `path.startswith(self.bucket_folder)`），或使用 `PurePosixPath` 進行更精確的比對。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-1:prefect-5:1|prefect-5#1

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行，候選管道 loc）bucket_folder 檢查過於寬鬆，可能跳過必要的前綴處理

> 在 `_resolve_path` 中，使用 `if self.bucket_folder and self.bucket_folder in path:` 來判斷路徑是否已包含 bucket_folder。這個檢查只要路徑中任何位置出現 bucket_folder 字串就會成立，即使 bucket_folder 出現在路徑中間或檔名中，也會錯誤地直接返回原始路徑，導致最終儲存路徑缺少必要的前綴。

例如，若 bucket_folder 為 `results/`，而傳入路徑為 `myresults/file.txt`，則 `self.bucket_folder in path` 為 True，函式會直接返回 `myresults/file.txt`，但正確行為應是加上前綴成為 `results/myresults/file.txt`。

建議改為檢查路徑是否以 bucket_folder 開頭（例如使用 `path.startswith(self.bucket_folder)`），或使用 `PurePosixPath` 進行更精確的比對。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## base-1:prefect-5:2|prefect-5#0

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 0 行，候選管道 loc）跨欄位驗證誤用 field_validator，可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中，試圖透過 `info.data.get("bucket")` 取得 bucket 欄位值來進行跨欄位驗證。但此驗證器是 `field_validator`，在驗證 bucket_folder 時，bucket 欄位可能尚未被驗證或設定，因此 `info.data` 中可能沒有 bucket 的值，導致驗證永遠不會觸發。

應改用 `model_validator` 來進行跨欄位驗證，確保所有欄位都已就緒。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## base-1:prefect-5:2|prefect-5#1

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 23 行，候選管道 ident）跨欄位驗證誤用 field_validator，可能無法取得 bucket 值

> 在 `_bucket_folder_suffix` 中，試圖透過 `info.data.get("bucket")` 取得 bucket 欄位值來進行跨欄位驗證。但此驗證器是 `field_validator`，在驗證 bucket_folder 時，bucket 欄位可能尚未被驗證或設定，因此 `info.data` 中可能沒有 bucket 的值，導致驗證永遠不會觸發。

應改用 `model_validator` 來進行跨欄位驗證，確保所有欄位都已就緒。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## base-1:prefect-5:3|prefect-5#2

**GT**（func）Incorrect parameter name prevents timeout configuration in test harness

> The test fixture uses `server_timeout=60` when calling `prefect_test_harness()`, but the correct parameter name is `server_startup_timeout`. This means the intended 60-second timeout is not actually applied, leaving tests vulnerable to the same timeout issues in CI environments that the change was meant to fix. The prefect_test_harness function will ignore the invalid parameter and use its default timeout value instead, potentially causing intermittent test failures when multiple xdist workers start simultaneously in CI.

GT 片段：`# Increase timeout for CI environments where multiple xdist workers ⏎ # start servers simultaneously, which can be slower on Python 3.11+ ⏎ # See https://github.com/PrefectHQ/prefect/issues/16397 ⏎ with prefect_test_harness(server_timeout=60):`

**finding**（`src/integrations/prefect-gcp/tests/conftest.py:19`，距錨點 0 行，候選管道 loc）移除 disable_logging fixture 可能導致測試輸出過多

> 原本的 `disable_logging` fixture 會暫時關閉 logging to API，避免測試時產生過多 log。移除後，測試期間可能會輸出大量 log，影響測試可讀性與效能。若這是為了簡化設定，建議確認是否有其他機制控制 log，否則應保留此 fixture。

finding 片段：`with prefect_test_harness(server_timeout=60): ⏎ yield`

## base-1:prefect-6:3|prefect-6#1

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:133`，距錨點 14 行，候選管道 ident）`get_or_create_client` 可能建立非預期的 client

> 原本使用 `@inject_client` 裝飾器，會根據上下文注入 client，若未提供則建立新的 client。現在改為 `get_or_create_client(client)`，其行為可能不同：若 `client` 為 None，它會建立一個新的 client，但可能未正確處理與目前執行中 flow run 的關聯（例如使用相同的 API URL 或認證）。這可能導致在 flow 內呼叫時無法正確連結父子關係。

建議：確認 `get_or_create_client` 的實作是否符合預期，或保留原本的 `@inject_client` 機制。

finding 片段：`client, _ = get_or_create_client(client)`

## base-1:prefect-6:4|prefect-6#1

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:149`，距錨點 0 行，候選管道 loc）`collect_task_run_inputs` 改為同步呼叫可能阻塞事件迴圈

> 原本 `await collect_task_run_inputs(v)` 是非同步呼叫，現在改為 `collect_task_run_inputs(v)` 同步呼叫。若該函式內部有 I/O 或耗時操作，會阻塞事件迴圈，影響效能。

建議：確認 `collect_task_run_inputs` 是否為非同步函式，若是則應保留 `await`。

finding 片段：`k: collect_task_run_inputs(v) for k, v in parameters.items()`

## base-1:prefect-6:5|prefect-6#2

**GT**（func）Wrong variable used for deployment ID in flow run creation

> On line 212, the function passes `deployment_id` to `create_flow_run_from_deployment()`, but this variable can be `None` when the deployment is looked up by name (line 138). In that case, only the `deployment` object has the actual ID via `deployment.id`. The API method requires a valid UUID, so passing `None` will cause an API error. The correct usage is `deployment.id` (as shown in the original PR), which is guaranteed to have a value after the deployment lookup succeeds.

GT 片段：`flow_run = await client.create_flow_run_from_deployment( ⏎ deployment_id, ⏎ parameters=parameters, ⏎ state=Scheduled(scheduled_time=scheduled_time),`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 0 行，候選管道 loc）使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤

> 原本 `client.create_flow_run_from_deployment(deployment.id, ...)` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如從名稱解析而來），而 API 期望 UUID，可能導致型別錯誤。

建議：確認 `deployment_id` 的型別，必要時轉換為 UUID。

finding 片段：`deployment_id,`

## base-1:prefect-6:5|prefect-6#3

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 17 行，候選管道 ident）使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤

> 原本 `client.create_flow_run_from_deployment(deployment.id, ...)` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如從名稱解析而來），而 API 期望 UUID，可能導致型別錯誤。

建議：確認 `deployment_id` 的型別，必要時轉換為 UUID。

finding 片段：`deployment_id,`

## base-1:prefect-7:1|prefect-7#1

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:42`，距錨點 0 行，候選管道 loc）使用 Python hash 作為 advisory lock key 不穩定

> `hash(str(trigger.id))` 的結果在每次 Python 程序啟動時都可能不同（因為 hash 隨機化），這會導致不同 worker 對同一個 trigger 計算出不同的 lock key，使得 advisory lock 無法正確序列化，競態條件仍然存在。建議改用 UUID 的整數表示（例如 `trigger.id.int`）並截斷至 63 位元，以確保跨程序一致。

finding 片段：`lock_key = hash(str(trigger.id)) % (2**63)`

## base-1:prefect-7:2|prefect-7#1

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:46`，距錨點 2 行，候選管道 loc）SQLite 上完全沒有鎖保護，競態仍可能發生

> 在 SQLite 上，`acquire_composite_trigger_lock` 直接返回，沒有取得任何鎖。雖然 SQLite 的寫入序列化可能降低機率，但讀取與寫入之間仍可能交錯，導致兩個 worker 都讀到相同的 child firings 並各自嘗試刪除，最終只有一個成功，但另一個可能已經通過檢查並觸發父觸發器。建議對 SQLite 使用其他機制（例如樂觀鎖或應用層級的鎖）。

finding 片段：`# SQLite doesn't support advisory locks, but SQLite also serializes writes ⏎ # at the database level, so the race condition is less likely to occur`

## base-1:prefect-7:3|prefect-7#2

**GT**（func）Race detection compares lengths instead of ID sets allowing double-firing

> The race detection logic compares only the count of deleted IDs rather than verifying the exact set of IDs match. This comparison using len(deleted_ids) != len(firing_ids) will incorrectly pass when a worker deletes the same number of firings but with different IDs than expected. For example, if firing_ids is {A, B} but deleted_ids is {C, D}, both have length 2 so the check passes and the trigger fires incorrectly. The correct implementation should use set equality (deleted_ids != firing_ids) to ensure the exact same firings were claimed, preventing spurious trigger firings when workers race.

GT 片段：`# Clear by firing id, and only proceed if we won the race to claim them. ⏎ # This prevents double-firing when multiple workers evaluate concurrently. ⏎ deleted_ids = await clear_child_firings( ⏎ session, trigger, firing_ids=list(firing_ids)`

**finding**（`src/prefect/server/events/triggers.py:396`，距錨點 0 行，候選管道 loc）刪除數量檢查可能因重複 firing_ids 而誤判

> `firing_ids` 可能包含重複的 ID（例如同一個 child firing 被多次加入），但 `clear_child_firings` 回傳的是實際刪除的 ID 集合，其長度可能小於 `firing_ids` 的長度，導致誤判為競態而跳過觸發。建議先對 `firing_ids` 去重，或比較集合而非長度。

finding 片段：`if len(deleted_ids) != len(firing_ids):`

## base-1:prefect-8:1|prefect-8#1

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:462`，距錨點 0 行，候選管道 model_line）V2 啟用時 static_subpath 指派錯誤

> 在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`static_subpath` 被指派為 `prefect.__ui_static_subpath__`（V1 的子路徑），而 `source_static_path` 為 `prefect.__ui_v2_static_path__`。這導致後續 `create_ui_static_subpath` 會將 V2 的靜態檔案複製到 V1 的子路徑，可能覆蓋 V1 檔案或造成路徑衝突。應將 `static_subpath` 指派為 `prefect.__ui_v2_static_subpath__`。

finding 片段：`static_subpath = prefect.__ui_static_subpath__`

## base-1:prefect-8:3|prefect-8#0

**GT**（rule）Direct logging.getLogger() call used

> The rule requires loggers to be instantiated using the pattern `logger: "logging.Logger" = get_logger("module_name")` instead of direct `logging.getLogger()` calls

GT 片段：`# Log which UI version is being served ⏎ if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

**finding**（`src/prefect/server/api/server.py:532`，距錨點 0 行，候選管道 loc）日誌訊息未使用結構化格式

> 新增的日誌訊息 `Serving experimental V2 UI` 使用 f-string 或直接字串，未包含結構化欄位（如 UI 版本），不利於日誌分析。建議使用結構化日誌或至少包含版本資訊。

finding 片段：`ui_logger.info("Serving experimental V2 UI")`

## base-1:prefect-9:1|prefect-9#2

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行，候選管道 loc）缺少 error boundary 處理查詢失敗

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有 error boundary 包覆，錯誤會向上傳播並可能導致整個應用程式崩潰。建議在元件外層或路由層級加入 error boundary，並提供 fallback UI。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## base-1:prefect-9:2|prefect-9#1

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行，候選管道 loc）stories 中 queryClient 設定不一致

> 在 `createTestRouter` 中建立了一個新的 `QueryClient` 並放入 router context，但 decorator 中使用的 `QueryClientProvider` 是全域的 `queryClient`。這可能導致測試時 query client 不一致，建議統一使用同一個 instance。

finding 片段：`context: { queryClient: new QueryClient() },`

## base-1:redis-1:1|redis-1#2

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:914`，距錨點 0 行，候選管道 loc）dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找可能失敗

> 在 dictSetKeyAtLink 中，當 newItem=0 且 *link 為 NULL 時，程式碼使用 addedKey 呼叫 dictFindLink。但 addedKey 是經過 keyDup 處理後的鍵，可能與原始 key 不同（例如 keyDup 可能複製或轉換鍵）。如果 dictFindLink 使用 addedKey 找不到對應的 entry，則會觸發 assert(*link != NULL) 失敗。

失敗情境：當 dictType.keyDup 非 NULL 且會改變鍵的內容（例如複製 sds 或進行其他轉換），且呼叫者傳入的 key 與儲存的鍵不同時，dictFindLink 將無法找到 entry。

建議：應使用原始 key（或 dictStoredKey2Key(d, key)）進行查找，而不是 addedKey。

finding 片段：`*link = dictFindLink(d, addedKey, NULL);`

## base-1:redis-1:2|redis-1#0

**GT**（rule）Test function missing REDIS_TEST wrapper

> The rule requires that all test functions and test-specific code in source files must be enclosed within #ifdef REDIS_TEST / #endif blocks, but the validateStoredKeyConversion function is a test/validation function that exists without the required preprocessor wrapper

GT 片段：`/* Validate that stored-key to key conversion works correctly */ ⏎ static int validateStoredKeyConversion(dict *d, const void *key __stored_key) { ⏎ const void *extracted = dictStoredKey2Key(d, key); ⏎ if (d->type->keyFromStoredKey) {`

**finding**（`src/dict.c:102`，距錨點 0 行，候選管道 loc）validateStoredKeyConversion 函式未被使用

> 新增的 validateStoredKeyConversion 函式在整個 diff 中沒有被呼叫。這可能是未完成的功能或遺留的除錯程式碼。

建議：如果不需要，應移除此函式；如果需要，應在適當的地方呼叫它。

finding 片段：`static int validateStoredKeyConversion(dict *d, const void *key __stored_key) {`

## base-1:redis-2:2|redis-2#2

**GT**（func）Memory leak due to missing error message reply to client

> In parseSlotRangesOrReply, when slot range validation fails, the error message allocated by slotRangeArrayNormalizeAndValidate is freed with sdsfree(err) but never sent to the client via addReplyErrorSds. This causes two problems: the client receives no error message explaining why their command failed, making debugging difficult, and it breaks the expected behavior where addReplyErrorSds transfers ownership of the sds string. The original PR intended to always send validation errors to the client for proper error reporting.

GT 片段：`sds err = NULL; ⏎ if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err); ⏎ slotRangeArrayFree(slots);`

**finding**（`src/cluster.c:2015`，距錨點 0 行，候選管道 loc）驗證失敗時未回覆錯誤給客戶端

> 在 `parseSlotRangesOrReply` 中，原本驗證失敗時會呼叫 `addReplyErrorSds(c, err)` 將錯誤訊息回覆給客戶端，但修改後只呼叫 `sdsfree(err)` 釋放錯誤訊息，卻未回覆任何錯誤。這會導致客戶端在提供無效 slot range 時收到空回覆或逾時，而非明確的錯誤訊息。

建議：
- 在釋放 `err` 之前，先呼叫 `addReplyErrorSds(c, err)` 回覆錯誤。
- 或者，若 `err` 為 NULL，則回覆一個通用的錯誤訊息。

finding 片段：`if (slotRangeArrayNormalizeAndValidate(slots, &err) != C_OK) { ⏎ sdsfree(err);`

## base-1:redis-2:3|redis-2#0

**GT**（rule）Unused variable causes compilation warning

> The rule requires that compilation completes successfully with no warnings when -Werror flag is enabled. The code contains an unused variable 'total_ranges' that triggers a compilation warning.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1012`，距錨點 0 行，候選管道 loc）`asmCountKeysInSlots` 可能造成大量迴圈與效能問題

> `asmCountKeysInSlots` 會針對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slot（例如整個 hash slot 空間 0-16383），則會執行 16384 次函式呼叫。雖然 `kvstoreDictSize` 本身可能只是 O(1) 的查詢，但大量的函式呼叫仍可能造成不必要的效能負擔，特別是在日誌記錄或任務啟動時頻繁呼叫。

建議：
- 評估是否有更有效率的方式取得 key 數量，例如直接從 `kvstore` 取得總數，或使用批次 API。
- 若無法避免，考慮加入快取或限制呼叫頻率。

finding 片段：`unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎  ⏎ unsigned long long key_count = 0;`

## base-1:redis-2:3|redis-2#6

**GT**（rule）Non-static internal helper function exported as global symbol

> asmCountKeysInSlots is introduced as a file-local helper (not declared in any header and used only within src/cluster_asm.c in this diff), but it is declared without the 'static' keyword, making it globally visible and violating the encapsulation rule for internal helpers.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1012`，距錨點 0 行，候選管道 loc）`asmCountKeysInSlots` 可能造成大量迴圈與效能問題

> `asmCountKeysInSlots` 會針對每個 slot range 中的每個 slot 呼叫 `kvstoreDictSize`，若 slot range 涵蓋大量 slot（例如整個 hash slot 空間 0-16383），則會執行 16384 次函式呼叫。雖然 `kvstoreDictSize` 本身可能只是 O(1) 的查詢，但大量的函式呼叫仍可能造成不必要的效能負擔，特別是在日誌記錄或任務啟動時頻繁呼叫。

建議：
- 評估是否有更有效率的方式取得 key 數量，例如直接從 `kvstore` 取得總數，或使用批次 API。
- 若無法避免，考慮加入快取或限制呼叫頻率。

finding 片段：`unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎  ⏎ unsigned long long key_count = 0;`

## base-1:redis-2:5|redis-2#1

**GT**（func）Incorrect comparison logic causes false negatives when comparing slot ranges

> The slotRangeArrayIsEqual function checks if the number of ranges are equal before normalizing and merging adjacent ranges. This causes the function to incorrectly return false (0) when comparing two slot range arrays that represent the same slots but have different numbers of ranges before merging. For example, comparing [1000-1001, 1002-1003] (2 ranges) with [1000-1003] (1 range) will return false even though they represent the same slots after merging. This breaks the task lookup functionality in asmLookupTaskBySlotRangeArray, preventing correct task identification when slot ranges are specified in different but equivalent formats.

GT 片段：`int slotRangeArrayIsEqual(slotRangeArray *slots1, slotRangeArray *slots2) { ⏎ if (slots1->num_ranges != slots2->num_ranges) return 0; ⏎ slotRangeArraySortAndMerge(slots1); ⏎ slotRangeArraySortAndMerge(slots2);`

**finding**（`src/cluster.c:1855`，距錨點 21 行，候選管道 ident）`slotRangeArraySortAndMerge` 未處理重疊範圍

> 註解明確指出「Overlapping ranges are not merged.」，但若輸入包含重疊範圍（例如 100-200 和 150-250），合併後仍會保留兩個範圍，且後續的驗證會偵測到重疊並回報錯誤。這可能是預期行為，但建議在函式中明確處理或至少記錄此情況，以避免未來誤用。

finding 片段：`/* Sort slot ranges by start slot and merge adjacent ranges. ⏎ * Adjacent means: prev.end + 1 == next.start. ⏎ * e.g. 1000-2000 2001-3000 0-100  =>  0-100 1000-3000 ⏎ *`

## base-1:redis-3:1|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行，候選管道 loc）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## base-1:redis-3:1|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行，候選管道 loc）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## base-1:redis-3:2|redis-3#3

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行，候選管道 loc）slot 可能未初始化即被使用

> 在 `extractKeysAndSlot` 中，原本 `*slot` 會先被設為 `INVALID_CLUSTER_SLOT`，但修改後只有當 `num_keys > 0` 時才呼叫 `extractSlotFromKeysResult` 設定 `*slot`。若 `num_keys == 0`，`*slot` 將保持呼叫者傳入的值，可能導致未初始化變數被使用。

建議在函式開頭明確初始化 `*slot = INVALID_CLUSTER_SLOT`，或確保所有呼叫者都已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## base-1:redis-3:3|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-3:3|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）malloc 未檢查失敗

> `malloc` 可能回傳 NULL，但程式碼未檢查，後續寫入 `slot_buffer[j]` 會導致 NULL pointer dereference。

建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-3:4|redis-3#2

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行，候選管道 loc）條件判斷變更可能影響無 key 命令的處理

> 原本 `else if (num_keys > 0)` 只在有 key 時檢查 cross-slot，現在改為 `else if (num_keys >= 0)`，這會讓 `num_keys == 0` 的命令也進入檢查。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為無 key 命令不會有 cross-slot），則會設定錯誤。但更可能的是，原本 `num_keys == 0` 時會跳過此區塊，現在會執行，可能影響後續邏輯。

建議確認此變更是否必要，或改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

## base-1:redis-3:5|redis-3#0

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-3:5|redis-3#1

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行，候選管道 loc）slot_buffer 可能造成不必要的記憶體分配

> 原本的實作不需要額外記憶體，現在為了追蹤 slot 而分配 `slot_buffer`。雖然在 cross-slot 時可以釋放，但若所有 key 都在同一 slot，仍會分配並釋放記憶體。若此函式被頻繁呼叫，可能影響效能。

建議考慮是否真的需要此 buffer，或改用其他方式。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## base-1:redis-4:1|redis-4#0

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行，候選管道 loc）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## base-1:redis-4:1|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2138`，距錨點 8 行，候選管道 ident）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或洩漏

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 通常會追蹤記憶體使用量並在 OOM 時終止程式，而 malloc 不會。此外，若後續程式碼假設記憶體已初始化為零，則可能讀取到未定義內容。建議改回 zmalloc，或確認後續有完整初始化。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## base-1:redis-4:2|redis-4#2

**GT**（func）ASM cron runs before cluster state update causing stale state issues

> The serverCron() function now calls asmCron() before clusterCron(). This is problematic because clusterCron() contains the call to clusterUpdateState() which updates the cluster's operational state (CLUSTER_OK vs CLUSTER_FAIL). ASM (Atomic Slot Migration) operations depend on having an accurate view of the cluster state to make correct migration decisions. By executing asmCron() first, migration tasks may operate on stale cluster state information from the previous iteration, potentially leading to incorrect slot migration decisions, failed migrations, or data consistency issues during cluster rebalancing operations.

GT 片段：`if (server.cluster_enabled) { ⏎ asmCron(); ⏎ clusterCron(); ⏎ }`

**finding**（`src/server.c:1658`，距錨點 0 行，候選管道 loc）asmCron() 呼叫順序可能影響原子槽遷移

> 原本 asmCron() 在 clusterCron() 內部最後呼叫，現在移到 serverCron 中 clusterCron() 之前。若 asmCron 依賴 clusterCron 更新後的叢集狀態，順序變更可能導致行為錯誤。建議確認 asmCron 的相依性，或維持原本順序。

finding 片段：`asmCron(); ⏎ clusterCron();`

## base-1:redis-4:4|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 3 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## base-1:redis-4:4|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2153`，距錨點 0 行，候選管道 loc）clusterDeleteKeysInUnownedSlots 中未檢查 clusterIsMySlot 的例外情況

> 在 clusterDeleteKeysInUnownedSlots 中，條件 `!clusterIsMySlot(i)` 會跳過屬於自己的槽，但若槽正在遷出（migrating）且仍有本地 keys，是否應刪除？原邏輯中若槽屬於自己則保留，但遷出狀態下可能仍需處理。建議確認遷出狀態下的行為。

finding 片段：`if (!countKeysInSlot(i) || ⏎ clusterIsMySlot(i) || ⏎ getImportingSlotSource(i))`

## base-1:redis-4:5|redis-4#1

**GT**（func）Incorrect operation order causes potential data loss during cluster verification

> The verifyClusterConfigWithData() function executes clusterDeleteKeysInUnownedSlots() before clusterClaimUnassignedSlots(). This reverses the intended logic: the function should first claim ownership of unassigned slots that contain keys (preventing orphaned data), then delete keys from slots that are genuinely owned by other nodes. With this bug, keys in unassigned slots may be incorrectly deleted before the node has a chance to claim ownership, resulting in permanent data loss during cluster startup or recovery scenarios.

GT 片段：`/* Delete keys in unowned slots */ ⏎ clusterDeleteKeysInUnownedSlots(); ⏎ /* Take over slots that we have keys for, but are assigned to no one. */ ⏎ clusterClaimUnassignedSlots();`

**finding**（`src/cluster.c:2167`，距錨點 35 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-4:5|redis-4#3

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 17 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-4:5|redis-4#4

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2167`，距錨點 10 行，候選管道 ident）clusterDeleteKeysInUnownedSlots 中未保存配置變更

> 原 verifyClusterConfigWithData 在刪除 keys 後會呼叫 clusterSaveConfigOrDie(1) 保存配置，但新的 clusterDeleteKeysInUnownedSlots 沒有保存。若刪除 keys 後配置未變更，可能不需要保存，但若刪除動作影響了 slot 狀態，可能需要保存。建議確認。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## base-1:redis-5:1|redis-5#0

**GT**（rule）Direct malloc_usable_size instead of zmalloc_size

> The rule requires all memory operations to use Redis zmalloc wrappers (zmalloc_size) instead of direct libc functions (malloc_usable_size)

GT 片段：`/* All kv-objects has at least kvobj header and embedded key */ ⏎ size_t asize = malloc_usable_size((void *)o);`

**finding**（`src/object.c:1239`，距錨點 22 行，候選管道 ident）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:redis-5:1|redis-5#1

**GT**（func）Incorrect memory calculation for QUICKLIST due to wrong denominator

> In the QUICKLIST encoding branch, the average element size calculation uses `elesize/samples` instead of `elesize/elecount`. This divides the accumulated element size by the number of sampled nodes rather than the total element count in those nodes. Since `elecount` represents the sum of all `node->count` values (the actual number of elements), using `samples` (number of nodes) produces an incorrect average that doesn't represent the true per-element memory usage. This causes the MEMORY USAGE command to return wildly inaccurate values for quicklist-encoded lists.

GT 片段：`do { ⏎ elesize += sizeof(quicklistNode)+zmalloc_size(node->entry); ⏎ elecount += node->count; ⏎ samples++;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:redis-5:1|redis-5#4

**GT**（func）Unused variable 'elecount' causes build failure with -Werror

> The variable 'elecount' is declared and incremented in the QUICKLIST encoding branch (line 1236: 'elecount += node->count') but is never used after the PR changed the calculation from 'elesize/elecount' to 'elesize/samples'. This creates an unused-but-set variable which triggers compiler warnings under -Wall (enabled in Makefile) and causes build failures when compiling with -Werror flag. This violates AGENTS.MD Rule #4 which requires the codebase to compile without warnings when REDIS_CFLAGS="-Werror" is enabled.

GT 片段：`size_t elesize = 0, elecount = 0, samples = 0; ⏎ ... ⏎ if (o->encoding == OBJ_ENCODING_QUICKLIST) { ⏎ quicklist *ql = o->ptr;`

**finding**（`src/object.c:1239`，距錨點 0 行，候選管道 loc）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## base-1:redis-5:2|redis-5#2

**GT**（func）Variable shadowing breaks sampling consistency for STREAM objects

> A local `samples` variable is declared at line 1319 within the OBJ_STREAM branch, shadowing the outer `samples` variable declared at line 1214. This prevents the outer samples counter from being updated during stream memory calculation. While this doesn't break the stream calculation itself, it violates the function's sampling design pattern where the outer `samples` variable tracks total sampling across all object type branches. This inconsistency could lead to unexpected behavior if the function logic is modified to check or use the outer samples counter after processing.

GT 片段：`raxStart(&ri,s->rax); ⏎ raxSeek(&ri,"^",NULL,0); ⏎ size_t lpsize = 0; ⏎ size_t samples = 0;`

**finding**（`src/object.c:1330`，距錨點 10 行，候選管道 ident）stream 的 lpsize 計算可能多算最後一個 listpack

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## base-1:redis-5:2|redis-5#3

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行，候選管道 loc）stream 的 lpsize 計算可能多算最後一個 listpack

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)`，現在改為 `lpsize * s->rax->numele`。若 `lpsize` 是平均每個 listpack 的大小，且最後一個 listpack 可能未滿，則乘以 `numele` 會高估記憶體。建議確認此變更是否正確，或保留原本的 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## base-1:redis-6:1|redis-6#1

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行，候選管道 loc）active defrag 恢復邏輯可能錯誤地啟用 defrag

> 在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

finding 片段：`server.active_defrag_enabled = 1;`

## base-1:redis-6:1|redis-6#4

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行，候選管道 loc）active defrag 恢復邏輯可能錯誤地啟用 defrag

> 在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

finding 片段：`server.active_defrag_enabled = 1;`

## base-1:redis-6:2|redis-6#2

**GT**（func）Stream entries incorrectly marked as referenced when cgroups_ref is NULL

> When cgroups_ref is NULL (which occurs after DEBUG RELOAD with empty PEL), the function returns 1 indicating the entry IS referenced, when it should return 0 indicating it is NOT referenced. This inverted logic prevents XADD/XTRIM operations with the ACKED strategy from correctly deleting entries that have been fully acknowledged by all consumer groups. The result is a memory leak where stream entries accumulate unnecessarily because they are incorrectly protected from deletion even though no consumer group has them in their pending entry list.

GT 片段：`/* Check if the message is in any consumer group's PEL */ ⏎ if (!s->cgroups_ref) return 1; ⏎ unsigned char buf[sizeof(streamID)]; ⏎ streamEncodeID(buf, id);`

**finding**（`src/t_stream.c:2708`，距錨點 0 行，候選管道 loc）streamEntryIsReferenced 在 cgroups_ref 為 NULL 時回傳 1 可能導致記憶體洩漏或錯誤保留

> 新增的 `if (!s->cgroups_ref) return 1;` 會在沒有 consumer groups 時直接回傳 1，表示該 entry 被引用。這可能導致 stream 的 entry 無法被刪除，即使沒有 consumer group 引用它。

失敗情境：當 stream 沒有 consumer groups 時，呼叫 streamEntryIsReferenced 會回傳 1，使得呼叫者認為 entry 仍被引用，因此不會刪除它，可能造成記憶體洩漏或資料不一致。

建議：確認此處的意圖。若 cgroups_ref 為 NULL，應回傳 0（未被引用）而非 1。或者，應檢查呼叫者是否正確處理此情況。

finding 片段：`if (!s->cgroups_ref) return 1;`

## base-1:redis-6:3|redis-6#3

**GT**（func）Inverted reply discard logic causes test infrastructure failure

> The condition for discarding replies is inverted - replies are discarded when count is NOT a multiple of frequency (!=), rather than when it IS a multiple (==). This causes the test to read and discard replies at the wrong times, leading to a buffer overflow of unread replies. The discard_replies_every helper is called throughout the test suite after batches of Redis commands to prevent reply buffer buildup. With this bug, replies accumulate in the buffer instead of being cleared, causing test hangs or failures when the client tries to send new commands with a full reply buffer.

GT 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

**finding**（`tests/unit/memefficiency.tcl:70`，距錨點 0 行，候選管道 loc）discard_replies_every 函式參數名稱可能造成混淆

> 函式 `discard_replies_every` 的參數 `frequency` 和 `discard_num` 的語意不夠清晰。`frequency` 代表每多少次觸發一次丟棄，`discard_num` 代表每次丟棄的數量。但呼叫時傳入的數值可能與預期不符，例如在 lpush 的測試中，原本每次丟棄 20000 個 replies，但函式呼叫為 `discard_replies_every $rd $count 10000 20000`，這表示每 10000 次丟棄 20000 個 replies，與原本邏輯相同，但可讀性較差。

建議：考慮重新命名參數或加入註解，以提升可讀性。

finding 片段：`proc discard_replies_every {rd count frequency discard_num} {`

## base-1:redis-7:1|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1722`，距錨點 5 行，候選管道 model_line）AOF_BROKEN_RECOVERED 在非最後一個檔案時未正確處理，可能導致資料不一致

> 在 loadAppendOnlyFiles 中，當 ret == AOF_BROKEN_RECOVERED 且 !last_file 時，程式碼將 ret 設為 AOF_FAILED 並記錄錯誤，但隨後在 if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) 的條件中，因為 ret 已被改為 AOF_FAILED，所以會進入 cleanup 並中止載入。然而，此處的邏輯有問題：如果 AOF_BROKEN_RECOVERED 發生在非最後一個檔案，實際上檔案已被 truncate 修改，但後續的檔案仍可能被載入，導致資料不一致。建議在非最後一個檔案遇到 AOF_BROKEN_RECOVERED 時，應立即中止載入並回報錯誤，且不應修改原始檔案。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## base-1:redis-7:3|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行，候選管道 loc）自動截斷可能造成資料遺失，且未提供足夠的警告或備份機制

> 當 aof-load-broken 啟用且損壞部分小於 max-size 時，程式會直接 truncate 檔案，丟棄損壞部分之後的所有資料。這可能導致資料遺失，且僅記錄 warning。建議在 truncate 前先將原始檔案備份（例如複製一份），或至少提供更明確的警告，讓使用者知道有多少資料被丟棄。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## base-1:redis-7:4|redis-7#1

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行，候選管道 ident）truncate 後未更新 AOF 檔案大小相關的狀態

> truncate 成功後，程式僅將檔案描述子 seek 到結尾，但未更新 server 中可能記錄的 AOF 檔案大小或 offset 等狀態。這可能導致後續 AOF 寫入時發生錯誤或覆蓋。建議檢查是否有相關狀態需要更新。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## base-1:redis-8:1|redis-8#1

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行，候選管道 loc）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:1|redis-8#3

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2306`，距錨點 3 行，候選管道 loc）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:1|redis-8#4

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2306`，距錨點 0 行，候選管道 loc）argv 陣列大小不足，寫入 6 個元素導致堆疊緩衝區溢位

> 在 hincrbyfloatCommand 中，宣告 `robj *argv[5];` 但隨後寫入 `argv[0]` 到 `argv[5]` 共 6 個元素，造成陣列越界寫入。這會破壞堆疊上的其他變數，可能導致程式崩潰或任意程式碼執行。

建議將陣列大小改為 6：
```c
robj *argv[6];
```

finding 片段：`robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1]; ⏎ argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:2|redis-8#1

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:2|redis-8#3

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:2|redis-8#4

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行，候選管道 loc）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## base-1:redis-8:3|redis-8#0

**GT**（rule）Unused variable causes compilation warning

> The code declares an unused variable 'unused_flag' that triggers a compilation warning, causing the build to fail when -Werror flag is enabled

GT 片段：`void hincrbyfloatCommand(client *c) { ⏎ long double value, incr; ⏎ long long ll; ⏎ robj *o;`

**finding**（`src/t_hash.c:2244`，距錨點 0 行，候選管道 loc）變數 unused_flag 宣告後未使用

> 在 hincrbyfloatCommand 中宣告了 `int unused_flag = 0;` 但從未使用。這可能是開發過程中的殘留，應移除。

finding 片段：`int unused_flag = 0;`

## base-1:tauri-1:1|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行，候選管道 ident）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行，候選管道 ident）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:1|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增 versionCode 可能超過上限或倒退

> 當 `auto_increment_version_code` 為 true 時，程式從 `tauri.properties` 讀取最後的 versionCode 並加 1，但未檢查新值是否超過 Android 上限 2100000000。若已達上限，`saturating_add` 會停在 2100000000，但這仍可能違反 Google Play 的要求（必須嚴格遞增）。此外，若檔案不存在或格式錯誤，會從 1 開始，可能導致已發布的應用程式版本碼倒退，造成更新失敗。建議在遞增後檢查是否超過上限，並在無法取得有效舊值時回傳錯誤或使用其他來源。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 15 行，候選管道 ident）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行，候選管道 loc）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#3

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行，候選管道 ident）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:2|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行，候選管道 loc）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## base-1:tauri-1:3|tauri-1#0

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 0 行，候選管道 loc）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#1

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 5 行，候選管道 loc）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#2

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 18 行，候選管道 ident）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#4

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 15 行，候選管道 ident）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-1:3|tauri-1#5

**GT**（rule）Public function added without documentation

> A new public API (`pub fn generate_tauri_properties`) was introduced without any `///` documentation comments explaining purpose/params/behavior, violating the requirement that public APIs must be documented.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 1 行，候選管道 loc）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## base-1:tauri-10:1|tauri-10#0

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行，候選管道 loc）inner_size 呼叫參數格式錯誤，可能導致編譯失敗

> 在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這在 Rust 中可能被解析為兩個獨立的 token，導致編譯錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## base-1:tauri-10:1|tauri-10#2

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行，候選管道 loc）inner_size 呼叫參數格式錯誤，可能導致編譯失敗

> 在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這在 Rust 中可能被解析為兩個獨立的 token，導致編譯錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## base-1:tauri-10:2|tauri-10#3

**GT**（func）Changed window naming pattern breaks window label consistency

> The window label format for dynamically created windows has been changed from "new-{number}" to "new-window-{number}". This breaks the established naming convention and will cause any code that attempts to retrieve or manipulate these windows using the expected label format to fail. For example, code trying to access "new-0" or "new-1" will not find the windows, as they are now named "new-window-0" and "new-window-1". This affects window management, event handling, and any window lookup operations that depend on the label pattern.

GT 片段：`let number = created_window_count.fetch_add(1, std::sync::atomic::Ordering::Relaxed); ⏎ let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 11 行，候選管道 ident）on_new_window 移至 cfg(desktop) 區塊可能改變非桌面平台行為

> 原本 `on_new_window` 的設定在所有平台都會執行，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內，這表示在非桌面平台（如行動裝置）上，新視窗的建立邏輯將不會被註冊。如果這是預期的行為變更，請確認；否則可能導致非桌面平台無法正確處理新視窗請求。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## base-1:tauri-10:2|tauri-10#5

**GT**（rule）New code uses unwrap() on fallible operations

> Added code introduces multiple `unwrap()` calls on fallible operations (`parse().unwrap()`, `set_title(...).unwrap()`, and `build().unwrap()`), which violates the rule prohibiting panics/unwraps in favor of explicit error handling via `Result`.

GT 片段：`let builder = tauri::WebviewWindowBuilder::new( ⏎ &app_, ⏎ format!("new-window-{number}"), ⏎ tauri::WebviewUrl::External("about:blank".parse().unwrap()),`

**finding**（`examples/api/src-tauri/src/lib.rs:76`，距錨點 13 行，候選管道 ident）on_new_window 移至 cfg(desktop) 區塊可能改變非桌面平台行為

> 原本 `on_new_window` 的設定在所有平台都會執行，現在被移至 `#[cfg(all(desktop, not(test)))]` 區塊內，這表示在非桌面平台（如行動裝置）上，新視窗的建立邏輯將不會被註冊。如果這是預期的行為變更，請確認；否則可能導致非桌面平台無法正確處理新視窗請求。

finding 片段：`let app_ = app.handle().clone(); ⏎ let mut created_window_count = std::sync::atomic::AtomicUsize::new(0); ⏎  ⏎ window_builder = window_builder`

## base-1:tauri-10:3|tauri-10#0

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行，候選管道 loc）position 呼叫參數格式不一致

> 在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，雖然這在 Rust 中不會導致編譯錯誤，但與專案中其他程式碼的風格不一致。建議改為 `self.window_builder.position(position.x, position.y);`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## base-1:tauri-10:3|tauri-10#2

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1321`，距錨點 0 行，候選管道 loc）position 呼叫參數格式不一致

> 在 `window_features` 方法中，`self.window_builder.position(position.x,position.y);` 的參數之間缺少空格，雖然這在 Rust 中不會導致編譯錯誤，但與專案中其他程式碼的風格不一致。建議改為 `self.window_builder.position(position.x, position.y);`。

finding 片段：`self.window_builder = self.window_builder.position(position.x,position.y);`

## base-1:tauri-11:1|tauri-11#3

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行，候選管道 loc）條件判斷邏輯反轉可能導致版本解析錯誤

> 原本的條件 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。這會使得當 lock 檔存在且 crate_lock_packages 非空時才進入鎖定版本解析，否則會回退到其他邏輯。若原本意圖是「當 lock 檔存在但找不到對應套件時才回退」，則此變更可能導致在 lock 檔存在且套件存在時仍使用鎖定版本，但若套件不存在則可能錯誤地使用其他來源。需要確認此變更是否為修正既有 bug，還是引入新問題。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## base-1:tauri-11:2|tauri-11#1

**GT**（func）GitHub mirror URL construction missing path component

> The generate_github_mirror_url_from_base function is supposed to construct a mirror URL by combining the base CDN URL with the GitHub asset path. However, the code removed the cdn.set_path(github_url) call, meaning the mirror URL will only return the base CDN URL without the asset path. This causes downloads from configured GitHub mirrors to fail because they'll request the wrong URL. When users configure TAURI_BUNDLER_TOOLS_GITHUB_MIRROR to use a mirror server, all downloads will fail with 404 errors since the asset path is missing from the constructed URL.

GT 片段：`fn generate_github_mirror_url_from_base(github_url: &str) -> Option<String> { ⏎ std::env::var("TAURI_BUNDLER_TOOLS_GITHUB_MIRROR") ⏎ .ok() ⏎ .and_then(|cdn| Url::parse(&cdn).ok())`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:37`，距錨點 0 行，候選管道 loc）鏡像 URL 處理方式變更可能導致錯誤網址

> 原本 `generate_github_mirror_url_from_base` 會將 `cdn` 的 path 設為 `github_url`，現在直接回傳 `cdn.to_string()`。這可能導致鏡像網址不再包含原始 GitHub URL 的路徑，使得下載失敗或指向錯誤資源。需要確認此變更是否為預期行為，並驗證鏡像功能是否仍正常運作。

finding 片段：`.map(|cdn| { ⏎ cdn.to_string() ⏎ })`

## base-1:tauri-11:3|tauri-11#2

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行，候選管道 loc）直接使用 ureq::get 可能未套用平台憑證設定

> 在 `download_webview2_offline_installer` 中，直接呼叫 `ureq::get(url)` 而非使用 `base_ureq_agent()`，這可能導致此請求未使用系統憑證，與 PR 目的不一致。建議改用 `base_ureq_agent().get(url)` 以確保一致性。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## base-1:tauri-12:1|tauri-12#0

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:1|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行，候選管道 loc）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:1|tauri-12#3

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:1|tauri-12#4

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行，候選管道 ident）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## base-1:tauri-12:2|tauri-12#0

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行，候選管道 loc）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-12:2|tauri-12#2

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 17 行，候選管道 ident）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-12:2|tauri-12#3

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 5 行，候選管道 loc）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-12:2|tauri-12#4

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` for CFBundleTypeName

> `association.name.as_ref()` returns `&String`; calling `.to_string()` on `&String` is commonly caught by clippy as redundant (e.g., `clippy::string_to_string`). With `-D warnings`, this can break CI; prefer `.clone()`/`.to_owned()` before converting into a plist value.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:353`，距錨點 0 行，候選管道 loc）CFBundleTypeName 使用 expect 可能導致 panic

> 原本使用 `unwrap_or(&association.ext[0].0)` 提供預設值，現在改為 `expect("File association must have a name")`。若使用者未提供 `name` 且 `ext` 為空，程式會 panic。

**失敗情境**：設定 `fileAssociations` 時未提供 `name` 且 `ext` 為空陣列，打包時會 panic。

**建議修法**：保留原本的 fallback 邏輯，或改用更安全的處理方式（例如回傳錯誤而非 panic）。

finding 片段：`.expect("File association must have a name")`

## base-1:tauri-13:1|tauri-13#3

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行，候選管道 loc）notarize_inner 中 map_or 的條件邏輯可能反轉

> 在 `notarize_inner` 函式中，原本的 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。

此變更會影響當 `status` 為 `None` 時的行為：
- 舊邏輯：若 `wait` 為 false，則 `map_or` 回傳 true（因為 `!wait`），因此會進入 if 區塊並印出 "Notarizing" 訊息。
- 新邏輯：若 `wait` 為 false，則 `map_or` 回傳 false，因此不會進入 if 區塊。

這可能導致在非等待模式下，即使 notarization 尚未完成，也不會印出 "Notarizing" 訊息，進而影響使用者體驗或後續流程。

建議確認此變更是否為預期行為，並考慮是否應保留原邏輯或調整條件。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## base-1:tauri-13:2|tauri-13#2

**GT**（func）Swapped source and destination in ditto archive command

> The arguments to the ditto command are reversed: zip_path appears before app_bundle_path, when ditto expects the source (app_bundle_path) before the destination (zip_path). This will cause ditto to fail when attempting to create the notarization archive, as it tries to compress a non-existent zip file into the app bundle directory. The command format should be 'ditto -c -k --keepParent --sequesterRsrc <source> <destination>', but the current order attempts '<destination> <source>', breaking the entire notarization workflow.

GT 片段：`let zip_args = vec![ ⏎ "-c", ⏎ "-k", ⏎ "--keepParent",`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行，候選管道 model_line）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## base-1:tauri-13:2|tauri-13#7

**GT**（rule）Use of expect() for fallible PathBuf-to-str conversion

> The code uses `.to_str().expect(...)`, which will panic on non-UTF8 paths. The rule requires fallible operations to return/propagate `Result` instead of panicking via `expect`/`unwrap`.

GT 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行，候選管道 model_line）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## base-1:tauri-13:3|tauri-13#0

**GT**（rule）Error enum doesn't use thiserror

> The rule requires custom error enums to use #[derive(thiserror::Error)] with #[error(...)] attributes, but this Error enum manually implements Display and Error traits instead of using thiserror

GT 片段：`#[derive(Debug)] ⏎ pub enum Error { ⏎ TempDir(std::io::Error), ⏎ ResolveHomeDir,`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 38 行，候選管道 ident）手動實作 Error trait 可能遺漏 source 方法

> 錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## base-1:tauri-13:3|tauri-13#1

**GT**（func）Missing error source for FailedToEncodeDER variant

> The Error::source() implementation is missing a case for Error::FailedToEncodeDER, which wraps an std::io::Error. This breaks error chain propagation when DER encoding fails. Callers using error context or debugging tools that traverse the error chain will lose the underlying IO error information, making it difficult to diagnose encoding failures. The original PR explicitly added source() support for this variant in the thiserror migration, but this manual implementation omits it.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行，候選管道 loc）手動實作 Error trait 可能遺漏 source 方法

> 錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## base-1:tauri-13:3|tauri-13#5

**GT**（func）Missing error source for Plist variant breaks error chain

> The Error::source() implementation is missing a case for Error::Plist, which wraps a plist::Error. This breaks error chain propagation when plist parsing or writing fails. The Plist variant is used for reading and writing application configuration files and provisioning profiles, making it one of the most commonly encountered errors. Without proper error source propagation, debugging tools and error context mechanisms lose access to the underlying plist parsing errors, making it difficult to diagnose configuration file issues.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行，候選管道 loc）手動實作 Error trait 可能遺漏 source 方法

> 錯誤處理從 `thiserror::Error` 改為手動實作 `Display` 和 `Error` trait。在 `source()` 方法中，僅對 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 回傳來源錯誤，但其他 variant（如 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER`）也包含錯誤欄位，卻未回傳其來源。

這可能導致使用 `anyhow` 或 `eyre` 等 crate 時，無法取得完整的錯誤鏈。建議為所有包含錯誤欄位的 variant 實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## base-1:tauri-2:1|tauri-2#0

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行，候選管道 ident）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-1:tauri-2:1|tauri-2#2

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行，候選管道 loc）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-1:tauri-2:1|tauri-2#4

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行，候選管道 ident）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## base-1:tauri-2:2|tauri-2#1

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行，候選管道 loc）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## base-1:tauri-2:2|tauri-2#3

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行，候選管道 loc）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## base-1:tauri-3:1|tauri-3#1

**GT**（func）TOML parsing errors incorrectly wrapped as JSON errors

> The do_parse_toml function wraps TOML parsing errors as ConfigError::FormatJson instead of ConfigError::FormatToml. This causes misleading error messages when TOML configuration files fail to parse - users will be told there's a JSON parsing error when the actual issue is with TOML syntax. This breaks the error handling contract established by the ConfigError enum and will confuse developers trying to debug configuration issues. The error type conversion using serde_json::Error::custom also loses the detailed TOML error context that would normally be preserved in ConfigError::FormatToml.

GT 片段：`#[cfg(feature = "config-toml")] ⏎ fn do_parse_toml<D: DeserializeOwned>(raw: &str, path: &Path) -> Result<D, ConfigError> { ⏎ // Parse using toml 0.9's from_str which returns different error types ⏎ ::toml::from_str(raw).map_err(|error| ConfigError::FormatJson {`

**finding**（`crates/tauri-utils/src/config/parse.rs:387`，距錨點 0 行，候選管道 loc）TOML 解析錯誤被錯誤地包裝為 JSON 格式錯誤

> 在 `do_parse_toml` 中，原本使用 `ConfigError::FormatToml` 來包裝 TOML 解析錯誤，但升級後改為使用 `ConfigError::FormatJson`，並將錯誤轉為字串後包裝成 `serde_json::Error`。這會導致錯誤類型不正確，使用者將看到誤導的錯誤訊息（例如「JSON 格式錯誤」而非「TOML 格式錯誤」），且可能丟失錯誤的結構化資訊（如行號、欄位）。建議保留 `ConfigError::FormatToml` 變體，並直接傳遞 `toml::de::Error`。

finding 片段：`::toml::from_str(raw).map_err(|error| ConfigError::FormatJson { ⏎ path: path.into(), ⏎ error: serde_json::Error::custom(error.to_string()), ⏎ })`

## base-1:tauri-3:2|tauri-3#0

**GT**（rule）Schema not regenerated after config change

> The rule requires that when source files like crates/tauri-utils/src/config.rs change, the corresponding generated schema files must be updated by running the schema generator build command. The code adds a new Flatpak bundle type to the BundleType enum without regenerating the schema files.

GT 片段：`/// A bundle referenced by tauri-bundler. ⏎ #[derive(Debug, PartialEq, Eq, Clone)] ⏎ #[cfg_attr(feature = "schema", derive(JsonSchema))] ⏎ #[cfg_attr(feature = "schema", schemars(rename_all = "lowercase"))]`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 18 行，候選管道 ident）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-1:tauri-3:2|tauri-3#2

**GT**（func）Case mismatch between BundleType serialization and deserialization for Flatpak

> The Display implementation for BundleType::Flatpak returns "Flatpak" with capital 'F', while the Deserialize implementation expects lowercase "flatpak". This creates a serialization round-trip bug where serializing a Flatpak bundle type and then deserializing it will fail. Any code that serializes bundle configurations to strings (for CLI output, config files, or API responses) and then attempts to parse them back will encounter deserialization errors. This inconsistency breaks the expected behavior that Display and Deserialize should be compatible with each other.

GT 片段：`impl Display for BundleType { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ write!( ⏎ f,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 0 行，候選管道 loc）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-1:tauri-3:2|tauri-3#3

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行，候選管道 ident）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## base-1:tauri-4:1|tauri-4#0

**GT**（rule）Line exceeds max_width of 100

> The rule requires all Rust code to pass 'cargo fmt --all -- --check' adhering to rustfmt.toml configuration (max_width=100). Line 153 in config.rs exceeds the 100 character limit.

GT 片段：`let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli");`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 24 行，候選管道 ident）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-1:tauri-4:1|tauri-4#1

**GT**（func）Incorrect field path for extracting original bundle identifier

> The code attempts to extract the original identifier from the 'bundle' field instead of the root-level 'identifier' field. Since 'bundle' is an object (not a string), the `.as_str()` call will always fail, causing `original_identifier` to always be None. This breaks the ability to track and report which config file overwrites the bundle identifier, as the `find_bundle_identifier_overwriter()` method relies on comparing against the original identifier value.

GT 片段：`let original_identifier = config ⏎ .as_object() ⏎ .and_then(|config| config.get("bundle")) ⏎ .and_then(|id| id.as_str())`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 0 行，候選管道 loc）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-1:tauri-4:1|tauri-4#4

**GT**（rule）Panicking on fallible config schema parsing/validation via expect()

> The new schema validator initialization performs fallible operations (JSON parsing and schema compilation) but uses `.expect(...)`, which will panic on failure instead of returning a `Result` and propagating/handling the error. This violates the rule requiring fallible operations to use `Result`-based error handling rather than panicking.

GT 片段：`CONFIG_SCHEMA_VALIDATOR.get_or_init(|| { ⏎ let schema: JsonValue = serde_json::from_str(include_str!("../../config.schema.json")).expect("Failed to parse config schema bundled in the tauri-cli"); ⏎ jsonschema::validator_for(&schema).expect("Config schema bundled in the tauri-cli is invalid") ⏎ })`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 23 行，候選管道 ident）讀取錯誤的設定欄位：應為 `identifier` 而非 `bundle`

> 在 `get_internal` 中，原本從設定物件讀取 `identifier` 欄位，但此變更改為讀取 `bundle`。這會導致 `original_identifier` 取得錯誤的值，可能影響後續的識別碼處理或驗證邏輯。請確認此變更是否為預期，若非預期應改回 `identifier`。

finding 片段：`.and_then(|config| config.get("bundle"))`

## base-1:tauri-4:2|tauri-4#2

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行，候選管道 loc）條件判斷從 OR 改為 AND，導致 JSON 設定檔不再進行驗證

> 原本的條件是當副檔名為 `json` 或 `json5` 時進行驗證，但改為 AND 後，只有副檔名同時為 `json` 和 `json5`（不可能）才會驗證，實際上完全停用了驗證。這會讓所有 JSON 設定檔跳過 schema 驗證，可能導致錯誤的設定被接受。請改回 OR 邏輯。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## base-1:tauri-4:3|tauri-4#3

**GT**（func）Config merge operation fails to apply merged values

> The `merge_with` function performs the merge operation into the `value` variable but never applies it back to `config_metadata.inner`. The line that should deserialize the merged value back into the config object (`config_metadata.inner = serde_json::from_value(value)...`) was replaced with just inserting into extensions. This means any runtime config merges requested via this function will be ignored - the environment variable will be set, but the actual in-memory config object used by the application will remain unchanged, causing a mismatch between what the application thinks is configured and what's actually being used.

GT 片段：`let mut value = ⏎ serde_json::to_value(config_metadata.inner.clone()).context("failed to serialize config")?; ⏎ merge(&mut value, &merge_config); ⏎ config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

**finding**（`crates/tauri-cli/src/helpers/config.rs:289`，距錨點 0 行，候選管道 loc）`merge_with` 不再合併設定，而是儲存擴充資料，可能破壞合併功能

> 原本的程式碼會將 `merge_config` 合併到 `config_metadata.inner` 中，但此變更改為將 `merge_config` 存入 `extensions`。這可能導致合併功能失效，影響依賴此行為的呼叫者。請確認此變更的意圖，若需保留合併行為，應保留原本的合併邏輯。

finding 片段：`config_metadata.extensions.insert(MERGE_CONFIG_EXTENSION_NAME.into(), merge_config);`

## base-1:tauri-5:1|tauri-5#4

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行，候選管道 loc）`Dirs` 持有 `&'static Path` 可能導致生命週期問題

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但其實際指向的 `PathBuf` 儲存在 `OnceLock` 中。雖然 `OnceLock` 的內容在程式結束前不會被釋放，因此生命週期上可行，但這會造成記憶體永遠無法回收，且若未來改為非靜態儲存，將導致 dangling reference。建議改為持有 `PathBuf` 或使用 `Arc<Path>`，以避免潛在的生命週期問題。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## base-1:tauri-5:3|tauri-5#2

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 8 行，候選管道 ident）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## base-1:tauri-5:3|tauri-5#5

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 18 行，候選管道 ident）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## base-1:tauri-6:1|tauri-6#1

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行，候選管道 ident）無 listener 且 WebView 無法回上一頁時，直接呼叫 activity.onBackPressed() 可能導致 Activity 意外關閉

> 在 `handleOnBackPressed` 中，當 `!hasListener(BACK_BUTTON_EVENT)` 且 `webView?.canGoBack() != true` 時，會執行 `this@AppPlugin.activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是關閉 Activity。如果開發者沒有註冊 listener，使用者按下返回鍵就會直接退出應用程式，這可能不是預期的行為（例如應用程式想要攔截返回鍵但尚未設定 listener）。建議改為不執行任何動作，或提供明確的 API 讓開發者控制是否退出。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## base-1:tauri-6:2|tauri-6#1

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行，候選管道 ident）callback 的 isEnabled 狀態管理可能導致返回鍵失效

> 在 `handleOnBackPressed` 中，當沒有 listener 且 WebView 無法回上一頁時，會先將 `this.isEnabled = false`，然後呼叫 `activity.onBackPressed()`，最後再設回 `true`。然而，`activity.onBackPressed()` 可能會觸發 Activity 的銷毀或暫停，此時 callback 可能已被移除，重新設為 `true` 可能無效或造成記憶體洩漏。此外，如果 `activity.onBackPressed()` 拋出例外，`isEnabled` 將永遠保持 `false`，導致後續返回鍵完全失效。建議使用 try-finally 確保狀態恢復，或避免直接呼叫 `onBackPressed()`。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## base-1:tauri-7:1|tauri-7#1

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:52`，距錨點 0 行，候選管道 loc）generate_github_alternative_url 忽略替代 URL，可能導致下載失敗

> 在 `generate_github_alternative_url` 函式中，原本應回傳替代 URL（`alt_url`），但修改後改為回傳原始 URL（`url.to_owned()`）。這會使函式失去備援功能：當原始 GitHub URL 無法存取時，原本設計的鏡像站或替代來源將不會被使用，可能導致下載失敗。

**失敗情境**：當使用者位於無法直接存取 GitHub 的環境（例如某些地區或企業網路），且設定了 GitHub 鏡像站時，此函式會忽略鏡像 URL，仍嘗試從原始 GitHub 下載，導致建置工具下載失敗。

**建議**：確認此修改是否為預期行為。若需保留備援機制，應回傳 `alt_url`；若因其他原因需使用原始 URL，請在 PR 描述中說明理由。

finding 片段：`.map(|_alt_url| { ⏎ ( ⏎ ureq::Agent::config_builder() ⏎ .user_agent(BUNDLER_USER_AGENT)`

## base-1:tauri-7:2|tauri-7#0

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:99`，距錨點 0 行，候選管道 loc）移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 條件可能影響跨平台行為

> 原本 `HashAlgorithm::Sha256` 僅在 Windows 上啟用，現在移除條件編譯後，所有平台皆可使用 Sha256。這可能是為了修正跨平台雜湊驗證問題，但需確認在其他平台（如 Linux、macOS）上使用 Sha256 是否會造成行為變更或與既有邏輯衝突。

**建議**：確認此變更是否為預期，並檢查是否有其他程式碼依賴此條件編譯。

finding 片段：`pub enum HashAlgorithm { ⏎ Sha256, ⏎ Sha1, ⏎ }`

## base-1:tauri-8:1|tauri-8#1

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行，候選管道 loc）MouseButtonState 的 From 實作將 Up/Down 對應反轉

> 在 `From<tray_icon::MouseButtonState>` 的實作中，原本的對應是 `Up => Up`、`Down => Down`，但此 PR 將其改為 `Up => Down`、`Down => Up`。這會導致所有從 `tray_icon` 轉換而來的滑鼠狀態都被反轉，例如使用者放開滑鼠時會被回報為按下。此變更與 PR 主旨（derive default）無關，且明顯是邏輯錯誤。

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## base-1:tauri-9:1|tauri-9#1

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行，候選管道 loc）cli.js 版本與 tauri-cli crate 版本不一致

> metadata-v2.json 中的 cli.js 版本從 2.8.1 改為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 升到 2.8.1。這可能導致發布流程中 npm 套件與 Rust crate 版本不匹配，或使用者安裝時取得錯誤的 CLI 版本。請確認此處是否應為 2.8.1，或 tauri-cli 應升到 2.8.2。

finding 片段：`"version": "2.8.2",`
