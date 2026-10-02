# v1.5.0：repo 規範檔另外用一次呼叫（D0f 正式功能）

> 第二十七輪（2026-09-28）。計畫：`.claude/plans/2026-09-28-d0f-repo-rules.md`（v2，計畫審查（深度模式））。
> 實驗依據：`../2026-09-26-rules-loop/D-plan.md`（D0f、子超裁定）。公開頁：`experiments/2026-09-26-rules-loop.md`。

## 子超 09-28 決定

- 格式**條目為主**：第 0 欄 `- `／`* ` 各一條，`##` 節標題當分組標籤；沒有條目的 `##` 節整節一條；其他散文不送；0 條或 >99 條跳過
- input 名稱 `repo-rules-path`；kit 自己**長期 dogfood**（`.github/review-rules.md`，草稿 `kit-review-rules-draft.md`，11 條）
- paths-ignore 說明先開小 docs PR（#46 已 merge）；CHANGELOG 1.4.0 的措辭調整（#47 裡獨立 commit）

## 進度

- #45（v1.4.0 出口公開頁）、#46（USAGE paths-ignore）merge
- #47 feature PR（branch `feat/repo-rules-pass`）：功能、過期註解、CHANGELOG 匿名化、文件、ReDoS 修正 共 5 commit
- 待：#47 merge → 發版 PR → `v1.5.0` tag（先不移 `v1`）→ probe → PR-X（kit 規範檔＋04 暫釘 `@v1.5.0`）→ PR-Y（USAGE/README 功能說明＋04 改回 `@v1`；它自己那次 review 就是真 API 端到端）→ 移 `v1`＋Release → merge PR-Y

## 驗證（都在 merge 前、$0 以外只花一次 API）

| 驗什麼 | 結果 | 腳本 |
|---|---|---|
| 沒設規範檔的 caller 行為不變（D1） | golden 三組（定位、跨檔改寫、7 種跳過原因與 max-inline）逐字相同；不帶新參數、`--rules-status skipped` 兩種。正向對照：`success` 就 DIFF | `make_post_golden.py`（用 `git show v1.4.1:` 的舊版產生）、`check_golden.py` |
| 送出去的規範區塊＝實驗量過的那段 | Qodo 8 個 repo 寫成簡單格式，kit 渲染跟 `render.render(v01)` **8/8 逐字相同**（ReDoS 修正後重跑仍 8/8） | `compare_v01_render.py` |
| 真 API 一次 | cal.com-11：規範 10 條、模型回 4 筆、留 1 筆 `[R07]`（直接存取 process.env，同實驗 hold-v01a）；併進同一處的一般 finding；Step Summary 一行統計。**$0.0052（尖峰）**，prompt 7,997 tokens 中 7,936 命中快取（同一段 prompt 兩天前實驗送過）| `real_rules_pass.py`，輸出在 `real-run/` |
| selftest 不空轉 | workflow 檢查對 4 種變異都叫；合併寬度 0/2/4/10 都叫、3 才過 | `mutate_wf_checks.py`、`mut_window.py` |
| selftest | 18 組 100 項 → **21 組 161 項** | `tools/selftest.py` |

⚠️ 過程中踩到的（已修、已記）：
- golden 的 diff 第一版行尾空白被吃掉（兩行 `' '` 變 `''`，行號少 2）→ 改用 list 組、從 git 取舊版重產。Edit/Write 吃行尾空白的**第二例**（第一例 PR #27 `ROOT =pathlib`）
- 合併寬度的變異測試第一次寫成 zsh one-liner（for＋heredoc），w=4 的輸出是錯的卻被讀成「抓到」；改寫成腳本檔才正確。全域 CLAUDE.md 早有「多行 shell 寫成腳本檔」
- 規範那次沒有單獨貼的 finding 時仍重排，會讓 failure/cancelled 的一般 inline 順序跟沒開時不同 → 只在有單獨貼的時候才排（selftest 抓到的）
- `cd /private/tmp` 讓 primary 被換走 1 次

## PR #47 的 CodeQL（threat-models: local）

