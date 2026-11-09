# -*- coding: utf-8 -*-
"""Preregistration P2 (v2 toy).  Written before any evaluation seed was run."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = {
    "id": "P2_v2_drone_r1",
    "model": "v2",
    "purpose": "E4 pilot: does the presence of the non-ACS rescuer (drone) delay collapse on held-out seeds "
               "with jittered severe-cold periods and swept world parameters.",
    "tuning_history": "The v2 mechanism was tuned on seed 1 (default scenario, fixed severe-cold periods). "
                      "Seed 2 was run once with snap_jitter=10 as a smoke test before registration. "
                      "Seeds 11-60 with snap_jitter were not run before registration.",
    "sources": [os.path.join(ROOT, "TOY2", "acs_toy", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"eat_gain": [4, 5, 6], "regen_period": [2, 3, 4], "snap_jitter": [10], "steps": [300]},
    "conditions": ["drone", "no_drone"],
    "rule_variants": {"R0": {}},
    "rule_independent_metrics": [],
    "judgment_rule_note": "T_col uses only the (SC-1) rule of v2 (integ = 0); zone, Recover and (FT-2) rules are "
                          "not involved, so no rule variants are registered for P2.",
    "hypotheses": [
        {"id": "H4", "kind": "paired", "metric": "T_col_i", "conditions": ["drone", "no_drone"],
         "statement": "ドローン（非 ACS の救助者）がいるとき、個体 i の崩壊到達時刻はいないとき以上である。",
         "rule": {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}},
        {"id": "H5", "kind": "paired", "metric": "T_col_j", "conditions": ["drone", "no_drone"],
         "statement": "同じく個体 j について。",
         "rule": {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}},
    ],
}
