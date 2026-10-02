# 盲標單 1：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-28-v140-exit/blind/labels-part1.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0001

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 37 行）對 base_job_template["variables"] 的型別假設可能導致執行期錯誤

> 在 `_fetch_work_pool` 中，原本有檢查 `isinstance(variables, dict)` 才指派給 `job_vars_schema`。移除檢查後，直接將 `base_job_template["variables"]` 指派給 `job_vars_schema`，但該值可能不是 dict（例如是 list 或 None）。後續程式碼若假設 `job_vars_schema` 是 dict（例如呼叫 `.items()` 或進行 dict 操作），會拋出 AttributeError 或 TypeError。建議保留型別檢查，或確保上游資料一定為 dict。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## P0002

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:41`，距錨點 16 行）測試依賴外部網路與 WebKit 非同步行為，可能導致不穩定

> `captureFrameAndOrigin` 使用真實的 `WKWebView` 載入 `https://example.com`，這引入了對外部網路的依賴。在 CI 環境中，網路可能不可用、被防火牆阻擋，或回應時間不穩定，導致測試逾時或失敗。此外，WebKit 的內部行為可能因版本而異，使得測試結果難以預測。

建議改為使用本機的測試伺服器（例如 `URLProtocol` mock 或 `WKWebView` 的 `loadHTMLString`）來提供可控的內容，避免外部依賴。

finding 片段：`// load a real https URL (use example.com to be safe) ⏎ webView.load(URLRequest(url: url))`

## P0003

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行）輔助函式缺少單元測試

> 新增的 `web/test/i18n-mock.ts` 包含多個輔助函式，但沒有對應的測試。這些函式將被多個測試檔案使用，若行為有誤可能影響大量測試。建議為這些輔助函式撰寫單元測試，涵蓋自訂翻譯、namespace 前綴、參數序列化等情境。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0004

**GT**（rule）Static property missing explicit access control modifier

> Rule 11 requires explicit access control on properties/methods. The modified static property `generator` is declared without an explicit access modifier (e.g., `private`, `internal`, `public`).

