<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 主要將 signup-form 的檔案命名改為 kebab-case，並新增 ESLint 規則強制執行。同時包含版本號更新、README 補充發佈流程，以及兩個功能性變更：email 輸入改為 trim 後送出、移除 minimal 模式下的 setLoading(false)。整體風險低，但 email trim 的變更可能影響既有行為，且 ESLint 規則的 regex 可能過於寬鬆，建議確認。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `apps/signup-form/src/components/pages/form-view.tsx:56` | email 輸入 trim 可能改變既有行為 | 0.80 |
| 🔸 | Minor | `apps/signup-form/.eslintrc.cjs:24` | ESLint 檔案命名規則 regex 可能過於寬鬆 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>apps/signup-form/src/components/pages/form-view.tsx:56</code> email 輸入 trim 可能改變既有行為</summary>

將 `onSubmit({email})` 改為 `onSubmit({email: email.trim()})` 會移除使用者輸入的前後空白。若原本允許 email 前後有空白（例如貼上時），此變更可能導致部分使用者無法登入或收到錯誤。建議確認產品需求是否允許空白，或改為在驗證時 trim 而非送出時。

**判斷依據**：diff 中 `-        onSubmit({email});` 改為 `+        onSubmit({email: email.trim()});`

</details>

<details><summary>🔸 <b>Minor</b> — <code>apps/signup-form/.eslintrc.cjs:24</code> ESLint 檔案命名規則 regex 可能過於寬鬆</summary>

新增的規則 `'ghost/filenames/match-regex': ['error', '^[a-z0-9.-]+$', false]` 允許連續的點或連字號，例如 `foo..bar` 或 `-foo`。這可能不是預期的 kebab-case 格式。建議使用更嚴格的 regex，例如 `^[a-z0-9]+(-[a-z0-9]+)*$`。

**判斷依據**：diff 中新增的 ESLint 規則。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7627 (cache hit 7552) ｜ completion tokens 549 ｜ PR #5</sub>