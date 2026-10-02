# 盲標單 5：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part5.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0377

**GT**（rule）Use of expect() for fallible PathBuf-to-str conversion

> The code uses `.to_str().expect(...)`, which will panic on non-UTF8 paths. The rule requires fallible operations to return/propagate `Result` instead of panicking via `expect`/`unwrap`.

GT 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

**finding**（`crates/tauri-macos-sign/src/lib.rs:173`，距錨點 0 行）ditto 命令參數順序調整可能影響行為

> 在 `notarize_inner` 中，`ditto` 命令的參數順序從原本的 `app_bundle_path` 在前、`zip_path` 在後，改為 `zip_path` 在前、`app_bundle_path` 在後。

需要確認 `ditto` 命令的參數順序是否正確：`ditto` 的語法為 `ditto [options] source destination`，因此 source 應為 `app_bundle_path`，destination 應為 `zip_path`。若順序顛倒，可能導致壓縮錯誤或失敗。

建議驗證此變更是否為修正或意外。

finding 片段：`zip_path ⏎ .to_str() ⏎ .expect("failed to convert zip_path to string"), ⏎ app_bundle_path`

## P0378

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 0 行）require 陳述式缺少分號

> 多個 require 陳述式（如 `const PaymentsService = require('./services/payments-service')`）缺少行尾分號，與專案風格不一致。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## P0379

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 3 行）動態切換欄位名稱可能導致資料殘留或驗證問題

> 根據 posture 動態決定使用 `trigger.after` 或 `trigger.expect` 欄位。當 posture 從 Reactive 切換到 Proactive 時，原本在 `trigger.expect` 的值不會自動轉移到 `trigger.after`，可能導致資料不一致。此外，若兩個欄位都有值，切換時可能造成混淆。建議在切換 posture 時清除或轉移相關欄位的值，或使用固定的欄位名稱並在提交時轉換。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0380

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行）orgId 型別轉換可能導致 SQL 錯誤或錯誤結果

> 在 `getTeamsWithPBACPermissions` 的第二個 UNION 查詢中，同樣使用 `${orgId}::bigint`，存在與前述相同的問題。此外，條件 `child."id" = ${orgId}` 可能不正確：若 orgId 是組織 ID，則 child.id 是團隊 ID，不應相等；應改為 `child."parentId" = ${orgId}` 或類似條件。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## P0381

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行）翻譯「Name」由「名字」改為「名稱」可能不恰當

> 在 portal.json 中，"Name" 的翻譯由「名字」改為「名稱」。在個人資料相關的上下文中，「名字」較為常見且自然；「名稱」通常用於物件或組織。若此處指的是使用者姓名，建議維持「名字」。

finding 片段：`"Name": "名称",`

## P0382

**GT**（func）Potential undefined return value breaks type contract

> The getUrlHistory() function can now return undefined when the form is embedded on the same host and getDefaultUrlHistory() returns undefined (e.g., when sessionStorage is empty or invalid). This violates the URLHistory return type contract and will cause a runtime error when the API tries to use the history in sendMagicLink(), as it expects an array. The original code properly handled this by checking 'if (history)' before returning, ensuring a fallback to the constructed history array.

GT 片段：`export function getUrlHistory({siteUrl}: {siteUrl: string}): URLHistory { ⏎ // If we are embedded on the site itself, use the default attribution sessionStorage, just like Portal ⏎ try { ⏎ if (window.location.host === new URL(siteUrl).host) {`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 0 行）getUrlHistory 簡化後可能回傳 null，與呼叫端預期不符

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯（例如回傳空物件或預設值），但簡化後直接回傳 history（可能為 null）。若呼叫端未處理 null，可能導致執行時錯誤。請確認所有呼叫端都能處理 null 回傳值，或保留原本的條件判斷。

finding 片段：`return history;`

