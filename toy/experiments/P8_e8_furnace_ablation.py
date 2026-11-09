# -*- coding: utf-8 -*-
"""Preregistration P8 = E8 part 2: E2 (ablation of principle-related function groups) repeated on the second
domain (furnace keeper).  Written before any evaluation seed was run on this domain."""
import os
import importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_s = importlib.util.spec_from_file_location("p7", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                "P7_e8_furnace_policies.py"))
_p7 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_p7)
PAIR = _p7.PAIR
GROUPS = [
    ("-integ", "情報取得・統合", "M1 の時間統合（燃焼後の温度変化から煙道の煤を推定すること）を外す"),
    ("-feas", "可行性感応評価", "M2 の Π_eval を定数にし、自己状態の閾値に基づく要請（寒・暑・燃料）を出さない"),
    ("-resp", "応答可能性評価・再構成", "目的からの候補生成と一段の先読みを外し、候補を U 全体、適合度を目的と行動の固定表にする"),
    ("-envuse", "環境利用・外部結合評価", "必要環境要因（燃料・煙道）に関わる目的と候補（集める・開ける）を外す"),
    ("-select", "応答形成・選択", "適合度を一定にし、候補のうち U の順で最初のものを選ぶ"),
    ("-update", "時間横断的情報保持・更新", "Update を恒等写像にする（M は M0 のまま）"),
    ("-phys", "物理的感知・作用・基盤維持", "PSL-4 の保護応答（暑い外気で tp≥4 のとき開ける）を外す"),
]
SPEC = {
    "id": "P8_e8_furnace_ablation_r1",
    "model": "e8_e2_furnace",
    "purpose": "E8 (Q7): repeat the main part of E2 (P4, v2 toy) on the furnace keeper: remove one principle-related "
               "function group (def:principle_related_functions) from the mechanism and compare T_col with the full "
               "mechanism on held-out seeds.",
    "ablation_implementation": {k: v for k, _, v in GROUPS},
    "ablation_mapping_note": "The mapping from the paper's function groups to code-level removals is a toy convention.",
    "tuning_history": _p7.TUNING,
    "sources": _p7.SPEC["sources"],
    "seeds": _p7.SPEC["seeds"],
    "sweep": _p7.SPEC["sweep"],
    "conditions": ["full"] + [k for k, _, _ in GROUPS],
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "hypotheses": [
        {"id": f"H{n + 1}", "kind": "paired", "metric": "T_col", "conditions": ["full", k],
         "statement": f"完全な機構の T_col は、{name}を除いた機構（{impl}）以上である。",
         "how_it_could_fail": "除去によって費用のかかる行動（燃焼・開放）が減り、存続が延びうる。試運転（調整用 seed）の生存は"
                              "完全 50 に対し -integ 51、-update 51、-phys 50、-resp 22、-feas・-envuse・-select 0 だった。"
                              "-integ・-update・-phys は大半の単位で同値になり、判定不能になりうる。",
         "rule": PAIR}
        for n, (k, name, impl) in enumerate(GROUPS)
    ],
}
