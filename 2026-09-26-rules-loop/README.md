# 注入 repo 規範檔的呈現方式：迭代 loop（2026-09-26 建立）

> 用途：在 Qodo PR-Review-Bench 上量「把 repo 規範附進 prompt」能讓規則類 recall 提高多少，
> 並用 loop 調規範的**呈現方式**（放哪、放多少、怎麼排）。不是自由改寫 rubric。
> 資料與評分沿用 `../2026-09-25-qodo-bench/`（evalset、PR diff、base-1／base-2 當 v00）。
> loop 主控檔：`.autoresearch-rules.md`（隱藏檔，接續時手動指這個路徑）。
> **結果（2026-09-26 跑完＋holdout 盲標）看 `final-comparison.md`**：規則類同一問題 0.078→0.187，功能性 0.469→0.432；子超選 D（規範另外用一次呼叫）。
> **D 的結果看 `D-plan.md`**：正式功能用 D0f（第二次呼叫 = v01 的 prompt，只留標了規則編號的 finding）：規則類 0.169、功能性 0.469 不變、高信心未對上 0.74→0.77。
> D1（再加任務範圍說明）引用命中 0.151→0.229，但高信心未對上 1.84/PR，照跑前判準不取代。

## 子超 09-26 拍板的五件事

1. 提早收工門檻：引用命中 ≥ 44%（追上功能性「同一個問題」的水準）
2. Guard 容忍度：沒對上任何標準答案的高信心 finding（每 PR）≤ v00 × 1.15
3. 切分：每個 repo 各自 70/30（seed 20260926）→ 調參組 69 PR（規則 188、功能 213）、holdout 31 PR（規則 83、功能 96）
4. 金額上限 $10（DeepSeek）
5. 收尾時在 holdout 盲標「同一個問題」，確認 metric 跟人判的方向一致

## metric：引用命中

規則類標準答案之中，有 finding **同時**滿足下面兩件事的比例：

- 位置命中：定位後行號在錨點 ±3 行內（沿用 Qodo 的 `score_bench.pairs_for`）
- 引用對：finding 標的規則編號（`[R03]`、`（R03）`、`【R03】` 都算，title 或 body 皆可）正是標準答案違反的那條

做得出來的原因：Qodo 的規則類標準答案每筆都帶 `rule_name`，去掉 `Rule N:` 前綴後 **271/271** 對得上
`rules_for_repo.jsonl` 的規則 title。只看位置命中會高估很多（規則類位置 27.3% vs 盲標同一問題 10.7%）。

## 搜尋空間（`scripts/render.py` 封死）

loop 每輪只改 `iterations/vNN.json`，四個欄位都只能選列舉值：

| 欄位 | 選項 |
|---|---|
| `placement` | `after_diff`（前綴不變、吃得到快取）／`before_diff` |
| `fields` | `title`／`title_objective`／`full`（加上符合／違反條件） |
| `format` | `list`／`sections`／`json` |
| `header` | `h1`／`h2`／`h3`（三句都只提供資訊，不含要求自我約束的話） |

規則文字逐字取自 `rules_for_repo.jsonl`，標準答案的內容進不來。要求模型標編號那句（`render.CITE`）每個版本都一樣。

## 檔案

| 檔案 | 作用 |
|---|---|
| `scripts/render.py` | 規則 → prompt 片段（編號 R01… 照規則檔順序，與設定無關） |
| `scripts/review_with_rules.py` | import kit 的 `deepseek_review.py`，只換 `USER_TEMPLATE`；kit 一行不改 |
| `scripts/run_rules.py` | runner，參數同 CI；同標籤換設定就拒跑；可續跑 |
| `scripts/loop_score.py` | 評分（$0）：引用命中、規則／功能位置命中、高信心未對上／PR、引用率 |
| `scripts/guard.py` | Guard：完整性、G1、G2（可給兩個標籤取平均）、G3（sha256 快照） |
| `scripts/dryrun.py` | $0 乾跑：攔在送出前，驗 system prompt 不變、位置、其餘內容不變、補充規則照舊、編號齊全、JSON 可解析 |
| `scripts/make_split.py` | 切分（`split.json` 已存在就不覆寫） |
| `guard-targets.sha256` | Guard target 快照（kit 的 rubric／腳本、資料集、評分與 runner 腳本、split） |

## 指令

```bash
S=.claude/experiments/2026-09-26-rules-loop/scripts
python3 $S/dryrun.py                                   # $0，改過 runner 就先跑
python3 $S/run_rules.py v01a --config .claude/experiments/2026-09-26-rules-loop/iterations/v01.json
python3 $S/run_rules.py v01b --config .claude/experiments/2026-09-26-rules-loop/iterations/v01.json
python3 $S/loop_score.py base-1 base-2 v01a v01b       # 調參組
python3 $S/guard.py v01a v01b                          # exit 0 才能 keep
```

同一個設定的兩次 run 要用兩個標籤（`v01a`、`v01b`）：同標籤會續跑、跳過已成功的 PR。

## 驗證紀錄（2026-09-26）

- 評分器用 base-1／base-2 重現 Qodo README：規則位置 0.273／0.280、功能位置 0.573／0.576，一致
- dry-run 6 組（2 個 PR × 3 種設定）全過；負向探針（renderer 故意漏最後一條）兩項檢查都 FAIL
- dry-run 中途修過兩次**檢查本身**：JSON 格式的編號是 `"id": "R01"` 不是 `[R01]`；user message 第一個 ```` ```json ```` 是 PR metadata
- 付費 smoke（tauri-10，$0.004 離峰）：規則確實注入（17 條、9751 字元）。模型**有**引用，但寫在 body、用全形括號「（R03）」，
  不是 title 開頭的 `[R03]` → 評分器改成接受各種括號與位置（沒括號、編號不存在都不算）；重評後引用命中 1/4，R03 正是標準答案那條
- v00 兩輪之間「高信心未對上／PR」就差 0.59 vs 0.71（約 ±9%），G2 的 +15% 離雜訊不遠 → guard.py 可給兩個標籤取平均判

## 限制

- Qodo 的規則是整理過的結構化條目；真實 repo 多半是 AGENTS.md 這類自由文字，呈現方式不一定搬得過去
- 注入的缺陷、標準答案不完整 → 只量 recall；「高信心未對上」不等於誤報
- 資料集 2026-02 公開，可能被模型看過
