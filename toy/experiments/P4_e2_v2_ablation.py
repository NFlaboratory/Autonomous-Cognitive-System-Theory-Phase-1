# -*- coding: utf-8 -*-
"""Preregistration P4 = E2 on the v2 toy: ablation of principle-related function groups.
Written before any evaluation seed was run with the ablations."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAIR = {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}
GROUPS = [
    ("-integ", "情報取得・統合", "M1 の時間統合を外す（見えないものの信念を直ちに失効させる）"),
    ("-feas", "可行性感応評価", "M2 の Π_eval を定数にし、自己状態の閾値に基づく欠乏・警告の要請を出さない"),
    ("-resp", "応答可能性評価・再構成", "先読みを外し（深さ 1）、候補を目的から生成せず U 全体に固定する"),
    ("-envuse", "環境利用・外部結合評価", "必要環境要因（energy・heat）に関わる目的の形成と候補の追加を外す"),
    ("-select", "応答形成・選択", "適合度を一定にし、選択射影の既定順だけで選ぶ"),
    ("-update", "時間横断的情報保持・更新", "Update を恒等写像にする（学習・忘却・記録の更新なし）"),
    ("-phys", "物理的感知・作用・基盤維持", "PSL-4 の保護応答と repair を外す"),
    ("-auto", "（追加）自動化", "ルーティン応答（比較を経ない応答）を外す"),
    ("-relation", "（追加）関係", "relation の要請（合図・贈与）を外す"),
    ("-rescuers", "（追加）救助の担い手", "relation を外し、ドローンと組織も除く"),
]
SPEC = {
    "id": "P4_e2_v2_ablation_r1",
    "model": "e2_v2",
    "purpose": "E2: remove one principle-related function group (def:principle_related_functions, 7 groups) "
               "or one additional element from both individuals' mechanisms in the v2 toy, and compare the "
               "collapse-reaching times with the full mechanism on held-out seeds.",
    "ablation_implementation": {k: v for k, _, v in GROUPS},
    "ablation_mapping_note": "The mapping from the paper's function groups to code-level removals is a toy "
                             "convention; another implementation of the same removal could give different results.",
    "tuning_history": "The v2 mechanism was tuned on seed 1 (fixed severe-cold periods).  The ablation switches "
                      "were written before any run.  One smoke test of all 11 conditions on tuning seed 1 "
                      "(eat_gain 5, regen 3, snap_jitter 10) was run before registration and showed T_col_sum: "
                      "full 334, -integ 172, -feas 57, -resp 236, -envuse 57, -select 131, -update 252, -phys 334, "
                      "-auto 539, -relation 468, -rescuers 468.  Seeds 11-60 were not run before registration.",
    "metric_note": "T_col_sum = T_col(i) + T_col(j), a structure lost at no time within 300 steps counted as 301.",
    "sources": [os.path.join(ROOT, "TOY2", "acs_toy", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"eat_gain": [4, 5, 6], "regen_period": [2, 3, 4], "snap_jitter": [10], "steps": [300]},
    "conditions": ["full"] + [k for k, _, _ in GROUPS],
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "hypotheses": [
        {"id": f"H{n + 1}", "kind": "paired", "metric": "T_col_sum", "conditions": ["full", k],
         "statement": f"完全な機構の T_col_sum は、{name}を除いた機構（{impl}）以上である。",
         "how_it_could_fail": "除去によって費用のかかる行動（移動・合図・修復・往復）が減り、存続が延びうる。"
                              "登録前の試運転（調整用 seed 1）で -auto・-relation・-rescuers は完全な機構を上回り、"
                              "-phys は同値だった。",
         "rule": PAIR}
        for n, (k, name, impl) in enumerate(GROUPS)
    ],
}
