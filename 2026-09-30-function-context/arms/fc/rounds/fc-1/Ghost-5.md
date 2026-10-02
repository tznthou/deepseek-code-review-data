<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案名稱改為 kebab-case，並更新所有 import 路徑，同時新增 ESLint 規則強制執行此命名慣例。此外，也包含一些功能性變更：在提交 email 前加上 trim、移除 minimal 模式下的 setLoading(false)、調整 getUrlHistory 的回傳邏輯，以及版本號更新。整體風險中等，需注意 email trim 可能影響既有行為、getUrlHistory 的回傳型別變更，以及 ESLint 規則可能導致其他檔案 CI 失敗。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-view.tsx:56` | 提交前對 email 進行 trim 可能改變既有行為 | 0.80 |
| ⚠️ | Major | `apps/signup-form/src/utils/helpers.tsx:47` | getUrlHistory 回傳型別可能為 undefined | 0.75 |
| 🔸 | Minor | `apps/signup-form/.eslintrc.cjs:24` | 新增 ESLint 規則可能導致其他檔案 CI 失敗 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> 提交前對 email 進行 trim 可能改變既有行為</summary>

在 `submitHandler` 中，`onSubmit({email: email.trim()})` 會移除 email 前後的空白字元。這可能導致原本包含前後空白的 email 被視為有效（如果驗證邏輯允許），但實際上送出的是修剪後的字串。若後端依賴原始輸入（例如用於比對或記錄），可能造成不一致。建議確認此變更是否為預期行為，並考慮在驗證前進行 trim，或保留原始輸入。

**判斷依據**：diff 中 `-        onSubmit({email});` 改為 `+        onSubmit({email: email.trim()});`

</details>

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/utils/helpers.tsx:47</code> getUrlHistory 回傳型別可能為 undefined</summary>

在 `getUrlHistory` 中，原本的寫法會在 `history` 存在時回傳 `history`，否則繼續執行後面的邏輯。修改後直接 `return history;`，但 `getDefaultUrlHistory()` 的回傳型別可能是 `URLHistory | undefined`（從函式定義推斷）。如果 `history` 為 `undefined`，則此函式會回傳 `undefined`，而呼叫端可能預期一定拿到陣列，導致後續處理出錯。建議檢查 `getDefaultUrlHistory` 的回傳型別，並在必要時提供預設值或調整型別。

**判斷依據**：diff 中 `-            if (history) {
-                return history;
-            }` 改為 `+            return history;`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/.eslintrc.cjs:24</code> 新增 ESLint 規則可能導致其他檔案 CI 失敗</summary>

新增的 `'ghost/filenames/match-regex': ['error', '^[a-z0-9.-]+$', false]` 規則會強制所有檔案名稱符合 kebab-case。如果專案中仍有其他檔案未遵循此命名（例如測試檔案或設定檔），可能會在 CI 中報錯。建議先確認所有檔案已符合規則，或將規則設為 warning 並逐步修正。

**判斷依據**：diff 中新增此規則

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7627 (cache hit 1536) ｜ completion tokens 847 ｜ PR #5</sub>