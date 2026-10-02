# 補上下文：擴到所在函式 vs ±3 行（2026-09-30）

> 來源：RESUME 待辦「下一個品質實驗 = 補上下文（擴到所在函式），排在 ①③ 前」；大綱在
> `.claude/plans/2026-09-28-review-followups.md` C 段。
> **下面「判準」與「操作定義」兩節在跑 API 之前寫定（2026-09-30 05:3x UTC），之後不改；結果只往後面的節追加。**

## 問題

在修改型 PR 上，送給模型的 diff 從 ±3 行上下文擴到「改動所在的整個函式」，功能缺陷的 recall 會不會變；
precision（Qodo 定義）與 F1 會不會變。

結果用在兩處：

1. **架構路線**（RESUME「架構路線」）：/pi-askall 的共識是「先做補上下文，別急著二選一」。
   量過的 prompt 改動換算成 F1 只動 2–4 點（[[code-review-recall-benchmarks]]）——這次量「單次呼叫多給 code」這個方向動多少
2. **kit 要不要加「函式上下文」選項**（collect 端產 `-W` diff）。本實驗不動 kit

## 兩個臂

| 臂 | 送出的 diff | 輪次 |
|---|---|---|
| 基準 | Qodo 資料夾的 `pr.diff`（`-U3`，GitHub 產的） | `base-1`、`base-2`（09-25，已有）＋ **`base-3`**（本次，同日對照） |
| 函式上下文 | `prs/<key>/fc.diff`（見下節） | `fc-1`、`fc-2` |

其他全部相同：rubric v1.4.0（sha256 開頭 `2e0703249d9bbcc7`，= 現在的 `prompts/review-rubric.md`）、
`deepseek-v4-pro`、參數照 CI（`run_ctx.py` 直接呼叫 09-25 的 `run_bench.main()`，只換資料根目錄）、`--rules-dir`。

- **payload 與 09-25 相同（已驗）**：kit 從 `c04b0d0`（base-1／2）到 `f36c025`（現在）改過 `deepseek_review.py`，
  `check_payload_equiv.py` 攔下兩版送出的 payload 逐 PR 比對 → **100/100 逐字相同**；反向對照（範本多一個空白）→ 0/100
- **為什麼還要 `base-3`**：09-25 到今天模型可能被更新過；同一天跑一輪基準才分得出「上下文的效果」與「模型變了」。
  它也是第三輪基準，給 L 的跨輪條件用

## 函式上下文的 diff（已產出，$0）

- `build_diffs.py`：每個 fork 一個 bare 的 partial clone（blob:none），照 SHA 抓 merge base 與 head（depth=1）；
  merge base 由 compare API 取得，**100/100 等於 PR 的 base_sha**
- **正向對照**：本機 `git diff -U3` 去掉 hunk 標頭的函式名稱後，與 Qodo 的 `pr.diff` **100/100 相同**
  （逐字相同：只照 repo 設定 74、加內建 driver 82——差別只在 GitHub 的 hunk 標頭用了語言規則，例如 `.cs` 用 C#）
- **函式邊界**：git 內建 driver（`scripts/builtin-drivers.gitattributes`：csharp／python／rust／cpp…），
  以 `core.attributesFile` 傳入，repo 自己的 `.gitattributes` 優先。**JS／TS／Swift 沒有內建 driver** → git 預設規則
  （行首是英文字母、底線或 `$`）→ **class 裡的方法會擴成整個 class**（firefox-ios ×4.28）。本臂就是這樣處理，
  不另寫規則
- **只擴程式碼檔**（`compose_fc.py` 的 `CODE_EXT`）：沒有函式結構的檔案（JSON／YAML／lock／markdown…）git 找不到
  「函式開頭」，`-W` 會把整個檔案塞進來（tauri-1 的兩個 `config.schema.json` 各放大約 100 倍）→ 這些檔案逐字沿用 Qodo 的區塊。
  功能性 GT 在 JSON 的只有 6 則
