# -*- coding: utf-8 -*-
"""Preregistration P7 = E8 part 1: E1 repeated on the second domain (furnace keeper) with the common judgment
layer.  Written before any evaluation seed was run on this domain."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAIR = {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}
POL = ["P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed", "P-wait"]
TUNING = ("The domain (E8/domains/furnace/model.py) was written first; its exhaustive checks passed without change. "
          "Smoke 1 (tuning seeds 1-3, hot_len 3, deliv_period 3, draught 1): every policy collapsed by t=18; the "
          "sweep of hot_len was then moved to {4,5,6}.  The mechanism's fit rule was changed once after smoke 1 "
          "(ties between gather and wait chose wait): a purpose-achievement component was added.  Smoke 2 with the "
          "final code (tuning seeds 1-10 x the 18 sweep points, 180 units) gave 60-step survivors: P-Viab-first 35, "
          "P-Viab-last 27, P-A-first 0, P-A-greedy 51, P-mech 50, P-greedy 8, P-fixed 0, P-wait 0; ablations: full "
          "50, -integ 51, -feas 0, -resp 22, -envuse 0, -select 0, -update 51, -phys 50.  Seeds 11-60 were not run "
          "on this domain before registration.")
SPEC = {
    "id": "P7_e8_furnace_policies_r1",
    "model": "e8_e1_furnace",
    "purpose": "E8 (Q7): repeat the main part of E1 (P3, MinACS) on a structurally different domain: no movement, "
               "two-sided danger (freezing and overheating), a sink-type required factor (flue) that the "
               "individual's own action can destroy.  The judgment layer is the common one (E8/acsjudge), verified "
               "to reproduce the MinACS analysis exactly.",
    "tuning_history": TUNING,
    "non_realisability_note": "P-Viab-* and P-A-* read the true Viab_f(K), A(x,e) and e; reference policies only.",
    "sources": [os.path.join(ROOT, "E8", "acsjudge", "*.py"), os.path.join(ROOT, "E8", "domains", "*.py"),
                os.path.join(ROOT, "E8", "domains", "furnace", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"hot_len": [4, 5, 6], "deliv_period": [2, 3, 4], "draught": [1, 2]},
    "conditions": POL,
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "hypotheses": [
        {"id": "H1", "kind": "share", "predicate": "kernel_exit_only_outside_Ereq", "conditions": POL,
         "statement": "（回帰検査）u_t∈U^Viab(x_t) を選んだ時刻に核から出るのは、e_t∉E_req(x_t) の時刻に限られる。",
         "how_it_could_fail": "e_t∈E_req で u_t∈U^Viab なのに核から出る例が一つでもあれば不成立。命題に反するので、"
                              "起こるとすれば共通判定層か領域の実装の誤りに限られる。回帰検査として登録する。",
         "rule": {"support_min": 1.0, "reject_max": 0.999}},
        {"id": "H2", "kind": "paired", "metric": "T_col", "conditions": ["P-Viab-first", "P-A-greedy"],
         "statement": "核維持応答を選ぶ方策の崩壊到達時刻は、一段先だけを見る方策（後続の tp を 3 に近づけ、次に燃料最大）以上である。",
         "how_it_could_fail": "U^Viab は実現した e を見ない。煤で煙道が塞がる時刻（e∉E_req）に U^Viab が待機を含めば凍えうる。"
                              "試運転（調整用 seed）では P-A-greedy の生存 51 に対し P-Viab-first は 35 だった。",
         "rule": PAIR},
        {"id": "H3", "kind": "paired", "metric": "T_col", "conditions": ["P-Viab-first", "P-mech"],
         "statement": "核維持応答を選ぶ方策の崩壊到達時刻は、TIPA 機構以上である。",
         "how_it_could_fail": "機構は燃料を早めに集める目的をもつが、P-Viab-first は U の先頭（待機）を優先する。"
                              "試運転では機構の生存 50 に対し P-Viab-first は 35 だった。",
         "rule": PAIR},
        {"id": "H4", "kind": "paired", "metric": "T_col", "conditions": ["P-mech", "P-greedy"],
         "statement": "TIPA 機構の崩壊到達時刻は、記憶をもたない観測反射以上である。",
         "how_it_could_fail": "反射は煙道の状態を推定しないが、高温で開ける規則をもつ。背景によっては反射が長く存続しうる。",
         "rule": PAIR},
        {"id": "H5a", "kind": "paired", "metric": "T_col", "conditions": ["P-mech", "P-fixed"],
         "statement": "TIPA 機構の崩壊到達時刻は、固定行動列以上である。",
         "how_it_could_fail": "固定行動列の燃焼・開放の時刻が背景と合えば、機構より長く存続しうる。",
         "rule": PAIR},
        {"id": "H5b", "kind": "paired", "metric": "T_col", "conditions": ["P-mech", "P-wait"],
         "statement": "TIPA 機構の崩壊到達時刻は、常に待機する方策以上である。",
         "how_it_could_fail": "待機は燃焼による亀裂を起こさない。暑い期間が長い背景では、機構の燃焼が過熱を招きうる。",
         "rule": PAIR},
    ],
}
