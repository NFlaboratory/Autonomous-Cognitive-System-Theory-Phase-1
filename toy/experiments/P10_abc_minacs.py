# -*- coding: utf-8 -*-
"""Preregistration P10 (MinACS): experiments A, B1, C on held-out aperiodic backgrounds, B2 on periodic ones."""
import importlib.util
import os
_s = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                              "P10_abc_common.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)
SPEC = {
    "id": "P10_abc_minacs_r1", "model": "e10_exact", "purpose": C.PURPOSE, "hypotheses_note": C.NO_HYPOTHESES,
    "tuning_history": "Nothing tuned (MinACS model and mechanism of E6).  Smoke test of the unit on tuning seeds 1-2 "
                      "at one sweep point (cold_len 3, regrow 5, gifts 3) before registration.",
    "periodic_background": "period lcm(12, regrow_period); one cold spell per 12-step block at a seed-fixed offset, "
                           "regrowth every regrow_period steps, gift_events gifts at seed-fixed positions per period.",
    "sources": ["acsjudge/*.py", "domains/*.py", "domains/furnace/*.py", "minacs/*.py", "e4/*.py", "run_prereg.py"],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"domain": ["minacs"], "cold_len": [2, 3, 4], "regrow_period": [2, 3, 5], "gift_events": [0, 3]},
    "conditions": ["aper", "periodic"],
    "rule_variants": {"R0": {}}, "rule_independent_metrics": [],
    "hypotheses": [dict(C.REG, conditions=["aper"])],
}