- **不變量**（100/100 通過；三個反向對照都抓得到）：檔案區塊順序與標頭相同；每個檔案的 `+`／`-` 行序列與 Qodo
  相同（只有上下文不同）；非程式碼檔逐字相同
- **超過 400,000 字元**（`deepseek_review.py` 的截斷門檻）的 PR 整份退回 Qodo `pr.diff`：**5 個**
  （Ghost-7、cal.com-4、cal.com-5、firefox-ios-2、firefox-ios-9）。另有 3 個沒有東西可擴 → fc 臂與基準**實際不同的是 92 個 PR**
- 大小：總字元 2,750,117 → 6,462,724（×2.35）；PR 倍率中位數 ×1.79、p90 ×6.58、最大 ×19.31（firefox-ios-11）

| repo | 倍率 | 退回 |
|---|---|---|
| Ghost | ×1.73 | 1 |
| aspnetcore | ×1.54 | 0 |
| cal.com | ×2.36 | 2 |
| dify | ×1.84 | 0 |
| firefox-ios | ×4.28 | 2 |
| prefect | ×1.49 | 0 |
| redis | ×5.68 | 0 |
| tauri | ×1.56 | 0 |

## 判準（跑前寫定）

分母固定：功能性 GT **309** 則（`evalset.json` 的 `kind == "func"`，含 diff 外）；全部 GT **580** 則；
finding 端 = 該輪全部 finding。**全部信心層級**——v1.6.0 起預設只貼摘要，摘要表列出全部 finding。

- **S(輪)**＝有至少一組「該輪 finding × 該 GT」被盲標成 `same` 的功能性 GT 則數
- **L(輪)**＝有至少一組「該輪 finding × 該 GT」位置命中（定位後行號落在錨點 ±3）的功能性 GT 則數（程式算）
- **P(輪)**（Qodo 定義）＝至少被標一組 `same`（對任何 GT，功能或規則）的 finding 數 ÷ 該輪 finding 數
- **R(輪)**＝至少被標一組 `same` 的 GT（功能＋規則）÷ 580；**F1**＝2PR/(P+R)

判決：

- **函式上下文較好**：兩條都成立——① S(fc-1) − S(base-3) ≥ **+10** 則；
  ② min(L(fc-1), L(fc-2)) > max(L(base-1), L(base-2), L(base-3))
- **函式上下文較差**：① S(fc-1) − S(base-3) ≤ **−10** 則；② max(L(fc-1), L(fc-2)) < min(L(base-1), L(base-2), L(base-3))
- 其他：**分不出來**
- 附帶條件（只在「較好」時看）：F1(fc-1) ≤ F1(base-3) → 改判 **recall 換 precision**

門檻理由：+10 則（3.2pp）沿用 09-28 v1.4.0 出口；同一份 rubric 兩輪的 L 可以差 11 則（v131-1 160、v131-2 149，信心 ≥ 0.7），
所以要一條跨輪都成立的條件，只看一輪的 S 會被雜訊帶著走。

對應的動作：

- **較好** → 另開計畫：collect 端產 `-W` 的選項（先 opt-in）、JS／TS／Swift 的函式規則、截斷策略、inline 定位
  （GitHub 只能把留言掛在 PR diff 的行上）；本實驗不動 kit
- **recall 換 precision** → 記錄；不動 kit
- **分不出來／較差** → 結案：單次呼叫多給所在函式，在這個量測解析度下沒有改變 recall；架構路線的討論帶著這個結果

讀法（跑前寫定，不當閘門）：ΔF1 = F1(fc-1) − F1(base-3) 跟「prompt 改動 2–4 點」比；|ΔF1| < 5 點 →
「多給所在函式」不是比調 prompt 更大的槓桿。參考雜訊：同一臂兩輪的位置命中版 F1 差 0.8 點（base-1 0.513、base-2 0.521）

