<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 旨在允許 JS root components 在 circuit 重啟時重新初始化。主要變更在 JSRootComponents.ts 中，透過新增 currentRendererId 與 hasInitializedJsComponents 來控制初始化流程。整體方向合理，但存在一個潛在的邏輯問題：當相同 renderer 重新啟用時，jsComponentParametersByIdentifier 並未更新，可能導致後續使用到舊的參數。此外，測試檔案移動與設定變更看似合理，但需確認測試涵蓋範圍是否足夠。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136` | 重新啟用時未更新 jsComponentParametersByIdentifier | 0.80 |

<details><summary>⚠️ <b>Major</b> — <code>src/Components/Web.JS/src/Rendering/JSRootComponents.ts:136</code> 重新啟用時未更新 jsComponentParametersByIdentifier</summary>

在 `enableJSRootComponents` 中，當 `manager && currentRendererId === rendererId` 為 false（即首次啟用或不同 renderer）時，會更新 `manager` 與 `currentRendererId`，但 `jsComponentParametersByIdentifier` 只在函式開頭指派一次，且該指派位於 `if (!hasInitializedJsComponents)` 區塊之外。這表示當相同 renderer 重新啟用時（例如 circuit 重啟），`jsComponentParametersByIdentifier` 仍保留舊的參數物件，可能導致後續動態 root component 使用到過時的參數。

建議：將 `jsComponentParametersByIdentifier = jsComponentParameters;` 移到 `if (!hasInitializedJsComponents)` 區塊內，或確保在每次啟用時都更新該變數。

**判斷依據**：diff 中顯示原本的 `jsComponentParametersByIdentifier = jsComponentParameters;` 被移除，但沒有在新的位置重新指派。在重新啟用的情境下，該變數不會被更新。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 6471 (cache hit 4224) ｜ completion tokens 491 ｜ PR #7</sub>