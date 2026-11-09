# -*- coding: utf-8 -*-
"""Preregistration P9 = E1 on the v2 toy: trajectory-level comparison of policies for individual i.
Written before any evaluation seed was run with these policies."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAIR = {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}
POL = ["P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed", "P-wait"]
WORLDS = ["alone", "default"]
COND = [f"{w}:{p}" for w in WORLDS for p in POL]
SMOKE = ("tuning seed 1, eat_gain 5, regen_period 3, snap_jitter 10, 300 steps; T_col of i: "
         "alone: P-Viab-first 166, P-Viab-last 166, P-A-first 25, P-A-greedy 25, P-mech 85, P-greedy 258, P-fixed 24, "
         "P-wait 25; default: P-Viab-first 166, P-Viab-last 166, P-A-first 35, P-A-greedy 35, P-mech 168, "
         "P-greedy 262, P-fixed 40, P-wait 35")


def paired(hid, world, a, b, stmt, fail):
    return {"id": hid, "kind": "paired", "metric": "T_col", "conditions": [f"{world}:{a}", f"{world}:{b}"],
            "statement": f"（{world}）" + stmt, "how_it_could_fail": fail, "rule": PAIR}


HYP = [
    {"id": "H1a", "kind": "share", "predicate": "cert_exit_only_outside_Ereq",
     "conditions": [c for c in COND if "Viab" in c],
     "statement": "（回帰検査）証明書つきの核維持応答 u∈U^Viab_cert(x_t) を選んで証明書の集合から出るのは、"
                  "e_t∉E_req(x_t) の時刻に限られる（prop:kernel_maintenance の一段の形）。",
     "how_it_could_fail": "判定層の頑健後続の列挙（局所像 lam の像）が世界の遷移と食い違えば、e∈E_req で集合から出る例が生じる。"
                          "命題に反するので、起こるとすれば実装の誤りに限られる。回帰検査として登録する。",
     "rule": {"support_min": 1.0, "reject_max": 0.999}},
    {"id": "H1b", "kind": "share", "predicate": "f_table_consistent",
     "conditions": [c for c in COND if "Viab" in c],
     "statement": "（回帰検査）判定層の後続表 f(x,u,lam|rel) は、世界で実現した後続と一致する（局所像による列挙の正確さ）。",
     "how_it_could_fail": "body.relevant が f の読む lam の成分を取りこぼしていれば不一致が生じる。回帰検査として登録する。",
     "rule": {"support_min": 1.0, "reject_max": 0.999}},
]
for w in WORLDS:
    HYP += [
        paired(f"H2-{w}", w, "P-Viab-first", "P-A-greedy",
               "核維持応答を選ぶ方策の崩壊到達時刻は、一段先だけを見る方策（後続の energy・temp・integ 最大）以上である。",
               "U^Viab_cert は実現した e を見ない。厳寒（e∉E_req）で U^Viab_cert が屋外の行動を含めば凍えうる。"
               "試運転では P-Viab-first 166 に対し P-A-greedy は 25（alone）・35（default）だった。"),
        paired(f"H3-{w}", w, "P-Viab-first", "P-mech",
               "核維持応答を選ぶ方策の崩壊到達時刻は、TIPA 機構以上である。",
               "機構は観測した寒さ・欠乏に先読みで応答するが、P-Viab は E_req 外の環境を考慮しない。"
               "試運転（default）では機構 168 が P-Viab-first 166 を上回った。"),
        paired(f"H4-{w}", w, "P-mech", "P-greedy",
               "TIPA 機構の崩壊到達時刻は、記憶をもたない観測反射以上である。",
               "試運転で観測反射は 258（alone）・262（default）で、機構（85・168）を上回った。"),
        paired(f"H5a-{w}", w, "P-mech", "P-fixed", "TIPA 機構の崩壊到達時刻は、固定行動列以上である。",
               "固定行動列が偶然に食べる・避難する時刻と背景が合えば、機構より長く存続しうる。"),
        paired(f"H5b-{w}", w, "P-mech", "P-wait", "TIPA 機構の崩壊到達時刻は、常に待機する方策以上である。",
               "待機は移動の費用を払わない。default では相手・ドローン・組織からの贈与で待機の方が長く存続しうる。"),
    ]
SPEC = {
    "id": "P9_e1_v2_policies_r1",
    "model": "e1_v2",
    "purpose": "E1 on the v2 toy: impose one policy on individual i (partner j, drone and organisation keep their "
               "rules) and compare collapse-reaching times on held-out seeds, in a world without others ('alone') "
               "and in the default world.  Kernel-maintaining responses use the judgment layer's certificates "
               "(U^Viab_cert, a subset of U^Viab), since Viab_f(K) is decided only by certificates in v2.",
    "undetermined_rule": "fixed before any run: if the oracle answers 'not_in' or 'undetermined', choose from A(x,e) "
                         "in the same order; if A is empty, wait (e4/policies_v2.py docstring).",
    "non_realisability_note": "P-Viab-*, P-A-* read the true lam, A(x,e) and the certificates; reference policies only.",
    "tuning_history": "No policy was tuned.  The policies were written before any run; one smoke test of all 16 "
                      "conditions (" + SMOKE + ") was run before registration.  Seeds 11-60 were not run with these "
                      "policies before registration.  The v2 mechanism was tuned earlier on seed 1 (v2 report).",
    "metric_note": "T_col = first step with integ = 0 for i; censored (None = +inf) if not reached within 300 steps.",
    "sources": [os.path.join(ROOT, "TOY2", "acs_toy", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"eat_gain": [4, 5, 6], "regen_period": [2, 3, 4], "snap_jitter": [10], "steps": [300]},
    "conditions": COND,
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "hypotheses": HYP,
}
