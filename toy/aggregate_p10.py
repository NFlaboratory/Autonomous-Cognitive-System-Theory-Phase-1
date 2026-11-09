# -*- coding: utf-8 -*-
"""Descriptive aggregation of the P10 unit records (experiments A, B, C).  Counts and shares only.
python3 aggregate_p10.py -> outputs/p10_summary.md"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def load(sid):
    p = os.path.join(HERE, "results", sid + "_units.jsonl")
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def med(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def exact_block(name, U, T=60):
    ap = [u for u in U if u["condition"] == "aper"]
    pe = [u for u in U if u["condition"] == "periodic"]
    s = lambda k: sum(u.get(k, 0) for u in ap)
    L = [f"## {name}", "", f"非周期の背景（評価用 seed、{len(ap)} 単位、各 {T} ステップ、TIPA 機構）", ""]
    L.append(f"- 60 ステップ生存：{sum(1 for u in ap if u['T_col'] is None)} 単位")
    L.append("### A：前件の持続性")
    L.append(f"- 生存中の時刻 {s('alive_steps')} のうち、$e_t\\in E_{{\\mathrm{{req}}}}(x_t)$：{s('A_e_in_Ereq')}"
             f"（{s('A_e_in_Ereq') / max(1, s('alive_steps')):.3f}）")
    L.append(f"- 必要環境の連続充足長の最大値（単位ごと）：中央値 {med([u['A_longest_e_in_Ereq'] for u in ap])}、"
             f"最大 {max(u['A_longest_e_in_Ereq'] for u in ap)}")
    L.append(f"- 核の中で両前件が続いた最長の長さ（単位ごと）：中央値 {med([u['A_longest_both_antecedents_in_Viab'] for u in ap])}、"
             f"最大 {max(u['A_longest_both_antecedents_in_Viab'] for u in ap)}、{T} に達した単位 "
             f"{sum(1 for u in ap if u['A_longest_both_antecedents_in_Viab'] >= T)}")
    fe = [u["A_first_kernel_exit"] for u in ap if u["A_first_kernel_exit"] is not None]
    L.append(f"- 核から一度も出なかった単位：{sum(1 for u in ap if u['A_first_kernel_exit'] is None)}。"
             f"出た単位の初回離脱時刻の中央値 {med(fe)}")
    L.append("### B1：核維持応答の選択傾向（有限時間）")
    L.append(f"- 核の中の時刻 {s('B1_inV_steps')} のうち $u_t\\in U^{{\\mathrm{{Viab}}}}(x_t)$：{s('B1_inV_u_in_Uviab')}"
             f"（{s('B1_inV_u_in_Uviab') / max(1, s('B1_inV_steps')):.3f}）")
    L.append(f"- そのうち $e_t\\in E_{{\\mathrm{{req}}}}$ の時刻 {s('B1_inV_EreqTrue_steps')} では {s('B1_inV_EreqTrue_u_in_Uviab')}"
             f"（{s('B1_inV_EreqTrue_u_in_Uviab') / max(1, s('B1_inV_EreqTrue_steps')):.3f}）")
    L.append(f"- 核の外で $u_t\\in U^{{\\mathrm{{Viab}}}}(x_t)$ だった時刻 {s('B1_outV_u_in_Uviab')}（そのうち $E_{{\\mathrm{{req}}}}(x_t)=\\emptyset$ による空虚な所属 {s('B1_outV_vacuous')}）")
    L.append("### B2：獲得（周期背景、定義どおり）")
    c = Counter(u["B2_status"] for u in pe)
    L.append(f"- {len(pe)} 単位：獲得 {c['acquired']}、非獲得 {c['not_acquired']}、未判定 {c['undetermined']}")
    def cnt(f):
        return sum(1 for u in pe if f(u))
    L.append(f"  - 獲得：周期がすべて核の中 {cnt(lambda u: u['B2_status'] == 'acquired' and u['B2_cycle_all_in_Viab'])}、"
             f"そのうち周期で $e\\in E_{{\\mathrm{{req}}}}$ が続く {cnt(lambda u: u['B2_status'] == 'acquired' and u['B2_cycle_all_in_Viab'] and u['B2_cycle_all_e_in_Ereq'])}、"
             f"空虚な所属を含む周期 {cnt(lambda u: u['B2_status'] == 'acquired' and u['B2_cycle_vacuous_steps'] > 0)}")
    L.append(f"  - 非獲得：崩壊後の周期 {cnt(lambda u: u['B2_status'] == 'not_acquired' and u['B2_cycle_after_collapse'])}、"
             f"周期がすべて核の中（核には永久にとどまるが獲得はしない） {cnt(lambda u: u['B2_status'] == 'not_acquired' and u['B2_cycle_all_in_Viab'])}")
    L.append("### C：前件の分類と実際の結果（生存中の時刻）")
    L.append("| 分類 | 時刻 | そのうち核から出た | 推定の誤りがあった時刻 |")
    L.append("|---|---|---|---|")
    for k, lab in (("OK", "OK（両前件が真）"), ("C1", "C1 環境の前件だけ偽"), ("C2", "C2 選択の前件だけ偽"),
                   ("C3", "C3 両方偽"), ("C0", "C0 核の外")):
        L.append(f"| {lab} | {s('C_' + k)} | {s('C_' + k + '_leaveV') if k != 'C0' else '—'} | {s('C_' + k + '_est_err')} |")
    L.append("")
    L.append("出来事の帰属（出来事の前に最後に核にいた時刻の分類。「+est」はその時刻に推定の誤りがあった）")
    for ev, lab in (("blk", "閉塞"), ("leaveK", "K の外への移行"), ("col", "崩壊")):
        tags = Counter()
        for u in ap:
            for k, v in u.items():
                if k.startswith(f"C_event_{ev}_lastInViab_"):
                    tags[k[len(f"C_event_{ev}_lastInViab_"):]] += v
        L.append(f"- {lab}：" + "、".join(f"{t} {n}" for t, n in sorted(tags.items())))
    return L


def v2_block(U):
    L = ["## v2 トイ（個体 i、証明書による判定）", ""]
    for w in ("alone", "default"):
        ap = [u for u in U if u["condition"] == w]
        if not ap:
            continue
        s = lambda k: sum(u.get(k, 0) for u in ap)
        L.append(f"### {w}（{len(ap)} 単位、各 300 ステップ）")
        L.append(f"- 300 ステップ生存：{sum(1 for u in ap if u['T_col'] is None)} 単位")
        L.append(f"- A：生存中の時刻 {s('alive_steps')} のうち $e\\in E_{{\\mathrm{{req}}}}$ {s('A_e_in_Ereq')}"
                 f"（{s('A_e_in_Ereq') / max(1, s('alive_steps')):.3f}）、証明書で核の中 {s('A_in_Viab_cert')}、未決定 {s('A_undetermined')}。"
                 f"両前件が続いた最長の長さ：中央値 {med([u['A_longest_both_antecedents_cert'] for u in ap])}、最大 {max(u['A_longest_both_antecedents_cert'] for u in ap)}")
        L.append(f"- B1（下限）：核の中の時刻 {s('B1_inV_steps')} のうち $u\\in U^{{\\mathrm{{Viab}}}}_{{\\mathrm{{cert}}}}$ {s('B1_inV_u_in_Uviab_cert')}"
                 f"（{s('B1_inV_u_in_Uviab_cert') / max(1, s('B1_inV_steps')):.3f}）。$e\\in E_{{\\mathrm{{req}}}}$ の時刻では {s('B1_inV_EreqTrue_u_in_Uviab_cert')} / {s('B1_inV_EreqTrue_steps')}")
        L.append("- C（C2・C3 は上限）：" + "、".join(f"{k} {s('C_' + k)}（核から出た {s('C_' + k + '_leaveV')}）"
                                               for k in ("OK", "C1", "C2", "C3")) + f"、C0 {s('C_C0')}、C0?（未決定） {s('C_C0?')}")
        for ev, lab in (("blk", "閉塞"), ("leaveK", "K の外への移行"), ("col", "崩壊")):
            tags = Counter()
            for u in ap:
                for k, v in u.items():
                    if k.startswith(f"C_event_{ev}_lastInViab_"):
                        tags[k[len(f"C_event_{ev}_lastInViab_"):]] += v
            L.append(f"  - {lab}の帰属：" + "、".join(f"{t} {n}" for t, n in sorted(tags.items())))
        L.append("")
    return L


def main():
    ids = ("P10_abc_minacs_r1", "P10_abc_furnace_r1", "P10_abc_v2_r3")
    missing = [sid for sid in ids if not os.path.exists(os.path.join(HERE, "results", sid + "_units.jsonl"))]
    if missing:
        raise SystemExit("Raw unit records not found: " + ", ".join(f"results/{sid}_units.jsonl" for sid in missing)
                         + ". They are archived separately (see results/UNITS_SHA256.md). "
                           "outputs/p10_summary.md was not changed.")
    L = ["# P10：実験 A・B・C の記述集計", "",
         "件数と割合だけを示す。分類は命題の前件のどれが偽だったかによる論理的な帰属であり、因果の主張ではない。"
         "推定の誤りは同じ時刻に起きていたことを記録しただけで、原因とはみなさない。", ""]
    L += exact_block("MinACS", load("P10_abc_minacs_r1")) + [""]
    L += exact_block("炉番", load("P10_abc_furnace_r1")) + [""]
    v2 = load("P10_abc_v2_r3")
    if v2:
        L += v2_block(v2)
    with open(os.path.join(HERE, "outputs", "p10_summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
