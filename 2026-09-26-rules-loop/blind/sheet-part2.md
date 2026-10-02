# 盲標單 2：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-26-rules-loop/blind/labels-part2.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0114

**GT**（func）Off-by-one error in scroll index calculation

> The scroll position calculation uses `state.tabs.count` instead of `state.tabs.count - 1` when scrolling to the last tab. Since array indices are zero-based, accessing index equal to the count will cause an index out-of-bounds crash. This occurs when switching between normal and private tab panels when there's no selected tab, causing the app to attempt scrolling to a non-existent tab position. The original code correctly used `count - 1` to get the last valid index before the inactive tabs feature was removed.

GT 片段：`if case .scrollToSelectedTab(let shouldAnimate) = scrollBehavior { ⏎ if let selectedTabIndex = state.tabs.firstIndex(where: { $0.isSelected }) { ⏎ return ScrollState(toIndex: selectedTabIndex, withAnimation: shouldAnimate) ⏎ } else if !state.tabs.isEmpty {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/State/TabsPanelState.swift:143`，距錨點 0 行）scrollToTab 的 toIndex 可能越界

> 在 `createTabScrollBehavior` 中，當沒有選取的 tab 時，回傳的 `toIndex` 為 `state.tabs.count`，但陣列索引應為 `count - 1`。這會導致滾動到不存在的索引，可能造成 collection view 崩潰或滾動到錯誤位置。

建議改為 `state.tabs.count - 1`。

finding 片段：`return ScrollState(toIndex: state.tabs.count, withAnimation: shouldAnimate)`

## P0115

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）Threshold 欄位使用 parseInt 而非 Number，可能導致非預期結果

> `parseInt(e.target.value)` 會將輸入轉為整數，若使用者輸入小數（如 1.5）會被截斷為 1，且若輸入為空字串或非數字字串，`parseInt` 會回傳 `NaN`，可能導致表單驗證失敗或提交錯誤資料。其他元件（如 `custom-trigger-fields.tsx`）使用 `Number(e.target.value)`，行為較一致且能正確處理小數。建議改為 `Number(e.target.value)`。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0116

**GT**（func）Incorrect stack view reference in divider width calculation

> The divider width is being determined by checking if leadingPageActionStack has elements instead of trailingPageActionStack. This was introduced during the refactoring that renamed pageActionStack to trailingPageActionStack. The divider should appear between the location view and trailing page actions, so it needs to check the trailing stack. This bug causes the divider to appear or disappear at incorrect times, breaking the visual separation between UI elements in the address toolbar.

GT 片段：`// Page action spacing ⏎ let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty ⏎ dividerWidthConstraint?.constant = hasPageActions ? uxConfig.browserActionsAddressBarDividerWidth : 0`

**finding**（`BrowserKit/Sources/ToolbarKit/AddressToolbar/BrowserAddressToolbar.swift:419`，距錨點 0 行）hasPageActions 判斷誤用 leadingPageActionStack

> 在 `updateToolbarLayout` 中，原本 `let hasPageActions = !pageActionStack.arrangedSubviews.isEmpty` 被改為 `!leadingPageActionStack.arrangedSubviews.isEmpty`。但此處的 `hasPageActions` 應代表 trailing page actions 是否存在，以決定 divider 寬度。若 leading 和 trailing page actions 不同時存在，可能導致 divider 顯示錯誤。

建議改回 `!trailingPageActionStack.arrangedSubviews.isEmpty`。

finding 片段：`let hasPageActions = !leadingPageActionStack.arrangedSubviews.isEmpty`

## P0117

**GT**（func）Missing From<FileWriteError> implementation causes compilation failure

> The write_and_make_executable function now returns Result<(), FileWriteError> instead of std::io::Result<()>, but there is no From<FileWriteError> implementation for the crate::Error type. All five call sites in prepare_tools use the ? operator which requires this conversion. The crate's Error enum has #[from] for io::Error but not for FileWriteError. This will cause compilation to fail with 'the trait From<FileWriteError> is not implemented for Error' at lines 232, 239, 245, 251, and 259, making the entire AppImage bundling functionality fail to compile.

GT 片段：`// Custom error type for file operations ⏎ #[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291`，距錨點 3 行）自訂錯誤型別未使用 thiserror

> 新增的 `FileWriteError` 手動實作 `Display` 和 `Error`，但專案規範 要求使用 `thiserror`。建議改用 `#[derive(thiserror::Error)]` 來簡化程式碼並保持一致。

finding 片段：`impl std::fmt::Display for FileWriteError { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ match self { ⏎ FileWriteError::Write(e) => write!(f, "Failed to write file: {}", e),`

## P0118

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:309`，距錨點 0 行）公開函式缺少文件註解

> write_and_make_executable 函式是公開的（pub fn），但沒有文件註解。根據規範  ，所有公開 API 都應該有 /// 文件說明其用途、參數和回傳值。建議補充文件。

finding 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> {`

## P0119

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:251`，距錨點 0 行）合併權重與群組標示可能造成視覺混淆

> 原本的實作中，權重（如 80%）和群組標示（如 (group)）是分開的 badge，現在合併成單一 label，例如「Value 80% (group)」。這可能讓使用者難以快速區分權重和群組狀態，且如果 label 過長，在有限的空間中可能被截斷。建議保留原本的分開顯示方式，或提供更清楚的視覺區隔。

finding 片段：`let label = attributeValue.value; ⏎ label = `${label} ${weight}`; ⏎ label = `${label}${groupIndicator}`;`

## P0120

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:49`，距錨點 21 行）validateCreateScheduleInput 回傳型別未嚴格驗證

> 函式回傳型別為 CreateScheduleInput，但僅透過型別斷言 (as CreateScheduleInput) 轉換，未實際驗證 schedule 與 eventTypeId 的型別。這可能導致呼叫端誤以為輸入已通過驗證，但實際上可能包含無效資料。建議使用型別守衛或 Zod schema 來確保型別安全。

finding 片段：`return data as CreateScheduleInput;`

## P0121

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0122

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1115`，距錨點 0 行）extractSlotFromKeysResult 中 free 位置不當導致記憶體洩漏

> 在 cross-slot 偵測到時，函式會 `free(slot_buffer)` 並回傳 `CLUSTER_CROSSSLOT`，但若迴圈正常結束，`free(slot_buffer)` 在迴圈外執行，這部分正確。然而，若在迴圈中發生 cross-slot，`free` 後直接回傳，但 `slot_buffer` 可能包含未初始化的值（若 `malloc` 成功但迴圈未完全填滿），但這不影響 free。真正的問題是：若 `malloc` 失敗（未檢查），則 `slot_buffer` 為 NULL，後續寫入會 crash。建議在 malloc 失敗時直接回傳 `INVALID_CLUSTER_SLOT`，並確保所有路徑都釋放記憶體。

finding 片段：`free(slot_buffer); ⏎ return CLUSTER_CROSSSLOT;`

## P0123

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 0 行）未處理 created_at 為 null 的情況

> `#getDaysSinceFirstEmail` 假設 `res.data[0].get('created_at')` 一定存在且為有效日期字串。若資料庫中該欄位為 null 或格式不符，`new Date(...)` 會產生 Invalid Date，導致計算結果為 NaN。建議加入防禦性檢查，例如驗證日期有效性或提供預設值。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0124

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）測試斷言可能失效：lightThemeView 改為 darkThemeView

> 在 testCheckSystemThemeChanges 測試中，原本選取 Light mode 後檢查 lightThemeView 的 value 為 "1"，現在改為檢查 darkThemeView 的 value。這可能導致測試失敗，因為選取 Light mode 時，darkThemeView 的 value 可能不是 "1"。建議確認此修改是否正確，或改回原本的 lightThemeView。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0125

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 為 null 時的行為不一致

> 在 getTeamsWithPBACPermissions 中，orgId 參數型別為 number | null，但 SQL 條件使用 `${orgId}::bigint IS NULL`。若 orgId 為 null，會產生 `null::bigint`，在 PostgreSQL 中可能被視為 NULL，但行為依賴於資料庫。建議明確處理 null 與 undefined。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0126

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）數字輸入的 type 從 'number' 改為 'text' 可能破壞數字驗證

> 原本 `<Input type="number" ...>` 改為 `<Input type="text" ...>`，這會讓瀏覽器不再限制輸入為數字，使用者可以輸入任意文字。如果後端預期收到數字，可能導致型別錯誤或驗證失敗。建議保留 `type="number"`，或明確說明為何需要改為文字輸入（例如為了自訂格式），並確保有適當的驗證。

finding 片段：`type="text"`

## P0127

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 3 行）Posture 變更時可能殘留舊欄位值

> 在 `deployment-status-trigger-fields.tsx` 中，當 posture 從 Reactive 切換到 Proactive 時，欄位名稱從 `trigger.expect` 改為 `trigger.after`，但舊的 `trigger.expect` 值可能仍保留在表單狀態中。這可能導致提交時包含不必要的資料。建議在 posture 變更時清除對應欄位。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0128

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1110`，距錨點 0 行）使用 malloc/free 而非 zmalloc/zfree

> 根據規範  ，應使用 zmalloc/zfree 而非標準 malloc/free。此處新增的 `malloc` 和 `free` 違反規範，且無法追蹤記憶體使用。建議改用 `zmalloc` 和 `zfree`。

finding 片段：`int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys);`

## P0129

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行）Badge 的 key 使用 label，可能因重複而導致 React 警告

> visibleItems 和 hiddenItems 中的 Badge 都以 item.label 作為 key，若 label 重複會產生 key 衝突。建議使用 index 或唯一識別碼。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0130

**GT**（rule）Uses single quotes instead of double quotes

> Rule 3 requires standardized formatting including double quotes for strings. The added code uses single-quoted strings in multiple places, violating the formatting rule.

GT 片段：`if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ } ⏎ ...`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 1 行）validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）及 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式的資料，可能導致後續 API 呼叫失敗或產生難以除錯的錯誤。建議使用 Zod 或更完整的型別檢查來驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0131

**GT**（rule）Helper methods marked public inappropriately

> Helper methods checkUrl(), copyUrl(), and checkCopiedUrl() are marked public but are only used internally within the ClipBoardTests class. They should be marked private to minimize exposure of internal implementation details.

GT 片段：`// Check for test url in the browser ⏎ public func checkUrl() { ⏎ let urlTextField = app.textFields[AccessibilityIdentifiers.Browser.AddressToolbar.searchTextField] ⏎ mozWaitForValueContains(urlTextField, value: "example.com")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/ClipBoardTests.swift:11`，距錨點 0 行）輔助方法改為 public 可能違反封裝原則

> 將 `checkUrl()`、`copyUrl()`、`checkCopiedUrl()` 三個方法從 internal 改為 public。這些方法僅在測試類別內部使用，若無外部呼叫需求，建議維持 internal 或改為 private，以符合最小暴露原則。

finding 片段：`public func checkUrl() {`

