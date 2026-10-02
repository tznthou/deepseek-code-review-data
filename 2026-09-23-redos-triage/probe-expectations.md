# probe v1.3.1 回歸 — 預期表定稿 2026-09-23T06:13:47Z (觸發前, 之後不改)

背景: v1 已從 79dd6a14d (v1.3.0) 移到 cffcc42 (v1.3.1 tag object) → ff63650。
假 key → deepseek_review.py 在 API 呼叫就 401, 走不到 v1.3.1 改的 locate.py。這次只驗 tag 移動。

| # | 看什麼 | 預期 | 不符代表 |
|---|---|---|---|
| 1 | caller 解析 reusable 的 ref | log 有 `@refs/tags/v1 (cffcc42...)` | tag 沒移成功 / 有快取 |
| 2 | kit checkout 落點 | `HEAD is now at ff63650` (chore: 發布 v1.3.1) | 同上 |
| 3 | filter-findings no-op | post 有 `##[warning]` 的 deprecated 提示 (不是 script 全文的 ::warning::) | no-op 路徑壞了 |
| 4 | 禁用詞掃描 | 未設 REVIEW_BLOCKED_TERMS → 沒有「送出前掃描」的 log 行 | 未設也在掃 |
| 5 | post 失敗點 | HTTP 401, exit 1; 不是 startup_failure 也不是更早的 step | 前面有東西壞了 |
| 6 | code review | success | static/codeql 在 v1.3.1 壞了 |
| 7 | 花費 | $0 (認證階段被拒) | — |
