# 規範那次為什麼沒吃到快取（2026-09-28 第二十八輪）

> 起因：v1.5.0 的規範那次呼叫緊接在一般那次之後，前綴到 diff 為止逐字相同。
> #50 四次只命中固定的 1,536，#51 一次整段命中（2,432／3,074）。資料在 `../2026-09-28-v150-repo-rules/cache-logs/`，
> 撈表 `../2026-09-28-v150-repo-rules/scripts/cache_table.py`。

## 觀察資料裡混在一起的兩個變因（跑之前就知道）

| | #50 ×4（沒命中） | #51 ×1（命中） |
|---|---|---|
| 長度 | 一般那次 6,979–8,895 | 2,469 |
| 前綴結構 | 一般那次 diff **後面還接了補充規則**（github-workflows.md，3 次再加 python.md）→ 兩次呼叫在 diff 之後就分岔 | 沒有補充規則 → 一般那次整段是規範那次的前綴 |
| 間隔（結束→開始） | 0.06–0.08 秒 | 0.09 秒 |

production 的組法（`deepseek_review.py` main）：一般＝`USER_TEMPLATE(diff)` ＋補充規則；規範＝`USER_TEMPLATE(diff)` ＋規範區塊＋補充規則。

## 設計（送出前定稿，跑完不改）

- 2×2：**長度** S（`inputs/pr51.diff` 1,403 字元）／L（`inputs/pr50.diff` 截到 ≤8,766 字元，對齊 #50 run 1）×**結構** c（一般那次不接補充規則＝完整前綴）／d（照 production 接補充規則＝分岔）
- 每格 2 對，順序固定：S-c、L-d、S-d、L-c、L-c、S-d、L-d、S-c；第 9 對 L-d 間隔 15 秒（描述用，n=1 不下結論）
- 每對用新的 nonce 放在 PR metadata 開頭（user message 的最前面）→ 對與對之間只共用 system prompt＋模板開頭，跟 production 跨 PR 的情況一樣
- system＝`prompts/review-rubric.md`；補充規則區塊用 kit 的 `select_rules(pr50 全文)` 產生，S-d／L-d 共用同一段；規範區塊用 kit 的 `render_repo_rules`（main 上的 `.github/review-rules.md`）
- payload 跟 production 相同（v4-pro、json_object、temperature 0.2、thinking disabled），只有 `max_tokens` 改 200（控制花費與呼叫時長，#50 run 4／#51 的一般那次輸出 152／106 token）
- 間隔：第一次回應收到後 0.1 秒送第二次；對與對之間停 2 秒
- 停止條件：任何 HTTP 錯誤立即全停（401 不印 body）；以尖峰價累計估算 > $0.15 就停

## 判定（送出前定稿）

P＝共同前綴的 token 數：c 格＝第一次的 prompt_tokens；d 格＝同長度 c 格第一次 prompt_tokens 的平均（兩者只差 nonce）。

第二次呼叫的 cached：
- **full**：≥ floor64(P) − 64
- **baseline**：≤ 第一次的 cached ＋ 64（沒用到第一次新送的內容）
- **partial**：其他

一格兩對結果相同才算該格結果，不同記 **mixed**。

| 格 | H_len（長度／建快取時間） | H_div（前綴分岔） | 交互（兩個條件都要） |
|---|---|---|---|
| S-c | full | full | full |
| S-d | full | baseline | baseline |
| L-c | baseline | full | baseline |
| L-d | baseline | baseline | baseline |

- **先驗重現**：L-d 要是 baseline（像 #50）、S-c 要是 full（像 #51）。重現不了就先報「實驗沒重現 production」，不下因果結論
- 有任何一格 mixed → 報「不穩定」，不下因果結論
- L-d 15 秒那對只描述

## 結果對應的後續（送出前定稿）

- 不論結果：USAGE、CHANGELOG `[Unreleased]`、`reusable-ai-review-post.yml`、`deepseek_review.py` 四處的「只隔幾秒」都要改（結束→開始 <0.1 秒）
- **H_div**：文件寫出原因；「規範區塊移到補充規則後面，讓一般那次成為完整前綴」是候選，但改的是 D0f v01 驗過的順序＝行為變更，要子超決定、要重新量
- **H_len**：文件寫「大 PR 緊接著送吃不到」；kit 不改（加延遲換 ~$0.008／PR 不值得）
- **交互／不穩定**：文件只寫事實與樣本數