## 操作定義（跑前寫定）

- 跑法：`run_ctx.py --arm base base-3`、`--arm fc fc-1`、`--arm fc fc-2`，依序（fc-2 吃 fc-1 的快取）。
  失敗的 PR 照 run_bench 的續跑設計重跑一次；仍失敗就該 PR 記 0 筆（對失敗那一臂不利，偏保守）
- 定位：finding 用**該臂送出去的 diff** 建索引重新定位（fc 臂 = `fc.diff`；基準臂 = Qodo `pr.diff`，= 09-25 做法）；
  GT 錨點（Qodo 的 `evalset.json`）與候選配對（`score_bench.pairs_for`）不變
- 計分的正向對照（**已做，碰新資料之前**）：`score_ctx.py check` 重現 base-1／base-2 的 L（全部）177／178、
  L（≥ 0.7）151／149、base-1 配對 430 組逐組相同、09-25 舊標籤的 S 137、P 160/347、R 166/580、F1 0.353 → 全部重現。
  判決那段用舊資料乾跑過（fc-1 ← base-1）：跑得完、數字相同
- 盲標是**混標**：fc-1 與 base-3 的全部候選配對同一批打亂（`score_ctx.py sheets`，seed 20260930）；編號不透明
  （`P0001…`），對照表 `blind/mapping.json` 不給標記員；標記單不含 confidence、severity、輪次；判準與格式沿用 09-28
  （`make_sheets.HEADER`／`block`，Martian：一個 code change 能同時修掉兩者才算 `same`）；一個 subagent 一份，只准讀自己那份
- 主 session 在讀標記員結果**之前**，先標分層抽樣 30 組（位置命中 20、其他 10）
- 標記員（general-purpose subagent，平行）的指示逐字用 `scripts/labeler-prompt.txt`（`{sheet}`／`{csv}` 換成該份的路徑）；
  交回後先跑格式檢查（缺、多、重複、不合法標籤——`verdict` 開頭就會擋）
- 附記（只記錄，`score_ctx.py verdict` 會印）：信心 ≥ 0.7 那層的 S、L；規則類 271 則的 S、L；排除 5 個退回 PR 的 S、L；
  fc 臂「落在擴出來的行」的 finding 數（定位後行號不在 Qodo `pr.diff` 的索引裡）與其中標 `same` 的數；
  fc 的 finding 改用 Qodo `pr.diff` 定位的 L；每輪 finding 數、prompt token、位置命中版 P／R／F1；各 repo 的 L（每 repo 9–16 個 PR，只描述）

## 成本（跑前估計）

用 base-1 每個 PR 的實際 prompt token 對 diff 字元回歸（每 token 3.64 字元），fc 臂 prompt 約 ×2.07：

| 輪 | 離峰 | 尖峰 |
|---|---|---|
| base-3（無快取） | $0.75 | $1.49 |
| fc-1（無快取） | $1.42 | $2.84 |
| fc-2（吃 fc-1 快取） | $0.30 | $0.60 |
| 合計 | **≈ $2.47** | ≈ $4.93 |

尖峰時段（DeepSeek 官網定價頁，2026-09-30 查）：**週一～五 UTC 01:00–04:00、06:00–10:00**；其他時間離峰（半價），
**中國國定假日整天離峰**。`deepseek-v4-pro` context 長度 1M token（最大一份 fc diff 約 10 萬 token）。

## 限制

- 只量 recall 與 Qodo 定義的 precision。Qodo 只列注入的缺陷：落在擴出來的舊 code 上的 finding 可能是真的既有問題，這裡算未對上
- 注入的缺陷大多寫在改動行上，需要看函式其他部分才判斷得出來的比例未知 → 這份評估集可能低估、也可能高估上下文的好處
- JS／TS／Swift 用的是 git 預設規則（擴成整個 class），不是真正的「所在函式」；兩種語言群的效果混在一起
- 每臂只盲標一輪；L 有兩到三輪
- 送出的是 8 個開源專案的 code（fork 在 `agentic-review-benchmarks`；授權：Ghost、aspnetcore MIT，prefect、tauri Apache-2.0，
  firefox-ios MPL-2.0，cal.com、dify、redis 是混合或修改過的授權），fc 臂送出的量約基準的 2 倍。09-25 的基準線已經送過它們的 diff

