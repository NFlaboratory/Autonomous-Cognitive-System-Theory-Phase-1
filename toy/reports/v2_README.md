# ACS トイモデル（v2：自律作動と状態遷移の実験系）

## 1. 目的

形式的に形付けられた個体が、環境の中で内部モデルを更新しながら自律的に振る舞うか。
その結果として、可行性の維持、閉塞、回復を経験し、最後には崩壊に至るか。
これを論文 §2〜§8 の構造的形式をすべて実装した上で、実験として確かめられるようにする。

本トイは論文の主張を証明するものではない。論文の定義・命題に従って判定した量を、
具体的な一つの実現について計算し、時系列として観察できるようにするものである。

## 2. 実行

```
python3 run.py [シナリオ] [key=value ...] [--out DIR] [--no-checks]
```

- シナリオ：`default`・`harsh`・`alone`・`no_drone`・`cooperative`・`explorer`・`rocky`・`long`（`acs_toy/config.py` の `SCENARIOS`）。
- `key=value` は `Config` の任意の欄を上書きする（例：`steps=400`、`seed=3`、`snaps="((50,30),)"`、`bias_j="(4,2)"`）。
- 出力（既定 `out/<シナリオ>`）：
  - `trace_<個体>.csv`：各時刻の判定量（§2〜§7、約 110 列）
  - `org.csv`：§8 組織水準
  - `relations.csv`：§6 関係記述子と双方向合成
  - `events.md`：判定量の変化の時系列
  - `summary.json`：経路量と集計
  - `checks.txt`：構成要件・仮定・命題の検査
  - `viewer.html`：地図、各時刻の判定量、状態帯、出来事を一つのページで見る表示
- 所要時間（実測、1 シナリオ 300 ステップ）：シミュレーションと判定で約 10〜20 秒、検査で約 60 秒。

依存は Python 3 の標準ライブラリだけである。

## 3. 構成

| ファイル | 内容 |
|---|---|
| `acs_toy/body.py` | 7 タプルの $X, U, f, \Pi$ と必要環境要因 $E=\{\eta_{\mathrm{heat}},\eta_{\mathrm{food}}\}$、$f=\oplus(f_{\mathrm{auto}},f_{\mathrm{dir}})$、活動・基盤機能・WF・(SC-1) の判定規則 |
| `acs_toy/world.py` | $E_{\mathrm{ext}}=E^{\mathrm{bg}}\times O$、外生背景列 $(b_t)$、行動応答成分 $o_t$ と $g_O$、他個体 $\Sigma_j$、非 ACS 行為主体（救助ドローン）、共同の遷移 |
| `acs_toy/mind.py` | TIPA（M1・M2・M3）・PSL・ISL による $P_{\mathrm{sens}},P_{\mathrm{disc}},P_{\mathrm{val}},P_{\mathrm{act}}$、Update（観測経由） |
| `acs_toy/org.py` | §8 の組織（共有貯蔵庫の台帳を運用する組織水準の記述） |
| `acs_toy/sim.py` | 標準作動記録の生成、許容外的作用 $\Upsilon_{\mathrm{adm}}$ |
| `acs_toy/judge.py` | 判定層：論文の定義を記録に適用する |
| `acs_toy/checks.py` | 構成要件 CR-1・CR-2、§2 仮定の証拠、命題の再検査 |
| `acs_toy/events.py`・`viewer.py` | 記述者の読解補助（新しい定義を導入しない） |

**分離規則。** 個体の機構（`mind.py`）は、真の $\Pi$、$A_t$、$\mathrm{Crit}^{(1)}$、$\mu_{\mathrm{eff}}$、$\mathrm{Viab}_f(K)$、$Q$ などを一切参照しない。
機構が使うのは $P_{\mathrm{sens}}(x,e)$ が返す情報 $I$ と内部モデル状態 $M$ だけである。
真の量は判定層だけが計算する（§1 の形式表現と ACS 内部認識の区別）。

## 4. 世界と個体（トイ規約）

7×7 の格子。避難所（扉つき）、共有貯蔵庫、資源 4 か所（再生する）、落石セル 4 か所。
外生背景 $b_t=(T,\text{落石},\text{前兆},\text{風},\text{再生})$ は決定論的な列で、どの行動にも応答しない。
$T$ は昼（0）・夜（1）・厳寒（2）で、厳寒期間は `snaps` で与える。

