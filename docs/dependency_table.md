# 命題・補題の依存一覧（自動生成）

- 生成：`python3 -I tools/gen_dependency_table.py paper docs/dependency_table.md`
- 対象：本文（§1〜§9）の命題 48・補題 3。各命題・補題の主張と、その直後の証明の中で `\ref` により参照される仮定・定義・命題・補題を列挙する。
- 「仮定~\ref{…} を用いない」のように不使用を述べる文（「用いない」「用いず」「使わない」を含む文）の中の参照は依存から除いた（除外した参照は末尾に記す）。
- **抽出の限界**：`\ref` を使わず言葉だけで依拠している場合、定義の整形式性を通じた間接的な依存、および備考・地の文での参照は数えていない。文の区切りによる除外は機械的であり、一つの文に使用と不使用が混在する場合は使用も除外される。依存関係の完全な記述ではなく、照合を始めるための索引である。

| 節 | 種類 | ラベル | 表題 | 参照する仮定 | 参照する定義の数 | 参照する命題・補題 |
|---|---|---|---|---|---|---|
| §2 | 命題 | `prop:xi_se_independence` | $\xi_{\mathrm{bnd},t}$ と $S_{\mathrm{struct}}$ の独立性 |  | 0 |  |
| §2 | 命題 | `prop:realized_reestablishment` | 実現した軌道上の再成立 |  | 2 |  |
| §2 | 命題 | `prop:collapse_basic` | 機能的終端指標と崩壊指標の基本性質 |  | 2 |  |
| §2 | 命題 | `prop:termination_order` | 機能的終端と崩壊の順序および崩壊後の整形式実現 |  | 3 |  |
| §2 | 命題 | `prop:theta_from_pi` | 可行性の等価性と $K$ の導出可能性 |  | 1 |  |
| §2 | 命題 | `prop:At_compact` | 可行行動集合の閉性とコンパクト性 | `ass:compact_spaces` `ass:f_continuity` | 1 |  |
| §2 | 命題 | `prop:nondegeneracy_implication` | 非退化性の水準間の含意 | `ass:env_viable_nondegeneracy` `ass:env_input_nondegeneracy` | 1 |  |
| §2 | 命題 | `prop:feasibility_sensitivity_scope` | 評価の可行性感応性が要求を課す範囲 | `ass:env_viable_nondegeneracy` | 2 | `prop:nondegeneracy_implication` |
| §3 | 補題 | `lem:principle_time_domain_down` | 原理判定時刻域の下方閉性 |  | 0 | `prop:collapse_basic` `prop:termination_order` |
| §3 | 命題 | `prop:pi_subdiff` | $\Pi$ の Lipschitz 連続性と Clarke 一般化勾配構造 |  | 1 |  |
| §3 | 命題 | `prop:pi_violation_profile` | $\Pi$ と閾値割れ集合の関係 |  | 2 |  |
| §3 | 命題 | `prop:sm_K_equiv` | SM と可行集合の同値性 |  | 2 |  |
| §3 | 命題 | `prop:sm_one_step_A` | 一段階の $K$ 保持と $A_t$ |  | 3 |  |
| §3 | 命題 | `prop:viab_core_max` | 最大 $E_{\mathrm{req}}$ 不変集合の存在 |  | 0 |  |
| §3 | 命題 | `prop:viab_stage_nested` | 有限段頑健可行集合の入れ子性 |  | 1 |  |
| §3 | 命題 | `prop:viab_stage_core` | $E_{\mathrm{req}}$ ロバスト可行性核と有限段頑健可行集合 |  | 2 | `prop:viab_core_max` |
| §3 | 命題 | `prop:viab_stage_finite` | 有限状態空間における可行性核と有限段頑健可行集合 |  | 2 | `prop:viab_stage_nested` `prop:viab_stage_core` |
| §3 | 命題 | `prop:kernel_standard_comparison` | 可行性核と全環境頑健核・楽観核の包含関係 |  | 1 | `prop:viab_core_max` |
| §3 | 命題 | `prop:viab_resp_max` | 応答込み頑健可行性核の不変性 |  | 0 |  |
| §3 | 命題 | `prop:robust_noninclusion` | 二つの頑健性の非包含 |  | 1 |  |
| §3 | 命題 | `prop:pi_E_sensitivity` | $\pi_E$ の最小感応性：同値版 | `ass:env_response` | 0 | `prop:pi_subdiff` |
| §3 | 命題 | `prop:eu_blockage` | 臨界必要要因の非充足と閉塞 |  | 1 |  |
| §3 | 命題 | `prop:eu_sm_next` | 臨界必要要因の非充足と次時刻の状態 |  | 1 | `prop:eu_blockage` `prop:sm_one_step_A` |
| §3 | 命題 | `prop:eu_fire_domain` | 臨界必要要因と要因別充足状態域 |  | 3 |  |
| §3 | 命題 | `prop:fr_domain_eu` | 定義域と EU の時刻別充足述語 |  | 3 |  |
| §3 | 命題 | `prop:fr_one_step` | 系：局所 FR と次状態の $K$ への所属 |  | 1 | `prop:sm_one_step_A` |
| §3 | 命題 | `prop:fr_next_sm` | 局所 FR の偽と次時刻の状態 |  | 2 | `prop:sm_one_step_A` |
| §3 | 命題 | `prop:fr_mu_eff` | 局所 FR と応答多様度 |  | 1 |  |
| §3 | 命題 | `prop:viab_stage_fr` | 有限段頑健可行集合と局所 FR |  | 4 |  |
| §3 | 命題 | `prop:selection_responsibility` | 選択の責務 |  | 0 | `prop:sm_one_step_A` |
| §3 | 命題 | `prop:blockage_dichotomy` | 閉塞の二分 |  | 3 | `prop:eu_blockage` `prop:fr_domain_eu` |
| §3 | 命題 | `prop:robust_nonresponse_viab` | 頑健応答不能と頑健可行集合 |  | 1 | `prop:viab_core_max` |
| §3 | 命題 | `prop:exterior_blockage` | $K$ 外部持続と閉塞 | `ass:theta_exterior_blockage` | 2 |  |
| §3 | 補題 | `lem:sd_viab` | 応答多様性縮退と応答の弱点による頑健応答不能 |  | 5 | `prop:viab_core_max` |
| §3 | 補題 | `lem:finite_exit` | 可行性核外部におけるロバスト可行性の喪失 |  | 0 | `prop:viab_core_max` |
| §3 | 命題 | `prop:sd_robust_nonresponse` | 主命題：応答多様性縮退と応答の弱点の持続による頑健応答不能の持続 |  | 2 | `lem:sd_viab` `prop:robust_nonresponse_viab` |
| §3 | 命題 | `prop:sd_necessity` | 系：応答多様性縮退の持続からの有限時間閉塞；強仮定のもとで | `ass:theta_exterior_blockage` | 0 | `prop:sd_robust_nonresponse` |
| §3 | 命題 | `prop:sd_necessity_fr` | 系：応答多様性縮退の持続と局所 FR | `ass:theta_exterior_blockage` | 2 | `prop:sd_robust_nonresponse` `prop:blockage_dichotomy` `prop:sd_necessity` `prop:viab_stage_fr` |
| §3 | 命題 | `prop:kernel_maintenance` | 核に留まる応答を選び続ける軌道 |  | 0 |  |
| §3 | 命題 | `prop:tstab_implies_principles` | T-STAB から有限窓内の時刻別充足述語への含意 |  | 1 | `lem:principle_time_domain_down` `prop:fr_domain_eu` |
| §3 | 命題 | `prop:tstab_zero_margin` | 時刻別充足述語の真と T-STAB |  | 1 |  |
| §4 | 命題 | `prop:purpose_self_attribution` | 目的の自己帰属性 |  | 5 |  |
| §4 | 命題 | `prop:purpose_ad_slot` | 外部側の区分と枠の作用差 |  | 1 |  |
| §5 | 命題 | `prop:s5_one_step` | P1：一段の整形式性 |  | 6 |  |
| §5 | 命題 | `prop:s5_continuation` | P2：数学的作動記録の継続 |  | 0 |  |
| §5 | 命題 | `prop:s5_causality` | P3：作動記録の因果性 |  | 1 |  |
| §5 | 命題 | `prop:s5_observation_causality` | 観測経由性の検査条件と内部モデルの因果性 | `ass:s5_observation_factorization` | 0 |  |
| §6 | 命題 | `prop:Q_not_RO_condition` | $Q$ と構造的環境結合条件の定義式上の相互非参照 |  | 4 |  |
| §7 | 命題 | `prop:blockage_viability_kernel` | 閉塞と $E_{\mathrm{req}}$ ロバスト可行性核の関係 |  | 2 |  |
| §7 | 命題 | `prop:recover_excludes_termination` | 外的回復可能性と終端状態指標 |  | 1 |  |
| §8 | 命題 | `prop:org_blockage_characterization` | 組織水準の閉塞の特徴づけ |  | 1 |  |

