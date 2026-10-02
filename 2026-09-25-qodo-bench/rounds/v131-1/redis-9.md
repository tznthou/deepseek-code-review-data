<!-- deepseek-review -->
## 🤖 DeepSeek Code Review — 💬 有需要留意的問題

此 PR 修正 HINCRBYFLOAT 在複製到 replica 時會移除欄位 TTL 的問題。主要變更為將複製指令從 HSET 改為 HSETEX 並加上 KEEPTTL 旗標，同時新增 shared objects 與測試。整體方向正確，但需注意 HSETEX 指令的可用性與相容性，以及測試中對 TTL 範圍的斷言可能過於嚴格。

### Findings（2 筆）

| | Severity | 位置 | 問題 | 信心 |
|---|---|---|---|---|
| ⚠️ | Major | `src/t_hash.c:2562` | HSETEX 指令可能不存在於舊版 Redis，導致複製中斷 | 0.80 |
| 🔸 | Minor | `tests/unit/type/hash-field-expire.tcl:1987` | 測試中 TTL 範圍斷言可能過於嚴格 | 0.70 |

<details><summary>⚠️ <b>Major</b> — <code>src/t_hash.c:2562</code> HSETEX 指令可能不存在於舊版 Redis，導致複製中斷</summary>

此變更將 HINCRBYFLOAT 的複製指令改為 HSETEX。若 replica 或 AOF 重播環境的 Redis 版本不支援 HSETEX（例如舊版或某些 fork），複製或 AOF 重播將失敗。建議確認 HSETEX 在所有支援的版本中皆可用，或提供 fallback 機制。

**判斷依據**：diff 中將原本的 rewriteClientCommandArgument(c,0,shared.hset) 改為 rewriteClientCommandVector(... shared.hsetex ...)，若 HSETEX 不存在將導致錯誤。

</details>

<details><summary>🔸 <b>Minor</b> — <code>tests/unit/type/hash-field-expire.tcl:1987</code> 測試中 TTL 範圍斷言可能過於嚴格</summary>

測試使用 assert_range [r httl h1 FIELDS 1 f1] 90 100 來驗證 TTL 未被移除。但 TTL 會隨時間遞減，若測試執行較慢，TTL 可能低於 90，導致 flaky test。建議放寬範圍或使用相對比較。

**判斷依據**：在測試中，從設定 TTL 到斷言之間可能有延遲，TTL 可能已減少。

</details>

---

<sub>model `deepseek-v4-pro` ｜ prompt tokens 3567 (cache hit 1408) ｜ completion tokens 585 ｜ PR #9</sub>