## P0132

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 10 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 與 eventTypeId 的型別。若呼叫端傳入錯誤型別（例如 schedule 不是陣列、eventTypeId 不是數字），將導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證方式完整驗證輸入，或至少檢查 schedule 與 eventTypeId 的型別。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0133

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行）bootstrapDependencies 標記 @MainActor 但未標示為 async

> 方法標記為 @MainActor，但未明確標示為 async。在 Swift 中，@MainActor 方法若在非主執行緒呼叫，編譯器會要求 await。此處方法內有同步程式碼，但呼叫端需 await，因此方法應隱含 async。建議明確加上 `async` 關鍵字以提升可讀性。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## P0134

**GT**（func）Navigation timing issue in settings toggle verification

> The test taps the 'Done' button before navigating to NewTabScreen, reversing the correct order of operations. The navigator.goto(NewTabScreen) call expects to transition from the settings screen, but 'Done' has already been tapped which dismisses the settings UI. This creates a race condition where the navigation command may fail or behave unpredictably because it's operating on an already-dismissed screen. The correct flow should be navigate first, then tap Done to confirm the navigation completed.

GT 片段：`app.switches["Shortcuts"].waitAndTap() ⏎ app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/HomePageSettingsUITest.swift:155`，距錨點 0 行）測試步驟順序變更可能影響穩定性

> 在 `testDisableTopSitesSettingsRemovesSection` 中，原本先 `navigator.goto(NewTabScreen)` 再點擊 `Done`，現在改為先點擊 `Done` 再 `navigator.goto(NewTabScreen)`。此變更可能影響測試的時序，若 `Done` 按鈕的點擊需要在新分頁畫面出現後才能生效，可能導致測試不穩定。建議確認此順序調整是否為必要，並在 CI 中觀察測試結果。

finding 片段：`app.buttons["Done"].waitAndTap() ⏎ navigator.goto(NewTabScreen)`

## P0135

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行）linuxdeploy 下載 URL 使用錯誤的架構變數

> 原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為 `arch`。若 `arch` 為 i686，則會下載不存在的 i686 版本，導致下載失敗。應保留 `linuxdeploy_arch`。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0136

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:20`，距錨點 0 行）硬編碼使用者可見文字，應使用 i18n 翻譯

> fallback UI 中的文字 "Loading devtools..." 是硬編碼的，違反專案規範  （前端使用者可見字串必須使用 i18n 翻譯）。請改用翻譯鍵，例如 `t('common.loading')` 或新增對應翻譯。

finding 片段：`<Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}>`

## P0137

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email trim 未同步更新驗證邏輯

> 提交時對 email 進行 trim，但驗證函式 isValidEmail 可能仍使用未 trim 的值。若使用者輸入前後有空白，驗證可能通過但提交的是 trim 後的值，或驗證失敗但 trim 後其實有效。建議在驗證前也進行 trim，或確認 isValidEmail 內部已處理。

finding 片段：`onSubmit({email: email.trim()});`

## P0138

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）使用 console.error 違反前端規範

> 此處使用 `console.error` 記錄錯誤，違反專案規範  （Frontend Code Must Not Use console Statements）。建議改用專案允許的 logging 機制，或移除該 console 語句。

finding 片段：`console.error('Failed to load React Scan devtools:', error)`

## P0139

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:34`，距錨點 14 行）tearDown() 中呼叫 super.tearDown() 可能需在最後執行

> 在 `tearDown() async throws` 中，`try await super.tearDown()` 被放在最後，但通常應先呼叫 super 再進行清理，以確保父類別狀態正確。請確認此順序是否會影響測試隔離。

finding 片段：`try await super.tearDown()`

## P0140

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）日期計算可能因時區或 DST 造成 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的 timestamp 差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或跨越 DST 轉換，可能導致天數計算多一天或少一天，進而影響暖機限制。建議改用 UTC 日曆日差（例如將兩個日期轉為 UTC 日期字串後相減），或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0141

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:79`，距錨點 8 行）Popover 缺乏鍵盤無障礙支援

> 觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

finding 片段：`aria-label={`Show ${hiddenItems.length} more items`} ⏎ onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0142

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）數字輸入框類型從 number 改為 text 可能影響驗證

> 將數字輸入框的 `type` 從 `number` 改為 `text`，可能導致瀏覽器不再自動驗證數字格式，且行動裝置可能顯示不同的鍵盤。若此變更非刻意為之，建議保留 `type="number"`。

finding 片段：`type="text"`

