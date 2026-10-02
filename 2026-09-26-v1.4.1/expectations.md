# v1.4.1 兩段式發版的 probe 預期表

> 寫於 2026-09-26 11:2x UTC，**打 tag 之前**。`<v1.4.1 tag object>`、`<merge commit>`、`<#N>` 在打完 tag、觸發之前補；其餘項目觸發之前定稿，之後不改。
> 對照基準：`../2026-09-24-v1.4.0-regression/`（R1–R7，7/7）與 `../2026-09-24-actions-policy/` 的 E3（09-24 當時 collect/code-review 都 failure、post skipped）。
> 花費預期 $0：probe 的 key 是假值，401 發生在計費之前。

## Phase S：probe 暫時釘 `@v1.4.1`（Actions 政策 = 還原後那行 JSON）

| # | 預期 | 在哪裡看 |
|---|---|---|
| S1 | collect、post 的 log 寫 `…@refs/tags/v1.4.1 (<v1.4.1 tag object>)` | `gh run view --log` |
| S2 | post 的 kit checkout：`HEAD is now at <merge commit> chore: 發布 v1.4.1 (#N)` | post 的 log |
| S3 | collect：success | `gh run list` |
| S4 | code-review：success（reviewdog、gitleaks、CodeQL Analyze、Trivy 四個 job success；dependency review skipped） | jobs |
| S5 | post：failure，停在 HTTP 401 | post 的 log |
| S6 | post 的 log 有 1 行 filter-findings no-op 的 `##[warning]` | post 的 log |
| S7 | 「送出前掃描」0 行 | post 的 log |
| S8 | 三個 run 的 `Download action repository` 全部是 `@<40 hex>`，沒有 `@v` 開頭的（含 trivy 的兩層巢狀） | 三份 log |
| S9 | code-review 的 reviewdog 那一步印出 `LINT_NAME: shellcheck`，而且那個 job success（④ static 部分實跑） | code-review 的 log |

## Phase E：重跑 E3（probe 仍釘 `@v1.4.1`，`sha_pinning_required=true`）

Phase S 的 post 跑完之後才改設定（post 是 `workflow_run`，開始時才判定政策）。

| # | 預期 |
|---|---|
| E1 | 改完 GET = `{"enabled":true,"allowed_actions":"all","sha_pinning_required":true}` |
| E2 | collect：**success**（09-24：failure，Set up 就被擋） |
| E3 | code-review：**success**，四個 job success、dependency review skipped（09-24：四個 job 在 Set up 失敗） |
| E4 | post：failure，停在 HTTP 401（09-24：skipped）。post 走到 401 ⇒ checkout ×2、download-artifact、upload-artifact 都在 Set up 通過了政策檢查 |
| E5 | 三個 run 的 log 都沒有 `must be pinned to a full-length commit SHA` |
| E6 | 還原後 GET 用字串比對，跟實測前那行 JSON 一模一樣 |

**追加（E2–E5 跑完後、還原政策前寫的，11:4x UTC）**：E2–E4 全綠，只證明了四格中的一格——政策如果此刻沒生效，也會是這個結果。所以在同一個設定下 dispatch 還在用 tag 引用的 `t-collect-nopr`（`@v1` = v1.4.0，內部 `actions/checkout@v7`、`actions/upload-artifact@v7`）當正向對照：

| # | 預期 |
|---|---|
| E7 | `t collect nopr` 的 run：failure（Set up 就被擋，不是 startup_failure——09-24 E3 的判定時間點） |
| E8 | log 有 `must be pinned to a full-length commit SHA`，點名 `actions/checkout@v7` 與 `actions/upload-artifact@v7` |

## Phase F：probe 改回 `@v1`，建 Release、移 `v1` 之後

| # | 預期 |
|---|---|
| F1 | collect、post 的 log 寫 `…@refs/tags/v1 (<v1.4.1 tag object>)` |
| F2 | `HEAD is now at <merge commit> chore: 發布 v1.4.1 (#N)`（`kit-ref` 用預設 `v1`） |
| F3–F7 | 同 S3–S7 |

## 結果：24/24，$0

| Phase | 觸發（probe trigger） | collect / code-review / post | 結果 |
|---|---|---|---|
| S（`@v1.4.1`，政策 all） | `d7ace96` 11:37:38 | `36239415325` / `36239415313` / `36239424354` | **9/9**。S8：下載的 action 11 種，全是 SHA |
| E（`@v1.4.1`，`sha_pinning_required=true`） | `7979b1d` 11:39:33 | `36239512121` / `36239512130` / `36239521606` | **E1–E6 6/6**：collect、code-review success，post 走到 401，0 行 `must be pinned`；11:42:13 還原，字串比對一致 |
| E 正向對照（同一設定，`t collect nopr` 用 `@v1`＝v1.4.0） | dispatch 11:41:38 | `36239620692` | **E7–E8 2/2**：failure，`actions/checkout@v7 and actions/upload-artifact@v7 … must be pinned to a full-length commit SHA`（與 09-24 E3 同一句） |
| F（`@v1`，`v1` 已移） | `71c75aa` 11:42:58 | `36239690452` / `36239690531` / `36239702148` | **7/7**。`@refs/tags/v1 (96c5bf9…)`、`HEAD is now at 2570d55` |

四格：v1.4.0×政策關＝綠、v1.4.0×強制釘 SHA＝**紅**（09-24、今天 E7/E8）、v1.4.1×政策關＝綠（S）、v1.4.1×強制釘 SHA＝**綠**（E）⇒ 差別來自釘 SHA，而且政策當下確實生效。

check.sh 本身先拿 09-24 v1.4.0 回歸的三個 run 驗過（[8] 列出 7 個 tag 引用、[9] 空 ⇒ 分得出新舊版）。小坑：E8 第一次用 `grep -E '…{0,260}'`，BSD grep 的重複上限是 255 → 明確報錯，改 250 重跑。

## 補填（打完 tag、觸發之前，2026-09-26 11:3x UTC）

- v1.4.1 tag object：`96c5bf9`（`96c5bf9822857caf775cca0072511042d6fd3de1`）
- 發版 merge commit：`2570d55`（`2570d556d8865563d21ed24a3c16462c2df32532`）
- 發版 PR 編號：#41
- → S1 要看到 `@refs/tags/v1.4.1 (96c5bf9…)`；S2／F2 要看到 `HEAD is now at 2570d55 chore: 發布 v1.4.1 (#41)`
- → F1 要看到 `@refs/tags/v1 (96c5bf9…)`（`git tag -f v1 v1.4.1` 讓 `v1` 指向 v1.4.1 的 tag object，同 v1.4.0 那次）
- 打完 tag 時 `v1` 仍是 `23023b4` → `fa37001`（v1.4.0），沒動