## 檔案

- `scripts/build_diffs.py`（抓資料＋產四種 diff）、`builtin-drivers.gitattributes`、`compose_fc.py`（組 fc.diff＋不變量）、
  `check_payload_equiv.py`（payload 比對，`--mutate` 是反向對照）、`run_ctx.py`（跑一輪，`--stage-only` 只建結構）、
  `score_ctx.py`（check／sheets／verdict）、`verdict_dry.py <空目錄>`（判決乾跑：fc-1 ← base-1 舊標籤）、`labeler-prompt.txt`、
  `check_verdict_independent.py`（跑後：verdict 主數字的獨立重算）、`post_hoc_locate_stats.py`（跑後事後探索：各輪定位不到的分布）、
  `post_hoc_l_vs_s.py`（10-01 事後分析：L×S 四格、配對檢定、跨輪一致性、多重命中改用模型行號）
- `prs/<key>/`：`u3`／`u3d`／`w`／`wd`／`fc` 五種 diff、`mb.json`、`meta.json`；`prs/manifest.json`、`prs/fc-manifest.json`
- `arms/<臂>/`：給 run_bench 用的資料根目錄（symlink）與 `rounds/<標籤>/` 輸出
- `blind/`：`mapping.json`（不給標記員）、`sheet-part1–9.md`、`labels-part1–9.csv`、`spot-sheet.md`／`spot-main.csv`（主 session 抽樣）、`results.json`（verdict 輸出）
- ~~`cache/`：8 個 fork 的 bare repo（710 MB，其中 Ghost 390 MB 是 lazy fetch 抓了整段歷史，見 build_diffs.py 註解）；實驗結束可刪~~
  **2026-10-01 已刪**（子超同意；刪前 `du -sh` 704M、Ghost.git 497M，全是 `agentic-review-benchmarks/*` 的公開 fork）。
  要重建跑 `build_diffs.py`（$0；lazy fetch 已修，Ghost 不會再抓整段歷史）。`prs/` 的五種 diff 都還在，重跑實驗不需要它

## 進度

- 05:0x–05:3x UTC：資料準備與所有 $0 檢查（上面各節）；`build_diffs.py` 第一版在 partial clone 裡用 `cat-file -e`
  檢查 commit 是否存在，觸發 lazy fetch 抓整段歷史（Ghost 390 MB）→ 改成檢查時設 `GIT_NO_LAZY_FETCH=1`（tauri-1 驗證：2.6 秒、264 KB）
- `score_ctx.py` 第一次跑拆包寫錯（`evalset()` 回兩個值，寫成拆三個），直接報錯、修掉
- 05:3x UTC：子超選「台灣 18:00 後跑」（UTC 10:00 起離峰）。跑之前的最後一步：`run_ctx.py --arm base base-3 --limit 1`
  與 `--arm fc fc-1 --limit 1` 各試一個 PR（run_bench 可續跑，試跑的結果算進該輪），再跑滿 100
- 10:18–10:30 UTC：三輪跑完（離峰；各輪先 `--limit 1` 試跑一個 PR 再續跑，試跑結果算進該輪）

  | 輪 | 成功 | finding | prompt token（hit） | completion | 離峰估價 |
  |---|---|---|---|---|---|
  | base-3 | 100/100 | 342 | 949,087（942,720） | 104,069 | $0.231 |
  | fc-1 | 100/100（`cal.com-7` 首跑失敗，重跑一次成功） | 346 | 1,790,962（295,040） | 110,972 | $1.214 |
  | fc-2 | 100/100（首跑） | 356 | 1,790,962（1,784,320） | 110,046 | $0.262 |

  合計 ≈ $1.71（跑前估 $2.47）。命中率：base-3 99.3%（09-25 送過同一份 payload、快取還在）、fc-1 16.5%（第一次送這批 payload）、fc-2 99.6%（吃 fc-1 的快取）
