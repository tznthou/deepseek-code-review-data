# 盲標單 1：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part1.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0001

**GT**（func）Missing await in setUserState mutation causes race condition

> The await keyword was removed from the featureOptInService.setUserFeatureState call in the tRPC mutation handler. This causes the mutation to return success immediately without waiting for the database operation to complete, creating a race condition where the response is sent before the state is actually persisted. Users will receive success responses even if the underlying operation fails, and subsequent reads might not reflect the changes they just made, leading to inconsistent UI state and data integrity issues.

GT 片段：`featureOptInService.setUserFeatureState({ ⏎ userId: ctx.user.id, ⏎ featureId: input.slug, ⏎ state: input.state,`

**finding**（`packages/trpc/server/routers/viewer/featureOptIn/_router.ts:103`，距錨點 0 行）setUserState mutation 缺少 await，可能造成未處理的 Promise rejection

> 在 `setUserState` mutation 中，呼叫 `featureOptInService.setUserFeatureState(...)` 時沒有加上 `await`。這會導致如果該方法拋出錯誤（例如 scope 驗證失敗），錯誤不會被 tRPC 正確捕獲，而會成為 unhandled promise rejection，可能導致伺服器不穩定或回傳錯誤的狀態碼。

**失敗情境**：當使用者嘗試設定一個不允許在 user scope 設定的功能時，`setUserFeatureState` 會拋出 `ErrorWithCode`，但因為沒有 `await`，這個錯誤不會被 tRPC 的錯誤處理機制攔截，客戶端可能收到成功回應，但實際上操作並未完成。

**建議修法**：在呼叫前加上 `await`。

finding 片段：`featureOptInService.setUserFeatureState({ ⏎ userId: ctx.user.id, ⏎ featureId: input.slug, ⏎ state: input.state,`

## P0002

**GT**（func）Post scheduling will fail on boot - missing required apiUrl parameter

> The scheduling.init() call is missing the required apiUrl parameter that was previously passed via urlUtils.urlFor('api', {type: 'admin'}, true). The PostScheduler constructor explicitly checks for this parameter and throws an IncorrectUsageError if it's not provided. This will cause Ghost to crash during the boot sequence when attempting to initialize the scheduling service. The apiUrl is critical for the scheduling service as it's used to generate signed admin tokens and callback URLs for scheduled post publishing. Without this parameter, the scheduled publishing feature cannot function.

GT 片段：`webhooks.listen(), ⏎ scheduling.init(), ⏎ comments.init(),`

**finding**（`ghost/core/core/boot.js:368`，距錨點 0 行）scheduling.init() 缺少 apiUrl 參數可能導致排程服務無法正常運作

> 原本 `scheduling.init()` 會傳入 `apiUrl` 參數，用於建構排程服務所需的 API URL。移除後，排程服務可能無法正確取得 API 位址，導致排程任務失敗或無法觸發。建議確認 `scheduling.init()` 是否已改為從其他來源取得 API URL，或此參數是否已不再需要。

finding 片段：`scheduling.init(),`

