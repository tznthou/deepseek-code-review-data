<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

這個 PR 新增了送出前禁用詞掃描功能，透過 REVIEW_BLOCKED_TERMS secret 在呼叫 DeepSeek API 前進行子字串比對，命中即拒送。整體設計考量周全，包含避免洩漏禁用詞本身、處理空字串與過短詞等邊界情況，並有對應的測試與文件更新。主要風險在於 workflow 中 secret 傳遞與腳本執行環境的相容性，以及 Python 程式碼中潛在的型別與例外處理問題。

### Findings（3 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `.github/workflows/reusable-ai-review-post.yml:188` | REVIEW_BLOCKED_TERMS 可能未正確傳遞至 Python 腳本 | 0.80 |
| 🔸 | Minor | `.github/scripts/deepseek_review.py:190` | load_blocked_terms 對輸入型別假設過強 | 0.70 |
| 🔸 | Minor | `.github/scripts/deepseek_review.py:210` | blocked_terms_hits 對 sections 的值未處理 None | 0.60 |

<details><summary>⚠️ <b>Major</b> — <code>.github/workflows/reusable-ai-review-post.yml:188</code> REVIEW_BLOCKED_TERMS 可能未正確傳遞至 Python 腳本</summary>

在 `reusable-ai-review-post.yml` 中，`REVIEW_BLOCKED_TERMS` 被設定為環境變數，但後續的 `run` 區塊中，腳本執行時可能未正確引用該變數。請確認 `deepseek_review.py` 是透過 `env` 區塊取得該變數，且 shell 展開時有正確引用。若未正確傳遞，掃描功能將靜默失效。

**判斷依據**：diff 中新增了 `REVIEW_BLOCKED_TERMS: ${{ secrets.REVIEW_BLOCKED_TERMS }}`，但未顯示後續 `run` 區塊如何使用該變數。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/scripts/deepseek_review.py:190</code> load_blocked_terms 對輸入型別假設過強</summary>

`load_blocked_terms` 的參數型別標註為 `str | None`，但實際傳入的 `os.environ.get(...)` 可能回傳 `None` 或字串。函式內使用 `(raw or "").splitlines()` 處理，但若 `raw` 為非字串型別（例如意外傳入 bytes），會拋出例外。建議在函式開頭明確檢查型別或直接使用 `str(raw or "")`。

**判斷依據**：函式參數型別標註為 `str | None`，但未防禦其他型別。

</details>

<details><summary>🔸 <b>Minor</b> — <code>.github/scripts/deepseek_review.py:210</code> blocked_terms_hits 對 sections 的值未處理 None</summary>

`blocked_terms_hits` 中對 `text` 使用 `(text or "").lower()`，但若 `text` 為非字串型別（例如 None 以外的 falsy 值），可能導致非預期行為。建議明確檢查 `isinstance(text, str)` 或直接使用 `str(text or "")`。

**判斷依據**：函式參數 `sections` 的型別為 `dict[str, str]`，但實際傳入的 `system_prompt` 與 `user_prompt` 可能為 None。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 11786 (cache hit 1408) ｜ completion tokens 866 ｜ PR #21</sub>