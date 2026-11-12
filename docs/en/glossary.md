# Glossary for the English summary

The English terms used in this directory. The list grows as sections are added.

**Source** column:
- **manuscript**: the manuscript itself states this English name.
- **overview**: already used in `docs/ACS_Phase1_overview_en.md`; kept for consistency.
- **approved**: chosen for this summary and approved by the author (2026-11-11). A term added later is marked **proposed** until the author approves it; by the author's standing instruction (2026-11-11), a proposed term is approved once both the drafting model and the independent auditor find it acceptable.

## 1. Rules of use

1. **"Feasible" and "viable".** In the definitions and results of ACS theory itself, the Japanese 可行 is rendered *feasible* / *feasibility* (feasible set, feasible action, feasible response). *Viability* and *viable* are used in established names from viability theory (*viability kernel*, *viability theory*) and where a cited work's own terminology is described (for example, Di Paolo's conditions of viability).
2. **Principles.** A principle has no truth value. What has a truth value is its **time-indexed satisfaction predicate**, and only on the principle time domain. Write "the time-indexed satisfaction predicate SM is false at $t$", not "SM fails" or "SM is violated".
3. **Undefined is not false.** Every time-indexed satisfaction predicate is defined only for $t\in\mathbb T_{\mathrm P,i}$ (`def:principle_time_domain`). $\mathrm{FR}_t$ is further defined only when $(x_t,e_t)\in\mathcal D_{\mathrm{FR}}$ (`def:fr_domain`, `def:FR`). Where a predicate is undefined, write "undefined", never "false".
4. **Collapse.** *Collapse* refers only to the following two indicators of `def:collapse`. The collapse-state indicator $\mathrm{CS}_{i,t}=1$ means that conditions (SC-1) and (SC-2) hold at time $t$. The collapse indicator $\mathrm{Col}_{i,t}=1$ is a history: it means that $\mathrm{CS}_{i,t'}=1$ for some $t'\le t$. "Collapse has occurred by time $t$" is expressed by $\mathrm{Col}_{i,t}=1$. Blockage, functional termination, loss of well-formed realization, zero health, a zero functional axis, and total functional stoppage are each not, by themselves, collapse. Do not write "structural collapse" or "functional collapse".
5. **Claim strength.** The English must not be stronger than the Japanese. In particular, *guarantee* and *ensure* are used only for proved consequences.

## 2. Terms

| Japanese | English | Source |
|---|---|---|
| 自律認知システム（ACS） | autonomous cognitive system (ACS) | manuscript |
| 倫理的協調知性理論（ECIT） | Ethical Coordinative Intelligence Theory (ECIT) | manuscript |
| 自己維持（SM） | self-maintenance (SM) | manuscript |
| 環境利用（EU） | environmental utilization (EU) | manuscript |
| 可行応答（FR） | feasible response (FR) | manuscript |
| 三機構情報処理アーキテクチャ（TIPA） | Triadic Information-Processing Architecture (TIPA) | manuscript |
| 物理的基盤層（PSL） | Physical Substrate Layer (PSL) | manuscript |
| 実装部位層（ISL） | Implementation Substrate Layer (ISL) | manuscript |
| 三原理時間統合評価条件（T-STAB） | three-principle time-integrated evaluation condition (T-STAB) | approved |
| 型分離規約（TSC） | Type Separation Convention (TSC) | manuscript |
| 規約／構成要件／仮定 | convention / constitutive requirement (CR) / assumption | manuscript |
| 整形式 | well-formed | manuscript |
| 自動性 | automaticity | manuscript |
| 差別化核 | discriminating kernel | manuscript |
| 明示された仮定のもとで | under stated assumptions | manuscript |
| 本枠組みの範囲内で | within the present framework | manuscript |
| 持続評価関数 $\Pi$ | persistence evaluation function | overview |
| 可行集合 $K$ | feasible set | overview |
| 可行行動集合 $A(x,e)$ | feasible action set | overview |
| 必要環境要因（$\eta\in E$） | required environmental factor | overview |
| 外部環境状態空間 $E_{\mathrm{ext}}$ | external environment state space | overview |
| $E_{\mathrm{req}}$ ロバスト可行性核 $\mathrm{Viab}_f(K)$ | $E_{\mathrm{req}}$ robust viability kernel | overview |
| 制約軸 | constraint axis | overview |
| 時刻別充足述語 | time-indexed satisfaction predicate | overview |
| 原理判定時刻域 $\mathbb T_{P,i}$ | principle time domain | overview |
| 一段階臨界 | one-step critical | overview |
| 原理水準／機構水準 | principle level / mechanism level | overview / approved |
| 閉塞（$A_t=\emptyset$） | blockage | overview |
| 崩壊 | collapse | overview |
| 機能的終端 | functional termination | overview |
| 整形式実現の不成立 | loss of well-formed realization | overview |
| 構造的個体 | structural individual | overview |
| 組織ACS | organizational ACS | overview |
| 標準機能形式（分類B） | standard functional form (classification B) | approved |
| 外部対象 | external object | overview |
| 一段の作動記録 | one-step operation record; record of one step of operation | overview |
| 標準作動形式 | standard operation form | approved |
| 時刻間の接続 | connection between time steps | approved |
| 関係品質 | relation quality | approved |
| 双方向合成関係 | bidirectional composite relation | approved |
| 方向性指標 | direction indicator | approved |
| 同種相互関係／異種相互関係 | homogeneous / heterogeneous mutual relation | approved |
| 双方向成立カテゴリー | bidirectional establishment category | approved |
| 関係品質の評価規則 | evaluation rule of relation quality | approved |
| 関係品質の評価可能域 | evaluable domain of relation quality | approved |
| 正側／中立／負側関係品質 | positive-side / neutral / negative-side relation quality | approved |
| 負の関係品質を伴う環境結合 | environment coupling with negative relation quality | approved |
| 関係品質の有限窓評価 | finite-window evaluation of relation quality | approved |
| 代表カテゴリーラベル集合 | set of representative category labels | approved |
| 六系分類 | six-family classification | approved |
| 競合隔離系 | competition and isolation family | approved |
| 認識された関係 | recognized relation | approved |
| 記述的状態帯 $\mathsf Z_0,\dots,\mathsf Z_5$ | descriptive state band | approved |
| 記述的崩壊前状態帯（崩壊前状態帯） | descriptive pre-collapse state band (pre-collapse state band) | approved |
| 基準帯 $\mathsf Z_0$ | reference band | approved |
| 許容外的作用集合 $\Upsilon_{\mathrm{adm},i}$ | admissible external action set | approved |
| 外的回復述語 $\mathrm{Recover}_{i,t}$／外的回復可能性 | external recovery predicate / external recoverability | approved |
| ACS記録有効時刻域 $I_{\mathrm{ACS}}(\sigma)$ | ACS-record-valid time domain | approved |
| 軌道記録空間 $\mathfrak P$／軌道記録 | trajectory record space / trajectory record | approved |
| 閉塞経路集合 $\mathfrak P_{\mathrm{blk}}$ | blockage path set | approved |
| 閉塞到達時刻 $T_{\mathrm{blk}}$ | blockage reaching time | approved |
| 崩壊到達経路集合 $\mathfrak P_{\mathrm{col}}$ | collapse-reaching path set | approved |
| 崩壊到達時刻 $T_{\mathrm{col}}$ | collapse reaching time | approved |
| 流入傾向 | inflow tendency | approved |
| 集団／組織／社会 | group / organization / society | approved |
| ACS組織 | ACS organization | approved |
| 個体ACS参加型組織ACS／個体ACS非参加型組織ACS | organizational ACS with / without individual-ACS participation | approved |
| 参加ACS集合 $\mathbb I_{\mathrm{org},t}(\mathcal O)$／参加ACS数 | participating-ACS set / participating-ACS number | approved |
| 組織水準のACS構造 $\Sigma_{\mathrm{org}}$ | organization-level ACS structure | approved |
| 組織水準の可行集合 $K_{\mathrm{org}}$／可行行動集合 $A_{\mathrm{org},t}$ | organization-level feasible set / feasible action set | approved |
| 組織ACSの記述的適用規約 | descriptive applicability convention for the organizational ACS | approved |
| 論理的地位 | logical status | approved |
| 可行性 | feasibility | approved (rule 1) |
| 可行性保存 | feasibility preservation | approved |
| 可行性保存制約 | feasibility-preservation constraint | approved |
| 可行性上の要請 | feasibility requirement | overview |
| 必要応答ポテンシャル | potential for needed responses | approved |
| 内部モデル状態（空間） | internal-model state (space) | approved |
| 内部機構構造 | internal mechanism structure | approved |
| 個体ACS | individual ACS | approved |
| 組織自身のACS性 | the organization's own status as an ACS | approved |
| 記述理論／構造理論 | descriptive theory / structural theory | approved |
| 補助的詳細化 | auxiliary refinement | approved |
| 分岐を許す時間的自己同一性 | temporal self-identity that permits branching | approved |
| 因果的関係動学 | causal relational dynamics | overview |
| 構造的源泉 | structural source (of an action) | approved |
| 構成的必要性 | constitutive necessity | approved |
| 定義的必然性／条件付き必然性／数学的必要性 | definitional necessity / conditional necessity / mathematical necessity | approved |
| 構造・機能概念の三分類 | three classes of structural and functional concepts | approved |
| 分類A：構成的必要機能 | classification A: constitutively necessary function | approved |
| 分類B：標準機能形式 | classification B: standard functional form | approved |
| 分類C：記述・診断・比較概念 | classification C: concept for description, diagnosis and comparison | approved |
| 形式表現とACS内部認識の区別 | formal representation versus the ACS's internal recognition | approved |
| 必要環境空間 $E$ | required environment space | approved |
| 状態遷移写像 $f$ | state transition map | approved |
| 内部モデル構造 $M$ | internal model structure | approved |
| 内部モデル更新作用素 $\mathrm{Update}$ | internal-model update operator | approved |
| 外生背景成分／行動応答成分 | exogenous background component / action-response component | overview |
| 構造的環境結合条件 | structural environment coupling condition | approved |
| 情報統合機構 M1／適応的評価機構 M2／応答行動機構 M3 | information-integration mechanism M1 / adaptive-evaluation mechanism M2 / response-action mechanism M3 | approved |
| 局所保護応答 | local protective response | approved |
| 実効行動（解決） | effective action (resolution) | approved |
| 応答多様度 $\mu_{\mathrm{eff}}$ | response diversity | approved |
| 応答多様性縮退 | response-diversity degeneration | overview |
| 可行な応答の弱点 | weak point of a feasible response | approved |
| 頑健応答不能 | inability to respond robustly | approved |
| 応答不能環境集合 $N(x,u)$ | response-inability environment set | approved |
| 応答不能領域 $\mathcal N^{(1)}$ | response-inability region | approved |
| 頑健応答集合 $U^{\mathrm{rob}}(x)$ | robust response set | approved |
| $K$ 外部持続 | persistence outside $K$ | approved |
| 可行性核外部持続 | persistence outside the viability kernel | approved |
| 核維持応答集合 $U^{\mathrm{Viab}}(x)$ | kernel-maintaining response set | approved |
| 核維持応答の獲得 | acquisition of kernel-maintaining responses | approved |
| 三原理評価ベクトル $s_t$ | three-principle evaluation vector | approved |
| 参照スケール $\Pi_{\mathrm{ref}}$ | reference scale | approved |
| 有限窓 $\mathcal W_{T,t}$ | finite window | approved |
| 三原理関連構造的機能 | principle-related structural functions | approved |
| 情報取得・統合機能 | information acquisition and integration function | approved |
| 可行性感応評価機能 | feasibility-sensitive evaluation function | approved |
| 応答可能性評価・再構成機能 | evaluation and reconstruction function for the possibility of response | approved |
| 環境利用・外部結合評価機能 | evaluation function for environmental utilization and external coupling | approved |
| 応答形成・選択機能 | response formation and selection function | approved |
| 時間横断的情報保持・更新機能 | cross-time information retention and updating function | approved |
| 物理的感知・作用・基盤維持機能 | physical sensing, acting and substrate maintenance function | approved |
| 偏向性／偏向強度 | bias / bias strength | overview |
| 実効的発展自由度 $d_{\mathrm{eff}}$ | effective development freedom | overview |
| 予測精度係数／実効的時間地平 | prediction accuracy coefficient / effective time horizon | overview / approved |
| 健全度 | health (index) | overview |
| 機能的記憶 | functional memory | approved |
| 関係カテゴリー | relational category | approved |
| 許容外的作用 | admissible external action | overview |
| 構造的自己 | structural self | approved |
| 自己--環境境界 | self–environment boundary | approved |
| ACS集団 | group of ACSs | approved |
| 記述水準の規約 | convention on levels of description | approved |
| 抽象構造型／個体／時刻別の値 | abstract structure type / individual / time-indexed value | approved |
| 枠（$a\in\mathcal A_O$） | slot | approved |
| 不在状態 $\bot_a$ | absent state | approved |
| 原始的な機能 | primitive function | overview |
| 感知／識別／評価／行動 | sensing / discrimination / evaluation / action | approved |
| 基盤機能 | base function | approved |
| 基礎的な機能 | basic function | approved |
| 実効行動 | effective action | approved |
| 選択的待機 $u_\emptyset$ | selective waiting | approved |
| 外部による強制 | external forcing | approved |
| 作用差 | action difference | approved |
| 自律的機能過程／指向的過程 | autonomous functional process / directed process | approved |
| 7タプルの非冗長性 | non-redundancy of the 7-tuple | approved |
| 絶対的最小性 | absolute minimality (used only in the non-claim of `rem:tuple_nonredundancy`) | approved |
| 動的自己状態 $S_{\mathrm{dyn},t}$ | dynamic self-state | approved |
| 実現水準 | realization level | approved |
| 整形式実現指標 $\mathrm{WF}_{i,t}$ | well-formed realization indicator | approved |
| 時間的自己同一性の予備条件 | preliminary conditions of temporal self-identity | approved |
| 個体同一性関係の非分岐性 | non-branching of the individual-identity relation | approved |
| 境界帰属識別 $\xi_{\mathrm{bnd},t}$ | boundary-attribution discrimination | approved |
| 識別状態の全体の行 $\xi_t(\ast)$／トークンの行 $\xi_t(k)$ | overall row / token row (of the discrimination state) | approved |
| 崩壊状態指標 $\mathrm{CS}_{i,t}$／崩壊指標 $\mathrm{Col}_{i,t}$ | collapse-state indicator / collapse indicator | approved (see rule 4) |
| 機能的終端判定時刻域 $\mathbb T_{\mathrm{FT},i}$ | functional-termination judgment time domain | approved |
| 機能的終端状態指標 $\mathrm{FTS}_{i,t}$／機能的終端指標 $\mathrm{FT}_{i,t}$ | functional-termination state indicator / functional-termination indicator | approved |
| 機能的終端後 | after functional termination | approved |
| 全面的機能停止 | total functional stoppage | approved |
| 帰属の規定 | attribution provision | approved |
| 判定規則 | judgment rule | approved |
| 状態指標／履歴指標 | state indicator / history indicator | approved |
| 構造の破損・欠損 | structural damage or deficiency | approved |
| 部分的な機能不全・機能喪失 | partial malfunction or loss of function | approved |
| 構造崩壊（`subsubsec:collapse_sec2` の括弧書きの別名） | not rendered; "collapse" is used (rule 4) | approved |
| 必要環境要因／必要環境空間 | required environmental factor / required environment space | overview / approved |
| 要因別充足状態域 $D_\eta$ | factor-wise satisfiable-state domain | approved |
| 必要環境充足集合 $E_{\mathrm{req}}(x)$ | required-environment satisfaction set | approved |
| 必要環境整合性（CR-1） | required-environment consistency | approved |
| 存続必要性／欠損の実現可能性／欠損時の存続不能性 | necessity for persistence / realizability of deficiency / inability to persist under deficiency | approved |
| 共同充足可能性 | joint satisfiability | approved |
| 外部依存性 | external dependence | approved |
| 状態遷移列 | state-transition sequence | approved |
| 持続的な非充足／一時的な非充足 | lasting non-satisfaction / temporary non-satisfaction | approved |
| 必要環境利用機能 | required-environment utilization function | approved |
| 環境変化応答機能 | environment-change response function | approved |
| 要因分解の非一意性 | non-uniqueness of the factor decomposition | approved |
| 必要性の存立／同定可能性 | existence of necessity / identifiability | approved |
| 標準的粗分類候補 $\mathsf{Cls}_\eta$ | standard coarse classes (candidates) | approved |
| 行動応答成分の遷移写像 $g_O$／環境実現 | transition map of the action-response component / environment realization | approved |
| 可行行動対応 $A(x,e)$／可行行動集合 $A_t$ | feasible action correspondence / feasible action set at time $t$ | approved |
| 構造的応答ポテンシャルの集合 | set of structural response potentials | approved |
| 維持の局面における閉塞／回復の局面における閉塞 | blockage in the maintenance phase / blockage in the recovery phase | approved |
| 一段階可行環境対応 $\mathcal{E}_{\mathrm{viab}}^{(1)}(x)$ | one-step feasible environment correspondence | approved |
| 非退化性（状態遷移・可行行動集合・感知の水準） | non-degeneracy (state-transition / feasible-action-set / sensing level) | approved |
| 可行実現可能性 | feasible realizability | approved |
| 機能的非退化性 | functional non-degeneracy | approved |
| 可行性感応性 | feasibility sensitivity | approved |
| 内部環境推定 $\hat e_t$ | internal environment estimate | approved |
| 学習成分・作動成分 | learning component / working component | approved |
| 学習停止 | learning stop (on a sequence) | approved |
| Update整合列 | Update-consistent sequence | approved |
| 時間平均内部モデル変化量 | time-average internal-model change | approved |
| 認知的処理能力 | cognitive processing capability (not formalized in Phase 1) | approved |
| 原理応答項目 | principle response item | approved |
| 構造的同時性 | structural simultaneity | approved |
| 構造的評価機能 | structural evaluation function | approved |
| 内発的評価機能 | intrinsic evaluation function | approved |
| 臨界必要要因 | critical required factor | approved |
| 可行性余裕度 | feasibility margin | approved |
| 閾値割れ集合 | threshold-violation set | approved |
| 不足量ベクトル | deficiency vector | approved |
| 診断量 | diagnostic quantity | approved |
| 必要環境充足状態域 | required-environment-satisfying state domain | approved |
| 有限段頑健可行集合 | finite-step robust feasible set | approved |
| 頑健存続可能段数 | robust persistence horizon | approved |
| 全環境頑健核 | all-environment robust kernel | approved |
| 楽観核 | optimistic kernel | approved |
| 背景充足集合 | background-satisfaction set | approved |
| 応答込み頑健可行性核 | response-inclusive robust viability kernel | approved |
| 環境応答成分 | environment-response component | approved |
| 外部相互作用指標 | external interaction indicator | approved |
| 完全孤立状態／終端的完全孤立 | completely isolated state / terminal complete isolation | approved |
| 一段階臨界域 | one-step critical domain | approved |
| 一段階臨界必要要因集合 | one-step critical required factor set | approved |
| FR の定義域 $\mathcal D_{\mathrm{FR}}$ | domain of FR | approved |
| 局所 FR | local FR | approved |
| 可行性保持指示関数 | feasibility-retention indicator | approved |
| 臨界必要要因非充足閉塞（B1） | blockage with unsatisfied critical required factor (B1) | approved |
| 臨界必要要因充足下閉塞（B2） | blockage under satisfied critical required factors (B2) | approved |
| 閉塞の二分 | dichotomy of blockage | approved |
| 選択の責務 | responsibility of selection | approved |
| 可行性余裕度の改善可能性 | improvability of the feasibility margin | approved |
| 決定論的選択射影 | deterministic selection projection | approved |
| 同時刻作動の担体規約 | carrier convention for same-time operation | approved |
| 機構出力の個体への帰属 | attribution of mechanism outputs to an individual | approved |
| M1内部状態 $\mathsf S_{M1,t}$ | M1 internal state | approved |
| 識別状態 | discrimination state | approved |
| 内部対象トークン | internal-object token | approved |
| 動態重み | dynamics weight | approved |
| 状態推定誤差 $\varepsilon_{\mathrm{est},t}$ | state estimation error | approved |
| 予測整合性誤差 $\varepsilon_{\mathrm{pred},t}$ | prediction-consistency error | approved |
| 外部側の集合値予測 | set-valued prediction on the external side | approved |
| 内部の予測外／理論上の予測外 | internal deviation from prediction / theoretical deviation from prediction | approved |
| 目的対象性 | purpose-objecthood | approved |
| M2内部評価情報空間 | internal-evaluation information of M2 | approved |
| 要求の一覧／要請信号 | list of requests / request signal | approved |
| 要求×対象の評価 | request-by-object evaluation | approved |
| 未評価（低評価ではない） | unevaluated (not a low evaluation value) | approved |
| 急性脅威の検出 | acute-threat detection | approved |
| 構造的脆弱性 | structural vulnerability | approved |
| 機構層有効行動多様度 | mechanism-level effective action diversity | approved |
| 潜在的不安定性 | latent instability | approved |
| Priority 警告体系 | Priority warning system | approved |
| 存続基準の評価／目的基準の評価／判断 | evaluation by the persistence criterion / evaluation by the purpose criterion / judgment | approved |
| 根本要求（目的の） | fundamental request (of a purpose) | approved |
| 目的の状態の判断 | judgment of the state of a purpose | approved |
| 候補集合 | candidate set | approved |
| 候補の適合比較 | candidate fit comparison | approved |
| 動作モード（3A/3B/3C） | operating mode (3A / 3B / 3C) | approved |
| 応答様式 | response style | approved |
| 要請と応答の不一致 | mismatch between request and response | approved |
| 利用可能性 | availability (of information, signals, resources) | approved |
| 局所応答成分 | local-response component | approved |
| 発動の保存 | preservation of firing | approved |
| PSL感度制御 | PSL sensitivity control | approved |
| 目的の自己帰属性 | self-attribution of purposes | approved |
| 要求の関与 | involvement of a request | approved |
| 目的行動 | purposive action | approved |
| 目的を介さない自己生成の行動 | self-generated action not mediated by a purpose | approved |
| 目的に関わる作用差 | action difference relating to a purpose | approved |
| 一段の条件充足 | one-step condition satisfaction | approved |
| 理論上の達成時刻／内部の達成判断時刻 | theoretical attainment time / internal attainment-judgment time | approved |
| 実装要素全体 $\mathcal B_\Sigma$／感覚・効果・記憶の実装役割 | implementation elements / sensing, effector and memory implementation roles | approved |
| 統合的高速処理 | integrated high-speed processing | approved |
| 高速処理の三層横断性 | cross-level character of high-speed processing | approved |
| 自動性（Automaticity）と熟慮依存度 | Automaticity and dependence on deliberation | approved |
| 五機能的記憶集合 | five functional memory sets | approved |
| 機能軸 $F_t$ | functional axis | approved |
| 標準作動形式との合成対応 | composition correspondence with the standard operation form | approved |
| 一段遷移写像 $\Phi_{\mathrm{step}}$ | one-step transition map | approved |
| 標準作動記録 | standard operation record | approved |
| 保持記録の一致（分類C） | agreement of retained records (classification C) | approved |
| Updateの観測経由性 | observation factorization of Update | approved |
| 偏向性の帰属区分／帰属写像 | attribution division / attribution map | approved |
| 読み出しの型 | readout type | approved |
| 時刻依存量の整理用タプル $\mathrm{Desc}_t$ | organizing tuple of time-dependent quantities | approved |
| 外部対象集合 $\mathcal Y_{-i}$ | set of external objects | approved |
| 外部対象の三分類 | three-way classification of external objects | approved |
| 局所的サイズ指標 | local size indicator | approved |
| 有限観測窓 | finite observation window | approved |
| 単方向関係記述子 | unidirectional relation descriptor | approved |

## 3. Fixed phrases for non-claims

The manuscript uses fixed forms to separate what it does not claim from what it shows cannot be derived. The English keeps the same distinction.

| Japanese form | English form | When |
|---|---|---|
| 本論文は、……を一般的な帰結として置かない | This paper does not state … as a general consequence. | a non-claim without proof |
| ……は一般には導かれない | … does not follow in general. | only where the manuscript gives a counterexample or proof; cite it |
| 本定義は……を要件として含まない | The definition does not include … as a requirement. | scope of a definition |
| 本仮定は……を規定しない | The assumption does not stipulate … | scope of an assumption |
| Phase 1 の定義・命題から得られた一般的な帰結としては主張しない | … is not claimed as a general consequence of the definitions and propositions of Phase 1. | hypotheses |
| ……を……と同一視しない | … is not identified with … | distinctions between concepts |
| 未定義は偽ではない | undefined is not false | FR outside its domain, and similar |

## 4. Expressions not used

The manuscript's list of prohibited expressions carries over to English: *complete*, *definitive*, *conclusive*, *revolutionary*, *ultimate*, *absolute(ly)*, *necessarily* / *inevitable* (in the sense of 必然), *obvious(ly)* / *clearly* / *trivial(ly)*, *well known*, *always*, *in most cases*, *usually*, *extremely*, *very*, *for the first time*, *we achieved*. As in the manuscript, a word used only inside a negation or restriction may be kept after checking the context. *Deterministic* is allowed.