- $X$：位置、energy（0〜20）、integ（0〜10）、temp（0〜8）、健全度 hpsl・hsens・heff・hmem（0〜3）、carry、starve、alert、beacon、last_u。
- $\Pi(x)=\min_k(x_k-\theta_k)$。$\theta$：energy 3、integ 3、temp 3、hpsl 1。他の座標には拘束しない値を置く。
- $U$：待機 $u_\emptyset$、移動 4 方向、eat、collect、give、open_door、deposit、repair、vigil、signal。
- $E$：$\eta_{\mathrm{heat}}$（$T\le1$、または閉じた避難所の中）、$\eta_{\mathrm{food}}$（現セルか隣接セルに資源、または贈与）。
- 他個体 $\Sigma_j$ は $\Sigma_i$ と同じ実装の別インスタンスで、偏向（初期の評価重み）だけが異なる。
- 救助の担い手は二つある。$\Sigma_j$ は協力関係の帰結として give を選ぶことがある。救助ドローン（非 ACS の行為主体）は固定の救助規則で動き、表示エネルギーの低い個体に届ける。
- 実現した救助は $e_t$ の贈与成分を通じてだけ効く。許容外的作用 $\upsilon\in\Upsilon_{\mathrm{adm}}$（inject・mend・carry_to_shelter）は、判定（Recover、(SC-2)、(FT-2)）の中でだけ用いる。

## 5. 判定層が計算するもの

計算の種類を三つに分けて示す。

- 厳密：有限集合上で定義どおりに計算する。$E_{\mathrm{ext}}$ 上の全称・存在量化は、$f$ と各 $\eta$ が $e$ を局所像 $\lambda(x,e)$ を通じてだけ読むことを用い、$\lambda$ の実現可能な像を列挙して評価する。
- 証明書：成立を示す証拠が見つかれば確定し、見つからなければ「未決定」と書く。
- 規則：論文が対象系ごとの判定規則や Phase 1.α に委ねている部分を、判定に先立ってトイ側で固定した規則。

| 論文 | 列 | 種類 |
|---|---|---|
| §2 $\Pi$、$K$、$A_t$、閉塞、一段階の量 | `Pi` `inK` `A` `blk` | 厳密 |
| §2 WF、(SC-1)、(FT-1)、活動 | `WF` `SC1` `FT1` `act_*` | 規則（integ>0 等） |
| §2 CS（(SC-1)+(SC-2)）、Col、FTS、FT、$\mathbb{T}_{\mathrm{FT}}$ | `CS` `Col` `FTS` `FT` | 規則（(SC-2)・(FT-2) は `checks.txt` の GRID 検査で裏づけ） |
| §3 $\mathbb{T}_{\mathrm{P}}$、SM、EU、FR、$\mathrm{Crit}^{(1)}$、$\mathcal{D}_{\mathrm{FR}}$、(B1)/(B2) | `T_P` `SM` `EU` `FR` `Crit` `D_FR` `B1` `B2` | 厳密 |
| §3 $\mu_{\mathrm{eff}}$、応答の弱点、$U^{\mathrm{rob}}$、EC | `mu_eff` `weak_point` `U_rob_n` `EC` | 厳密 |
| §3 $V^-$、$d^-$、$\Pi$ の最小座標、$\pi_E$ 感応 | `V_minus` `d_minus` `argmin_Pi` `piE_sensitive` | 厳密 |
| §3 $\chi_{\mathrm{EI}}$、終端的完全孤立 | `chi_EI`、`summary.json` | 規則（境界横断作用の判定）。完全孤立は記録の終わりまでの観察 |
| §3 $\mathrm{Viab}^{(1)}$、$\mathrm{Hor}_f$（上限 `hor_cap`） | `in_Viab1` `Hor` | 厳密（`hor_every` ごと） |
| §3 $\mathrm{Viab}_f(K)$ | `Viab_core` | 証明書：「in」は $x$ を含む $E_{\mathrm{req}}$ 不変集合を構成できた場合、「not_in」は $x\notin K_{\mathrm{req}}$ か $\mathrm{Hor}_f$ が有限の場合（命題 prop:viab_stage_core） |
| §3 $s_{\mathrm{SM}}$、T-STAB（T1〜T4） | `s_SM` `TSTAB` | 厳密（パラメータは `tstab`） |
| §4 Priority、$\Pi_{\mathrm{eval}}$、C1・C2（5 類型）・C3、要請、モード、スタイル、目的、状態、自動化、PSL-4 | `P` `C1` `C2` `C3` `sig` `mode` `style` `Pur` `stat` `fast` `r_local` | 機構の出力（WF=1 の時刻だけ帰属） |
| §4 要請関与と行為区分 | `action_class` | 反実仮想の M3 呼び出し |
| §4 $\varepsilon$、予測外れ（内部・理論） | `eps_est` `pred_internal_miss` `pred_theory_miss` | 厳密 |
| §4 機能軸 $F_t$ | `F_*` | 規則 |
| §5 $\delta^M$、学習成分の変化、記録一致、偏向 $\beta$、$d_{\mathrm{eff}}$、$\pi_\tau$、$\hat\tau$、健全度、五記憶集合 | `delta_M` `delta_L` `rec_agree` `beta_*` `d_eff` `pi_tau` `tau_hat` `h_*` `T_*` | $\delta$ は正規化距離（直径 1）で厳密。$d_{\mathrm{eff}}$ と $\beta$ の基準は規則 |
| §6 関係記述子 6 成分、$Q$、双方向合成 | `relations.csv` | 規則（カテゴリー成立条件は Phase 1.α のため記録規則として固定） |
| §7 状態帯 Z0〜Z5、Recover、$I_{\mathrm{ACS}}$、$T_{\mathrm{blk}}$、$T_{\mathrm{col}}$ | `zones` `Recover`、`summary.json` | 帯は規則（分割ではない）。Recover は $\upsilon$ を加えた継続を `recover_horizon` まで前向きに計算 |
| §8 $n_{\mathrm{org}}$、組織 ACS、$K_{\mathrm{org}}$、$A_t(\Sigma_{\mathrm{org}})$、組織水準の閉塞 | `org.csv` | 厳密（組織の 3 行動について共同遷移を計算） |