## P0383

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1962`，距錨點 0 行）active defrag 恢復邏輯可能錯誤地啟用 defrag

> 在 rdbLoadEmptyDbFunc 中，程式碼先儲存 `orig_active_defrag = server.active_defrag_enabled`，然後將其設為 0，最後在 emptyData 後直接設為 1，而非恢復為 orig_active_defrag。這可能導致原本停用 defrag 的伺服器在同步後意外啟用 defrag。

失敗情境：若使用者在設定檔中將 active-defrag 設為 no，則 server.active_defrag_enabled 初始為 0。當 replica 進行同步時，此函式會將其暫時設為 0，但最後會設為 1，導致 defrag 被意外啟用，可能影響效能或造成非預期行為。

建議：將最後一行改為 `server.active_defrag_enabled = orig_active_defrag;`

finding 片段：`server.active_defrag_enabled = 1;`

## P0384

**GT**（rule）Missing braces in for loop

> The rule requires all control flow statements (if, else, for, foreach, while, do-while) to use curly braces even for single-line bodies, but the inner for loop omits curly braces

GT 片段：`for (const [initializerIdentifier, componentIdentifiers] of Object.entries(jsComponentInitializers)) { ⏎ const initializerFunc = DotNet.findJSFunction(initializerIdentifier, 0) as JSComponentInitializerCallback; ⏎ for (const componentIdentifier of componentIdentifiers) ⏎ initializerFunc(componentIde`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 4 行）hasInitializedJsComponents 全域旗標可能導致初始化被跳過

> `hasInitializedJsComponents` 是模組層級的全域變數，一旦設為 `true` 後，即使之後有新的渲染器（例如同時存在 Server 與 WebAssembly 渲染器）呼叫 `enableJSRootComponents`，初始化回呼也不會被執行。這在多主機（multi-host）或混合渲染模式的情境下可能導致元件未正確初始化。

建議將此旗標改為以 `rendererId` 為鍵的集合（例如 `Set<number>`），或將初始化邏輯與 manager 綁定，確保每個渲染器都能正確初始化。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers. This is an arbitrary subset of the JS component types that are registered ⏎ // on the .NET side - just those of them that require some JS-side initialization (e.g., to register them ⏎ // as custom elements).`

## P0385

**GT**（func）Missing type coercion for retries value causes potential type inconsistency

> The retries display removes the .toString() call that was present in the original PR, directly rendering taskRun.empirical_policy?.retries ?? "0". This creates a type inconsistency where the value could be either a number (when retries exists) or a string "0" (when it doesn't). While React can render both, this inconsistency violates the principle of uniform data handling and could cause issues in the component tree if parent or child components expect consistent string formatting for this field, or if the value is later used in string operations or comparisons.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retries</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retries ?? "0"}`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 10 行）Retry Jitter Factor 使用 truthy 檢查可能將 0 顯示為 None

> 在 Retry Jitter Factor 欄位中，使用 `taskRun.empirical_policy?.retry_jitter_factor ? ... : "None"`。若 `retry_jitter_factor` 為 `0`（合法值），則會顯示 `None`，但實際上應該顯示 `0`。建議改用 `!== null && !== undefined` 或 `??` 來判斷。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## P0386

**GT**（rule）UI constants not in UX struct

> The rule requires UI constants and magic numbers to be organized within a dedicated nested UX struct, but the button size constant (40) is hardcoded directly in the constraint definitions instead of being defined in a private struct UX.

GT 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

**finding**（`firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192`，距錨點 0 行）魔法數字取代常數降低可讀性

> 原本使用 `UX.buttonSize` 常數，現在直接使用數字 40。雖然功能不變，但失去語意，未來修改時容易遺漏。建議保留常數或使用有意義的名稱。

finding 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

## P0387

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行）搜尋過濾功能失效：渲染改用 teamMembers 而非 filteredMembers

> 原本使用 `filteredMembers` 來渲染成員列表，以支援搜尋過濾功能。此變更改為直接使用 `teamMembers`，導致搜尋輸入不會影響顯示的成員列表。請確認此變更是否為預期行為；若非預期，應保留 `filteredMembers` 的過濾邏輯。

finding 片段：`{teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))} ⏎ {teamMembers.length === 0 && (`

## P0388

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）新增的 SettingsTextFormatter 未被使用

> 新增的 `SettingsTextFormatter` 類別目前沒有被任何程式碼引用，可能是為了未來使用而預留，但若無計畫使用，建議移除以避免死代碼。

finding 片段：`class SettingsTextFormatter {`

## P0389

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行）stories 中 queryClient 設定不一致

> 在 `createTestRouter` 中建立了一個新的 `QueryClient` 並放入 router context，但 decorator 中使用的 `QueryClientProvider` 是全域的 `queryClient`。這可能導致測試時 query client 不一致，建議統一使用同一個 instance。

finding 片段：`context: { queryClient: new QueryClient() },`

## P0390

**GT**（rule）Clippy lint: unnecessary `to_string()` on `&String` when building LSItemContentTypes

> `content_types.iter()` yields `&String`, and calling `to_string()` on a `&String` is typically flagged by clippy as an unnecessary conversion/clone (e.g., `clippy::string_to_string`). With warnings denied, this would fail clippy; use `s.clone()`/`s.to_owned()` instead.

GT 片段：`dict.insert( ⏎ "LSItemContentTypes".into(), ⏎ plist::Value::Array(content_types.iter().map(|s| s.to_string().into()).collect()), ⏎ );`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 14 行）條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions

> 在 `create_info_plist` 中，原本的程式碼無條件加入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才加入。這會導致當 `ext` 非空時（正常情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，造成檔案關聯失效。

**失敗情境**：使用者設定 `ext: ["png"]`，產生的 Info.plist 將缺少 `CFBundleTypeExtensions`，macOS 無法將 .png 檔案與應用程式關聯。

**建議**：移除 `if association.ext.is_empty()` 條件，改回無條件加入，或改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0391

**GT**（rule）Missing ConfigureAwait(false) on Task.Yield

> The rule requires all await expressions in library code (non-test, non-sample projects) to use .ConfigureAwait(false) to avoid capturing the synchronization context, but the await Task.Yield() expression at line 291 omits it.

GT 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:290`，距錨點 0 行）新增的 Task.Yield() 可能造成登出流程的競態或延遲

> 在 `ProcessLogOut` 中，於取得驗證狀態前新增了 `await Task.Yield();`。這可能導致登出流程延遲，且若 `AuthenticationProvider.GetAuthenticationStateAsync()` 依賴某些同步狀態，可能引入競態。建議移除或提供明確理由。

finding 片段：`// Ensure we're authenticated before proceeding with sign-out ⏎ await Task.Yield(); ⏎  ⏎ var state = await AuthenticationProvider.GetAuthenticationStateAsync();`

## P0392

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）移除 slack.listen() 可能導致 Slack 服務無法接收事件

> 原本在 `Promise.all` 中有 `slack.listen()`，但修改後被移除。若 Slack 服務需要監聽特定事件（例如發佈通知），移除後可能導致功能失效。請確認 Slack 服務是否已改為其他方式初始化，或此移除是否為有意為之。

finding 片段：`scheduling.init(),`

## P0393

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 18 行）查詢條件 csd_email_count:-null 可能無法正確過濾 null

> `#getDaysSinceFirstEmail` 使用 filter `'csd_email_count:-null'` 來取得第一封有 csd_email_count 的郵件。但 `-null` 在 Ghost 的 NQL 中可能表示「不等於 null」，而非「不為 null」，這可能導致查詢結果包含 null 值，進而使 `created_at` 為 null 或錯誤的資料被選中。建議確認 NQL 語法，或改用 `csd_email_count:>0` 等明確條件。

finding 片段：`filter: 'csd_email_count:-null',`

## P0394

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 0 行）拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0395

**GT**（func）Missing directory parameter breaks WiX upgrade code validation

> In `wix_settings`, the environment variable check `std::env::var_os("TAURI_BUNDLER_WIX_FIPS_COMPLIANT")` was changed but the subsequent check incorrectly compares `OsString` with a string literal "true". The original code used `std::env::var()` which returns a `String`, but `var_os()` returns `OsString` which cannot be directly compared with `==` against a string slice. This breaks FIPS compliance detection for WiX installers, potentially creating non-compliant Windows builds when FIPS mode is required.

GT 片段：`fips_compliant: std::env::var_os("TAURI_BUNDLER_WIX_FIPS_COMPLIANT") ⏎ .map(|v| v == "true") ⏎ .unwrap_or(config.fips_compliant),`

**finding**（`crates/tauri-cli/src/helpers/config.rs:74`，距錨點 0 行）環境變數讀取從 var 改為 var_os 可能影響非 UTF-8 值

> 在 `wix_settings` 中，原本使用 `std::env::var` 讀取 `TAURI_BUNDLER_WIX_FIPS_COMPLIANT`，現在改為 `var_os`。`var_os` 回傳 `OsString`，若環境變數包含非 UTF-8 字元，比較 `v == "true"` 可能失敗。

具體情境：若使用者設定該環境變數為非 UTF-8 值，原本會回傳錯誤，現在可能靜默忽略。

建議：確認此變更是否必要，或使用 `to_str()` 進行安全轉換。

finding 片段：`fips_compliant: std::env::var_os("TAURI_BUNDLER_WIX_FIPS_COMPLIANT") ⏎ .map(|v| v == "true")`

## P0396

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行）buildInviteLink 條件判斷反轉，導致連結格式錯誤

> 原本的邏輯是：如果不是組織情境（`!isOrgContext`），直接回傳 `teamInviteLink`；否則（組織情境）會加上 getting started 路徑。修改後變成：如果是組織情境（`isOrgContext`），直接回傳 `teamInviteLink`；否則（非組織情境）才加上 getting started 路徑。這與原本的意圖相反，可能導致非組織團隊的邀請連結錯誤地包含 getting started 路徑，而組織團隊的連結缺少該路徑。

**建議**：將條件改回 `if (!isOrgContext)`，或確認變數名稱與邏輯是否正確。

finding 片段：`if (isOrgContext) {`

## P0397

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）測試斷言可能使用錯誤的輔助功能識別碼

> 在 testCheckSystemThemeChanges 中，原本檢查 lightThemeView 的選取狀態，但變更後改為檢查 darkThemeView。這可能導致測試在選取 Light mode 時，錯誤地驗證 Dark mode 的狀態，造成測試失敗或誤判。建議確認此變更是否為預期行為，或改回 lightThemeView。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0398

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 39 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0399

**GT**（rule）Service file uses disallowed '.service.ts' suffix / naming convention violation

> Rule 1 disallows dot-suffix service filenames like '.service.ts' and requires service files to be named '<Entity>Service.ts' with matching PascalCase. This PR modifies a service located at 'services/output.service.ts', which violates the naming convention.

GT 片段：`export class OutputBookingsService_2024_08_13 {`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/services/output.service.ts:96`，距錨點 3 行）正規表達式可能誤刪合法 email 中的加號標籤

> `getDisplayEmail` 使用 `/\+[a-zA-Z0-9]{25}/` 移除 email 中加號後綴，但此模式會匹配任何 email 中加號後恰好 25 個英數字元的片段。例如 `user+tag@example.com` 若 `tag` 長度為 25，則整個 `+tag` 會被移除，導致 displayEmail 變成 `user@example.com`，但原始 email 的加號部分可能是使用者自訂的合法標籤，而非 OAuth CUID。這可能造成顯示錯誤的 email。

建議：確認 OAuth CUID 的實際格式，並使用更精確的匹配（例如固定前綴或更嚴格的長度與字元集），或改為從資料庫中直接取得原始 email，而非事後用正規表達式移除。

finding 片段：`private getDisplayEmail(email: string): string { ⏎ return email.replace(/\+[a-zA-Z0-9]{25}/, ""); ⏎ }`

## P0400

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0401

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0402

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:365`，距錨點 0 行）使用 Path.GetFullPath 比較路徑可能因相對路徑或符號連結而誤判

> 在檢查現有 SSL_CERT_DIR 是否已包含憑證目錄時，程式碼使用 `Path.GetFullPath(dir)` 與 `certDirFullPath` 進行比較。然而，`SSL_CERT_DIR` 中的路徑可能是相對路徑，或是包含符號連結，而 `Path.GetFullPath` 只會將相對路徑轉換為絕對路徑，但不會解析符號連結。這可能導致即使實際指向相同目錄，但因為路徑表示不同而被誤判為未包含，進而重複建議設定環境變數，或誤判為已包含而跳過必要的提示。建議使用 `Path.GetFullPath` 後再透過 `Path.GetRelativePath` 或比較 `FileSystemInfo` 的 `FullName` 來處理符號連結，或使用 `Path.TrimEndingDirectorySeparator` 標準化路徑分隔符號。

finding 片段：`var certDirFullPath = Path.GetFullPath(prettyCertDir); ⏎ var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir))`

## P0403

**GT**（func）Missing try keyword in async throws method call

> The IpadOnlyTestCase.setUp() method is marked as 'async throws' but calls 'await super.setUp()' without the 'try' keyword. Since BaseTestCase.setUp() is declared as 'async throws', this means any errors thrown by the parent setUp will not be properly propagated and will instead cause a compilation error or runtime crash. This breaks the error handling contract for all iPad-specific test cases that inherit from IpadOnlyTestCase, potentially causing test suite failures or silent test skips.

GT 片段：`class IpadOnlyTestCase: BaseTestCase { ⏎ override func setUp() async throws { ⏎ specificForPlatform = .pad ⏎ if iPad() {`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/BaseTestCase.swift:508`，距錨點 0 行）IpadOnlyTestCase.setUp 中呼叫 super.setUp() 缺少 try

> 在 IpadOnlyTestCase 的 setUp 方法中，`super.setUp()` 現在是 async throws，但呼叫時沒有加上 `try`。這會導致編譯錯誤：`Call can throw but is not marked with 'try'`。

建議改為 `try await super.setUp()`。

finding 片段：`await super.setUp()`

## P0404

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:34`，距錨點 15 行）無 listener 且 WebView 無法回上一頁時，直接呼叫 activity.onBackPressed() 可能導致 Activity 意外關閉

> 在 `handleOnBackPressed` 中，當 `!hasListener(BACK_BUTTON_EVENT)` 且 `webView?.canGoBack() != true` 時，會執行 `this@AppPlugin.activity.onBackPressed()`。這會觸發 Activity 的預設返回行為，通常是關閉 Activity。如果開發者沒有註冊 listener，使用者按下返回鍵就會直接退出應用程式，這可能不是預期的行為（例如應用程式想要攔截返回鍵但尚未設定 listener）。建議改為不執行任何動作，或提供明確的 API 讓開發者控制是否退出。

finding 片段：`this.isEnabled = false ⏎ this@AppPlugin.activity.onBackPressed() ⏎ this.isEnabled = true`

## P0405

**GT**（rule）Direct logging.getLogger() call used

> The rule requires loggers to be instantiated using the pattern `logger: "logging.Logger" = get_logger("module_name")` instead of direct `logging.getLogger()` calls

GT 片段：`# Log which UI version is being served ⏎ if v2_enabled: ⏎ ui_logger = logging.getLogger("ui_server") ⏎ ui_logger.info("Serving experimental V2 UI")`

**finding**（`src/prefect/server/api/server.py:532`，距錨點 0 行）日誌訊息未使用結構化格式

> 新增的日誌訊息 `Serving experimental V2 UI` 使用 f-string 或直接字串，未包含結構化欄位（如 UI 版本），不利於日誌分析。建議使用結構化日誌或至少包含版本資訊。

finding 片段：`ui_logger.info("Serving experimental V2 UI")`

## P0406

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> 新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0407

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）SortableContext 包含不可拖曳的 prefix items，可能導致拖曳行為異常

> `sortableKeys` 是 `localKeyedValues` 的所有 key，包含 prefixItems 的 key。但 prefixItems 的 `canMove` 為 false，其對應的 `SchemaFormInputArrayItem` 不會渲染拖曳把手，且 `useSortable` 的 `disabled` 設為 true。將 disabled 的項目納入 SortableContext 可能導致 dnd-kit 在計算排序時出現非預期行為，例如拖曳時跳過 disabled 項目或無法正確定位。

建議：僅將可移動項目的 key 傳入 SortableContext，例如 `localKeyedValues.filter((_, index) => getCanMoveForIndex(index)).map(item => item.key)`。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0408

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27`，距錨點 0 行）使用 assert 取代 XCTAssertTrue 會使測試在 release 建置中失效

> 在測試方法中，將 `XCTAssertTrue` 改為 `assert` 會導致斷言在 release 建置（`-O` 或 `-Ounchecked`）中被編譯器移除，使得測試永遠通過，無法驗證行為。此外，`assert` 失敗時會直接 crash 而非記錄測試失敗，破壞 XCTest 的報告機制。

建議改回 `XCTAssertTrue`，並保留原本的訊息參數。

finding 片段：`assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

## P0409

**GT**（func）Inverted existence check prevents GTK plugin installation

> The condition for writing the GTK plugin script was changed from `if !gtk.exists()` to `if gtk.exists()`, inverting the logic. This causes the plugin to only be written when it already exists, and to be skipped when it doesn't exist - the opposite of the intended behavior. Applications using GTK will fail to bundle correctly on systems where the plugin hasn't been previously cached, as the required linuxdeploy-plugin-gtk.sh script won't be created. This breaks the PR's main purpose of inlining the GTK plugin to avoid download failures.

GT 片段：`let gtk = tools_path.join("linuxdeploy-plugin-gtk.sh"); ⏎ if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 4 行）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0410

**GT**（func）Incorrect automation_triggered_event_id for state-specific actions

> When actions_on_trigger or actions_on_resolve are executed, they should be linked to their specific triggered_event.id or resolved_event.id respectively. However, the code incorrectly uses primary_state_change_event_id (which always prefers Triggered over Resolved) for both types of actions. This breaks the tracing chain for actions_on_resolve - they will reference the wrong event ID when only a Resolved state change occurs, making it impossible to correctly trace the action back to the automation.resolved event that actually prompted it.

GT 片段：`# Conditionally add in actions that fire on specific trigger states ⏎ if TriggerState.Triggered in firing.trigger_states: ⏎ triggered_event = state_change_events[TriggerState.Triggered] ⏎ source_actions += [`

**finding**（`src/prefect/server/events/triggers.py:460`，距錨點 0 行）primary_state_change_event 可能為 None，導致後續 KeyError

> `primary_state_change_event` 可能為 None（當 state_change_events 中沒有 Triggered 或 Resolved 時），但後續在 `if TriggerState.Triggered in firing.trigger_states:` 區塊中直接使用 `state_change_events[TriggerState.Triggered]`，若該鍵不存在會拋出 KeyError。需確認 firing.trigger_states 與 state_change_events 的對應關係，或加入防禦性檢查。

finding 片段：`triggered_event = state_change_events[TriggerState.Triggered]`

## P0411

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:11`，距錨點 0 行）config 值未驗證，可能導致排程邏輯錯誤

> `config.get('memberWelcomeEmailTestInbox')` 的回傳值直接作為條件判斷，若 config 值為空字串或未定義，則不會排程；若為任意 truthy 值（例如 'false' 字串），則會排程。建議明確驗證該值是否為有效的 email 或布林值。

finding 片段：`if (!config.get('memberWelcomeEmailTestInbox')) {`

## P0412

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:25`，距錨點 0 行）throttle 方法中 lastExecutionTime 更新順序變更可能影響節流邏輯

> 原本在 guard 檢查前更新 `lastExecutionTime`，現在移到 guard 之後。這可能導致在 threshold 條件不滿足時，`lastExecutionTime` 未被更新，使得後續呼叫的節流判斷不正確。建議確認此變更是否為預期行為。

finding 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

## P0413

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）AND 條件與 OR 條件組合可能導致邏輯錯誤

> 在 Prisma 的 where 中同時使用 OR 和 AND 時，AND 條件會與 OR 條件以 AND 結合，但 OR 內部的條件是 OR 關係。這可能導致過濾條件未如預期套用。例如，若 OR 條件為 (syncSubscribedAt 為 null 或 channelExpiration 小於某時間)，AND 條件為 NOT externalId endsWith 後綴，則最終條件為 (OR 條件) AND (AND 條件)，這通常是正確的。但若未來 OR 條件有變動，可能導致邏輯錯誤。建議明確使用巢狀 AND 或分開條件，並增加測試驗證。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0414

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136`，距錨點 7 行）多渲染器情境下 manager 被覆寫但未處理舊 manager

> 當 `currentRendererId !== rendererId` 時，程式會直接覆寫 `manager` 與 `currentRendererId`，但未對舊的 `manager` 做任何處理。雖然註解提到舊的 manager 已失效，但若舊渲染器仍存活（例如同時存在多個電路），可能導致舊渲染器的後續呼叫使用到錯誤的 manager。

建議確認此情境是否可能發生，若可能，應考慮以 Map 管理多個 manager，或明確禁止多渲染器同時啟用。

finding 片段：`currentRendererId = rendererId; ⏎ manager = managerInstance;`

## P0415

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:147`，距錨點 0 行）JWT 簽署時移除 `noTimestamp` 選項，可能影響 token 格式

> 原本 `jwt.sign(payload, this.tinybirdConfig.adminToken, {noTimestamp: true})` 明確指定不加入 `iat` 時間戳，現在改為 `jwt.sign(payload, this.tinybirdConfig.adminToken)`，會自動加入 `iat`。這可能影響 token 的 payload 結構，若 Tinybird 端預期沒有 `iat` 欄位，可能導致驗證失敗或行為改變。

**建議**：確認 Tinybird 端是否接受含有 `iat` 的 token，若不需要可保留 `noTimestamp: true`。

finding 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

## P0416

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:42`，距錨點 0 行）使用 hash() 產生 advisory lock key 會因 PYTHONHASHSEED 而失效

> `lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash() 對字串做雜湊。在 CPython 中，字串的 hash 會受到 PYTHONHASHSEED 環境變數影響，每個 process 的 seed 可能不同，導致不同 worker process 對同一個 trigger.id 計算出不同的 lock key。這會使 advisory lock 無法跨 process 互斥，競態條件仍然存在。

建議改用 UUID 的整數表示（例如 `trigger.id.int`）或使用穩定的雜湊函式（如 hashlib.sha256）來產生 lock key。

finding 片段：`lock_key = hash(str(trigger.id)) % (2**63)`

## P0417

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）測試步驟順序調整可能影響穩定性

> 在 `testDisableTopSitesSettingsRemovesSection` 中，原本先 `navigator.goto(NewTabScreen)` 再點擊 "Done"，現在改為先點擊 "Done" 再 `navigator.goto(NewTabScreen)`。如果 "Done" 按鈕在當前畫面不存在或不可點擊，可能導致測試失敗。需要確認此調整是否為了解決特定問題，並驗證在各種裝置與狀態下仍能穩定執行。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0418

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳值型別錯誤：使用 Python 的 `True` 而非 JavaScript 的 `true`

> 在 `handleJSONSchemaChange` 函式中，成功解析 JSON 後回傳了 `True`（Python 布林值），但在 JavaScript/TypeScript 中應為 `true`。這會導致回傳值型別不一致，且若呼叫端依賴此回傳值，可能造成非預期行為。建議改為 `return true`。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0419

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行）移除 strict=True 可能導致 zip 截斷而遺漏工作池

> 在 `_fetch_work_pools_parallel` 中，原本使用 `zip(pool_names_list, results, strict=True)` 確保兩個序列長度一致。移除 `strict=True` 後，若 `results` 的長度小於 `pool_names_list`（例如某個 task 被取消或未回傳），zip 會靜默截斷，導致部分工作池未被處理，且不會有任何警告。這可能造成 SDK 資料不完整，且難以察覺。建議保留 `strict=True`，或明確處理長度不一致的情況。

finding 片段：`for name, result in zip(pool_names_list, results):`

## P0420

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:212`，距錨點 17 行）使用 `deployment_id` 而非 `deployment.id` 可能導致型別錯誤

> 原本 `client.create_flow_run_from_deployment(deployment.id, ...)` 使用 `deployment.id`，現在改為 `deployment_id`。若 `deployment_id` 是字串（例如從名稱解析而來），而 API 期望 UUID，可能導致型別錯誤。

建議：確認 `deployment_id` 的型別，必要時轉換為 UUID。

finding 片段：`deployment_id,`

## P0421

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:68`，距錨點 35 行）輪詢可能產生競態條件

> `confirmHandle` 使用 `mutateAsync` 但未處理錯誤，且輪詢間隔固定為 5 秒。若前一次請求尚未完成，下一次輪詢可能同時發出多個請求，導致伺服器壓力或狀態不一致。此外，若 `confirmBlueskyHandleMutation` 失敗（例如網路錯誤），錯誤未被捕獲，可能造成 unhandled rejection。建議在 `confirmHandle` 中加入錯誤處理，並考慮使用 `isPending` 或鎖定機制避免重疊請求。

finding 片段：`const confirmHandle = useCallback(() => { ⏎ confirmBlueskyHandleMutation.mutateAsync().then((handle) => { ⏎ if (handle) { ⏎ setHandleConfirmed(true);`

## P0422

**GT**（func）Selected block document not found when search filter is active

> The `selectedBlockDocument` memo is incorrectly using `filteredData` instead of the original `data` array. When a user performs a search that doesn't match the currently selected block's name, the selected block will not be found in the filtered results, causing it to become undefined. This breaks the UI by displaying 'Select a block...' placeholder instead of showing the actual selected block name, even though a block is selected.

GT 片段：`const selectedBlockDocument = useMemo(() => { ⏎ return filteredData.find( ⏎ (blockDocument) => blockDocument.id === selectedBlockDocumentId, ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 6 行）前端過濾可能導致選項遺漏

> `filteredData` 使用 `deferredSearch` 進行前端過濾，但後端查詢已使用 `like_` 條件。若後端過濾與前端過濾不一致（例如大小寫敏感度、特殊字元處理），可能導致使用者輸入搜尋字串時，後端已回傳符合的資料，但前端又將其過濾掉，造成選項遺漏。建議移除前端過濾，直接使用後端回傳的 `data`，或確保前後端過濾邏輯完全一致。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0423

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1317`，距錨點 0 行）inner_size 呼叫參數格式錯誤，可能導致編譯失敗

> 在 `window_features` 方法中，`self.window_builder.inner_size(size.width,    size.height);` 的參數之間有多餘空格，這在 Rust 中可能被解析為兩個獨立的 token，導致編譯錯誤。建議移除多餘空格，改為 `self.window_builder.inner_size(size.width, size.height);`。

finding 片段：`self.window_builder = self.window_builder.inner_size(size.width,    size.height);`

## P0424

**GT**（func）Navigation exception test disables the exception mechanism it's meant to test

> The NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException test is designed to verify that NavigationException thrown during circular redirects doesn't become an unobserved task exception. The test name, comments, and logic all indicate it should test the exception handling behavior. However, the AppContext switch is set to true, which enables DisableThrowNavigationException, preventing NavigationException from being thrown at all. This fundamentally breaks the test's purpose - it can't validate exception handling behavior when exceptions are disabled. The test navigates to a circular redirect page that relies on NavigationException being thrown and properly handled, but with the switch enabled, the navigation manager uses a different code path that doesn't throw exceptions, making the test validate nothing meaningful.

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 0 行）AppContext.SetSwitch 參數反轉可能導致測試失效

> 原本設定 DisableThrowNavigationException 為 false，現在改為 true。若測試目的是驗證例外拋出，設為 true 會停用例外，可能使測試無法觸發預期行為。需確認此變更是否為預期修正。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0425

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:42`，距錨點 0 行）使用 Python hash 作為 advisory lock key 不穩定

> `hash(str(trigger.id))` 的結果在每次 Python 程序啟動時都可能不同（因為 hash 隨機化），這會導致不同 worker 對同一個 trigger 計算出不同的 lock key，使得 advisory lock 無法正確序列化，競態條件仍然存在。建議改用 UUID 的整數表示（例如 `trigger.id.int`）並截斷至 63 位元，以確保跨程序一致。

finding 片段：`lock_key = hash(str(trigger.id)) % (2**63)`

## P0426

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27`，距錨點 0 行）使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效

> 將 XCTAssertTrue 改為 assert 可能導致測試在 release 建置中失效，因為 assert 在最佳化編譯時可能被移除。建議使用 XCTest 的斷言方法（如 XCTAssertTrue）以確保測試在各種建置中都能正常執行。

finding 片段：`assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

## P0427

**GT**（func）Async test assertion never verified due to missing expectation

> The test was updated to use @Sendable closures for Swift 6 concurrency compliance, but the expectation and wait statements were removed. The test now completes immediately without waiting for the asynchronous requestMediaCapturePermission callback. The XCTAssertEqual inside the decisionHandler closure will never execute, causing the test to always pass even when the media capture permission logic is broken. This is particularly problematic because this test validates critical permission handling behavior.

GT 片段：`func testRequestMediaCaptureSuccess() { ⏎ let subject = createSubject(isActive: true) ⏎ let decisionHandler: @Sendable (WKPermissionDecision) -> Void = { (decision: WKPermissionDecision) in ⏎ XCTAssertEqual(decision, .prompt)`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:42`，距錨點 0 行）測試未等待非同步決策處理器，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，移除了 expectation 的建立與 `wait(for:)`，但 `requestMediaCapturePermission` 可能非同步呼叫決策處理器。測試方法現在是同步的，可能在處理器執行前就返回，導致斷言未被執行。建議保留 expectation 並等待。

finding 片段：`subject.requestMediaCapturePermission(decisionHandler: decisionHandler)`

## P0428

**GT**（func）Missing type validation for work pool job variables schema

> The code removes the `isinstance(variables, dict)` type check before assigning `base_job_template["variables"]` to `job_vars_schema`. The `job_vars_schema` variable is typed as `dict[str, Any]` and is expected to be a dictionary throughout the SDK generation process. If `base_job_template["variables"]` contains a non-dict value (like a list, string, or other type due to malformed work pool configuration), this will cause type inconsistencies that could lead to runtime errors in downstream code that expects a dict, such as the template renderer or SDK generator that processes the schema.

GT 片段：`base_job_template = work_pool.base_job_template ⏎ if base_job_template and "variables" in base_job_template: ⏎ job_vars_schema = base_job_template["variables"]`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 0 行）對 base_job_template["variables"] 的型別假設可能導致執行期錯誤

> 在 `_fetch_work_pool` 中，原本有檢查 `isinstance(variables, dict)` 才指派給 `job_vars_schema`。移除檢查後，直接將 `base_job_template["variables"]` 指派給 `job_vars_schema`，但該值可能不是 dict（例如是 list 或 None）。後續程式碼若假設 `job_vars_schema` 是 dict（例如呼叫 `.items()` 或進行 dict 操作），會拋出 AttributeError 或 TypeError。建議保留型別檢查，或確保上游資料一定為 dict。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## P0429

**GT**（func）Incorrect priority sorting in sortHosts breaks round-robin host assignment

> The priority comparison logic is inverted when weights are equal in round-robin mode. The code now returns `priorityA - priorityB` instead of `priorityB - priorityA`, which sorts hosts in ascending priority order (lowest priority first) instead of descending (highest priority first). This causes lower-priority hosts to be selected before higher-priority hosts when weights are equal, breaking the intended assignment logic throughout the application wherever host assignment is used.

GT 片段：`if (isRRWeightsEnabled) { ⏎ if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else {`

**finding**（`packages/lib/bookings/hostGroupUtils.ts:52`，距錨點 0 行）sortHosts 函式在權重相等時排序邏輯反轉

> 在 `isRRWeightsEnabled` 為 true 且 `weightA === weightB` 時，原本的實作回傳 `priorityB - priorityA`（優先權高者在前），但移動後的版本回傳 `priorityA - priorityB`，導致排序方向相反。這會影響依賴此函式的主機排序（例如 EventTeamAssignmentTab），可能造成優先權較低的主機被排在前面的錯誤。

建議修正為：
```ts
if (weightA === weightB) {
  return priorityB - priorityA;
}
```

finding 片段：`if (weightA === weightB) { ⏎ return priorityA - priorityB; ⏎ } else { ⏎ return weightB - weightA;`

## P0430

**GT**（func）Inverted logic for non-blocking notarization success check

> The condition 'submit_output.status.map_or(wait, |s| s == "Accepted")' has inverted logic for the non-blocking case. When wait is false and status is None (pending submission), map_or returns false (the value of wait), causing the function to incorrectly treat successful submissions as failures. The original logic was 'map_or(!wait, ...)' which correctly returns true for pending non-blocking submissions. This bug causes notarize_without_stapling to fail immediately after successful submission, preventing users from receiving the submission ID and instructions for checking status later.

GT 片段：`// status is empty when not waiting for the notarization to finish ⏎ if submit_output.status.map_or(wait, |s| s == "Accepted") { ⏎ println!("Notarizing {log_message}"); ⏎ if wait {`

**finding**（`crates/tauri-macos-sign/src/lib.rs:233`，距錨點 0 行）notarize_inner 中 map_or 的條件邏輯可能反轉

> 在 `notarize_inner` 函式中，原本的 `submit_output.status.map_or(!wait, |s| s == "Accepted")` 被改為 `submit_output.status.map_or(wait, |s| s == "Accepted")`。

此變更會影響當 `status` 為 `None` 時的行為：
- 舊邏輯：若 `wait` 為 false，則 `map_or` 回傳 true（因為 `!wait`），因此會進入 if 區塊並印出 "Notarizing" 訊息。
- 新邏輯：若 `wait` 為 false，則 `map_or` 回傳 false，因此不會進入 if 區塊。

這可能導致在非等待模式下，即使 notarization 尚未完成，也不會印出 "Notarizing" 訊息，進而影響使用者體驗或後續流程。

建議確認此變更是否為預期行為，並考慮是否應保留原邏輯或調整條件。

finding 片段：`if submit_output.status.map_or(wait, |s| s == "Accepted") {`

## P0431

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 19 行）start_execution 在 enqueue 之前呼叫可能導致狀態不一致

> 在 `enqueue_node` 之前呼叫 `start_execution` 可能造成節點狀態被標記為執行中，但尚未進入佇列。若後續 `enqueue_node` 失敗或拋出例外，節點會停留在執行中狀態而無法被正確處理。建議確認 `start_execution` 的實作是否具冪等性，或調整呼叫順序。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0432

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 4 行）`run_deployment` 別名失去同步包裝，同步呼叫會失敗

> 原本 `run_deployment` 有 `@sync_compatible` 裝飾器，可在同步上下文中呼叫。現在 `run_deployment = arun_deployment` 只是 async 函式的別名，同步呼叫會回傳 coroutine 而非執行結果，導致既有同步程式碼失效。建議保留同步包裝或提供明確的同步版本。

finding 片段：`run_deployment = arun_deployment`

## P0433

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions

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

## P0435

**GT**（func）Incorrect parameter name prevents timeout configuration in test harness

> The test fixture uses `server_timeout=60` when calling `prefect_test_harness()`, but the correct parameter name is `server_startup_timeout`. This means the intended 60-second timeout is not actually applied, leaving tests vulnerable to the same timeout issues in CI environments that the change was meant to fix. The prefect_test_harness function will ignore the invalid parameter and use its default timeout value instead, potentially causing intermittent test failures when multiple xdist workers start simultaneously in CI.

GT 片段：`# Increase timeout for CI environments where multiple xdist workers ⏎ # start servers simultaneously, which can be slower on Python 3.11+ ⏎ # See https://github.com/PrefectHQ/prefect/issues/16397 ⏎ with prefect_test_harness(server_timeout=60):`

**finding**（`src/integrations/prefect-gcp/tests/conftest.py:19`，距錨點 0 行）移除 disable_logging fixture 可能導致測試輸出過多

> 原本的 `disable_logging` fixture 會暫時關閉 logging to API，避免測試時產生過多 log。移除後，測試期間可能會輸出大量 log，影響測試可讀性與效能。若這是為了簡化設定，建議確認是否有其他機制控制 log，否則應保留此 fixture。

finding 片段：`with prefect_test_harness(server_timeout=60): ⏎ yield`

## P0436

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 29 行）輔助函式缺少單元測試

> 新增的 `web/test/i18n-mock.ts` 包含多個輔助函式，但沒有對應的測試。這些函式將被多個測試檔案使用，若行為有誤可能影響大量測試。建議為這些輔助函式撰寫單元測試，涵蓋自訂翻譯、namespace 前綴、參數序列化等情境。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0437

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:238`，距錨點 21 行）transcripts 端點的 guard 順序與 recordings 不一致

> recordings 端點使用 `@UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`，而 transcripts 端點使用 `@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`。順序不同可能影響錯誤回應（例如未驗證時先觸發 Pbac 而非 ApiAuth）。建議統一順序。

finding 片段：`@UseGuards(BookingPbacGuard, ApiAuthGuard, BookingUidGuard)`

## P0438

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:247`，距錨點 0 行）reload_config 可能導致資料競爭

> `reload_config` 接受 `&mut ConfigMetadata`，但呼叫端可能同時有多個執行緒持有同一個 `ConfigMetadata` 的參考（例如在 `run_dev_watcher` 中，`config` 被包在 `Mutex` 中，但鎖定後傳遞的是 `&mut` 參考，而其他執行緒可能也在存取）。

具體情境：在 dev 模式下，檔案監視器執行緒與主執行緒可能同時存取 `config`，導致資料競爭。

建議：確保所有對 `ConfigMetadata` 的存取都透過 Mutex 保護，或使用不可變共享（如 `Arc<RwLock<ConfigMetadata>>`）。

finding 片段：`pub fn reload_config( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

## P0439

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）TryGetValidatableTypeInfo 中 out 參數初始化位置移動

> 原本在方法最後才設定 `validatableTypeInfo = null`，現在移到方法開頭。這在功能上可能沒有差異，因為 out 參數在方法內必須賦值，但移動位置可能影響可讀性或與其他程式碼的互動。建議確認此變更是否為預期，並確保所有路徑都有正確賦值。

finding 片段：`validatableTypeInfo = null;`

## P0440

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0441

**GT**（func）Slack notifications not functioning - event listeners never registered

> The slack.listen() call was removed from the service initialization in Promise.all, but the slack service module is still imported. This means the Slack service event listeners for 'post.published' and 'slack.test' events are never registered during boot. As a result, posts published on the site will not trigger Slack webhook notifications even when Slack integration is configured correctly. The slack.listen() method registers critical event handlers that connect the Ghost event system to the Slack notification service, and without this call, the integration is completely non-functional.

GT 片段：`await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(), ⏎ memberAttribution.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 移至 Promise.all 可能造成初始化順序問題

> 原本 `await emailAddressService.init()` 是依序執行，現在改為在 `Promise.all` 中並行初始化。若其他服務（如 newsletter、email）依賴 emailAddressService 完成初始化，可能導致競態條件或初始化失敗。建議確認相依性，必要時保留依序 await。

finding 片段：`emailAddressService.init(),`

## P0442

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0443

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行）測試依賴真實網路與 WebKit 行為，可能導致不穩定或逾時

> captureFrameAndOrigin 會建立真實的 WKWebView 並載入 https://example.com。這使得測試依賴外部網路連線與 WebKit 的實際行為，可能因網路延遲、離線環境或 WebKit 內部變更而失敗或逾時。建議改用 local test server 或注入 mock 的 navigation delegate 來提供所需的 WKFrameInfo 與 WKSecurityOrigin，以提升測試穩定性。

finding 片段：`webView.load(URLRequest(url: url))`

## P0444

**GT**（func）Missing PreReleaseBrandingLabel for servicing builds

> The PreReleaseBrandingLabel configuration is missing the condition for 'servicing' builds. While the PreReleaseVersionLabel is set to 'servicing', there is no corresponding conditional assignment for PreReleaseBrandingLabel when PreReleaseVersionLabel equals 'servicing'. This means servicing builds will have an undefined or incorrect branding label, causing incorrect version strings in build outputs and package metadata. The original PR added this condition to properly support servicing releases.

GT 片段：`<PreReleaseVersionLabel>servicing</PreReleaseVersionLabel> ⏎ <!-- PreReleaseBrandingLabel is automatically calculated based on PreReleaseVersionLabel --> ⏎ <PreReleaseBrandingLabel Condition="'$(PreReleaseVersionLabel)' == 'alpha'">Alpha $(PreReleaseVersionIteration)</PreReleaseBrandingLabel> ⏎ <Pre`

**finding**（`eng/Versions.props:14`，距錨點 8 行）停用 ValidateBaseline 可能隱藏套件參考變更

> 將 `ValidateBaseline` 從 `true` 改為 `false` 會關閉基線驗證，可能導致未預期的套件參考變更在 servicing 更新中被忽略。建議確認此變更的必要性，或僅在特定條件下停用。

finding 片段：`<ValidateBaseline>false</ValidateBaseline>`

## P0445

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 21 行）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0446

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行）hasPageActions 判斷誤用 leadingPageActionStack

> 在 `updateToolbarLayout` 中，原本 `let hasPageActions = !pageActionStack.arrangedSubviews.isEmpty` 被改為 `!leadingPageActionStack.arrangedSubviews.isEmpty`。但此處的 `hasPageActions` 應代表 trailing page actions 是否存在，以決定 divider 寬度。若 leading 和 trailing page actions 不同時存在，可能導致 divider 顯示錯誤。

建議改回 `!trailingPageActionStack.arrangedSubviews.isEmpty`。

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## P0447

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:67`，距錨點 0 行）前端過濾可能導致選項遺漏

> `filteredData` 使用 `deferredSearch` 進行前端過濾，但後端查詢已使用 `like_` 條件。若後端過濾與前端過濾不一致（例如大小寫敏感度、特殊字元處理），可能導致使用者輸入搜尋字串時，後端已回傳符合的資料，但前端又將其過濾掉，造成選項遺漏。建議移除前端過濾，直接使用後端回傳的 `data`，或確保前後端過濾邏輯完全一致。

finding 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

## P0448

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:914`，距錨點 0 行）dictSetKeyAtLink 在 newItem=0 時使用 addedKey 查找可能失敗

> 在 dictSetKeyAtLink 中，當 newItem=0 且 *link 為 NULL 時，程式碼使用 addedKey 呼叫 dictFindLink。但 addedKey 是經過 keyDup 處理後的鍵，可能與原始 key 不同（例如 keyDup 可能複製或轉換鍵）。如果 dictFindLink 使用 addedKey 找不到對應的 entry，則會觸發 assert(*link != NULL) 失敗。

失敗情境：當 dictType.keyDup 非 NULL 且會改變鍵的內容（例如複製 sds 或進行其他轉換），且呼叫者傳入的 key 與儲存的鍵不同時，dictFindLink 將無法找到 entry。

建議：應使用原始 key（或 dictStoredKey2Key(d, key)）進行查找，而不是 addedKey。

finding 片段：`*link = dictFindLink(d, addedKey, NULL);`

## P0449

**GT**（rule）Variable declared using var keyword

> The rule requires all variable declarations to use let (for reassignable variables) or const (for constants), never var. The code uses var to declare the member variable.

GT 片段：`const context = options && options.context || {}; ⏎ const source = this._resolveContextSource(context); ⏎ const eventData = _.pick(data, ['created_at']); ⏎ const memberAddOptions = {...(options || {}), withRelated};`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 1 行）config 值型別不一致可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 回傳值可能是字串（如測試中設定的 'test-inbox@example.com'）或 undefined。在條件判斷中，空字串會被視為 falsy，但非空字串為 truthy，因此若設定為空字串會停用功能，但設定為任意非空字串（即使不是有效 email）也會啟用。建議明確檢查是否為有效 email 或使用布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0450

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 0 行）isReaderModeEnabled 的布林值反轉，可能導致遙測記錄錯誤

> 原本 `case .available: true`、`default: false`，現在改為 `case .available: false`、`default: true`。這會讓閱讀模式按鈕的遙測事件記錄錯誤的啟用狀態。請確認此變更是否為筆誤，若不是，請提供對應的測試與說明。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## P0451

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 0 行）FakeWKNavigationDelegate 可能無法捕捉到 targetFrame

> 在 `decidePolicyFor` 中，`navigationAction.targetFrame` 可能為 nil（例如在新視窗開啟的導航），此時 `capturedFrame` 會是 nil，導致函式回傳 nil。雖然目前測試使用簡單的 URL，但若未來測試情境改變，可能無法取得 frame。

建議在 `targetFrame` 為 nil 時採取替代方案，或明確處理此情況。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0452

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行）bootstrapDependencies 標記為 @MainActor 但未處理非主執行緒呼叫

> `bootstrapDependencies` 被標記為 `@MainActor`，但方法內部仍有 `DispatchQueue.main.sync` 的舊程式碼被移除，改為直接在主執行緒上執行。這可能導致在非主執行緒呼叫時發生問題。建議確認所有呼叫點都在主執行緒上，或保留適當的執行緒處理。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## P0453

**GT**（rule）Cross-field validation uses field validator

> The rule requires cross-field validation to use @model_validator decorator, but the code uses @field_validator which accesses unvalidated fields via info.data, causing order-dependent validation issues

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行）欄位驗證器依賴欄位順序，可能因未來調整而失效

> `validate_automation_triggered_event_id` 驗證器使用 `info.data.get("triggering_event")` 來檢查 `triggering_event` 是否存在。在 Pydantic v2 中，`info.data` 僅包含已驗證的欄位，因此若 `triggering_event` 欄位在 `automation_triggered_event_id` 之後定義，驗證器將無法取得其值，導致驗證失效。

失敗情境：若未來有人調整欄位順序，將 `triggering_event` 移到 `automation_triggered_event_id` 之後，則即使 `triggering_event` 為 None，驗證器也不會拋出錯誤，允許不一致的資料。

建議修法：改用 `model_validator` 或在驗證器中直接從 `info.data` 以外的來源取得 `triggering_event`，或使用 `@model_validator(mode='after')` 進行跨欄位驗證。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## P0454

**GT**（func）Active defragmentation incorrectly forced ON after replication sync

> The code saves the original active_defrag_enabled value but then unconditionally sets it to 1 instead of restoring the original value. This means if active defragmentation was disabled before the replication sync (orig_active_defrag = 0), it will be incorrectly enabled after emptyData() completes. This breaks the intended behavior of preserving the user's defragmentation configuration and can cause unexpected performance degradation or memory operations on replicas that should not have defragmentation running.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1961`，距錨點 0 行）active_defrag_enabled 未正確還原，可能意外啟用 defrag

> 在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 存入 `orig_active_defrag`，然後設為 0，但在函式結尾卻直接設為 1，而非還原為 `orig_active_defrag`。這會導致原本停用 active defrag 的伺服器在執行此函式後被強制啟用，可能造成非預期的記憶體整理行為，甚至影響效能或穩定性。

建議修正：
```c
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`/* Restore the original active defragmentation setting. */ ⏎ server.active_defrag_enabled = 1;`

## P0455

**GT**（func）Incorrect logical operator in tearDown causing theme reset to be skipped for all iPad tests

> The tearDown method uses OR (||) instead of AND (&&) when checking if the test should skip theme reset. This causes the theme reset to be skipped for ALL tests running on iPad devices, not just the testSelectBottomPlacement test. The original intent was to skip theme reset only when BOTH conditions are true (the test is testSelectBottomPlacement AND it's running on iPad), but the current code skips it when EITHER condition is true. This will leave the theme in Dark mode after any test runs on iPad, potentially affecting subsequent tests that expect Light theme.

GT 片段：`override func tearDown() async throws { ⏎ if #available(iOS 17.0, *) { ⏎ if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there.`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29`，距錨點 0 行）tearDown 中提前 return 可能略過清理步驟

> 在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 成立時直接 `return`，導致後續的 `app.terminate()` 與 `super.tearDown()` 不會被執行。這可能造成測試狀態殘留，影響後續測試的隔離性。建議改為使用 `if` 條件包住主題切換，但保留 `app.terminate()` 與 `super.tearDown()` 的執行。

finding 片段：`if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there. ⏎ return ⏎ } else {`

## P0456

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行）orgId 過濾邏輯可能排除應包含的團隊

> 在 UNION 的第二部分，條件 `AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})` 只檢查 org.id 或 child.id 等於 orgId，但未考慮 child.parentId 等於 orgId 的情況。這可能導致當 orgId 為父組織時，子團隊被錯誤排除。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## P0457

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0458

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會讓 `j` 等於 `numkeys` 時仍進入迴圈，此時 `slot_buffer[j]` 寫入超出配置的記憶體（配置大小為 `numkeys`）。這會造成 heap buffer overflow，可能導致程式崩潰或安全漏洞。

建議改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0459

**GT**（func）Incorrect EHLO hostname parameter in opportunistic TLS mode

> When opportunistic TLS is enabled, the code passes `local_host` (which can be None or an empty string) to the EHLO command instead of using `self.server`. According to RFC 5321, the EHLO command should identify the client using its fully qualified domain name. The original code correctly used `self.server` as the EHLO identifier before this PR. This bug will cause SMTP servers that validate EHLO domains to reject the connection, especially when SMTP_LOCAL_HOSTNAME is not configured or is empty.

GT 片段：`assert smtp is not None ⏎ if self.use_tls and self.opportunistic_tls: ⏎ smtp.ehlo(local_host) ⏎ smtp.starttls()`

**finding**（`api/libs/smtp.py:32`，距錨點 0 行）assert 不應作為執行時期檢查

> `assert smtp is not None` 在 Python 最佳化模式（`-O`）下會被移除，且此處 smtp 必定不為 None，因此 assert 無實際作用。建議移除該 assert，或改為明確的例外處理。

finding 片段：`assert smtp is not None`

## P0460

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 17 行）JWT 驗證改為僅解碼，未驗證簽章

> `_isJWTExpired` 方法原本使用 `jwt.verify(token, this.tinybirdConfig.adminToken)` 來驗證 token 的簽章與有效性，現在改為 `jwt.decode(token)`，只解碼而不驗證簽章。這會讓攻擊者可以偽造 token（只要 payload 包含有效的 `exp` 欄位），繞過驗證。

**失敗情境**：攻擊者自行產生一個帶有未來 `exp` 的 JWT，即使簽章無效，系統仍會視為有效，進而取得未授權的存取。

**建議**：保留 `jwt.verify` 來驗證簽章，若需要解碼 payload 可另行處理。

finding 片段：`const decoded = jwt.decode(token);`

## P0461

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:342`，距錨點 15 行）Redis pipeline 寫入失敗時，快取資料遺失且無重試機制

> 在 `get_plan_bulk_with_cache` 的 Step 3 中，使用 pipeline 批次寫入 Redis。如果 `pipe.execute()` 拋出例外，程式只記錄錯誤，但不會將資料寫入快取，也不會影響回傳值。這會導致下次查詢時仍然 cache miss，增加 API 負載。雖然不影響正確性，但降低了快取效益。

**失敗情境**：Redis 暫時不可用或 pipeline 執行失敗時，所有從 API 取得的資料都不會被快取，下次相同查詢仍會打到 API。

**建議**：考慮加入簡單的重試機制，或在 pipeline 失敗時降級為逐筆寫入（或至少記錄警告）。

finding 片段：`except Exception: ⏎ logger.exception("get_plan_bulk_with_cache: redis pipeline failed")`

## P0462

**GT**（func）Missing @Sendable annotation on completionHandler breaks WKUIDelegate contract

> The completionHandler parameter has @MainActor but is missing the @Sendable annotation that WKWebKit requires in Swift 6. The original delegate signature from WKWebKit expects @escaping @MainActor @Sendable () -> Void, but this implementation only provides @escaping @MainActor () -> Void. When this completion handler is passed through to the legacyResponder (which is a WKUIDelegate), it creates a type mismatch that violates Sendable checking. This can lead to compiler warnings being suppressed and potential data races when the closure captures mutable state, as Sendable enforcement is bypassed.

GT 片段：`func webView( ⏎ _ webView: WKWebView, ⏎ runJavaScriptAlertPanelWithMessage message: String, ⏎ initiatedByFrame frame: WKFrameInfo,`

**finding**（`firefox-ios/Client/Frontend/Browser/BrowserViewController/WebEngineIntegration/BrowserWebUIDelegate.swift:42`，距錨點 0 行）移除 @Sendable 可能導致並行檢查錯誤

> 在 BrowserWebUIDelegate.swift 中，completionHandler 的型別從 `@escaping @MainActor @Sendable () -> Void` 改為 `@escaping @MainActor () -> Void`，移除了 @Sendable。若此閉包需要跨 actor 傳遞，移除 @Sendable 可能導致 Swift 6 的並行檢查錯誤。請確認此變更是否必要，並檢查所有呼叫端是否相容。

finding 片段：`completionHandler: @escaping @MainActor () -> Void`

## P0463

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）versionCode 達到上限時靜默飽和

> 使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0464

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行）條件判斷錯誤：ext 為空時才加入 CFBundleTypeExtensions

> 在 `create_info_plist` 中，原本的程式碼無條件加入 `CFBundleTypeExtensions`，但修改後變成 `if association.ext.is_empty()` 才加入。這會導致當 `ext` 非空時（正常情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，造成檔案關聯失效。

**失敗情境**：使用者設定 `ext: ["png"]`，產生的 Info.plist 將缺少 `CFBundleTypeExtensions`，macOS 無法將 .png 檔案與應用程式關聯。

**建議**：移除 `if association.ext.is_empty()` 條件，改回無條件加入，或改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0465

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:126`，距錨點 5 行）高流量分支的計算可能導致上限下降

> 在 `lastCount >= 400000` 時，回傳 `Math.min(scaledIncrease, absoluteIncrease)`。其中 `scaledIncrease = Math.ceil(lastCount * 1.2)`，`absoluteIncrease = lastCount + 75000`。當 `lastCount` 大於 375000 時，`absoluteIncrease` 會小於 `scaledIncrease`，因此回傳 `lastCount + 75000`。這可能導致暖機上限的成長幅度低於預期，但仍在合理範圍內。建議確認此行為是否符合產品需求。

finding 片段：`const scaledIncrease = Math.ceil(lastCount * WARMUP_SCALING_TABLE.highVolume.maxScale); ⏎ const absoluteIncrease = lastCount + WARMUP_SCALING_TABLE.highVolume.maxAbsoluteIncrease; ⏎ return Math.min(scaledIncrease, absoluteIncrease);`

## P0466

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行）update 方法未處理可能找不到預訂的情況

> `update` 方法直接呼叫 `prisma.booking.update`，若找不到符合條件的預訂會拋出例外。在取消流程中，若預訂已被刪除或不存在，可能導致未處理的錯誤。建議使用 `update` 的 `rejectOnNotFound` 選項或改用 `updateMany` 並檢查 `count`。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## P0467

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 8 行）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## P0468

**GT**（func）Missing dependency in useEffect causes stale clamp detection

> The CommentContent component's useEffect hook has an empty dependency array, but it uses item.html to determine if content should be clamped. When a comment's HTML content changes (e.g., after an edit or when new data is loaded), the clamp detection won't re-run. This means the 'Show more' button may appear when it shouldn't or disappear when it should still be visible, creating a poor user experience. The dependency array should include item.html to ensure the clamp detection re-runs whenever the content changes.

GT 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 0 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `CommentContent` 中的 `useEffect` 僅在掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 載入或狀態變更）。若內容更新後高度改變，`isClamped` 不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0469

**GT**（rule）Missing Mozilla Public License header

> The rule requires that every .swift file begins with the exact Mozilla Public License header comment block at the top of the file. This file is missing the required header entirely.

GT 片段：`import ContentBlockingGenerator ⏎ @main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏執行緒安全問題

> `nonisolated(unsafe)` 標註表示開發者自行保證執行緒安全，但若 `ContentBlockerGenerator` 實例並非執行緒安全，可能導致資料競爭。建議確認其內部狀態或改為隔離。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0470

**GT**（rule）Line length exceeds SwiftLint limit

> This added/modified line is very likely >125 characters due to the long `NSLocalizedString` call and comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextStudies = NSLocalizedString("Settings.detailTextStudies", value: "%@ may install and run studies from time to time.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focus\" or \"Firefox Klar\").")`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:207`，距錨點 2 行）格式化字串參數數量不符

> `detailTextStudiesV2` 與 `detailTextRollouts` 的字串值包含一個 `%@` 佔位符，但 `SettingsTextFormatter` 中的 `formatStudiesText` 與 `formatRolloutsText` 方法僅傳入一個 `appName` 參數，數量相符。然而，`detailTextStudies` 與 `detailTextSendUsageData` 的原始字串也包含 `%@`，但未提供對應的格式化方法，可能導致呼叫端自行格式化時出錯。建議確認所有使用這些字串的程式碼都正確處理了格式化參數。

finding 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`
