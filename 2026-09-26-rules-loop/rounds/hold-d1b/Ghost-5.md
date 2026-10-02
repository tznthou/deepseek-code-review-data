<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 應用程式的檔案重新命名為 kebab-case，並更新相關 import 路徑，同時包含一些程式碼變更（移除 setLoading(false)、email trim、getUrlHistory 簡化）及文件更新。整體風險低，但發現兩處違反 repo 規範：R18（使用雙引號字串）與 R21（使用寬鬆相等運算子）。建議修正後再合併。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `apps/signup-form/src/utils/helpers.tsx:20` | [R18] 使用雙引號字串，違反單引號規範 | 0.95 |
| 🔸 | Minor | `apps/signup-form/src/utils/helpers.tsx:43` | [R21] 使用寬鬆相等運算子，違反嚴格相等規範 | 0.95 |

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/utils/helpers.tsx:20</code> [R18] 使用雙引號字串，違反單引號規範</summary>

此處將原本的單引號字串改為雙引號，違反 repo 規範 R18（Code Must Use Single Quotes for Strings）。建議改回單引號。

**判斷依據**：diff 中顯示 `-    const STORAGE_KEY = 'ghost-history';` 改為 `+    const STORAGE_KEY = "ghost-history";`，違反 R18。

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/src/utils/helpers.tsx:43</code> [R21] 使用寬鬆相等運算子，違反嚴格相等規範</summary>

此處使用 `==` 比較 `window.location.host` 與 `new URL(siteUrl).host`，違反 repo 規範 R21（Code Must Use Strict Equality Operators）。建議改用 `===`。

**判斷依據**：diff 中顯示此行未變更，但此 PR 觸及此檔案，且該行違反 R21。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 8639 (cache hit 8576) ｜ completion tokens 492 ｜ PR #5</sub>