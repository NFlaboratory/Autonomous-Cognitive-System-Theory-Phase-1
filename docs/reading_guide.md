# 読み方の案内：最初に読む定義 20 と命題 10

- 本文は定義 186・命題 48・補題 3 を含む。初めて読むときは、次の 30 項目を順に読み、その後で必要な節に進むことを勧める。
- 表の「ラベル」は `paper/` の `\label` である。付録 C（定義・命題等の一覧）で番号とページを引ける。
- 選んだ基準は、三原理・可行性核・閉塞と崩壊の区別という本論文の骨格を、最短で追えることである。重要度の順位ではない。
- 依存関係の機械的な索引は `docs/dependency_table.md` にある（抽出の限界は同ファイルの冒頭を参照）。

## A. 定義 20

| # | 節 | ラベル | 名称 | 読む理由 |
|---|---|---|---|---|
| 1 | §2 | `def:acs` | 自律認知システム | 7タプル $\Sigma=(X,U,E,f,\Pi,M,\mathrm{Update})$ |
| 2 | §2 | `def:Eext_decomposition` | 外部環境状態空間の分解 | $E_{\mathrm{ext}}=E^{\mathrm{bg}}\times O$（外生背景成分と行動応答成分） |
| 3 | §2 | `def:environment_space` | 必要環境要因と必要環境空間 | $\eta:X\times E_{\mathrm{ext}}\to\{0,1\}$。$E$ と $E_{\mathrm{ext}}$ の区別 |
| 4 | §2 | `def:E_req` | 必要環境充足集合 | $E_{\mathrm{req}}(x)$。可行性核の外乱の範囲になる |
| 5 | §2 | `def:state_transition` | 状態遷移 | $f:X\times U\times E_{\mathrm{ext}}\to X$ |
| 6 | §2 | `def:Pi` | 持続評価関数 | $\Pi$ |
| 7 | §2 | `def:K` | 可行集合 | $K=\{x\mid\Pi(x)\ge0\}$ |
| 8 | §2 | `def:at` | 可行行動対応と可行行動集合 | $A(x,e)$、$A_t$ |
| 9 | §2 | `def:blockage_sec2` | 閉塞 | $A_t=\emptyset$。崩壊とは別の概念 |
| 10 | §2 | `def:primitive_functions` | 原始的な機能 | 感知・識別・評価・行動の四区分 |
| 11 | §2 | `def:internal_model` | 内部モデル構造 | $M$。真の $\Pi$ や $A_t$ を ACS が知ることとは区別される |
| 12 | §2 | `def:collapse` | 崩壊状態指標と崩壊指標 | (SC-1)・(SC-2)、$\mathrm{CS}_{i,t}$ と $\mathrm{Col}_{i,t}$ |
| 13 | §2 | `def:functional_termination` | 機能的終端状態指標と機能的終端指標 | 崩壊と別の終端概念 |
| 14 | §3 | `def:principle_time_domain` | 原理判定時刻域 | 時刻別充足述語が定義される時刻の範囲 |
| 15 | §3 | `def:SM` | SM の時刻別充足述語 | $x_t\in K$ |
| 16 | §3 | `def:eu_critical_domain` | 一段階臨界域 | 条件 (i)〜(iii)。EU の中心 |
| 17 | §3 | `def:EU` | EU の時刻別充足述語 | 臨界必要要因がすべて充足されること |
| 18 | §3 | `def:fr_domain` | FR の定義域 | FR は EU が真の所でだけ定義される |
| 19 | §3 | `def:FR` | FR の時刻別充足述語（局所 FR） | $A_t\neq\emptyset$。未定義は偽ではない |
| 20 | §3 | `def:viab_core` | $E_{\mathrm{req}}$ ロバスト可行性核 | $\exists u\,\forall e\in E_{\mathrm{req}}(x)$ の量化 |

## B. 命題 10

| # | 節 | ラベル | 名称 | 内容の要点 |
|---|---|---|---|---|
| 1 | §2 | `prop:termination_order` | 機能的終端と崩壊の順序および崩壊後の整形式実現 | 崩壊の時刻までに機能的終端は成立済み |
| 2 | §3 | `prop:sm_K_equiv` | SM と可行集合の同値性 | 定義的な同値 |
| 3 | §3 | `prop:eu_blockage` | 臨界必要要因の非充足と閉塞 | EU が偽なら閉塞 |
| 4 | §3 | `prop:fr_domain_eu` | 定義域と EU の時刻別充足述語 | FR が定義されることと EU が真であることの同値 |
| 5 | §3 | `prop:blockage_dichotomy` | 閉塞の二分 | (B1) 臨界必要要因非充足閉塞と (B2) 臨界必要要因充足下閉塞 |
| 6 | §3 | `prop:selection_responsibility` | 選択の責務 | 述語がすべて真でも、$u_t\notin A_t$ なら $K$ の外に出る |
| 7 | §3 | `prop:viab_core_max` | 最大 $E_{\mathrm{req}}$ 不変集合の存在 | 可行性核は不変で最大 |
| 8 | §3 | `prop:viab_stage_finite` | 有限状態空間における可行性核と有限段頑健可行集合 | $X$ が有限なら段の反復が核に一致する（仮定を用いない） |
| 9 | §3 | `prop:kernel_standard_comparison` | 可行性核と全環境頑健核・楽観核の包含関係 | 標準的な二つの核との包含関係（仮定を用いない） |
| 10 | §3 | `prop:sd_robust_nonresponse` | 主命題：応答多様性縮退と応答の弱点の持続による頑健応答不能の持続 | 強仮定を用いない主命題。強仮定のもとの系は `prop:sd_necessity` |

## C. 次に読むところ

- 仮定の一覧と各仮定の主な依拠箇所：§2 の仮定一覧表。
- 機構の標準形式（TIPA・PSL・ISL）：§4。原理水準と機構水準の区別は `rem:principle_level_locus`。
- 閉塞と可行性核の関係、崩壊経路集合：§7（`prop:blockage_viability_kernel`）。
- 限界と未解決問題：§9。