- **ReDoS 2 筆已修**（d4410b5）：#48 規範檔標題 regex（py/polynomial-redos）→ `lstrip('#')`；#49 selftest 巢狀量詞（py/redos）→ `indented_block`
- **path-injection 3 筆（#45 #46 #47）待 dismiss won't fix**（等子超確認）：source 全是 argv，值由 workflow 寫死（`review.md`、`findings.json`）或 caller 自己 default branch 的 input（`repo-rules-path`），PR 作者改不到；同 #29 的判準
- ⚠️ **#46、#47 是舊 sink 搬家後冒出的新 alert**：#47＝`open(args.review)`（原 #35，won't fix，第 186 行），上面插了新函式、前後文變了就換了指紋；#46＝`open(args.findings)`（原 #36）搬進 `load_findings()`。→ RESUME 待辦「dismiss 綁在 sink 上的後果」的實例：**code 一搬家，dismiss 就跟不上**（不是「不受信任的資料流進已 dismiss 的 sink 會不會重跳」那題本身）

## PR #47 的 AI review（v1.4.1，rubric 同 v1.4.0）

第一次 run：5 筆、3 筆 ≥0.7 貼 inline，**0 成立**（`verify_pr47_findings.py` 逐筆實跑）：

| # | 信心 | 說法 | 判定 |
|---|---|---|---|
| F1 | 0.80 | fence 結束行會掉下去被當成新條目 | 不成立：fence 那段有無條件 `continue`（讀漏）；實跑三種輸入都正確 |
| F2 | 0.75 | 沒有單獨貼的時候沒重排 | 不成立：`normalize` 已排序；不重排是 D1 的刻意設計，註解寫了 |
| F3 | 0.70 | `repo-rules-path` 沒驗路徑、可讀任意檔 | 不成立：**信任邊界型**——caller 自己 default branch 上的值，PR 改不到；`rubric-path` 同寫法。＝v1.4.0 出口頁「限制」那一型的真實 PR 實例（貼成 inline） |
| F4 | 0.65 | `###` 讓條目提前結束 | 不成立：文件寫明的行為，selftest 在測 |
| F5 | 0.60 | `line` 為 None 時 `merge_into` 丟例外 | 不成立（走不到）：`normalize` 把 None 轉 0、`select_inline` 先跳過定不到的；直接餵 None 確實會 TypeError |

第二次 run（ReDoS 修正後，d4410b5）：5 筆、2 筆貼 inline，**1 筆部分成立**：

| # | 信心 | 說法 | 判定 |
|---|---|---|---|
| G1 | 0.75 | `` - ```python `` 條目的 fence 會被誤判 | **部分成立**：機制對（條目那一行開的 fence 沒被認出）、後果講錯（它說切成兩條、code 被丟；實跑是**後面的條目全被吞進 R01**，編號錯位）→ 09c2b05 修＋selftest 紅綠 |
| G2 | 0.70 | 成功但 rules-findings.json 不在時會安靜地說「沒有」 | 不成立：兩個 `return 0` 路徑都先寫檔；兩步之間也沒有 artifact |
| G3 | 0.65 | timeout-minutes 6 不夠 | 不成立：最壞 2×120+2＝242 秒（4.0 分） |
| G4 | 0.60 | 空行後的續行會被丟 | 不成立：空行後縮排續行有接上，docstring 寫明、selftest 在測 |
| G5 | 0.55 | 規範檔不存在回 1 | 不成立：離開碼 1＝設定錯誤，設計如此 |

兩次 run 合計 10 筆：**0 成立、1 部分成立（而且是真問題）、9 不成立**；貼成 inline 的 5 筆裡 G1 是唯一有用的

第三次 run（G1 修正後，09c2b05）：3 筆全 major、全貼 inline（verdict request_changes，kit 只送 COMMENT）：
- H1 0.85「縮排的結尾 ``` 會讓 fence 永遠不關」→ 不成立：正是這次新加的 selftest 那個輸入，實跑 3 條切得正確
- H2 0.80「合併過的規範 finding 會被重複貼」→ 不成立：`main()` 只把 `standalone` 加進要貼的；selftest 斷言合併的 R01 不單獨出現
- H3 0.75 路徑穿越 → 不成立：同 F3，**信任邊界型第二次**

**PR #47 三次 run 共 13 筆：1 部分成立（G1，已修）、12 不成立**；信任邊界型 2 筆（F3、H3，都貼 inline）。同一個 PR 每次重跑報的都不一樣

## 發版驗證（2026-09-28）

