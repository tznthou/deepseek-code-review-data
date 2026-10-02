# 盲標單 4：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-26-rules-loop/blind/labels-part4.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0340

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email.trim() 可能改變原本的驗證行為

> 在提交時對 email 進行 trim 是合理的，但需確認驗證邏輯（isValidEmail）是否也應該使用 trim 後的值，否則可能出現前後不一致。例如使用者輸入前後有空白的 email，驗證可能通過但提交的是 trim 後的值，或反之。

finding 片段：`onSubmit({email: email.trim()});`

## P0341

**GT**（rule）New public struct and function lack rustdoc comments

> `Dirs` and `resolve_dirs` are newly introduced public API items but have no `///` documentation comments as required.

GT 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

**finding**（`crates/tauri-cli/src/helpers/app_paths.rs:26`，距錨點 0 行）Dirs 結構體持有 &'static Path 可能造成懸垂指標

> `Dirs` 結構體中的 `tauri` 和 `frontend` 欄位型別為 `&'static Path`，但實際值是從 `OnceLock<PathBuf>` 中取得的參考。雖然目前 `OnceLock` 只會被初始化一次，但若未來程式碼在 `resolve_dirs()` 之後再次呼叫 `TAURI_DIR.set(...)` 或 `FRONTEND_DIR.set(...)`（例如在測試或重設邏輯中），舊的 `Dirs` 實例將持有指向已釋放記憶體的懸垂指標。建議改為持有 `PathBuf` 或使用 `Arc<Path>` 來確保生命週期安全。

finding 片段：`pub struct Dirs { ⏎ pub tauri: &'static Path, ⏎ pub frontend: &'static Path, ⏎ }`

## P0342

**GT**（func）Test-to-implementation mismatch: integration test helper uses Math.round while implementation uses Math.floor

> The integration test file defines a helper function `getExpectedLimit` that uses `Math.round` to calculate expected warmup limits, but the actual implementation uses `Math.floor`. This mismatch will cause test failures because the test expects different values than what the implementation produces. For example, on day 1, the formula produces 237.6, which Math.floor rounds to 237 but Math.round rounds to 238. This inconsistency means tests will fail even though the implementation logic might be correct, blocking the PR from merging successfully.

GT 片段：`const getExpectedLimit = (day) => { ⏎ const start = 200; ⏎ const end = 200000; ⏎ const totalDays = 42;`

**finding**（`ghost/core/test/integration/services/email-service/domain-warming.test.js:302`，距錨點 0 行）測試使用 Math.round 與實作 Math.floor 不一致

> 測試中的 `getExpectedLimit` 使用 `Math.round`，但實作使用 `Math.floor`。這可能導致在某些天數下測試期望值與實作結果不同，造成測試脆弱。建議測試與實作使用相同的捨入方式。

finding 片段：`return Math.round(start * Math.pow(end / start, day / (totalDays - 1)));`

## P0343

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 輸出日誌，應改用 logging

> 在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0344

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291`，距錨點 0 行）自訂錯誤型別未使用 thiserror

> 新增的 `FileWriteError` 手動實作 `Display` 和 `Error`，但專案規範 要求使用 `thiserror`。建議改用 `#[derive(thiserror::Error)]` 來簡化程式碼並保持一致。

finding 片段：`impl std::fmt::Display for FileWriteError { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ match self { ⏎ FileWriteError::Write(e) => write!(f, "Failed to write file: {}", e),`

## P0345

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:102`，距錨點 0 行）移除 source 參數傳遞可能影響現有功能

> 原本有將 `options.source` 加入 tinybirdOptions 的邏輯（允許空字串代表 Direct traffic），但此 PR 移除了該區塊。若前端仍會傳送 `source` 參數，則後端將不再將其傳遞給 Tinybird，可能導致 source 過濾失效。請確認是否有其他地方處理 source，或是有意移除。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## P0346

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291`，距錨點 3 行）自訂錯誤型別未使用 thiserror

> 新增的 FileWriteError 型別手動實作了 Display 和 Error trait，但專案規範   要求使用 thiserror 來定義錯誤型別。建議改用 `#[derive(thiserror::Error)]` 並使用 `#[error(...)]` 屬性來簡化程式碼並符合規範。

finding 片段：`impl std::fmt::Display for FileWriteError { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ match self { ⏎ FileWriteError::Write(e) => write!(f, "Failed to write file: {}", e),`

## P0347

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行）使用 propertyName 取代 metadata.Name 可能導致參數名稱不一致

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如使用別名或序列化名稱），可能找不到對應的參數。建議確認兩者是否永遠相同，或保留原本的比對方式。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0348

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 3 行）狀態欄位名稱依 posture 切換可能導致資料遺失

> 當 posture 從 Reactive 切換到 Proactive 時，欄位名稱從 `trigger.expect` 改為 `trigger.after`，但原本在 `trigger.expect` 中的值不會自動轉移到 `trigger.after`，可能導致使用者已選擇的狀態遺失。建議在切換時同步值或使用相同欄位名稱。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0349

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 19 行）Popover 在桌面端 hover 時可能閃爍或無法點擊內容

> 在桌面端，Popover 的開啟與關閉依賴於觸發按鈕和 PopoverContent 的 onMouseEnter/onMouseLeave。當滑鼠從觸發按鈕移向 PopoverContent 時，若兩者之間有間隙，會觸發 mouseleave 關閉 Popover，造成閃爍；且 PopoverContent 的 onMouseEnter 可能因關閉而無法觸發，導致內容無法點擊。建議改用 Radix Popover 的 hover 模式或加入延遲關閉機制。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0350

**GT**（rule）Unused import: Skeleton

> `Skeleton` is imported but never used in this file, which violates the rule requiring unused imports to be removed.

GT 片段：`import { Skeleton } from "@/components/ui/skeleton";`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14`，距錨點 8 行）Suspense 缺少 fallback，可能導致空白畫面

> 元件使用 `useSuspenseQuery` 取得資料，但外層的 `<Suspense>` 沒有提供 `fallback` prop。當查詢處於 pending 狀態時，React 會暫停渲染並尋找最近的 Suspense boundary；如果沒有 fallback，使用者會看到空白內容，直到資料載入完成。建議提供一個載入中的 UI，例如 `<Suspense fallback={<Skeleton />}>`，以改善使用者體驗。

finding 片段：`<Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} /> ⏎ </Suspense>`

## P0351

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能允許無效的 schedule 結構

> 此函式僅驗證 name 為非空字串，未驗證 schedule 欄位的結構（例如是否為陣列、元素是否為 { start, end } 物件）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 Zod schema 進行完整驗證，或至少檢查 schedule 的型別與元素結構。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0352

**GT**（func）Incorrect falsy value handling for run_count displays wrong value for zero

> The run_count display uses the logical OR operator (||) instead of the nullish coalescing operator (??). This causes a bug when run_count is explicitly 0 (a valid value indicating the task has not been retried). When run_count is 0, the || operator treats it as falsy and displays the fallback value '0' instead of the actual value 0 from the API. While the visual output is the same, this semantic error means the code doesn't distinguish between 'no data' (null/undefined) and 'zero retries' (0), which could cause issues if the UI behavior needs to differentiate these states in the future or if the fallback value changes.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Run Count</dt> ⏎ <dd className="">{taskRun.run_count || 0}</dd> ⏎ </dl>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:88`，距錨點 0 行）使用 `||` 處理數字 0 會錯誤顯示 'None'

> 在顯示 `run_count` 時使用 `taskRun.run_count || 0`，若 `run_count` 為 0（合法值），則會顯示 0，但若 `run_count` 為 null 或 undefined，也會顯示 0，可能無法區分。建議使用 `??` 運算子：`taskRun.run_count ?? 0`。

finding 片段：`<dd className="">{taskRun.run_count || 0}</dd>`

## P0353

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291`，距錨點 18 行）自訂錯誤型別未使用 thiserror

> 新增的 FileWriteError 型別手動實作了 Display 和 Error trait，但專案規範   要求使用 thiserror 來定義錯誤型別。建議改用 `#[derive(thiserror::Error)]` 並使用 `#[error(...)]` 屬性來簡化程式碼並符合規範。

finding 片段：`impl std::fmt::Display for FileWriteError { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ match self { ⏎ FileWriteError::Write(e) => write!(f, "Failed to write file: {}", e),`

## P0354

**GT**（func）Incorrect section index after inactive tabs removal

> The scrollToTab method hardcodes section index as 1, which was correct when there were two sections (inactive tabs at section 0 and regular tabs at section 1). After removing inactive tabs, there is only one section (section 0), so this will cause scroll operations to fail or crash when trying to access a non-existent section. This affects all scroll-to-tab functionality including selecting tabs, undoing tab closures, and panel switching. The TabDisplayDiffableDataSource now only creates a single section `.tabs`, but this scroll method wasn't updated accordingly.