## P0143

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:20`，距錨點 9 行）硬編碼使用者可見文字，應使用 i18n 翻譯

> fallback UI 中的文字 "Loading devtools..." 是硬編碼的，違反專案規範  （前端使用者可見字串必須使用 i18n 翻譯）。請改用翻譯鍵，例如 `t('common.loading')` 或新增對應翻譯。

finding 片段：`<Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}>`

## P0144

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 將 `mark_edge_skipped` 移到 `propagate_skip_from_edge` 之後，可能改變遞迴過程中的邊狀態。若 `propagate_skip_from_edge` 依賴邊尚未被標記為 skipped 的狀態，此變更可能導致錯誤。建議確認此順序變更的必要性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0145

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）extractSlotFromKeysResult 迴圈邊界錯誤導致 heap buffer overflow

> 迴圈條件 `j <= keys_result->numkeys` 會多執行一次，當 `j == numkeys` 時，`slot_buffer[j] = this_slot;` 會寫入超出配置的記憶體（配置大小為 `numkeys` 個 int）。此外，`argv[keys_result->keys[j].pos]` 也會讀取超出 `keys_result->keys` 陣列範圍的記憶體。

**失敗情境**：當 `numkeys > 0` 時，最後一次迭代會造成 heap buffer overflow，可能導致程式崩潰或任意程式碼執行。

**建議修法**：將迴圈條件改為 `j < keys_result->numkeys`。

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0146

**GT**（rule）Missing MARK comments in Swift

> The rule requires Swift files to use MARK comments to organize distinct code sections such as Public Methods, Private Methods, Properties, and Initializers. This file lacks MARK comments to separate its public bootstrapDependencies method from its reset method.

GT 片段：`final class DependencyHelperMock { ⏎ @MainActor ⏎ func bootstrapDependencies( ⏎ injectedWindowManager: WindowManager? = nil,`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/DependencyInjection/DependencyHelperMock.swift:11`，距錨點 0 行）bootstrapDependencies 標記 @MainActor 但未標記 async，呼叫端需 await

> `bootstrapDependencies` 被標記為 `@MainActor`，但未標記為 `async`。在 Swift 中，從非 async 上下文呼叫 @MainActor 方法需要 await，但從 async 上下文呼叫則不需要。然而，此方法內部有同步的 MainActor 隔離操作，若從非 MainActor 執行緒呼叫會導致執行緒不安全。建議將方法標記為 `async`，或確保所有呼叫端都在 MainActor 上。

finding 片段：`@MainActor ⏎ func bootstrapDependencies(`

## P0147

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行）RequestBody.Description 設定位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在 if 區塊開頭，現在移到範例處理之後。若 `propertyComment.Examples` 存在但 `content` 為 null，會執行 `continue`，導致 `Description` 不會被設定。建議確認此情境是否會發生，或將 Description 設定保持在區塊開頭。

finding 片段：`operation.RequestBody.Description = description;`

## P0148

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）直接存取 process.env 判斷 webhook 是否啟用

> 在 `handleCancelBooking.ts` 中直接使用 `process.env.ENABLE_WEBHOOKS !== "false"` 來決定是否發送 webhook，違反  （環境變數不得在非設定程式碼中直接存取）。這會降低可測試性，且可能因環境變數未正確設定而導致 webhook 意外停用。建議將此判斷移至集中式設定模組，或透過依賴注入傳入。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0149

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 14 行）日期計算可能因時區或 DST 造成 off-by-one

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 與 `created_at` 的 timestamp 差值除以 86400000 毫秒，再以 `Math.ceil` 取整。若伺服器時區與 UTC 有偏移，或跨越 DST 轉換，可能導致天數計算多一天或少一天，進而影響暖機限制。建議改用 UTC 日曆日差（例如將兩個日期轉為 UTC 日期字串後相減），或明確指定時區。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0150

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142`，距錨點 0 行）拖放後呼叫 moveItem 的參數順序可能錯誤

> 在 `handleDragEnd` 中，取得 `oldIndex` 和 `newIndex` 後呼叫 `moveItem(newIndex, oldIndex)`。但 `moveItem` 的簽名為 `moveItem(index: number, newIndex: number)`（從既有程式碼推測），因此第一個參數應為原始索引，第二個參數為目標索引。目前傳入的順序相反，會導致拖放後項目順序錯誤。請確認 `moveItem` 的實作，並修正為 `moveItem(oldIndex, newIndex)`。

finding 片段：`moveItem(newIndex, oldIndex);`

## P0151

**GT**（func）Missing await on async MainActor method causing race condition

> The setUp method calls DependencyHelperMock().bootstrapDependencies() without the await keyword. Since bootstrapDependencies() is marked with @MainActor and performs critical initialization including setting up AppContainer, SearchEnginesManager, and other dependencies, this creates a race condition. Tests may start executing before dependencies are fully initialized, leading to unpredictable test failures, null pointer exceptions, or incorrect test state. This is particularly problematic since subsequent initialization steps (creating MockProfile, setting up LegacyFeatureFlagsManager) may depend on the container being properly bootstrapped.

GT 片段：`override func setUp() async throws { ⏎ try await super.setUp() ⏎ DependencyHelperMock().bootstrapDependencies() ⏎ profile = MockProfile()`

**finding**（`firefox-ios/firefox-ios-tests/Tests/ClientTests/Coordinators/LaunchView/LaunchScreenViewModelTests.swift:19`，距錨點 0 行）bootstrapDependencies() 未加 await，可能導致測試不穩定或失敗

> 在 `setUp() async throws` 中呼叫 `DependencyHelperMock().bootstrapDependencies()` 但未加 `await`。由於該方法現在是 async，未 await 會造成編譯錯誤或測試執行時依賴未正確初始化。請改為 `await DependencyHelperMock().bootstrapDependencies()`。

finding 片段：`DependencyHelperMock().bootstrapDependencies()`

## P0152

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行）RequestBody.Description 設定時機變更可能影響既有行為

> 原本在處理 propertyComment.Examples 之前就設定 `operation.RequestBody.Description = description`，現在移到處理 Examples 之後。若 Examples 處理過程中發生例外或提前 continue，可能導致 Description 未被設定。建議確認此變更不會造成描述遺失。

finding 片段：`operation.RequestBody.Description = description;`

## P0153

**GT**（func）Loading state not reset in minimal mode success case

> When the form is in minimal mode and successfully sends a magic link, the loading state is set to true but never reset to false. This causes the submit button to remain disabled with a loading spinner showing indefinitely, preventing users from resubmitting. The non-minimal mode correctly resets loading through setPage(), but minimal mode now lacks the setLoading(false) call that was removed, creating an inconsistent and broken user experience.

GT 片段：`if (minimal) { ⏎ // Don't go to the success page, but show the success state in the form ⏎ setSuccess(true); ⏎ } else {`

**finding**（`apps/signup-form/src/components/pages/form-page.tsx:29`，距錨點 0 行）移除 setLoading(false) 可能導致 minimal 模式永遠顯示 loading 狀態

> 在 minimal 模式下，送出成功後原本會呼叫 setLoading(false) 來停止 loading 動畫，但此 PR 移除了該行。若 loading 狀態沒有在其他地方被重設，使用者會看到無限的 loading 指示。請確認是否有其他機制（例如元件 unmount 或 effect）會重設 loading，否則應保留此行。

finding 片段：`setSuccess(true);`

## P0154

**GT**（func）onClick handler lost for hidden items in popover

> The LimitedBadges component displays overflow items in a popover when there are more items than maxVisible. However, the onClick handler is removed from hidden items in the popover (line 93-97). While visible badge items preserve their onClick functionality (line 69), the span elements in the popover don't call item.onClick. This breaks interactive functionality for users trying to click on hidden badges in the teams column or attribute columns, where clicking should filter the table.

GT 片段：`<div className="flex flex-col gap-1"> ⏎ {hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label}`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 22 行）Badge 的 onClick 可能導致非互動元素可點擊

> Badge 元件可能不支援 onClick，若傳入 onClick 可能導致無效或非預期的行為。建議確認 Badge 的 props 或改用 Button。

finding 片段：`<Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}>`

## P0155

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:86`，距錨點 22 行）mark_edge_skipped 順序變更可能導致狀態不一致

> 在 _propagate_skip_to_node 中，原本先呼叫 mark_edge_skipped 再遞迴 propagate_skip_from_edge，現在順序對調。這可能導致在遞迴過程中，邊的狀態尚未標記為 skipped，若遞迴中發生錯誤或依賴邊狀態的邏輯，可能造成不一致。需要確認此變更的必要性與影響。

finding 片段：`self._state_manager.mark_edge_skipped(edge.id) ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

## P0156

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:75`，距錨點 8 行）使用 Date.now() 而非可注入時鐘，導致測試與實際行為不一致

> `#getDaysSinceFirstEmail` 使用 `Date.now()` 計算天數，但測試中使用了 `sinon.useFakeTimers` 固定時間。在測試環境中，`Date.now()` 會被 fake timers 影響，但實際執行時使用真實時間。這使得測試無法完全模擬真實情境，且若未來需要測試不同時間點的行為，會受到限制。建議將時間來源注入（例如在建構子接收 `now` 函式），或使用 `this.#config` 中的時間服務。

finding 片段：`return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

## P0157

**GT**（rule）console.error used in frontend code

> Rule 25 prohibits console statements in frontend code. The added code logs an error with console.error when lazy-loading fails.

GT 片段：`}).catch((error) => { ⏎ console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null } ⏎ }),`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 0 行）React Scan 載入失敗時錯誤被吞掉且可能洩漏資訊

> 當動態 import 失敗時，catch 區塊會回傳一個靜默的 fallback 元件，導致錯誤被隱藏。此外，`console.error` 輸出的錯誤物件可能包含敏感的內部路徑或堆疊資訊，在生產環境中可能造成資訊洩漏。建議：1) 考慮使用更安全的錯誤記錄方式（例如 Sentry），避免直接輸出到 console；2) 在開發模式下保留錯誤顯示，但在生產環境中提供更安全的 fallback。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0158

**GT**（rule）Direct process.env access in handler

> Business logic directly accesses process.env.ENABLE_WEBHOOKS instead of receiving the configuration value through dependency injection or a configuration object

GT 片段：`// Only send webhooks if enabled in environment ⏎ const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false"; ⏎ const promises = webhooksEnabled ? webhooks.map((webhook) =>`

**finding**（`packages/features/bookings/lib/handleCancelBooking.ts:414`，距錨點 0 行）新增 ENABLE_WEBHOOKS 環境變數可能意外停用 webhook

> 此處新增 `const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`，若環境變數未設定，則 `webhooksEnabled` 為 `true`，行為不變。但若部署環境中已存在 `ENABLE_WEBHOOKS=false`（例如用於其他目的），則會意外停用所有取消 booking 的 webhook，可能導致下游系統收不到通知。建議確認此環境變數名稱是否專用，或改用更明確的名稱，並在文件中說明。

finding 片段：`const webhooksEnabled = process.env.ENABLE_WEBHOOKS !== "false";`

## P0159

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）write_and_make_executable 先設定權限再寫入檔案

> 函式 `write_and_make_executable` 先呼叫 `fs::set_permissions` 設定權限，再呼叫 `fs::write` 寫入檔案。若檔案不存在，`set_permissions` 會失敗並回傳錯誤，導致無法建立檔案。應先寫入檔案再設定權限，或使用 `OpenOptions` 建立檔案後設定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0160

**GT**（rule）Missing semicolons in getWarmupLimit method

> The rule requires all JavaScript and TypeScript statements to end with explicit semicolons, but this code relies on automatic semicolon insertion (ASI) instead

GT 片段：`async getWarmupLimit(emailCount: number): Promise<number> { ⏎ const day = await this.#getDaysSinceFirstEmail() ⏎ if (day >= this.#warmupConfig.totalDays) { ⏎ return Infinity`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0161

**GT**（func）Missing source parameter in Tinybird API request

> The fetchRawTopContentData method removes the critical logic that passes the `source` filter parameter to the Tinybird API. While the method still handles `options.source` validation (including empty strings for 'Direct' traffic) at lines 105-108 in the comment, it no longer assigns it to `tinybirdOptions.source`. This means source-based filtering will silently fail—the API endpoint will be called without the source parameter, returning unfiltered results instead of data filtered by the requested traffic source.

GT 片段：`// Only add location if defined ⏎ if (options.location) { ⏎ tinybirdOptions.location = options.location; ⏎ }`

**finding**（`ghost/core/core/server/services/stats/ContentStatsService.js:102`，距錨點 0 行）移除 source 參數傳遞可能破壞現有功能

> 此處刪除了將 `options.source` 加入 `tinybirdOptions` 的程式碼，但 `source` 是有效的過濾參數，且在其他端點（如 `api_top_sources_v2`）中仍被使用。若呼叫端仍傳入 `source`，將被忽略，導致結果不正確。

建議保留此參數傳遞，或確認所有呼叫端都已更新。

finding 片段：`// Only add source if defined (allow empty string for "Direct" traffic) ⏎ if (options.source !== undefined) { ⏎ tinybirdOptions.source = options.source; ⏎ }`

## P0162

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:291`，距錨點 0 行）自訂錯誤型別未使用 thiserror

> 新增的 FileWriteError 型別手動實作了 Display 和 Error trait，但專案規範   要求使用 thiserror 來定義錯誤型別。建議改用 `#[derive(thiserror::Error)]` 並使用 `#[error(...)]` 屬性來簡化程式碼並符合規範。

finding 片段：`impl std::fmt::Display for FileWriteError { ⏎ fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { ⏎ match self { ⏎ FileWriteError::Write(e) => write!(f, "Failed to write file: {}", e),`

## P0163

**GT**（func）Drag-and-drop reordering swaps source and target indices

> The handleDragEnd function passes arguments to moveItem in the wrong order - it calls moveItem(newIndex, oldIndex) instead of moveItem(oldIndex, newIndex). This causes drag-and-drop operations to place items in the opposite position from where they're dropped. For example, dragging an item from index 2 to index 0 will incorrectly move the item at index 0 to index 2 instead, creating confusing and incorrect reordering behavior for users.

GT 片段：`function handleDragEnd(event: DragEndEvent) { ⏎ const { active, over } = event; ⏎ if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex(`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 0 行）拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0164

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1730`，距錨點 3 行）日誌訊息中 broken size 可能為負數

> 在日誌訊息中，`(long long)(sb.st_size - valid_up_to)` 可能為負數（若 `valid_up_to` 大於 `sb.st_size`），但此處未檢查。雖然在正常情況下 `valid_up_to` 不應大於檔案大小，但若發生異常，日誌會顯示負數，造成混淆。建議加入檢查或使用無符號型別。

finding 片段：`serverLog(LL_WARNING, ⏎ "AOF loaded anyway because aof-load-broken is enabled and " ⏎ "broken size '%lld' is less than aof-load-broken-max-size '%lld'", ⏎ (long long)(sb.st_size - valid_up_to), (long long)(server.aof_load_broken_max_size));`

## P0165

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `hiddenItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{hiddenItems.map((item, index) => ( ⏎ <span ⏎ key={item.label} ⏎ className="text-default cursor-pointer text-sm hover:text-emphasis">`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:79`，距錨點 13 行）Popover 缺乏鍵盤無障礙支援

> 觸發按鈕僅有 aria-label，但未提供鍵盤操作方式（如 Enter/Space 開啟、Esc 關閉、焦點管理）。Radix Popover 通常內建鍵盤支援，但此處使用受控 open 搭配 hover 事件，可能覆蓋了預設行為。建議確認鍵盤使用者能否操作，或改用 Popover 的 trigger 屬性。

finding 片段：`aria-label={`Show ${hiddenItems.length} more items`} ⏎ onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0166

**GT**（func）Type mismatch in Slot.userIds changes number[] to string[]

> The Slot type definition has been changed from userIds?: number[] to userIds?: string[]. This breaks the contract with existing code that expects numeric user IDs. Throughout the codebase, user IDs are consistently represented as numbers (see SlotInfo.fromUser.id, SlotInfo.toUser.id types for reference), and any code that passes numeric user IDs to slots or processes userIds from slots will now encounter type errors or runtime issues when trying to perform numeric operations or comparisons with these IDs.

GT 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

**finding**（`packages/platform/atoms/booker/types.ts:17`，距錨點 0 行）Slot 型別中 userIds 型別從 number[] 改為 string[]，可能與實際 API 回應不符

> 原本從 @calcom/trpc/server/routers/viewer/slots/types 匯入的 Slot 型別中 userIds 為 number[]，但此處新定義為 string[]。若實際 API 回傳的 userIds 為數字陣列，將導致型別錯誤或執行時期問題。請確認 API 實際回傳型別，並保持與原定義一致。

finding 片段：`export type Slot = { ⏎ time: string; ⏎ userIds?: string[]; ⏎ attendees?: number;`

## P0167

**GT**（func）orgId parameter not propagated in getTeamIdsWithPermission

> The method getTeamIdsWithPermission accepts an orgId parameter to scope permission checks to a specific organization, but it fails to pass this parameter to the underlying getTeamIdsWithPermissions method. This causes organization scoping to be ignored when checking single permissions, allowing users to potentially access teams from all organizations instead of only the specified one. The bug breaks the core security feature introduced in this PR where organization-scoped permission checks were meant to restrict access based on orgId.

GT 片段：`async getTeamIdsWithPermission({ ⏎ userId, ⏎ permission, ⏎ fallbackRoles,`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:222`，距錨點 0 行）getTeamIdsWithPermission 未傳遞 orgId 參數

> 在 `getTeamIdsWithPermission` 方法中，呼叫 `this.getTeamIdsWithPermissions` 時未傳遞 `orgId` 參數，導致 orgId 過濾功能在單一權限查詢中失效。建議補上 `orgId` 參數。

finding 片段：`return this.getTeamIdsWithPermissions({ userId, permissions: [permission], fallbackRoles });`

## P0168

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行）RequestBody.Description 指派位置變更可能影響範例處理

> 原本 `operation.RequestBody.Description = description;` 在處理範例之前，現在移到範例處理之後。若 `propertyComment.Examples` 存在且解析失敗，原本仍會設定 Description，現在則可能不會。建議確認此順序變更是否會造成行為差異。

finding 片段：`operation.RequestBody.Description = description;`

## P0169

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1725`，距錨點 2 行）valid_up_to 可能為 -1 或指向錯誤位置，導致截斷過多或過少

> 在 `fmterr` 處理中，程式使用 `valid_up_to` 作為截斷位置。但 `valid_up_to` 的初始值為 -1，且只有在成功解析命令後才會更新。如果格式錯誤發生在第一個命令之前，`valid_up_to` 會是 -1，此時 `sb.st_size - valid_up_to` 會變成 `sb.st_size + 1`，可能大於 `aof_load_broken_max_size`，導致無法自動修復。另外，如果 `valid_up_to` 指向的位置不是命令邊界（例如在多命令 AOF 中，某個命令解析到一半失敗），截斷後可能留下不完整的命令，造成後續載入錯誤。

**失敗情境**：AOF 檔案開頭就是損壞資料，且 `aof-load-broken-max-size` 設定大於檔案大小，程式會因為 `valid_up_to == -1` 而拒絕修復，但實際上整個檔案都應該被丟棄。

**建議**：在 `valid_up_to == -1` 時，應將截斷位置設為 0（或直接視為空檔案），並確保截斷位置落在命令邊界上。

finding 片段：`if (valid_up_to == -1) { ⏎ serverLog(LL_WARNING,"Last valid command offset is invalid"); ⏎ } else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

## P0170

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:133`，距錨點 14 行）handleDragEnd 未驗證 over 項目是否可移動

> 在 `handleDragEnd` 中，僅檢查 `over` 存在且 id 不同，未確認 `over` 對應的項目是否可移動（即非 prefix item）。若使用者將可移動項目拖到 prefix item 上，會執行 `moveItem`，可能導致 prefix item 被移動或陣列順序錯誤。

建議：在執行移動前，檢查 `over` 對應的 index 是否滿足 `getCanMoveForIndex(newIndex)`。

finding 片段：`if (over && active.id !== over.id) { ⏎ const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ );`

## P0171

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:49`，距錨點 3 行）validateCreateScheduleInput 回傳型別未嚴格驗證

> 函式回傳型別為 CreateScheduleInput，但僅透過型別斷言 (as CreateScheduleInput) 轉換，未實際驗證 schedule 與 eventTypeId 的型別。這可能導致呼叫端誤以為輸入已通過驗證，但實際上可能包含無效資料。建議使用型別守衛或 Zod schema 來確保型別安全。

finding 片段：`return data as CreateScheduleInput;`

## P0172

**GT**（func）Incorrect section index after inactive tabs removal

> The scrollToTab method hardcodes section index as 1, which was correct when there were two sections (inactive tabs at section 0 and regular tabs at section 1). After removing inactive tabs, there is only one section (section 0), so this will cause scroll operations to fail or crash when trying to access a non-existent section. This affects all scroll-to-tab functionality including selecting tabs, undoing tab closures, and panel switching. The TabDisplayDiffableDataSource now only creates a single section `.tabs`, but this scroll method wasn't updated accordingly.

GT 片段：`private func scrollToTab(_ scrollState: TabsPanelState.ScrollState) { ⏎ let indexPath = IndexPath(row: scrollState.toIndex, section: 1) ⏎ // Piping this into main thread let the collection view finish its layout process ⏎ DispatchQueue.main.async {`

**finding**（`firefox-ios/Client/Frontend/Browser/Tabs/Views/TabDisplayView.swift:172`，距錨點 0 行）scrollToTab 使用硬編碼 section 1

> 在 `scrollToTab` 方法中，原本根據 `scrollState.isInactiveTabSection` 決定 section，現在固定為 1。由於移除 inactive tabs 後只剩一個 section，這樣做可能正確，但若未來新增 section 則容易出錯。建議使用常數或從 snapshot 取得 section index。

finding 片段：`let indexPath = IndexPath(row: scrollState.toIndex, section: 1)`

## P0173

**GT**（func）Empty lines not filtered in Expected Events textarea

> In the CustomTriggerFields component, the onChange handler for the Expected Events textarea fails to filter out empty or whitespace-only lines. When users press Enter multiple times or leave blank lines between events, these empty strings are included in the events array sent to the trigger configuration. This will cause backend validation failures or create malformed automation triggers that expect empty event names, leading to automations that never fire correctly.

GT 片段：`onChange={(e) => { ⏎ const lines = e.target.value.split("\n"); ⏎ field.onChange(lines.length > 0 ? lines : undefined); ⏎ }}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/custom-trigger-fields.tsx:39`，距錨點 0 行）Expected Events 欄位在空輸入時設定為 undefined 可能導致型別不符

> 當使用者清空文字框時，`lines` 為 `['']`，`lines.length > 0` 為 true，因此 `field.onChange([''])` 會被呼叫，而不是 `undefined`。這可能導致表單值包含空字串，與預期的 `undefined` 不符。建議檢查 `lines` 是否為空或僅包含空字串。

finding 片段：`field.onChange(lines.length > 0 ? lines : undefined);`

## P0174

**GT**（rule）Print statement in production code

> The rule requires that all logging in production code must be performed using logger = logging.getLogger(__name__) declared at module top, with no print() statements outside of test files

GT 片段：`# Enqueue node ⏎ self._state_manager.enqueue_node(downstream_node_id) ⏎ print(f"Starting execution for node: {downstream_node_id}") ⏎ self._state_manager.start_execution(downstream_node_id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 21 行）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 在 _propagate_skip_to_node 中，原本先 mark_edge_skipped 再 propagate_skip_from_edge，現在順序對調。若 propagate_skip_from_edge 內部依賴邊的 skipped 狀態（例如 analyze_edge_states 會檢查），則可能導致行為不同。需確認此變更是否為修正所需，並驗證遞迴邏輯仍正確。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0175

**GT**（func）Incorrect truthy check for retry_jitter_factor hides valid zero values

> The retry_jitter_factor check was changed from an explicit null/undefined check to a simple truthy check. This is a critical bug because a jitter factor of 0 is a valid configuration value (meaning no randomness in retry delays), but the truthy check treats 0 as falsy and displays "None" instead. This misrepresents the actual task configuration to users, making them think no jitter factor is set when it's actually configured to 0. The original PR correctly distinguished between 'not set' (null/undefined) and 'set to zero' (0), but this change breaks that distinction.

GT 片段：`<dl className="flex flex-col gap-1 mb-2"> ⏎ <dt className="text-gray-500">Retry Jitter Factor</dt> ⏎ <dd className=""> ⏎ {taskRun.empirical_policy?.retry_jitter_factor`

**finding**（`ui-v2/src/components/task-runs/task-run-details/task-run-details.tsx:179`，距錨點 0 行）retry_jitter_factor 為 0 時顯示 'None'

> 條件 `taskRun.empirical_policy?.retry_jitter_factor` 在值為 0 時為 falsy，因此會顯示 'None'，但 0 是有效的 jitter factor。建議改用 `typeof ... === 'number'` 或 `??` 來判斷。

finding 片段：`{taskRun.empirical_policy?.retry_jitter_factor ⏎ ? taskRun.empirical_policy.retry_jitter_factor.toString() ⏎ : "None"}`

## P0176

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:44`，距錨點 24 行）maxVisible 為 0 或負數時行為未定義

> 若 maxVisible 傳入 0 或負數，visibleItems 會是空陣列，hiddenItems 會包含所有項目，但 UI 仍會顯示 +N 按鈕，可能造成困惑。建議加上 prop 驗證或限制最小值為 1。

finding 片段：`visibleItems: items.slice(0, maxVisible), ⏎ hiddenItems: items.slice(maxVisible),`

## P0177

**GT**（func）Missing Suspense fallback causes blank UI during loading

> The FlowIconText component wraps FlowIconTextImplementation in a Suspense boundary but doesn't provide a fallback prop. When the component suspends while fetching flow data via useSuspenseQuery, React has no fallback content to display, resulting in a blank space in the UI until the query resolves. This creates a poor user experience with no loading indicator. The original implementation should have included a fallback prop like `<Skeleton className="h-4 w-full" />` to show a loading state during data fetching.

GT 片段：`export const FlowIconText = ({ flowId }: FlowIconTextProps) => { ⏎ return ( ⏎ <Suspense> ⏎ <FlowIconTextImplementation flowId={flowId} />`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:21`，距錨點 0 行）useSuspenseQuery 缺少錯誤邊界，查詢失敗可能導致應用程式崩潰

> `useSuspenseQuery` 在查詢失敗時會拋出錯誤，若沒有被 ErrorBoundary 捕獲，會導致整個 React 元件樹卸載。建議在 FlowIconText 外層包覆 ErrorBoundary，或改用 `useQuery` 並自行處理錯誤狀態。

finding 片段：`const { data: flow } = useSuspenseQuery(buildFLowDetailsQuery(flowId));`

## P0178

**GT**（func）Off-by-one error in warmup completion check extends warmup period

> The condition checking if warmup is complete uses `day > this.#warmupConfig.totalDays` instead of `day >= this.#warmupConfig.totalDays`. With a 42-day warmup period (totalDays=42), this means the warmup won't complete until day 43 instead of day 42. On day 42, the system will still calculate and apply a limit instead of returning Infinity to indicate unlimited sending. This extends the warmup period by one full day, delaying when users can send emails at full volume and potentially causing confusion when the warmup doesn't complete as documented.

GT 片段：`const day = await this.#getDaysSinceFirstEmail() ⏎ if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 0 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0179

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:86`，距錨點 0 行）mark_edge_skipped 順序變更可能導致狀態不一致

> 在 _propagate_skip_to_node 中，原本先呼叫 mark_edge_skipped 再遞迴 propagate_skip_from_edge，現在順序對調。這可能導致在遞迴過程中，邊的狀態尚未標記為 skipped，若遞迴中發生錯誤或依賴邊狀態的邏輯，可能造成不一致。需要確認此變更的必要性與影響。

finding 片段：`self._state_manager.mark_edge_skipped(edge.id) ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

## P0180

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1860`，距錨點 18 行）AOF_BROKEN_RECOVERED 在非最後檔案時未正確處理（第二處）

> 與前一個 finding 相同，在第二個迴圈中也有相同的邏輯，建議一併修正。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0181

**GT**（rule）Method brace on same line

> The rule requires opening braces to appear on a new line after method declarations, but this method has its opening brace on the same line as the declaration (K&R style).

GT 片段：`[Experimental("ASP0029", UrlFormat = "https://aka.ms/aspnet/analyzer/{0}")] ⏎ public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) { ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:66`，距錨點 0 行）方法開頭括號未換行，違反 Allman 風格

> `TryGetValidatableParameterInfo` 方法的開頭括號從新行移至與方法簽名同一行，違反專案規範  （Opening Braces Must Be on New Line）。建議將 `{` 移至下一行。

finding 片段：`public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) {`

## P0182

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:73`，距錨點 2 行）鍵盤使用者無法操作 Popover

> PopoverTrigger 包著 Button，但 Button 沒有設定 onClick 處理常式，而是依賴 Popover 的 onOpenChange。鍵盤使用者聚焦到 Button 後按 Enter 或 Space 會觸發 Button 的點擊事件，但 Popover 可能不會因此開啟，因為 PopoverTrigger 的 asChild 會將事件處理器傳遞給 Button，但 Button 本身沒有 onClick，可能導致事件無法正確觸發 Popover 的開啟。建議明確設定 Button 的 onClick 來切換 isOpen，或確保 PopoverTrigger 的事件處理能正確傳遞。

finding 片段：`<Button ⏎ color="minimal" ⏎ className="h-auto p-0 border-0 hover:border-0" ⏎ aria-label={`Show ${hiddenItems.length} more items`}`

## P0183

**GT**（rule）Needless return statement in function

> The rule requires all Rust code to pass 'cargo clippy --all-targets --all-features -- -D warnings' without any warnings. The code contains an unnecessary explicit return statement that Clippy will flag with the needless_return lint.

GT 片段：`#[cfg(not(feature = "platform-certs"))] ⏎ let agent: ureq::Agent = ureq::Agent::config_builder() ⏎ .proxy(ureq::Proxy::try_from_env()) ⏎ .build()`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:56`，距錨點 6 行）新增的 base_ureq_agent 函式缺少文件註解

> 新增的 `pub(crate) fn base_ureq_agent()` 是公開 API（crate 內可見），但缺少 `///` 文件註解。根據專案規範  ，所有公開 API 都應有文件說明。建議補充說明此函式的用途與回傳值。

finding 片段：`pub(crate) fn base_ureq_agent() -> ureq::Agent {`

## P0184

**GT**（rule）Raising generic Exception instead of domain-specific exception

> New code raises a generic `Exception` from a service method. Per the rule, backend services should raise domain-specific exceptions (e.g., from `services/errors` or `core/errors`) to provide clearer context and allow consistent translation to HTTP responses.

GT 片段：`if len(cached_values) != len(tenant_ids): ⏎ raise Exception( ⏎ "get_plan_bulk_with_cache: unexpected error: redis mget failed: cached values length mismatch" ⏎ )`

**finding**（`api/services/billing_service.py:292`，距錨點 33 行）型別不一致：`get_plan_bulk` 可能回傳 `None` 值，但型別標註為 `SubscriptionPlan`

> 在 `get_plan_bulk` 方法中，當 `subscription_adapter.validate_python(plan)` 拋出例外時，程式碼會將 `results[tenant_id]` 設為 `None`。然而，方法的回傳型別標註為 `dict[str, SubscriptionPlan]`，這表示每個值都應該是 `SubscriptionPlan` 物件，而不是 `None`。這會導致下游呼叫者在未檢查 `None` 的情況下直接存取屬性（例如 `plan['plan']`）時發生 `AttributeError` 或 `TypeError`。

**具體失敗情境**：
1. 某個 tenant 的 billing API 回傳了格式錯誤的資料（例如缺少 `expiration_date` 欄位）。
2. `get_plan_bulk` 將該 tenant 對應的值設為 `None`。
3. 呼叫者（例如 `get_plan_bulk_with_cache` 或其它程式碼）遍歷回傳的字典，並直接使用 `subscription_plan['plan']`，此時會因為 `None` 沒有 `__getitem__` 方法而拋出例外。

**建議修法**：
- 將回傳型別改為 `dict[str, Optional[SubscriptionPlan]]`，並確保所有呼叫者都處理 `None` 的情況。
- 或者，在驗證失敗時直接跳過該 tenant（不加入 `results`），而不是設為 `None`。這樣可以保持型別一致性，但需要確認呼叫者是否依賴於鍵的存在性。

finding 片段：`results[tenant_id] = None`

## P0185

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:142`，距錨點 5 行）拖放後呼叫 moveItem 的參數順序可能錯誤

> 在 `handleDragEnd` 中，取得 `oldIndex` 和 `newIndex` 後呼叫 `moveItem(newIndex, oldIndex)`。但 `moveItem` 的簽名為 `moveItem(index: number, newIndex: number)`（從既有程式碼推測），因此第一個參數應為原始索引，第二個參數為目標索引。目前傳入的順序相反，會導致拖放後項目順序錯誤。請確認 `moveItem` 的實作，並修正為 `moveItem(oldIndex, newIndex)`。

finding 片段：`moveItem(newIndex, oldIndex);`

## P0186

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> 新增的 `let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape` 使用了 iOS 13 已棄用的 `statusBarOrientation`，可能導致未來版本無法正確取得方向。建議改用 `view.window?.windowScene?.interfaceOrientation` 或其他現代 API。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0187

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）將 number 輸入的 type 從 'number' 改為 'text' 可能導致非數字輸入

> 原本使用 `type="number"` 可限制輸入為數字，改為 `type="text"` 後，使用者可以輸入任意字元，可能導致後續處理錯誤。若目的是移除 maxLength 限制，應保留 type="number" 並移除 maxLength 屬性。

finding 片段：`type="text"`

## P0188

**GT**（func）Unsigned integer wraparound in AOF corruption size check

> The size comparison casts both operands to size_t (unsigned), which causes undefined behavior when valid_up_to exceeds sb.st_size. In this edge case, the subtraction sb.st_size - valid_up_to produces a negative value that wraps around to a very large unsigned integer, always exceeding aof_load_broken_max_size. This prevents automatic recovery even when the corruption is actually small, causing the server to fail to start when it should recover successfully.

GT 片段：`} else if ((size_t)(sb.st_size - valid_up_to) < (size_t)server.aof_load_broken_max_size) {`

**finding**（`src/aof.c:1722`，距錨點 5 行）AOF_BROKEN_RECOVERED 在非最後一個檔案時未正確處理，可能導致資料不一致

> 在 loadAppendOnlyFiles 中，當 ret == AOF_BROKEN_RECOVERED 且 !last_file 時，程式碼將 ret 設為 AOF_FAILED 並記錄錯誤，但隨後在 if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) 的條件中，因為 ret 已被改為 AOF_FAILED，所以會進入 cleanup 並中止載入。然而，此處的邏輯有問題：如果 AOF_BROKEN_RECOVERED 發生在非最後一個檔案，實際上檔案已被 truncate 修改，但後續的檔案仍可能被載入，導致資料不一致。建議在非最後一個檔案遇到 AOF_BROKEN_RECOVERED 時，應立即中止載入並回報錯誤，且不應修改原始檔案。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0189

**GT**（func）Incorrect rounding in day calculation causes off-by-one error in warmup schedule

> The getDaysSinceFirstEmail method uses Math.ceil instead of Math.floor to calculate days since the first email. This causes the warmup to start one day ahead of schedule. For example, on the same day an email is sent (even minutes after), the partial day will round up to day 1 instead of day 0. This breaks the entire 42-day warmup progression as all subsequent calculations will be offset by one day, causing the service to use higher email limits than intended for each actual day, potentially harming domain reputation by warming up too aggressively.

GT 片段：`if (!res.data.length) { ⏎ return 0; ⏎ } ⏎ return Math.ceil((Date.now() - new Date(res.data[0].get('created_at') as string).getTime()) / (1000 * 60 * 60 * 24));`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 10 行）暖機完成後回傳 Infinity 可能導致呼叫端錯誤

> `getWarmupLimit` 在 `day > totalDays` 時回傳 `Infinity`。呼叫端若直接將此值用於計算或比較，可能產生非預期結果（例如 `Math.min(emailCount, Infinity)` 會回傳 `emailCount`，但若後續有算術運算或序列化，`Infinity` 可能造成問題）。建議改為回傳 `emailCount`（表示無限制），或明確回傳一個可辨識的常數，並在文件與型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`

## P0190

**GT**（func）Wrong dictionary used in Redis cache pipeline loop

> In the get_plan_bulk_with_cache method, when caching new tenant plans to Redis, the code iterates over `bulk_plans.items()` instead of `plans_to_cache.items()`. This is problematic because `bulk_plans` may contain tenant plans that had None values from validation failures in get_plan_bulk (when results[tenant_id] = None is set on exception). The code will attempt to cache these None values or invalid entries, leading to corrupted cache data. Additionally, if bulk_plans contains more entries than plans_to_cache due to any filtering logic, the logging statement will report an incorrect count of cached items.

GT 片段：`if plans_to_cache: ⏎ try: ⏎ pipe = redis_client.pipeline() ⏎ for tenant_id, subscription_plan in bulk_plans.items():`

**finding**（`api/services/billing_service.py:372`，距錨點 0 行）快取寫入時未使用 pipeline 的上下文管理器

> `redis_client.pipeline()` 通常建議使用 `with` 語句來確保資源正確釋放。雖然目前程式碼在 `try` 區塊中呼叫 `pipe.execute()`，但如果 `pipe.execute()` 拋出例外，pipeline 物件可能不會被正確關閉，導致連線洩漏。

**建議修法**：使用 `with redis_client.pipeline() as pipe:` 來管理 pipeline 的生命週期。

finding 片段：`pipe = redis_client.pipeline()`

## P0191

**GT**（rule）Manual error trait implementation used

> The rule requires all custom error types to use #[derive(thiserror::Error)] with appropriate #[error(...)] attributes for descriptive error messages, but FileWriteError manually implements Display and Error traits instead

GT 片段：`#[derive(Debug)] ⏎ enum FileWriteError { ⏎ Write(std::io::Error), ⏎ Permissions(std::io::Error),`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 8 行）write_and_make_executable 先設定權限再寫入，可能導致權限被覆蓋

> 函式 `write_and_make_executable` 原本先寫入檔案再設定權限，現在改為先設定權限再寫入。若檔案已存在，`fs::write` 會以預設權限（通常為 0644）覆寫內容，導致先前設定的執行權限（0770）遺失。建議改回先寫入再設定權限，或使用 `OpenOptions` 明確指定權限。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0192

**GT**（func）Off-by-one error causing buffer overflow in extractSlotFromKeysResult

> The loop condition in extractSlotFromKeysResult uses `j <= keys_result->numkeys` instead of `j < keys_result->numkeys`, causing an off-by-one error. This results in accessing one element beyond the valid range of both the `keys_result->keys` array and the `slot_buffer` array. When numkeys is N, valid indices are 0 to N-1, but the loop accesses index N, leading to out-of-bounds memory access. This can cause crashes, memory corruption, or unpredictable behavior when processing multi-key commands in cluster mode.

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j <= keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1115`，距錨點 0 行）使用 free 而非 zfree

> 根據規範  ，應使用 zfree 而非 free。此處的 `free(slot_buffer)` 違反規範。建議改用 `zfree`。

finding 片段：`free(slot_buffer);`

## P0193

**GT**（func）Generic type parameter mismatch in component marker validation

> The test creates and renders a GenericComponent<int> with value 456, but then validates the component marker against GenericComponent<string> type instead of GenericComponent<int>. This causes the test to check for the wrong fully qualified type name and assembly metadata. The type validation will fail because the actual rendered component is GenericComponent<int> while the test expects GenericComponent<string>, breaking the validation of WebAssembly component prerendering for closed generic types.

GT 片段：`var preamble = match.Groups["preamble"].Value; ⏎ var preambleMarker = JsonSerializer.Deserialize<ComponentMarker>(preamble, ServerComponentSerializationSettings.JsonSerializationOptions); ⏎ Assert.NotNull(preambleMarker.PrerenderId); ⏎ Assert.Equal("webassembly", preambleMarker.Type);`

**finding**（`src/Components/Endpoints/test/EndpointHtmlRendererTest.cs:837`，距錨點 0 行）ClientMode 測試中使用了錯誤的泛型型別

> 在 `CanPrerender_ClosedGenericComponent_ClientMode` 測試中，元件是以 `typeof(GenericComponent<int>)` 進行 prerender，但後續斷言卻使用 `typeof(GenericComponent<string>)` 來取得 Assembly 與 FullName。這會導致斷言失敗，因為 `GenericComponent<int>` 與 `GenericComponent<string>` 的 FullName 不同（例如 `GenericComponent`1[[System.Int32]]` vs `GenericComponent`1[[System.String]]`）。建議將斷言中的型別改為 `typeof(GenericComponent<int>)`。

finding 片段：`Assert.Equal(typeof(GenericComponent<string>).Assembly.GetName().Name, preambleMarker.Assembly); ⏎ Assert.Equal(typeof(GenericComponent<string>).FullName, preambleMarker.TypeName);`

## P0194

**GT**（func）Incorrect condition causes cross-slot check for keyless commands

> The condition was changed from `num_keys > 0` to `num_keys >= 0`, which incorrectly includes the case where num_keys equals 0. For keyless commands (num_keys == 0), the slot value may be uninitialized or contain arbitrary data from extractKeysAndSlot. The code will then spuriously check if this uninitialized slot equals CLUSTER_CROSSSLOT, potentially causing false positive cross-slot errors for legitimate keyless commands. This breaks the handling of keyless commands like PING, INFO, or SELECT in cluster mode.

GT 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

**finding**（`src/server.c:4141`，距錨點 0 行）條件判斷變更可能影響無 key 命令的處理

> 原本 `else if (num_keys > 0)` 只在有 key 時檢查 cross-slot，現在改為 `else if (num_keys >= 0)`，這會讓 `num_keys == 0` 的命令也進入檢查。若 `pcmd->slot` 為 `CLUSTER_CROSSSLOT`（不太可能，因為無 key 命令不會有 cross-slot），則會設定錯誤。但更可能的是，原本 `num_keys == 0` 時會跳過此區塊，現在會執行，可能影響後續邏輯。

建議確認此變更是否必要，或改回 `num_keys > 0`。

finding 片段：`} else if (num_keys >= 0) { ⏎ /* Handle cross-slot keys: mark error and reset slot. */ ⏎ if (pcmd->slot == CLUSTER_CROSSSLOT) { ⏎ pcmd->read_error = CLIENT_READ_CROSS_SLOT;`

## P0195

**GT**（func）Incorrect early exit prevents loading incremental AOF after successful base recovery

> The error handling condition incorrectly treats AOF_BROKEN_RECOVERED as a failure state, causing the function to exit immediately after successfully recovering a corrupted base AOF file. When a base AOF is the last file and gets successfully recovered (ret == AOF_BROKEN_RECOVERED), the server should continue to load any incremental AOF files. However, this bug causes an early exit to cleanup, preventing incremental files from being loaded and potentially losing data. The correct behavior is to only exit on AOF_OPEN_ERR or AOF_FAILED, not on successful recovery.

GT 片段：`if (ret == AOF_OPEN_ERR || ret == AOF_FAILED || ret == AOF_BROKEN_RECOVERED) { ⏎ goto cleanup; ⏎ }`

**finding**（`src/aof.c:1830`，距錨點 11 行）AOF_BROKEN_RECOVERED 在非最後檔案時被視為致命錯誤，但日誌訊息仍稱「truncated」

> 在 `loadAppendOnlyFiles` 中，若 `ret == AOF_BROKEN_RECOVERED` 且不是最後一個檔案，程式會記錄「Fatal error: the truncated file is not the last file」。此處的「truncated」可能造成混淆，因為實際上是格式錯誤後自動截斷。建議調整日誌訊息以區分兩種情況。

finding 片段：`if ((ret == AOF_TRUNCATED || ret == AOF_BROKEN_RECOVERED) && !last_file) { ⏎ ret = AOF_FAILED; ⏎ serverLog(LL_WARNING, "Fatal error: the truncated file is not the last file"); ⏎ }`

## P0196

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行）新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用

> 檔案中定義的 Schedule 型別未加上 export，但後續的 CreateScheduleHandlerReturn 等型別使用了它。若其他檔案需要直接使用 Schedule，將無法匯入。建議將 Schedule 加上 export，或確認其僅供內部使用。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0197

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 20 行）使用 print 而非 logging

> 在 propagate_skip_from_edge 方法中新增了 print 陳述式，違反專案規範  （Backend Code Must Use Logging Instead of Print Statements）。print 會直接輸出到 stdout，無法被日誌系統收集，且可能造成效能問題。應改用 logging 模組，並在模組頂部宣告 logger。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0198

**GT**（func）Incorrect tauri version in metadata file

> The metadata-v2.json file specifies tauri version as "2.8.2" but the actual tauri crate version is "2.8.3" as shown in crates/tauri/Cargo.toml. This version mismatch will cause the CLI to report incorrect version information to tools and scripts that depend on this metadata. The PR updated the tauri version to 2.8.3, but the metadata file was not updated accordingly, creating an inconsistency between the actual library version and the advertised version.

GT 片段：`{ ⏎ "cli.js": { ⏎ "version": "2.8.2", ⏎ "node": ">= 10.0.0"`

**finding**（`crates/tauri-cli/metadata-v2.json:3`，距錨點 0 行）cli.js 版本與 tauri-cli crate 版本不一致

> metadata-v2.json 中的 cli.js 版本從 2.8.1 改為 2.8.2，但 tauri-cli 的 Cargo.toml 版本僅從 2.8.0 升到 2.8.1。這可能導致發布流程中 npm 套件與 Rust crate 版本不匹配，或使用者安裝時取得錯誤的 CLI 版本。請確認此處是否應為 2.8.1，或 tauri-cli 應升到 2.8.2。

finding 片段：`"version": "2.8.2",`

## P0199

**GT**（func）QueryClient instance mismatch between router context and provider

> The Storybook decorator creates a QueryClient instance mismatch. The `createTestRouter` function instantiates a new QueryClient (`new QueryClient()`) and passes it to the router context on line 32. However, the decorator wraps the component with `QueryClientProvider` using the module-level `queryClient` instance on line 43. This creates two separate QueryClient instances - one for the router context and one for the provider. Queries executed within the router tree will use a different cache than queries executed through the provider, causing cache inconsistency and potential state synchronization issues. The router and provider should share the same QueryClient instance.

GT 片段：`return createRouter({ ⏎ routeTree: rootRoute, ⏎ history: createMemoryHistory({ initialEntries: ["/"] }), ⏎ context: { queryClient: new QueryClient() },`

**finding**（`ui-v2/src/components/flows/flow-icon-text/flow-icon-text.stories.tsx:32`，距錨點 0 行）stories 中 queryClient 設定不一致

> 在 `createTestRouter` 中建立了一個新的 `QueryClient` 並放入 router context，但 decorator 中使用的 `QueryClientProvider` 是全域的 `queryClient`。這可能導致測試時 query client 不一致，建議統一使用同一個 instance。

finding 片段：`context: { queryClient: new QueryClient() },`

## P0200

**GT**（rule）New React component added without a co-located test file

> Rule 10 requires React component test files to be co-located with the component. This PR adds `deployment-status-trigger-fields.tsx` but does not add a corresponding `deployment-status-trigger-fields.test.tsx` in the same directory.

GT 片段：`export const DeploymentStatusTriggerFields = () => { ⏎ const form = useFormContext<AutomationWizardSchema>(); ⏎ const posture = useWatch<AutomationWizardSchema>({ name: "trigger.posture" });`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/deployment-status-trigger-fields.tsx:30`，距錨點 3 行）Proactive 模式下使用 trigger.after 欄位，但未提供預設值或驗證

> 當 posture 為 "Proactive" 時，狀態欄位綁定到 `trigger.after`，但此欄位可能未在 schema 中定義或未設定預設值，導致初始值為 `undefined`，`selectedStatus` 為 `undefined`，Select 顯示 placeholder。若使用者未選擇狀態，表單提交時可能缺少必要欄位。建議確認 schema 中 `trigger.after` 的定義，並考慮加入驗證或預設值。

finding 片段：`const statusFieldName = ⏎ posture === "Proactive" ? "trigger.after" : "trigger.expect";`

## P0201

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:63`，距錨點 0 行）start_execution 呼叫時機可能造成狀態不一致

> 在 `enqueue_node` 之前呼叫 `start_execution` 可能導致節點在尚未進入佇列時就被標記為執行中，若後續 `enqueue_node` 失敗，狀態將不一致。建議確認 `start_execution` 的實作是否具冪等性，或調整呼叫順序。

finding 片段：`self._state_manager.start_execution(downstream_node_id) ⏎ self._state_manager.enqueue_node(downstream_node_id)`

## P0202

**GT**（func）Prefix items incorrectly included in sortable context

> The sortableKeys array is constructed from all localKeyedValues instead of excluding prefix items. The code removed the .slice(prefixItemsCount) operation, meaning prefix items (which should have fixed positions and not be draggable) are now included in the SortableContext. This allows prefix items to be moved via drag-and-drop, violating the constraint that prefix items must remain in their fixed positions and breaking the schema's structural requirements.

GT 片段：`// Get the keys of items that can be dragged (non-prefix items) ⏎ const sortableKeys = localKeyedValues.map((item) => item.key);`

**finding**（`ui-v2/src/components/schemas/schema-form-input-array-list.tsx:134`，距錨點 13 行）拖曳排序索引計算未考慮 prefixItems，可能導致資料順序錯誤

> 在 `handleDragEnd` 中，`oldIndex` 和 `newIndex` 是基於 `localKeyedValues` 的完整陣列索引，但 `moveItem` 函式預期的是「可移動項目」的索引（即扣除 prefixItems 後的索引）。當陣列包含 prefixItems 時，這兩個索引會錯位，導致拖曳後資料順序不正確。

例如：prefixItems 有 2 個，使用者將第一個可移動項目（完整索引 2）拖到第二個可移動項目（完整索引 3）的位置，`oldIndex=2`、`newIndex=3`，但 `moveItem(3, 2)` 會嘗試移動可移動項目中的索引 3 和 2，實際上可移動項目只有索引 0 和 1，造成錯誤。

建議：在計算索引時，先扣除 prefixItems 的數量，或改用 `item.key` 直接操作資料陣列。

finding 片段：`const oldIndex = localKeyedValues.findIndex( ⏎ (item) => item.key === active.id, ⏎ ); ⏎ const newIndex = localKeyedValues.findIndex(`

## P0203

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 將 `mark_edge_skipped` 移到 `propagate_skip_from_edge` 之後，可能改變遞迴過程中的邊狀態。若 `propagate_skip_from_edge` 依賴邊尚未被標記為 skipped 的狀態，此變更可能導致錯誤。建議確認此順序變更的必要性。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0204

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:66`，距錨點 11 行）TryGetValidatableParameterInfo 方法格式調整

> 方法簽名從多行改為單行，且大括號位置改變。這僅為格式調整，不影響功能。

finding 片段：`public bool TryGetValidatableParameterInfo(ParameterInfo parameterInfo, [NotNullWhen(true)] out IValidatableInfo? validatableInfo) {`

## P0205

**GT**（func）Incorrect default value for requestReschedule in webhook payload builder

> The BookingPayloadBuilder sets the default value of requestReschedule to true instead of false when the field is not provided. This means any BOOKING_CANCELLED webhook that doesn't explicitly pass requestReschedule will be incorrectly flagged as a reschedule request. This affects all existing code paths that trigger cancellation webhooks without specifying this field, causing webhook consumers to misinterpret normal cancellations as reschedule requests and potentially trigger incorrect business logic, notifications, or automated processes.

GT 片段：`case WebhookTriggerEvents.BOOKING_CANCELLED: ⏎ return this.buildBookingPayload({ ⏎ booking: dto.booking, ⏎ eventType: dto.eventType,`

**finding**（`packages/features/webhooks/lib/factory/versioned/v2021-10-20/BookingPayloadBuilder.ts:48`，距錨點 0 行）requestReschedule 預設值不一致可能導致下游誤判

> 在 v2021-10-20 的 builder 中，`requestReschedule` 使用 `dto.requestReschedule ?? true` 作為預設值，但在 `BookingWebhookFactory` 中則使用 `params.requestReschedule ?? false`。這表示當呼叫端未明確傳入此欄位時，不同版本的 webhook payload 會得到相反的布林值。若下游系統依賴此欄位判斷是否為 reschedule 流程，可能造成行為不一致。建議統一預設值（例如皆為 false），或在所有呼叫點明確傳入。

finding 片段：`requestReschedule: dto.requestReschedule ?? true,`

## P0206

**GT**（func）Incorrect version suffix order in endpoint URL construction

> The frontend code constructs Tinybird endpoint URLs with the version prefix in reverse order compared to the backend. The frontend builds URLs as `v2_api_kpis` (version first) while the backend expects `api_kpis_v2` (version last). This mismatch causes the frontend to call non-existent endpoints when the version config is set, resulting in failed API calls and missing analytics data. The comment correctly describes the pattern as 'api_kpis_v2' but the implementation reverses this to `${config.version}_${endpointName}`.

GT 片段：`// Append version suffix if provided (e.g., "v2" -> "api_kpis_v2") ⏎ const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

**finding**（`apps/admin-x-framework/src/utils/stats-config.ts:18`，距錨點 0 行）版本前綴邏輯與後端不一致，導致端點名稱錯誤

> 此處使用 `config.version ? `${config.version}_${endpointName}` : endpointName`，產生如 `v2_api_kpis` 的端點名稱；但後端 `tinybird.js` 使用 `${pipeName}_${version}`，產生 `api_kpis_v2`。兩者不一致，當前端設定 version 時，會呼叫不存在的端點，導致 API 404。

建議統一命名規則，例如都使用後綴方式，或在此處改為 `${endpointName}_${config.version}`。

finding 片段：`const finalEndpointName = config.version ? `${config.version}_${endpointName}` : endpointName;`

## P0207

**GT**（func）Incorrect sequence validation for multiple generic components

> The test validates deserialization of multiple closed generic components but checks that both descriptors have sequence number 0 instead of verifying that the second descriptor has sequence number 1. Component descriptors in a collection must have sequential ordering starting from 0, and this test should verify the second component has sequence 1. This incorrect assertion fails to validate proper sequence ordering, which is critical for component initialization and rendering order in Blazor.

GT 片段：`var secondDescriptor = descriptors[1]; ⏎ Assert.Equal(typeof(GenericTestComponent<string>).FullName, secondDescriptor.ComponentType.FullName); ⏎ Assert.Equal(0, secondDescriptor.Sequence);`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 18 行）使用 Convert.ToInt64 可能隱藏型別資訊

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64` 將參數值轉換為 long，但未驗證參數值的原始型別。這可能導致測試無法偵測到反序列化過程中型別資訊的遺失或錯誤。建議先斷言參數值的型別（例如 `Assert.IsType<JsonElement>(parameters["Value"])`），再進行數值比較。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0208

**GT**（rule）Unused local constant triggers SwiftLint unused_variable

> A new local constant `isLandscape` is introduced but never used in `setupSkeletonAddressBarsLayout()`. This is a definitive SwiftLint violation (typically `unused_variable` / `unused_declaration`) and will fail linting.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）使用已棄用的 statusBarOrientation API

> `UIApplication.shared.statusBarOrientation` 在 iOS 13 已棄用，建議改用 `view.window?.windowScene?.interfaceOrientation` 或 `traitCollection.verticalSizeClass` 來判斷方向。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0209

**GT**（func）Edge marked as skipped after recursive propagation breaks skip chain

> In `_propagate_skip_to_node`, the edge is marked as skipped AFTER the recursive call to `propagate_skip_from_edge`. During the recursive propagation, the edge state is still UNKNOWN rather than SKIPPED. The `propagate_skip_from_edge` method analyzes incoming edge states and stops processing if any edge is UNKNOWN (line 56). This causes the skip propagation to terminate prematurely, leaving downstream nodes in an incorrect state instead of properly propagating the skip status through the entire dependency chain.

GT 片段：`outgoing_edges = self._graph.get_outgoing_edges(node_id) ⏎ for edge in outgoing_edges: ⏎ # Recursively propagate skip ⏎ self.propagate_skip_from_edge(edge.id)`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:85`，距錨點 0 行）mark_edge_skipped 呼叫順序變更可能影響遞迴邏輯

> 在 _propagate_skip_to_node 中，原本先 mark_edge_skipped 再 propagate_skip_from_edge，現在順序對調。若 propagate_skip_from_edge 內部依賴邊的 skipped 狀態（例如 analyze_edge_states 會檢查），則可能導致行為不同。需確認此變更是否為修正所需，並驗證遞迴邏輯仍正確。

finding 片段：`self.propagate_skip_from_edge(edge.id) ⏎ self._state_manager.mark_edge_skipped(edge.id)`

## P0210

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:280`，距錨點 21 行）orgId 過濾條件可能排除應包含的團隊

> 在 `getTeamsWithPBACPermissions` 的第一個 UNION 分支中，過濾條件為 `(t."id" = ${orgId} OR t."parentId" = ${orgId})`。這表示當 `orgId` 指定為某個組織 ID 時，只會回傳該組織本身及其直接子團隊。但若團隊階層超過兩層（例如組織 → 部門 → 子團隊），則更深層的子團隊將不會被包含。這可能導致使用者無法看到其應有權限的 bookings。

建議確認團隊階層的深度，若可能超過兩層，應改用遞迴 CTE 或調整過濾邏輯以包含所有後代團隊。

finding 片段：`AND (${orgId}::bigint IS NULL OR t."id" = ${orgId} OR t."parentId" = ${orgId})`

## P0211

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0212

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）記憶體洩漏：createStringObjectFromLongLong 建立的物件未釋放

> 在傳播 HPEXPIREAT 時，`argv[2] = createStringObjectFromLongLong(expireat);` 建立了一個新的 robj，但在 `alsoPropagate` 之後沒有對其進行 `decrRefCount`。這會導致每次執行此路徑時洩漏一個 robj 的記憶體。

建議在 `alsoPropagate` 呼叫後加入 `decrRefCount(argv[2]);` 或使用 stack 分配的 robj 並設定 refcount。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

## P0213

**GT**（func）parseInt without radix causes NaN values in threshold field

> In WorkPoolStatusTriggerFields, the threshold input's onChange handler uses `parseInt(e.target.value)` without specifying a radix parameter. When users clear the threshold field, parseInt returns NaN instead of a number, which gets set as the form value. This breaks form validation and can cause runtime errors when the automation is saved. Additionally, parseInt will silently truncate decimal inputs (e.g., 1.5 becomes 1) rather than properly handling invalid input, and without the radix parameter it may misinterpret values with leading zeros as octal numbers in older JavaScript environments.

GT 片段：`<Input ⏎ type="number" ⏎ min={1} ⏎ {...field}`

**finding**（`ui-v2/src/components/automations/automations-wizard/trigger-step/work-pool-status-trigger-fields.tsx:78`，距錨點 0 行）數字輸入處理不一致：使用 parseInt 而非 Number

> 在 `work-pool-status-trigger-fields.tsx` 中，Threshold 欄位的 `onChange` 使用 `parseInt(e.target.value)`，而其他元件（如 `custom-trigger-fields.tsx`）使用 `Number(e.target.value)`。`parseInt` 會忽略非數字字元（例如輸入 "12abc" 會得到 12），可能導致非預期行為。建議統一使用 `Number` 並搭配驗證。

finding 片段：`onChange={(e) => field.onChange(parseInt(e.target.value))}`

## P0214

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，但原文仍包含該變數。這可能導致使用者看不到具體的新聞信名稱，影響理解。建議保留變數。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0215

**GT**（func）Missing null check for max_length causes runtime error in batch validation

> The batch input validation logic at line 260 checks if a string exceeds max_length without verifying that max_length is defined. When max_length is undefined (which is now allowed after removing DEFAULT_VALUE_MAX_LEN), the comparison 'item[varIndex].length > varItem.max_length' will compare against undefined, resulting in a TypeError. This breaks batch file upload validation and prevents users from running batch operations when variables don't have explicit max_length values set.

GT 片段：`promptConfig?.prompt_variables.forEach((varItem, varIndex) => { ⏎ if (errorRowIndex !== 0) ⏎ return ⏎ if (varItem.type === 'string') {`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）當 max_length 未定義時，比較邏輯可能失效

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 提供預設值，移除後若 `varItem.max_length` 為 undefined，則 `item[varIndex].length > varItem.max_length` 會變成 `length > undefined`，結果為 false，導致長度檢查失效。應保留預設值或明確處理 undefined 情況。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0216

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）React Scan 載入失敗時僅回傳空元件，使用者無法察覺 devtools 未啟動

> 在 `lazy` 的 `catch` 中，回傳 `{ default: () => null }`，這會讓 `ReactScan` 元件渲染為空。如果動態載入失敗（例如網路問題或 chunk 載入錯誤），使用者將看不到任何 devtools 功能，且沒有任何視覺提示，可能誤以為 devtools 正常運作。建議在 catch 中回傳一個顯示錯誤狀態的元件，或至少保留錯誤 log（目前已有 `console.error`，但使用者看不到）。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0217

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能導致執行時期錯誤

> 此函式僅驗證 name 為非空字串，但未驗證 schedule 的結構（應為 { start: Date; end: Date }[][]）及 eventTypeId 的型別（應為 number）。若呼叫端傳入錯誤格式的資料，可能導致後續 API 呼叫失敗或產生難以除錯的錯誤。建議使用 Zod 或更完整的型別檢查來驗證輸入。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0218

**GT**（rule）Direct UIApplication.shared usage instead of protocol

> The code directly accesses UIApplication.shared.statusBarOrientation instead of using a protocol abstraction (e.g., ApplicationProtocol), making the code difficult to test in isolation and violating the dependency injection pattern used throughout the codebase.

GT 片段：`// Check if the interface is in landscape mode for layout adjustments ⏎ let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/AddressToolbarContainer.swift:465`，距錨點 0 行）未使用的變數 isLandscape

> 在 setupSkeletonAddressBarsLayout 中新增了 isLandscape 變數，但並未在後續程式碼中使用。這可能是開發中的殘留，應移除或實際使用。

finding 片段：`let isLandscape = UIApplication.shared.statusBarOrientation.isLandscape`

## P0219

**GT**（func）Incomplete orgId filtering in PBAC child team query

> In the SQL query for getTeamsWithPBACPermissions, the WHERE clause for child teams is missing a check for child."parentId" = ${orgId}. The original PR added this condition to properly scope child teams when an orgId is provided, but this implementation only checks org."id" and child."id", missing the case where a child team's parent should match the orgId. This causes the query to incorrectly exclude child teams whose parentId matches the specified orgId, breaking the inheritance model where organization permissions should propagate to child teams.

GT 片段：`SELECT DISTINCT child."id" ⏎ FROM "Membership" m ⏎ INNER JOIN "Role" r ON m."customRoleId" = r.id ⏎ INNER JOIN "Team" org ON m."teamId" = org.id`

**finding**（`packages/features/pbac/infrastructure/repositories/PermissionRepository.ts:309`，距錨點 0 行）orgId 過濾條件在 UNION 分支中不一致

> 在 `getTeamsWithPBACPermissions` 的第二個 UNION 分支中，過濾條件為 `(org."id" = ${orgId} OR child."id" = ${orgId})`，但未包含 `child."parentId" = ${orgId}`。這可能導致當 `orgId` 指定為某個父團隊時，其子團隊不會被包含在結果中。

請確認此處的意圖，並與第一個分支的過濾邏輯保持一致。

finding 片段：`AND (${orgId}::bigint IS NULL OR org."id" = ${orgId} OR child."id" = ${orgId})`

## P0220

**GT**（func）Zod schema validation replaced with unsafe manual validation

> The original code used proper Zod schemas (ZCreateInputSchema with z.ZodType<TCreateInputSchema>) for type-safe validation. The new validateCreateScheduleInput function performs only basic manual runtime checks without Zod's comprehensive validation capabilities. This violates Repository Rule #5 which requires schema files to export both TypeScript types AND corresponding Zod schemas, and handlers should use these typed schemas for validation. The manual validation also lacks proper validation for the optional schedule and eventTypeId fields, and doesn't validate the structure of nested objects like the schedule array.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 0 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0221

**GT**（rule）Validation logic mixed with schema types

> The rule requires that schema files contain only TypeScript types and Zod schemas, while handler logic should be in separate handler files. However, the validateCreateScheduleInput function (which is handler/validation logic) has been placed directly in the types.ts schema file, mixing schema definitions with handler logic.

GT 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 37 行）新增檔案缺少 export 修飾詞，可能導致型別無法被外部使用

> 檔案中定義的 Schedule 型別未加上 export，但後續的 CreateScheduleHandlerReturn 等型別使用了它。若其他檔案需要直接使用 Schedule，將無法匯入。建議將 Schedule 加上 export，或確認其僅供內部使用。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0222

**GT**（rule）Possible undefined used as number (max_length) under strict TS

> Under strict TypeScript settings, `varItem.max_length` is likely typed as an optional value (e.g., `number | undefined`). It is used directly in a numeric comparison (`length > varItem.max_length`) and assigned to `maxLength` without a fallback/null check, which will fail strict type checking (and can lead to runtime NaN comparison behavior when undefined).

GT 片段：`if (item[varIndex].length > varItem.max_length) { ⏎ moreThanMaxLengthVarName = varItem.name ⏎ maxLength = varItem.max_length ⏎ errorRowIndex = index + 1`

**finding**（`web/app/components/share/text-generation/index.tsx:261`，距錨點 0 行）移除預設 max_length 後可能導致無限制輸入

> 原本使用 `varItem.max_length || DEFAULT_VALUE_MAX_LEN` 作為長度上限，現在改為直接使用 `varItem.max_length`。若後端未提供 `max_length`（例如舊資料或未設定），則 `varItem.max_length` 為 `undefined`，比較 `item[varIndex].length > undefined` 會得到 `false`，因此不會觸發長度錯誤，等同於無限制。請確認後端是否保證提供 `max_length`，或在前端保留預設值作為 fallback。

finding 片段：`if (item[varIndex].length > varItem.max_length) {`

## P0223

**GT**（func）Type mismatch in availability.days changes number[] to string[]

> The days field in GetAvailabilityListHandlerReturn has been changed from number[] to string[]. Days of the week are conventionally represented as numbers (0-6 for Sunday-Saturday or 1-7 for Monday-Sunday) throughout calendar and scheduling systems. This type change will break any code that iterates over days for date calculations, comparisons with Date.getDay(), or bitwise operations for day-of-week checks. Components consuming this data will fail when attempting to use the days array for schedule calculations or when mapping days to calendar views.

GT 片段：`export type GetAvailabilityListHandlerReturn = { ⏎ schedules: (Omit<Schedule, "userId"> & { ⏎ availability: { ⏎ id: number;`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:1`，距錨點 15 行）Schedule 型別缺少部分欄位，可能與實際 API 回應不符

> 新定義的 Schedule 型別僅包含 id、userId、name、timeZone，但原 trpc 的 Schedule 型別可能包含更多欄位（如 availability 等）。若 API 回應包含額外欄位，此型別仍可相容（多餘欄位會被忽略），但若使用此型別進行操作（如更新）可能遺漏必要欄位。建議確認實際 API 回應結構，補齊必要欄位。

finding 片段：`type Schedule = { ⏎ id: number; ⏎ userId: number; ⏎ name: string;`

## P0224

**GT**（rule）Throws generic Error instead of typed/custom error

> Rule 10 forbids throwing generic `Error` objects and requires structured/typed custom error classes (e.g., extending a base error type with codes/status/context). The added validation throws plain `Error` instances.

GT 片段：`throw new Error('Invalid input: must be an object'); ⏎ ... ⏎ throw new Error('Invalid input: name must be a non-empty string');`

**finding**（`packages/platform/atoms/hooks/schedules/types.ts:38`，距錨點 2 行）validateCreateScheduleInput 驗證不足，可能讓無效資料進入 API

> 此函式僅檢查 `name` 是否為非空字串，未驗證 `schedule` 和 `eventTypeId` 的型別與格式。若呼叫端傳入錯誤型別（例如 `schedule` 不是二維陣列或元素不是 {start, end}），可能導致後續 API 呼叫失敗或產生非預期行為。建議使用 zod 或其他驗證函式庫完整驗證輸入，或至少手動檢查每個欄位。

finding 片段：`export function validateCreateScheduleInput(input: unknown): CreateScheduleInput { ⏎ if (!input || typeof input !== 'object') { ⏎ throw new Error('Invalid input: must be an object'); ⏎ }`

## P0225

**GT**（func）Email trimming creates validation and display inconsistency

> The form now trims the email on submission but validates and displays the untrimmed version. If a user enters ' user@example.com ' (with spaces), the validator checks the untrimmed email which passes validation (spaces don't invalidate the regex), but the API receives 'user@example.com' (trimmed). This creates confusion where the displayed email in the UI doesn't match what was actually submitted, and could cause issues if the user needs to verify what they signed up with. The trim should either be applied before validation and reflected in the display, or not applied at all.

GT 片段：`const submitHandler: FormEventHandler<HTMLFormElement> = (e) => { ⏎ e.preventDefault(); ⏎ onSubmit({email: email.trim()}); ⏎ };`

**finding**（`apps/signup-form/src/components/pages/form-view.tsx:56`，距錨點 0 行）email.trim() 可能改變既有行為並影響驗證邏輯

> 在 submitHandler 中將 email 傳遞前加上 trim()，這會移除前後空白。若原本允許使用者輸入含空白的 email（例如複製貼上時），此變更可能導致驗證失敗或行為不一致。此外，若後端或驗證邏輯依賴原始輸入，可能造成非預期結果。建議確認此變更為預期行為，並補充測試涵蓋空白輸入情境。

finding 片段：`onSubmit({email: email.trim()});`

## P0226

**GT**（func）Using Math.floor instead of Math.round produces consistently lower warmup limits

> The warmup limit calculation uses Math.floor instead of Math.round to compute the daily email limit. This systematically underestimates the intended limits throughout the warmup period. For exponential growth calculations, proper rounding is critical - when the formula produces values like 237.6, Math.floor gives 237 while Math.round would give 238. Over a 42-day warmup period, this accumulates significant deviation from the intended warmup curve, making the warmup more conservative than designed and potentially extending the effective time needed to reach full sending capacity. This undermines the carefully calculated exponential progression from 200 to 200,000 emails.

GT 片段：`const limit = Math.floor( ⏎ this.#warmupConfig.start * ⏎ Math.pow( ⏎ this.#warmupConfig.end / this.#warmupConfig.start,`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:85`，距錨點 4 行）暖機完成後回傳 Infinity 可能導致非預期行為

> 在 `getWarmupLimit` 中，當 `day > totalDays` 時回傳 `Infinity`。這會使呼叫端在執行 `Math.min(emailCount, Infinity)` 時得到 `emailCount`，看似正確，但若呼叫端未預期到 `Infinity` 值，可能導致後續計算錯誤或型別問題。建議改為回傳 `emailCount`，或明確回傳一個極大值（如 `Number.MAX_SAFE_INTEGER`），並在文件或型別上說明。

finding 片段：`if (day > this.#warmupConfig.totalDays) { ⏎ return Infinity ⏎ }`