- **#48 發版、`v1.5.0` tag**（tag object `fce93b1` → `babdcc6`，01:56:26 UTC 推送；`v1` 未動）
- **probe Phase P：12/12、R1–R2 通過**（`probe-expectations.md`、`probe-P-result.txt`）。第一次判 11/12 是檢查寫錯（log 印出 `run:` 腳本全文，P7 被腳本裡的 warning 字樣誤判），改成只認 `##[warning]` 後同一批 run 重判 12/12
- **#49 merge**（`e8aa586`）：`.github/review-rules.md`（11 條）＋04 暫釘 `@v1.5.0`＋`repo-rules-path`
- **端到端（#50 自己的 review，main 的 04 = v1.5.0＋規範檔）**：
  - run 1 `36368358151`：規範那步真跑、success；規範 11 條、1,185 字元，模型回 1 筆、標了有效編號 0 筆；摘要出現「### repo 規範 / 這次沒有標了規範編號的 finding。」；15 個 step 全 success
  - run 2 `36368536464`：模型回 2 筆、留 0 筆
  - **快取沒命中**：兩次規範那次都只命中 1,536 個 prompt token（7,583、9,362 裡）；前綴跟一般那次逐字相同（selftest 驗過），兩次呼叫只隔幾秒，原因沒查。run 1 費用：一般那次尖峰 $0.0115、規範那次 $0.0098（0.85 倍）→ 程式註解與 USAGE 的「吃得到快取」已更正（#50）
  - **第二十八輪補（#51 反例）**：`scripts/cache_table.py`（log 在 `cache-logs/`）撈五次 run：#50 四次規範那次都 1,536（prompt 7,583–9,499）；**#51 規範那次 2,432／3,074＝一般那次整段 2,469 取 64 的倍數**。五次都是一般那次**結束後 0.06–0.09 秒**就送規範那次（開始到開始 3.6–11.6 秒；#50 run 4 是 4.4 秒、#51 是 3.6 秒，結果相反）→ **間隔不是差別**，「只隔幾秒」這個說法也不精確；看得到的差別只剩 prompt 長度（4 比 1，因果沒驗）
  - **合併那條路徑沒在 GitHub 上走到**（0 筆標了編號）；由 selftest 與本機真 API dry-run（cal.com-11，merged=1）涵蓋
- AI review 判定：
  - #49：J1 0.80 inline「`@v1.5.0` 要改釘 SHA」不成立（把規範第 1 條「外部 action」套到 kit 自己的 reusable；而且跑的是 v1.4.1 一般那次，是模型讀了 diff 裡新加的規範檔自己套用）；J2 0.60「規範檔可被 PR 改」不成立（取自 default branch；**信任邊界型第 3 次**）
  - #50 run 1：K1 0.90「kit-ref 兩句矛盾」不成立（讀錯；措辭已改清楚）；K2 0.80「移 v1 前不能 merge」**成立**（已在流程裡）
  - #50 run 2：L1 0.80 同 K2 **成立**；L2 0.60「快取那句沒講樣本數」**部分成立**（已補第二次實測）
- **移 `v1`**：02:09:19 UTC，`v1` → `fce93b1`（v1.5.0 tag object）→ `babdcc6`；Release v1.5.0（Latest，02:09:36 UTC；body 取 CHANGELOG [1.5.0]，相對連結轉絕對，`make_release_notes.py`）
- **#50 merge**（`750b310`，02:11:41 UTC）：04 改回 `@v1`＋`repo-rules-path`；#50 共 4 輪 review，規範那次每輪都真跑（模型回 1／2／3／1 筆，標了有效編號都是 0）；第三輪 M2（費用倍數驗算不了）部分成立→改寫兩邊實際金額
- **probe Phase F 8/8**（移 v1 之後、原本的 `@v1` caller）→ 這次 probe 合計 22/22

## merge 後 main 的 CodeQL（02:1x UTC 發現）

- main open **2 筆**（#47 merge 後 01:52:54 UTC 的完整分析冒出來，PR 上看不到：那兩行不在 diff 範圍）
  - #50 `deepseek_review.py:188` `open(path)`（`load_text`）＝原 #29（v1.4.1:164）
  - #51 `deepseek_review.py:872` `open(summary_path)`＝原 #34（v1.4.1:673）
- 對照：#28（162→186）、#33（667→864）行號也移了卻**延續**。差別是**後面幾行有沒有變**（#29 後面插了新函式、#34 後面加了 `if rule_ids:`）→ 行號移動不影響指紋，後文變了才換編號
- RESUME 待辦「新資料流進已 dismiss 的 sink 會不會重跳」部分答案：#28 這次多了 `--repo-rules` 流入、指紋沒變，沒有重跳（但 source 同樣是 argv）
- #50、#51 以 won't fix dismiss（子超 09-28 同意，comment 註明原 #29／#34）→ **main open alert 回到 0**