GT 片段：`private func scrollToTab(_ scrollState: TabsPanelState.ScrollState) { ⏎ let indexPath = IndexPath(row: scrollState.toIndex, section: 1) ⏎ // Piping this into main thread let the collection view finish its layout process ⏎ DispatchQueue.main.async {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172`，距錨點 0 行）滾動目標 section 固定為 1，但現在只有一個 section

> 在 `scrollToTab` 中，原本根據 `scrollState.isInactiveTabSection` 決定 section 為 0 或 1，現在直接寫死為 1。但移除 inactive tabs 後，collection view 只有一個 section（index 0），因此 `IndexPath(row:section:1)` 會指向不存在的 section，導致滾動功能失效。

建議將 section 改為 0。

finding 片段：`let indexPath = IndexPath(row: scrollState.toIndex, section: 1)`

## P0355

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：argv[2] 使用 createStringObjectFromLongLong 建立後未釋放

> 在 hincrbyfloatCommand 中，當 has_expiration 為真時，程式碼建立 argv[2] = createStringObjectFromLongLong(expireat)，但之後沒有對其呼叫 decrRefCount。這會導致每次執行此路徑時洩漏一個 robj。

失敗情境：任何對具有過期時間的 hash 欄位執行 HINCRBYFLOAT 的請求，都會造成記憶體洩漏，長期下來可能耗盡記憶體。

建議修法：在 alsoPropagate 呼叫之後，加入 decrRefCount(argv[2]); 釋放該物件。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0356

**GT**（rule）TypeScript strict mode is disabled

> The rule requires TypeScript strict mode to be enabled in the compiler configuration, but it was disabled in tsconfig.app.json

GT 片段：`"noEmit": true, ⏎ "jsx": "react-jsx", ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`ui-v2/tsconfig.app.json:19`，距錨點 0 行）關閉 TypeScript 嚴格模式

> 將 `strict` 從 `true` 改為 `false` 違反了專案規範  ，會降低型別安全，可能隱藏潛在的型別錯誤。建議恢復為 `true`，並修正因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0357

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行）使用 propertyName 取代 metadata.Name 可能影響參數比對

> 原本 `p.Name == metadata.Name` 改為 `p.Name == propertyName`。若 `metadata.Name` 與 `propertyName` 可能不同（例如 metadata 名稱經過轉換），此變更可能導致找不到對應的 operation parameter，進而將描述套用到 RequestBody 而非參數。建議確認兩者在此情境下是否恆等。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0358

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 回傳型別可能包含 undefined

> 原本的程式碼在 history 為 falsy 時會繼續執行後續邏輯，但現在直接回傳 history。若 getDefaultUrlHistory() 回傳 undefined，則此函式可能回傳 undefined，與宣告的回傳型別 URLHistory 不符。請確認呼叫端是否能處理 undefined，或調整型別定義。

finding 片段：`return history;`

## P0359

**GT**（rule）New public config functions lack rustdoc comments

> The newly introduced public functions `get_config`, `reload_config`, and `merge_config_with` have no `///` documentation comments, violating the requirement that public APIs be documented.

GT 片段：`pub fn get_config( ⏎ target: Target, ⏎ merge_configs: &[&serde_json::Value], ⏎ tauri_dir: &Path,`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 18 行）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## P0360

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:82`，距錨點 10 行）PopoverContent 的 onMouseEnter/onMouseLeave 可能導致 popover 意外關閉

> PopoverContent 上設置了 onMouseEnter={handleMouseEnter} 和 onMouseLeave={handleMouseLeave}。當滑鼠從觸發按鈕移動到 popover 內容時，會先觸發按鈕的 mouseleave（關閉 popover），然後才觸發內容的 mouseenter（重新開啟），可能造成閃爍。此外，若 popover 內容與按鈕之間有間隙，mouseleave 可能導致 popover 關閉而無法進入內容。建議使用 Popover 內建的 hover 模式或增加延遲關閉。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0361

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：createStringObjectFromLongLong 建立的物件未釋放

> 在傳播 HPEXPIREAT 時，`argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 `alsoPropagate` 之後沒有對其進行 `decrRefCount`。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。

建議在 `alsoPropagate` 呼叫後加入 `decrRefCount(argv[2]);` 或使用 stack 分配的 robj 並設定 refcount。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0362

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯變更可能不符合繁體中文習慣

> 將「新聞信」改為「邮件通讯」等用語，可能不符合繁體中文使用者的習慣。建議確認目標受眾，若為繁體中文使用者，應保留原有用語。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。"`

## P0363

**GT**（func）Incorrect requestReschedule flag for seat cancellation webhooks

> The cancelAttendeeSeat function incorrectly sets requestReschedule to true when cancelling individual attendee seats, even though this is not a reschedule request. This flag should be false for regular seat cancellations and only true for actual reschedule requests. External webhook consumers receiving BOOKING_CANCELLED events will incorrectly interpret seat cancellations as reschedule requests, potentially triggering wrong automated workflows, email templates, or business logic in integrated systems.

GT 片段：`const payload: EventPayloadType = { ⏎ ...evt, ⏎ ...eventTypeInfo, ⏎ status: "CANCELLED",`

**finding**（`packages/features/bookings/lib/handleSeats/cancel/cancelAttendeeSeat.ts:167`，距錨點 0 行）requestReschedule 硬編碼為 true

> 在取消座位（cancelAttendeeSeat）流程中，`requestReschedule` 被硬編碼為 `true`。這可能不正確，因為取消座位不一定代表要求重新排程。建議確認此處的業務邏輯，若取消座位僅是取消單一與會者，應設為 `false`。

finding 片段：`requestReschedule: true,`

## P0364

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）不必要的 print 陳述式

> 新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會將內部執行狀態輸出到 stdout，可能造成日誌污染或效能影響。建議移除或改用正式的 logging 機制。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0365

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 0 行）Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證