計算しないもの：$\mathrm{Viab}^{\mathrm{resp}}_f(K)$（応答込みの核は機構の内部状態を含む積空間の最大不変集合で、このトイの規模では計算しきれない）、組織水準の EU・FR（組織の必要環境要因をこのトイでは定めていない）。

## 6. 検査（`checks.txt`）

- WITNESS：存在の主張に対する具体例（CR-1a(i)、CR-1b、CR-1c、CR-2b(i)〜(iv)、非退化性、可行実現可能性）。
- GRID：全称の主張について、一歩ごとの不等式を有限の格子で検査する。
  - CR-1a(ii)：$\eta_{\mathrm{heat}}=0$ の持続では temp が単調に下がり、temp≤1 で integ が毎時刻減る。$\eta_{\mathrm{food}}=0$ の持続では energy+eat_gain·carry が毎時刻 1 以上減る。
  - (SC-2)：integ=0 はすべての $u,e$ と $\Upsilon_{\mathrm{adm}}$ のもとで不変である。
  - (FT-2)：hpsl=0 から抜けられない。
  - 格子外の状態に対しては、不等式が読む欄以外を $f$ が読まないこと（コードの目視）を根拠にしている。格子検査そのものは証明ではない。
- RECORD：当該実行の記録上で論文の命題を再検査する（閉塞の二分、prop:eu_blockage、prop:fr_mu_eff、選択の責務、prop:blockage_viability_kernel、prop:viab_stage_core、(C-2) 吸収性、終端の順序、prop:recover_excludes_termination、T-STAB からの含意、組織水準の閉塞の特徴づけ）。
  - あわせて、$g_O$ と共同シミュレーションの一致、$g_O$ が個体の $M$ に依存しないこと、観測による因数分解、M2 が M3 を参照しないことを確かめる。
  - ここでの不一致は実装の誤りを示すものであり、論文への反例ではない。

## 7. トイ規約の一覧（論文の定義ではない選択）

- 世界の幾何、数値（代謝 1、移動 1、eat +5、贈与 3、再生周期 3、厳寒の時刻）。
- $\oplus$ と基準元 $o^\ast$。
- 活動・基盤機能・WF・(SC-1)・(FT-2) の判定規則：integ>0 で WF=1、integ=0 で (SC-1)、hpsl=0 または integ=0 での (FT-1) は回復不能。
- 機構の中身：M1 の 8 軸識別、M2 の閾値、M3 の価値関数と先読み深さ（3A：2、3B：3、3C：1）、目的形成と状態判定の規則、ルーティンの学習則、PSL-4 の保護応答（落石の前兆があるセルから出る）、ビーコンは通常の感知範囲より 3 だけ遠くまで知覚できる。
- 機構内部の信念：資源は再生する、近くの相手に合図すると助けが来る、エネルギー 0 では何もできない。これらは機構の内部モデルであり、判定層は使わない。
- 状態帯の規則（Z1：健全度 2 または energy≤6、integ≤6、temp≤4。Z2：基礎的な機能の一部停止または健全度≤1。Z3：(FT-1)。Z4：閉塞。Z5：Col=1）。
- $\Upsilon_{\mathrm{adm}}$ の作用規則と Recover の判定規則（`recover_horizon` 以内に、同一個体のまま $K$ に入り基盤機能が作動する）。
- §6 の記録規則（関係の継続はトークン同定、カテゴリーは give・同時摂食・利用から割り当てる）、$Q=0.5Q_{\mathrm{res}}+0.5Q_{\mathrm{via}}$。
- 扉の操作は 1 時刻に 1 回だけ効く（複数個体が同時に押しても 1 回の切り替え）。

## 8. 非主張

- 本トイの挙動は、論文の命題の証明でも反例でもない。
- 特定のシナリオで崩壊に至ったこと、または至らなかったことから、一般的な傾向を導かない。
- 機構の性能（どれだけ長く存続するか）は、トイ規約の数値に強く依存する。実際に、数値の小さな変更で崩壊時刻は大きく変わった。
- $x_t\in\mathrm{Viab}_f(K)$ の時刻があっても、その後に崩壊しうる。核は $E_{\mathrm{req}}$ 上の頑健性であり、実現した $e_t$ が $E_{\mathrm{req}}(x_t)$ の外に出ること（厳寒で避難所の外にいる等）や、機構が核にとどまる応答を選ばないことを排除しない。
