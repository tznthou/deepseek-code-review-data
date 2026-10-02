# 盲標單 4：finding 跟標準答案（GT）是不是同一個問題

判準（Martian）：
- `same`：**一個 code change 能同時修掉兩者**。finding 只抓到問題的一半、或嚴重度講錯但修法相同，仍算 `same`
- `partial`：同一處、相關，但講的是別的問題；或指對地方但講錯機制
- `no`：其他情況；同一行上兩個互相獨立的缺陷也算 `no`

規則：
- 只讀這一份檔案，不要讀同目錄或其他目錄的任何檔案
- 每一組都要標，不要跳過；看不出來就依判準選最接近的一個，在 note 寫原因
- 把結果寫成 CSV：`<repo>/.claude/experiments/2026-09-30-function-context/blind/labels-part4.csv`，第一行是 `pair,label,note`，每組一行（label 只能是 same／partial／no；note 可空，含逗號就用雙引號包起來）

---
## P0301

**GT**（func）Memory leak in HPEXPIREAT propagation

> The code creates a new string object via createStringObjectFromLongLong(expireat) and stores it in argv[2], but fails to call decrRefCount(argv[2]) after propagating the command. This causes a memory leak every time HINCRBYFLOAT is executed on a field with an expiration time. Over time, repeated calls will accumulate leaked string objects, gradually consuming server memory and potentially leading to out-of-memory conditions.

GT 片段：`argv[2] = createStringObjectFromLongLong(expireat); ⏎ argv[3] = shared.fields; ⏎ argv[4] = shared.integers[1]; ⏎ argv[5] = c->argv[2];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）手動傳播 HPEXPIREAT 時未處理 createStringObjectFromLongLong 可能失敗的情況

> `createStringObjectFromLongLong(expireat)` 可能因為記憶體不足而回傳 NULL，但程式碼未檢查就直接指派給 argv[2]，後續 alsoPropagate 可能對 NULL 物件進行操作，導致崩潰。

失敗情境：在記憶體極度不足時，執行 HINCRBYFLOAT 且欄位有過期時間。

建議修正：檢查回傳值，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0302

**GT**（func）Auto-increment version code lacks maximum value validation

> The auto-increment feature increments the version code using saturating_add(1) without validating against Android's maximum version code limit of 2,100,000,000. When auto-increment is enabled and the version code approaches or exceeds this limit through repeated builds, it will produce invalid version codes that violate Android platform constraints. This causes silent corruption of the version code until it eventually triggers build failures. The semver-derived path has proper validation (lines 652-661), but the auto-increment path bypasses all validation checks.

GT 片段：`let new_version_code = last_version_code.map(|v| v.saturating_add(1)).unwrap_or(1); ⏎ app_tauri_properties.push(format!("tauri.android.versionCode={new_version_code}"));`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:652`，距錨點 6 行）dev 模式下 versionCode 的 clamp 順序可能導致非預期結果

> 在 dev 模式下，程式先檢查 `version_code == 0` 和 `> 2100000000` 並回傳錯誤，然後才執行 `clamp(1, 2100000000)`。這表示如果 semver 計算出的 `version_code` 超過上限，dev 模式會直接失敗，而不是被 clamp 到上限。原本在 `tauri-build` 中的邏輯是先 clamp 再檢查，行為可能不一致。建議確認預期行為，並調整順序或移除重複檢查。

finding 片段：`if version_code == 0 { ⏎ crate::error::bail!( ⏎ "You must change the `version` in `tauri.conf.json`. The default value `0.0.0` is not allowed for Android package and must be at least `0.0.1`." ⏎ );`

## P0303

**GT**（rule）Unused parameter `index` in map callback

> `index` is declared but never used in the `visibleItems.map` callback, which will trigger a Biome/TS lint warning (unused variable). The pre-commit hook rule requires lint to pass with `--error-on-warnings`.

GT 片段：`{visibleItems.map((item, index) => ( ⏎ <Badge key={item.label} variant={item.variant || "gray"} onClick={item.onClick}> ⏎ {item.label} ⏎ </Badge>`

**finding**（`apps/web/components/ui/LimitedBadges.tsx:69`，距錨點 0 行）Popover 的 hover 與 click 互動可能導致無法關閉

> 在桌面端，Popover 的開啟由 onMouseEnter 觸發，關閉由 onMouseLeave 觸發。但 Popover 本身也受 onOpenChange 控制，當使用者點擊 trigger 按鈕時，Popover 會切換 open 狀態，但 mouse enter/leave 事件可能不會如預期觸發，導致 popover 卡在開啟狀態。建議移除自訂的 mouse enter/leave 處理，改用 Popover 內建的 hover 模式（例如設定 trigger="hover"），或明確處理 click 與 hover 的狀態轉換。

finding 片段：`onMouseEnter={handleMouseEnter} ⏎ onMouseLeave={handleMouseLeave}>`

## P0304

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 2 行）測試依賴真實網路，可能不穩定

> `captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或不穩定，導致測試逾時或失敗。

建議改用本地 HTML 字串或 `data:` URL 來避免外部依賴，或使用 `WKWebView` 的 `loadHTMLString` 方法。

finding 片段：`webView.load(URLRequest(url: url))`

## P0305

**GT**（rule）Line exceeds Biome configured line width

> The codebase formatting rule specifies a 110 character line width. This added line is clearly longer than 110 characters (chained call with long template literal), violating the configured formatting constraints.

GT 片段：`+      const first = await request(app.getHttpServer()).post(`/v2/teams/${team.id}/invite`).expect(200);`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.e2e-spec.ts:73`，距錨點 2 行）測試未驗證邀請連結的實際可用性

> 測試僅檢查 token 長度大於 0 且 inviteLink 包含 token，但未驗證該 token 是否真的存在於資料庫且未過期。建議加入後續使用該 token 加入團隊的測試，以確保邀請流程完整。

finding 片段：`expect(response.body.data.token.length).toBeGreaterThan(0); ⏎ expect(response.body.data.inviteLink).toEqual(expect.any(String)); ⏎ expect(response.body.data.inviteLink).toContain(response.body.data.token);`

## P0306

**GT**（func）Incorrect type conversion in generic component parameter assertion

> The test validates a generic component with an int type parameter but uses Convert.ToInt64 instead of Convert.ToInt32 to assert the parameter value. Since the parameter is defined as int (System.Int32) in GenericTestComponent<int>, this creates a type mismatch. The assertion compares a long (Int64) value to the expected int (Int32) value 42, which will cause the test to fail even though the component deserialization is working correctly. This breaks the validation logic for generic component parameters.