> 當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0366

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:117`，距錨點 27 行）權限範圍變更可能導致資料外洩或遺漏

> 原本的實作僅允許 ADMIN/OWNER 角色查看團隊成員的 bookings，現在改為使用 `PermissionCheckService.getTeamIdsWithPermission` 取得具有 `booking.read` 權限的團隊。這可能擴大或縮小可存取的範圍，取決於 PBAC 權限的設定。若某些團隊的 PBAC 權限設定不正確，可能導致使用者看到不應看到的 bookings，或看不到應有的 bookings。

建議確認此變更符合預期的權限模型，並進行充分的測試。

finding 片段：`const teamIdsWithBookingPermission = await permissionCheckService.getTeamIdsWithPermission({ ⏎ userId: user.id, ⏎ permission: "booking.read", ⏎ fallbackRoles,`

## P0367

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）及 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式的資料，可能導致後續 API 呼叫失敗或產生難以除錯的錯誤。建議使用 Zod 或更完整的型別檢查來驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0368

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴順序與後端不一致

> 前端 `getStatEndpointUrl` 將 `config.version` 放在 endpointName 之前（`${config.version}_${endpointName}`），但後端 `tinybird.js` 是放在之後（`${pipeName}_${version}`）。例如 version='v2'、endpointName='api_kpis' 時，前端會呼叫 `v2_api_kpis`，後端會呼叫 `api_kpis_v2`，導致 404。請統一為後端的 `api_kpis_v2` 格式。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0369

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行）start_execution 與 enqueue_node 的呼叫順序可能導致狀態不一致

> 在 has_taken 分支中，先呼叫 `start_execution(downstream_node_id)` 再呼叫 `enqueue_node(downstream_node_id)`。若 start_execution 會將節點狀態改為執行中，而 enqueue_node 預期節點尚未開始執行，可能造成狀態機內部不一致。需確認 GraphStateManager 的實作是否允許此順序，或應先 enqueue 再 start。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0370

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致可能導致下游誤判

> 在 BookingPayloadBuilder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true` 作為預設值，但在 BookingWebhookFactory 中則使用 `params.requestReschedule ?? false`。這兩個地方對同一欄位的預設值不同，可能導致不同路徑產生的 webhook payload 不一致，進而影響下游系統的判斷。建議統一預設值，並明確其語意。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0371

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 20 行）使用 print 輸出日誌，應改用 logging

> 在 propagate_skip_from_edge 中新增的 `print(f"Starting execution for node: {downstream_node_id}")` 會直接輸出到 stdout，可能污染正式環境的日誌，且無法透過 logging 設定控制輸出等級或格式。建議改用 `logging.getLogger(__name__).debug(...)` 或移除。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0372

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行）查詢函式名稱拼寫錯誤：buildFLowDetailsQuery

> 匯入的查詢建構函式名稱為 `buildFLowDetailsQuery`，其中 `FLow` 的大小寫可能不符合命名慣例（應為 `buildFlowDetailsQuery`）。這可能導致可讀性問題，且若其他程式碼使用正確拼寫，會造成不一致。建議確認函式名稱並修正。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## P0373

**GT**（rule）Nested struct added without explicit access control modifier

> The newly added nested type `v147` is declared as `struct v147` without an explicit access control modifier (e.g., `public`/`internal`/`private`). Rule 11 requires explicit access control on declarations based on intended scope. Many other nested structs in this file use `public struct ...`, so this is an inconsistency and a clear violation in the added code.

GT 片段：`struct v147 { ⏎ public static let TabsTrayInactiveTabsSectionClosedAccessibilityTitle = MZLocalizedString( ⏎ key: "TabsTray.InactiveTabs.SectionTitle.Closed.Accessibility.v103", ⏎ tableName: nil,`

**finding**（`firefox-ios/Shared/Strings.swift:8461`，距錨點 0 行）新增的 v147 結構體可能造成重複定義

> 在 `String.TabsTray` 中新增了 `struct v147`，其中包含與先前刪除的 `InactiveTabs` 結構體相同的靜態屬性。若專案中其他地方已存在 `v147` 結構體，或未來版本更新時可能衝突。建議確認此結構體名稱的唯一性，或考慮使用更明確的名稱。

finding 片段：`struct v147 {`

## P0374

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）max_length 為 undefined 時長度驗證失效

> 當 `varItem.max_length` 未定義時，`item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果永遠為 false，導致長度驗證被跳過。

建議改為：
```ts
if (varItem.max_length && item[varIndex].length > varItem.max_length) {
```
或使用 `Number.isFinite(varItem.max_length)` 進行檢查。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0375

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 24 行）write_and_make_executable 先設定權限再寫入檔案

> 函式 `write_and_make_executable` 先呼叫 `fs::set_permissions` 設定權限，再呼叫 `fs::write` 寫入檔案。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致無法建立檔案。應先寫入檔案再設定權限，或使用 `OpenOptions` 建立檔案後設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0376

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足，可能允許無效的 schedule 結構

> 此函式僅驗證 name 為非空字串，未驗證 schedule 欄位的結構（例如是否為陣列、元素是否為 { start, end } 物件）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 Zod schema 進行完整驗證，或至少檢查 schedule 的型別與元素結構。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0377

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行）命名空間宣告未使用 file-scoped 語法

> 此檔案將原本的 file-scoped namespace 改為 block-scoped namespace，違反 repo 規範  （Use File-Scoped Namespace Declarations）。

建議改回 file-scoped namespace 宣告，例如：
```csharp
namespace Microsoft.AspNetCore.Components.Server.Circuits;
```

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ {`

## P0378

**GT**（func）Incorrect field switching in DeploymentStatusTriggerFields breaks trigger data model

> The DeploymentStatusTriggerFields component incorrectly implements posture-dependent field switching, using 'trigger.after' for Proactive posture and 'trigger.expect' for Reactive posture. While this pattern exists in FlowRunStateTriggerFields where it serves a semantic purpose (states to enter vs. stay in), deployment status triggers don't have this distinction in the backend data model. This causes the selected status to be written to the wrong field when Proactive posture is selected, potentially causing data loss when the form is saved or incorrect trigger behavior. The backend may not recognize 'after' field for deployment status events.

GT 片段：`// Determine which field to use based on posture ⏎ const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect"; ⏎ // ...`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 0 行）Posture 變更時可能殘留舊欄位值

> 在 `deployment-status-trigger-fields.tsx` 中，當 posture 從 Reactive 切換到 Proactive 時，欄位名稱從 `trigger.expect` 改為 `trigger.after`，但舊的 `trigger.expect` 值可能仍保留在表單狀態中。這可能導致提交時包含不必要的資料。建議在 posture 變更時清除對應欄位。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0379

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）日期計算可能因時區或 DST 造成 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的 timestamp 差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或跨越 DST 轉換，可能導致天數計算多一天或少一天，進而影響暖機限制。建議改用 UTC 日曆日差（例如將兩個日期轉為 UTC 日期字串後相減），或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0380

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致可能導致下游誤判

> 在 `BookingPayloadBuilder.ts` 中，`requestReschedule` 使用 `dto.requestReschedule ?? true`，但其他建構器（如 `BookingWebhookFactory.ts`）使用 `?? false`。若呼叫端未明確提供此欄位，不同版本或路徑的 webhook payload 會得到不同的預設值，可能導致下游系統誤判取消類型。建議統一預設值，或明確在 DTO 中要求此欄位。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0381

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）當 max_length 未定義時，長度檢查失效

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在改為直接使用 `varItem.max_length`。如果 `varItem.max_length` 是 `undefined`，則 `item[varIndex].length > undefined` 會是 `false`（因為 `undefined` 會被轉成 `NaN`，任何比較都為 false），導致長度檢查永遠不會觸發，可能允許超長輸入。建議保留預設值，或明確處理 `max_length` 未定義的情況（例如視為無限制）。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0382

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:72`，距錨點 20 行）鍵盤使用者無法操作 Popover

> Popover 的開啟僅依賴滑鼠 hover，鍵盤使用者無法聚焦觸發按鈕來開啟 Popover，且 PopoverContent 內的項目為 span 而非可聚焦元素，無法用鍵盤選取。建議改用 Button 或加入 tabIndex 與鍵盤事件處理。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0383

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:29`，距錨點 9 行）tearDown 中呼叫 @MainActor 方法但類別未標記 @MainActor

> `tearDown` 中呼叫 `AppContainer.shared.reset()`，該方法可能也是 @MainActor，但類別未標記 @MainActor，可能導致編譯錯誤。

finding 片段：`AppContainer.shared.reset()`

## P0384

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）日期計算可能因時區或時鐘偏移產生 off-by-one 錯誤

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並無條件進位。若伺服器時區與 UTC 有偏移，或系統時鐘在兩次呼叫間被調整，可能導致天數計算錯誤。例如，若首次 email 建立於 UTC 23:59，而目前時間為 UTC 00:01（相差 2 分鐘），計算結果為 1 天，但實際上可能尚未滿 24 小時。建議改用日曆日期（如 `created_at` 的日期部分與今天的日期差）來計算天數，或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0385

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）out 參數初始化位置調整可能影響可讀性

> 將 `validatableTypeInfo = null;` 移至方法開頭，雖然功能上無差異，但可能降低可讀性，因為初始化與後續邏輯分離。若無特殊原因，建議保留在迴圈後。

finding 片段：`validatableTypeInfo = null;`

## P0386

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:14`，距錨點 0 行）Suspense 缺少 fallback，可能導致空白畫面

> 元件使用 `useSuspenseQuery` 取得資料，但外層的 `<Suspense>` 沒有提供 `fallback` prop。當查詢處於 pending 狀態時，React 會暫停渲染並尋找最近的 Suspense boundary；如果沒有 fallback，使用者會看到空白內容，直到資料載入完成。建議提供一個載入中的 UI，例如 `<Suspense fallback={<Skeleton />}>`，以改善使用者體驗。

finding 片段：`<Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} /> ⏎ </Suspense>`

## P0387

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）測試步驟順序調整可能影響穩定性

> 原本先執行 `navigator.goto(NewTabScreen)` 再點擊 "Done" 按鈕，修改後順序對調。若 "Done" 按鈕的點擊會觸發畫面跳轉，先點擊可能導致後續 `navigator.goto(NewTabScreen)` 失敗或行為不符預期。建議確認此順序調整是否為修正既有問題，並確保測試仍能穩定通過。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0388

**GT**（rule）Traditional namespace declaration with braces

> The rule requires C# files to use file-scoped namespace declarations (ending with semicolon without braces), but this file uses traditional namespace declarations with opening and closing braces.

GT 片段：`using Microsoft.AspNetCore.Components.Endpoints; ⏎ using Microsoft.AspNetCore.DataProtection; ⏎ using Microsoft.Extensions.Logging.Abstractions; ⏎ namespace Microsoft.AspNetCore.Components.Server.Circuits`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:10`，距錨點 0 行）使用 block-scoped namespace 而非 file-scoped namespace

> 此檔案將原本的 file-scoped namespace 宣告改為 block-scoped namespace，違反了專案規範  （Use File-Scoped Namespace Declarations）。

**建議修法**：改回 file-scoped namespace 宣告，例如：
```csharp
namespace Microsoft.AspNetCore.Components.Server.Circuits;
```
並移除多餘的括號。

finding 片段：`namespace Microsoft.AspNetCore.Components.Server.Circuits ⏎ { ⏎ public class ServerComponentDeserializerTest ⏎ {`

## P0389

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行）「Name」翻譯從「名字」改為「名稱」可能造成不一致

> 在 portal.json 中，`"Name"` 的翻譯從 `"名字"` 改為 `"名稱"`。但在同檔案的 `"Jamie Larson": "阿宇"` 和 `"jamie@example.com": "ayu@example.com"` 等範例中，可能仍使用「名字」的語境。此外，ghost.json 中 `"Name"` 的翻譯也改為 `"名字"`，可能造成不一致。請確認此變更是否為預期。

finding 片段：`"Name": "名称",`

## P0390

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0391

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）日期計算可能因時區或時鐘偏移產生 off-by-one 錯誤

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的毫秒差除以 86400000 並無條件進位。若伺服器時區與 UTC 有偏移，或系統時鐘在兩次呼叫間被調整，可能導致天數計算錯誤。例如，若首次 email 建立於 UTC 23:59，而目前時間為 UTC 00:01（相差 2 分鐘），計算結果為 1 天，但實際上可能尚未滿 24 小時。建議改用日曆日期（如 `created_at` 的日期部分與今天的日期差）來計算天數，或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0392

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試使用錯誤的泛型型別參數

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，參數使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為實際元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。

建議將斷言中的 `GenericComponent<string>` 改為 `GenericComponent<int>`，以符合實際使用的型別。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0393

**GT**（func）Incorrect type conversion in generic component parameter assertion

> The test validates a generic component with an int type parameter but uses Convert.ToInt64 instead of Convert.ToInt32 to assert the parameter value. Since the parameter is defined as int (System.Int32) in GenericTestComponent<int>, this creates a type mismatch. The assertion compares a long (Int64) value to the expected int (Int32) value 42, which will cause the test to fail even though the component deserialization is working correctly. This breaks the validation logic for generic component parameters.

GT 片段：`var parameters = deserializedDescriptor.Parameters.ToDictionary(); ⏎ Assert.Single(parameters); ⏎ Assert.Contains("Value", parameters.Keys); ⏎ Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 0 行）使用 Convert.ToInt64 可能隱藏型別資訊

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64` 將參數值轉換為 long，但未驗證參數值的原始型別。這可能導致測試無法偵測到反序列化過程中型別資訊的遺失或錯誤。建議先斷言參數值的型別（例如 `Assert.IsType<JsonElement>(parameters["Value"])`），再進行數值比較。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0394

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）權限設定在寫入前執行，導致檔案權限錯誤

> 在 `write_and_make_executable` 函式中，先呼叫 `fs::set_permissions` 再呼叫 `fs::write`。若檔案不存在，`set_permissions` 會失敗；若檔案已存在，`write` 會覆蓋內容但保留先前設定的權限，可能導致權限不符合預期。應先寫入檔案再設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0395

**GT**（func）Flow run link displays empty or undefined text when flow_run_name is missing

> The condition for displaying the flow run link was changed from checking both flow_run_id AND flow_run_name to only checking flow_run_id. When a task run has a flow_run_id but flow_run_name is null or undefined (which is valid according to the UITaskRun schema where flow_run_name is 'string | null | undefined'), the link will render with empty text or display 'undefined'. This creates a broken user experience where users see a clickable link with no visible text. The original code correctly ensured both values existed before showing the link.

GT 片段：`{taskRun.flow_run_id ? ( ⏎ <dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Flow Run</dt> ⏎ <dd>`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:45`，距錨點 0 行）flow_run_id 存在但 flow_run_name 為空時渲染空連結

> 原本的條件是 `taskRun.flow_run_name && taskRun.flow_run_id`，現在改成只檢查 `taskRun.flow_run_id`。如果 `flow_run_id` 有值但 `flow_run_name` 為 null/undefined，會進入第一個分支，但 `<Link>` 內顯示的 `taskRun.flow_run_name` 會是空的，導致使用者看到一個沒有文字的連結。建議改回同時檢查兩者，或是在名稱缺失時顯示 fallback 文字。

finding 片段：`{taskRun.flow_run_id ? (`

## P0396

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0397

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）Schedule 型別缺少部分原始欄位，可能導致型別不相容

> 新定義的 `Schedule` 型別僅包含 `id`、`userId`、`name`、`timeZone`，但原始 `@calcom/trpc` 中的 Schedule 型別可能包含更多欄位（如 `availability`、`isDefault` 等）。若其他程式碼依賴這些欄位，型別檢查會失敗或執行時期出現 undefined。建議完整複製原始型別定義，或使用 `Pick`/`Omit` 明確選擇所需欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0398

**GT**（func）Empty suffix array incorrectly bypasses generic calendar filtering

> The filtering logic adds a length check (genericCalendarSuffixes?.length) that treats an empty array as falsy, setting AND to undefined instead of an empty array. In Prisma, AND: undefined means no filtering, while AND: [] also means no filtering but with different semantics. More critically, this breaks the filtering for providers like office365_calendar that have an empty suffix list in GENERIC_CALENDAR_SUFFIXES. The double optional chaining (?. used twice) is redundant and the length check changes the behavior from the intended design where empty arrays should still be processed.

GT 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

**finding**（`packages/features/selectedCalendar/repositories/SelectedCalendarRepository.ts:41`，距錨點 0 行）AND 條件設為 undefined 可能導致 Prisma 查詢問題

> 當 genericCalendarSuffixes 為空或未提供時，AND 被設為 undefined。Prisma 通常會忽略 undefined 的條件，但某些版本或嚴格模式下可能拋出型別錯誤。建議改用條件展開（例如 ...(genericCalendarSuffixes?.length ? { AND: [...] } : {})）以避免傳入 undefined。

finding 片段：`AND: genericCalendarSuffixes?.length ⏎ ? genericCalendarSuffixes?.map((suffix) => ({ ⏎ NOT: { externalId: { endsWith: suffix } }, ⏎ }))`

## P0399

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）當 max_length 未定義時，長度檢查失效

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，現在改為直接使用 `varItem.max_length`。如果 `varItem.max_length` 是 `undefined`，則 `item[varIndex].length > undefined` 會是 `false`（因為 `undefined` 會被轉成 `NaN`，任何比較都為 false），導致長度檢查永遠不會觸發，可能允許超長輸入。建議保留預設值，或明確處理 `max_length` 未定義的情況（例如視為無限制）。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0400

**GT**（func）Generic calendar suffix filtering includes disabled providers

> The getGenericCalendarSuffixes() method uses Object.keys(GENERIC_CALENDAR_SUFFIXES) to iterate over all providers defined in the constant, including office365_calendar. However, getProviders() only returns ['google_calendar'], meaning Office365 is not actually enabled. This causes the subscription system to filter out Office365 calendar suffixes even when Office365 calendars shouldn't be processed at all. The filtering should only include suffixes for enabled providers by using this.getProviders() as in the original implementation.

GT 片段：`getGenericCalendarSuffixes(): string[] { ⏎ return Object.keys(GENERIC_CALENDAR_SUFFIXES).flatMap( ⏎ (provider) => GENERIC_CALENDAR_SUFFIXES[provider as CalendarSubscriptionProvider] ⏎ );`

**finding**（`packages/features/calendar-subscription/adapters/AdaptersFactory.ts:67`，距錨點 0 行）getGenericCalendarSuffixes 合併所有 provider 的後綴，可能導致跨 provider 錯誤過濾

> `getGenericCalendarSuffixes` 方法將所有 provider 的後綴合併成一個陣列，但呼叫端 `CalendarSubscriptionService` 在查詢時並未區分 provider，而是將所有後綴套用到所有 provider 的日曆上。這可能導致例如未來為 office365 定義後綴時，Google 日曆也被錯誤過濾。建議改為依 provider 分別取得後綴，或在查詢中依 provider 條件分開處理。

finding 片段：`getGenericCalendarSuffixes(): string[] { ⏎ return Object.keys(GENERIC_CALENDAR_SUFFIXES).flatMap( ⏎ (provider) => GENERIC_CALENDAR_SUFFIXES[provider as CalendarSubscriptionProvider] ⏎ );`

## P0401

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）測試中泛型型別參數不一致

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，使用 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來比對 Assembly 與 TypeName。這會導致斷言失敗，因為實際渲染的元件型別是 `GenericComponent<int>`，而非 `GenericComponent<string>`。建議將斷言中的型別改為 `GenericComponent<int>`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0402

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:249`，距錨點 0 行）硬編碼的 " (group)" 字串未使用 i18n

> 在合併 label 時，使用了硬編碼的 " (group)" 來表示群組選項。這可能導致在地化問題，因為其他文字都使用 t() 進行翻譯。建議使用翻譯鍵或至少使用更通用的符號。

finding 片段：`groupIndicator = " (group)";`

## P0403

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47`，距錨點 0 行）BackgroundQueueSize 驗證條件變更可能拒絕 0 值

> 原本的驗證條件為 `if (value < 0)`，允許 0 值。變更後為 `if (value <= 0)`，拒絕 0 值。但屬性文件說明為「maximum size of the background log message queue or null for no limit」，且錯誤訊息仍為「must be non-negative」，因此拒絕 0 可能違反設計意圖。若設定為 0，可能代表不允許任何佇列，但此處可能導致無法設定為 0。建議確認此變更是否為預期，若非預期應改回 `< 0`。

finding 片段：`if (value <= 0)`

## P0404

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行）翻譯用語可能不符合繁體中文習慣

> 將「名字」改為「名称」，但「名称」通常用於事物而非人。建議維持「名字」。

finding 片段：`"Name": "名称",`

## P0405

**GT**（func）Off-by-one error in field expiration comparison

> The expiration check uses strict greater-than (>) instead of greater-than-or-equal (>=) when comparing expiredAt with commandTimeSnapshot(). This causes fields that expire at exactly the current timestamp to be incorrectly treated as expired. In high-frequency operations, this can lead to premature field expiration and data loss, especially affecting the HINCRBYFLOAT operation's ability to preserve field TTL correctly.

GT 片段：`if (*expiredAt > (uint64_t) commandTimeSnapshot()) ⏎ return GETF_OK;`

**finding**（`src/t_hash.c:742`，距錨點 0 行）邊界條件變更：>= 改為 > 可能影響過期判斷

> 原本的判斷是 `if (expiredAt >= (uint64_t) commandTimeSnapshot())`，現在改為 `if (*expiredAt > (uint64_t) commandTimeSnapshot())`。這表示當 `expiredAt` 等於當前時間時，原本會被視為未過期，現在會被視為已過期。這可能導致在時間邊界上的行為差異，例如欄位剛好在同一毫秒過期時，原本可能回傳值，現在會回傳過期。需要確認此變更是否為預期行為，並考慮是否應保留 `>=` 以維持原有語意。

finding 片段：`if (*expiredAt > (uint64_t) commandTimeSnapshot()) ⏎ return GETF_OK;`

## P0406

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）使用 expect 可能導致 panic

> 在 write_and_make_executable 中，使用 fs::set_permissions 和 fs::write 並以 map_err 處理錯誤，但沒有使用 expect 或 unwrap。然而，函式簽名回傳 Result<(), FileWriteError>，但內部可能因為其他原因 panic？實際上沒有直接使用 expect，但建議確認所有可能的錯誤都被妥善處理。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0407

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1734`，距錨點 7 行）截斷後未更新 AOF 檔案大小或相關狀態，可能導致後續寫入錯誤

> 在成功截斷 AOF 檔案後，程式只將檔案描述子 seek 到結尾，但沒有更新 `server.aof_current_size` 或其他記錄 AOF 大小的變數。這可能導致後續 AOF 重寫或寫入時，Redis 認為檔案比實際大，進而產生錯誤或資料不一致。

**失敗情境**：截斷後，Redis 繼續寫入 AOF，但 `server.aof_current_size` 仍保留舊值，導致 AOF 重寫觸發條件判斷錯誤，或寫入位置偏移。

**建議**：截斷後應更新相關的 AOF 大小記錄，或至少確保後續寫入使用正確的檔案偏移。

finding 片段：`if (server.aof_fd != -1 && lseek(server.aof_fd,0,SEEK_END) == -1) { ⏎ serverLog(LL_WARNING,"Can't seek the end of the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0408

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能允許無效的 schedule 結構

> 此函式僅驗證 name 為非空字串，未驗證 schedule 欄位的結構（例如是否為陣列、元素是否為 { start, end } 物件）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 Zod schema 進行完整驗證，或至少檢查 schedule 的型別與元素結構。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0409

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行）快取寫入時可能將 None 序列化為 'null' 字串

> 即使修正了變數名稱，如果 `plans_to_cache` 中包含值為 `None` 的項目（例如 `get_plan_bulk` 回傳的字典中某個 tenant 的值為 `None`），`json.dumps(None)` 會產生字串 `'null'`。之後讀取快取時，`json.loads('null')` 會得到 `None`，然後 `validate_python(None)` 會拋出例外，導致該 tenant 被視為 cache miss，但實際上快取中已有無效資料。

**失敗情境**：`get_plan_bulk` 回傳 `{'tenant-1': None}`，`plans_to_cache` 包含 `tenant-1`，寫入快取的值為 `'null'`。下次讀取時，`json.loads` 得到 `None`，驗證失敗，進入 cache miss，重新呼叫 API，但 API 可能再次回傳 `None`，形成無效快取。

**建議修法**：在寫入快取前，過濾掉值為 `None` 的項目，或確保 `get_plan_bulk` 不會回傳 `None` 值。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0410

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0411

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1830`，距錨點 11 行）AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理

> 在 `loadAppendOnlyFiles` 中，若 `ret == AOF_BROKEN_RECOVERED` 且該檔案不是最後一個，程式會將 `ret` 改為 `AOF_FAILED` 並記錄錯誤，但之後的 `if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED)` 會再次進入 cleanup，可能導致重複處理。建議在設定 `ret = AOF_FAILED` 後直接跳轉到 cleanup，避免重複。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0412

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）使用 print 而非 logging

> 在 propagate_skip_from_edge 方法中新增了 print 陳述式，違反專案規範  （Backend Code Must Use Logging Instead of Print Statements）。print 會直接輸出到 stdout，無法被日誌系統收集，且可能造成效能問題。應改用 logging 模組，並在模組頂部宣告 logger。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0413

**GT**（rule）Missing MIT license header

> The rule requires that every C# source file must start with the exact two-line MIT license header comment: '// Licensed to the .NET Foundation under one or more agreements.' followed by '// The .NET Foundation licenses this file to you under the MIT license.' This file is missing the required license header at the start.

GT 片段：`using System.Collections.Generic; ⏎ using System.Collections.Immutable; ⏎ using System.IO; ⏎ using Microsoft.CodeAnalysis;`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:1`，距錨點 0 行）移除 MIT 授權標頭

> 檔案開頭的 MIT 授權標頭被移除，違反專案規範  。所有 C# 原始檔必須以標準的 .NET Foundation MIT 授權標頭開頭。請恢復授權標頭。

finding 片段：`using System.Collections.Generic;`

## P0414

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 型別轉換可能導致索引失效與全表掃描

> 在 SQL 查詢中使用 `${orgId}::bigint` 進行型別轉換，可能導致資料庫無法使用 Team.id 上的索引，造成全表掃描。當 orgId 為 null 時，條件 `(${orgId}::bigint IS NULL OR ...)` 會使整個條件恆真，但資料庫仍可能對 Team 表進行全表掃描。建議改為在應用程式層處理 null 情況，例如使用條件式查詢或將 orgId 作為參數傳遞，避免在 SQL 中進行型別轉換。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0415

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖身完成後回傳 Infinity 可能導致呼叫端未預期行為

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接使用此值進行數學運算或與其他數值比較，可能產生非預期結果。例如，若呼叫端將此值傳入 `Math.min` 或作為陣列索引，可能導致錯誤。建議回傳 `emailCount`（表示無限制）或定義明確的常數，並確認所有呼叫端都能正確處理。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0416

**GT**（rule）__str__ without complementary __repr__

> The SubscriptionPlan class overrides __str__ without implementing the complementary __repr__ method, violating the requirement that special methods should be properly implemented with their relevant complementary methods

GT 片段：`class SubscriptionPlan(TypedDict): ⏎ """Tenant subscriptionplan information.""" ⏎ plan: str ⏎ expiration_date: int`

**finding**（`api/services/billing_service.py:28`，距錨點 0 行）新增 __str__ 方法可能違反不必要的 dunder 覆寫規範

> 在 `SubscriptionPlan` TypedDict 中新增了 `__str__` 方法，用於除錯。但 TypedDict 通常不應定義方法，且此方法僅用於日誌輸出，可能違反專案規範  （避免不必要的 dunder 方法覆寫）。

**建議**：若僅為除錯，可考慮使用 `repr()` 或直接在日誌中格式化 dict，而不覆寫 `__str__`。

finding 片段：`def __str__(self) -> str: ⏎ """Return a human-readable string representation for debugging.""" ⏎ return f"Plan: {self['plan']}, Expiration: {self['expiration_date']}"`

## P0417

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:68`，距錨點 0 行）Popover 在桌面端僅依賴 mouseenter/mouseleave，缺乏鍵盤與觸控支援

> 在桌面端，Popover 的開啟與關閉僅由 Button 和 PopoverContent 上的 onMouseEnter/onMouseLeave 控制。這會導致：
1. 鍵盤使用者無法聚焦到觸發按鈕並開啟 popover（除非 PopoverTrigger 本身有處理，但此處未提供）。
2. 觸控裝置（如平板）沒有 hover 事件，使用者可能無法查看隱藏的 badges。
建議使用 Popover 的 trigger 屬性（如 click）或確保 Button 可聚焦並處理鍵盤事件，或提供明確的點擊切換。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0418

**GT**（func）Inconsistent Chinese translation for 'Name' field across namespaces

> The PR updates the Chinese translation for 'Name' from '称呼' to '姓名' across multiple translation files to ensure consistency. However, this change creates a cross-namespace inconsistency issue. In ghost.json, line 31 shows 'Name' translated as '名字' (first name), while in portal.json line 117 it's translated as '名称' (generic name/title). This inconsistency will confuse Chinese users when they see different terminology for the same 'Name' field between email templates (using ghost namespace) and the portal UI (using portal namespace). The correct translation should be '姓名' (full name) consistently across both files as intended by the original PR.

GT 片段：`"month": "月", ⏎ "Monthly": "月付", ⏎ "More like this": "更多类似内容", ⏎ "Name": "名称",`

**finding**（`ghost/i18n/locales/zh/portal.json:117`，距錨點 0 行）「Name」翻譯不一致

> 在 portal.json 中，「Name」被改為「名稱」，但在 ghost.json 中仍為「名字」。這可能導致不同頁面顯示不一致。建議統一。

finding 片段：`"Name": "名称",`

## P0419

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:82`，距錨點 9 行）PopoverContent 的 onMouseEnter/onMouseLeave 可能導致 popover 意外關閉

> PopoverContent 上設置了 onMouseEnter={handleMouseEnter} 和 onMouseLeave={handleMouseLeave}。當滑鼠從觸發按鈕移動到 popover 內容時，會先觸發按鈕的 mouseleave（關閉 popover），然後才觸發內容的 mouseenter（重新開啟），可能造成閃爍。此外，若 popover 內容與按鈕之間有間隙，mouseleave 可能導致 popover 關閉而無法進入內容。建議使用 Popover 內建的 hover 模式或增加延遲關閉。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0420

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1725`，距錨點 2 行）valid_up_to 為 -1 時仍可能嘗試截斷

> 在 `fmterr` 處理中，若 `valid_up_to == -1`，程式只記錄警告，但之後仍會繼續執行到 `ret = AOF_FAILED` 並跳至 cleanup，不會嘗試截斷。然而，若 `valid_up_to` 為 -1 但 `server.aof_load_broken` 為真，且 `sb.st_size - valid_up_to` 小於限制（實際上會是很大的正數），條件 `(size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size` 可能意外成立，導致對檔案進行截斷。建議在 `valid_up_to == -1` 時直接跳過截斷邏輯，或明確檢查 `valid_up_to >= 0`。

finding 片段：`if (valid_up_to == -1) { ⏎ serverLog(LL_WARNING,"Last valid command offset is invalid"); ⏎ } else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

## P0421

**GT**（func）Duplicate browserActionStack reference causing missing trailing page action animations

> The updateToolbarLayout method incorrectly references browserActionStack twice instead of including trailingPageActionStack in the stacks array. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. As a result, trailing page action buttons won't be included in the animation logic, causing them to not animate properly when the toolbar layout updates. Users will see trailing page actions appear/disappear abruptly without smooth alpha transitions while other toolbar elements animate correctly.

GT 片段：`let stacks = browserActionStack.arrangedSubviews + ⏎ navigationActionStack.arrangedSubviews + ⏎ leadingPageActionStack.arrangedSubviews + ⏎ browserActionStack.arrangedSubviews`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:332`，距錨點 0 行）updateActionStack 動畫陣列重複加入 browserActionStack，可能導致動畫異常

> 在 `updateActionStack` 方法中，原本的 stacks 陣列包含 `browserActionStack`、`navigationActionStack`、`leadingPageActionStack` 和 `pageActionStack`。此 PR 將最後一項改為 `browserActionStack`，導致 `browserActionStack` 被加入兩次。這可能使動畫過程中的視圖操作重複執行，造成不必要的效能開銷或視覺異常。

**失敗情境**：當 toolbar 更新且有動畫時，`browserActionStack` 的 arranged subviews 會被處理兩次，可能導致動畫閃爍或約束衝突。

**建議**：應改為 `trailingPageActionStack`，與其他程式碼的重新命名一致。

finding 片段：`browserActionStack.arrangedSubviews`

## P0422

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 6 行）sortableKeys 未使用 useMemo，可能導致不必要的重新渲染

> `sortableKeys` 在每次 render 時重新建立陣列，若 `localKeyedValues` 未變，仍會產生新陣列參考，可能觸發 `SortableContext` 的重新渲染。建議使用 `useMemo` 包裹。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0423

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 0 行）使用 propertyName 取代 metadata.Name 可能導致參數比對失敗

> 原本以 `metadata.Name` 比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如 metadata.Name 可能包含前綴或不同大小寫），可能找不到對應參數，導致描述無法套用。請確認兩者在此情境下是否恆等。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0424

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0425

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:68`，距錨點 24 行）Popover 在桌面端僅依賴 mouseenter/mouseleave，缺乏鍵盤與觸控支援

> 在桌面端，Popover 的開啟與關閉僅由 Button 和 PopoverContent 上的 onMouseEnter/onMouseLeave 控制。這會導致：
1. 鍵盤使用者無法聚焦到觸發按鈕並開啟 popover（除非 PopoverTrigger 本身有處理，但此處未提供）。
2. 觸控裝置（如平板）沒有 hover 事件，使用者可能無法查看隱藏的 badges。
建議使用 Popover 的 trigger 屬性（如 click）或確保 Button 可聚焦並處理鍵盤事件，或提供明確的點擊切換。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0426

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 9 行）天數計算使用 Date.now() 導致測試不穩定

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但在測試中使用了 `sinon.useFakeTimers` 固定時間，而此方法並未使用注入的時鐘，可能導致測試結果與實際時間不一致，造成 flaky tests。建議將時間來源注入或使用可替換的 clock。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0427

**GT**（func）Incorrect cache count in observability logging

> In the get_plan_bulk_with_cache method, the logging statement reports `len(bulk_plans)` as the number of cached items instead of `len(plans_to_cache)`. This creates misleading observability metrics. When some tenant plans fail validation or are filtered out, bulk_plans will contain more entries than plans_to_cache, causing the log to report an inflated count of successfully cached items. This makes it difficult to diagnose caching issues and can mask problems where fewer plans are actually cached than expected.

GT 片段：`logger.info( ⏎ "get_plan_bulk_with_cache: cached %s new tenant plans to Redis", ⏎ len(bulk_plans), ⏎ )`

**finding**（`api/services/billing_service.py:376`，距錨點 4 行）json.dumps 無法序列化 SubscriptionPlan (TypedDict)

> 在 `get_plan_bulk_with_cache` 中，`subscription_plan` 是 `SubscriptionPlan` 型別（TypedDict），但 `json.dumps(subscription_plan)` 會嘗試直接序列化該物件。TypedDict 在執行時是普通的 dict，但此處的 `subscription_plan` 是從 `subscription_adapter.validate_python(plan_dict)` 回傳的，其型別為 `SubscriptionPlan`，實際上是一個 dict，因此 `json.dumps` 應該可以正常運作。然而，如果 `validate_python` 回傳的物件不是純 dict（例如是 Pydantic model 或其他自訂型別），則會拋出 `TypeError`。建議先將 `subscription_plan` 轉換為 dict 再序列化，例如 `json.dumps(dict(subscription_plan))`。

finding 片段：`json_str = json.dumps(subscription_plan)`

## P0428

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:17`，距錨點 0 行）非 @MainActor 的測試類別中呼叫 @MainActor 方法可能導致執行緒問題

> `LaunchScreenViewModelTests` 類別未標記 `@MainActor`，但其 `setUp` 中呼叫了 `DependencyHelperMock().bootstrapDependencies()`（未加 `await`，但該方法現在是 async 且 @MainActor）。這可能導致編譯錯誤或執行緒問題。建議將測試類別標記為 `@MainActor`，並確保呼叫方式正確。

finding 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

## P0429

**GT**（func）Empty lines not filtered in Expected Events textarea

> In the CustomTriggerFields component, the onChange handler for the Expected Events textarea fails to filter out empty or whitespace-only lines. When users press Enter multiple times or leave blank lines between events, these empty strings are included in the events array sent to the trigger configuration. This will cause backend validation failures or create malformed automation triggers that expect empty event names, leading to automations that never fire correctly.

GT 片段：`onChange={(e) => { ⏎ const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined); ⏎ }}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38`，距錨點 0 行）Expected Events 欄位在空輸入時可能設定為 undefined

> 在 `custom-trigger-fields.tsx` 中，當使用者清空文字區域時，`lines` 會是 `[""]`（長度為 1），因此 `field.onChange(lines)` 會被呼叫，而不是 `undefined`。這可能導致表單值變成 `[""]` 而非預期的空陣列或 undefined。建議檢查是否為空字串並設定為空陣列或 undefined。

finding 片段：`const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined);`

## P0430

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1728`，距錨點 1 行）截斷後未更新 AOF 檔案大小或相關狀態

> 呼叫 `truncate(aof_filepath, valid_up_to)` 後，程式僅將 `server.aof_fd` 的檔案偏移移至結尾，但未更新 `sb.st_size` 或其他可能快取的檔案大小資訊。若後續程式依賴 `sb.st_size` 或 AOF 檔案大小來判斷載入進度，可能產生不一致。建議在截斷後重新取得檔案狀態，或確保所有相關變數同步更新。

finding 片段：`if (truncate(aof_filepath,valid_up_to) == -1) { ⏎ serverLog(LL_WARNING,"Error truncating the AOF file: %s", ⏎ strerror(errno)); ⏎ } else {`

## P0431

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:452`，距錨點 12 行）使用 propertyName 取代 metadata.Name 可能導致參數比對失敗

> 原本以 `metadata.Name` 比對 operation.Parameters 中的參數名稱，現在改為 `propertyName`。若 `metadata.Name` 與 `propertyName` 不同（例如 metadata.Name 可能包含前綴或不同大小寫），可能找不到對應參數，導致描述無法套用。請確認兩者在此情境下是否恆等。

finding 片段：`var parameter = operation.Parameters?.SingleOrDefault(p => p.Name == propertyName);`

## P0432

**GT**（rule）Single underscore include guard used

> The rule requires header files to use include guards with double underscores at the start (e.g., __FILENAME_H), but the code uses a single underscore prefix instead (_REDIS_H)

GT 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

**finding**（`src/server.h:15`，距錨點 0 行）Include guard 命名不符合規範

> 變更將 include guard 從 `__REDIS_H` 改為 `_REDIS_H`，違反專案規範  （必須使用雙底線開頭與結尾）。此變更可能導致與其他標頭檔的 include guard 衝突，且破壞一致性。建議恢復為 `__REDIS_H`。

finding 片段：`#ifndef _REDIS_H ⏎ #define _REDIS_H`

## P0433

**GT**（func）BackgroundQueueSize incorrectly rejects zero value despite 'non-negative' contract

> The BackgroundQueueSize property validation was changed to reject values less than or equal to zero, but the error message states 'must be non-negative' which includes zero. According to the XML documentation, null represents no limit. While zero is semantically different from null, the validation is now inconsistent with the documented contract that explicitly states 'non-negative' (which mathematically includes zero). This prevents callers from setting a zero queue size if that was their intent, even though zero is a valid non-negative integer. The validation logic contradicts the error message, creating a confusing API contract.

GT 片段：`public int? BackgroundQueueSize ⏎ { ⏎ get { return _backgroundQueueSize; } ⏎ set`

**finding**（`src/Logging.AzureAppServices/src/BatchingLoggerOptions.cs:47`，距錨點 0 行）BackgroundQueueSize 驗證條件變更可能禁止 0 值

> 驗證條件從 `if (value < 0)` 改為 `if (value <= 0)`，這將禁止 `BackgroundQueueSize = 0`。但文件描述為「null for no limit」，且 0 可能被視為合法值（例如表示不排隊）。建議確認此變更是否為預期，若非預期應改回 `< 0`。

finding 片段：`if (value <= 0)`

## P0434

**GT**（rule）Double quotes used for string literal

> The rule requires string literals to use single quotes, but this code uses double quotes for the STORAGE_KEY constant without justified reason (no interpolation needed).

GT 片段：`export function getDefaultUrlHistory() { ⏎ const STORAGE_KEY = "ghost-history"; ⏎ try { ⏎ const historyString = sessionStorage.getItem(STORAGE_KEY);`

**finding**（`apps/signup-form/src/utils/helpers.tsx:45`，距錨點 22 行）getUrlHistory 回傳型別可能變為 undefined，呼叫端未處理

> 原本在 history 為 falsy 時會回傳 undefined，但現在直接回傳 history，型別從 URLHistory | undefined 變為 URLHistory | null | undefined（若 getDefaultUrlHistory 可能回傳 null）。呼叫端若未處理 null 可能導致執行時期錯誤。建議確認所有呼叫端皆能處理 null，或保留原本的條件判斷。

finding 片段：`return history;`

## P0435

**GT**（func）Configuration merge bypasses validation when merging with empty configs

> The `merge_config_with` function returns early with `Ok(())` when `merge_configs.is_empty()`, but this skips critical validation and state updates that should occur even when no merge is performed. The original code in `merge_with` returned the handle, maintaining the contract that callers could safely use the config. This early return can cause downstream code to operate on stale or unvalidated configuration state, particularly affecting build and dev commands that rely on properly initialized config metadata.

GT 片段：`pub fn merge_config_with( ⏎ config: &mut ConfigMetadata, ⏎ merge_configs: &[&serde_json::Value], ⏎ ) -> crate::Result<()> {`

**finding**（`crates/tauri-cli/src/helpers/config.rs:271`，距錨點 8 行）`merge_config_with` 未處理 `serde_json::to_string` 的錯誤

> 在 `merge_config_with` 中，`serde_json::to_string(&merge_config).unwrap()` 直接 unwrap。雖然 `merge_config` 是由 JSON Value 組成，序列化失敗的可能性極低，但為了穩健性，建議改為 `?` 或 `context` 處理。

finding 片段：`let merge_config_str = serde_json::to_string(&merge_config).unwrap();`

## P0436

**GT**（func）Authorization bypass when filtering multiple userIds including current user

> The isCurrentUser check was changed from a strict equality check (filters.userIds.length === 1 && user.id === filters.userIds[0]) to a loose inclusion check (filters.userIds.includes(user.id)). This allows a user to bypass permission checks by including their own userId in a list alongside other userIds they don't have permission to access. For example, if a user requests bookings for [ownUserId, unauthorizedUserId], the check passes even though they lack permission for the unauthorized user, allowing them to access bookings they shouldn't see.

GT 片段：`if (!!filters?.userIds && filters.userIds.length > 0) { ⏎ const areUserIdsWithinUserOrgOrTeam = filters.userIds.every((userId) => ⏎ allAccessibleUserIds.includes(userId) ⏎ );`

**finding**（`packages/trpc/server/routers/viewer/bookings/get.handler.ts:149`，距錨點 0 行）isCurrentUser 判斷邏輯變更可能導致權限繞過

> 原本 `isCurrentUser` 僅在 `filters.userIds.length === 1 && user.id === filters.userIds[0]` 時為 true，現在改為 `filters.userIds.includes(user.id)`。這表示若 userIds 陣列包含目前使用者 ID 及其他使用者 ID，則 `isCurrentUser` 會為 true，可能繞過後續的權限檢查。建議確認此變更是否符合預期，並確保不會造成未授權存取。

finding 片段：`const isCurrentUser = filters.userIds.includes(user.id);`

## P0437

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `custom-trigger-fields.tsx` but does not add a corresponding `custom-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const CustomTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" }); ⏎ return (`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:38`，距錨點 19 行）Expected Events 欄位在空輸入時可能設定為 undefined

> 在 `custom-trigger-fields.tsx` 中，當使用者清空文字區域時，`lines` 會是 `[""]`（長度為 1），因此 `field.onChange(lines)` 會被呼叫，而不是 `undefined`。這可能導致表單值變成 `[""]` 而非預期的空陣列或 undefined。建議檢查是否為空字串並設定為空陣列或 undefined。

finding 片段：`const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined);`

## P0438

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0439

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0440

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:148`，距錨點 0 行）sortableKeys 包含不可移動的 prefix items，可能導致拖放索引錯亂

> `sortableKeys` 直接使用所有 `localKeyedValues` 的 key，但 `canMove` 對 prefix items 回傳 false，這些項目不應參與排序。若使用者拖曳可移動項目到 prefix item 上，`handleDragEnd` 會計算出新索引並呼叫 `moveItem`，但 `moveItem` 內部可能未考慮 prefix items 不可移動的限制，導致陣列順序錯誤或 prefix items 被移動。

建議：`sortableKeys` 應只包含 `canMove` 為 true 的項目 key，並在 `handleDragEnd` 中檢查 `over` 是否為可移動項目。

finding 片段：`const sortableKeys = localKeyedValues.map((item) => item.key);`

## P0441

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能允許無效的 schedule 結構

> 此函式僅驗證 name 為非空字串，未驗證 schedule 欄位的結構（例如是否為陣列、元素是否為 { start, end } 物件）。若呼叫端傳入錯誤格式，可能導致後續 API 請求失敗或產生非預期行為。建議使用 Zod schema 進行完整驗證，或至少檢查 schedule 的型別與元素結構。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0442

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 將 `mark_edge_skipped` 移到 `propagate_skip_from_edge` 之後，可能改變遞迴過程中的邊狀態。若 `propagate_skip_from_edge` 依賴邊尚未被標記為 skipped 的狀態，此變更可能導致錯誤。建議確認此順序變更的必要性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0443

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:27`，距錨點 4 行）連結缺少可存取性標籤

> 連結內容只有圖示和流程名稱，但圖示可能無法被螢幕閱讀器正確讀取，建議加入 `aria-label` 或 `title` 屬性，提供更明確的描述。

finding 片段：`<Link ⏎ to="/flows/flow/$id" ⏎ params={{ id: flow.id }} ⏎ className="flex items-center gap-1"`

## P0444

**GT**（func）Inverted condition prevents lock version display for multiple crate versions

> The condition on line 194 checks if lock exists AND packages are NOT empty, but this logic is backwards. The code should handle the case where multiple versions exist in the lock file (when crate_lock_packages.len() != 1 as per line 170). The correct behavior is to show lock versions when the lock exists but no single matching package was found earlier. By inverting the is_empty check, the code now only executes when packages DO exist, which is the opposite of the intended scenario. This breaks the display of version information when there are dependency conflicts or multiple versions of the same crate.

GT 片段：`if lock.is_some() && !crate_lock_packages.is_empty() { ⏎ let lock_version = crate_lock_packages ⏎ .iter() ⏎ .map(|p| p.version.clone())`

**finding**（`crates/tauri-cli/src/helpers/cargo_manifest.rs:194`，距錨點 0 行）條件判斷邏輯反轉可能導致版本解析錯誤

> 原本的條件 `lock.is_some() && crate_lock_packages.is_empty()` 改為 `lock.is_some() && !crate_lock_packages.is_empty()`。這會使得當 lock 檔存在且 crate_lock_packages 非空時才進入鎖定版本解析，否則會回退到其他邏輯。若原本意圖是「當 lock 檔存在但找不到對應套件時才回退」，則此變更可能導致在 lock 檔存在且套件存在時仍使用鎖定版本，但若套件不存在則可能錯誤地使用其他來源。需要確認此變更是否為修正既有 bug，還是引入新問題。

finding 片段：`if lock.is_some() && !crate_lock_packages.is_empty() {`

## P0445

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行）bootstrapDependencies 標記為 @MainActor 但未處理非主執行緒呼叫

> `bootstrapDependencies` 被標記為 `@MainActor`，但方法內部仍有 `DispatchQueue.main.sync` 的舊程式碼被移除，改為直接在主執行緒上執行。這可能導致在非主執行緒呼叫時發生問題。建議確認所有呼叫點都在主執行緒上，或保留適當的執行緒處理。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## P0446

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）測試斷言可能指向錯誤的 UI 元素

> 在 `testCheckSystemThemeChanges` 中，原本檢查 `lightThemeView` 的 value，現在改為檢查 `darkThemeView`。但變數名稱仍為 `lightIsSelected`，且後續的 XCTAssertEqual 預期值為 "1"。如果 `darkThemeView` 的 value 在選取 Light mode 後不是 "1"，測試將失敗。需要確認此變更是否為刻意修正（例如原本的 identifier 有誤），否則可能造成測試不穩定或誤報。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0447

**GT**（func）Uninitialized slot value for keyless commands due to missing assignment

> The function extractKeysAndSlot now only sets the slot value when `num_keys > 0`, leaving the slot pointer uninitialized when num_keys is 0 (keyless commands). The caller (preprocessCommand in server.c) expects the slot to always be set by this function. For keyless commands, the slot will contain garbage data or whatever value was previously at that memory location, leading to unpredictable behavior in downstream slot validation logic and potentially causing commands to be incorrectly routed or rejected in cluster mode.

GT 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ } ⏎ return num_keys;`

**finding**（`src/db.c:3201`，距錨點 0 行）slot 可能未初始化

> 在 `extractKeysAndSlot` 中，原本的程式碼在 `num_keys >= 0` 時會將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，但修改後僅在 `num_keys > 0` 時呼叫 `extractSlotFromKeysResult` 來設定 `*slot`。若 `num_keys == 0`，`*slot` 將不會被設定，可能保留呼叫者傳入的未初始化值，導致後續使用時出現未定義行為。

**失敗情境**：當命令沒有 key 時，`*slot` 可能包含垃圾值，若後續程式碼依賴此值判斷 slot，可能造成錯誤。

**建議修法**：在 `num_keys == 0` 時明確將 `*slot` 設為 `INVALID_CLUSTER_SLOT`，或確保呼叫者已初始化。

finding 片段：`if (num_keys > 0) { ⏎ *slot = extractSlotFromKeysResult(argv, result); ⏎ }`

## P0448

**GT**（rule）Unused variable causes compilation warning

> The code declares an unused variable 'unused_flag' that triggers a compilation warning, causing the build to fail when -Werror flag is enabled

GT 片段：`void hincrbyfloatCommand(client *c) { ⏎ long double value, incr; ⏎ long long ll; ⏎ robj *o;`

**finding**（`src/t_hash.c:2244`，距錨點 0 行）變數 unused_flag 宣告後未使用

> 在 hincrbyfloatCommand 中宣告了 `int unused_flag = 0;` 但從未使用。這可能是開發過程中的殘留，應移除。

finding 片段：`int unused_flag = 0;`

## P0449

**GT**（rule）Unused import: Skeleton

> `Skeleton` is imported but never used in this file, which violates the rule requiring unused imports to be removed.

GT 片段：`import { Skeleton } from "@/components/ui/skeleton";`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1`，距錨點 5 行）未提供對應的測試檔案

> 根據規範  ，React 元件測試檔案應與元件放在同一目錄。此 PR 新增了 flow-icon-text.tsx，但未見 flow-icon-text.test.tsx。建議補上測試，至少涵蓋成功載入與錯誤處理的情境。

finding 片段：`import { useSuspenseQuery } from "@tanstack/react-query";`

## P0450

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）TryGetValidatableTypeInfo 中 out 參數初始化位置移動

> 原本在方法最後才設定 `validatableTypeInfo = null`，現在移到方法開頭。這在功能上可能沒有差異，因為 out 參數在方法內必須賦值，但移動位置可能影響可讀性或與其他程式碼的互動。建議確認此變更是否為預期，並確保所有路徑都有正確賦值。

finding 片段：`validatableTypeInfo = null;`

## P0451

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）回傳 Infinity 可能導致呼叫端未預期行為

> 當暖機天數超過 `totalDays` 時，`getWarmupLimit` 回傳 `Infinity`。若呼叫端將此值用於後續計算（例如分配郵件數量），可能產生非預期結果。建議回傳一個明確的數值（例如 `emailCount`）或定義一個特殊常數，並在文件說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0452

**GT**（func）Buffer overflow in HPEXPIREAT propagation array

> The argv array is declared with size 5 (robj *argv[5]) which allocates indices 0-4, but the code attempts to access argv[5] which is out of bounds. This array is used to propagate the HPEXPIREAT command to replicas and AOF when a field has expiration. The buffer overflow can cause memory corruption, crash the server, or lead to undefined behavior during replication.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：createStringObjectFromLongLong 建立的物件未釋放

> 在傳播 HPEXPIREAT 時，`argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 `alsoPropagate` 之後沒有對其進行 `decrRefCount`。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。

建議在 `alsoPropagate` 呼叫後加入 `decrRefCount(argv[2]);` 或使用 stack 分配的 robj 並設定 refcount。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`
