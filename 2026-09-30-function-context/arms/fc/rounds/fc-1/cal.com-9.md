<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 🛑 建議修改後再合併

此 PR 將多個 WebWrapper 元件從 packages/platform/atoms 遷移至 apps/web/modules，並更新相關 import 路徑。主要風險在於 BookerWebWrapper 中移除了 useRouter 的 import 與宣告，但程式碼仍使用 router，可能導致執行時錯誤；此外 sortHosts 函式在遷移時邏輯被意外修改，可能影響排序行為。建議先修正這兩個問題再合併。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🛑 | Blocker | `apps/web/modules/bookings/components/BookerWebWrapper.tsx:4` | 移除 useRouter import 但程式碼仍使用 router | 0.95 |
| ⚠️ | Major | `packages/lib/bookings/hostGroupUtils.ts:52` | sortHosts 函式邏輯與原始版本不一致 | 0.80 |
| 🔸 | Minor | `apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52` | 動態 import 路徑可能不正確 | 0.60 |

<details><summary>🛑 <b>Blocker</b> — <code>apps/web/modules/bookings/components/BookerWebWrapper.tsx:4</code> 移除 useRouter import 但程式碼仍使用 router</summary>

在 diff 中，原本的 `import { useSearchParams, usePathname, useRouter } from "next/navigation";` 被改為 `import { useSearchParams, usePathname } from "next/navigation";`，且原本的 `const router = useRouter();` 也被移除。然而，在後續的程式碼中仍有多處使用 `router`，例如 `router.push(...)`、`router.push("/apps/categories/calendar")` 等。這會導致執行時出現 `ReferenceError: router is not defined`。

建議：保留 `useRouter` 的 import 與宣告，或改用其他方式取得 router。

**判斷依據**：diff 中移除 `useRouter` 的 import 與 `const router = useRouter();`，但程式碼中仍使用 `router.push`。

</details>

<details><summary>⚠️ <b>Major</b> — <code>packages/lib/bookings/hostGroupUtils.ts:52</code> sortHosts 函式邏輯與原始版本不一致</summary>

在遷移 sortHosts 函式時，原本在 HostEditDialogs.tsx 中的實作在 `isRRWeightsEnabled` 為 true 且權重相同時回傳 `priorityB - priorityA`，但新版本回傳 `priorityA - priorityB`，導致排序方向相反。這可能影響依權重排序的主持人清單。

建議：確認此變更是否為預期，若非預期請修正為 `priorityB - priorityA`。

**判斷依據**：原始程式碼（HostEditDialogs.tsx）中為 `return priorityB - priorityA;`，新版本改為 `return priorityA - priorityB;`。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/web/modules/event-types/components/EventTypeWebWrapper.tsx:52</code> 動態 import 路徑可能不正確</summary>

在 EventTypeWebWrapper.tsx 中，多個動態 import 的路徑從絕對路徑改為相對路徑，例如 `import("./tabs/setup/EventSetupTabWebWrapper")`。需確認這些相對路徑是否正確指向目標檔案，否則會導致模組載入失敗。

**判斷依據**：diff 中將原本的 `import("./EventSetupTabWebWrapper")` 改為 `import("./tabs/setup/EventSetupTabWebWrapper")`，需確認檔案實際位置。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 16657 (cache hit 1536) ｜ completion tokens 936 ｜ PR #9</sub>