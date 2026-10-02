<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了送出前禁用詞掃描功能，透過 `REVIEW_BLOCKED_TERMS` secret 在呼叫 DeepSeek API 前進行子字串比對，命中即拒送。整體設計考量周全，包含避免洩漏禁用詞本身、處理空字串與過短詞等邊界情況，並有對應的自測與文件更新。主要風險在於 workflow 中 secret 的傳遞方式，以及 Python 程式碼中潛在的效能與正確性問題。最該先修的是 `reusable-ai-review-post.yml` 中 secret 傳遞的寫法，以及 `blocked_terms_hits` 函式的效能問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `.github/workflows/reusable-ai-review-post.yml:188` | secret 傳遞方式可能導致值未正確遮蔽 | 0.90 |
| 🔸 | Minor | `.github/scripts/deepseek_review.py:211` | blocked_terms_hits 效能問題：對每個詞重複掃描整個文字 | 0.70 |
| 🔸 | Minor | `.github/scripts/deepseek_review.py:190` | load_blocked_terms 未處理可能的編碼問題 | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>.github/workflows/reusable-ai-review-post.yml:188</code> secret 傳遞方式可能導致值未正確遮蔽</summary>

在 `env:` 區塊中直接使用 `${{ secrets.REVIEW_BLOCKED_TERMS }}` 將 secret 傳入環境變數。GitHub Actions 會自動遮蔽 secret 的值，但若 secret 包含換行符，可能導致遮蔽失效或產生非預期行為。建議改用 `fromJSON` 或將 secret 寫入檔案後讀取，或確認 secret 格式符合預期。

**判斷依據**：diff 中新增的 env 設定，直接將 secret 傳入環境變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/scripts/deepseek_review.py:211</code> blocked_terms_hits 效能問題：對每個詞重複掃描整個文字</summary>

`blocked_terms_hits` 對每個詞都執行一次 `term in lowered`，若詞的數量多或文字很長，可能造成不必要的效能負擔。建議改用 Aho-Corasick 或正規表示式一次掃描，或至少先將文字轉為小寫一次。

**判斷依據**：函式內對每個 term 執行子字串搜尋，時間複雜度為 O(n*m)。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/scripts/deepseek_review.py:190</code> load_blocked_terms 未處理可能的編碼問題</summary>

從環境變數讀取的字串可能包含非 UTF-8 字元，但程式碼未處理解碼錯誤。若 secret 包含非預期編碼，可能導致例外。建議明確指定編碼或處理例外。

**判斷依據**：直接使用 splitlines() 處理原始字串，未考慮編碼問題。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11796 (cache hit 1408) ｜ completion tokens 773 ｜ PR #21</sub>