- `fc-1` 的 `cal.com-7` 首跑 exit 2：`輸出被 max_tokens=8192 截斷（content 14581 字元）`（fc.diff 54,021 字元、thinking=disabled）。照操作定義重跑一次成功（3 筆 finding）；參數不動（要跟 CI 一致）。base-3 與 fc-2 全部首跑成功
- **`run_bench.py` 的 log 檔名 bug**：`stem.with_suffix(".log")` 把 `cal.com-7` 的「副檔名」`.com-7` 換掉 → 16 個 cal.com PR 共用 `cal.log`（後寫的覆蓋前面）。09-25 的 base-1 也有（`cal.log` 1 個、`cal.com-*.log` 0 個）。只影響除錯用的 log：`.json`／`.md` 用字串串接、用量從 stderr 直接解析。實驗中途不改
- 10:31 UTC `score_ctx.py check`：正向對照全部重現；新輪次 L（全部信心）base-3 175、fc-1 163、fc-2 154（base-1／2 是 177／178）；候選配對 459／438／442
- 10:31 UTC `score_ctx.py sheets`（seed 20260930）：897 組（base-3 459 + fc-1 438）分 9 份、每份 97–100 組；func／rule：fc-1 296／142、base-3 301／158
- 主 session 抽樣 30 組**在派標記員之前**標完並存檔（`blind/spot-main.csv`：same 11、partial 2、no 17；P0036、P0399 判 same 但也可判 partial）。10:33 UTC 前派出 9 位標記員（general-purpose、平行，prompt 逐字用 `labeler-prompt.txt`）
- 10:50 UTC 前 9 位標記員全數回報（每份自報只讀了自己那份）；`verdict` 約 10:50 UTC 執行：格式檢查 897／897、缺／多／重複／不合法皆 0。標籤分布（same／partial／no）：第 1 份 40／10／50、第 2 份 39／12／49、第 3 份 28／8／64、第 4 份 42／7／51、第 5 份 33／10／57、第 6 份 31／10／59、第 7 份 44／6／50、第 8 份 33／7／60、第 9 份（97 組）38／10／49；加總 328／80／489，依輪次 fc-1 160／39／239、base-3 168／41／250
- 第 2 份標記員回報：9 位共用同一個 scratchpad，它的檢查腳本被另一位標記員改成檢查 `labels-part5.csv`；它沒動、改用自己的腳本。→ 標記員之間不是完全隔離（沒有證據顯示有人讀過別份，但只有自報）

## 結果（2026-09-30 約 10:50 UTC 判決；上面「判準」「操作定義」兩節跑前寫定、未改）

**判決：分不出來**

| | fc-1 | base-3 | 差 |
|---|---|---|---|
| S（功能性 309，盲標 same） | 134（0.434） | 130（0.421） | +4（門檻 ±10） |
| P（Qodo 定義） | 155/346 = 0.448 | 162/342 = 0.474 | −0.026 |
| R（580） | 157 = 0.271 | 167 = 0.288 | −0.017（−10 則） |
| F1 | 0.337 | 0.358 | **−0.021** |

L（位置命中，功能性）：base-1 177｜base-2 178｜base-3 175｜fc-1 163｜fc-2 154

- 「較好」不成立：S 差 +4 < +10，且 fc 最低 154 < 基準最高 178。「較差」只缺條件①（S 差 +4 > −10），條件②成立（fc 最高 163 < 基準最低 175）
- 讀法：|ΔF1| = 2.1 點 < 5 點 → 「多給所在函式」不是比調 prompt（2–4 點）更大的槓桿；方向是略低。位置命中版 F1：base-1 0.513、base-2 0.521、base-3 0.529（基準三輪範圍 1.6 點）｜fc-1 0.476、fc-2 0.466