GT 片段：`// FXIOS-14548 ContentBlockerGenerator is not thread safe ⏎ nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）使用 nonisolated(unsafe) 可能隱藏資料競爭

> `generator` 被標註為 `nonisolated(unsafe) static let`，這表示編譯器不會檢查其執行緒安全性。如果 `ContentBlockerGenerator` 實例不是執行緒安全的，多個執行緒同時存取可能導致資料競爭。建議確認 `ContentBlockerGenerator` 是否為 Sendable，或改用其他隔離機制（如 actor 或鎖）。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0005

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行）回傳的 token 不是實際邀請 token

> `createInvite` 回傳的 `token` 改為 `newToken.identifier`，但 `identifier` 的值是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致 API 回傳的 `token` 欄位與 `inviteLink` 中的 token 不一致，且測試中 `expect(response.body.data.inviteLink).toContain(response.body.data.token)` 會失敗。應回傳 `token` 變數（即 `newToken.token`）或直接回傳 `token`。

finding 片段：`token: newToken.identifier,`

## P0006

**GT**（rule）File association uses expect instead Result

> The code uses expect() to unwrap an Option when the name field is None, causing a panic instead of returning a Result type that allows callers to handle the error gracefully.

GT 片段：`dict.insert( ⏎ "CFBundleTypeName".into(), ⏎ association ⏎ .name`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 13 行）CFBundleTypeExtensions 條件判斷邏輯錯誤

> 在 `create_info_plist` 中，原本無條件插入 `CFBundleTypeExtensions`，現在改為 `if association.ext.is_empty()` 才插入。這會導致當 `ext` 非空時（最常見的情況），`CFBundleTypeExtensions` 不會被加入 Info.plist，使得 macOS 無法將檔案副檔名與應用程式關聯。

**失敗情境**：使用者設定 `fileAssociations` 且 `ext` 不為空（例如 `["png"]`），產生的 app bundle 將缺少 `CFBundleTypeExtensions`，導致雙擊該副檔名的檔案時無法開啟應用程式。

**建議修法**：將條件改為 `if !association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0007

**GT**（rule）User-facing change added without a corresponding .changes entry

> This PR introduces a user-facing functionality change (adding a new `Flatpak` bundle type to the public config surface) but the diff does not include any new markdown change file under the `.changes/` directory (covector format) to document the change and version bump. Rule 13 requires such a change file for releasable functionality changes.

GT 片段：`+  /// The Flatpak bundle (.flatpak). ⏎ +  Flatpak,`

**finding**（`crates/tauri-utils/src/config.rs:180`，距錨點 33 行）Flatpak 的 Display 實作大小寫不一致

> 在 `Display for BundleType` 中，新增的 `Flatpak` 變體回傳 `"Flatpak"`（首字母大寫），而其他變體均回傳小寫字串（如 `"nsis"`、`"app"`、`"dmg"`）。這可能導致序列化或顯示時的不一致，若此 Display 用於產生設定檔或 CLI 輸出，可能造成問題。建議改為 `"flatpak"` 以維持一致性。

finding 片段：`Self::Flatpak => "Flatpak",`

## P0008

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴與後端後綴不一致

> 前端 `getStatEndpointUrl` 將 `config.version` 加在端點名稱**前面**（例如 `v2_api_kpis`），但後端 `tinybird.js` 是加在**後面**（`api_kpis_v2`）。這會導致前端在設定 `version: 'v2'` 時呼叫不存在的端點，造成 404。

建議統一命名規則，例如都使用後綴 `_v2`。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0009

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行）get_plan_bulk 回傳值型別不一致：失敗時設為 None

> 在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（包括新的 `get_plan_bulk_with_cache`）預期每個值都是 `SubscriptionPlan`（TypedDict）。這會導致下游在存取 `plan` 或 `expiration_date` 時發生 `AttributeError` 或 `TypeError`。

**失敗情境**：如果 billing API 回傳的某個 tenant 資料格式錯誤，`get_plan_bulk` 會將該 tenant 對應的值設為 `None`。之後 `get_plan_bulk_with_cache` 將此結果合併到 `tenant_plans` 並回傳，呼叫端若嘗試讀取 `result[tenant_id]['plan']` 就會崩潰。

**建議**：不要將失敗的 tenant 設為 `None`，而是直接跳過（不加入 `results`），或記錄錯誤後繼續。這樣可以保持回傳值型別一致。

finding 片段：`results[tenant_id] = None`

## P0010

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 3 行）移除 slack.listen() 可能導致 Slack 服務無法接收事件

> 原本在 `Promise.all` 中有 `slack.listen()`，但修改後被移除。若 Slack 服務需要監聽特定事件（例如發佈通知），移除後可能導致功能失效。請確認 Slack 服務是否已改為其他方式初始化，或此移除是否為有意為之。

finding 片段：`scheduling.init(),`

## P0011

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 23 行）跨欄位驗證誤用 field_validator，導致 bucket_folder 與 bucket 名稱相同時無法正確驗證

> 在 `_bucket_folder_suffix` 中，使用 `info.data.get("bucket")` 來取得 bucket 欄位，但 `field_validator` 的 `info.data` 只包含已驗證的欄位，且欄位驗證順序不保證 bucket 先被驗證。若 bucket 欄位在 bucket_folder 之後才驗證，則 `info.data.get("bucket")` 會是 None，導致跨欄位驗證失效。應改用 `model_validator(mode='after')` 來進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0012

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行）命名空間格式變更可能影響其他測試

> 此 diff 將 `namespace Microsoft.AspNetCore.Components.Server.Circuits;` 改為 block 形式，並將類別包在 namespace 內。這可能影響檔案中其他測試類別的命名空間解析，但若檔案內只有此類別則無影響。建議確認此變更是否必要，或是否為意外格式變更。

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ { ⏎ public class ServerComponentDeserializerTest ⏎ {`

## P0013

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯中遺失變數 {newsletterName}

> 原文為 "{memberEmail} will no longer receive {newsletterName} newsletter."，翻譯改為 "{memberEmail}将不会再收到新闻信。"，遺漏了 {newsletterName} 變數。這會導致使用者看到的訊息缺少新聞信名稱，且可能造成 i18n 函式庫在插入變數時出現錯誤或顯示不完整。建議保留變數，例如："{memberEmail}将不会再收到{newsletterName}新闻信。"

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0014

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）自動遞增時未處理 versionCode 為 0 的情況

> 若 `tauri.properties` 中現有的 versionCode 為 0（可能因先前錯誤或手動修改），自動遞增會得到 1，但這可能不符合預期。建議在讀取後驗證舊值是否合法（>=1）。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0015

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 2 行）Popover 的 hover 觸發可能導致點擊事件無法觸發

> 在桌面端，Popover 的開啟依賴於 onMouseEnter 和 onMouseLeave。當使用者將滑鼠移到觸發按鈕上時，Popover 會開啟，但當滑鼠移入 PopoverContent 時，由於 onMouseLeave 觸發，Popover 會立即關閉，導致使用者無法點擊隱藏項目。這是因為 PopoverContent 的 onMouseEnter 和 onMouseLeave 雖然有設定，但可能因為事件傳遞或元件結構問題而無法正確維持開啟狀態。建議改用 Radix Popover 的 hover 模式或使用延遲關閉機制，確保滑鼠在 PopoverContent 上時不會關閉。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0016

**GT**（func）RetainedFileCountLimit allows zero value violating positive-only constraint

> The RetainedFileCountLimit property validation was changed from rejecting values <= 0 to only rejecting values < 0, which now allows zero as a valid value. However, both the XML documentation and the error message explicitly state that this must be a 'positive' value, and zero is not positive. The remarks indicate this controls maximum retained file count - a value of zero would mean no log files are retained, which could lead to complete log loss. This violates the documented API contract and creates a dangerous configuration scenario where all logs could be immediately discarded.

GT 片段：`public int? RetainedFileCountLimit ⏎ { ⏎ get { return _retainedFileCountLimit; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/AzureFileLoggerOptions.cs:53`，距錨點 0 行）RetainedFileCountLimit 驗證條件變更可能允許 0 值

> 原本的驗證條件 `value <= 0` 會拒絕 0 和負數，但變更後只拒絕負數，允許 0。若設定為 0，可能導致不保留任何檔案，造成資料遺失或非預期行為。建議確認 0 是否為有效值，若不是，應維持原本的 `<= 0` 驗證。

finding 片段：`if (value < 0)`

## P0017

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 0 行）動態切換欄位名稱可能導致資料殘留或驗證問題

> 根據 posture 動態決定使用 `trigger.after` 或 `trigger.expect` 欄位。當 posture 從 Reactive 切換到 Proactive 時，原本在 `trigger.expect` 的值不會自動轉移到 `trigger.after`，可能導致資料不一致。此外，若兩個欄位都有值，切換時可能造成混淆。建議在切換 posture 時清除或轉移相關欄位的值，或使用固定的欄位名稱並在提交時轉換。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0018

**GT**（func）Unused variable 'elecount' causes build failure with -Werror

> The variable 'elecount' is declared and incremented in the QUICKLIST encoding branch (line 1236: 'elecount += node->count') but is never used after the PR changed the calculation from 'elesize/elecount' to 'elesize/samples'. This creates an unused-but-set variable which triggers compiler warnings under -Wall (enabled in Makefile) and causes build failures when compiling with -Werror flag. This violates AGENTS.MD Rule #4 which requires the codebase to compile without warnings when REDIS_CFLAGS="-Werror" is enabled.

GT 片段：`size_t elesize = 0, elecount = 0, samples = 0; ⏎ ... ⏎ if (o->encoding == OBJ_ENCODING_QUICKLIST) { ⏎ quicklist *ql = o->ptr;`

**finding**（`src/object.c:1239`，距錨點 0 行）quicklist 取樣計算使用 samples 而非 elecount 可能導致估算偏差

> 在 quicklist 的記憶體估算中，原本使用 `elesize/elecount*ql->count`，現在改為 `elesize/samples*ql->count`。`samples` 是走訪的節點數，而 `elecount` 是這些節點中的元素總數。若每個節點包含多個元素（例如 listpack 節點），使用 `samples` 會低估平均元素大小，導致整體估算不準確。建議改回使用 `elecount`，或確認此變更為有意為之。

finding 片段：`asize += (double)elesize/samples*ql->count;`

## P0019

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有除法或轉換可能出錯）。建議回傳 `emailCount` 或一個明確的常數（如 `Number.MAX_SAFE_INTEGER`），並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0020

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:462`，距錨點 0 行）V2 啟用時 static_subpath 指派錯誤

> 在 `create_ui_app` 中，當 `v2_enabled` 為 True 時，`static_subpath` 被指派為 `prefect.__ui_static_subpath__`（V1 的子路徑），而 `source_static_path` 為 `prefect.__ui_v2_static_path__`。這導致後續 `create_ui_static_subpath` 會將 V2 的靜態檔案複製到 V1 的子路徑，可能覆蓋 V1 檔案或造成路徑衝突。應將 `static_subpath` 指派為 `prefect.__ui_v2_static_subpath__`。

finding 片段：`static_subpath = prefect.__ui_static_subpath__`

## P0021

**GT**（rule）Interface used instead of type

> The rule requires using 'type' keyword for type declarations, but the code uses 'interface' declaration instead

GT 片段：`interface TranslationMap extends Record<string, string | string[]> {}`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 6 行）`createTFunction` 未處理 `returnObjects` 選項，可能導致依賴此功能的測試失敗

> 在舊的全域 mock 中，當 `options.returnObjects` 為真時，會回傳一個陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`）。新的 `createTFunction` 完全沒有檢查 `returnObjects`，因此會回傳字串。若任何測試或元件依賴此行為（例如使用 `returnObjects: true` 來取得多個翻譯），測試將失敗。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，或確認沒有測試使用此選項。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## P0022

**GT**（rule）Interface used instead of type

> The rule requires using 'type' keyword for type declarations, but the code uses 'interface' declaration instead

GT 片段：`interface TranslationMap extends Record<string, string | string[]> {}`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 6 行）輔助函式缺少單元測試

> 新增的 `web/test/i18n-mock.ts` 包含多個輔助函式，但沒有對應的測試。這些函式將被多個測試檔案使用，若行為有誤可能影響大量測試。建議為這些輔助函式撰寫單元測試，涵蓋自訂翻譯、namespace 前綴、參數序列化等情境。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0023

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email.trim() 可能導致驗證邏輯不一致

> 在 submitHandler 中將 email 先 trim 再傳給 onSubmit，但上游的驗證（如 isValidEmail）可能是在未 trim 的狀態下進行。若使用者輸入前後有空白，驗證可能通過（例如 isValidEmail 自行 trim）或失敗（若未 trim），但最終送出的 email 已被 trim，可能造成行為不一致。建議確認 isValidEmail 的實作，並在驗證前統一 trim。

finding 片段：`onSubmit({email: email.trim()});`

## P0024

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:99`，距錨點 0 行）移除 HashAlgorithm::Sha256 的 cfg(target_os = "windows") 條件可能影響跨平台行為

> 原本 `HashAlgorithm::Sha256` 僅在 Windows 上啟用，現在移除條件編譯後，所有平台皆可使用 Sha256。這可能是為了修正跨平台雜湊驗證問題，但需確認在其他平台（如 Linux、macOS）上使用 Sha256 是否會造成行為變更或與既有邏輯衝突。

**建議**：確認此變更是否為預期，並檢查是否有其他程式碼依賴此條件編譯。

finding 片段：`pub enum HashAlgorithm { ⏎ Sha256, ⏎ Sha1, ⏎ }`

## P0025

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:46`，距錨點 6 行）變數不存在時僅記錄警告，可能導致資料遺失

> 當 `variable_pool.get(selector)` 回傳非 `Variable` 時，僅記錄警告並跳過，但該變數可能已從節點輸出中標記為更新，卻未持久化，導致資料不一致。建議考慮拋出例外或採取其他補救措施。

finding 片段：`if not isinstance(variable, Variable): ⏎ logger.warning( ⏎ "Conversation variable not found in variable pool. selector=%s", ⏎ selector,`

## P0026

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:99`，距錨點 0 行）移除 HashAlgorithm::Sha256 的 cfg 條件可能影響跨平台編譯

> 原本 `HashAlgorithm::Sha256` 帶有 `#[cfg(target_os = "windows")]`，表示該變體僅在 Windows 上可用。移除後，Sha256 將在所有平台上可用，這可能是有意為之（例如其他平台也需要使用 SHA-256），但也可能導致非 Windows 平台出現未預期的編譯或行為變化。

建議：確認所有使用 `HashAlgorithm::Sha256` 的程式碼路徑是否已正確處理跨平台情況。

finding 片段：`pub enum HashAlgorithm { ⏎ Sha256, ⏎ Sha1, ⏎ }`

## P0027

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 4 行）GTK 腳本存在性檢查邏輯反轉

> 原本的邏輯是「若檔案不存在，則下載並寫入」，但修改後變成「若檔案存在，則寫入內嵌內容」。這會導致：
1. 當檔案不存在時，不會建立該檔案，後續執行可能因缺少腳本而失敗。
2. 當檔案已存在時，會用內嵌內容覆蓋，可能破壞使用者自訂的腳本。

建議改回 `if !gtk.exists()` 的條件。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0028

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）truncate 後未更新 AOF 檔案大小相關的狀態

> truncate 成功後，程式僅將檔案描述子 seek 到結尾，但未更新 server 中可能記錄的 AOF 檔案大小或 offset 等狀態。這可能導致後續 AOF 寫入時發生錯誤或覆蓋。建議檢查是否有相關狀態需要更新。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0029

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 輸出執行資訊，應改用 logger

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將訊息輸出到 stdout，可能污染正式環境的 log 或影響效能。建議改用專案的 logger（例如 `logging.getLogger(__name__)`）並設定適當的 log level。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0030

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行）linuxdeploy 下載 URL 使用 arch 而非 linuxdeploy_arch，可能導致 i686 架構下載錯誤

> 原本下載 linuxdeploy 時使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為使用 `arch`。若 `arch` 為 `i686`，則會嘗試下載 `linuxdeploy-i686.AppImage`，但實際檔案名稱可能為 `linuxdeploy-i383.AppImage`，導致下載失敗。建議保留 `linuxdeploy_arch` 變數。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0031

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能接受無效資料

> 此函式僅檢查 input 是否為物件且 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）或 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 zod 或其他 schema 驗證庫完整驗證所有欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0032

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）createStringObjectFromLongLong 建立的物件未釋放，造成記憶體洩漏

> `argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 alsoPropagate 之後沒有對其呼叫 decrRefCount。雖然 alsoPropagate 可能會複製參照，但此處建立的物件在函式結束後不再使用，應釋放以避免記憶體洩漏。

建議在 alsoPropagate 呼叫後加入 `decrRefCount(argv[2]);`。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0033

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）versionCode 達到上限時靜默飽和

> 使用 `saturating_add` 在 versionCode 達到 `u32::MAX` 時會停留在最大值，但 Android 的 versionCode 上限是 2100000000。如果超過此上限，Google Play 會拒絕上傳。建議在遞增前檢查是否超過上限，並提供明確的錯誤訊息。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0034

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:11`，距錨點 8 行）React Scan 載入失敗時回傳的元件可能導致渲染錯誤

> 在 `lazy` 的 `catch` 中回傳 `{ default: () => null }`，但 `ReactScan` 元件本身可能接受 props 或依賴 context。若 `ReactScan` 在渲染時需要特定 props 或 context，這個 fallback 元件可能無法滿足，導致錯誤。此外，`lazy` 的 factory 必須回傳一個 Promise，其 resolve 值必須是 `{ default: Component }`，此處符合，但 fallback 元件若被渲染且內部有 hook 或依賴，可能造成問題。建議改為回傳一個明確的 fallback 元件，或直接讓錯誤拋出並由 error boundary 處理。

finding 片段：`return { default: () => null }`

## P0035

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 3 行）Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證

> 當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0036

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:630`，距錨點 18 行）寫入 tauri.properties 的時機可能造成 CI 中版本碼不一致

> `generate_tauri_properties` 在 build 和 dev 命令中被呼叫，但若 `tauri.properties` 被 `.gitignore` 忽略（如預設），則在 CI 環境中每次建置都會從 1 開始，導致版本碼無法持續遞增。文件雖建議移除 `.gitignore` 條目，但未強制，可能造成使用者混淆。建議在啟用此功能時檢查檔案是否被忽略，或提供更明確的警告。

finding 片段：`let app_tauri_properties_path = config.project_dir().join("app").join("tauri.properties");`

## P0037

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行）bootstrapDependencies 標記 @MainActor 但未處理非 MainActor 呼叫

> 將 `bootstrapDependencies` 標記為 `@MainActor` 後，所有呼叫端都必須在 MainActor 上執行。但仍有部分測試類別（如 `LaunchScreenViewModelTests`）未標記 `@MainActor`，且呼叫時未使用 `await`，可能導致編譯錯誤或 runtime 問題。建議全面檢查所有呼叫端，確保在 MainActor 上呼叫或使用 `await MainActor.run`。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## P0038

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:292`，距錨點 33 行）get_plan_bulk 回傳值型別不一致：失敗時設為 None

> 在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端（包括新的 `get_plan_bulk_with_cache`）預期每個值都是 `SubscriptionPlan`（TypedDict）。這會導致下游在存取 `plan` 或 `expiration_date` 時發生 `AttributeError` 或 `TypeError`。

**失敗情境**：如果 billing API 回傳的某個 tenant 資料格式錯誤，`get_plan_bulk` 會將該 tenant 對應的值設為 `None`。之後 `get_plan_bulk_with_cache` 將此結果合併到 `tenant_plans` 並回傳，呼叫端若嘗試讀取 `result[tenant_id]['plan']` 就會崩潰。

**建議**：不要將失敗的 tenant 設為 `None`，而是直接跳過（不加入 `results`），或記錄錯誤後繼續。這樣可以保持回傳值型別一致。

finding 片段：`results[tenant_id] = None`

## P0039

**GT**（func）Double-counting last listpack in STREAM memory calculation

> The stream memory estimation algorithm samples the first N listpacks, computes their average size, and then explicitly adds the last listpack's actual size separately (line 1336). The multiplication at line 1330 should use `(s->rax->numele-1)` to account for all listpacks except the last one, but it incorrectly uses `s->rax->numele` without the subtraction. This causes the last listpack to be counted twice: once in the averaged estimate and once with its actual size, resulting in inflated memory usage reports for streams with more elements than the sample size.

GT 片段：`if (s->rax->numele <= samples) { ⏎ asize += lpsize; ⏎ } else { ⏎ if (samples) lpsize /= samples; /* Compute the average. */`

**finding**（`src/object.c:1330`，距錨點 0 行）stream 記憶體估算可能重複計算最後一個節點

> 在 stream 的記憶體估算中，原本使用 `s->rax->numele-1` 來計算平均 listpack 大小乘以節點數，但此 PR 改為 `s->rax->numele`。這可能導致最後一個 listpack 被重複計算，因為在取樣迴圈中已經包含了最後一個節點。

**失敗情境**：當 stream 的節點數大於 sample_size 時，最後一個節點會被包含在取樣中，然後又用 `numele` 相乘，導致高估。

**建議**：確認 `numele` 的定義是否包含最後一個節點，若包含則應維持 `-1`。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0040

**GT**（func）Test completes without waiting for async image download

> The test was converted from async to synchronous but the expectation and wait statement were removed. This causes the test to complete immediately without waiting for the asynchronous image download callback to execute. The XCTAssert statements inside the completion handler will never be verified, resulting in false positive test passes even if the image download fails or produces incorrect results. This is a critical testing bug that undermines test reliability.

GT 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ guard let imageData = try? dataFor(type: assetType) else {`

**finding**（`BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12`，距錨點 0 行）測試方法從 async 改為同步可能導致執行緒阻塞或逾時

> 原本的 async 測試方法使用 `await fulfillment(of:timeout:)` 等待非同步完成，現在改為同步方法並使用 `wait(for:timeout:)`。然而，`startMockImageServer` 原本標記為 `@MainActor`，現在移除了該標記，且測試方法本身未標註 `@MainActor`。若 `startMockImageServer` 內部需要在主執行緒執行（例如 GCDWebServer 初始化），在同步測試方法中直接呼叫可能導致主執行緒阻塞或崩潰。建議確認 GCDWebServer 的執行緒需求，或將測試方法標註為 `@MainActor` 並使用 `wait(for:timeout:)` 的正確變體。

finding 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() {`

## P0041

**GT**（rule）Traditional namespace declaration used

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`namespace Microsoft.AspNetCore.Components.Forms ⏎ { ⏎ /// <summary> ⏎ /// Displays the display name for a specified field, reading from <see cref="DisplayAttribute"/>`

**finding**（`src/Components/Web/src/Forms/DisplayName.cs:46`，距錨點 30 行）DisplayName 元件在 For 參數變更時可能不會更新顯示名稱

> 在 `SetParametersAsync` 中，只有當 `For` 表達式與 `_previousFieldAccessor` 不同時才會重新計算顯示名稱。然而，如果 `For` 表達式相同但底層模型屬性的顯示名稱因動態變更（例如資源檔更新或屬性變更）而改變，元件不會重新渲染。這可能導致顯示名稱過時。建議在每次 `SetParametersAsync` 時都重新計算，或提供一個方法來強制更新。

finding 片段：`if (For != _previousFieldAccessor) ⏎ { ⏎ var newDisplayName = ExpressionMemberAccessor.GetDisplayName(For); ⏎ `

## P0042

**GT**（func）Incorrect conditional operator in onboarding redirect logic

> The conditional logic for redirecting users with pending invites uses OR (||) instead of AND (&&). This means users will be redirected to '/onboarding/personal/settings' if they have a pending invite OR if onboarding-v3 is enabled, rather than requiring both conditions. This breaks the normal onboarding flow - any user with onboarding-v3 enabled will be incorrectly redirected to personal settings regardless of whether they have pending invites. The intended behavior was to only redirect users who have both onboarding-v3 enabled AND a pending invite.

GT 片段：`// Determine which onboarding path to use ⏎ const onboardingV3Enabled = await featuresRepository.checkIfFeatureIsEnabledGlobally("onboarding-v3"); ⏎ const hasPendingInvite = await MembershipRepository.hasPendingInviteByUserId({ userId }); ⏎ if (hasPendingInvite || onboardingV3Enabled) {`

**finding**（`packages/features/auth/lib/onboardingUtils.ts:69`，距錨點 0 行）條件由 AND 改為 OR 可能改變既有流程

> 原本只有在同時有 pending invite 且 onboarding-v3 啟用時才導向 personal/settings，現在改成任一條件成立即導向。若 onboarding-v3 啟用但用戶沒有 pending invite，原本會繼續其他流程，現在會直接導向 personal/settings。請確認此行為變更是否符合預期。

finding 片段：`if (hasPendingInvite || onboardingV3Enabled) {`

## P0043

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:513`，距錨點 0 行）findManyIncludeWorkflowRemindersAndReferences 的 where 條件可能遺漏時區處理

> 在 `handleCancelBooking` 中，`findManyIncludeWorkflowRemindersAndReferences` 的 `where` 條件使用 `gte: bookingToDelete.startTime`，但 `bookingToDelete.startTime` 是 Date 物件，可能包含時區資訊。若資料庫儲存的是 UTC，而此處傳入的 Date 未正確轉換，可能導致查詢結果不正確。

建議：確認 `bookingToDelete.startTime` 的時區處理，必要時使用 UTC 時間進行比較。

finding 片段：`const allUpdatedBookings = await bookingRepository.findManyIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ recurringEventId: bookingToDelete.recurringEventId, ⏎ startTime: {`

## P0044

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴順序與後端不一致

> 前端 `getStatEndpointUrl` 將 `config.version` 放在 endpointName 之前（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是放在之後（`${pipeName}_${version}`）。例如 version='v2'、endpointName='api_kpis' 時，前端會呼叫 `v2_api_kpis`，後端會呼叫 `api_kpis_v2`，導致 404。請統一為後端的 `api_kpis_v2` 格式。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0045

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）路徑比較未正規化尾端分隔符，可能誤判目錄是否已包含

> 在比較 `Path.GetFullPath(dir)` 與 `certDirFullPath` 時，若其中一個路徑以目錄分隔符結尾（例如 `/usr/local/share/certs/` 與 `/usr/local/share/certs`），`Path.GetFullPath` 不會移除尾端分隔符，導致 `string.Equals` 回傳 false，即使實際上是同一目錄。這會造成程式誤以為憑證目錄尚未加入 SSL_CERT_DIR，而重複輸出建議訊息。

**建議**：在比較前使用 `Path.TrimEndingDirectorySeparator` 或 `Path.GetFullPath` 後再 `TrimEnd` 目錄分隔符，或使用 `Path.GetRelativePath` 判斷是否為同一路徑。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0046

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行）使用 `||` 處理數字 0 會錯誤顯示 'None'

> 在顯示 `run_count` 時使用 `taskRun.run_count || 0`，若 `run_count` 為 0（合法值），則會顯示 0，但若 `run_count` 為 null 或 undefined，也會顯示 0，可能無法區分。建議使用 `??` 運算子：`taskRun.run_count ?? 0`。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## P0047

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行）moduleLoader 的 token 可能與綁定 token 不一致

> 在 `moduleLoader` 中，`token` 被設定為 `moduleToken`，但 `bindModuleToClassOnToken` 的 `token` 參數是 `FLAGS_DI_TOKENS.FEATURES_REPOSITORY`。這可能導致使用 `moduleLoader.token` 來取得實例時，實際上是取得模組 token 而非服務 token，造成型別或實例錯誤。建議確認 `moduleLoader.token` 應該回傳服務 token 還是模組 token，並保持一致性。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## P0048

**GT**（rule）Line length exceeds SwiftLint limit

> This added line is very likely >125 characters due to the long `NSLocalizedString` call, long value string, and long comment string, violating the SwiftLint line_length rule referenced by Rule 2.

GT 片段：`static let detailTextRollouts = NSLocalizedString("Settings.detailTextRollouts", value: "%@ will improve features, performance, and stability between updates. Changes applied remotely.", comment: "Description associated to the Rollouts toggle on the settings screen. %@ is the app name (for example \`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:207`，距錨點 2 行）格式化字串參數數量不符

> `detailTextStudiesV2` 與 `detailTextRollouts` 的字串值包含一個 `%@` 佔位符，但 `SettingsTextFormatter` 中的 `formatStudiesText` 與 `formatRolloutsText` 方法僅傳入一個 `appName` 參數，數量相符。然而，`detailTextStudies` 與 `detailTextSendUsageData` 的原始字串也包含 `%@`，但未提供對應的格式化方法，可能導致呼叫端自行格式化時出錯。建議確認所有使用這些字串的程式碼都正確處理了格式化參數。

finding 片段：`static let detailTextStudiesV2 = NSLocalizedString("Settings.detailTextStudies.v2", value: "%@ randomly selects users to test features, which improves quality for everyone.", comment: "Description associated to the Studies toggle on the settings screen. %@ is the app name (for example \"Firefox Focu`

## P0049

**GT**（func）Reply threading broken for nested comments due to incorrect in_reply_to_id

> The submit function uses `parent.id` as `in_reply_to_id` instead of `openForm.in_reply_to_id`. For nested replies (replying to a reply), these values differ: `openForm.in_reply_to_id` points to the specific comment being replied to, while `parent.id` points to the top-level parent comment. Using `parent.id` breaks the reply chain, causing nested replies to be incorrectly threaded to the wrong comment. This destroys the conversation hierarchy and makes it impossible to track which comment a user is actually replying to in multi-level discussions.

GT 片段：`const submit = useCallback(async ({html}) => { ⏎ // Send comment to server ⏎ await dispatchAction('addReply', { ⏎ parent: parent,`

**finding**（`apps/comments-ui/src/components/content/forms/reply-form.tsx:30`，距錨點 0 行）in_reply_to_id 改為 parent.id 可能影響回覆巢狀結構

> 原本使用 `openForm.in_reply_to_id`，現在改為 `parent.id`。如果 openForm 代表的是回覆某個回覆（即巢狀回覆），則原本的 in_reply_to_id 可能指向上一層回覆的 id，而 parent.id 可能指向頂層評論的 id。這可能導致回覆的巢狀結構不正確。建議確認 parent 的定義是否為直接父評論，並確保此變更符合預期。

finding 片段：`in_reply_to_id: parent.id,`

## P0050

**GT**（func）Incorrect translation lookup order breaks backward compatibility with simple key translations

> The `createTFunction` implementation now checks `translations[fullKey]` (with namespace prefix) before `translations[key]` (without namespace). This inverts the original lookup order documented in the function comment. When tests provide translations like `{ 'operation.copy': 'Copy' }` and components use `useTranslation('common')`, the function will first look for `'common.operation.copy'`, fail to find it, then check `'operation.copy'` and find it. However, if no match is found with namespace and the key doesn't exist without namespace either, it returns the namespaced fallback string. This breaks tests that previously worked by matching keys without namespaces first, particularly affecting tests in files like `input-with-copy/index.spec.tsx` that provide simple key translations.

GT 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 0 行）`createTFunction` 未處理 `returnObjects` 選項，可能導致依賴此功能的測試失敗

> 在舊的全域 mock 中，當 `options.returnObjects` 為真時，會回傳一個陣列（例如 `[`${key}-feature-1`, `${key}-feature-2`]`）。新的 `createTFunction` 完全沒有檢查 `returnObjects`，因此會回傳字串。若任何測試或元件依賴此行為（例如使用 `returnObjects: true` 來取得多個翻譯），測試將失敗。建議在 `createTFunction` 中加入對 `returnObjects` 的處理，或確認沒有測試使用此選項。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) { ⏎ return (key: string, options?: Record<string, unknown>) => { ⏎ const ns = (options?.ns as string | undefined) ?? defaultNs ⏎ const fullKey = ns ? `${ns}.${key}` : key`

## P0051

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:52`，距錨點 0 行）generate_github_alternative_url 不再使用替代 URL，可能導致下載失敗

> 在 `generate_github_alternative_url` 中，原本會將 `alt_url`（替代 URL）作為回傳值，但修改後改為回傳原始的 `url`。這使得函式失去其設計目的（提供 GitHub 下載的替代鏡像），當原始 URL 無法存取時，將無法自動切換到替代來源，可能導致下載失敗。

建議：確認此修改是否為預期行為。若需保留替代 URL 功能，應回傳 `alt_url`；若不再需要，應考慮移除整個函式或調整其邏輯。

finding 片段：`.map(|_alt_url| { ⏎ ( ⏎ ureq::Agent::config_builder() ⏎ .user_agent(BUNDLER_USER_AGENT)`

## P0052

**GT**（func）Schema validation never executes due to impossible condition

> The conditional check was changed from OR (`||`) to AND (`&&`) when checking file extensions. A file path cannot have both '.json' AND '.json5' extensions simultaneously, making this condition impossible to satisfy. As a result, JSON schema validation is completely bypassed for all configuration files, allowing invalid configurations to pass through undetected. This could lead to runtime errors or unexpected behavior when the invalid config is later used by the application.

GT 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5")) ⏎ {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:201`，距錨點 0 行）條件判斷邏輯修正可能改變驗證範圍

> 原本的條件是 `extension == json || extension == json5`，現在改為 `extension == json && extension == json5`，這會使得只有副檔名同時為 json 和 json5 的檔案才會進行驗證，實際上不可能發生，因此驗證可能永遠不會執行。請確認此變更是否為預期，或應改回 `||`。

finding 片段：`if config_path.extension() == Some(OsStr::new("json")) ⏎ && config_path.extension() == Some(OsStr::new("json5"))`

## P0053

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 12 行）selector 長度檢查可能不完整

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## P0054

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這會導致同一事件在不同 webhook 版本中收到不同的預設值，可能造成下游系統誤判。建議統一預設值，或明確在 DTO 中必填此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0055

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行）listFeaturesForUser 過濾條件反轉，回傳未啟用的功能

> 在 `listFeaturesForUser` 中，原本的 `.filter((state) => state.globalEnabled)` 被改為 `.filter((state) => !state.globalEnabled)`，這會導致只回傳 `globalEnabled` 為 false 的功能，與方法註解「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」矛盾。這將使前端無法取得任何已啟用的功能，造成功能失效。

**建議修法**：將條件改回 `state.globalEnabled`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## P0056

**GT**（func）Wrong stored-key pointer used for dict lookup after keyDup

> In dictSetKeyAtLink when newItem is 0 and *link is NULL, the function attempts to find the link by calling dictFindLink with addedKey. However, addedKey is the result of keyDup (if keyDup is configured) or the original stored-key, and dictFindLink expects a lookup key. Additionally, after keyDup, addedKey may point to a newly allocated object with a different address than the original key in the dict, causing the lookup to fail even with pointer comparison. This will cause the assertion to fail, or worse, result in corrupted dict state if the assertion is disabled.

GT 片段：`/* Setting key of existing dictEntry (newItem == 0)*/ ⏎ if (*link == NULL) { ⏎ *link = dictFindLink(d, addedKey, NULL); ⏎ assert(*link != NULL);`

**finding**（`src/dict.c:890`，距錨點 21 行）dictSetKeyAtLink 中 keyDup 可能重複轉換 key

> 在 `dictSetKeyAtLink` 中，`addedKey` 是透過 `d->type->keyDup(d, key)` 產生的。若 keyDup 實作假設輸入是 lookup key，但此處傳入的是 stored-key，可能導致錯誤。需要確認所有 keyDup 實作是否相容於 stored-key。

finding 片段：`void *addedKey = (d->type->keyDup) ? d->type->keyDup(d, key) : key;`

## P0057

**GT**（rule）Undefined identifier True used instead

> The rule requires all TypeScript code to compile successfully with strict mode enabled. The code uses `True` (Python-style boolean) which is not a valid JavaScript/TypeScript identifier, causing a compilation error.

GT 片段：`const handleJSONSchemaChange = useCallback((value: string) => { ⏎ const isEmpty = value == null || value.trim() === '' ⏎ if (isEmpty) { ⏎ handlePayloadChange('json_schema')(undefined)`

**finding**（`web/app/components/app/configuration/config-var/config-modal/index.tsx:138`，距錨點 0 行）回傳值 True 未定義，將導致 ReferenceError

> 在 handleJSONSchemaChange 中，成功解析 JSON 後回傳了 `True`（Python 風格），但 JavaScript 中應為 `true`。由於 `True` 未定義，執行到此處會拋出 ReferenceError，導致整個函式失敗，且可能影響後續邏輯。

建議改為 `return true` 或直接省略回傳值。

finding 片段：`handlePayloadChange('json_schema')(value) ⏎ return True`

## P0058

**GT**（func）Incomplete cache clearing during hot reload causes stale display names

> The ClearCache method only clears _memberInfoCache but fails to clear _displayNameCache (line 85). During hot reload scenarios when metadata updates occur, the HotReloadManager triggers ClearCache to ensure fresh metadata is loaded. However, with _displayNameCache not being cleared, the component will continue to display stale display names from cached MemberInfo objects even after the attributes have been modified in code. This breaks the hot reload functionality for DisplayAttribute and DisplayNameAttribute changes, requiring developers to restart the application to see attribute changes take effect.

GT 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

**finding**（`src/Components/Web/src/Forms/ExpressionMemberAccessor.cs:83`，距錨點 0 行）Hot Reload 時未清除顯示名稱快取，可能導致顯示名稱不更新

> `ClearCache` 方法僅清除了 `_memberInfoCache`，但未清除 `_displayNameCache`。當 Hot Reload 應用程式碼變更時，如果屬性的顯示名稱（例如透過 `DisplayAttribute` 或 `DisplayNameAttribute`）發生變化，快取中的舊值將繼續被使用，導致顯示名稱不正確。建議同時清除 `_displayNameCache`。

finding 片段：`private static void ClearCache() ⏎ { ⏎ _memberInfoCache.Clear(); ⏎ }`

## P0059

**GT**（func）Race detection compares lengths instead of ID sets allowing double-firing

> The race detection logic compares only the count of deleted IDs rather than verifying the exact set of IDs match. This comparison using len(deleted_ids) != len(firing_ids) will incorrectly pass when a worker deletes the same number of firings but with different IDs than expected. For example, if firing_ids is {A, B} but deleted_ids is {C, D}, both have length 2 so the check passes and the trigger fires incorrectly. The correct implementation should use set equality (deleted_ids != firing_ids) to ensure the exact same firings were claimed, preventing spurious trigger firings when workers race.

GT 片段：`# Clear by firing id, and only proceed if we won the race to claim them. ⏎ # This prevents double-firing when multiple workers evaluate concurrently. ⏎ deleted_ids = await clear_child_firings( ⏎ session, trigger, firing_ids=list(firing_ids)`

**finding**（`src/prefect/server/events/triggers.py:396`，距錨點 0 行）刪除數量檢查可能因重複 firing_ids 而誤判

> `firing_ids` 可能包含重複的 ID（例如同一個 child firing 被多次加入），但 `clear_child_firings` 回傳的是實際刪除的 ID 集合，其長度可能小於 `firing_ids` 的長度，導致誤判為競態而跳過觸發。建議先對 `firing_ids` 去重，或比較集合而非長度。

finding 片段：`if len(deleted_ids) != len(firing_ids):`

## P0060

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 6 行）buildInviteLink 條件判斷反轉

> 原本的條件是 `if (!isOrgContext)` 回傳 teamInviteLink，現在改為 `if (isOrgContext)`。這會導致在非組織情境下，程式會繼續執行並呼叫 `OnboardingPathService.getGettingStartedPathWhenInvited`，可能產生錯誤的連結或非預期行為。應確認此變更是否為預期，否則應改回 `if (!isOrgContext)`。

finding 片段：`if (isOrgContext) {`

## P0061

**GT**（func）Semaphore context released before API call defeats concurrency control

> The semaphore's async context manager exits at line 151 (after only creating the EventFilter object), but the actual API call to check for duplicate events happens at line 153-159, outside the semaphore's protection. This defeats the entire purpose of the semaphore, which was introduced to limit concurrent API calls during observer startup to prevent overwhelming the API server. The API request that queries '/events/filter' is now unprotected, allowing unlimited concurrent requests when there are many existing pods in the cluster, potentially causing API server performance degradation or timeouts during startup.

GT 片段：`async with _startup_event_semaphore: ⏎ # Use the Kubernetes event timestamp for the filter to avoid "Query time range is too large" error ⏎ event_filter = EventFilter( ⏎ event=EventNameFilter(name=[f"prefect.kubernetes.pod.{phase.lower()}"]),`

**finding**（`src/integrations/prefect-kubernetes/prefect_kubernetes/observer.py:132`，距錨點 5 行）Semaphore 未初始化時拋出 RuntimeError 可能中斷事件處理

> 在 `_replicate_pod_event` 中，若 `_startup_event_semaphore` 為 `None`，會拋出 `RuntimeError`。這可能發生在 `initialize_clients` 尚未完成或未呼叫時，導致 kopf handler 失敗並可能影響整個 observer 的穩定性。建議改為記錄警告並跳過 semaphore 限制，或確保初始化順序。

finding 片段：`if _startup_event_semaphore is None: ⏎ raise RuntimeError("Startup event semaphore not initialized")`

## P0062

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1735`，距錨點 8 行）在非最後一個 AOF 檔案上進行截斷可能導致資料不一致

> 在 `loadAppendOnlyFiles` 中，當 `ret == AOF_BROKEN_RECOVERED` 且 `!last_file` 時，程式碼會將 `ret` 設為 `AOF_FAILED` 並記錄錯誤，但此時檔案已經被截斷。這意味著即使載入失敗，AOF 檔案已經被修改，可能導致後續手動修復更加困難。

**失敗情境**：假設有多個 AOF 檔案，第一個檔案損壞且被截斷，但因為不是最後一個檔案而導致載入失敗。此時第一個檔案已被修改，但伺服器並未啟動，使用者需要手動修復，但原始損壞資料已丟失。

**建議修法**：在決定是否截斷之前，應先判斷該檔案是否為最後一個檔案。如果不是，則不應進行截斷，直接回報錯誤。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) {`

## P0063

**GT**（func）FeatureOptInService creates isolated containers breaking dependency sharing

> The getFeatureOptInService() function creates a fresh DI container on every call, which then loads its dependencies including FeaturesRepository into that isolated container. This breaks the expected dependency injection pattern where services should share repository instances. When code calls both getFeaturesRepository() and getFeatureOptInService(), they each create separate containers with separate FeaturesRepository instances, leading to inconsistent cached state and duplicated database connections. The FeatureOptInService's repository will have different cached data than repositories retrieved elsewhere, causing unpredictable behavior in feature flag resolution.

GT 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

**finding**（`packages/features/di/containers/FeatureOptInService.ts:6`，距錨點 0 行）每次呼叫 getFeatureOptInService 都建立新容器，可能造成效能與狀態問題

> `getFeatureOptInService` 每次呼叫都會建立新的容器並載入模組，這可能導致每個請求都建立新的服務實例，增加不必要的開銷。如果服務內部有狀態或依賴共享資源（如資料庫連線），也可能造成資源浪費或狀態不一致。建議考慮使用單例模式或由全域容器管理。

finding 片段：`export function getFeatureOptInService(): IFeatureOptInService { ⏎ const featureOptInServiceContainer = createContainer(); ⏎ featureOptInServiceModuleLoader.loadModule(featureOptInServiceContainer); ⏎ return featureOptInServiceContainer.get<IFeatureOptInService>(featureOptInServiceModuleLoader.token`

## P0064

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）write_and_make_executable 先設定權限再寫入可能導致問題

> 函式改為先執行 `fs::set_permissions` 再執行 `fs::write`。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致函式提前返回，檔案永遠不會被建立。此外，即使檔案存在，先設定權限再寫入也可能在寫入過程中因權限不足而失敗。建議維持原本的先寫入再設定權限的順序。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0065

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:149`，距錨點 0 行）`collect_task_run_inputs` 改為同步呼叫可能阻塞事件迴圈

> 原本 `await collect_task_run_inputs(v)` 是非同步呼叫，現在改為 `collect_task_run_inputs(v)` 同步呼叫。若該函式內部有 I/O 或耗時操作，會阻塞事件迴圈，影響效能。

建議：確認 `collect_task_run_inputs` 是否為非同步函式，若是則應保留 `await`。

finding 片段：`k: collect_task_run_inputs(v) for k, v in parameters.items()`

## P0066

**GT**（rule）Non-xUnit test attribute added

> The rule requires using xUnit test framework attributes. The added [QuarantinedTest] attribute is not an xUnit attribute ([Fact]/[Theory]) and introduces non-xUnit test metadata on the test method.

GT 片段：`[QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")]`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:291`，距錨點 3 行）AppContext.SetSwitch 參數反轉可能導致測試失效

> 原本設定 DisableThrowNavigationException 為 false，現在改為 true。若測試目的是驗證例外拋出，設為 true 會停用例外，可能使測試無法觸發預期行為。需確認此變更是否為預期修正。

finding 片段：`AppContext.SetSwitch("Microsoft.AspNetCore.Components.Endpoints.NavigationManager.DisableThrowNavigationException", true);`

## P0067

**GT**（rule）Missing braces in for loop

> The rule requires all control flow statements (if, else, for, foreach, while, do-while) to use curly braces even for single-line bodies, but the inner for loop omits curly braces

GT 片段：`for (const [initializerIdentifier, componentIdentifiers] of Object.entries(jsComponentInitializers)) { ⏎ const initializerFunc = DotNet.findJSFunction(initializerIdentifier, 0) as JSComponentInitializerCallback; ⏎ for (const componentIdentifier of componentIdentifiers) ⏎ initializerFunc(componentIde`

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:139`，距錨點 4 行）多 renderer 並存時初始化可能被跳過

> `hasInitializedJsComponents` 是全域變數，一旦設為 true，之後任何 renderer 呼叫 `enableJSRootComponents` 都不會再執行初始化。若頁面同時存在多個不同 renderer（例如一個 Server 和一個 WebAssembly），且第一個 renderer 初始化後，第二個 renderer 的 JS 元件將不會被初始化，導致功能失效。

建議將 `hasInitializedJsComponents` 改為以 rendererId 為鍵的集合，或將初始化邏輯綁定到每個 manager 實例。

finding 片段：`if (!hasInitializedJsComponents) { ⏎ // Call the registered initializers... ⏎ ... ⏎ hasInitializedJsComponents = true;`

## P0068

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）cli.js 版本與 tauri-cli 版本不一致

> metadata-v2.json 中 cli.js 的版本從 2.8.1 更新為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 更新為 2.8.1。這可能導致發布的 CLI 二進制檔案版本與 npm 套件版本不一致，造成使用者混淆或依賴解析問題。建議確認正確的版本號並統一。

finding 片段：`"version": "2.8.2",`

## P0069

**GT**（func）Job scheduler will never schedule on first invocation

> The condition `hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')` is incorrect - it checks if the job is already scheduled before scheduling it, creating a logical impossibility. The job will never be scheduled on the first call since `hasScheduled.processOutbox` starts as `false`. This should be `!hasScheduled.processOutbox` to schedule the job when it hasn't been scheduled yet. This breaks the welcome email processing functionality entirely, as the background job that processes the outbox entries will never be registered.

GT 片段：`async scheduleMemberWelcomeEmailJob() { ⏎ if (!config.get('memberWelcomeEmailTestInbox')) { ⏎ return false; ⏎ }`

**finding**（`ghost/core/core/server/services/member-welcome-emails/jobs/index.js:15`，距錨點 0 行）排程條件反轉導致重複排程或完全停用

> 原本條件 `!hasScheduled.processOutbox` 確保只排程一次，但改為 `hasScheduled.processOutbox` 後，當 `hasScheduled.processOutbox` 為 true 時會再次排程，造成重複排程；若為 false 則永遠不排程。應改回 `!hasScheduled.processOutbox`。

finding 片段：`if (hasScheduled.processOutbox && !process.env.NODE_ENV.startsWith('test')) {`

## P0070

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:133`，距錨點 14 行）`get_or_create_client` 可能建立非預期的 client

> 原本使用 `@inject_client` 裝飾器，會根據上下文注入 client，若未提供則建立新的 client。現在改為 `get_or_create_client(client)`，其行為可能不同：若 `client` 為 None，它會建立一個新的 client，但可能未正確處理與目前執行中 flow run 的關聯（例如使用相同的 API URL 或認證）。這可能導致在 flow 內呼叫時無法正確連結父子關係。

建議：確認 `get_or_create_client` 的實作是否符合預期，或保留原本的 `@inject_client` 機制。

finding 片段：`client, _ = get_or_create_client(client)`

## P0071

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 0 行）缺少對新功能的測試

> 新增的自動遞增邏輯沒有對應的單元測試或整合測試。建議添加測試覆蓋以下情境：首次建置、正常遞增、檔案不存在、檔案格式錯誤、並行建置（如果實作鎖定）等。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0072

**GT**（func）Inconsistent date filter causes missing bookings in recurring event cancellation

> When cancelling recurring bookings with 'allRemainingBookings' flag, the code updates bookings using 'new Date()' as the time threshold but then fetches updated bookings using 'bookingToDelete.startTime'. This creates a time window mismatch where bookings between these two timestamps will be cancelled in the database but won't be included in 'allUpdatedBookings', causing workflow reminders and calendar event cleanup to be skipped for those bookings. This leads to orphaned reminders and stale calendar events that were cancelled but never properly cleaned up.

GT 片段：`const recurringEventId = bookingToDelete.recurringEventId; ⏎ const gte = cancelSubsequentBookings ? bookingToDelete.startTime : new Date(); ⏎ // Proceed to mark as cancelled all remaining recurring events instances (greater than or equal to right now) ⏎ await bookingRepository.updateMany({`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:546`，距錨點 30 行）updateIncludeWorkflowRemindersAndReferences 的 where 條件改為 uid 可能影響行為

> 原本的 `prisma.booking.update` 使用 `where: uid ? { uid } : { id }`，現在改為固定使用 `uid: bookingToDelete.uid`。若 `bookingToDelete.uid` 為空或未定義，將導致查詢失敗。雖然 `bookingToDelete` 應有 uid，但此變更可能影響某些邊界情況。

建議：確認 `bookingToDelete.uid` 一定存在，或保留原本的條件邏輯。

finding 片段：`const updatedBooking = await bookingRepository.updateIncludeWorkflowRemindersAndReferences({ ⏎ where: { ⏎ uid: bookingToDelete.uid, ⏎ },`

## P0073

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter.wait 的結果未檢查，可能隱藏逾時錯誤

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，函式會回傳 nil，但呼叫端僅以 XCTFail 處理，無法區分是逾時還是其他錯誤。建議檢查 waiter 結果，並在逾時時提供更明確的錯誤訊息。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0074

**GT**（func）Swapped answer price unit values causing incorrect billing calculations

> In the create_agent_thought method, the answer_unit_price and answer_price_unit values are swapped. The answer_unit_price is initialized to Decimal('0.001') instead of Decimal(0), while answer_price_unit is initialized to Decimal(0) instead of Decimal('0.001'). This mirrors the correct initialization pattern used for message_unit_price and message_price_unit but with reversed values. This will cause incorrect pricing calculations when computing the total cost of agent responses, potentially leading to billing discrepancies or revenue loss.

GT 片段：`answer="", ⏎ observation="", ⏎ answer_token=0, ⏎ answer_unit_price=Decimal("0.001"),`

**finding**（`api/core/agent/base_agent_runner.py:319`，距錨點 3 行）message_unit_price 與 answer_unit_price 的 Decimal 值可能不符預期

> 在 create_agent_thought 中，message_unit_price 設為 Decimal(0)，answer_unit_price 設為 Decimal("0.001")，而 message_price_unit 設為 Decimal("0.001")，answer_price_unit 設為 Decimal(0)。這些值可能與原本的整數 0 和預設 0.001 不同，需確認是否符合業務邏輯。

finding 片段：`message_unit_price=Decimal(0), ⏎ message_price_unit=Decimal("0.001"),`

## P0075

**GT**（rule）Legacy typing imports instead modern syntax

> The rule requires using Python 3.12+ modern type syntax (set[tuple[str, ...]] instead of Set[Tuple[str, ...]]), but the code imports and uses legacy typing module classes Set and Tuple

GT 片段：`from collections.abc import Mapping, Sequence ⏎ from typing import TYPE_CHECKING, Any, Set, Tuple ⏎ ... ⏎ def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

**finding**（`api/core/workflow/nodes/variable_assigner/v1/node.py:36`，距錨點 0 行）型別提示 `Set[Tuple[str, ...]]` 可能與實際傳入型別不符

> `blocks_variable_output` 的參數 `variable_selectors` 標註為 `Set[Tuple[str, ...]]`，但呼叫端可能傳入其他可迭代型別（如 list）。若型別不符，可能導致執行時期錯誤或型別檢查警告。建議確認呼叫端傳入的型別，或放寬為 `Iterable[Tuple[str, ...]]`。

finding 片段：`def blocks_variable_output(self, variable_selectors: Set[Tuple[str, ...]]) -> bool:`

## P0076

**GT**（func）Inverted filter logic in listFeaturesForUser returns disabled features instead of enabled

> The filter condition in listFeaturesForUser was changed from `filter((state) => state.globalEnabled)` to `filter((state) => !state.globalEnabled)`, inverting the logic. This causes the method to return only globally disabled features instead of enabled ones. Users will see an empty or incorrect list of available features in their settings UI, as only features that are globally disabled (which should be hidden) will be shown, while actually available features will be filtered out. This breaks the entire feature opt-in UI for users.

GT 片段：`const resolvedStates = await this.resolveFeatureStatesAcrossTeams({ ⏎ userId, ⏎ orgId, ⏎ teamIds,`

**finding**（`packages/features/feature-opt-in/services/FeatureOptInService.ts:207`，距錨點 0 行）listFeaturesForUser 過濾條件邏輯錯誤

> 在 `listFeaturesForUser` 方法中，原本的過濾條件是 `state.globalEnabled`，但此 PR 將其改為 `!state.globalEnabled`。這會導致只回傳全域停用的功能，而全域啟用的功能反而被排除。這與方法的文件說明「Only returns features that are in the allowlist, globally enabled, and scoped to "user"」完全相反。

**失敗情境**：當使用者呼叫此方法時，所有全域啟用的功能都不會出現在結果中，而全域停用的功能卻會出現。這將導致使用者介面顯示錯誤的功能列表，或讓使用者無法看到應該可用的功能。

**建議修法**：將條件改回 `state.globalEnabled`。

finding 片段：`return featureIds.map((featureId) => resolvedStates[featureId]).filter((state) => !state.globalEnabled);`

## P0077

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）記憶體配置失敗未處理

> `malloc` 可能回傳 NULL，但程式碼未檢查就直接使用 `slot_buffer`，可能導致 NULL 指標解參考。雖然在 Redis 中記憶體配置失敗通常會觸發 OOM 處理，但此處直接使用仍不夠安全。建議檢查 `slot_buffer` 是否為 NULL，若為 NULL 則回傳錯誤或觸發 OOM。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0078

**GT**（func）Inverted logic in servicing build validation

> The condition for servicing build validation has inverted logic - it triggers an error when AspNetCorePatchVersion equals '1' instead of when it does not equal '1'. This means the first servicing release (patch version 1) will incorrectly fail builds if package references changed, while subsequent servicing releases (patch version 2, 3, etc.) will incorrectly allow breaking changes to package references. The original intent was to allow package reference changes only for the first servicing release (version 10.0.1) but block them for later releases.

GT 片段：`<Error ⏎ Condition=" '$(IsServicingBuild)' == 'true' AND '@(UnusedBaselinePackageReference->Count())' != '0' AND '$(AspNetCorePatchVersion)' == '1'" ⏎ Code="BUILD002" ⏎ Text="Package references changed since the last release. This could be a breaking change and is not allowed in a servicing update. `

**finding**（`eng/targets/ResolveReferences.targets:211`，距錨點 0 行）條件式停用錯誤檢查可能允許未使用的基線套件參考

> 在錯誤條件中新增 '$(AspNetCorePatchVersion)' == '1'，這表示只有當修補版本為 1 時才會檢查未使用的基線套件參考。這可能導致在其他修補版本中允許未使用的參考，進而隱藏潛在的相依性問題。建議確認此條件是否正確，或考慮使用更通用的條件。

finding 片段：`Condition=" '$(IsServicingBuild)' == 'true' AND '@(UnusedBaselinePackageReference->Count())' != '0' AND '$(AspNetCorePatchVersion)' == '1'"`

## P0079

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）屬性 badge 的 label 拼接可能導致顯示問題

> 在 generateAttributeColumns 中，label 由 attributeValue.value、weight 和 groupIndicator 拼接而成，例如 "value 100% (group)"。這可能導致顯示不美觀，且若 value 本身包含空格或特殊字元，可能造成誤解。建議使用更結構化的方式呈現，例如在 Badge 內使用多個元素或 tooltip。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0080

**GT**（func）Validation incorrectly rejects proactive triggers with automation_triggered_event_id

> The field_validator for automation_triggered_event_id prevents setting this field when triggering_event is None. However, proactive triggers (which have no triggering_event) still create automation.triggered events and need to link actions to them via automation_triggered_event_id. The code in triggers.py sets automation_triggered_event_id=primary_state_change_event_id for all actions including proactive triggers, causing Pydantic validation to fail at runtime. This breaks all proactive automations, which is a critical functional regression.

GT 片段：`@field_validator("automation_triggered_event_id") ⏎ @classmethod ⏎ def validate_automation_triggered_event_id(cls, v, info): ⏎ """Ensure automation_triggered_event_id is only set when triggering_event exists."""`

**finding**（`src/prefect/server/events/schemas/automations.py:776`，距錨點 0 行）validator 依賴欄位順序，可能導致驗證失敗

> `validate_automation_triggered_event_id` 使用 `info.data.get("triggering_event")` 檢查 triggering_event 是否存在，但 Pydantic v2 的 `info.data` 僅包含已驗證的欄位，若 `automation_triggered_event_id` 在 `triggering_event` 之前定義，則 `info.data` 中可能尚無 triggering_event，導致誤判。建議改用 `info.data.get("triggering_event", None) is not None` 或使用 `model_validator`。

finding 片段：`if v is not None and info.data.get("triggering_event") is None:`

## P0081

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行）自動截斷可能造成資料遺失，且未提供足夠的警告或備份機制

> 當 aof-load-broken 啟用且損壞部分小於 max-size 時，程式會直接 truncate 檔案，丟棄損壞部分之後的所有資料。這可能導致資料遺失，且僅記錄 warning。建議在 truncate 前先將原始檔案備份（例如複製一份），或至少提供更明確的警告，讓使用者知道有多少資料被丟棄。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0082

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 0 行）並行建置可能產生相同的 versionCode

> 在 `generate_tauri_properties` 中，讀取舊的 versionCode 後直接加 1 寫入，沒有使用鎖定或原子操作。如果兩個建置同時執行（例如 CI 中並行觸發），它們可能讀到相同的舊值，並產生相同的 versionCode，導致上架衝突。建議使用檔案鎖（例如 `flock`）或將 versionCode 儲存在可原子更新的位置（如資料庫或遠端服務）。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0083

**GT**（func）Race condition from premature TaskCompletionSource recreation

> The _receiveTcs TaskCompletionSource is recreated before checking if the buffer is zero-sized, creating a race condition in the WebSocketWrapper's ReceiveAsync implementation. When a zero-byte read occurs (buffer.Count == 0), the method returns early with the result but the TCS has already been reset. This means if another thread or the background task tries to set a result on the now-recreated TCS while this zero-byte read is in progress, it will affect the next receive operation rather than completing the current one. This breaks the synchronization contract and can cause message loss or out-of-order receives in the stateful reconnection test scenarios where WebSocket message sequencing is critical.

GT 片段：`public override async Task<WebSocketReceiveResult> ReceiveAsync(ArraySegment<byte> buffer, CancellationToken cancellationToken) ⏎ { ⏎ var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409`，距錨點 0 行）WebSocketWrapper 的競態條件修正可能不完整

> 將 `_receiveTcs` 的重設移至 `ReceiveAsync` 開頭，可避免在零位元組讀取時未重設的問題。但若 `ReceiveAsync` 在等待 `_receiveTcs.Task` 時被取消，可能導致 `_receiveTcs` 未重設，影響後續呼叫。建議考慮在 `finally` 區塊中重設，或使用更安全的同步機制。

finding 片段：`_receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

## P0084

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1502`，距錨點 0 行）updateMany 方法未回傳更新筆數

> `updateMany` 方法未回傳 `count`，但介面 `IBookingRepository` 定義回傳 `Promise<{ count: number }>`。這可能導致呼叫端無法確認更新是否成功。建議回傳 `count` 或調整介面定義。

finding 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({`

## P0085

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 0 行）config 值型別不一致可能導致非預期行為

> `config.get('memberWelcomeEmailTestInbox')` 回傳值可能是字串（如測試中設定的 'test-inbox@example.com'）或 undefined。在條件判斷中，空字串會被視為 falsy，但非空字串為 truthy，因此若設定為空字串會停用功能，但設定為任意非空字串（即使不是有效 email）也會啟用。建議明確檢查是否為有效 email 或使用布林值。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0086

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:66`，距錨點 5 行）查詢條件 `csd_email_count:-null` 可能無法正確過濾

> `filter: 'csd_email_count:-null'` 的語法可能不正確，Ghost 的 filter 通常使用 `csd_email_count:not null` 或 `csd_email_count:!=null`。若語法錯誤，可能導致查詢失敗或回傳所有記錄。建議確認正確的 filter 語法。

finding 片段：`filter: 'csd_email_count:-null',`

## P0087

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:40`，距錨點 0 行）selector 長度檢查可能不完整

> 程式碼檢查 `len(selector) < 2` 後才使用 `selector[0]`，但未驗證 selector 的第二個元素是否為有效的 variable name。若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID]`（長度 1），會被跳過；但若 selector 為 `[CONVERSATION_VARIABLE_NODE_ID, None]` 或類似，可能導致後續 `variable_pool.get` 行為異常。建議增加更嚴格的驗證。

finding 片段：`if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector) ⏎ continue ⏎ if selector[0] != CONVERSATION_VARIABLE_NODE_ID:`

## P0088

**GT**（func）Incorrect section index after inactive tabs removal

> The scrollToTab method hardcodes section index as 1, which was correct when there were two sections (inactive tabs at section 0 and regular tabs at section 1). After removing inactive tabs, there is only one section (section 0), so this will cause scroll operations to fail or crash when trying to access a non-existent section. This affects all scroll-to-tab functionality including selecting tabs, undoing tab closures, and panel switching. The TabDisplayDiffableDataSource now only creates a single section `.tabs`, but this scroll method wasn't updated accordingly.

GT 片段：`private func scrollToTab(_ scrollState: TabsPanelState.ScrollState) { ⏎ let indexPath = IndexPath(row: scrollState.toIndex, section: 1) ⏎ // Piping this into main thread let the collection view finish its layout process ⏎ DispatchQueue.main.async {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172`，距錨點 0 行）滾動目標 section 固定為 1，但現在只有一個 section

> 在 `scrollToTab` 中，原本根據 `scrollState.isInactiveTabSection` 決定 section 為 0 或 1，現在直接寫死為 1。但移除 inactive tabs 後，collection view 只有一個 section（index 0），因此 `IndexPath(row:section:1)` 會指向不存在的 section，導致滾動功能失效。

建議將 section 改為 0。

finding 片段：`let indexPath = IndexPath(row: scrollState.toIndex, section: 1)`

## P0089

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行）tool_call_response 的 content 誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本使用 `tool_responses.get(tool, agent_thought.observation)` 作為 ToolPromptMessage 的 content，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具回應內容變成工具輸入，而非實際的觀察結果，造成歷史訊息錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史記錄中的工具回應會顯示輸入參數而非輸出結果，影響後續模型理解上下文。

建議改回使用 `tool_responses`，並考慮是否需要 `str()` 轉換。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0090

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）多個變數更新時多次 flush，可能導致部分更新遺失

> 在 `on_event` 中，對每個 updated variable 呼叫 `update` 後立即呼叫 `flush`。若有多個變數需要更新，且其中一個更新失敗，先前已 flush 的變更不會被回滾，導致資料不一致。建議收集所有更新後只 flush 一次，或使用交易包裹所有更新。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0091

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）數字輸入框類型從 number 改為 text 可能影響驗證

> 將數字輸入框的 `type` 從 `number` 改為 `text`，可能導致瀏覽器不再自動驗證數字格式，且行動裝置可能顯示不同的鍵盤。若此變更非刻意為之，建議保留 `type="number"`。

finding 片段：`type="text"`

## P0092

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:92`，距錨點 2 行）useEffect 相依陣列為空可能導致截斷偵測失效

> `CommentContent` 中的 `useEffect` 僅在掛載時執行一次，但 `item.html` 可能在之後更新（例如從 API 載入或狀態變更）。若內容更新後高度改變，`isClamped` 不會重新計算，導致「Show more」按鈕顯示不正確。建議將 `item.html` 加入相依陣列，或使用 ResizeObserver 監聽內容變化。

finding 片段：`useEffect(() => { ⏎ const checkIfClamped = () => { ⏎ if (contentRef.current) { ⏎ // Check if the content is clamped by comparing scrollHeight with clientHeight`

## P0093

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）截斷後未同步 AOF 檔案描述符的偏移量

> 在 `truncate(aof_filepath, valid_up_to)` 成功後，程式碼嘗試使用 `lseek(server.aof_fd, 0, SEEK_END)` 來將檔案描述符的偏移量設定到檔案結尾。然而，`server.aof_fd` 可能不是當前載入的 AOF 檔案的描述符，或者可能尚未開啟。此外，`lseek` 失敗時僅記錄警告，但未將 `ret` 設為錯誤，可能導致後續寫入使用錯誤的偏移量。

**失敗情境**：如果 `server.aof_fd` 指向另一個檔案（例如在載入多個 AOF 檔案時），`lseek` 會影響錯誤的檔案描述符，導致後續寫入到錯誤的位置。

**建議修法**：在截斷後，應使用 `fseek` 或 `ftruncate` 來同步檔案指標，並確保操作的是正確的檔案描述符。若無法確保，應關閉並重新開啟檔案。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) {`

## P0094

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 建立的 robj 未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後未呼叫 decrRefCount 釋放。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。建議在 alsoPropagate 呼叫後立即釋放 argv[2]，或改用其他方式避免手動管理記憶體。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`
