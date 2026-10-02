<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

本次 PR 新增了 FlowIconText 元件及其 Storybook 設定，整體結構清晰。但違反了兩條 repo 規範：R10 要求測試檔案與元件同目錄，但未提供測試檔；R12 要求自動移除未使用的 import，但 flow-icon-text.tsx 中匯入了未使用的 Skeleton。建議補上測試檔並移除未使用的 import。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:6` | [R12] 未使用的 import：Skeleton | 0.95 |
| 🔸 | Minor | `ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1` | [R10] 缺少同目錄測試檔 | 0.90 |

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:6</code> [R12] 未使用的 import：Skeleton</summary>

檔案中匯入了 `Skeleton`，但在元件中並未使用。這違反了 R12（未使用的 import 必須自動移除），且會增加 bundle size。建議移除該 import。

**判斷依據**：diff 中新增的 flow-icon-text.tsx 第 6 行匯入了 Skeleton，但整個檔案中沒有使用到 Skeleton 元件。

</details>

<details><summary>🔸 <b>Minor</b> — <code>ui-v2/src/components/flows/flow-icon-text/flow-icon-text.tsx:1</code> [R10] 缺少同目錄測試檔</summary>

R10 要求每個 React 元件檔案（component.tsx）都必須在同目錄下有對應的測試檔（component.test.tsx）。此 PR 新增了 flow-icon-text.tsx，但沒有提供 flow-icon-text.test.tsx。建議補上測試檔。

**判斷依據**：diff 中只新增了 flow-icon-text.tsx、flow-icon-text.stories.tsx 和 index.ts，沒有 flow-icon-text.test.tsx。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 4292 (cache hit 4224) ｜ completion tokens 492 ｜ PR #9</sub>