## kit 規範檔拍板（09-28 第二十七輪記錄建議 → 第二十八輪拍板）

`.github/review-rules.md` 現況 11 條（送出時 R01–R11，`##` 標題當分組）與由來：

| # | 分組 | 規則（摘要） | 由來 |
|---|---|---|---|
| R01 | Actions | 外部 action 釘 40 字元 SHA、行尾註解寫完整版本號 | v1.4.1 釘 SHA（#39） |
| R02 | Actions | `run:` 不直接內插 `${{ inputs.* }}`／PR 標題，走 `env:` | v1.0.0 `$(whoami)` injection；v1.4.1 改 6 處 |
| R03 | Actions | `run:` 註解裡不寫完整 `${{ }}` | 09-21 parse error |
| R04 | Actions | secret 逐 step 在 `env:` 明確傳 | 09-28 計畫審查重審（規範那步差點漏 `REVIEW_BLOCKED_TERMS`） |
| R05 | Actions | `v1` 線上不移除、不改名 input，淘汰留 no-op＋warning | v1.2.0 `filter-findings` |
| R06 | Actions | caller 要宣告 `permissions:` | 09-21 startup_failure |
| R07 | prompt | rubric 與 `prompts/rules/` 不寫給人看的註記 | 09-20 元評論改變行為 |
| R08 | Python | 只用標準函式庫 | kit 設計原則 |
| R09 | Python | log 不印禁用詞內容、key、secret | 禁用詞掃描設計；一次 401 事故 |
| R10 | Python | `gh`／`git` 失敗要看得見，不被 `check=False`、空值吞掉 | 09-21 PR #5：全綠卻零留言 |
| R11 | 文件 | 給人照做的文件不寫「檔名:行號」 | 09-25 SETUP-CHECKLIST |

**拍板（子超 2026-09-28 第二十八輪）**：
- **R01 照草稿收窄** → PR #51（branch `chore/review-rules-r01`，commit `01f3772`，02:39 UTC 開）。用 kit 的 `parse_repo_rules`／`render_repo_rules` 比對前後：11 條、編號不變、只有 R01 變；送出長度 1,185 → 1,251 字元；selftest 21 組 162 項全綠（`scratchpad` 的 `check_rules_diff.py`，一次性）
  - 拍板前補查的證據：① #49 J1 是**一般那次**（v1.4.1，當時還沒有規範那次）讀了 diff 裡新加的規範檔自己套用 ② **規範那次**在 #50 真跑 4 次、diff 裡就有 `@v1.5.0 → @v1`：標 R01 的 0 筆、四份 `rules-review.md` 摘要都沒提 SHA（兩份提到那行，講的是 v1 還沒移會 startup_failure = K2/L1）；沒標編號的原始 finding 不在 artifact 裡，所以只能說「摘要裡沒出現」③ selftest [18] 的 `workflow_uses` 跳過 `./` 與所有 `/.github/workflows/` 引用＝只管 action；本 repo 引用的 reusable workflow 只有自己的（03/04 兩處＋四支 reusable 開頭註解）④ R01 文字只出現在規範檔本身
  - ⇒ 改的理由是**文字歧義＋發版驗證期間每次都會碰到**，不是「規範那次已經誤套過」
  - #51 自己的 review（04 run `36370692594`）：一般那次 0 筆、approve；規範那次（用 main 上的舊 R01，1,185 字元）模型回 0 筆；摘要以 review 形式貼出，含「### repo 規範／這次沒有標了規範編號的 finding。」；checks 全過、PR 上 CodeQL 0 筆
  - **merge `7c0ccdc`（02:43:54 UTC，squash，遠端 branch 已刪）**；之後的 PR 才用新 R01（1,251 字元）
  - merge 後 main 的 CodeQL（02:44:38 UTC 分析 `7c0ccdc`）：results_count 31（同 `750b310`）、**open 0**（02:45 UTC 查）