附記（不影響判決；照跑前寫定的清單）：

- 信心 ≥ 0.7：S fc-1 117、base-3 115｜L base-1 151、base-2 149、base-3 149、fc-1 142、fc-2 137
- 規則類 271 則：S fc-1 **23**、base-3 **37**｜L base-1 74、base-2 76、base-3 81、fc-1 68、fc-2 71。R 少的 10 則全來自規則類（功能性 S +4、規則類 S −14）
- 排除 5 個 fallback PR（功能性 294 則）：S fc-1 127、base-3 124｜L base-1 171、base-2 172、base-3 170、fc-1 157、fc-2 148
- fc 臂「落在擴出來的行」：fc-1 7 筆（其中標 same 2）、fc-2 6 筆（共 346、356 筆）；定位不到 38、39 筆。fc 改用 Qodo `pr.diff` 定位的 L：fc-1 169、fc-2 157
- finding 數（≥ 0.7）：base-1 347（270）、base-2 362（278）、base-3 342（262）、fc-1 346（271）、fc-2 356（272）；prompt token 949,087 vs 1,790,962（×1.89）
- 位置命中版 P／R：base-1 0.631／0.433、base-2 0.644／0.438、base-3 0.661／0.441、fc-1 0.592／0.398、fc-2 0.584／0.388
- 各 repo 的 L（只描述；基準 1／2／3｜fc-1／fc-2）：Ghost 26／27／25｜21／23、aspnetcore 16／18／15｜16／12、cal.com 28／26／27｜26／26、dify 21／25／25｜**18／17**、firefox-ios 25／22／21｜23／17、prefect 24／21／21｜22／20、redis 16／18／17｜15／15、tauri 21／21／24｜22／24
- 主 session 抽樣 vs 標記員：三類一致 29/30、same 與否一致 30/30；分歧 P0567（主 session partial、標記員 no）

驗證：

- 獨立重算（`check_verdict_independent.py`，不 import `score_ctx`）：S 功能性／規則類、P 分子、R 分子 fc-1 134／23／155／157、base-3 130／37／162／167，與 verdict 逐項一致
- verdict 的 L 與 `score_ctx.py check`（10:31 UTC）印的一致（base-3 175、fc-1 163、fc-2 154）；計分的正向對照跑前已全部重現

事後探索（跑後才做，不在跑前寫定的判準內）：

- `post_hoc_locate_stats.py`：定位不到的 finding：base-1 28（8.1%）、base-2 31（8.6%）、base-3 31（9.1%）｜fc-1 38（11.0%）、fc-2 39（11.0%）；多出來的幾乎都是「片段多重命中，不猜」（基準三輪 29 上下 → fc-1 36）。以位置命中版 P 0.59–0.66 粗估，多 7–8 筆定位不到最多影響 4–5 則 L，**解釋不了 12–24 的落差；L 落差的來源沒查明**
- 描述性事實（不當原因）：沒有任何 repo 的 fc 輪高於基準最高值（tauri fc-2 24 = 基準最高 24）；差最多的是 dify（Python；基準 21／25／25、fc 18／17）

解讀與限制：