## P0003

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:18`，距錨點 8 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

## P0004

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 0 行）讀取失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或解析失敗時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致意外重置版本碼，尤其是在檔案被誤刪或格式錯誤時，造成 Google Play 上傳失敗。

建議：在無法讀取時發出警告或錯誤，或提供明確的 fallback 策略。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0005

**GT**（func）File comparison logic always evaluates to not-equal due to operand order

> The file content comparison has a subtle logical error where the operands are reversed in the inequality check at line 677. The code reads the existing file content into variable `o` and checks `app_tauri_properties_content != o` instead of `o != app_tauri_properties_content`. While mathematically equivalent for inequality, this changes the semantic meaning in Rust's comparison evaluation and may cause unnecessary file writes. More critically, this breaks the optimization that prevents redundant writes when content hasn't changed, potentially causing unnecessary build triggers and file system churn on every build even when the properties haven't actually changed.

GT 片段：`if std::fs::read_to_string(&app_tauri_properties_path) ⏎ .map(|o| app_tauri_properties_content != o) ⏎ .unwrap_or(true) ⏎ {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 31 行）自動遞增時未檢查 versionCode 上限

> 當 `auto_increment_version_code` 為 true 時，直接使用 `saturating_add(1)`，但未檢查是否超過 Google Play 的 2100000000 上限。若已達上限，`saturating_add` 會停留在 2100000000，可能導致上傳失敗。

建議：在遞增後檢查上限，若超過則報錯。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

## P0006

**GT**（func）Navigation exception test disables the exception mechanism it's meant to test

> The NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException test is designed to verify that NavigationException thrown during circular redirects doesn't become an unobserved task exception. The test name, comments, and logic all indicate it should test the exception handling behavior. However, the AppContext switch is set to true, which enables DisableThrowNavigationException, preventing NavigationException from being thrown at all. This fundamentally breaks the test's purpose - it can't validate exception handling behavior when exceptions are disabled. The test navigates to a circular redirect page that relies on NavigationException being thrown and properly handled, but with the switch enabled, the navigation manager uses a different code path that doesn't throw exceptions, making the test validate nothing meaningful.

GT 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:287`，距錨點 0 行）測試被標記為隔離且開關值變更，可能掩蓋問題

> 測試 `NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException` 被加上 `[QuarantinedTest]` 屬性，且 `DisableThrowNavigationException` 開關從 `false` 改為 `true`。這可能表示測試目前不穩定或失敗，但隔離測試會使其在 CI 中跳過，無法驗證修復。建議確認隔離原因，並在修復後移除隔離標記。

finding 片段：`[TestMethod] ⏎ [QuarantinedTest("https://github.com/dotnet/aspnetcore/pull/63708/")] ⏎ public void NavigationException_InAsyncContext_DoesNotBecomeUnobservedTaskException() ⏎ {`

## P0007

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:102`，距錨點 29 行）findPage 查詢的 filter 使用 <= 可能包含今日資料

> 原本 `findOne` 使用 `created_at:<${today}` 排除今日，但改為 `findPage` 後 filter 變成 `created_at:<=${today}`，這會包含今日建立的 email。若今日已有 email，則 `#getHighestCount` 可能取到今日的 csd_email_count，導致 warmup limit 計算錯誤。建議確認是否應排除今日，若需排除，應改回 `<`。

finding 片段：`filter: `created_at:<=${new Date().toISOString().split('T')[0]}`,`

## P0008

**GT**（rule）New/modified path resolution introduces panics/unwraps for fallible operations

> `resolve_dirs` uses `panic!` and `unwrap()` (`tauri.parent().unwrap()`) for fallible operations (project discovery/path parent resolution) instead of returning a `Result`, violating the rule to make failure explicit rather than panicking.

GT 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| { ⏎ let env_var_name = env_tauri_app_path().is_some().then(|| format!("`{ENV_TAURI_APP_PATH}`")); ⏎ panic!("Couldn't recognize the {} folder as a Tauri project. It must contain a `{}`, `{}` o`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:130`，距錨點 0 行）`resolve_dirs()` 使用 `OnceLock` 快取路徑，可能在不同工作目錄間切換時回傳舊值

> `resolve_dirs()` 使用 `TAURI_DIR` 和 `FRONTEND_DIR` 兩個 `OnceLock` 來快取解析結果。一旦第一次呼叫後，後續呼叫即使工作目錄改變，仍會回傳相同的路徑。這在 CLI 工具中可能造成問題，例如在同一個程序內處理多個專案（如測試或未來功能）。建議改為每次重新解析，或提供清除快取的機制。

finding 片段：`pub fn resolve_dirs() -> Dirs { ⏎ let tauri = TAURI_DIR.get_or_init(|| resolve_tauri_dir().unwrap_or_else(|| { ⏎ let env_var_name = env_tauri_app_path().is_some().then(|| format!("`{ENV_TAURI_APP_PATH}`")); ⏎ panic!("Couldn't recognize the {} folder as a Tauri project. It must contain a `{}`, `{}` o`

## P0009

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:364`，距錨點 0 行）SSL_CERT_DIR 解析時未處理空目錄項目

> 程式碼使用 `existingSslCertDir.Split(Path.PathSeparator)` 分割環境變數，但未移除空字串項目。若 SSL_CERT_DIR 包含連續分隔符（如 `dir1::dir2`），會產生空字串，後續 `string.IsNullOrWhiteSpace(dir)` 檢查會將其忽略，但可能導致其他邏輯問題。建議使用 `StringSplitOptions.RemoveEmptyEntries` 分割。

finding 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator);`

## P0010

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 輸出日誌

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將訊息輸出到標準輸出，可能污染正式環境的日誌或影響效能。建議改用 logging 模組，並設定適當的日誌層級。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0011

**GT**（func）Missing await on async function call in task input collection

> The `collect_task_run_inputs` function is an async function that must be awaited, but in line 149 it's being called without `await` in a dictionary comprehension. This will result in the `task_inputs` dictionary containing coroutine objects instead of the actual collected task run input sets. When this dictionary is passed to `client.create_task_run()` on line 191, it will cause a type error since the API expects properly resolved input sets, not coroutine objects. This breaks the subflow linking functionality when `arun_deployment` is called from within a parent flow or task.

GT 片段：`# This was called from a flow. Link the flow run as a subflow. ⏎ task_inputs = { ⏎ k: collect_task_run_inputs(v) for k, v in parameters.items() ⏎ }`

**finding**（`src/prefect/deployments/flow_runs.py:149`，距錨點 0 行）`collect_task_run_inputs` 改為同步呼叫，可能導致效能問題

> 原本 `await collect_task_run_inputs(v)` 是非同步呼叫，現在改為 `collect_task_run_inputs(v)` 同步呼叫。如果 `collect_task_run_inputs` 內部有 I/O 或需要非同步操作，這會阻塞事件迴圈。需確認該函式是否為純同步函式，否則應保留 `await`。

finding 片段：`k: collect_task_run_inputs(v) for k, v in parameters.items()`

## P0012

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:241`，距錨點 4 行）同步呼叫路徑失效：`run_deployment` 不再支援同步執行

> 原本 `run_deployment` 使用 `@sync_compatible` 裝飾器，允許在同步環境中直接呼叫。此 PR 移除了該裝飾器，並將 `run_deployment` 設為 `arun_deployment` 的別名，但 `arun_deployment` 是純非同步函式。這導致所有現有的同步呼叫（例如 `run_deployment(...)` 在沒有事件迴圈的環境中）會拋出 `RuntimeError` 或回傳 coroutine 物件而非實際結果。測試中仍使用 `_sync=True` 參數呼叫，但該參數已不存在於函式簽名中，會引發 `TypeError`。

**失敗情境**：任何在同步 Python 腳本或測試中呼叫 `run_deployment` 的使用者，會遇到 `TypeError: run_deployment() got an unexpected keyword argument '_sync'` 或 `RuntimeError: no running event loop`。

**建議**：保留同步包裝器，例如使用 `asyncio.run` 或 `anyio.run` 在同步函式中執行非同步邏輯，或提供獨立的同步函式。

finding 片段：`run_deployment = arun_deployment`

## P0013

**GT**（rule）Nested test delegate missing final modifier

> The rule requires that classes not designed for subclassing must be marked with the 'final' keyword to prevent unintended inheritance and enable compiler optimizations. The FakeWKNavigationDelegate class is a test utility not intended for inheritance but lacks the 'final' modifier.

GT 片段：`final class WebKitTestHelpers { ⏎ class FakeWKNavigationDelegate: NSObject, WKNavigationDelegate { ⏎ let expect: XCTestExpectation ⏎ var capturedFrame: WKFrameInfo?`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 26 行）XCTWaiter.wait 的結果未檢查

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0014

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:286`，距錨點 0 行）get_plan_bulk 將無效 tenant 設為 None，可能造成下游型別錯誤

> 在 `get_plan_bulk` 中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式會將 `results[tenant_id]` 設為 `None`。但函式回傳型別標註為 `dict[str, SubscriptionPlan]`，且呼叫端可能預期每個值都是有效的 `SubscriptionPlan`。這可能導致下游在存取 `plan` 或 `expiration_date` 時發生 `AttributeError` 或 `TypeError`。

**失敗情境**：某 tenant 的 billing API 回傳格式錯誤，`get_plan_bulk` 回傳包含 `None` 的 dict，呼叫端若直接使用 `result[tenant_id]['plan']` 就會崩潰。

**建議**：跳過無效 tenant（不要加入 dict），或回傳一個明確的錯誤物件。若必須保留 `None`，應更新型別標註並在文件說明。

finding 片段：`except Exception: ⏎ logger.exception( ⏎ "get_plan_bulk: failed to validate subscription plan for tenant(%s)", tenant_id ⏎ )`

## P0015

**GT**（func）Extension ignores bookingUrl and constructs incorrect fallback URLs

> The browser extension's copy link functionality ignores the bookingUrl field from the API and always constructs URLs using the fallback pattern 'https://cal.com/${username}/${slug}'. The original PR migrated all link building to use eventType.bookingUrl when available, but this change reverts that behavior in the extension. For users with custom domains or team event types, this results in copying incorrect URLs that don't match the actual booking page, breaking the core link-sharing functionality of the extension.

GT 片段：`copyBtn.addEventListener("click", (e) => { ⏎ e.stopPropagation(); ⏎ // Copy to clipboard ⏎ const bookingUrl =`

**finding**（`companion/extension/entrypoints/content.ts:1122`，距錨點 0 行）複製按鈕未使用 eventType.bookingUrl

> 在 copyBtn 的事件處理中，bookingUrl 的建構方式仍為手動拼接，未使用 eventType.bookingUrl。這可能導致複製的連結與預覽不一致，若 bookingUrl 存在且與預設格式不同（例如使用自訂網域），使用者會複製到錯誤的連結。建議與 previewBtn 的處理方式一致，優先使用 eventType.bookingUrl。

finding 片段：`const bookingUrl = ⏎ `https://cal.com/${ ⏎ eventType.users?.[0]?.username || "user" ⏎ }/${eventType.slug}`;`

## P0016

**GT**（rule）Non-static internal helper function exported as global symbol

> asmCountKeysInSlots is introduced as a file-local helper (not declared in any header and used only within src/cluster_asm.c in this diff), but it is declared without the 'static' keyword, making it globally visible and violating the encapsulation rule for internal helpers.

GT 片段：`/* Return the number of keys in the specified slot ranges. */ ⏎ unsigned long long asmCountKeysInSlots(slotRangeArray *slots) { ⏎ if (!slots) return 0; ⏎ unsigned long long key_count = 0;`

**finding**（`src/cluster_asm.c:1018`，距錨點 0 行）asmCountKeysInSlots 可能造成效能問題或非預期行為

> asmCountKeysInSlots 會對每個 slot 呼叫 kvstoreDictSize，若 slot 範圍很大（例如 0-16383），可能導致大量的函式呼叫，影響效能。此外，此函式在 asmLogTaskEvent 中被呼叫，而 asmLogTaskEvent 可能在任務生命週期的多個事件中被呼叫，若 slot 範圍大且 key 數量多，可能造成明顯延遲。建議考慮快取或使用更有效率的方式計算 key 數量。

finding 片段：`for (int j = slots->ranges[i].start; j <= slots->ranges[i].end; j++) { ⏎ key_count += kvstoreDictSize(server.db[0].keys, j); ⏎ }`

## P0017

**GT**（func）Type contract violation in get_plan_bulk return value

> In the get_plan_bulk method, when subscription plan validation fails for a tenant, the code sets `results[tenant_id] = None` instead of skipping that tenant with `continue`. This violates the method's return type contract of `dict[str, SubscriptionPlan]` by inserting None values. Downstream consumers expecting valid SubscriptionPlan objects will encounter AttributeError or TypeError when attempting to access plan fields like `subscription_plan['plan']` or `subscription_plan['expiration_date']`. This bug can cascade through the caching layer in get_plan_bulk_with_cache, potentially storing None values in Redis.

GT 片段：`for tenant_id, plan in data.items(): ⏎ try: ⏎ subscription_plan = subscription_adapter.validate_python(plan) ⏎ results[tenant_id] = subscription_plan`

**finding**（`api/services/billing_service.py:292`，距錨點 0 行）get_plan_bulk 的變更可能影響既有呼叫者

> get_plan_bulk 現在會將無效租戶設為 None 而不是拋出例外。這可能導致既有呼叫者（如果有）在處理結果時遇到 None 值而發生錯誤。建議確認所有呼叫者都能處理 None 值，或提供一個參數來控制行為。

finding 片段：`results[tenant_id] = None`

## P0018

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2138`，距錨點 0 行）使用 malloc 取代 zmalloc 可能導致記憶體未初始化或未對齊

> 在 clusterCommonInit() 中，原本使用 zmalloc 配置 server.cluster_slot_stats，現在改為 malloc。zmalloc 會將記憶體初始化為零，而 malloc 不會。若後續程式碼假設 slot stats 已歸零（例如 resetClusterStats() 可能只重置部分欄位），可能導致未定義行為或錯誤的統計數據。建議改回 zmalloc 或使用 zcalloc。

finding 片段：`server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

## P0019

**GT**（func）Conversation variable persistence failures are silently ignored

> The ConversationVariablePersistenceLayer calls update() without catching exceptions, relying on the graph engine's blanket exception handler which logs but continues execution. When persistence fails (e.g., database errors, ConversationVariableNotFoundError), the exception is caught by the engine's try-except in event_manager.py, logged, and execution continues. This creates silent data loss where the in-memory variable pool contains updated values but the database doesn't, causing data inconsistency. In the original implementation, these errors would fail the node execution and stop the workflow, providing clear feedback to users.

GT 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）每個變數更新後都 flush，可能造成效能問題

> 在 `for item in updated_variables` 迴圈內，每次呼叫 `self._conversation_variable_updater.update(...)` 後都呼叫 `self._conversation_variable_updater.flush()`。如果一次更新多個 conversation variables，會造成多次資料庫寫入。建議將 flush 移到迴圈外，或讓 updater 內部累積變更後一次 flush。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0020

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:27`，距錨點 0 行）使用 assert 取代 XCTAssertTrue 可能導致測試在 release 建置中失效

> 在測試方法 `testRequestAuthorization` 中，原本的 `XCTAssertTrue` 被改為 Swift 標準庫的 `assert`。`assert` 在 release 建置（`-O`）中會被編譯器移除，因此測試將不會驗證任何條件，可能導致測試永遠通過而失去防護力。建議改回 `XCTAssertTrue` 或使用 `XCTAssert` 系列斷言。

finding 片段：`assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

## P0021

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 23 行）跨欄位驗證誤用 field_validator，導致驗證失效或誤報

> 在 `_bucket_folder_suffix` 中嘗試進行跨欄位驗證，但此方法以 `@field_validator` 裝飾，僅能存取當前欄位的值，無法可靠取得其他欄位（如 `bucket`）。`info.data` 在驗證時可能尚未包含 `bucket` 的值（取決於欄位順序），導致驗證永遠不觸發或誤報。應改用 `@model_validator` 並在 `mode='after'` 中進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0022

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）日期計算可能因時區或浮點數誤差導致天數不正確

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `new Date(created_at).getTime()` 的差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或 `created_at` 包含時間部分，可能導致天數計算與預期不符。此外，浮點數除法後取 ceil 可能因精度問題造成邊界錯誤。建議改用 UTC 日期字串比較或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0023

**GT**（rule）Using assert instead of XCTAssert

> The rule requires test methods to use assertions from the XCTest framework (XCTAssert family), but standard Swift assert() functions were used instead of XCTAssertTrue()

GT 片段：`func testRequestAuthorization() { ⏎ notificationManager.requestAuthorization { [center] (granted, error) in ⏎ assert(granted, "Authorization should be granted") ⏎ assert(center?.requestAuthorizationWasCalled ?? false, "requestAuthorization should be called")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Helpers/NotificationManagerTests.swift:26`，距錨點 0 行）測試方法未標註 @MainActor，但使用非 Sendable 的 center 屬性

> `testRequestAuthorization` 方法未標註 `@MainActor`，但 closure 中捕捉了 `center`（MockUserNotificationCenter 已標註為 @unchecked Sendable）。雖然 @unchecked Sendable 可暫時規避編譯器檢查，但若測試在非主執行緒執行，可能導致資料競爭。建議將測試方法標註為 @MainActor，或確保所有存取都在主執行緒。

finding 片段：`notificationManager.requestAuthorization { [center] (granted, error) in`

## P0024

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）Prisma where 條件中 AND: undefined 可能導致查詢錯誤

> 當 `genericCalendarSuffixes` 為空或未提供時，`AND` 欄位被設為 `undefined`。Prisma 可能不接受 `undefined` 作為 `AND` 的值，導致查詢拋出錯誤或產生非預期行為。

**失敗情境**：呼叫 `findNextSubscriptionBatch` 時未傳入 `genericCalendarSuffixes`（例如舊程式碼或測試），Prisma 可能回傳錯誤，使批次訂閱流程中斷。

**建議**：僅在 `genericCalendarSuffixes` 存在且長度大於 0 時才加入 `AND` 條件，否則省略該欄位。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0025

**GT**（func）Linter exclusion points to wrong message key version

> The linter configuration exclusion was updated to reference 'Settings.Studies.Message.v148' but the original PR added this key to exclude quotes validation for the v136 message. Since the PR adds new v148 strings with similar content containing quotes, the exclusion should have remained as v136 to maintain the existing exclusion, or both versions should be excluded. This change will cause the linter to fail validation on the v136 string that legitimately needs the exclusion, while potentially missing issues in the new v148 string.

GT 片段：`"quotes": { ⏎ "enabled": true, ⏎ "exclusions": [ ⏎ "firefox-ios.xliff:Settings.Studies.Message.v148"`

**finding**（`.github/l10n/linter_config_ios.json:8`，距錨點 0 行）Linter 排除規則可能掩蓋格式問題

> 在 linter 設定中新增了排除 `firefox-ios.xliff:Settings.Studies.Message.v148`，這可能掩蓋了該字串的格式問題。建議確認該字串是否真的需要排除，或者是否應該修正格式問題而不是排除。

finding 片段：`"exclusions": [ ⏎ "firefox-ios.xliff:Settings.Studies.Message.v148" ⏎ ]`

## P0026

**GT**（rule）UI-related callback closure missing @MainActor annotation

> This closure is passed into an API whose `onActionTap` parameter is `@MainActor`, but the closure provided here is not annotated with `@MainActor`, violating the requirement that UI-related code/callbacks be main-actor isolated.

GT 片段：`onActionTap: { [weak self] action, cardName, completion in`

**finding**（`firefox-ios/Client/Coordinators/Launch/LaunchCoordinator.swift:271`，距錨點 0 行）將 @MainActor 閉包包在 Task 中可能造成非預期執行緒切換

> 原本 `onActionTap` 閉包標註為 `@MainActor`，直接呼叫 `onboardingService.handleAction`。修改後將呼叫包在 `Task { ... }` 中，但 `Task` 預設會繼承當前 actor context，若呼叫端已在 MainActor 上，則仍會在 MainActor 執行；然而若呼叫端不在 MainActor，則會切換到背景執行緒，可能導致 UI 操作或狀態更新不在主執行緒。建議明確使用 `Task { @MainActor in ... }` 或保留原本的直接呼叫。

finding 片段：`Task { ⏎ onboardingService.handleAction( ⏎ action, ⏎ from: cardName,`

## P0027

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 8 行）測試依賴外部網路可能導致不穩定

> captureFrameAndOrigin 使用真實的 WKWebView 載入 https://example.com，這需要網路連線。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。建議改用本地 HTML 字串或攔截請求的方式，避免外部依賴。

finding 片段：`webView.load(URLRequest(url: url))`

## P0028

**GT**（func）Generic calendar suffix filtering includes disabled providers

> The getGenericCalendarSuffixes() method uses Object.keys(GENERIC_CALENDAR_SUFFIXES) to iterate over all providers defined in the constant, including office365_calendar. However, getProviders() only returns ['google_calendar'], meaning Office365 is not actually enabled. This causes the subscription system to filter out Office365 calendar suffixes even when Office365 calendars shouldn't be processed at all. The filtering should only include suffixes for enabled providers by using this.getProviders() as in the original implementation.

GT 片段：`getGenericCalendarSuffixes(): string[] { ⏎ return Object.keys(GENERIC_CALENDAR_SUFFIXES).flatMap( ⏎ (provider) => GENERIC_CALENDAR_SUFFIXES[provider as CalendarSubscriptionProvider] ⏎ );`

**finding**（`packages/features/calendar-subscription/adapters/AdaptersFactory.ts:56`，距錨點 11 行）getProviders() 未包含 office365_calendar，導致通用日曆過濾失效

> `getProviders()` 目前只回傳 `['google_calendar']`，但 `GENERIC_CALENDAR_SUFFIXES` 定義了 `office365_calendar` 的後綴（目前為空陣列）。這使得 `checkForNewSubscriptions` 中的 `integrations` 參數只包含 `google_calendar`，因此 `office365_calendar` 的日曆永遠不會被選取，即使未來為其添加後綴也無法生效。

**失敗情境**：當團隊同時使用 Office 365 日曆且需要過濾通用日曆時，這些日曆仍會被訂閱，造成不必要的同步與快取。

**建議**：將 `getProviders()` 改為回傳所有支援的 provider，例如 `['google_calendar', 'office365_calendar']`，或從 `GENERIC_CALENDAR_SUFFIXES` 的鍵動態產生。

finding 片段：`getProviders(): CalendarSubscriptionProvider[] { ⏎ const providers: CalendarSubscriptionProvider[] = ["google_calendar"]; ⏎ return providers; ⏎ }`

## P0029

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444`，距錨點 5 行）metadata 為 null 時可能遺漏 XML 註解套用

> 當 `metadata` 為 null 時，整個 if 區塊會被跳過，導致該參數的 XML 註解（例如 `<param>` 或屬性註解）不會被套用。雖然這避免了 NullReferenceException，但可能造成 OpenAPI 文件中缺少描述。建議確認 `metadata` 為 null 的情境是否合理，若可能發生，應考慮其他處理方式（例如記錄警告或使用替代資訊）。

finding 片段：`if (metadata is not null ⏎ && metadata.MetadataKind == ModelMetadataKind.Property ⏎ && metadata.ContainerType is { } containerType ⏎ && metadata.PropertyName is { } propertyName)`

## P0030

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）新增的 print 陳述式可能造成 log 污染

> 在生產程式碼中使用 `print` 會將訊息輸出到 stdout，可能干擾正常的 log 格式或造成不必要的輸出。建議改用正式的 logging 模組，或移除該陳述式。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0031

**GT**（func）Race condition from premature TaskCompletionSource recreation

> The _receiveTcs TaskCompletionSource is recreated before checking if the buffer is zero-sized, creating a race condition in the WebSocketWrapper's ReceiveAsync implementation. When a zero-byte read occurs (buffer.Count == 0), the method returns early with the result but the TCS has already been reset. This means if another thread or the background task tries to set a result on the now-recreated TCS while this zero-byte read is in progress, it will affect the next receive operation rather than completing the current one. This breaks the synchronization contract and can cause message loss or out-of-order receives in the stateful reconnection test scenarios where WebSocket message sequencing is critical.

GT 片段：`public override async Task<WebSocketReceiveResult> ReceiveAsync(ArraySegment<byte> buffer, CancellationToken cancellationToken) ⏎ { ⏎ var res = await _receiveTcs.Task; ⏎ _receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

**finding**（`src/SignalR/server/StackExchangeRedis/test/RedisEndToEnd.cs:409`，距錨點 0 行）WebSocketWrapper.ReceiveAsync 中 _receiveTcs 重設位置可能導致競態條件

> 將 `_receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);` 移至 `await _receiveTcs.Task` 之後、零位元組讀取處理之前。這可能導致在零位元組讀取時，`_receiveTcs` 已被重設，但後續的 `SetReceiveResult` 可能設定到新的 TCS，而舊的 TCS 已完成，造成訊息遺失或錯誤。建議將重設邏輯放在處理完成後，或使用更安全的同步機制。

finding 片段：`_receiveTcs = new(TaskCreationOptions.RunContinuationsAsynchronously);`

## P0032

**GT**（rule）Missing semicolons in variable declarations

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but lines 88-90 rely on automatic semicolon insertion (ASI) instead

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 18 行）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接插入 `item.html`。若評論內容未經徹底消毒（例如包含 `<script>` 或事件處理器），攻擊者可注入任意 JavaScript，竊取管理員 session 或執行未授權操作。建議使用 sanitize 函式庫（如 DOMPurify）在渲染前清理 HTML，或改用安全的替代方案（如將內容轉為純文字）。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0033

**GT**（func）Inverted condition excludes file extensions from CFBundleDocumentTypes

> The condition for adding CFBundleTypeExtensions to CFBundleDocumentTypes is inverted. The code checks `if association.ext.is_empty()` and then attempts to insert the extensions array, which means extensions are only added when the vector is empty (resulting in an empty array being added), and extensions are skipped when they actually exist. This logic error will prevent file associations from being properly registered with their extensions on macOS, causing the system to not recognize which file types the application can handle.

GT 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

**finding**（`crates/tauri-bundler/src/bundle/macos/app.rs:328`，距錨點 0 行）`CFBundleTypeExtensions` 條件判斷可能相反

> 程式碼在 `association.ext.is_empty()` 為 true 時才插入 `CFBundleTypeExtensions`，但這與預期相反：通常應該在有副檔名時才加入此鍵。若 `ext` 為空，則不應加入；若 `ext` 非空，則應加入。目前的寫法會導致有副檔名時反而沒有寫入 `CFBundleTypeExtensions`，可能影響檔案關聯功能。

建議：將條件改為 `!association.ext.is_empty()`。

finding 片段：`if association.ext.is_empty() { ⏎ dict.insert( ⏎ "CFBundleTypeExtensions".into(), ⏎ plist::Value::Array(`

## P0034

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 17 行）測試依賴外部網路可能導致不穩定

> captureFrameAndOrigin 使用真實的 WKWebView 載入 https://example.com，這需要網路連線。在 CI 環境中若無網路或網路不穩定，測試可能逾時或失敗。建議改用本地 HTML 字串或攔截請求的方式，避免外部依賴。

finding 片段：`webView.load(URLRequest(url: url))`

## P0035

**GT**（rule）TypeScript using space indentation

> The rule requires TypeScript files to use tab characters for indentation, but this code uses spaces instead of tabs

GT 片段：`const filteredData = useMemo(() => { ⏎ return data.filter((blockDocument) => ⏎ blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()), ⏎ );`

**finding**（`ui-v2/src/components/blocks/block-document-combobox/block-document-combobox.tsx:69`，距錨點 0 行）搜尋過濾邏輯可能因大小寫處理不當而漏掉結果

> 在 `filteredData` 的 `useMemo` 中，使用 `blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase())` 進行過濾。但 `deferredSearch` 可能包含特殊正規表示式字元，雖然 `includes` 是字串比對，不會有正規表示式問題，但若 `blockDocument.name` 為 `null` 或 `undefined`，`toLowerCase()` 會拋出錯誤。

**失敗情境**：當某個區塊文件的名稱是 `null`（例如匿名區塊），使用者輸入搜尋字串時，`blockDocument.name?.toLowerCase()` 會因為 `name` 為 `null` 而拋出 `TypeError`，導致元件崩潰。

**建議**：使用 `blockDocument.name?.toLowerCase() ?? ""` 或先檢查 `name` 是否存在。

finding 片段：`blockDocument.name?.toLowerCase().includes(deferredSearch.toLowerCase()),`

## P0036

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行）遞迴順序變更可能導致狀態不一致

> 原本先標記邊為 skipped 再遞迴傳播，現在改為先遞迴再標記。若遞迴過程中發生例外，邊的狀態可能未被正確標記，導致後續節點狀態分析錯誤。建議確認此順序變更的必要性，或加入例外處理確保狀態一致性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0037

**GT**（rule）Missing semicolons in CommentContent hook declarations

> The added variable/state declarations rely on automatic semicolon insertion (ASI). The codebase rule requires explicit semicolons at the end of all statements.

GT 片段：`function CommentContent({item}: {item: Comment}) { ⏎ const contentRef = useRef<HTMLDivElement>(null) ⏎ const [isClamped, setIsClamped] = useState(false) ⏎ const [isExpanded, setIsExpanded] = useState(false)`

**finding**（`apps/posts/src/views/comments/components/comments-list.tsx:110`，距錨點 20 行）使用 dangerouslySetInnerHTML 渲染評論內容可能導致 XSS

> `CommentContent` 元件使用 `dangerouslySetInnerHTML` 直接插入 `item.html`。若評論內容未經徹底消毒（例如包含 `<script>` 或事件處理器），攻擊者可注入任意 JavaScript，竊取管理員 session 或執行未授權操作。建議使用 sanitize 函式庫（如 DOMPurify）在渲染前清理 HTML，或改用安全的替代方案（如將內容轉為純文字）。

finding 片段：`dangerouslySetInnerHTML={{__html: item.html || ''}}`

## P0038

**GT**（func）Wrong static subpath used for V2 UI

> When v2_enabled is True, the code incorrectly assigns static_subpath to prefect.__ui_static_subpath__ (V1 path) instead of prefect.__ui_v2_static_subpath__ (V2 path). This causes the V2 UI files to be copied to the wrong temporary directory (ui_build instead of ui_v2_build), resulting in incorrect file serving and potential conflicts with V1 UI files. The bug occurs because the variable assignment on line 464 doesn't follow the conditional logic properly.

GT 片段：`if v2_enabled: ⏎ source_static_path = prefect.__ui_v2_static_path__ ⏎ static_subpath = prefect.__ui_static_subpath__ ⏎ cache_key = f"v2:{prefect.__version__}:{base_url}"`

**finding**（`src/prefect/server/api/server.py:472`，距錨點 3 行）`static_subpath` 可能未定義導致 `NameError`

> `static_subpath` 在 `if v2_enabled` 為真時未被賦值，但此處直接使用 `str(static_subpath)`。若 `v2_enabled` 為真，將拋出 `NameError`。

**失敗情境**：啟用 V2 UI 時，伺服器啟動即失敗。

**建議修法**：在條件判斷前先定義 `static_subpath` 的預設值，或將此邏輯移入對應分支。

finding 片段：`static_dir = prefect.settings.PREFECT_UI_STATIC_DIRECTORY.value() or str( ⏎ static_subpath ⏎ )`

## P0039

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:645`，距錨點 3 行）讀取失敗時靜默重置 versionCode 為 1

> 當 `tauri.properties` 不存在或解析失敗時，`last_version_code` 為 `None`，`new_version_code` 會被設為 1。這可能導致意外重置版本碼，尤其是在檔案被誤刪或格式錯誤時，造成 Google Play 上傳失敗。

建議：在無法讀取時發出警告或錯誤，或提供明確的 fallback 策略。

finding 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1);`

## P0040

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:12`，距錨點 2 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const EventRepository = require('./repositories/event-repository'); ⏎ const ProductRepository = require('./repositories/product-repository'); ⏎ const RouterController = require('./controllers/router-controller'); ⏎ const MemberController = require('./controllers/member-controller');`

## P0041

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:469`，距錨點 1 行）organize_agent_history 中 tool_inputs 與 tool_responses 的解析邏輯重複且可能不一致

> 原本對 tool_input 和 observation 的 JSON 解析各自獨立，現在改為先檢查是否為空字串再解析。但兩者的處理邏輯幾乎相同，可考慮抽成輔助函式以減少重複。

失敗情境：若未來需要修改解析邏輯，可能只改到其中一處而導致不一致。

建議：將 JSON 解析邏輯抽成共用函式。

finding 片段：`tool_input_payload = agent_thought.tool_input ⏎ if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload)`

## P0042

**GT**（func）Incorrect logical operator in tearDown causing theme reset to be skipped for all iPad tests

> The tearDown method uses OR (||) instead of AND (&&) when checking if the test should skip theme reset. This causes the theme reset to be skipped for ALL tests running on iPad devices, not just the testSelectBottomPlacement test. The original intent was to skip theme reset only when BOTH conditions are true (the test is testSelectBottomPlacement AND it's running on iPad), but the current code skips it when EITHER condition is true. This will leave the theme in Dark mode after any test runs on iPad, potentially affecting subsequent tests that expect Light theme.

GT 片段：`override func tearDown() async throws { ⏎ if #available(iOS 17.0, *) { ⏎ if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there.`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29`，距錨點 0 行）tearDown 中提前 return 可能導致 app.terminate() 未執行

> 在 `tearDown()` 中，當 `self.name.contains("testSelectBottomPlacement") || iPad()` 為真時，會直接 `return`，跳過後續的 `app.terminate()`。這可能導致測試結束後應用程式仍在前景執行，影響後續測試的隔離性，甚至造成測試失敗。建議改為使用 `if` 條件包住主題切換邏輯，但保留 `app.terminate()` 的執行。

finding 片段：`if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there. ⏎ return ⏎ } else {`

## P0043

**GT**（func）Incorrect require path for MagicLink module after file rename

> The require statement references 'magic-link' (kebab-case) but the actual file is still named 'MagicLink.js' (PascalCase). This PR renamed many files to kebab-case, but this file was not renamed - it remains as MagicLink.js. When this code executes, Node.js will throw a MODULE_NOT_FOUND error because the path './../../lib/magic-link/magic-link' does not exist. The correct path should be './../../lib/magic-link/MagicLink' to match the actual file. This will cause the entire members API to fail to initialize, breaking member authentication, signup, and magic link functionality across the application.

GT 片段：`const {EmailSuppressedEvent} = require('../../email-suppression-list/email-suppression-list'); ⏎ const MagicLink = require('../../lib/magic-link/magic-link');`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:1`，距錨點 17 行）程式碼風格不一致：部分 require 陳述式缺少分號

> 在此檔案中，前 10 行的 require 陳述式沒有以分號結尾，但後續的 require 陳述式（例如 `const EventRepository = require('./repositories/event-repository');`）卻有分號。這可能是無意的，且與專案慣例不一致。建議統一加上分號。

finding 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

## P0044

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 10 行）路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確

> Unix 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，可能將不同大小寫的目錄視為相同，導致誤判。例如 `/home/user/.dotnet/corefx/cryptography/x509stores/ca` 與 `/HOME/USER/.DOTNET/...` 會被視為相同，但實際上可能指向不同位置。建議在 Unix 上使用 `StringComparison.Ordinal`，或根據作業系統選擇比較方式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0045

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行）fmterr 處理中未檢查 truncate 失敗後的檔案描述符狀態

> 在 `fmterr` 處理中，若 `truncate` 失敗，程式碼僅記錄錯誤，但未處理 `server.aof_fd` 的狀態。若 `server.aof_fd` 不為 -1，且 `truncate` 失敗，後續的 AOF 寫入可能會使用錯誤的檔案偏移。

建議在 `truncate` 失敗時，也確保 `server.aof_fd` 被正確處理（例如關閉或重置）。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0046

**GT**（func）Logout validation incorrectly rejects valid logout requests when HistoryEntryState is null

> The sign-out validation logic was modified to remove the null check for Navigation.HistoryEntryState before calling ValidateSignOutRequestState(). This causes ValidateSignOutRequestState() to return false when HistoryEntryState is null (since GetCachedNavigationState() returns null), which incorrectly redirects users to the logout failure page even for legitimate logout operations. The original code correctly allowed logout when HistoryEntryState is null by using the condition 'HistoryEntryState != null && !ValidateSignOutRequestState()', which only validated if state existed. This breaks backward compatibility with logout flows that don't use history state.

GT 片段：`private async Task ProcessLogOut(string returnUrl) ⏎ { ⏎ if (!ValidateSignOutRequestState()) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/RemoteAuthenticatorViewCore.cs:281`，距錨點 0 行）登出流程完全依賴 HistoryEntryState，可能導致登出失敗

> 原本的登出流程在 `Navigation.HistoryEntryState` 為 null 時會 fallback 到 `SignOutManager.ValidateSignOutState()`。移除 `SignOutSessionStateManager` 後，若 `HistoryEntryState` 為 null（例如使用者直接輸入登出 URL），`ValidateSignOutRequestState()` 可能回傳 false，導致登出失敗並導向失敗頁面。這可能破壞向後相容性。建議確認 `ValidateSignOutRequestState()` 對 null 的處理，或保留某種 fallback 機制。

finding 片段：`if (!ValidateSignOutRequestState()) ⏎ { ⏎ Log.LogoutOperationInitiatedExternally(Logger); ⏎ Navigation.NavigateTo(ApplicationPaths.LogOutFailedPath, AuthenticationNavigationOptions with { HistoryEntryState = "The logout was not initiated from within the page." });`

## P0047

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行）缺少錯誤邊界，useSuspenseQuery 失敗可能導致應用程式崩潰

> 元件使用 `useSuspenseQuery`，但沒有提供錯誤邊界（Error Boundary）。如果查詢失敗（例如網路錯誤或 API 回傳 500），React 會將錯誤拋出到最近的錯誤邊界；若沒有錯誤邊界，整個應用程式可能會 unmount。建議在元件外層或應用程式路由層級加入錯誤邊界，以妥善處理查詢失敗的情況。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## P0048

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，payload 會是 `true`。但在 `BookingWebhookFactory.createCancelledEventPayload` 中，預設值為 `false`。這兩個產生路徑的預設行為不同，可能導致下游 webhook 消費者收到不一致的資料。建議統一預設值，或明確在 DTO 層級提供。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0049

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:75`，距錨點 16 行）Popover 內容無法透過鍵盤操作

> PopoverTrigger 使用 Button 元件，但未提供 onKeyDown 或 focus 管理，鍵盤使用者無法開啟或瀏覽 popover 內容。建議加入適當的鍵盤事件處理（例如 Enter/Space 開啟、Escape 關閉），並確保焦點能移至 popover 內。

finding 片段：`<PopoverTrigger asChild> ⏎ <Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0"`

## P0050

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）React Scan 載入失敗時僅回傳空元件，且錯誤僅記錄於 console

> 當 `import('./scan')` 失敗時，catch 區塊回傳 `{ default: () => null }`，這會讓開發者無法在 UI 上察覺 devtools 未載入。雖然有 `console.error`，但在生產環境中可能被忽略。建議在開發模式下顯示一個明確的錯誤提示元件，或至少提供一個可視的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0051

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 19 行）XCTWaiter 使用方式錯誤，導致測試必定逾時

> `XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0052

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行）`getWarmupLimit` 可能回傳 `Infinity`，呼叫端需能處理

> 當 `day > totalDays` 時，函式回傳 `Infinity`。若呼叫端未預期此值，可能導致後續計算（如 `Math.min`、陣列 slice 等）出現非預期行為。建議確認所有呼叫端都能正確處理 `Infinity`，或改回傳一個明確的哨兵值（例如 `emailCount` 或 `Number.MAX_SAFE_INTEGER`）。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0053

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 setLoading(false) 可能導致 loading 狀態無法正確重設

> 在 minimal 模式下，成功送出表單後原本會呼叫 `setLoading(false)` 來重設 loading 狀態，但此 PR 移除了這一行。如果 `setLoading(false)` 是必要的，移除後可能導致 UI 一直顯示 loading 狀態。建議確認 minimal 模式下的狀態管理邏輯，若需要重設 loading 則應保留。

finding 片段：`setSuccess(true);`

## P0054

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）新增 ENABLE_WEBHOOKS 環境變數可能意外停用所有取消 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，`webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），將導致所有取消 webhook 停止發送，且無任何 log 提示。建議確認此環境變數是否為新引入，並考慮使用更特定的名稱（如 `ENABLE_CANCELLATION_WEBHOOKS`）或增加 log 警告。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0055

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）條件判斷反轉，導致 lock_version 永遠無法被設定

> 原本的條件是 `lock.is_some() && crate_lock_packages.is_empty()`，但邏輯上應該是在 lock 存在且 crate_lock_packages 不為空時才設定 lock_version。此變更將條件改為 `!crate_lock_packages.is_empty()`，但這會使得當 crate_lock_packages 為空時（例如找不到對應套件）反而進入設定 lock_version 的區塊，而此時 `crate_lock_packages` 為空，`lock_version` 會是空字串，最終不會被設定。反之，當 crate_lock_packages 不為空時，條件為 false，不會設定 lock_version。這將導致 lock_version 永遠無法被正確設定，可能影響依賴版本解析。

建議改回 `lock.is_some() && crate_lock_packages.is_empty()`，或根據實際需求調整條件。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0056

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:444`，距錨點 5 行）metadata 為 null 時直接跳過，可能遺漏文件產生

> 新增 `metadata is not null` 檢查後，若 `parameterDescription.ModelMetadata` 為 null，則整個 if 區塊跳過，不會嘗試從其他來源取得文件。若此情況常見，可能導致部分參數缺少描述。建議確認 null 是否為預期狀態，或考慮記錄警告。

finding 片段：`if (metadata is not null ⏎ && metadata.MetadataKind == ModelMetadataKind.Property`

## P0057

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行）Popover 內容的 hover 處理可能造成閃爍

> PopoverContent 上也設定了 onMouseEnter 和 onMouseLeave，當滑鼠從 trigger 移動到 popover 內容時，可能會因為 mouseleave 觸發關閉，然後 mouseenter 又開啟，造成閃爍。建議使用 Popover 的 hover 模式或設定適當的 delay。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0058

**GT**（func）Missing None-check allows invalid template render result to propagate

> The validation logic in `render_template` was modified to skip type checking when `rendered` is None. The original code correctly rejected None values with 'Template render result must be a string', but the new condition `if rendered is not None and not isinstance(rendered, str)` allows None to pass through and be returned. This will cause AttributeError exceptions downstream when code attempts to call string methods like `len()` on the None value, breaking template transformation workflows that depend on always receiving a valid string output.

GT 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

**finding**（`api/core/workflow/nodes/template_transform/template_renderer.py:37`，距錨點 0 行）render_template 可能回傳 None，導致後續 len() 拋出未捕捉例外

> 在 `CodeExecutorJinja2TemplateRenderer.render_template` 中，若 `execute_workflow_code_template` 回傳的 dict 中 `result` 鍵不存在或值為 None，則 `rendered` 會是 None，函式直接回傳 None。呼叫端 `TemplateTransformNode._run` 接著執行 `len(rendered)`，會拋出 `TypeError: object of type 'NoneType' has no len()`，且此例外未被捕捉，可能導致整個 workflow 失敗。建議在 renderer 中檢查 `rendered is None` 並拋出 `TemplateRenderError`，或在呼叫端先檢查。

finding 片段：`rendered = result.get("result") ⏎ if rendered is not None and not isinstance(rendered, str): ⏎ raise TemplateRenderError("Template render result must be a string.") ⏎ return rendered`

## P0059

**GT**（func）Missing related resources in action.triggered event on failure path

> In the fail() method, the code builds related_resources list that includes both automation-triggered-event and triggering-event references. However, when emitting the 'prefect.automation.action.triggered' event, it incorrectly uses self._resulting_related_resources instead of the newly built related_resources list. This means the action.triggered event will not include the automation-triggered-event or triggering-event links on the failure path, breaking the traceability chain documented in the PR. Users won't be able to trace from failed actions back to their source events.

GT 片段：`await events.emit( ⏎ Event( ⏎ occurred=triggered_action.triggered, ⏎ event="prefect.automation.action.triggered",`

**finding**（`src/prefect/server/events/actions.py:177`，距錨點 22 行）fail() 中 action.triggered 事件缺少 triggering-event 連結

> 即使修正了上述 blocker，`fail()` 中的 `action.triggered` 事件仍可能缺少 `triggering-event` 連結。目前 `related_resources` 僅在 `triggered_action.triggering_event` 存在時才加入該連結，但 `triggering_event` 可能為 None（例如 proactive trigger 且無最近事件）。這會導致事件缺少關鍵上下文。

**失敗情境**：當 `triggering_event` 為 None 時，`action.triggered` 事件將沒有 `triggering-event` 相關資源，使用者無法追溯觸發來源。

**建議修法**：確認此情境下是否應包含 `triggering-event` 連結，或至少確保 `automation-triggered-event` 連結存在。

finding 片段：`if triggered_action.triggering_event:`

## P0060

**GT**（rule）Direct malloc instead of zmalloc

> The rule requires using zmalloc() wrapper for memory allocation, but malloc() was used directly in the cluster initialization code

GT 片段：`/* This function is called at server startup in order to initialize cluster data ⏎ * structures that are shared between the different cluster implementations. */ ⏎ void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat));`

**finding**（`src/cluster.c:2137`，距錨點 0 行）clusterCommonInit() 呼叫順序可能導致未初始化相依性

> clusterCommonInit() 呼叫 resetClusterStats() 和 asmInit()，但這兩個函式可能依賴其他尚未初始化的全域狀態（例如 server.cluster 或 asm 相關結構）。原本在 clusterInit() 中呼叫的順序是 resetClusterStats() 在 clusterUpdateMyselfIp() 等之後，asmInit() 在最後。現在提前到 clusterInit() 之前，可能造成相依性問題。建議確認這些函式的相依性，或調整呼叫順序。

finding 片段：`void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat)); ⏎ resetClusterStats(); ⏎ asmInit();`

## P0061

**GT**（rule）SettingsTextFormatter and its methods lack explicit access control

> Rule requires explicit access control modifiers. The new nested class and its members use default (implicit) access levels (`class`, `static let shared`, and `func` declarations have no explicit `internal`/`private`/`public`).

GT 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {} ⏎ func formatStudiesText(appName: String) -> String {`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:418`，距錨點 0 行）SettingsTextFormatter 可能造成記憶體洩漏或執行緒安全問題

> 新增的 `SettingsTextFormatter` 使用 singleton 模式，但沒有明顯的必要性。如果這個類別只包含無狀態的方法，可以考慮使用靜態方法，避免不必要的 singleton。另外，如果未來加入狀態，需注意執行緒安全。

finding 片段：`class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎  ⏎ private init() {}`

## P0062

**GT**（rule）Missing semicolons in require statements

> The rule requires all JavaScript statements to end with explicit semicolons, but these require statements rely on automatic semicolon insertion (ASI) instead of having explicit semicolons.

GT 片段：`const {Router} = require('express') ⏎ const body = require('body-parser') ⏎ const errors = require('@tryghost/errors') ⏎ const logging = require('@tryghost/logging')`

**finding**（`ghost/core/core/server/services/members/members-api/members-api.js:6`，距錨點 0 行）require 陳述式缺少分號

> 此檔案中多個 require 陳述式結尾缺少分號，與專案其他檔案的風格不一致。雖然 JavaScript 會自動插入分號（ASI），但建議補上以維持一致性。

finding 片段：`const PaymentsService = require('./services/payments-service') ⏎ const TokenService = require('./services/token-service') ⏎ const GeolocationService = require('./services/geolocation-service') ⏎ const MemberBREADService = require('./services/member-bread-service')`

## P0063

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:99`，距錨點 0 行）移除 Sha256 的 Windows 限定可能影響跨平台行為

> 原本 `HashAlgorithm::Sha256` 只在 Windows 上可用，現在移除 `#[cfg(target_os = "windows")]`，使其在所有平台可用。這可能是為了支援跨平台雜湊驗證，但需確認是否有其他平台特定邏輯依賴此 cfg。若無其他限制，此變更應屬安全，但建議確認相關使用情境。

finding 片段：`pub enum HashAlgorithm { ⏎ Sha256, ⏎ Sha1, ⏎ }`

## P0064

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）extractSlotFromKeysResult 迴圈邊界錯誤導致越界讀取

> 在 `extractSlotFromKeysResult` 中，迴圈條件 `j <= keys_result->numkeys` 應為 `j < keys_result->numkeys`。當 `j == numkeys` 時，`keys_result->keys[j]` 會讀取到陣列之外，造成未定義行為，可能導致程式崩潰或洩漏記憶體內容。

建議修正為：
```c
for (int j = 0; j < keys_result->numkeys; j++) {
```

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0065

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）_serverToken 型別不一致可能導致 JWT 驗證失敗

> 在 `getServerToken` 中，原本 `this._serverToken = tokenData.token` 儲存的是字串，但現在改為 `this._serverToken = tokenData` 儲存整個物件。然而，後續使用 `this._serverToken` 的地方（例如 `_isJWTExpired(this._serverToken)` 或回傳給呼叫端）仍預期它是字串。這會導致 `jwt.decode` 收到物件而非字串，可能拋出錯誤或回傳 null，進而使 token 永遠被視為過期，每次請求都重新產生 token，造成效能問題或功能失效。

建議：維持 `this._serverToken = tokenData.token`，或同步修改所有使用 `_serverToken` 的地方以處理物件型別。

finding 片段：`this._serverToken = tokenData;`

## P0066

**GT**（rule）Windows-only Sha256 lacks platform guards

> The HashAlgorithm::Sha256 variant is only used for Windows-specific WIX tooling downloads but lacks #[cfg(target_os = "windows")] guards. Platform-specific code should use conditional compilation attributes to ensure it only compiles on supported platforms.

GT 片段：`#[allow(dead_code)] ⏎ #[derive(Clone, Copy)] ⏎ pub enum HashAlgorithm { ⏎ Sha256,`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:100`，距錨點 0 行）移除 HashAlgorithm::Sha256 的 cfg 屬性可能影響跨平台編譯

> 原本 `Sha256` variant 有 `#[cfg(target_os = "windows")]`，現在移除後在所有平台都會啟用。若其他平台原本未使用 Sha256，可能導致未使用的依賴或編譯警告。請確認此變更是否必要。

finding 片段：`Sha256,`

## P0067

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）setupSkeletonAddressBarsLayout 中新增的 isLandscape 變數未使用

> 在 `setupSkeletonAddressBarsLayout` 中，新增了 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`，但該變數在後續程式碼中並未被使用。這可能是開發過程中的殘留，建議移除或實際使用。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0068

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`[Fact] ⏎ public async Task CanPrerender_ClosedGenericComponent_ClientMode()`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 20 行）ClientMode 測試中 preamble marker 的型別名稱斷言錯誤

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，實際渲染的元件型別是 `GenericComponent<int>`，但斷言卻使用了 `typeof(GenericComponent<string>).Assembly.GetName().Name` 和 `typeof(GenericComponent<string>).FullName`。這會導致測試失敗，因為 `GenericComponent<string>` 的 full name 與 `GenericComponent<int>` 不同。建議改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0069

**GT**（func）Incorrect field path for extracting original bundle identifier

> The code attempts to extract the original identifier from the 'bundle' field instead of the root-level 'identifier' field. Since 'bundle' is an object (not a string), the `.as_str()` call will always fail, causing `original_identifier` to always be None. This breaks the ability to track and report which config file overwrites the bundle identifier, as the `find_bundle_identifier_overwriter()` method relies on comparing against the original identifier value.

GT 片段：`let original_identifier = config ⏎ .as_object() ⏎ .and_then(|config| config.get("bundle")) ⏎ .and_then(|id| id.as_str())`

**finding**（`crates/tauri-cli/src/helpers/config.rs:177`，距錨點 0 行）取得 identifier 的欄位從 "identifier" 改為 "bundle"，可能導致行為錯誤

> 原本從 config 物件中取得 "identifier" 欄位，現在改為取得 "bundle" 欄位。但 "bundle" 通常是一個物件，而非字串，因此 `as_str()` 會回傳 `None`，導致 `original_identifier` 永遠為 `None`。這可能影響後續依賴此值的邏輯（例如合併設定或驗證）。請確認此變更是否為預期，若不是，應改回 "identifier"。

finding 片段：`.and_then(|config| config.get("bundle"))`

## P0070

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1509`，距錨點 5 行）新增的 `update` 方法回傳型別可能與介面不符

> `IBookingRepository` 介面中定義 `update` 回傳 `Promise<Booking>`，但 `BookingRepository` 的 `update` 方法直接回傳 `this.prismaClient.booking.update(...)`，其回傳型別是 Prisma 的 `Booking` 型別，可能包含更多欄位，但型別上應相容。然而，若 `BookingUpdateData` 的欄位與 Prisma 的 `BookingUpdateInput` 不完全一致，可能導致型別錯誤。建議確認介面與實作的型別一致性。

finding 片段：`async update({ where, data }: { where: BookingWhereUniqueInput; data: BookingUpdateData }) { ⏎ return await this.prismaClient.booking.update({ ⏎ where, ⏎ data,`

## P0071

**GT**（func）Test completes without waiting for async image download

> The test was converted from async to synchronous but the expectation and wait statement were removed. This causes the test to complete immediately without waiting for the asynchronous image download callback to execute. The XCTAssert statements inside the completion handler will never be verified, resulting in false positive test passes even if the image download fails or produces incorrect results. This is a critical testing bug that undermines test reliability.

GT 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ guard let imageData = try? dataFor(type: assetType) else {`

**finding**（`BrowserKit/Tests/SiteImageViewTests/SVGImageProcessorTests.swift:12`，距錨點 0 行）移除 expectation 可能導致測試提前結束

> 在 `testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase` 中，原本使用 `expectation` 等待非同步下載完成，但修改後移除了 `expectation` 的建立與等待，且未使用 `wait(for:)`。這可能導致測試方法在非同步回呼執行前就返回，使得測試永遠通過，無法驗證實際行為。建議保留 expectation 或改用 `wait(for:)` 來等待非同步操作。

finding 片段：`func testDownloadingSVGImage_withKingfisherProcessor_forStandardSVGCase() { ⏎ let assetType: AssetType = .svgCase1 ⏎ let expectedRasterSize = CGSize(width: 360, height: 360) ⏎ `

## P0072

**GT**（rule）Force unwrap of URL initializer in tests (second occurrence)

> Same SwiftLint force-unwrapping violation as above; appears again in the added lines for another test.

GT 片段：`guard let (frame, origin) = WebKitTestHelpers.captureFrameAndOrigin(for: URL(string: "https://example.com")!) else {`

**finding**（`BrowserKit/Tests/WebEngineTests/WKUIHandlerTests.swift:34`，距錨點 4 行）expectation 在 decisionHandler 外被 fulfill，可能導致測試提前結束

> 在 `testRequestMediaCaptureSuccess` 中，`expectation.fulfill()` 被放在 `wait(for:)` 之後，而不是在 `decisionHandler` 內。這會導致 `wait(for:)` 永遠等不到 expectation 被 fulfill，直到逾時。

應將 `expectation.fulfill()` 移回 `decisionHandler` 內，與其他測試保持一致。

finding 片段：`wait(for: [expectation]) ⏎ expectation.fulfill()`

## P0073

**GT**（func）Window size applied before position in window_features causing incorrect window placement

> In the window_features method, the size configuration is now applied before the position configuration, reversing the original order. This can lead to incorrect window positioning behavior because some window managers calculate the final window position based on the current window size. When the size is set after the position, the position may be recalculated or adjusted incorrectly. This particularly affects windows opened through the on_new_window handler when both size and position are specified in NewWindowFeatures.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）`window_features` 中 size 與 position 的設定順序對調可能影響視窗初始狀態

> 原本先設定 position 再設定 size，現在改為先設定 size 再設定 position。在部分平台（如 Windows）上，設定 position 後再設定 size 可能導致視窗位置被重新計算，反之亦然。若此順序調整非刻意為之，可能造成視窗初始位置或大小不符合預期。建議確認此變更的意圖，或恢復原本順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0074

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）HPEXPIREAT 傳播時建立的 argv[2] 字串物件未釋放，造成記憶體洩漏

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);` 並傳遞給 `alsoPropagate`。但 `alsoPropagate` 不會取得物件的所有權，呼叫後此物件不會被釋放。每次執行具有過期時間的 HINCRBYFLOAT 都會洩漏一個 robj，長期下來可能導致記憶體耗盡。

建議在 `alsoPropagate` 呼叫後立即 `decrRefCount(argv[2]);`，或改用其他方式建立暫時物件（例如使用 stack 上的 robj 或直接傳遞字串）。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0075

**GT**（func）Logic inversion in hasPendingInviteByUserId method

> The hasPendingInviteByUserId method checks for accepted:true memberships instead of accepted:false (pending invites). This inverts the method's logic - it will return true when users have accepted team memberships rather than pending invites. This breaks the onboarding flow for users with team invites, causing users with accepted memberships to be redirected to personal onboarding instead of users with pending invites. The method name and its intended purpose clearly indicate it should check for pending (non-accepted) invites.

GT 片段：`static async hasPendingInviteByUserId({ userId }: { userId: number }): Promise<boolean> { ⏎ const pendingInvite = await prisma.membership.findFirst({ ⏎ where: { ⏎ userId,`

**finding**（`packages/features/membership/repositories/MembershipRepository.ts:588`，距錨點 0 行）hasPendingInviteByUserId 查詢條件錯誤：accepted 應為 false

> 方法名稱為 `hasPendingInviteByUserId`，但查詢條件使用 `accepted: true`，這會導致：
- 有 pending invite（accepted: false）的使用者，此方法回傳 false，不會被重導向。
- 沒有 pending invite 但已有 accepted membership 的使用者，此方法回傳 true，被錯誤重導向。

這與 PR 目的完全相反。應將條件改為 `accepted: false`。

finding 片段：`accepted: true,`

## P0076

**GT**（func）Inverted renderer type check prevents circuit restart

> The condition checking for different renderer types has been inverted from `!==` to `===`. This causes the function to throw an error when the SAME renderer type tries to re-enable JS root components (e.g., during circuit restart), which is the exact scenario that should be allowed. The original intent was to throw an error only when a DIFFERENT renderer type attempts to enable root components. This bug breaks circuit restart functionality, causing applications to fail when users reconnect after a circuit disconnect.

GT 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

**finding**（`src/Components/Web.JS/src/Rendering/JSRootComponents.ts:126`，距錨點 0 行）多 host 情境下 manager 可能被錯誤覆寫

> 條件 `if (manager && currentRendererId === rendererId)` 僅在 rendererId 相同時拋出錯誤。若不同 rendererId（例如 Server 與 WebAssembly 同時存在），則會直接覆寫全域變數 `manager` 與 `currentRendererId`，導致先前 host 的 manager 遺失。這可能造成動態 root components 操作指向錯誤的 manager，或先前 host 的元件無法正常運作。

建議：在多 host 情境下應明確禁止或隔離狀態，例如使用 Map 以 rendererId 為鍵儲存 manager，或至少在覆寫前記錄警告並確保舊 manager 不再被使用。

finding 片段：`if (manager && currentRendererId === rendererId) { ⏎ // A different renderer type (e.g., Server vs WebAssembly) is trying to enable JS root components. ⏎ // This is a multi-host scenario which is not supported for dynamic root components. ⏎ throw new Error('Dynamic root components have already been `

## P0077

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）HPEXPIREAT 傳播時建立的 argv[2] 字串物件未釋放，造成記憶體洩漏

> 在 `hincrbyfloatCommand` 中，當 `has_expiration` 為真時，程式碼建立 `argv[2] = createStringObjectFromLongLong(expireat);` 並傳遞給 `alsoPropagate`。但 `alsoPropagate` 不會取得物件的所有權，呼叫後此物件不會被釋放。每次執行具有過期時間的 HINCRBYFLOAT 都會洩漏一個 robj，長期下來可能導致記憶體耗盡。

建議在 `alsoPropagate` 呼叫後立即 `decrRefCount(argv[2]);`，或改用其他方式建立暫時物件（例如使用 stack 上的 robj 或直接傳遞字串）。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0078

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:106`，距錨點 0 行）buildInviteLink 條件判斷反轉，導致邀請連結錯誤

> 原本的邏輯是 `if (!isOrgContext) { return teamInviteLink; }`，現在改為 `if (isOrgContext) { return teamInviteLink; }`。這會使得在組織情境下（isOrgContext 為 true）直接回傳 teamInviteLink，而沒有附加 getting started 路徑；反之在非組織情境下卻會附加 getting started 路徑。

失敗情境：組織團隊的邀請連結缺少必要的 onboarding 參數，使用者點擊後可能無法正確導向。

建議：恢復原本的條件判斷，或確認邏輯是否應為 `if (isOrgContext) { ... } else { return teamInviteLink; }`。

finding 片段：`if (isOrgContext) { ⏎ return teamInviteLink; ⏎ }`

## P0079

**GT**（func）Polling logic performs one extra retry attempt beyond configured maximum

> The confirmation polling interval increments the retry counter after checking if the limit is reached, combined with changing the condition from `>` to `>=`. This creates an off-by-one error where the system will actually make 13 API calls (retries 0-12) instead of the intended 12 calls defined by MAX_CONFIRMATION_RETRIES. The counter starts at 0, gets incremented to 12, makes a call, then on the next iteration checks if 12 >= 12 and only then stops. This wastes API resources and delays the timeout error message by one additional polling interval (5 seconds).

GT 片段：`const confirmHandleInterval = setInterval(async () => { ⏎ if (retryCountRef.current >= MAX_CONFIRMATION_RETRIES) { ⏎ clearInterval(confirmHandleInterval); ⏎ toast.error('Something went wrong, please try again.');`

**finding**（`apps/activitypub/src/views/Preferences/components/BlueskySharing.tsx:78`，距錨點 25 行）輪詢 effect 缺少對 disableBlueskyMutation 的依賴

> 在 `useEffect` 中呼叫了 `disableBlueskyMutation.mutateAsync()`，但依賴陣列僅包含 `account?.blueskyEnabled`, `account?.blueskyHandleConfirmed`, `confirmHandle`，並註解 `disableBlueskyMutation is stable`。若 mutation 函式因 hook 重新渲染而改變（例如 queryClient 或 handle 變化），可能導致 effect 使用過時的 mutation 函式。建議將 `disableBlueskyMutation` 加入依賴陣列，或確認其穩定性。

finding 片段：`// eslint-disable-next-line react-hooks/exhaustive-deps ⏎ }, [account?.blueskyEnabled, account?.blueskyHandleConfirmed, confirmHandle]); // disableBlueskyMutation is stable`

## P0080

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 13 行）拖曳排序的索引計算未考慮 prefixItems，可能導致資料錯位

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 預期的索引是相對於可移動項目（即排除 prefixItems 後）的索引。當陣列包含 prefixItems 時，拖曳非 prefix 項目會導致移動到錯誤的位置，造成資料順序錯誤。

例如：prefixItems 有 2 項，可移動項目從索引 2 開始。若將索引 2 的項目拖到索引 3，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會將項目移到可移動項目中的索引 3，實際上可能超出範圍或錯位。

建議：在計算索引時減去 `prefixItemsCount`，或改用可移動項目的相對索引。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0081

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）malloc 失敗未處理，可能導致 null pointer dereference

> `slot_buffer = malloc(sizeof(int) * keys_result->numkeys);` 沒有檢查回傳值。若記憶體配置失敗，`slot_buffer` 為 NULL，後續 `slot_buffer[j] = this_slot;` 會寫入 NULL 位址，造成程式崩潰。

失敗情境：在記憶體不足或 `numkeys` 極大時，malloc 可能失敗，導致伺服器 crash。

建議修正：檢查 malloc 回傳值，若為 NULL 則回傳錯誤或改用 stack allocation（若 numkeys 有上限）。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0082

**GT**（rule）Strict mode disabled in TypeScript config

> The rule requires TypeScript configuration files to have 'strict' set to true in compilerOptions, but it was set to false

GT 片段：`/* Linting */ ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`apps/activitypub/tsconfig.json:18`，距錨點 0 行）關閉 TypeScript strict 模式

> 將 `strict` 從 `true` 改為 `false` 會大幅降低型別安全，可能隱藏潛在的 null/undefined 錯誤。此變更與 PR 目的無關，且會影響整個專案的型別檢查。建議恢復為 `true`，並修正因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0083

**GT**（func）Type mismatch in _isJWTExpired call after token caching change

> The _isJWTExpired method expects a string token parameter, but after line 98 changes this._serverToken from storing just the token string to storing the entire tokenData object, line 96 now passes an object {token: string, exp: number} to _isJWTExpired instead of a string. This causes jwt.decode() at line 164 to fail when trying to decode an object instead of a JWT string. The method will always return true (treating the token as expired) on subsequent calls, forcing unnecessary token regeneration on every request and breaking the token caching mechanism entirely.

GT 片段：`if (!this._serverToken || this._isJWTExpired(this._serverToken)) { ⏎ const tokenData = this._generateToken({name, expiresInMinutes}); ⏎ this._serverToken = tokenData; ⏎ this._serverTokenExp = tokenData.exp;`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:98`，距錨點 0 行）`_serverToken` 型態不一致可能導致下游錯誤

> `_serverToken` 原本存的是字串（`tokenData.token`），現在改存整個 `tokenData` 物件。但 `getToken` 回傳的 `token` 欄位型態仍標示為 `string`，且其他使用 `getToken` 的程式碼可能預期收到字串。若下游直接將 `token` 用於 HTTP header 或字串操作，會得到 `[object Object]` 或錯誤。建議確認所有呼叫端，或改回存字串並另外保存 exp。

finding 片段：`this._serverToken = tokenData;`

## P0084

**GT**（func）Reply threading broken for nested comments due to incorrect in_reply_to_id

> The submit function uses `parent.id` as `in_reply_to_id` instead of `openForm.in_reply_to_id`. For nested replies (replying to a reply), these values differ: `openForm.in_reply_to_id` points to the specific comment being replied to, while `parent.id` points to the top-level parent comment. Using `parent.id` breaks the reply chain, causing nested replies to be incorrectly threaded to the wrong comment. This destroys the conversation hierarchy and makes it impossible to track which comment a user is actually replying to in multi-level discussions.

GT 片段：`const submit = useCallback(async ({html}) => { ⏎ // Send comment to server ⏎ await dispatchAction('addReply', { ⏎ parent: parent,`

**finding**（`apps/comments-ui/src/components/content/forms/reply-form.tsx:30`，距錨點 0 行）回覆目標改為 parent.id 可能影響巢狀回覆

> 原本使用 `openForm.in_reply_to_id` 作為回覆目標，現在改為 `parent.id`。若 `parent` 是回覆的回覆（即巢狀回覆），`parent.id` 可能不是正確的頂層回覆 ID，導致回覆鏈結錯誤。請確認此變更是否符合預期，並考慮是否應保留 `openForm.in_reply_to_id` 或使用其他方式取得正確的父 ID。

finding 片段：`in_reply_to_id: parent.id,`

## P0085

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）變更標記邊為跳過的順序可能導致競態條件

> 原本先標記邊為跳過再遞迴傳播，現在改為先遞迴傳播再標記。若遞迴過程中依賴邊的狀態，可能讀到未更新的狀態。需要確認 `propagate_skip_from_edge` 是否會讀取該邊的狀態，以及此變更是否會影響其他並行操作。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0086

**GT**（func）Incorrect skeleton bar constraint references causing toolbar layout failure

> The toolbar's leading anchor constraint is incorrectly set to rightSkeletonAddressBar.trailingAnchor instead of leftSkeletonAddressBar.trailingAnchor. This creates contradictory Auto Layout constraints where the toolbar's leading edge is constrained to the right skeleton bar's trailing edge, while its trailing edge is also constrained to the same right skeleton bar's leading edge. This will cause an Auto Layout constraint conflict and render the toolbar incorrectly positioned or completely broken when tab swiping is enabled.

GT 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true ⏎ toolbar.trailingAnchor.constraint(equalTo: rightSkeletonAddressBar.leadingAnchor).isActive = true`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:448`，距錨點 0 行）toolbar 的 leadingAnchor 錯誤地約束到 rightSkeletonAddressBar 的 trailingAnchor

> 在 `setupToolbarConstraints` 中，當啟用滑動分頁時，toolbar 的 leadingAnchor 被設定為 `rightSkeletonAddressBar.trailingAnchor`，但根據上下文，應該約束到 `leftSkeletonAddressBar.trailingAnchor`。這可能導致 toolbar 的位置錯誤，特別是在 RTL 或特定佈局下。

**失敗情境**：在啟用滑動分頁的裝置上，地址欄可能與左側骨架欄重疊或位置偏移，影響使用者體驗。

**建議修法**：將 `rightSkeletonAddressBar` 改為 `leftSkeletonAddressBar`。

finding 片段：`toolbar.leadingAnchor.constraint(equalTo: rightSkeletonAddressBar.trailingAnchor).isActive = true`

## P0087

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致可能導致下游誤判

> 在 v2021-10-20 的 payload builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，若 DTO 未提供此欄位，預設為 `true`。但在 `BookingWebhookFactory` 中，`requestReschedule` 預設為 `false`。這兩個建構路徑的預設值相反，可能導致同一事件在不同 webhook 版本或路徑下產生不一致的 payload，下游系統若依此欄位判斷是否為 reschedule 請求，將可能誤判。

建議統一預設值，或明確在 DTO 層級設定，避免隱含預設。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0088

**GT**（func）Type mismatch in total_price initialization breaks Decimal arithmetic

> The total_price field is initialized with integer 0 instead of Decimal(0), creating a type inconsistency. The MessageAgentThought model defines total_price as Mapped[Decimal | None] expecting a Decimal type, and other price fields (message_unit_price, answer_unit_price, etc.) are correctly initialized with Decimal types. This inconsistency will cause type errors during price calculations when the system attempts to perform Decimal arithmetic operations (addition, multiplication) between Decimal and int types, potentially breaking billing computations or causing runtime exceptions.

GT 片段：`answer_price_unit=Decimal(0), ⏎ tokens=0, ⏎ total_price=0, ⏎ position=self.agent_thought_count + 1,`

**finding**（`api/core/agent/base_agent_runner.py:320`，距錨點 6 行）create_agent_thought 中 message_price_unit 與 answer_price_unit 的初始值可能導致價格計算錯誤

> 在 create_agent_thought 中，`message_price_unit` 被設為 `Decimal("0.001")`，而 `answer_price_unit` 被設為 `Decimal(0)`。這與模型定義中的預設值相反（模型定義中 message_price_unit 預設為 0.001，answer_price_unit 預設為 0.001）。這可能導致後續價格計算時，answer 部分的價格被錯誤地乘以 0，造成總價低估。

失敗情境：當 agent 產生 answer 時，若未更新 answer_price_unit，則總價計算會將 answer 的 token 數乘以 0，導致費用計算錯誤。

建議：確認初始值應與模型預設值一致，或明確設定為正確的價格單位。

finding 片段：`message_price_unit=Decimal("0.001"), ⏎ answer_price_unit=Decimal(0),`

## P0089

**GT**（func）Keyword trimming logic may break escape sequences

> The workflow app service trims the keyword to 30 characters and then applies escape_like_pattern(). However, this creates a subtle bug: if a backslash character appears exactly at position 30, the trim could split an escape sequence that the user intended. More critically, if special characters appear in positions 28-30, they'll be included in the escaped output, but any context around them will be lost, potentially creating malformed escape sequences. The trimming should occur AFTER escaping to preserve the integrity of the escape sequences, or better yet, the escaping should be done before any string manipulation.

GT 片段：`# Escape special characters in keyword to prevent SQL injection via LIKE wildcards ⏎ keyword_trimmed = keyword[:30] ⏎ escaped_keyword = escape_like_pattern(keyword_trimmed) ⏎ keyword_like_val = f"%{escaped_keyword}%"`

**finding**（`api/services/workflow_app_service.py:94`，距錨點 0 行）移除 unicode_escape 編碼可能改變搜尋行為

> 原本的程式碼將關鍵字進行 unicode_escape 編碼，並將 "\\u" 替換為 "\\\\u"，這可能是為了處理 JSON 欄位中的 Unicode 表示。新程式碼直接使用原始關鍵字，可能導致搜尋行為不一致。例如，若輸入包含非 ASCII 字元，原本的編碼可能使其與 JSON 中的 Unicode 轉義序列匹配，而新程式碼則無法匹配。建議確認此變更是否會影響現有功能，並考慮保留必要的編碼處理。

finding 片段：`keyword_like_val = f"%{escaped_keyword}%"`

## P0090

**GT**（func）Variable shadowing breaks sampling consistency for STREAM objects

> A local `samples` variable is declared at line 1319 within the OBJ_STREAM branch, shadowing the outer `samples` variable declared at line 1214. This prevents the outer samples counter from being updated during stream memory calculation. While this doesn't break the stream calculation itself, it violates the function's sampling design pattern where the outer `samples` variable tracks total sampling across all object type branches. This inconsistency could lead to unexpected behavior if the function logic is modified to check or use the outer samples counter after processing.

GT 片段：`raxStart(&ri,s->rax); ⏎ raxSeek(&ri,"^",NULL,0); ⏎ size_t lpsize = 0; ⏎ size_t samples = 0;`

**finding**（`src/object.c:1330`，距錨點 10 行）stream 的 listpack 數量計算可能多算一個

> 在 stream 的記憶體估算中，原本使用 `lpsize * (s->rax->numele-1)` 計算 listpack 的總大小，現在改為 `lpsize * s->rax->numele`。但 `s->rax->numele` 是 radix tree 中的元素數量，而 listpack 的數量可能與元素數量不同。若 radix tree 中的每個元素對應一個 listpack，則 listpack 數量應為 `numele`，但若最後一個 listpack 是部分填充的，則可能不應計入平均。此變更可能導致記憶體估算偏高。建議確認 stream 的資料結構，並根據實際 listpack 數量計算。

finding 片段：`asize += lpsize * s->rax->numele;`

## P0091

**GT**（rule）Test method missing Arrange/Act/Assert comments

> The new test method does not include the required '// Arrange', '// Act', and '// Assert' (or '// Act & Assert') comments to delineate phases per the AAA pattern.

GT 片段：`[Fact] ⏎ public async Task SupportsRouteParametersFromControllers() ⏎ { ⏎ var source = """`

**finding**（`src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:141`，距錨點 38 行）測試方法缺少 Arrange/Act/Assert 結構，且未驗證 Summary

> 測試 `SupportsRouteParametersFromControllers` 直接驗證 `path.Parameters[0].Description`，但未驗證 Summary 是否正確。若 PR 同時修改了 Summary 行為，此測試可能無法捕捉回歸。建議增加對 Summary 的斷言。

finding 片段：`Assert.Equal("The id of the user.", path.Parameters[0].Description);`

## P0092

**GT**（rule）Broad exception catch (except Exception) added for tool_inputs JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type (e.g., `json.JSONDecodeError`, `TypeError`) and/or handling specific failure modes. The new code introduces a broad `except Exception:` while parsing JSON.

GT 片段：`if tool_input_payload: ⏎ try: ⏎ tool_inputs = json.loads(tool_input_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 26 行）工具回應內容誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 ToolPromptMessage 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具呼叫的回應內容變成工具的輸入參數，而非實際的輸出結果，造成對話歷史中工具回應錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史訊息中的工具回應會顯示輸入參數而非輸出，導致後續 LLM 判斷錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0093

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）遞迴順序變更可能導致狀態不一致

> 原本先標記邊為 skipped 再遞迴傳播，現在改為先遞迴再標記。若遞迴過程中發生例外，邊的狀態可能未被正確標記，導致後續節點狀態分析錯誤。建議確認此順序變更的必要性，或加入例外處理確保狀態一致性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0094

**GT**（func）Race condition in email service initialization - dependency order violated

> The emailAddressService.init() was moved from sequential await execution into the parallel Promise.all block alongside emailService.init(). The comment explicitly states 'newsletter service and email service depend on email address service', indicating a required initialization order. The EmailServiceWrapper's init() method imports and uses emailAddressService, expecting it to be fully initialized. By running these initializations in parallel, emailService may attempt to access emailAddressService before it has completed initialization, leading to undefined behavior, null reference errors, or incorrect email configuration. This race condition can cause intermittent failures that are difficult to reproduce and debug.

GT 片段：`// NOTE: newsletter service and email service depend on email address service ⏎ await Promise.all([ ⏎ emailAddressService.init(), ⏎ identityTokens.init(),`

**finding**（`ghost/core/core/boot.js:352`，距錨點 0 行）emailAddressService.init() 改為非同步呼叫可能影響相依服務

> 原本 `emailAddressService.init()` 是同步呼叫（前面有 `await`），現在改為在 `Promise.all` 中非同步執行。若其他服務（如 newsletter 或 email service）依賴 email address service 初始化完成，可能導致競態條件。建議確認這些服務是否已正確處理非同步初始化。

finding 片段：`emailAddressService.init(),`

## P0095

**GT**（func）Poll interval delay happens before first status check in timeout loop

> The polling loop on lines 229-235 was changed to sleep *before* checking the flow run status, rather than after. This means when `timeout` is very short (e.g., just above 0), the function will sleep for `poll_interval` seconds first, potentially causing the timeout to expire before even the first status check occurs. This wastes valuable timeout time and changes the behavior - the original code would check status immediately, then sleep between subsequent checks. For quick-running flows, this could mean missing their completion state entirely due to the initial unnecessary delay.

GT 片段：`with anyio.move_on_after(timeout): ⏎ while True: ⏎ await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

**finding**（`src/prefect/deployments/flow_runs.py:231`，距錨點 0 行）輪詢邏輯變更：先 sleep 再檢查狀態，可能延遲最終結果

> 原本的輪詢迴圈先讀取 flow run 狀態，若未完成則 sleep；現在改為先 sleep 再讀取。這會導致即使 flow run 在第一次檢查前已完成，也會等待 `poll_interval` 秒後才回傳。

**失敗情境**：當 `timeout` 設定較小且 `poll_interval` 較大時，可能超過 timeout 才回傳，或延遲回傳已完成的结果。

**建議**：恢復先檢查再 sleep 的順序，或使用 `anyio.move_on_after` 搭配更精確的輪詢。

finding 片段：`await anyio.sleep(poll_interval) ⏎ flow_run = await client.read_flow_run(flow_run_id)`

## P0096

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）`window_features` 中 size 與 position 的設定順序對調可能影響視窗初始狀態

> 原本先設定 position 再設定 size，現在改為先設定 size 再設定 position。在部分平台（如 Windows）上，設定 position 後再設定 size 可能導致視窗位置被重新計算，反之亦然。若此順序調整非刻意為之，可能造成視窗初始位置或大小不符合預期。建議確認此變更的意圖，或恢復原本順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0097

**GT**（rule）Broad exception catch (except Exception) added for tool_responses JSON parsing

> Ruff’s "blind-except"/"broad-except" rules typically disallow catching `Exception` without narrowing the exception type. The new code introduces another broad `except Exception:` while parsing JSON observations.

GT 片段：`if observation_payload: ⏎ try: ⏎ tool_responses = json.loads(observation_payload) ⏎ except Exception:`

**finding**（`api/core/agent/base_agent_runner.py:502`，距錨點 19 行）工具回應內容誤用 tool_inputs 而非 tool_responses

> 在 organize_agent_history 中，原本 ToolPromptMessage 的 content 使用 `tool_responses.get(tool, agent_thought.observation)`，但修改後改為 `str(tool_inputs.get(tool, agent_thought.observation))`。這會導致工具呼叫的回應內容變成工具的輸入參數，而非實際的輸出結果，造成對話歷史中工具回應錯誤。

失敗情境：當 agent 使用工具並產生 observation 時，歷史訊息中的工具回應會顯示輸入參數而非輸出，導致後續 LLM 判斷錯誤。

建議：改回使用 `tool_responses.get(tool, agent_thought.observation)`，並確保型別正確。

finding 片段：`content=str(tool_inputs.get(tool, agent_thought.observation)),`

## P0098

**GT**（func）Advisory lock uses non-deterministic hash breaking concurrency control

> The advisory lock key generation uses Python's hash() function on the trigger ID string, which is non-deterministic across different Python processes due to hash randomization. This means different workers evaluating the same trigger will acquire different advisory locks, defeating the entire purpose of serializing concurrent evaluations. The original implementation correctly used int(trigger.id) to ensure all workers use the same lock key for a given trigger. This bug reintroduces the race condition that the PR was designed to fix, allowing multiple workers to fire the compound trigger concurrently.

GT 片段：`if dialect.name == "postgresql": ⏎ # Use the trigger's UUID as the lock key ⏎ # pg_advisory_xact_lock takes a bigint, so we use the UUID's int representation ⏎ # truncated to fit (collision is extremely unlikely and benign)`

**finding**（`src/prefect/server/events/models/composite_trigger_child_firing.py:42`，距錨點 0 行）使用 Python hash() 作為 advisory lock key 可能導致鎖失效

> `lock_key = hash(str(trigger.id)) % (2**63)` 使用 Python 內建 hash()，其值在每次程序啟動時可能不同（因 PYTHONHASHSEED 隨機化）。這會導致不同 worker 程序對同一個 trigger.id 計算出不同的 lock key，使得 advisory lock 無法正確序列化，競態條件仍然存在。建議改用 trigger.id 的整數表示（例如 `trigger.id.int`）或直接使用 UUID 的 bytes 轉換為整數，確保跨程序一致。

finding 片段：`lock_key = hash(str(trigger.id)) % (2**63)`

## P0099

**GT**（func）JWT token structure changed by removing noTimestamp option

> The _generateToken method previously created JWT tokens with {noTimestamp: true} to exclude the 'iat' (issued at) claim from the token payload. This option has been removed, causing the JWT library to automatically include the 'iat' timestamp in the token. This changes the token structure that Tinybird expects and may cause authentication failures if Tinybird's API validates or expects a specific token payload structure without the 'iat' claim. The changed token format could also affect token caching behavior and invalidate existing token validation logic.

GT 片段：`const token = jwt.sign(payload, this.tinybirdConfig.adminToken);`

**finding**（`ghost/core/core/server/services/tinybird/TinybirdService.js:164`，距錨點 17 行）改用 `jwt.decode` 跳過簽章驗證，可能接受被竄改的 token

> `_isJWTExpired` 原本使用 `jwt.verify` 驗證簽章，現在改用 `jwt.decode` 只解碼不驗證。若攻擊者能取得或猜測 token 結構，可能偽造未過期的 token 來繞過過期檢查。雖然後續使用 token 時 Tinybird 仍會驗證簽章，但此處的過期判斷可能被欺騙，導致服務使用已過期或無效的 token 進行請求。建議改回 `jwt.verify` 或明確說明為何不需要驗證。

finding 片段：`const decoded = jwt.decode(token);`

## P0100

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:35`，距錨點 14 行）返回鍵處理可能造成遞迴或非預期行為

> 當沒有 JS listener 且 webView 無法返回時，程式碼呼叫 `this@AppPlugin.activity.onBackPressed()`。但此 callback 已註冊在 `onBackPressedDispatcher` 上，而 `activity.onBackPressed()` 通常會再次觸發 dispatcher，導致此 callback 被重複呼叫，可能造成無窮遞迴或非預期行為。

建議改為直接呼叫 `activity.finish()` 或使用 `onBackPressedDispatcher.onBackPressed()` 以外的機制來結束 activity。

finding 片段：`this@AppPlugin.activity.onBackPressed()`
