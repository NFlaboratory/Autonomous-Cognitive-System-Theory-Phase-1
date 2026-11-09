# -*- coding: utf-8 -*-
"""Preregistration P1 (MinACS).  Written before any evaluation seed was run."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = {
    "id": "P1_minacs_learning_r1",
    "model": "minacs",
    "purpose": "E4 pilot: does the E6 learning / no-learning contrast (observed on three hand-picked backgrounds "
               "after tuning) hold on held-out, seed-generated backgrounds; is the Recover narrowing before "
               "collapse dependent on the Recover judgment rule.",
    "tuning_history": "MinACS model and mechanism thresholds were tuned on the three named backgrounds "
                      "(mild, cold, famine) of minacs/trajectory.py.  Seeds 1-10 of the seed generator are "
                      "reserved for smoke tests (seed 1 was run once for a smoke test before registration); "
                      "seeds 11-60 were not run before registration.",
    "sources": [os.path.join(ROOT, "MINACS", "minacs", "*.py"), os.path.join(ROOT, "E4", "e4", "*.py"),
                os.path.join(ROOT, "E4", "run_prereg.py")],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"cold_len": [2, 3, 4], "regrow_period": [2, 3, 5], "gift_events": [0, 3]},
    "conditions": ["learn", "no-learn"],
    "rule_variants": {
        "R0": {"recover_horizon": 10, "recover_rule": "first"},
        "R1": {"recover_horizon": 5, "recover_rule": "first"},
        "R2": {"recover_horizon": 20, "recover_rule": "first"},
        "R3": {"recover_horizon": 10, "recover_rule": "hold2"},
    },
    "rule_independent_metrics": ["T_col", "blocked", "B1", "B2"],
    "hypotheses": [
        {"id": "H1", "kind": "paired", "metric": "T_col", "conditions": ["learn", "no-learn"], "variants": ["R0"],
         "statement": "Update が働く個体（learn）の崩壊到達時刻は、信念を更新しない個体（no-learn）以上である"
                      "（崩壊なしは +∞ とみなす）。",
         "rule": {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}},
        {"id": "H2", "kind": "share", "predicate": "recover_narrowed_before_collapse",
         "conditions": ["learn", "no-learn"],
         "statement": "崩壊した軌道では、崩壊直前の生存時刻に Recover=1 となる許容外的作用が 3 種すべてではない"
                      "（外的回復可能性が狭まっている）。",
         "rule": {"support_min": 0.9, "reject_max": 0.5}},
        {"id": "H3", "kind": "share", "predicate": "blockage_before_collapse", "conditions": ["learn", "no-learn"],
         "variants": ["R0"],
         "statement": "（モデル記述の仮説）MinACS では崩壊した軌道のすべてで、崩壊前に少なくとも一度閉塞が生じる。"
                      "本文の『崩壊は閉塞の事前経由を要しない』とは別の、このモデルについての記述。",
         "rule": {"support_min": 0.9, "reject_max": 0.5}},
    ],
}
