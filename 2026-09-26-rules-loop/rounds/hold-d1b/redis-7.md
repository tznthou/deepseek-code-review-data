<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 新增了 aof-load-broken 與 aof-load-broken-max-size 設定，用於在 AOF 檔案中間損壞時自動截斷損壞部分。主要風險在於自動截斷可能造成資料遺失，且程式碼中對 aof-load-broken-max-size 的型別處理可能導致比較錯誤。此外，src/server.h 的 include guard 從雙底線改為單底線，違反了專案規範 R03。

### Findings（1 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| 🔸 | Minor | `src/server.h:15` | [R03] 違反 Header Files Must Use Double-Underscore Include Guards | 0.95 |

<details><summary>🔸 <b>Minor</b> — <code>src/server.h:15</code> [R03] 違反 Header Files Must Use Double-Underscore Include Guards</summary>

此變更將 include guard 從 `__REDIS_H` 改為 `_REDIS_H`，違反了專案規範 R03（必須使用雙底線）。請改回 `__REDIS_H`。

**判斷依據**：diff 中顯示 `-#ifndef __REDIS_H` 改為 `+#ifndef _REDIS_H`，且規範 R03 明確要求雙底線。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 7395 (cache hit 7296) ｜ completion tokens 315 ｜ PR #7</sub>