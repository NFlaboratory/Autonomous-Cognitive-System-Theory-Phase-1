# -*- coding: utf-8 -*-
"""Preregistration P3 = E1 on MinACS: trajectory-level comparison of policies.  Written before any
evaluation seed was run with these policies."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAIR = {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}
SPEC = {
    "id": "P3_e1_minacs_policies_r1",
    "model": "e1_minacs",
    "purpose": "E1: compare the kernel-maintaining oracle (u in U^Viab), one-step oracles (u in A_t), the TIPA "
               "mechanism, an observation-only reflex, a fixed action sequence and constant waiting on held-out "
               "backgrounds; observe what happens where prop:kernel_maintenance does not apply (e_t not in E_req).",
    "tuning_history": "No policy was tuned.  The policies were written before any run; one smoke test on tuning "
                      "seed 1 (cold_len 3, regrow 3, no gifts) was run before registration and showed: P-greedy "
                      "survived 60 steps, P-Viab-first/last and P-mech collapsed at 11, P-A-*/P-wait at 5, "
                      "P-fixed at 8.  Seeds 11-60 were not run before registration.  The MinACS model and the "
                      "mechanism are those of E6 (tuned on the three named backgrounds, see E6 report).",
    "non_realisability_note": "P-Viab-* and P-A-* read the true Viab_f(K), A(x,e) and e; they are reference "
                              "policies, not mechanisms an ACS individual could implement (sec.1 distinction).",
    "sources": [os.path.join(ROOT, "MINACS", "minacs", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"cold_len": [2, 3, 4], "regrow_period": [2, 3, 5], "gift_events": [0, 3]},
    "conditions": ["P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed",
                   "P-wait"],
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "hypotheses": [
        {"id": "H1", "kind": "share", "predicate": "kernel_exit_only_outside_Ereq",
         "conditions": ["P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed",
                        "P-wait"],
         "statement": "（回帰検査）u_t∈U^Viab(x_t) を選んだ時刻に核から出るのは、e_t∉E_req(x_t) の時刻に限られる"
                      "（prop:kernel_maintenance の一段の形）。",
         "how_it_could_fail": "e_t∈E_req で u_t∈U^Viab なのに核から出る例が一つでもあれば不成立。命題に反するので、"
                              "起こるとすれば実装の誤りに限られる。これは仮説ではなく回帰検査として登録する。",
         "rule": {"support_min": 1.0, "reject_max": 0.999}},
        {"id": "H2", "kind": "paired", "metric": "T_col", "conditions": ["P-Viab-first", "P-A-greedy"],
         "statement": "核維持応答を選ぶ方策の崩壊到達時刻は、一段先だけを見る方策（後続の energy 最大）以上である。",
         "how_it_could_fail": "U^Viab は x だけで決まり、実現した e を見ない。資源セルで寒波（e∉E_req）のとき "
                              "U^Viab が留まる行動を含めば P-Viab は寒さで崩壊し、e を見る P-A-greedy は避けうる。",
         "rule": PAIR},
        {"id": "H3", "kind": "paired", "metric": "T_col", "conditions": ["P-Viab-first", "P-mech"],
         "statement": "核維持応答を選ぶ方策の崩壊到達時刻は、TIPA 機構以上である。",
         "how_it_could_fail": "機構は観測した寒さに反応して避難するが、P-Viab は E_req 外の寒さを考慮しない。",
         "rule": PAIR},
        {"id": "H4", "kind": "paired", "metric": "T_col", "conditions": ["P-mech", "P-greedy"],
         "statement": "TIPA 機構の崩壊到達時刻は、記憶をもたない観測反射以上である。",
         "how_it_could_fail": "登録前の試運転（調整用 seed 1）で、P-greedy は生存し P-mech は崩壊した。",
         "rule": PAIR},
        {"id": "H5a", "kind": "paired", "metric": "T_col", "conditions": ["P-mech", "P-fixed"],
         "statement": "TIPA 機構の崩壊到達時刻は、固定行動列以上である。",
         "how_it_could_fail": "固定行動列が偶然に食べる・避難する時刻と背景が合えば、機構より長く存続しうる。",
         "rule": PAIR},
        {"id": "H5b", "kind": "paired", "metric": "T_col", "conditions": ["P-mech", "P-wait"],
         "statement": "TIPA 機構の崩壊到達時刻は、常に待機する方策以上である。",
         "how_it_could_fail": "待機は移動の費用を払わない。贈与が多い背景では待機の方が長く存続しうる。",
         "rule": PAIR},
    ],
}
