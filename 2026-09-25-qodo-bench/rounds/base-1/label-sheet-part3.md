# 盲標單：finding 跟 GT 是不是同一個問題

判準（Martian）：**一個 code change 能同時修掉兩者**才算 `same`；同處、相關但講的是別的問題算 `partial`；否則 `no`。
本單刻意不含 confidence、severity。標在 `labels.csv`：`pair,label,note`。

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
