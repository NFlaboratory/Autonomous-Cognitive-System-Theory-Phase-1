# -*- coding: utf-8 -*-
"""Preregistration P6 = E7 on MinACS: estimation error of the mechanism (degraded observation) and survival.
Written before any evaluation seed was run for E7."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAIR = {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}
DEG = ["D-en+1", "D-en+2", "D-tp+1", "D-blindcold", "D-stalefood"]
SPEC = {
    "id": "P6_e7_minacs_estimation_r1",
    "model": "e7_minacs",
    "purpose": "E7 (sec.9 prob:estimation_error): degrade the mechanism's observation I = P_sens(x,e) by a fixed map "
               "(true x, e, f and the judgment layer untouched) and compare survival with the undegraded mechanism; "
               "record the internal-vs-true feasibility sign mismatch, selection-responsibility antecedents (u not in "
               "A_t while A_t nonempty) and decision divergence.",
    "degradations": {"D-en+1": "energy read as en+1 (clipped)", "D-en+2": "energy read as en+2 (clipped)",
                     "D-tp+1": "body temperature read as tp+1 (clipped)",
                     "D-blindcold": "weather never sensed (belief stays at its initial value: not cold)",
                     "D-stalefood": "resource never sensed (belief stays at its initial value: present)"},
    "structural_notes": [
        "Energy-only degradations cannot produce a sign mismatch of Pi_eval in MinACS: Pi < 0 through energy only "
        "when en = 0, where the base functions are inactive and Pi_eval is undefined.",
        "Whenever a degraded trajectory differs from the baseline at all, its first differing step has a decision "
        "divergence > 0 (same state and M as the baseline at that step); 'shorter survival implies divergence' "
        "is therefore not registered as a hypothesis.",
    ],
    "tuning_history": "No degradation or metric was tuned.  One smoke test on tuning seed 1 (cold 3, regrow 3, no "
                      "gifts) was run before registration: T_col baseline 11; D-en+1 11, D-en+2 5, D-tp+1 11, "
                      "D-blindcold 11, D-stalefood 11.  Seeds 11-60 were not run for E7 before registration.",
    "sources": [os.path.join(ROOT, "MINACS", "minacs", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"cold_len": [2, 3, 4], "regrow_period": [2, 3, 5], "gift_events": [0, 3]},
    "conditions": ["D0"] + DEG,
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "hypotheses": [
        {"id": f"H{n + 1}", "kind": "paired", "metric": "T_col", "conditions": ["D0", d],
         "statement": f"観測の劣化（{d}）のない機構の崩壊到達時刻は、劣化した機構以上である。",
         "how_it_could_fail": "過大評価が遠回りや無駄な避難を減らし、または古い信念がたまたま有利に働けば、"
                              "劣化した機構の方が長く存続しうる。試運転では 5 条件中 4 条件で同値だった。",
         "rule": PAIR}
        for n, d in enumerate(DEG)
    ] + [
        {"id": "H6", "kind": "share", "predicate": "sign_mismatch_present", "conditions": ["D-tp+1"],
         "statement": "体温を過大評価する機構では、内部評価 Π_eval と真の Π の符号が食い違う時刻が、"
                      "25% 以上の単位で少なくとも 1 回生じる。",
         "how_it_could_fail": "食い違いは tp=0 の時刻にしか生じない。tp=0 は寒波の最中に外にいる場合だけで、"
                              "機構が避難していればほとんど生じない。",
         "rule": {"support_min": 0.25, "reject_max": 0.05}},
    ],
}