GT 片段：`var parameters = deserializedDescriptor.Parameters.ToDictionary(); ⏎ Assert.Single(parameters); ⏎ Assert.Contains("Value", parameters.Keys); ⏎ Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

**finding**（`src/Components/Server/test/Circuits/ServerComponentDeserializerTest.cs:124`，距錨點 0 行）參數值轉換使用 Convert.ToInt64 可能隱藏型別問題

> 在 `CanParseSingleMarkerForClosedGenericComponentWithParameters` 測試中，使用 `Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture)` 來驗證參數值。如果實際反序列化的值是 `JsonElement` 或其他型別，`Convert.ToInt64` 可能成功轉換，但無法驗證型別是否正確。建議直接斷言型別為 `JsonElement` 並取得其值，或使用 `Assert.IsType<long>` 等更精確的斷言。

finding 片段：`Assert.Equal(42, Convert.ToInt64(parameters["Value"]!, CultureInfo.InvariantCulture));`

## P0307

**GT**（rule）Unused local variable triggers -Werror build failure

> The newly introduced local variable `orig_active_defrag` is never used, which will trigger an `-Wunused-variable` warning. With `-Werror`, this becomes a compilation error, violating the rule that the build must compile cleanly with warnings treated as errors.

GT 片段：`int orig_active_defrag = server.active_defrag_enabled; ⏎ server.active_defrag_enabled = 0; ⏎ emptyData(-1, empty_db_flags, replicationEmptyDbCallback); ⏎ /* Restore the original active defragmentation setting. */`

**finding**（`src/replication.c:1961`，距錨點 0 行）無條件將 active_defrag_enabled 設為 1，可能意外啟用 defrag

> 在 `rdbLoadEmptyDbFunc` 中，程式碼先將 `server.active_defrag_enabled` 設為 0，呼叫 `emptyData` 後再無條件設為 1。如果原本 `active_defrag_enabled` 為 0（例如使用者透過設定停用 defrag），此函式會錯誤地啟用 defrag，可能導致非預期的記憶體重整行為，甚至影響效能或穩定性。

建議改為儲存原始值並在最後恢復：
```c
int orig_active_defrag = server.active_defrag_enabled;
server.active_defrag_enabled = 0;
emptyData(-1, empty_db_flags, replicationEmptyDbCallback);
server.active_defrag_enabled = orig_active_defrag;
```

finding 片段：`/* Restore the original active defragmentation setting. */ ⏎ server.active_defrag_enabled = 1;`

## P0308

**GT**（func）Description field incorrectly trims whitespace

> The work pool edit form now calls .trim() on the description before saving (line 42). This removes any intentional leading or trailing whitespace that users may want to preserve in their work pool descriptions, such as indented text or formatting for markdown. The original PR correctly converted empty strings to null using `||`, but the added .trim() operation inappropriately modifies user input. This breaks the principle of preserving user data as-is unless there's a specific business requirement.

GT 片段：`const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool( ⏎ { ⏎ name: workPool.name,`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:42`，距錨點 0 行）description 可能為 undefined 導致型別不符

> 在 `handleSubmit` 中，`data.description?.trim()` 的結果可能為 `undefined`，但後續將 `trimmedDescription === "" ? null : trimmedDescription` 指派給 `description`。若 `data.description` 為 `undefined`，則 `trimmedDescription` 為 `undefined`，最終 `description` 會是 `undefined`，但 `WorkPoolUpdate` 型別可能預期 `string | null`。建議明確處理 `undefined` 情況，例如使用 `data.description?.trim() ?? null`。

finding 片段：`const trimmedDescription = data.description?.trim(); ⏎ updateWorkPool( ⏎ { ⏎ name: workPool.name,`

## P0309

**GT**（rule）Strict mode disabled in TypeScript config

> The rule requires TypeScript configuration files to have 'strict' set to true in compilerOptions, but it was set to false

GT 片段：`/* Linting */ ⏎ "strict": false, ⏎ "noUnusedLocals": true,`

**finding**（`apps/activitypub/tsconfig.json:18`，距錨點 0 行）關閉 TypeScript strict 模式可能隱藏型別錯誤

> 將 `strict` 從 `true` 改為 `false` 會降低型別安全性，可能導致未處理的 null/undefined 或型別錯誤在編譯期未被發現。這與專案原本的嚴格模式慣例相違背，且可能引入潛在的 runtime 錯誤。建議恢復 `strict: true`，並修正任何因此產生的型別錯誤。

finding 片段：`"strict": false,`

## P0310

**GT**（rule）Async test method missing Async suffix

> This method returns Task and is marked async, but its name does not end with the required 'Async' suffix.

GT 片段：`public async Task SupportsRouteParametersFromControllers()`

**finding**（`src/OpenApi/test/Microsoft.AspNetCore.OpenApi.SourceGenerators.Tests/OperationTests.Controllers.cs:141`，距錨點 40 行）測試方法缺少 Arrange/Act/Assert 結構，且未驗證 Summary

> 測試 `SupportsRouteParametersFromControllers` 直接驗證 `path.Parameters[0].Description`，但未驗證 Summary 是否正確。若 PR 同時修改了 Summary 行為，此測試可能無法捕捉回歸。建議增加對 Summary 的斷言。

finding 片段：`Assert.Equal("The id of the user.", path.Parameters[0].Description);`

## P0311

**GT**（func）Incorrect UI element verification for light theme selection

> After selecting light theme mode via Action.SelectLightTheme, the test verifies the wrong UI element by checking darkThemeView instead of lightThemeView. This causes the test to validate dark theme selection state when it should be verifying light theme was properly selected. The bug means the test will fail when light theme is correctly selected (darkThemeView will be '0' not '1'), or pass incorrectly if light theme selection fails but dark theme happens to be selected.

GT 片段：`// Select Light mode ⏎ navigator.performAction(Action.SelectLightTheme) ⏎ let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value ⏎ XCTAssertEqual(lightIsSelected as? String, "1")`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/DisplaySettingsTests.swift:53`，距錨點 0 行）斷言目標從 lightThemeView 改為 darkThemeView，可能導致測試失效

> 在 testCheckSystemThemeChanges 中，原本在選擇 Light 模式後檢查 lightThemeView 的值，現在改為檢查 darkThemeView 的值。若 darkThemeView 在 Light 模式下不存在或值不為 "1"，測試將失敗。請確認此變更是否為有意修正，並確保測試仍能正確驗證主題切換。

finding 片段：`let lightIsSelected = app.buttons[AccessibilityIdentifiers.Settings.Appearance.darkThemeView].value`

## P0312

**GT**（rule）UI constants not in UX struct

> The rule requires UI constants and magic numbers to be organized within a dedicated nested UX struct, but the button size constant (40) is hardcoded directly in the constraint definitions instead of being defined in a private struct UX.

GT 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

**finding**（`firefox-ios/Client/Frontend/Browser/DownloadHelper/DownloadToast.swift:192`，距錨點 0 行）移除 UX 常數改用魔法數字 40

> 原本使用 UX.buttonSize 常數，現在直接寫死 40。若未來需要調整按鈕大小，需修改多處。建議保留常數或使用有意義的名稱。

finding 片段：`closeButton.heightAnchor.constraint(equalToConstant: 40), ⏎ closeButton.widthAnchor.constraint(equalToConstant: 40),`

## P0313

**GT**（func）File permissions set before file creation causes failure

> In the `write_and_make_executable` function, the order of operations was reversed - `fs::set_permissions` is now called before `fs::write`. This attempts to set Unix permissions on a file that doesn't exist yet, which will fail with a "file not found" error. Every call to this function will fail, breaking the entire bundling process for AppImage. All tools (AppRun, linuxdeploy, GTK plugin, GStreamer plugin) that rely on this function to be written and made executable will fail to be prepared, making AppImage bundling completely non-functional.

GT 片段：`fn write_and_make_executable(path: &Path, data: &[u8]) -> Result<(), FileWriteError> { ⏎ use std::os::unix::fs::PermissionsExt; ⏎ fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:312`，距錨點 0 行）write_and_make_executable 中先設定權限再寫入檔案，可能導致權限設定失敗或檔案內容被覆蓋

> 在 `write_and_make_executable` 函式中，原本的順序是先寫入檔案再設定權限，但此 PR 將其反轉為先設定權限再寫入。這會造成兩個問題：
1. 如果 `fs::set_permissions` 失敗（例如檔案不存在），函式會回傳錯誤，但此時檔案尚未寫入，可能導致後續流程中斷。
2. 如果 `fs::write` 成功，它會以預設權限建立或覆蓋檔案，使得先前設定的 0o770 權限失效，最終檔案權限可能不是預期的 0o770。

建議恢復原本的順序：先 `fs::write`，再 `fs::set_permissions`。

finding 片段：`fs::set_permissions(path, fs::Permissions::from_mode(0o770)).map_err(FileWriteError::Permissions)?; ⏎ fs::write(path, data).map_err(FileWriteError::Write)?;`

## P0314

**GT**（func）Incorrect operation order causes potential data loss during cluster verification

> The verifyClusterConfigWithData() function executes clusterDeleteKeysInUnownedSlots() before clusterClaimUnassignedSlots(). This reverses the intended logic: the function should first claim ownership of unassigned slots that contain keys (preventing orphaned data), then delete keys from slots that are genuinely owned by other nodes. With this bug, keys in unassigned slots may be incorrectly deleted before the node has a chance to claim ownership, resulting in permanent data loss during cluster startup or recovery scenarios.

GT 片段：`/* Delete keys in unowned slots */ ⏎ clusterDeleteKeysInUnownedSlots(); ⏎ /* Take over slots that we have keys for, but are assigned to no one. */ ⏎ clusterClaimUnassignedSlots();`

**finding**（`src/cluster.c:2167`，距錨點 35 行）clusterDeleteKeysInUnownedSlots 中 clusterDelKeysInSlot 的參數可能導致資料遺失

> 在 clusterDeleteKeysInUnownedSlots 中呼叫 `clusterDelKeysInSlot(i, 0)`。第二個參數的語意需要確認：若為 `save` 旗標，傳 0 可能表示不保存，但若為其他語意（例如是否為 async），可能導致錯誤。請檢查 clusterDelKeysInSlot 的定義，確保傳入正確的參數。

finding 片段：`clusterDelKeysInSlot(i, 0);`

## P0315

**GT**（func）Threshold boundary values skip their designated scaling tier

> The loop uses `<` instead of `<=` when comparing lastCount to threshold limits. This causes exact boundary values (1000, 5000, 100000, 400000) to incorrectly skip their tier and fall through to the next scaling factor or the fallback logic. For example, a site with exactly 1000 previous emails will bypass the 1.25× tier and incorrectly use 1.5× scaling (getting 1500 instead of 1250). Similarly, 5000 will use 1.75× instead of 1.5×, and 100000 will use 2× instead of 1.75×. This creates unexpected jumps in scaling at precisely the documented threshold boundaries.

GT 片段：`for (const threshold of WARMUP_SCALING_TABLE.thresholds.sort((a, b) => a.limit - b.limit)) { ⏎ if (lastCount < threshold.limit) { ⏎ return Math.ceil(lastCount * threshold.scale); ⏎ }`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:101`，距錨點 30 行）`findPage` 回傳值可能未定義 `data` 屬性，導致執行時期錯誤

> `#getHighestCount` 改為呼叫 `findPage` 後，直接存取 `result.data.length`。若 `findPage` 的實作在某些情況下（例如資料庫錯誤、回傳格式不符）未提供 `data` 陣列，將拋出 `TypeError`。建議先檢查 `result` 與 `result.data` 是否存在，或使用選用鏈結（`result?.data?.length`）並提供預設值。

finding 片段：`const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC', ⏎ limit: 1`

## P0316

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:32`，距錨點 17 行）webView 可能為 null 時使用 !! 強制解參考

> 在 `handleOnBackPressed` 中，當 `webView?.canGoBack() == true` 時，使用 `this@AppPlugin.webView!!.goBack()`。雖然 `load` 方法會在 WebView 載入時設定 `webView`，但若 callback 在 `load` 之前被觸發（例如 activity 初始化期間），`webView` 可能仍為 null，導致 NPE。

建議使用安全呼叫或明確檢查 null。

finding 片段：`this@AppPlugin.webView!!.goBack()`

## P0317

**GT**（func）Swapped answer price unit values causing incorrect billing calculations

> In the create_agent_thought method, the answer_unit_price and answer_price_unit values are swapped. The answer_unit_price is initialized to Decimal('0.001') instead of Decimal(0), while answer_price_unit is initialized to Decimal(0) instead of Decimal('0.001'). This mirrors the correct initialization pattern used for message_unit_price and message_price_unit but with reversed values. This will cause incorrect pricing calculations when computing the total cost of agent responses, potentially leading to billing discrepancies or revenue loss.

GT 片段：`answer="", ⏎ observation="", ⏎ answer_token=0, ⏎ answer_unit_price=Decimal("0.001"),`

**finding**（`api/core/agent/base_agent_runner.py:319`，距錨點 3 行）message_unit_price 與 answer_price_unit 的預設值可能與既有資料不一致

> 在 create_agent_thought 中，`message_unit_price` 由 `0` 改為 `Decimal(0)`，`message_price_unit` 由 `0` 改為 `Decimal("0.001")`，`answer_unit_price` 由 `0` 改為 `Decimal("0.001")`，`answer_price_unit` 由 `0` 改為 `Decimal(0)`。這些變更可能影響計費邏輯，且與模型定義中的 server_default 不完全一致。

失敗情境：若既有資料依賴舊的預設值，可能導致計算錯誤或顯示異常。

建議：確認這些預設值變更是有意為之，並與模型定義及資料庫 schema 對齊。

finding 片段：`message_unit_price=Decimal(0), ⏎ message_price_unit=Decimal("0.001"), ⏎ message_files=json.dumps(messages_ids) if messages_ids else "", ⏎ answer="",`

## P0318

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:710`，距錨點 0 行）跨欄位驗證誤用 field_validator，導致驗證失效或誤報

> 在 `_bucket_folder_suffix` 中嘗試進行跨欄位驗證，但此方法以 `@field_validator` 裝飾，僅能存取當前欄位的值，無法可靠取得其他欄位（如 `bucket`）。`info.data` 在驗證時可能尚未包含 `bucket` 的值（取決於欄位順序），導致驗證永遠不觸發或誤報。應改用 `@model_validator` 並在 `mode='after'` 中進行跨欄位驗證。

finding 片段：`if info.data.get("bucket") and value.strip("/") == info.data.get("bucket"): ⏎ raise ValueError("bucket_folder cannot be the same as bucket name")`

## P0319

**GT**（func）Incorrect logical operator allows unwanted welcome email triggers

> The condition uses OR (`||`) instead of AND (`&&`) when checking whether to create welcome email outbox entries. This means welcome emails will be triggered if EITHER the config is set OR the source is 'member', instead of requiring BOTH conditions. This causes two problems: (1) welcome emails are sent even when the feature is disabled (config not set) as long as source is 'member', and (2) welcome emails are sent for disallowed sources (like 'import' or 'admin') when the config is set. The correct logic should require both the feature to be enabled AND the source to be in the allowed list.

GT 片段：`const memberAddOptions = {...(options || {}), withRelated}; ⏎ var member; ⏎ const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

**finding**（`ghost/core/core/server/services/members/members-api/repositories/MemberRepository.js:341`，距錨點 0 行）config 值型別不一致可能導致條件判斷錯誤

> `config.get('memberWelcomeEmailTestInbox')` 在測試中被設定為字串（如 'test-inbox@example.com'）或空字串，但在程式碼中直接作為布林條件使用。若 config 值為空字串，`welcomeEmailConfig` 為 falsy，但 `WELCOME_EMAIL_SOURCES.includes(source)` 仍可能為 true，導致非預期建立 outbox。建議明確檢查 config 值是否為非空字串，或統一型別。

finding 片段：`const welcomeEmailConfig = config.get('memberWelcomeEmailTestInbox'); ⏎ if (welcomeEmailConfig || WELCOME_EMAIL_SOURCES.includes(source)) {`

## P0320

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:243`，距錨點 4 行）gtk 腳本存在時仍會覆寫，可能導致非預期更新

> 原本的邏輯是當 `gtk` 檔案不存在時才下載並寫入，但此 PR 改為當檔案存在時仍使用 `include_bytes!` 的內容覆寫。這可能導致使用者自訂的腳本被覆蓋，或造成不必要的寫入。

建議保留原本的 `if !gtk.exists()` 條件，或明確說明覆寫意圖。

finding 片段：`if gtk.exists() { ⏎ let data = include_bytes!("./linuxdeploy-plugin-gtk.sh"); ⏎ write_and_make_executable(&gtk, data)?; ⏎ }`

## P0321

**GT**（func）Removed HTML5 min validation from concurrency limit input

> The concurrency limit input field previously had `min={0}` attribute (HTML5 validation) to prevent negative numbers from being entered. This attribute was removed in this PR change. While the Zod schema still validates that the value must be >= 0, users now lose immediate feedback when trying to enter negative values. They can type a negative number like `-5` and only discover it's invalid after clicking Save, rather than being prevented from entering it in the first place. This degrades the user experience by removing client-side validation that provides instant feedback.

GT 片段：`<Input ⏎ {...field} ⏎ type="number" ⏎ placeholder="Unlimited"`

**finding**（`ui-v2/src/components/work-pools/edit/work-pool-edit-form.tsx:112`，距錨點 0 行）concurrency limit 輸入可能產生 NaN 或負數

> 在 onChange 中直接使用 `Number(value)`，若使用者輸入非數字字元（例如 'e'、'-'、'+'），可能得到 NaN。此外，沒有驗證最小值，可能送出負數。建議使用 zod schema 驗證（例如 `z.number().int().nonnegative().nullable()`），或在 onChange 中過濾無效輸入。

finding 片段：`onChange={(e) => { ⏎ const value = e.target.value; ⏎ field.onChange(value === "" ? null : Number(value)); ⏎ }}`

## P0322

**GT**（func）Wrong token value returned breaks invite link functionality

> The method returns `newToken.identifier` which contains the database identifier string 'invite-link-for-teamId-{teamId}' instead of returning the actual random hex token that was generated. This means the invite link will embed this identifier string in the URL instead of the actual verification token. When users attempt to use the invite link, the token lookup will fail because the identifier is not a valid token value, completely breaking the invite acceptance flow.

GT 片段：`const token = randomBytes(32).toString("hex"); ⏎ const newToken = await prisma.verificationToken.create({ ⏎ data: { ⏎ identifier: `invite-link-for-teamId-${teamId}`,`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 0 行）回傳的 token 與實際建立的 verificationToken 不一致

> `createInvite` 原本回傳 `token`（隨機產生的 token），現在改為回傳 `newToken.identifier`。但 `identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的 token。這會導致 API 回傳的 token 無法用於驗證邀請，且與 `inviteLink` 中的 token 不一致。

失敗情境：使用者取得邀請連結後，使用連結中的 token 進行驗證，但資料庫中的 verificationToken 的 token 欄位是隨機產生的 token，而 identifier 是固定格式，因此驗證會失敗。

建議：回傳 `token` 而非 `newToken.identifier`。

finding 片段：`token: newToken.identifier,`

## P0323

**GT**（func）Search filter ignored causing all members to be displayed

> The EditWeightsForAllTeamMembers component renders teamMembers instead of filteredMembers in the member list. The filteredMembers variable is computed using useMemo to filter team members based on the search query and assignAllTeamMembers flag, but the rendering logic uses the unfiltered teamMembers array directly. This causes the search functionality to be completely non-functional - when users type in the search box, no filtering occurs and all team members are still displayed, making it impossible to search through large team member lists.

GT 片段：`<div className="flex max-h-[80dvh] flex-col overflow-y-auto rounded-md border"> ⏎ {teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

**finding**（`apps/web/modules/event-types/components/EditWeightsForAllTeamMembers.tsx:304`，距錨點 0 行）搜尋與過濾功能失效：直接使用 teamMembers 取代 filteredMembers

> 原本使用 `filteredMembers` 來根據 `searchQuery` 和 `assignAllTeamMembers` 過濾顯示的成員，但現在改為直接 map `teamMembers`，導致搜尋框輸入不會過濾列表，且當 `assignAllTeamMembers` 為 false 時，仍會顯示所有團隊成員，而非僅限於已指派者。

**失敗情境**：使用者輸入搜尋關鍵字，列表不會更新；或未勾選「指派所有成員」時，仍看到未指派的成員。

**建議**：恢復使用 `filteredMembers`，或將過濾邏輯套用至 `teamMembers` 後再 map。

finding 片段：`{teamMembers.map((member) => ( ⏎ <TeamMemberItem key={member.value} member={member} onWeightChange={handleWeightChange} /> ⏎ ))}`

## P0324

**GT**（func）SettingsTextFormatter class missing final keyword

> The newly added SettingsTextFormatter class violates repository Rule #12 from AGENTS.md, which requires classes that are not designed for subclassing to be marked with the 'final' keyword. This helper class is clearly not intended for inheritance (it has a private initializer and is a simple utility class), but lacks the final modifier. This prevents compiler optimizations and fails to communicate design intent explicitly, violating an explicit compliance rule added in this same PR.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:423`，距錨點 0 行）使用 String(format:) 搭配本地化字串可能導致崩潰

> `SettingsTextFormatter` 中的 `formatStudiesText` 和 `formatRolloutsText` 使用 `String(format: strings.detailTextStudies, appName)`。`detailTextStudies` 和 `detailTextRollouts` 是本地化字串，其內容可能包含額外的格式說明符（例如翻譯後的字串可能包含 `%d` 或 `%2$@`），這會導致 `String(format:)` 在執行時期因參數數量不符而崩潰，或顯示錯誤的內容。建議改用 `String.localizedStringWithFormat` 或避免使用格式字串，直接使用字串插值或替換。

finding 片段：`func formatStudiesText(appName: String) -> String { ⏎ return String(format: strings.detailTextStudies, appName) ⏎ } ⏎ `

## P0325

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 10 行）未檢查 XCTWaiter 結果，可能回傳 nil 導致測試失敗

> `XCTWaiter.wait` 的回傳值（`XCTWaiter.Result`）未被檢查。若等待逾時，`capturedFrame` 和 `capturedOrigin` 可能為 nil，函式會回傳 nil，導致呼叫端的 `guard` 失敗並使測試失敗。但此失敗無法區分是逾時還是其他錯誤，且沒有提供足夠的診斷資訊。

建議檢查 waiter 結果，若為 `.timedOut` 則記錄錯誤或直接 `XCTFail`，並考慮增加逾時時間或改用更可靠的等待機制。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0326

**GT**（func）GitHub mirror URL ignored, always downloads from original URL

> The function `generate_github_alternative_url` computes an alternative mirror URL from environment variables but then returns the original GitHub URL instead of the computed mirror URL. This breaks the GitHub mirror functionality that users configure via `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR` or `TAURI_BUNDLER_TOOLS_GITHUB_MIRROR_TEMPLATE` environment variables. When GitHub has rate limits or accessibility issues, the configured mirrors will be silently ignored and downloads will fail from the original GitHub URLs. The bug occurs because `alt_url` is renamed to `_alt_url` (indicating it's unused) and `url.to_owned()` is returned instead of `alt_url`.

GT 片段：`fn generate_github_alternative_url(url: &str) -> Option<(ureq::Agent, String)> { ⏎ if !url.starts_with("https://github.com/") { ⏎ return None; ⏎ }`

**finding**（`crates/tauri-bundler/src/utils/http_utils.rs:52`，距錨點 0 行）鏡像 URL 回退邏輯可能錯誤改寫非 GitHub 網址

> 在 `generate_github_alternative_url` 中，原本回傳替代 URL（`alt_url`），現在改為回傳原始 URL（`url.to_owned()`）。這可能導致當 `generate_github_mirror_url_from_template` 或 `generate_github_mirror_url_from_base` 成功產生鏡像 URL 時，函式卻回傳原始 URL，使得鏡像功能失效。此外，若原始 URL 不是 GitHub 網址，此函式仍可能被呼叫並回傳原始 URL，但呼叫端可能預期只有 GitHub 網址會被處理。建議確認此函式的呼叫情境，並確保只有 GitHub 網址會進入此邏輯，或修正回傳值為 `alt_url`。

finding 片段：`.map(|_alt_url| { ⏎ ( ⏎ ureq::Agent::config_builder() ⏎ .user_agent(BUNDLER_USER_AGENT)`

## P0327

**GT**（func）Database transaction commits called on every variable update instead of batched

> The ConversationVariablePersistenceLayer now calls flush() inside the loop for each updated conversation variable, rather than batching all updates and flushing once after the loop completes. This causes multiple unnecessary database commits when multiple conversation variables are updated in a single node execution, significantly degrading performance and creating database contention. The original implementation correctly tracked whether any updates occurred with the `updated_any` flag and only flushed once after all updates were queued.

GT 片段：`for item in updated_variables: ⏎ selector = item.selector ⏎ if len(selector) < 2: ⏎ logger.warning("Conversation variable selector invalid. selector=%s", selector)`

**finding**（`api/core/app/layers/conversation_variable_persist_layer.py:52`，距錨點 0 行）每個變數更新後都 flush，可能造成效能問題

> 在 `for item in updated_variables` 迴圈內，每次呼叫 `self._conversation_variable_updater.update(...)` 後都呼叫 `self._conversation_variable_updater.flush()`。如果一次更新多個 conversation variables，會造成多次資料庫寫入。建議將 flush 移到迴圈外，或讓 updater 內部累積變更後一次 flush。

finding 片段：`self._conversation_variable_updater.update(conversation_id=conversation_id, variable=variable) ⏎ self._conversation_variable_updater.flush()`

## P0328

**GT**（func）Missing return value breaks caller's count tracking

> The 'updateMany' method in BookingRepository no longer returns the Prisma update result object which contains the count of updated records. According to the IBookingRepository interface, this method should return 'Promise<{ count: number }>', but the implementation now returns 'Promise<void>'. This breaks any calling code that depends on knowing how many bookings were updated, potentially affecting audit logging, metrics, or conditional logic that needs to verify if the update affected any records.

GT 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

**finding**（`packages/features/bookings/repositories/BookingRepository.ts:1502`，距錨點 0 行）updateMany 回傳型別與介面不一致

> `IBookingRepository` 介面定義 `updateMany` 回傳 `Promise<{ count: number }>`，但實作中 `updateMany` 沒有回傳值（`await` 後未回傳）。這會導致呼叫端若依賴回傳值會得到 `undefined`，可能造成執行時期錯誤。建議讓實作回傳 `{ count }` 或調整介面。

finding 片段：`async updateMany({ where, data }: { where: BookingWhereInput; data: BookingUpdateData }) { ⏎ await this.prismaClient.booking.updateMany({ ⏎ where: where, ⏎ data,`

## P0329

**GT**（func）Ignoring XCTWaiter result allows returning stale data on timeout

> The captureFrameAndOrigin method no longer checks if waiter == .completed before returning captured values. This means the function will return potentially nil or incomplete frame and origin data even when the expectation times out or is interrupted. The function may return cached/partial data from a failed navigation attempt, causing tests to use invalid WebKit objects and producing false test results.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter 使用方式錯誤，導致測試必定逾時

> `XCTWaiter.wait(for:timeout:)` 是同步方法，會阻塞當前執行緒直到 expectation 被 fulfill 或逾時。但 `webView.load` 觸發的導航事件需要 RunLoop 持續運作才能處理，因此 delegate 方法永遠不會被呼叫，測試會卡住直到逾時。

建議改用非同步等待方式，例如 `await fulfillment(of: [expect], timeout: timeout)`（需將方法標記為 `async`），或使用 `XCTWaiter` 搭配 `RunLoop.current.run(mode:before:)` 手動驅動 RunLoop。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

## P0330

**GT**（rule）Android function missing target_os guard

> The rule requires platform-specific APIs to use #[cfg(target_os = "...")] or similar conditional compilation attributes. The generate_tauri_properties function is Android-specific but lacks proper conditional compilation guards, causing it to be compiled on all platforms where it may fail.

GT 片段：`pub fn generate_tauri_properties( ⏎ config: &AndroidConfig, ⏎ tauri_config: &TauriConfig, ⏎ dev: bool,`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 6 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0331

**GT**（func）WebView2 offline installer bypasses platform certificate verification

> The download_webview2_offline_installer function was modified to use ureq::get() directly instead of calling the download() helper function. This bypasses the new platform certificate verification feature introduced in this PR. While webview2_guid_path correctly uses base_ureq_agent() which includes platform cert verification, the actual file download in lines 65-68 uses the default ureq::get which doesn't respect platform certificates. This inconsistency means WebView2 downloads will fail on systems that require custom certificate authorities (corporate environments, China, etc.) defeating the purpose of this PR.

GT 片段：`let response = ureq::get(url).call().map_err(Box::new)?; ⏎ let mut bytes = Vec::new(); ⏎ response.into_body().into_reader().read_to_end(&mut bytes)?; ⏎ std::fs::write(&file_path, bytes)?;`

**finding**（`crates/tauri-bundler/src/bundle/windows/util.rs:65`，距錨點 0 行）下載 WebView2 離線安裝程式時未使用代理設定

> 在 `download_webview2_offline_installer` 中，原本使用 `download(url)` 函式（可能內部有處理代理），但改為直接使用 `ureq::get(url)`，這會忽略代理設定。若使用者在需要代理的環境下執行，下載可能失敗。建議改用 `base_ureq_agent()` 或確保代理設定被套用。

finding 片段：`let response = ureq::get(url).call().map_err(Box::new)?;`

## P0332

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）當 SMTP_LOCAL_HOSTNAME 為空字串時，local_hostname 傳入 None 可能導致非預期行為

> 程式碼使用 `local_host or None`，若設定為空字串，則傳入 None。smtplib 在建構時若 local_hostname 為 None，會自動使用 socket.getfqdn()，這可能與預期不符（預期不覆寫時應使用預設行為，但 None 可能觸發不同的行為）。建議明確處理空字串，例如僅在設定非空時才傳遞 local_hostname 參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0333

**GT**（func）Empty string fallback breaks SMTP local_hostname default behavior

> The code uses `dify_config.SMTP_LOCAL_HOSTNAME or ""` which converts None to an empty string. However, the smtplib library expects None (not an empty string) when no custom hostname is specified, allowing it to use the system's FQDN as a default. By providing an empty string instead of None, the SMTP connection will fail to properly identify itself during the HELO/EHLO handshake when SMTP_LOCAL_HOSTNAME is not configured. This breaks the intended fallback behavior and can cause mail delivery failures on servers that validate client hostnames.

GT 片段：`local_host = dify_config.SMTP_LOCAL_HOSTNAME or ""`

**finding**（`api/libs/smtp.py:28`，距錨點 3 行）當 SMTP_LOCAL_HOSTNAME 為空字串時，local_hostname 傳入 None 可能導致非預期行為

> 程式碼使用 `local_host or None`，若設定為空字串，則傳入 None。smtplib 在建構時若 local_hostname 為 None，會自動使用 socket.getfqdn()，這可能與預期不符（預期不覆寫時應使用預設行為，但 None 可能觸發不同的行為）。建議明確處理空字串，例如僅在設定非空時才傳遞 local_hostname 參數。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0334

**GT**（func）Unconditional weight concatenation adds empty space to attribute labels

> In the attribute columns rendering logic, the weight string is always concatenated to the label even when weights are disabled. When attribute.isWeightsEnabled is false, weight remains an empty string but is still added to the label with a space (line 252). This causes attribute labels to have trailing spaces when weights are not enabled, affecting display formatting and potentially breaking string matching or filtering operations that expect exact label text.

GT 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

**finding**（`apps/web/modules/users/components/UserTable/UserListTable.tsx:243`，距錨點 0 行）Attributes 的權重與群組標示改為純文字，降低可讀性

> 原本 attributes 的顯示會將權重以獨立 Badge 呈現，並以顏色區分群組選項；現在改為在 label 中附加權重與 "(group)" 文字，可能讓使用者難以快速辨識。建議保留原本的視覺區分，或提供更明確的格式。

finding 片段：`let weight = ""; ⏎ if (attribute.isWeightsEnabled) { ⏎ weight = `${attributeValue.weight || 100}%`; ⏎ }`

## P0335

**GT**（func）Number input type changed to text breaks numeric validation

> At line 166 in the prompt value panel, the Input component for number type variables was changed from type="number" to type="text". This breaks the browser's native numeric input validation and allows users to enter non-numeric characters into fields that expect numbers. The onChange handler still expects numeric values, which will cause type mismatches when the input is processed downstream in the application logic.

GT 片段：`{type === 'number' && ( ⏎ <Input ⏎ type="text" ⏎ value={inputs[key] ? `${inputs[key]}` : ''}`

**finding**（`web/app/components/app/configuration/prompt-value-panel/index.tsx:167`，距錨點 0 行）數字輸入類型從 number 改為 text，可能影響輸入驗證

> 將 `<Input type="number">` 改為 `<Input type="text">`，可能導致使用者輸入非數字字元，且喪失瀏覽器原生的數字驗證與上下箭頭調整功能。若後端預期數字，可能造成型別錯誤。建議確認此變更的必要性，或改用其他方式限制輸入。

finding 片段：`type="text"`

## P0336

**GT**（rule）Missing explicit access control on helper method

> Rule requires explicit access control modifiers. The newly added `captureFrameAndOrigin` method lacks an explicit access level (defaults to `internal`).

GT 片段：`static func captureFrameAndOrigin(for url: URL, timeout: TimeInterval = 3.0) -> (WKFrameInfo, WKSecurityOrigin)? {`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:23`，距錨點 11 行）FakeWKNavigationDelegate 未處理非 targetFrame 的情況

> `decidePolicyFor` 中直接使用 `navigationAction.targetFrame`，但某些導航（例如新視窗或下載）的 `targetFrame` 可能為 nil。雖然目前測試只使用簡單的 URL，但若未來擴充可能會遇到問題。

建議增加對 nil 的處理，或明確註明此 helper 僅適用於 main frame 導航。

finding 片段：`let frame = navigationAction.targetFrame ⏎ capturedFrame = frame ⏎ capturedOrigin = frame?.securityOrigin`

## P0337

**GT**（func）Inverted logic causes wrong invite URLs for organizations vs teams

> The condition `if (isOrgContext)` returns the team invite link format when it should return the organization signup format, and vice versa. Organization invites need to direct users to the signup flow with callback to getting-started, but will incorrectly receive the teams URL. Regular team invites need the teams URL but will incorrectly receive the signup URL with callback. This breaks the entire invite flow by sending users to the wrong destination based on whether they're joining an organization or a regular team.

GT 片段：`private static async buildInviteLink(token: string, isOrgContext: boolean): Promise<string> { ⏎ const teamInviteLink = `${WEBAPP_URL}/teams?token=${token}`; ⏎ if (isOrgContext) { ⏎ return teamInviteLink;`

**finding**（`packages/features/ee/teams/services/teamService.ts:99`，距錨點 5 行）createInvite 回傳錯誤的 token 欄位

> 在 `createInvite` 中，原本回傳 `token`（隨機產生的 token），但修改後回傳 `newToken.identifier`。`identifier` 是 `invite-link-for-teamId-${teamId}`，並非實際的邀請 token。這會導致回傳給客戶端的 token 不正確，邀請連結中的 token 也與資料庫中的 token 不一致，使用者將無法透過該 token 加入團隊。

建議改回傳 `token` 變數，或明確使用 `newToken.token`。

finding 片段：`token: newToken.identifier,`

## P0338

**GT**（func）Exit command resolves after activity termination

> The exit command calls `activity.finish()` before `invoke.resolve()`. This creates a race condition where the activity lifecycle may terminate before the JavaScript callback receives the resolution response. This can lead to lost responses, potential crashes in the JavaScript layer when expecting a resolution that never arrives, and unreliable exit behavior. The resolution should occur before finishing the activity to ensure the response is sent back to the frontend before the Android activity is destroyed.

GT 片段：`@Command ⏎ fun exit(invoke: Invoke) { ⏎ activity.finish() ⏎ invoke.resolve()`

**finding**（`crates/tauri/mobile/android/src/main/java/app/tauri/AppPlugin.kt:51`，距錨點 0 行）exit 命令未處理 activity 可能為 null 的情況

> `exit` 命令直接呼叫 `activity.finish()`。若 activity 已銷毀或為 null，可能拋出 NPE。雖然在正常情況下 activity 不應為 null，但建議加入防禦性檢查。

finding 片段：`activity.finish()`

## P0339

**GT**（func）Inverted logic for search mode activation based on category collections

> The search mode logic has been inverted on line 43. The original logic was `!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category has NO collections), but it's now `PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)` (force search mode when category HAS collections). This causes the opposite behavior: categories that are designed to show collections will be forced into search mode, while categories without collections will try to show a collection view that doesn't exist. Users will see incorrect UI states when switching between different plugin categories.

GT 片段：`export function useMarketplaceSearchMode() { ⏎ const [searchPluginText] = useSearchPluginText() ⏎ const [filterPluginTags] = useFilterPluginTags() ⏎ const [activePluginType] = useActivePluginType()`

**finding**（`web/app/components/plugins/marketplace/atoms.ts:43`，距錨點 0 行）布林邏輯變更可能導致搜尋模式判斷錯誤

> 在 `useMarketplaceSearchMode` 中，原本的條件是 `(searchMode ?? (!PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，現在改為 `(searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`，移除了 `!` 運算子。這會反轉當 `searchMode` 為 null/undefined 時的預設行為：原本當 activePluginType 不在集合中時會進入搜尋模式，現在變成在集合中時才進入搜尋模式。這可能導致在非集合分類下無法正確顯示搜尋模式，或在集合分類下錯誤顯示搜尋模式。請確認此變更是否為預期行為，若非預期請恢復 `!`。

finding 片段：`|| (searchMode ?? (PLUGIN_CATEGORY_WITH_COLLECTIONS.has(activePluginType)))`

## P0340

**GT**（func）Version code validation occurs before dev mode clamping causing build failures

> The order of operations for version code validation and dev mode clamping has been reversed, causing validation to fail for valid semver versions in development mode. Previously, the code clamped the version_code in dev mode BEFORE validation (line 652-654 originally), but now validation happens first (lines 652-661) and clamping occurs after (lines 663-665). This means that if a semver version produces a version_code greater than 2100000000, the build will fail with an error even in dev mode where it should be clamped to a valid range. For example, a version like "3.0.0" produces version_code 3000000000, which will now throw an error in dev builds instead of being safely clamped.

GT 片段：`} else if let Ok(version) = Version::parse(version) { ⏎ let mut version_code = version.major * 1000000 + version.minor * 1000 + version.patch; ⏎ if version_code == 0 { ⏎ crate::error::bail!(`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 12 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫回，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Android 套件衝突。建議使用檔案鎖（例如 `flock`）或將遞增邏輯移到單一建置流程中，確保同一時間只有一個程序更新。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0341

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:220`，距錨點 0 行）移除 `strict=True` 可能隱藏長度不一致問題

> 原本的 `zip(..., strict=True)` 會在兩個序列長度不一致時拋出例外，移除後若 `pool_names_list` 與 `results` 長度不同，會靜默忽略多餘的元素。雖然目前兩者長度應相同，但移除嚴格模式降低了防禦性。

建議保留 `strict=True` 以確保長度一致。

finding 片段：`for name, result in zip(pool_names_list, results):`

## P0342

**GT**（func）Swapped source and destination in ditto archive command

> The arguments to the ditto command are reversed: zip_path appears before app_bundle_path, when ditto expects the source (app_bundle_path) before the destination (zip_path). This will cause ditto to fail when attempting to create the notarization archive, as it tries to compress a non-existent zip file into the app bundle directory. The command format should be 'ditto -c -k --keepParent --sequesterRsrc <source> <destination>', but the current order attempts '<destination> <source>', breaking the entire notarization workflow.

GT 片段：`let zip_args = vec![ ⏎ "-c", ⏎ "-k", ⏎ "--keepParent",`

**finding**（`crates/tauri-macos-sign/src/lib.rs:176`，距錨點 0 行）notarize_inner 中參數順序變更可能影響可讀性

> 在 `notarize_inner` 中，`app_bundle_path` 和 `zip_path` 的參數順序被調換，這可能只是為了可讀性，但需確認是否影響任何依賴此函數的程式碼（雖然此函數為私有，但可能被測試或內部呼叫）。

finding 片段：`app_bundle_path ⏎ .to_str() ⏎ .expect("failed to convert bundle_path to string"), ⏎ zip_path`

## P0343

**GT**（func）Missing error logging in TanStack devtools lazy import

> The TanStackDevtoolsLoader silently swallows import errors without logging them, making it impossible to debug why the devtools fail to load. This creates an inconsistent error handling pattern compared to the ReactScanLoader (in the same PR), which properly logs errors with console.error before returning a fallback component. When developers encounter issues with TanStack devtools not appearing, they will have no visibility into whether it's due to an import failure, missing dependencies, or other issues.

GT 片段：`const TanStackDevtoolsWrapper = lazy(() => ⏎ import('./devtools').then(module => ({ ⏎ default: module.TanStackDevtoolsWrapper, ⏎ })).catch(() => {`

**finding**（`web/app/components/devtools/tanstack/loader.tsx:9`，距錨點 0 行）TanStack devtools 載入失敗被靜默吞掉

> 在 lazy import 的 catch 中直接回傳 `{ default: () => null }`，沒有記錄任何錯誤。這會讓開發者無法察覺 devtools 載入失敗，喪失除錯能力。建議至少加上 `console.error`，或考慮在開發環境顯示錯誤訊息。

finding 片段：`})).catch(() => { ⏎ return { default: () => null } ⏎ }),`

## P0344

**GT**（rule）Any type used for selector parameter

> The rule requires using specific types instead of 'any' annotations. The selector parameter uses 'any' instead of a proper function type signature.

GT 片段：`export function usePluginPageContext(selector: any) { ⏎ return useContextSelector(PluginPageContext, selector) ⏎ }`

**finding**（`web/app/components/plugins/plugin-page/context.tsx:51`，距錨點 0 行）喪失型別安全：selector 參數改為 any

> `usePluginPageContext` 的參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`，這會讓 TypeScript 無法檢查傳入的 selector 是否為函式，也無法推斷回傳值型別。若呼叫端誤傳非函式值，將在執行時期拋出錯誤，且編譯器無法攔截。建議保留原本的函式型別，或使用更精確的泛型來保留型別推斷。

finding 片段：`export function usePluginPageContext(selector: any) {`

## P0345

**GT**（func）RequestBody description set after iteration may use stale or modified description value

> The operation.RequestBody.Description is now set after iterating through media types and parsing examples, instead of before. This reordering creates a potential race condition or state dependency issue where the description variable could be modified or cleared during the example parsing logic. Additionally, if parsing throws an exception or causes early termination, the description will never be set. The original code correctly set the description first to ensure it's always applied before potentially failing example operations. This bug can result in missing or incorrect request body descriptions in the OpenAPI specification.

GT 片段：`if (operation.RequestBody is not null) ⏎ { ⏎ if (propertyComment.Examples?.FirstOrDefault() is { } jsonString) ⏎ {`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 0 行）RequestBody.Description 設定時機變更可能影響範例處理

> 原本先設定 `operation.RequestBody.Description = description`，再處理範例；現在改為先處理範例，再設定 Description。若範例處理過程中發生例外（例如 `jsonString.Parse()` 失敗），Description 將不會被設定，可能導致部分資訊遺失。建議確認此變更是否為預期，並考慮將 Description 設定放在 finally 或確保例外處理。

finding 片段：`operation.RequestBody.Description = description;`

## P0346

**GT**（func）Parameter lookup uses wrong identifier causing documentation mismatch

> The code searches for operation parameters using propertyName instead of metadata.Name, which causes a mismatch when the property name differs from the parameter name in the API metadata. The metadata.Name represents how the parameter is actually named in the OpenAPI operation, while propertyName is the original C# property name. Using propertyName will fail to find the correct parameter in cases where parameter naming conventions differ (e.g., camelCase in API vs PascalCase in C#), resulting in parameter descriptions not being applied correctly to the OpenAPI documentation.

GT 片段：`var propertyDocId = DocumentationCommentIdHelper.CreateDocumentationId(containerType, propertyName); ⏎ if (XmlCommentCache.Cache.TryGetValue(DocumentationCommentIdHelper.NormalizeDocId(propertyDocId), out var propertyComment)) ⏎ { ⏎ var parameter = operation.Parameters?.SingleOrDefault(p => p.Name =`

**finding**（`src/OpenApi/gen/XmlCommentGenerator.Emitter.cs:479`，距錨點 27 行）RequestBody.Description 設定時機變更可能影響範例處理

> 原本先設定 `operation.RequestBody.Description = description`，再處理範例；現在改為先處理範例，再設定 Description。若範例處理過程中發生例外（例如 `jsonString.Parse()` 失敗），Description 將不會被設定，可能導致部分資訊遺失。建議確認此變更是否為預期，並考慮將 Description 設定放在 finally 或確保例外處理。

finding 片段：`operation.RequestBody.Description = description;`

## P0347

**GT**（rule）SettingsTextFormatter missing @MainActor annotation

> The rule requires that classes interacting with UIKit or performing UI updates must be marked with @MainActor annotation. The SettingsTextFormatter class formats text for UI display in settings screens but lacks the @MainActor annotation.

GT 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ private init() {}`

**finding**（`focus-ios/Blockzilla/UIComponents/UIConstants.swift:417`，距錨點 0 行）新增的 SettingsTextFormatter 可能未被使用

> `SettingsTextFormatter` 類別被新增，但在此 diff 中未看到任何使用它的程式碼。如果沒有其他地方使用，這將是死代碼，增加維護負擔。建議確認是否有後續 PR 會使用，或考慮延後加入。

finding 片段：`// Helper class for formatting Study and Rollout settings text for display ⏎ class SettingsTextFormatter { ⏎ static let shared = SettingsTextFormatter() ⏎ `

## P0348

**GT**（func）Using display path instead of actual path breaks certificate directory validation

> The code uses prettyCertDir (which contains '$HOME' placeholder for display purposes) instead of certDir (the actual file system path) when computing certDirFullPath. Since prettyCertDir contains the literal string '$HOME' rather than the expanded home directory path, Path.GetFullPath() will fail to resolve it correctly or resolve it to an incorrect path. This causes the directory comparison logic to always fail, preventing the tool from detecting when the certificate directory is already configured in SSL_CERT_DIR, resulting in unnecessary warning messages to users who have already configured their environment correctly.

GT 片段：`var existingDirs = existingSslCertDir.Split(Path.PathSeparator); ⏎ var certDirFullPath = Path.GetFullPath(prettyCertDir);`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 10 行）路徑比較使用 OrdinalIgnoreCase 在 Linux 上可能導致誤判

> 在 Linux 上，檔案路徑是區分大小寫的。使用 `StringComparison.OrdinalIgnoreCase` 比較路徑可能將不同目錄視為相同（例如 `/Certs` 與 `/certs`），導致錯誤地認為憑證目錄已存在於 SSL_CERT_DIR 中，進而跳過必要的設定。建議在 Unix 平台上使用 `StringComparison.Ordinal`，或根據作業系統動態選擇比較方式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0349

**GT**（rule）Public ensureMainThread<T> lacks documentation comment

> A new/modified public API was introduced/changed without an accompanying triple-slash documentation comment describing its purpose/parameters/return value.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? {`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行）ensureMainThread<T> 在非主執行緒時回傳 nil 可能造成呼叫端誤判

> 原本的 `ensureMainThread<T>` 在非主執行緒時會透過 `DispatchQueue.main.async` 非同步執行工作並忽略結果，但現在改為回傳 `nil`。這會讓呼叫端無法區分「工作尚未執行」與「工作執行後回傳 nil」，可能導致邏輯錯誤。例如，若呼叫端預期取得一個非 nil 的值，但在背景執行緒呼叫時會立即收到 nil，而實際工作稍後才在主執行緒完成。建議改為使用 `DispatchQueue.main.sync` 同步等待結果，或保留非同步行為但提供 completion handler。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## P0350

**GT**（func）Race condition: dialog closes before parent callback executes

> In the block creation success handler, `onOpenChange(false)` is called before `onCreated(res.id)`. This creates a timing issue where the dialog closes and unmounts before the parent component's `onCreated` callback can properly execute. If the parent component relies on the dialog context or performs async operations in the callback, they may fail or cause errors. The proper sequence should close the dialog after the parent has finished handling the creation event.

GT 片段：`onSuccess: (res) => { ⏎ toast.success("Block created successfully"); ⏎ onOpenChange(false); ⏎ onCreated(res.id);`

**finding**（`ui-v2/src/components/blocks/block-document-create-dialog/block-document-create-dialog.tsx:161`，距錨點 13 行）驗證錯誤處理不完整，可能誤導使用者

> 在 `onSave` 中，呼叫 `validateForm` 後檢查 `errors.length > 0` 就 `return`，但沒有顯示任何錯誤訊息給使用者。使用者可能填寫了無效的資料，按下送出後沒有任何反應，誤以為建立成功。

建議在 `errors.length > 0` 時顯示錯誤提示（例如 toast 或表單內錯誤），或將驗證錯誤整合到表單的錯誤顯示中。

finding 片段：`await validateForm({ schema: values }); ⏎ if (errors.length > 0) { ⏎ return; ⏎ }`

## P0351

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行）MouseButtonState 的 From 轉換邏輯被反轉

> 在 `From<tray_icon::MouseButtonState>` 的實作中，原本 `Up` 對應 `Up`、`Down` 對應 `Down`，但此變更將其反轉為 `Up` 對應 `Down`、`Down` 對應 `Up`。這會導致所有依賴此轉換的程式碼（例如處理 tray icon 點擊事件）得到相反的按鍵狀態，造成邏輯錯誤。

建議修正為：
```rust
match value {
    tray_icon::MouseButtonState::Up => MouseButtonState::Up,
    tray_icon::MouseButtonState::Down => MouseButtonState::Down,
}
```

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## P0352

**GT**（func）ensureMainThread generic function loses return value when dispatched asynchronously

> The generic ensureMainThread<T> function was modified to return T? but has a critical flaw: when not on the main thread, it dispatches the work asynchronously to main queue and immediately returns nil, discarding the actual computation result. This breaks any caller that depends on the return value, as they will always receive nil when called from background threads. The function's contract promises to return the work result but fails to do so in the async dispatch path.

GT 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

**finding**（`BrowserKit/Sources/Common/Utilities/DispatchQueueHelper.swift:22`，距錨點 0 行）ensureMainThread<T> 在非主執行緒時回傳 nil 可能造成呼叫端誤判

> 原本的 `ensureMainThread<T>` 在非主執行緒時會透過 `DispatchQueue.main.async` 非同步執行工作並忽略結果，但現在改為回傳 `nil`。這會讓呼叫端無法區分「工作尚未執行」與「工作執行後回傳 nil」，可能導致邏輯錯誤。例如，若呼叫端預期取得一個非 nil 的值，但在背景執行緒呼叫時會立即收到 nil，而實際工作稍後才在主執行緒完成。建議改為使用 `DispatchQueue.main.sync` 同步等待結果，或保留非同步行為但提供 completion handler。

finding 片段：`public func ensureMainThread<T>(execute work: @escaping @MainActor () -> T) -> T? { ⏎ if Thread.isMainThread { ⏎ return MainActor.assumeIsolated { ⏎ return work()`

## P0353

**GT**（func）Missing await on async service call returns Promise instead of data

> The getBookingRecordings method calls this.calVideoService.getRecordings(bookingUid) without awaiting the Promise. Since getRecordings is an async method that fetches recordings from the database and external Cal Video API, the recordings variable will contain a Promise object instead of the actual recordings array. This Promise will be returned to the client in the response data field, causing a type mismatch and breaking the API contract.

GT 片段：`async getBookingRecordings(@Param("bookingUid") bookingUid: string): Promise<GetBookingRecordingsOutput> { ⏎ const recordings = this.calVideoService.getRecordings(bookingUid); ⏎ return { ⏎ status: SUCCESS_STATUS,`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 0 行）getRecordings 呼叫缺少 await，可能回傳未解析的 Promise

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 的呼叫移除了 `await`。若 `getRecordings` 是非同步方法（從其他端點如 `getVideoSessions` 使用 `await` 可推測），則回傳的 `recordings` 會是 Promise 物件而非實際資料，導致 API 回傳錯誤的資料型態或序列化失敗。

**失敗情境**：當客戶端呼叫此端點時，回應中的 `data` 欄位會是 Promise 物件，而非錄製陣列，可能造成客戶端解析錯誤或資料外洩。

**建議**：恢復 `await`，改為 `const recordings = await this.calVideoService.getRecordings(bookingUid);`

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0354

**GT**（rule）Hardcoded devtools loading message text

> The rule requires all user-facing strings to be defined in web/i18n/en-US/ translation files and accessed via useTranslation hook. The code hardcodes 'Loading devtools...' directly in the JSX instead of using a translation key.

GT 片段：`return ( ⏎ <Suspense fallback={<div className="text-xs text-gray-500">Loading devtools...</div>}> ⏎ <ReactScan /> ⏎ </Suspense>`

**finding**（`web/app/components/devtools/react-scan/loader.tsx:10`，距錨點 9 行）React Scan 載入失敗時回傳 null 元件可能造成非預期行為

> 在 catch 中回傳 `{ default: () => null }`，雖然有記錄錯誤，但回傳 null 元件可能導致 React 在渲染時出現問題（例如 Suspense 邊界無法正確處理）。建議改為回傳一個空的 Fragment 或明確的 fallback 元件。

finding 片段：`console.error('Failed to load React Scan devtools:', error) ⏎ return { default: () => null }`

## P0355

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行）linuxdeploy 下載 URL 使用錯誤的架構變數

> 原本使用 `linuxdeploy_arch`（i686 對應 i383），但修改後改為直接使用 `arch`。這可能導致 i686 架構下載到錯誤的檔案。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0356

**GT**（func）Incorrect escape character in IRIS vector database LIKE query

> The IRIS vector database implementation escapes special characters using backslash (via escape_like_pattern which produces \%, \_, \\) but then specifies ESCAPE '|' in the SQL query instead of ESCAPE '\'. This mismatch causes the database to look for the wrong escape character - it will treat | as the escape character while the string contains backslash escapes. As a result, the escaped special characters won't be properly interpreted, allowing SQL wildcards to remain active and causing search queries with special characters to produce incorrect results or security vulnerabilities.

GT 片段：`escaped_query = escape_like_pattern(query) ⏎ query_pattern = f"%{escaped_query}%" ⏎ sql = f""" ⏎ SELECT TOP {top_k} id, text, meta`

**finding**（`api/core/rag/datasource/vdb/iris/iris_vector.py:298`，距錨點 0 行）ESCAPE 子句使用 '|' 但 escape_like_pattern 使用 '\' 作為跳脫字元

> 在 IRIS 向量資料庫的 LIKE 查詢中，ESCAPE 子句指定 '|' 作為跳脫字元，但 `escape_like_pattern` 函式使用反斜線 '\' 進行跳脫。這會導致跳脫字元不一致：例如，輸入 "50%" 會被轉成 "50\\%"，但資料庫會將 '|' 視為跳脫字元，因此 '\\' 不會被視為跳脫，而 '%' 仍會被當作萬用字元。建議將 ESCAPE 子句改為 '\\'，或修改 escape_like_pattern 以使用 '|'。

finding 片段：`WHERE text LIKE ? ESCAPE '|'`

## P0357

**GT**（func）Incorrect string matching for path prefix detection causes false positives

> The double-nesting prevention logic uses `self.bucket_folder in path` instead of `path.startswith(self.bucket_folder)`. This causes false positives when bucket_folder appears anywhere in the path, not just as a prefix. For example, if bucket_folder is 'results/' and the path is 'my-results/file.txt', the code incorrectly treats it as already prefixed and returns it unchanged, skipping the necessary path resolution. This breaks the fix for issue #20174 in edge cases where folder names contain the bucket_folder as a substring.

GT 片段：`# See https://github.com/PrefectHQ/prefect/issues/20174 ⏎ if self.bucket_folder and self.bucket_folder in path: ⏎ return path ⏎ path = (`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 0 行）子字串檢查可能誤判非前綴路徑

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串檢查，若路徑中段包含 bucket_folder 字串但並非前綴，會錯誤地跳過前綴處理。例如 bucket_folder 為 "results/"，路徑為 "myresults/file.txt" 時，`"results/" in "myresults/file.txt"` 為 True，導致回傳未加前綴的路徑，造成儲存位置錯誤。建議改為檢查 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較前綴。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0358

**GT**（func）autoCloseOnSelect fails to close popover in non-inline multiselect mode

> The autoCloseOnSelect feature was implemented inconsistently across inline and non-inline modes. In non-inline Popover mode (line 1135-1137), when a multiselect option is selected with autoCloseOnSelect enabled, the code only calls onClose?.() without calling setOpen(false). Since SelectOptionsPopover can be instantiated without an onClose prop (line 1598), the optional chaining results in a no-op, leaving the popover open despite user selection. This breaks the intended UX where the dropdown should close immediately after selection when autoCloseOnSelect is configured. The inline mode implementation (line 1272-1273) correctly calls handleClose() which performs both operations.

GT 片段：`// Auto-close if configured ⏎ if (field.autoCloseOnSelect) { ⏎ onClose?.(); ⏎ }`

**finding**（`apps/shade/src/components/ui/filters.tsx:1125`，距錨點 9 行）使用 var 宣告變數可能導致作用域問題

> 在 multiselect 的 onSelect 中，將 `const newValues` 改為 `var newValues`。雖然在此情境下可能無實際影響，但 var 有函式作用域且可能提升，建議維持 const 以保持一致性與可讀性。

finding 片段：`var newValues = [...effectiveValues, option.value] as T[];`

## P0359

**GT**（rule）Lambda block uses K&R-style opening brace

> The opening brace for the lambda block is on the same line as the lambda declaration (`dir => {`). Rule 18 requires Allman style (opening braces on a new line) for blocks.

GT 片段：`var isCertDirIncluded = existingDirs.Any(dir => ⏎ { ⏎ if (string.IsNullOrWhiteSpace(dir)) ⏎ {`

**finding**（`src/Shared/CertificateGeneration/UnixCertificateManager.cs:375`，距錨點 0 行）路徑比較使用 OrdinalIgnoreCase 在 Unix 上可能不正確

> Unix 檔案系統通常區分大小寫，但此處使用 `StringComparison.OrdinalIgnoreCase` 比較路徑，可能將不同大小寫的目錄視為相同，導致誤判。例如 `/home/user/.dotnet/corefx/cryptography/x509stores/ca` 與 `/HOME/USER/.DOTNET/...` 會被視為相同，但實際上可能指向不同位置。建議在 Unix 上使用 `StringComparison.Ordinal`，或根據作業系統選擇比較方式。

finding 片段：`return string.Equals(Path.GetFullPath(dir), certDirFullPath, StringComparison.OrdinalIgnoreCase);`

## P0360

**GT**（rule）Unused local constant

> `waiter` is assigned but never used, which typically triggers SwiftLint's `unused_variable`/compiler warning. The code calls `XCTWaiter.wait` and stores the result without referencing it.

GT 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout)`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:44`，距錨點 0 行）XCTWaiter.wait 的結果未檢查

> XCTWaiter.wait 的回傳值未被檢查，若等待逾時，capturedFrame 與 capturedOrigin 可能為 nil，函式會回傳 nil，導致測試中 XCTFail 被觸發。但若等待逾時，測試會花費 timeout 秒數才失敗，可能拖慢測試。建議檢查 waiter 結果，若逾時則直接 XCTFail 並 return，避免後續不必要的等待。

finding 片段：`let waiter = XCTWaiter.wait(for: [expect], timeout: timeout) ⏎ if let frame = delegate.capturedFrame, let origin = delegate.capturedOrigin { ⏎ return (frame, origin) ⏎ }`

## P0361

**GT**（func）Removed strict zip validation enables silent data corruption

> The code removes `strict=True` from the `zip(pool_names_list, results)` call in the work pool parallel fetching logic. The strict parameter ensures that both iterables have the same length and raises a ValueError if they don't match. Without it, if there's a mismatch between the number of work pool names and the results from `asyncio.gather()` (which should never happen in correct code but could occur due to bugs in the async gather logic or unexpected exceptions), the zip will silently truncate to the shorter sequence. This means some work pool results could be dropped or mismatched with the wrong names, leading to incorrect work pool metadata in the generated SDK without any warning or error.

GT 片段：`work_pools: dict[str, WorkPoolInfo] = {} ⏎ for name, result in zip(pool_names_list, results): ⏎ if isinstance(result, BaseException):`

**finding**（`src/prefect/_sdk/fetcher.py:182`，距錨點 37 行）對 base_job_template['variables'] 的型別假設可能導致錯誤

> 在 `_fetch_work_pool` 中，原本有檢查 `variables` 是否為 dict，現在直接賦值給 `job_vars_schema`。若 `base_job_template['variables']` 不是 dict（例如是 list 或 None），後續使用 `job_vars_schema` 時可能拋出型別錯誤。建議保留型別檢查，或明確處理非 dict 的情況。

finding 片段：`job_vars_schema = base_job_template["variables"]`

## P0362

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行）缺少團隊管理員權限驗證

> 控制器使用 `@Roles("TEAM_MEMBER")`，但建立邀請連結通常需要管理員權限。目前任何團隊成員（甚至非管理員）都可以呼叫此端點，可能導致權限提升。建議改為 `@Roles("TEAM_ADMIN")` 或加入自訂的權限檢查，確保只有管理員能建立邀請。

finding 片段：`@Roles("TEAM_MEMBER")`

## P0363

**GT**（func）Auto-increment version code incorrectly applied in dev mode

> The auto-increment version code feature is now active during development builds, which violates the design intention stated in the config schema documentation. The condition `if tauri_config.bundle.android.auto_increment_version_code && !dev` has been changed to remove the `&& !dev` check (line 635). This means dev builds will now increment and persist the version code to tauri.properties, causing version code drift during development and potentially exhausting the version code space prematurely. The feature should only increment during production builds to avoid polluting the version history with development iterations.

GT 片段：`if tauri_config.bundle.android.auto_increment_version_code { ⏎ let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| {`

**finding**（`crates/tauri-cli/src/mobile/android/mod.rs:636`，距錨點 0 行）自動遞增 versionCode 存在競態條件

> `generate_tauri_properties` 在讀取舊的 `versionCode` 後直接加 1 寫入，沒有鎖定或原子操作。若兩個建置同時執行（例如 CI 平行建置），可能讀到相同的舊值，導致產生相同的 `versionCode`，造成 Google Play 上傳衝突。

建議：使用檔案鎖（如 `flock`）或將遞增邏輯移至建置系統中確保原子性。

finding 片段：`let last_version_code = std::fs::read_to_string(&app_tauri_properties_path) ⏎ .ok() ⏎ .and_then(|content| { ⏎ content`

## P0364

**GT**（func）Missing null check for InteractiveRequestUrl causes potential null reference in navigation

> The Redirect() method condition was changed from checking both InteractionOptions and InteractiveRequestUrl to only checking InteractionOptions. This creates a bug where if InteractionOptions is not null but InteractiveRequestUrl is null, the code will call NavigateToLogin with a null URL parameter at line 40. The NavigateToLogin method expects a non-null URL, so this will cause a null reference exception or navigation failure. The original PR properly validated both properties before choosing the navigation method.

GT 片段：`public void Redirect() ⏎ { ⏎ if (_tokenResult.InteractionOptions != null) ⏎ {`

**finding**（`src/Components/WebAssembly/WebAssembly.Authentication/src/Services/AccessTokenNotAvailableException.cs:44`，距錨點 0 行）Redirect() 可能因 InteractiveRequestUrl 為 null 而拋出 NullReferenceException

> 原本在 RedirectUrl 為 null 時會使用 null-forgiving 運算子，但現在直接使用 InteractiveRequestUrl!。若 InteractiveRequestUrl 為 null，NavigateTo 可能拋出 ArgumentNullException 或導致非預期行為。建議加入 null 檢查或確保該屬性在需要時必定有值。

finding 片段：`_navigation.NavigateTo(_tokenResult.InteractiveRequestUrl!);`

## P0365

**GT**（rule）Direct malloc/free instead of zmalloc/zfree

> The rule requires using zmalloc() and zfree() wrappers for memory allocation instead of direct malloc() and free() calls outside of the zmalloc implementation

GT 片段：`/* Allocate temporary buffer for slot tracking */ ⏎ int *slot_buffer = malloc(sizeof(int) * keys_result->numkeys); ⏎ for (int j = 0; j < keys_result->numkeys; j++) { ⏎ robj *this_key = argv[keys_result->keys[j].pos];`

**finding**（`src/cluster.c:1112`，距錨點 0 行）extractSlotFromKeysResult 迴圈邊界錯誤導致越界讀取

> 在 `extractSlotFromKeysResult` 中，迴圈條件 `j <= keys_result->numkeys` 應為 `j < keys_result->numkeys`。當 `j == numkeys` 時，`keys_result->keys[j]` 會讀取到陣列之外，造成未定義行為，可能導致程式崩潰或洩漏記憶體內容。

建議修正為：
```c
for (int j = 0; j < keys_result->numkeys; j++) {
```

finding 片段：`for (int j = 0; j <= keys_result->numkeys; j++) {`

## P0366

**GT**（func）Stale element reference captured before navigation in test initialization

> In the InitializeAsync method, _originalH1Element is captured by calling Browser.Exists(By.TagName("h1")) before navigating to the test page. This captures an element from whatever page the browser was previously on (from a prior test), then the Navigate() call loads the /redirect page. The stored element reference now points to a detached DOM node from the old page, making it stale. When test methods later access _originalH1Element.Text, they will encounter StaleElementReferenceException or get incorrect values because the element belongs to a different page's DOM that no longer exists in the browser.

GT 片段：`public override async Task InitializeAsync() ⏎ { ⏎ await base.InitializeAsync(); ⏎ _originalH1Element = Browser.Exists(By.TagName("h1"));`

**finding**（`src/Components/test/E2ETest/ServerRenderingTests/RedirectionTest.cs:32`，距錨點 0 行）Navigate 呼叫順序變更可能影響測試初始化

> 原本先 `Navigate` 再取得 `_originalH1Element`，現在順序相反。若 `Navigate` 會導致頁面重新載入，則先前取得的元素參考可能失效，導致後續 `Browser.Equal` 失敗。請確認此順序變更是否安全。

finding 片段：`_originalH1Element = Browser.Exists(By.TagName("h1")); ⏎ Navigate($"{ServerPathBase}/redirect");`

## P0367

**GT**（rule）JSON file uses 4-space indentation (should be 2 spaces)

> Rule 17 specifies that JSON files should use 2-space indentation. The newly added/modified JSON line is indented with 4 spaces.

GT 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 `{newsletterName}` 變數，可能導致使用者無法知道是哪個新聞信。建議保留變數以提供完整資訊。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。",`

## P0368

**GT**（func）Container created on every function call breaks singleton pattern

> The getFeaturesRepository() function now creates a new DI container instance on every invocation instead of reusing a module-level singleton container. This causes each call to return a different FeaturesRepository instance with its own PrismaClient connection, breaking the singleton pattern. This leads to database connection pool exhaustion and inconsistent cached state across repository instances, as FeaturesRepository maintains an internal cache for features (line 34 in features.repository.ts checks FeaturesRepository.featuresCache).

GT 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

**finding**（`packages/features/di/containers/FeaturesRepository.ts:4`，距錨點 0 行）每次呼叫 getFeaturesRepository 都建立新容器與新 repository 實例

> 與 `getFeatureOptInService` 相同，每次呼叫都建立新容器，可能造成不必要的資源消耗。若 repository 無狀態則影響較小，但仍建議考慮快取。

finding 片段：`export function getFeaturesRepository(): FeaturesRepository { ⏎ const featuresRepositoryContainer = createContainer(); ⏎ featuresRepositoryModuleLoader.loadModule(featuresRepositoryContainer); ⏎ return featuresRepositoryContainer.get<FeaturesRepository>(featuresRepositoryModuleLoader.token);`

## P0369

**GT**（rule）Inconsistent spacing around function arguments

> The code contains inconsistent spacing around commas in function arguments that violates the project's rustfmt configuration. Specifically, missing space after comma and extra spaces after comma in method calls.

GT 片段：`pub fn window_features(mut self, features: NewWindowFeatures) -> Self { ⏎ if let Some(position) = features.position() { ⏎ self.window_builder = self.window_builder.position(position.x,position.y); ⏎ }`

**finding**（`crates/tauri/src/webview/webview_window.rs:1316`，距錨點 0 行）window_features 方法中參數順序調整可能影響行為

> 在 `window_features` 方法中，原本先處理 position 再處理 size，現在順序對調。若兩者同時存在，且後者會覆蓋前者的設定，則可能導致最終視窗位置或大小不符合預期。請確認 `self.window_builder` 的 position 和 inner_size 設定是否互相獨立，否則應保持原有順序。

finding 片段：`if let Some(size) = features.size() { ⏎ self.window_builder = self.window_builder.inner_size(size.width,    size.height); ⏎ } ⏎ `

## P0370

**GT**（func）Wrong frame captured in navigation delegate

> The delegate captures navigationAction.targetFrame instead of navigationAction.sourceFrame. The targetFrame represents the frame that will be navigated (which may be nil for new windows), while sourceFrame represents the frame that initiated the navigation. This causes the helper to capture nil or incorrect frame information, breaking all tests that depend on valid WKFrameInfo objects. The original intent was to capture the frame initiating the navigation request.

GT 片段：`func webView(_ webView: WKWebView, ⏎ decidePolicyFor navigationAction: WKNavigationAction, ⏎ decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) { ⏎ let frame = navigationAction.targetFrame`

**finding**（`BrowserKit/Tests/WebEngineTests/Utilities/WebKitTestHelpers.swift:42`，距錨點 17 行）測試依賴真實網路，可能不穩定

> `captureFrameAndOrigin` 會載入 `https://example.com`，這需要網路連線。在 CI 環境中，網路可能不可用或不穩定，導致測試逾時或失敗。

建議改用本地 HTML 字串或 `data:` URL 來避免外部依賴，或使用 `WKWebView` 的 `loadHTMLString` 方法。

finding 片段：`webView.load(URLRequest(url: url))`

## P0371

**GT**（func）MainThreadThrottler timing logic inverted causing throttling to never execute

> In the throttle method, lastExecutionTime is updated to Date() BEFORE checking the threshold guard condition. This means timeIntervalSinceNow will always be approximately 0 (since it was just set), which will never be less than -threshold (a negative value). The guard condition will always fail, preventing the completion from ever executing. This completely breaks the throttling mechanism, causing any code depending on throttled callbacks to never receive them.

GT 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

**finding**（`firefox-ios/Client/Utils/MainThreadThrottler.swift:25`，距錨點 0 行）MainThreadThrottler.throttle 的節流邏輯可能失效

> 原本的 `throttle` 方法先檢查時間間隔，若未超過閾值則直接 return，否則更新 `lastExecutionTime` 並執行 completion。修改後，`lastExecutionTime` 在檢查前就被更新，導致每次呼叫都會更新時間戳，使得節流條件永遠不成立（因為 `lastExecutionTime.timeIntervalSinceNow` 會是極小的負數，永遠小於 `-threshold`）。這會讓節流功能失效，可能造成過多的執行。建議將 `lastExecutionTime = Date()` 移回 guard 之後。

finding 片段：`func throttle(completion: @escaping @MainActor () -> Void) { ⏎ lastExecutionTime = Date() ⏎ guard threshold <= 0 || lastExecutionTime.timeIntervalSinceNow < -threshold else { return } ⏎ DispatchQueue.main.async(execute: completion)`

## P0372

**GT**（rule）Line exceeds 110 character limit (Biome formatting rule)

> The added line appears to exceed the configured 110 character line width requirement, violating the repo's Biome formatting standards.

GT 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

**finding**（`apps/web/modules/event-types/hooks/useTeamMembersWithSegment.tsx:28`，距錨點 0 行）傳遞給 useProcessTeamMembersData 的 matchingTeamMembersWithResult 型別可能不符

> `useProcessTeamMembersData` 期望 `matchingTeamMembersWithResult` 為 `{ result: TeamMemberDto[] | null }`，但此處傳入的是 `matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult`。當 `matchingTeamMembersWithResult` 為 undefined 時，會傳入 undefined，可能導致型別錯誤或執行時期問題。

**失敗情境**：當查詢未啟用或尚未回傳時，`matchingTeamMembersWithResult` 為 undefined，傳入 undefined 可能導致 `useProcessTeamMembersData` 內部存取 `matchingTeamMembersWithResult?.result` 時出錯。

**建議**：確保傳入的物件符合型別，或調整 `useProcessTeamMembersData` 的參數型別以接受 undefined。

finding 片段：`matchingTeamMembersWithResult: matchingTeamMembersWithResult?.result ? { result: matchingTeamMembersWithResult.result } : matchingTeamMembersWithResult,`

## P0373

**GT**（func）Incorrect logical operator in tearDown causing theme reset to be skipped for all iPad tests

> The tearDown method uses OR (||) instead of AND (&&) when checking if the test should skip theme reset. This causes the theme reset to be skipped for ALL tests running on iPad devices, not just the testSelectBottomPlacement test. The original intent was to skip theme reset only when BOTH conditions are true (the test is testSelectBottomPlacement AND it's running on iPad), but the current code skips it when EITHER condition is true. This will leave the theme in Dark mode after any test runs on iPad, potentially affecting subsequent tests that expect Light theme.

GT 片段：`override func tearDown() async throws { ⏎ if #available(iOS 17.0, *) { ⏎ if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there.`

**finding**（`firefox-ios/firefox-ios-tests/Tests/XCUITests/OnboardingTests.swift:29`，距錨點 0 行）tearDown 提前 return 可能跳過 super.tearDown()

> 在 `tearDown()` 中，當條件成立時直接 `return`，這會跳過後續的 `app.terminate()` 和 `super.tearDown()`。若 `super.tearDown()` 包含必要的清理（如釋放資源、重設狀態），可能導致測試環境污染。建議改為 `if`/`else` 結構，確保 `super.tearDown()` 總是被呼叫。

finding 片段：`if self.name.contains("testSelectBottomPlacement") || iPad() { ⏎ // Toolbar option not available for iPad, so the theme is not changed there. ⏎ return ⏎ } else {`

## P0374

**GT**（rule）Unused constant fails linting check

> The rule requires that all staged files pass linting checks (including Biome's noUnusedVariables rule) before commit, but an unused constant UNUSED_CONSTANT was introduced that would cause 'biome lint --error-on-warnings' to fail

GT 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

**finding**（`packages/features/feature-opt-in/config.ts:4`，距錨點 0 行）未使用的常數 UNUSED_CONSTANT 應移除

> 新增的 `UNUSED_CONSTANT` 沒有被任何地方使用，且註解也說「Unused import that should be caught by linting」。這會觸發 lint 錯誤，並增加程式碼噪音。

**建議修法**：直接刪除此常數。

finding 片段：`// Unused import that should be caught by linting ⏎ const UNUSED_CONSTANT = "this-should-be-removed";`

## P0375

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:13`，距錨點 26 行）全域 mock 行為變更可能影響未修改的測試

> 全域 mock 原本在沒有 namespace 時直接回傳 key，現在改為一律加上 namespace 前綴（若存在）。這會改變所有依賴全域 mock 的測試行為，可能導致大量測試失敗。建議先執行完整測試套件確認影響範圍，或考慮保留舊行為作為預設，僅在需要時才加上前綴。

finding 片段：`const fullKey = ns ? `${ns}.${key}` : key`

## P0376

**GT**（func）Date filter includes today's emails instead of excluding them

> The filter in #getHighestCount() uses `created_at:<=` which includes today's date, but the docstring explicitly states it should exclude today. This causes the method to potentially return today's partial email count instead of the previous day's complete count. When emails are sent early in the day, this will result in a lower base count for warmup limit calculations, causing the domain warming progression to restart or regress unexpectedly. This breaks the intended day-over-day scaling behavior where each day's limit should be based on the previous day's complete sending volume.

GT 片段：`async #getHighestCount(): Promise<number> { ⏎ const result = await this.#emailModel.findPage({ ⏎ filter: `created_at:<=${new Date().toISOString().split('T')[0]}`, ⏎ order: 'csd_email_count DESC',`

**finding**（`ghost/core/core/server/services/email-service/DomainWarmingService.ts:111`，距錨點 7 行）`get` 方法可能不存在於回傳的資料物件

> `result.data[0].get('csd_email_count')` 假設 `data` 陣列中的元素具有 `get` 方法。若 `findPage` 回傳的是純物件而非模型實例，將導致錯誤。建議確認 `findPage` 的回傳型別，或改用屬性存取（如 `result.data[0].csd_email_count`）。

finding 片段：`const count = result.data[0].get('csd_email_count');`

## P0377

**GT**（func）Missing error source for Plist variant breaks error chain

> The Error::source() implementation is missing a case for Error::Plist, which wraps a plist::Error. This breaks error chain propagation when plist parsing or writing fails. The Plist variant is used for reading and writing application configuration files and provisioning profiles, making it one of the most commonly encountered errors. Without proper error source propagation, debugging tools and error context mechanisms lose access to the underlying plist parsing errors, making it difficult to diagnose configuration file issues.

GT 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

**finding**（`crates/tauri-macos-sign/src/lib.rs:80`，距錨點 0 行）Error::source() 未涵蓋所有可提供來源的變體

> 手動實作的 `source()` 僅回傳 `TempDir`、`FailedToUploadApp`、`CommandFailed`、`Fs` 的底層錯誤，但 `Plist`、`X509Certificate`、`FailedToCreateSelfSignedCertificate`、`FailedToEncodeDER` 等變體也包含底層錯誤，卻未回傳。這會讓使用 `Error::source()` 的錯誤鏈走訪中斷，影響錯誤診斷。建議為所有包含底層錯誤的變體實作 `source()`。

finding 片段：`impl std::error::Error for Error { ⏎ fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { ⏎ match self { ⏎ Error::TempDir(e) => Some(e),`

## P0378

**GT**（func）Missing defaultNs parameter in useTranslation mock breaks namespace support

> The `createUseTranslationMock` function's `useTranslation` hook no longer accepts or uses the `defaultNs` parameter that was passed to it. In the original implementation, `useTranslation(defaultNs?: string)` would pass this parameter to `createTFunction`, enabling proper namespace handling for components that call `useTranslation('pluginNamespace')`. Without this parameter propagation, any component or test that relies on a default namespace will have all translations fall back to keys without the namespace prefix, breaking translation lookups and causing tests to fail or display incorrect translation keys.

GT 片段：`export function createUseTranslationMock(translations: TranslationMap = {}) { ⏎ return { ⏎ useTranslation: () => ({ ⏎ t: createTFunction(translations),`

**finding**（`web/test/i18n-mock.ts:10`，距錨點 29 行）缺少輔助函式的單元測試

> 新增的 `createTFunction`、`createUseTranslationMock`、`createTransMock` 等函式沒有對應的測試。建議補上單元測試，確保其行為符合預期，特別是參數處理和 fallback 邏輯。

finding 片段：`export function createTFunction(translations: TranslationMap, defaultNs?: string) {`

## P0379

**GT**（func）Inverted reply discard logic causes test infrastructure failure

> The condition for discarding replies is inverted - replies are discarded when count is NOT a multiple of frequency (!=), rather than when it IS a multiple (==). This causes the test to read and discard replies at the wrong times, leading to a buffer overflow of unread replies. The discard_replies_every helper is called throughout the test suite after batches of Redis commands to prevent reply buffer buildup. With this bug, replies accumulate in the buffer instead of being cleared, causing test hangs or failures when the client tries to send new commands with a full reply buffer.

GT 片段：`proc discard_replies_every {rd count frequency discard_num} { ⏎ if {$count % $frequency != 0} { ⏎ for {set k 0} {$k < $discard_num} {incr k} { ⏎ $rd read ; # Discard replies`

**finding**（`tests/unit/memefficiency.tcl:70`，距錨點 0 行）discard_replies_every 函式參數名稱可能造成混淆

> 新定義的 `discard_replies_every` 函式參數 `frequency` 和 `discard_num` 的命名可能不夠清晰。`frequency` 實際上是「每多少筆丟棄一次」，而 `discard_num` 是「每次丟棄的回覆數」。建議改名為 `discard_interval` 和 `replies_per_discard` 以提高可讀性。

finding 片段：`proc discard_replies_every {rd count frequency discard_num} {`

## P0380

**GT**（func）Missing interpolation variable in newsletter unsubscribe message

> The translation for the key '{memberEmail} will no longer receive {newsletterName} newsletter.' in portal.json is missing the {newsletterName} interpolation variable. The Chinese translation only includes '{memberEmail}将不会再收到新闻信。' which omits the newsletter name placeholder. This means when users unsubscribe from a specific newsletter, they won't see which newsletter they're unsubscribing from, leading to confusion and potential accidental unsubscriptions. The translation should include both {memberEmail} and {newsletterName} variables to match the English source and maintain functional parity.

GT 片段：`"{amount} off forever.": "永久减免{amount}", ⏎ "{discount}% discount": "{discount}% 折扣", ⏎ "{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。", ⏎ "{memberEmail} will no longer receive emails when someone replies to your comments.": "{memberEmail}将不会再收到评论回复提醒邮件。`

**finding**（`ghost/i18n/locales/zh/portal.json:9`，距錨點 0 行）翻譯遺漏變數 {newsletterName}

> 翻譯中移除了 {newsletterName} 變數，可能導致使用者無法知道是哪個新聞信。建議保留變數以提供完整資訊。

finding 片段：`"{memberEmail} will no longer receive {newsletterName} newsletter.": "{memberEmail}将不会再收到新闻信。"`

## P0381

**GT**（func）Incorrect boolean operator in regex validation

> The test assertion uses AND (&&) operator instead of OR (||) when checking if the log message matches either the old or new CSP error pattern. This causes the test to fail because a log message cannot simultaneously match both regex patterns - they represent different browser error message formats. The original intent was to accept either format, but the AND operator requires both patterns to match at the same time, which is impossible. This will cause the test to fail even when receiving a valid CSP error message in either format.

GT 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

**finding**（`src/Components/test/E2ETest/ServerExecutionTests/WebSocketCompressionTests.cs:107`，距錨點 0 行）測試斷言邏輯變更可能導致測試無法正確捕捉錯誤

> 原本使用 `Assert.Matches(ParseErrorMessage(), logs[0].Message)` 檢查單一正則表達式，現在改為同時檢查兩個正則表達式（`ParseErrorMessageRegexOld` 和 `ParseErrorMessageRegexNew`）都必須匹配。這可能過於嚴格：如果實際錯誤訊息只符合其中一種模式，測試就會失敗。請確認是否應使用 `||` 而非 `&&`，或者是否預期錯誤訊息同時包含兩種模式。

finding 片段：`Assert.True( ⏎ ParseErrorMessageRegexOld.IsMatch(logs[0].Message) && ⏎ ParseErrorMessageRegexNew.IsMatch(logs[0].Message), ⏎ $"Expected log message to match one of the CSP error patterns: {ParseErrorMessageRegexOld} or {ParseErrorMessageRegexNew}. Actual: {logs[0].Message}");`

## P0382

**GT**（rule）Obfuscated SMTP class selection logic

> The rule requires code to maintain readable control flow and avoid clever hacks. The code uses a ternary expression to dynamically select and instantiate an SMTP class in a single line, making the logic harder to understand and maintain compared to a straightforward if-else structure.

GT 片段：`# Use ternary to select SMTP class based on TLS mode ⏎ smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host ⏎ )`

**finding**（`api/libs/smtp.py:28`，距錨點 0 行）local_hostname 參數傳遞空字串可能導致 SMTP 連線失敗

> 程式碼使用 `local_host or None` 將空字串轉為 None，但 smtplib.SMTP 的 local_hostname 參數若為 None，會使用 socket.getfqdn() 取得本機主機名稱。若設定 SMTP_LOCAL_HOSTNAME 為空字串，原本意圖可能是使用預設值，但傳遞 None 會觸發 getfqdn()，可能導致 DNS 查詢延遲或失敗。建議明確處理空字串，例如直接傳遞 local_host（若為空字串則由 smtplib 自行處理）或設定為 None 前先檢查。

finding 片段：`smtp = (smtplib.SMTP_SSL if (self.use_tls and not self.opportunistic_tls) else smtplib.SMTP)( ⏎ self.server, self.port, timeout=10, local_hostname=local_host or None ⏎ )`

## P0383

**GT**（func）Incorrect token in moduleLoader breaks DI resolution

> The moduleLoader exports the wrong token for dependency resolution. The FeaturesRepository class is bound to the container using FLAGS_DI_TOKENS.FEATURES_REPOSITORY (line 14: token parameter in bindModuleToClassOnToken), but the moduleLoader.token is set to FLAGS_DI_TOKENS.FEATURES_REPOSITORY_MODULE (line 20). When consumers try to retrieve the FeaturesRepository from the container using moduleLoader.token, the lookup will fail because the binding was registered under a different token. This causes a runtime error when getFeaturesRepository() or any service depending on FeaturesRepository attempts to resolve it from the DI container.

GT 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

**finding**（`packages/features/di/modules/FeaturesRepository.ts:19`，距錨點 0 行）moduleLoader.token 可能設定錯誤

> 在 `FeaturesRepository.ts` 中，`moduleLoader` 的 `token` 屬性被設定為 `moduleToken`，但其他模組（如 `FeatureOptInService.ts`）的 `moduleLoader.token` 是設定為實際的服務 token。這可能導致依賴此模組的容器在解析時找不到正確的 token。

建議確認 `moduleLoader.token` 的預期用途：若它代表模組本身的 token，則應使用 `moduleToken`；若代表模組提供的服務 token，則應使用 `token`。請參考其他模組的實作方式，確保一致性。

finding 片段：`export const moduleLoader: ModuleLoader = { ⏎ token: moduleToken, ⏎ loadModule, ⏎ };`

## P0384

**GT**（rule）Any type used for selector parameter

> The rule requires using specific types instead of 'any' annotations. The selector parameter uses 'any' instead of a proper function type signature.

GT 片段：`export function usePluginPageContext(selector: any) { ⏎ return useContextSelector(PluginPageContext, selector) ⏎ }`

**finding**（`web/app/components/plugins/plugin-page/context.tsx:51`，距錨點 0 行）selector 參數型別從函式放寬為 any，喪失型別安全

> `usePluginPageContext` 的 selector 參數型別從 `(value: PluginPageContextValue) => any` 改為 `any`。這會讓呼叫端可以傳入任何值，包括非函式，可能導致執行時期錯誤（例如 `useContextSelector` 內部呼叫 selector 時拋出錯誤）。建議保留原本的函式型別，或至少使用 `(value: PluginPageContextValue) => any` 以維持型別檢查。

finding 片段：`export function usePluginPageContext(selector: any) {`

## P0385

**GT**（rule）Missing Mozilla Public License header

> The rule requires that every .swift file begins with the exact Mozilla Public License header comment block at the top of the file. This file is missing the required header entirely.

GT 片段：`import ContentBlockingGenerator ⏎ @main ⏎ public struct MainContentBlockerGenerator { ⏎ // FXIOS-14548 ContentBlockerGenerator is not thread safe`

**finding**（`BrowserKit/Sources/ExecutableContentBlockingGenerator/MainContentBlockerGenerator.swift:6`，距錨點 0 行）nonisolated(unsafe) 可能隱藏執行緒安全問題

> 使用 `nonisolated(unsafe)` 來繞過 Swift 6 的嚴格並發檢查，但若 `ContentBlockerGenerator` 真的非執行緒安全，此標註只是暫時壓制問題。建議確認其執行緒安全性，或改用其他並發安全機制。

finding 片段：`nonisolated(unsafe) static let generator = ContentBlockerGenerator.factory()`

## P0386

**GT**（func）Inverted mouse button state mapping in tray icon event conversion

> The From implementation for converting tray_icon::MouseButtonState to MouseButtonState has the Up and Down states inverted. When a mouse button is released (Up) from the underlying tray_icon library, it's incorrectly mapped to Down in the Tauri TrayIconEvent, and vice versa. This will cause all tray icon click handlers to receive the opposite button state than what actually occurred, breaking event handling logic that depends on distinguishing between button press and release events. The new_click factory method added in this PR uses MouseButtonState::default() which is Up, but when real events are converted through this From implementation, the states will be backwards.

GT 片段：`impl From<tray_icon::MouseButtonState> for MouseButtonState { ⏎ fn from(value: tray_icon::MouseButtonState) -> Self { ⏎ match value { ⏎ tray_icon::MouseButtonState::Up => MouseButtonState::Down,`

**finding**（`crates/tauri/src/tray/mod.rs:34`，距錨點 0 行）MouseButtonState 的 From 實作將 Up/Down 對應反轉

> 在 `From<tray_icon::MouseButtonState>` 的實作中，原本 `Up` 對應到 `MouseButtonState::Up`、`Down` 對應到 `MouseButtonState::Down`，但此變更將兩者對調，導致外部事件轉換後狀態完全相反。例如使用者放開滑鼠按鈕時，應用程式會收到 `Down` 狀態。請將 match 分支改回正確對應。

finding 片段：`tray_icon::MouseButtonState::Up => MouseButtonState::Down, ⏎ tray_icon::MouseButtonState::Down => MouseButtonState::Up,`

## P0387

**GT**（rule）Types package imports from features

> The rule requires that lower-level packages do not import from higher-level packages. The platform types package should not import from the features package as this violates the dependency hierarchy.

GT 片段：`import { ApiProperty } from "@nestjs/swagger"; ⏎ import { Type } from "class-transformer"; ⏎ import { IsEnum, ValidateNested, IsNumber, IsString, IsOptional, IsUrl } from "class-validator"; ⏎ import { SUCCESS_STATUS, ERROR_STATUS } from "@calcom/platform-constants";`

**finding**（`packages/platform/types/bookings/2024-08-13/outputs/get-booking-recordings.output.ts:6`，距錨點 0 行）新增的 BookingRepository import 似乎未使用

> 在 `get-booking-recordings.output.ts` 中新增了 `import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`，但在此檔案中沒有看到使用 `BookingRepository` 的地方。這可能是多餘的 import，建議移除以避免 lint 錯誤。

finding 片段：`import type { BookingRepository } from "@calcom/features/bookings/lib/BookingRepository";`

## P0388

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:38`，距錨點 3 行）缺少對 teamId 的擁有權或存在性檢查

> 控制器直接呼叫 `TeamService.createInvite(teamId)`，但沒有先驗證目前使用者是否屬於該團隊或團隊是否存在。雖然有 RolesGuard，但 RolesGuard 可能只檢查全域角色，而非針對特定團隊的成員資格。

失敗情境：使用者可能對任意 teamId 建立邀請，即使不是該團隊成員。

建議：在服務層或控制器中加入團隊成員資格檢查。

finding 片段：`const result = await TeamService.createInvite(teamId);`

## P0389

**GT**（rule）Out-of-bounds write to argv array may trigger -Warray-bounds (and is UB)

> The code declares `robj *argv[5];` (valid indices 0..4) but then writes `argv[5]` and passes an argument count of 6 to `alsoPropagate`. This is undefined behavior and can also trigger compiler diagnostics such as `-Warray-bounds`, which will fail the build under `-Werror`.

GT 片段：`/* Propagate HPEXPIREAT */ ⏎ robj *argv[5]; ⏎ argv[0] = shared.hpexpireat; ⏎ argv[1] = c->argv[1];`

**finding**（`src/t_hash.c:2309`，距錨點 0 行）手動傳播 HPEXPIREAT 時未處理 createStringObjectFromLongLong 可能失敗的情況

> `createStringObjectFromLongLong(expireat)` 可能因為記憶體不足而回傳 NULL，但程式碼未檢查就直接指派給 argv[2]，後續 alsoPropagate 可能對 NULL 物件進行操作，導致崩潰。

失敗情境：在記憶體極度不足時，執行 HINCRBYFLOAT 且欄位有過期時間。

建議修正：檢查回傳值，若為 NULL 則回傳錯誤或採取其他處理。

finding 片段：`argv[2] = createStringObjectFromLongLong(expireat);`

## P0390

**GT**（func）Architecture mapping bypassed in linuxdeploy download URL

> The download URL for linuxdeploy now uses the raw `arch` variable instead of `linuxdeploy_arch`, bypassing the critical i686→i383 architecture translation that happens on line 235. When building for i686 architecture, the code will attempt to download from a URL containing "i686" instead of "i383", which will fail because the binary is not available at that URL. This breaks AppImage bundling specifically for 32-bit x86 systems, an architecture that requires special handling in the tauri-apps binary releases repository.

GT 片段：`let linuxdeploy_arch = if arch == "i686" { "i383" } else { arch }; ⏎ let linuxdeploy = tools_path.join(format!("linuxdeploy-{linuxdeploy_arch}.AppImage")); ⏎ if !linuxdeploy.exists() { ⏎ let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxde`

**finding**（`crates/tauri-bundler/src/bundle/linux/appimage/mod.rs:238`，距錨點 0 行）linuxdeploy 下載 URL 中的 arch 變數可能錯誤

> 在 `prepare_tools` 中，原本的 linuxdeploy 下載 URL 使用 `linuxdeploy_arch`（其中 i686 被替換為 i383），但此 PR 將其改為直接使用 `arch`。這可能導致在 i686 架構下下載錯誤的檔案（i686 而非 i383），造成後續執行失敗。

建議確認 `linuxdeploy` 的實際發布架構命名，並保留原本的 `linuxdeploy_arch` 邏輯。

finding 片段：`let data = download(&format!("https://github.com/tauri-apps/binary-releases/releases/download/linuxdeploy/linuxdeploy-{arch}.AppImage"))?;`

## P0391

**GT**（func）Incorrect permission level on recordings endpoint

> The GET /bookings/:bookingUid/recordings endpoint is decorated with @Permissions([BOOKING_WRITE]) which requires write permissions to read recordings. This is incorrect - read-only operations should use BOOKING_READ permission. As a result, users with only read permissions (who should be able to view recordings) will be denied access with a 403 Forbidden error, while users with write permissions can unexpectedly access recordings even if that wasn't intended for their role.

GT 片段：`@Get("/:bookingUid/recordings") ⏎ @Pbac(["booking.readRecordings"]) ⏎ @Permissions([BOOKING_WRITE]) ⏎ @UseGuards(ApiAuthGuard, BookingUidGuard, BookingPbacGuard)`

**finding**（`apps/api/v2/src/ee/bookings/2024-08-13/controllers/bookings.controller.ts:227`，距錨點 10 行）getRecordings 呼叫缺少 await，可能回傳 Promise 而非實際資料

> 在 `getBookingRecordings` 方法中，`this.calVideoService.getRecordings(bookingUid)` 沒有加上 `await`。如果 `getRecordings` 是非同步方法，則 `recordings` 會是 Promise 物件，而非實際的錄音資料陣列。這會導致 API 回傳錯誤的資料格式，且可能造成序列化問題。請確認 `getRecordings` 是否為 async，若是則必須加上 `await`。

finding 片段：`const recordings = this.calVideoService.getRecordings(bookingUid);`

## P0392

**GT**（func）Node execution started before being enqueued and marked as TAKEN

> The `start_execution` method is called before `enqueue_node`, which violates the expected state machine flow. The node is added to the `_executing_nodes` set before it's marked as TAKEN or added to the ready queue. This creates a race condition where concurrent operations might observe a node in the executing state while it's still in UNKNOWN state, leading to inconsistent state validation failures. The correct order should be: first enqueue (which marks as TAKEN and adds to queue), then start execution tracking.

GT 片段：`# If any edge is taken, node may still execute ⏎ if edge_states["has_taken"]: ⏎ # Start execution and enqueue node ⏎ print(f"Starting execution for node: {downstream_node_id}")`

**finding**（`api/core/workflow/graph_engine/graph_traversal/skip_propagator.py:62`，距錨點 0 行）新增的 print 陳述式可能造成 log 污染

> 在生產程式碼中使用 `print` 會將訊息輸出到 stdout，可能干擾正常的 log 格式或造成不必要的輸出。建議改用正式的 logging 模組，或移除該陳述式。

finding 片段：`print(f"Starting execution for node: {downstream_node_id}")`

## P0393

**GT**（func）Insufficient authorization - regular members can create invite links

> The endpoint uses @Roles('TEAM_MEMBER') which allows any team member to create invite links, but the business logic requires admin permissions for this sensitive operation. The e2e tests verify that only admins should be able to create invites (returning 403 for regular members), but this permission check is too permissive. This security issue allows unauthorized users to generate invite tokens that could be used to add members to teams without proper authorization.

GT 片段：`@Post("/invite") ⏎ @Roles("TEAM_MEMBER") ⏎ @ApiOperation({ summary: "Create team invite link" }) ⏎ @HttpCode(HttpStatus.OK)`

**finding**（`apps/api/v2/src/modules/teams/invite/controllers/teams-invite.controller.ts:32`，距錨點 0 行）權限設定過於寬鬆：TEAM_MEMBER 即可建立邀請，但測試預期非管理員應被拒絕

> 控制器使用 `@Roles("TEAM_MEMBER")`，這表示任何團隊成員（包括 MEMBER）都可以呼叫此端點。然而，端對端測試中明確預期非管理員成員應收到 403。這可能導致權限提升漏洞：一般成員可以建立邀請連結，進而邀請他人加入團隊。

失敗情境：一個非管理員的團隊成員呼叫此 API，成功建立邀請連結，違反了團隊管理員的權限控制。

建議：將角色改為 `TEAM_ADMIN` 或更嚴格的權限，並確認測試與實作一致。

finding 片段：`@Roles("TEAM_MEMBER")`

## P0394

**GT**（func）Internal helper function clusterDeleteKeysInUnownedSlots missing static declaration

> The function clusterDeleteKeysInUnownedSlots() is defined and used only within cluster.c (no external callers, not declared in any header file), but lacks the 'static' keyword. According to AGENTS.md Rule #7, all internal helper functions that are not part of the public API must be declared static to enforce proper encapsulation and prevent symbol pollution. This violation could lead to naming conflicts in large codebases and breaks the repository's explicit encapsulation requirements.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2137`，距錨點 9 行）clusterCommonInit() 呼叫順序可能導致未初始化相依性

> clusterCommonInit() 呼叫 resetClusterStats() 和 asmInit()，但這兩個函式可能依賴其他尚未初始化的全域狀態（例如 server.cluster 或 asm 相關結構）。原本在 clusterInit() 中呼叫的順序是 resetClusterStats() 在 clusterUpdateMyselfIp() 等之後，asmInit() 在最後。現在提前到 clusterInit() 之前，可能造成相依性問題。建議確認這些函式的相依性，或調整呼叫順序。

finding 片段：`void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat)); ⏎ resetClusterStats(); ⏎ asmInit();`

## P0395

**GT**（func）Inverted reader mode telemetry state tracking

> The recordReaderModeTelemetry function has inverted logic for determining reader mode state. When the reader mode is 'available' (about to be enabled), it reports false instead of true, and for all other states it reports true instead of false. This causes telemetry data to incorrectly track reader mode usage patterns - reporting that reader mode is being disabled when it's actually being enabled and vice versa. This will corrupt analytics data about reader mode feature usage.

GT 片段：`private func recordReaderModeTelemetry(state: AppState, windowUUID: WindowUUID) { ⏎ guard let toolbarState = state.screenState(ToolbarState.self, for: .toolbar, window: windowUUID) else { return } ⏎ let isReaderModeEnabled = switch toolbarState.addressToolbar.readerModeState { ⏎ case .available: fal`

**finding**（`firefox-ios/Client/Frontend/Browser/Toolbars/Redux/ToolbarMiddleware.swift:524`，距錨點 0 行）readerModeState 的 isEnabled 判斷反轉可能導致遙測錯誤

> 原本 `case .available: true` 改為 `case .available: false`，且 `default: false` 改為 `default: true`。這會讓閱讀模式按鈕的遙測事件記錄相反的啟用狀態，影響數據分析。請確認此變更是否為移除 QR code 時的必要調整，若非必要請還原。

finding 片段：`case .available: false // will be enabled after action gets executed ⏎ default: true`

## P0396

**GT**（func）Variable scope error causes UnboundLocalError when template rendering succeeds

> The length validation check was moved inside the try block before the except clause, creating a critical variable scope issue. When `render_template()` succeeds, the `rendered` variable is assigned inside the try block. However, if the length check passes and no exception occurs, execution continues to the return statement outside the try-except block which references `rendered`. In Python, this creates an undefined variable scenario where `rendered` is only defined within the try block scope but accessed outside it, resulting in UnboundLocalError at runtime whenever template rendering succeeds without exceeding length limits.

GT 片段：`try: ⏎ rendered = self._template_renderer.render_template(self.node_data.template, variables) ⏎ if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH: ⏎ return NodeRunResult(`

**finding**（`api/core/workflow/nodes/template_transform/template_transform_node.py:68`，距錨點 0 行）render_template 回傳 None 時 len() 會拋出 TypeError

> 在 `_run` 中，`rendered = self._template_renderer.render_template(...)` 後直接呼叫 `len(rendered)`。但 `CodeExecutorJinja2TemplateRenderer.render_template` 在 `result.get("result")` 為 None 時會回傳 None（見 template_renderer.py 第 36 行），此時 `len(None)` 會拋出 `TypeError`，且未被 `except TemplateRenderError` 捕捉，導致節點執行崩潰。建議在 renderer 中對 None 結果拋出 `TemplateRenderError`，或在 `_run` 中檢查 `rendered is None` 並回傳失敗。

finding 片段：`rendered = self._template_renderer.render_template(self.node_data.template, variables) ⏎ if len(rendered) > MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH:`

## P0397

**GT**（rule）Cross-field validation using field_validator incorrectly

> The validation logic checks both bucket_folder and bucket fields (cross-field validation) but uses @field_validator instead of @model_validator, causing order-dependent validation issues and accessing potentially unvalidated fields via info.data

GT 片段：`@field_validator("bucket_folder") ⏎ @classmethod ⏎ def _bucket_folder_suffix(cls, value, info): ⏎ """`

**finding**（`src/integrations/prefect-gcp/prefect_gcp/cloud_storage.py:734`，距錨點 21 行）子字串檢查可能誤判非前綴路徑

> `if self.bucket_folder and self.bucket_folder in path:` 使用子字串檢查，若路徑中段包含 bucket_folder 字串但並非前綴，會錯誤地跳過前綴處理。例如 bucket_folder 為 "results/"，路徑為 "myresults/file.txt" 時，`"results/" in "myresults/file.txt"` 為 True，導致回傳未加前綴的路徑，造成儲存位置錯誤。建議改為檢查 `path.startswith(self.bucket_folder)` 或使用 `PurePosixPath` 比較前綴。

finding 片段：`if self.bucket_folder and self.bucket_folder in path: ⏎ return path`

## P0398

**GT**（func）Incorrect comparison logic causes false negatives when comparing slot ranges

> The slotRangeArrayIsEqual function checks if the number of ranges are equal before normalizing and merging adjacent ranges. This causes the function to incorrectly return false (0) when comparing two slot range arrays that represent the same slots but have different numbers of ranges before merging. For example, comparing [1000-1001, 1002-1003] (2 ranges) with [1000-1003] (1 range) will return false even though they represent the same slots after merging. This breaks the task lookup functionality in asmLookupTaskBySlotRangeArray, preventing correct task identification when slot ranges are specified in different but equivalent formats.

GT 片段：`int slotRangeArrayIsEqual(slotRangeArray *slots1, slotRangeArray *slots2) { ⏎ if (slots1->num_ranges != slots2->num_ranges) return 0; ⏎ slotRangeArraySortAndMerge(slots1); ⏎ slotRangeArraySortAndMerge(slots2);`

**finding**（`src/cluster.c:1867`，距錨點 9 行）slotRangeArraySortAndMerge 未處理重疊範圍，可能導致驗證失效

> 函式僅合併相鄰範圍（prev.end + 1 == next.start），但未處理重疊範圍（例如 100-200 和 150-250）。若輸入包含重疊範圍，合併後仍保留重疊，後續 validateSlotRanges 會偵測到重疊並回傳錯誤，但若重疊範圍在合併後變成相鄰（例如 100-200 和 201-300 合併為 100-300），則可能掩蓋原始的重疊問題。此外，若重疊範圍未合併，validateSlotRanges 仍會偵測到，但錯誤訊息可能不如預期。建議在合併前先檢查重疊，或明確規定重疊範圍為非法輸入。

finding 片段：`if (slots->ranges[idx].end + 1 == slots->ranges[i].start) ⏎ slots->ranges[idx].end = slots->ranges[i].end; ⏎ else ⏎ slots->ranges[++idx] = slots->ranges[i];`

## P0399

**GT**（func）Premature null assignment in TryGetValidatableTypeInfo violates out parameter semantics

> The validatableTypeInfo out parameter is now being set to null at the beginning of the method before iterating through resolvers, rather than after the loop when no resolver was found. While this may appear equivalent, it violates proper out parameter semantics and the contract implied by [NotNullWhen(true)]. If a resolver incorrectly returns true while leaving the out parameter unassigned or null (a buggy resolver implementation), the early null assignment would mask this contract violation. Additionally, this creates unnecessary assignment overhead since the parameter will be overwritten by successful resolvers. The original pattern of assigning null only when no resolver succeeds is more semantically correct and provides better detection of misbehaving resolvers.

GT 片段：`public bool TryGetValidatableTypeInfo(Type type, [NotNullWhen(true)] out IValidatableInfo? validatableTypeInfo) ⏎ { ⏎ validatableTypeInfo = null; ⏎ foreach (var resolver in Resolvers)`

**finding**（`src/Validation/src/ValidationOptions.cs:46`，距錨點 0 行）out 參數初始化位置變更可能影響行為

> 在 `TryGetValidatableTypeInfo` 方法中，原本在迴圈後才將 `validatableTypeInfo` 設為 null，現在移到方法開頭。這在功能上等價，但若未來在迴圈前加入其他邏輯，可能造成影響。建議確認此變更是否必要，或僅為程式碼整理。

finding 片段：`validatableTypeInfo = null;`

## P0400

**GT**（rule）Non-static internal helper function exported from cluster.c

> `clusterDeleteKeysInUnownedSlots()` is introduced as a file-local helper and is only used within `src/cluster.c` (called by `verifyClusterConfigWithData()`), but it is declared without `static`, unnecessarily exporting the symbol outside this compilation unit. Per the rule, internal helper functions must be declared `static`.

GT 片段：`void clusterDeleteKeysInUnownedSlots(void) { ⏎ if (clusterNodeIsSlave(getMyClusterNode())) return; ⏎ /* Check that all the slots we have keys for are assigned to us. Otherwise, ⏎ * delete the keys. */`

**finding**（`src/cluster.c:2137`，距錨點 9 行）clusterCommonInit() 呼叫順序可能導致未初始化相依性

> clusterCommonInit() 呼叫 resetClusterStats() 和 asmInit()，但這兩個函式可能依賴其他尚未初始化的全域狀態（例如 server.cluster 或 asm 相關結構）。原本在 clusterInit() 中呼叫的順序是 resetClusterStats() 在 clusterUpdateMyselfIp() 等之後，asmInit() 在最後。現在提前到 clusterInit() 之前，可能造成相依性問題。建議確認這些函式的相依性，或調整呼叫順序。

finding 片段：`void clusterCommonInit(void) { ⏎ server.cluster_slot_stats = malloc(CLUSTER_SLOTS*sizeof(clusterSlotStat)); ⏎ resetClusterStats(); ⏎ asmInit();`