- **R10 留著，退場條件先定好**（照 [[expectation-table-before-run]]，事後才判會被結果帶著走）：**標到 R10 的 finding 累積到 3 筆時算成立幾筆，≤1 筆成立 → 收窄或拿掉**。計數從 v1.5.0 開規範檔起算（至 #50 為 0 筆）；每筆照常實跑驗證
- **09-30 拿掉 R01**（子超裁定；依據 `2026-09-28-v160-inline/README.md` 觀察段：收窄後 #56、#57 仍誤套 2/2，selftest [18] 已確定性地檢查同一件事）→ PR #58（branch `chore/review-rules-drop-r01`，commit `ea41319`，04:16 UTC 開）。用 kit 的 `parse_repo_rules`／`render_repo_rules` 比對前後：11 → 10 條，移除的只有原 R01，其餘文字逐字不變、依序往前一號；送出長度 1,251 → 1,044 字元；selftest 22 組 171 項全綠（`scratchpad` 的 `compare_rules.py`，一次性）
  - ⚠️ **上表是 #58 之前的編號**。#58 merge 後原 R02–R11 → R01–R10：**R10 觀察追的那條（`gh`／`git` 失敗要看得見）變成 R09**，新的 R10 是「檔名:行號」。計數照內容延續，不照編號（編號是位置指標，同 [[locate-by-snippet-not-line-number]]）
  - 考慮過保留編號的兩種做法都不採用：① 留一個佔位條目（`- ` 開頭就會被當成規範送出＝prompt 裡的元評論，違反 R07／新 R06）② 把 `## 文件` 整節移到最前面，讓 R02–R10 編號不動（R01 換成「檔名:行號」，跟「R01 誤套」的紀錄衝突；而且是讓檔案順序去綁編號穩定度，下次刪條目又要再移一次）→ 照順序重排、PR 說明附對照表、觀察照內容追
  - #58 自己的 04 仍用 main 上的舊 11 條（含 R01），標到的編號照舊表讀
  - #58 的 04（run `36668105573`，04:16:35 UTC 建立）：`Uses: …@refs/tags/v1 (40c2a78…)`＝v1.6.0；`repo 規範：11 條、1251 字元`；一般那次與規範那次都 0 筆、approve；`inline=0`（不是 `off`）、`完成：inline 0 筆已張貼`；沒有 `##[warning]`／`[warn]`。**R10（舊編號）計數至 #58 仍 0 筆**
  - 摘要內文兩點「需注意」（不在 Findings 表）實查：① 「selftest 沒涵蓋所有第三方 action」**不成立**：repo 沒有 composite action；workflows 以外的 `uses:` 只有文件範例、CodeQL query suite、selftest 測資；引用的 reusable workflow 全是自己的。理論邊界：**第三方 reusable workflow** [18] 不檢查、R01 括號的定義（`uses:` 指到別的 repo）涵蓋得到，目前 0 處 ② 「其他文件或自動化依賴舊編號」**已處理**：`cited_rule` 每次照當下的檔案產生編號；tracked 檔裡的 R 編號只有格式範例（`[R03]`）與歷史 CHANGELOG；R10 觀察已改照內容追
  - 查 ① 時自己的檢查先錯一次：`git grep -E` 不支援 `\s`／`\S`（`uses:\s` 0 筆 vs `uses:[[:space:]]` 8 筆，USAGE.md），空結果長得像「沒有」；改純字串＋陽性對照（03/04 引用自己 reusable 那兩行）才查實
  - 規範那次快取命中 2,432／3,079（diff 只有 markdown、沒套到補充規則）＝「沒分岔就幾乎整段命中」第 2 例 → [[deepseek-cache-back-to-back-miss]]
  - **merge `f36c025`（04:22:03 UTC，squash，遠端 branch 已刪；本機 branch 比對 tree 相同後刪除）**；之後的 PR 才用新的 10 條（1,044 字元）
  - merge 後 main：`f36c025` 的 kit selftest／02 codeql（push）都 success；CodeQL 分析（04:22:53 UTC）results_count 31（同 `7c0ccdc`）、**open 0**

原待拍板內容：
1. **R01 收窄**。改寫草稿：「**第三方** action（`uses:` 指到別的 repo）一律釘 40 字元的 commit SHA，行尾註解寫完整版本號（例如 `# v7.0.1`）。只寫 `# v7`、或版本號後面還接著別的字，Dependabot 換 SHA 時不會跟著更新註解。本 repo 自己的 reusable workflow 用 tag 引用是刻意的，不在此限」。依據：#49 的 AI review 把 R01 套到 `uses: …/reusable-ai-review-post.yml@v1.5.0`；selftest [18] 本來就只管第三方
2. **R10 觀察**：比其他條靠判斷，誤報可能較高；目前 4 次真跑標了編號的 0 筆，沒資料。可以先留著，等有標到它的 finding 再看
3. 拍板後改的話走小 PR（改的是 default branch 上的規範檔，merge 之後的 PR 才生效）