## 仮定ごとの使用（命題・補題とその証明の中での参照）

| 仮定 | 参照する命題・補題 |
|---|---|
| `ass:no_branching` | （なし） |
| `ass:compact_spaces` | `prop:At_compact` |
| `ass:f_continuity` | `prop:At_compact` |
| `ass:Eext_time_fixed` | （なし） |
| `ass:f_decomposition` | （なし） |
| `ass:env_input_nondegeneracy` | `prop:nondegeneracy_implication` |
| `ass:env_viable_nondegeneracy` | `prop:nondegeneracy_implication` `prop:feasibility_sensitivity_scope` |
| `ass:viable_realizability` | （なし） |
| `ass:M_compact` | （なし） |
| `ass:env_response` | `prop:pi_E_sensitivity` |
| `ass:nonstationary` | （なし） |
| `ass:theta_exterior_blockage` | `prop:exterior_blockage` `prop:sd_necessity` `prop:sd_necessity_fr` |
| `ass:functional_concurrency` | （なし） |
| `ass:m1c_temporal` | （なし） |
| `ass:psl_minimal` | （なし） |
| `ass:impl_structure` | （なし） |
| `ass:fast_structural_consistency` | （なし） |
| `ass:s5_observation_factorization` | `prop:s5_observation_causality` |
| `ass:obj_stable` | （なし） |
| `ass:unidirect_scope` | （なし） |
| `ass:bidirect_scope` | （なし） |

命題・補題とその証明から参照されない仮定：14 件（21 件中）。定義・備考・地の文での参照は別に数える必要がある。

## 依存から除いた参照（不使用を述べる文）

- `prop:sd_robust_nonresponse` の中の `ass:theta_exterior_blockage`