- **在這個評估集與量測解析度下**：單次呼叫預先擴到所在函式，功能性 recall 分不出來（+4／309 = +1.3pp）、F1 略低（−2.1 點）、規則類 recall 掉（S 37 → 23）、prompt ×1.89、fc-1 有 1 個 PR 首跑輸出被 `max_tokens=8192` 截斷。沒有任何一項指向「較好」
- **不能說的**：① 「補上下文沒用」——只量了「預先擴到函式（JS／TS／Swift 是整個 class）再一次送出」這一種，agent 自己挑要查什麼那條路徑沒被碰到 ② 分辨力：偵測不到小於約 10 則（3pp）的效果，每臂只盲標一輪 ③ 評估集的缺陷大多寫在改動行上，需要看函式其他部分才判斷得出來的比例未知（見「限制」）
- **標記員自報的邊界 same**（修法相同但理由或機制不同、或只抓到一半，依判準仍標 same）共 21 組：第 1 份 P0002／P0063／P0091、第 2 份 P0126／P0170、第 3 份 P0295、第 4 份 P0307／P0360／P0387、第 5 份 P0402／P0422／P0440、第 7 份 P0647／P0687／P0694、第 8 份 P0760／P0794、第 9 份 P0820／P0835／P0858／P0876。我的 30 組抽樣 same 與否 30/30 一致，沒有證據顯示系統性偏寬；抽樣只涵蓋 30/897，但兩臂混標，偏寬對兩臂是對稱的
- 對應的動作（依「對應的動作」）：結案；kit 不動；架構路線的討論帶著這個結果（/pi-askall 的「先做補上下文」第一步——單次呼叫多給所在函式——沒有增益）。公開頁待子超決定；`cache/`（710 MB）可刪

## 事後分析：把 S、L、規則類拆開（2026-10-01，`scripts/post_hoc_l_vs_s.py`；不改判決）

起因：子超問「真的是分不出來嗎，結論應該再細一點」。

**判決重核**：「較好」① +4 < +10 不成立；「較差」要兩條同時成立，② 成立（fc 最高 163 < 基準最低 175）、① 不成立（+4 > −10）
→ **分不出來，規則套用正確**。但兩條判準的方向不一致：S 沒差，L 指向較差。「分不出來」把這件事蓋掉了。

正向對照：腳本重算的功能性 L（177／178／175／163／154）、S（134／130），規則類 S（23／37）、L（74／76／81／68／71）
與 `results.json` 逐項相同；base-1 用 09-25 舊標籤的功能性 S = 137，與 09-25 的數字相同。

1. **功能性同一問題（S）：真的沒差。** fc-1 134 落在基準兩輪之間（base-1 137 用 09-25 舊標籤、base-3 130）。
   逐則配對：fc-1 vs base-3 各自獨有 34／30 則（McNemar p = 0.71）；基準兩輪之間 +7（28／21，p = 0.39）
2. **功能性位置命中（L）：fc 一致偏低；有盲標的 fc-1 少掉的主要是巧合命中，不是漏報。**
   - 每輪平均：基準 176.7、fc 158.5（−18.2）。跨臂 6 組全負（−12～−24）；臂內：基準三輪之間 −1～+3、fc 兩輪之間 +9。
     未校正 p：fc-2 vs 三輪基準 0.005–0.024（PR 層置換 0.006–0.014），fc-1 vs 三輪基準 0.08–0.21
   - fc-1 vs base-3 的 L×S 四格：位置對＋同一問題 121 vs 124（−3）｜位置對、不是同一問題 42 vs 51（**−9**）｜
     同一問題、位置差 > 3 行 13 vs 6（+7）→ L 少的 12 則裡 9 則是巧合的位置命中
   - fc-1 那 13 則「同一問題、位置差 > 3 行」：9 則走 `model_line`（定位結果全是「片段多重命中，不猜」，其中 8 則模型行號在錨點 ±3）、
     4 則走 `ident`（距離 6–30）。base-3 的 6 則：5 則同型（多重命中、模型行號 ±1 內）、1 則 `ident`
   - **多重命中不是 L 落差的原因**（假說證偽）：把「多重命中、模型行號在錨點 ±3」也算位置命中，五輪各 +5～+9
     （185／185／182｜172／159），平均 基準 184.0、fc 165.5，落差不變（−18.5）。
     另一種算法（附記那條：fc 的 finding 改用 Qodo `pr.diff` 定位，169／157，各 +6／+3）：fc 平均 163.0，落差 13.7。
     兩種算法下落差都還在 → 定位只解釋得了一小部分
   - 跨輪一致性：基準三輪都命中的 143 則，fc 兩輪都沒命中 16 則；反方向（fc 兩輪都命中、基準三輪都沒有）4 則。
     那 16 則在 fc-1：同一問題但位置差 > 3 行 5、同檔沒有 finding 5、其他 6；base-3 那邊的位置命中 14/16 標 same
   - base-3 命中、fc-1 沒命中的 45 則 vs 反方向 33 則，沒命中那輪「同一個檔沒有 finding」都是 13 則（對稱）；
     不對稱的在「同一問題、位置差 > 3 行」7 vs 2、「同檔有 finding、距離太遠」12 vs 8
   - **沒查明**：fc-2 掉得更多（vs base-3 −21）但沒盲標，拆不開；「位置對、不是同一問題」為什麼變少，原因沒查
   - 單則 GT 在兩輪之間進出很大：基準任兩輪各自獨有 19–24 則，總數只差 1–3