## 結果（02:52:14–02:53:5x UTC，尖峰時段；`results/run-20260928T025214Z.jsonl`；估算 $0.095）

跑前檢查：dry-run 結構 PASS；`scripts/mutate_check.py` 故意組錯 c／d 四種都抓到（5/5）；`scripts/classify_check.py` 已知答案 6/6（含剛好在門檻上的兩個）。

| 對 | 格 | 一般那次 prompt／cached | 間隔 | 規範那次 prompt／cached | P | 判定 |
|---|---|---|---|---|---|---|
| 1 | S-c | 2,410／1,536 | 0.103 s | 3,043／**2,304** | 2,410 | full |
| 2 | L-d | 7,530／1,536 | 0.104 s | 8,162／1,536 | 5,949 | baseline |
| 3 | S-d | 3,993／1,536 | 0.105 s | 4,625／1,536 | 2,408 | baseline |
| 4 | L-c | 5,953／1,536 | 0.101 s | 6,586／**5,888** | 5,953 | full |
| 5 | L-c | 5,945／1,536 | 0.105 s | 6,578／**5,888** | 5,945 | full |
| 6 | S-d | 3,985／1,536 | 0.104 s | 4,617／1,536 | 2,408 | baseline |
| 7 | L-d | 7,528／1,536 | 0.104 s | 8,160／1,536 | 5,949 | baseline |
| 8 | S-c | 2,407／1,536 | 0.106 s | 3,040／**2,304** | 2,407 | full |
| 9 | L-d | 7,536／1,536 | **15.004 s** | 8,168／1,536 | 5,949 | baseline |

- 格：S-c full／S-d baseline／L-c full／L-d baseline，每格兩對一致，沒有 mixed
- **先驗重現通過**：S-c 像 #51（整段命中）、L-d 像 #50（只命中 1,536）
- **判定：H_div**。H_len 被 L-c 推翻（大 prompt 完整前綴照樣整段命中）；交互被 S-d 推翻
- 15 秒那對（n=1，只描述）：分岔時等 15 秒也一樣只命中 1,536 → 不是建快取來不及
- 細節：full 的命中量都是 floor64(P) − 64（剛好在預先定的容忍線上），#51 production 是 floor64(P)；差一個 64 單位的原因沒查，不影響判定
- 1,536 在所有一般那次都出現：system prompt 2,938 字元，所以 1,536 大約就是 system 那段（沒驗 token 數）

**機制只驗到「分岔 → 只吃到 system 那段」**。「快取以 message 邊界／整段 prompt 為單位存」是跟資料一致的推測，沒測（要測就是把 diff 放在獨立的 user message，看分岔時命中量會不會變成 system＋diff）。

## 後續（照上面預先定的「H_div」那條）

- 四處「只隔幾秒」改寫成實際原因與樣本數 → **docs PR #52**（branch `docs/rules-pass-cache-cause`，commit `e85dec9`）；公開文字的數字逐一回查過主檔（cache_table 輸出、SSOT 金額、本表、`RULE_MAP`）
  - **#52 自己的 review 當現場預測（PR 描述裡跑前寫下）**：diff 動到 `.py` 與 workflow YAML → 一般那次接補充規則 → 分岔 → 規範那次只命中 ~1,536
  - **預測命中**：04 run `36371947009`（套用 github-workflows.md, python.md）一般 5,237／1,536 → 隔 0.09 s → 規範 5,869／**1,536**；兩次 0 筆 finding、approve；規範那次送 1,251 字元（#51 的新 R01 已生效）
  - **#52 merge `2196002`（03:01:30 UTC，squash，遠端 branch 已刪）**；merge 後 main 的 CodeQL（03:02:28 UTC 分析）results_count 31、**open 0**（03:02 UTC 查）
- 候選「規範區塊移到補充規則後面」：省的是規範那次約 6–9k token 從 miss 變 hit ≈ 每個 PR $0.005（離峰）／$0.009（尖峰），而且只有 PR 動到 python／workflow（有補充規則的型態）時才有差；代價是改 D0f v01 驗過的順序、要重量（rules-loop holdout 一輪 $0.5 以上）→ **建議不改；子超 09-28 第二十八輪同意：不改**（重開條件：規範那次的費用變成值得在意的量級，或因為別的理由本來就要重量 v01 順序）