3. **規則類：fc 全部偏低，幅度跟基準輪間差同級。** S：fc-1 23 vs base-1 29（舊標籤）、base-3 37；
   L：fc 68／71 vs 基準 74／76／81。跨臂 8 組全負。顯著的只有 S fc-1 vs base-3（獨有 0／14，p < 0.001），
   但基準兩輪自己就差 8（5／13，p = 0.096），fc-1 vs base-1 −6（3／9，p = 0.15）。fc-1 vs base-3 四格：
   位置對＋同一問題 23 vs 35、位置對但不是同一問題 45 vs 46 → 少的是真命中，不是位置。候選配對 142 vs 158（same 26 vs 38）
4. **代價是確定的**：prompt token ×1.89；fc-1 有 1 個 PR 首跑輸出被 `max_tokens=8192` 截斷

**細緻版結論**：預先擴到所在函式，功能性問題抓到的一樣多（S 落在基準兩輪之間）；位置命中兩輪都偏低（平均 −18，
基準三輪之間最多差 3），在有盲標的 fc-1 裡少掉的主要是巧合命中；規則類方向一致偏低、但幅度跟基準兩輪之間的差同級；
成本 ×1.89。→ **沒有量得到的收益，只有確定的代價**。跟原判決相容，多說的是「不是零代價、也不是什麼都沒變」。

事後分析的限制：跑後才做，約 36 組比較、p 值未校正（Bonferroni 後只剩規則類 S fc-1 vs base-3，而它被 base-1 vs base-3 的 −8 削弱）；
McNemar 把 GT 當獨立，PR 層置換是較保守的版本；base-1 的標籤來自另一批（09-25；09-28 量過新舊標籤 same 與否一致 98.5%）；
fc-2 沒盲標

## 公開與收尾（2026-10-01）

- 公開頁 `experiments/2026-09-30-function-context.md`：PR #59（squash `0ad9059`，05:05:17 UTC merge）。推送閘門
  `.claude/plans/push_gate_fc.py`：清理 0、回查 49 組、B2 用 `score_ctx` 重算 18 項（四格與「多重命中改用模型行號」另寫一次，
  不 import 事後分析腳本）；GitHub 渲染 3 張表（清單項目內那張也在 `<li>` 裡）
- AI review 兩輪：第一輪 0 筆；摘要說「token 89%」與「字元數 ×2.35」可能混淆 → **部分成立**（頁面把 diff 字元數寫成「送出的字元數」），
  第二個 commit 改成分別寫明。修的時候差點寫成「比 ×2.35 小是因為 rubric 固定部分」——算過：固定部分只把 ×2.35 壓到約 ×2.07
  （用跑前估價那條回歸），實際 ×1.89，剩下的另有原因 → 改成只寫兩個數字各量什麼、不歸因。第二輪 0 筆；規範那次模型回 3 筆、
  0 筆標有效編號
- `cache/` 已刪（見「檔案」）
