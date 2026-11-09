# -*- coding: utf-8 -*-
"""Preregistration P10 (furnace keeper): experiments A, B1, C on held-out aperiodic backgrounds, B2 on periodic."""
import importlib.util
import os
_s = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                              "P10_abc_common.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)
SPEC = {
    "id": "P10_abc_furnace_r1", "model": "e10_exact", "purpose": C.PURPOSE, "hypotheses_note": C.NO_HYPOTHESES,
    "tuning_history": "Nothing tuned (furnace model and mechanism of E8).  Smoke test of the unit on tuning seeds 1-2 "
                      "at one sweep point (hot_len 5, deliv 3, draught 1) before registration.",
    "periodic_background": "period 12; one hot spell per block at a seed-fixed offset, delivery every deliv_period "
                           "steps, `draught` bad-draught steps at seed-fixed positions per block.",
    "sources": ["acsjudge/*.py", "domains/*.py", "domains/furnace/*.py", "minacs/*.py", "e4/*.py", "run_prereg.py"],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"domain": ["furnace"], "hot_len": [4, 5, 6], "deliv_period": [2, 3, 4], "draught": [1, 2]},
    "conditions": ["aper", "periodic"],
    "rule_variants": {"R0": {}}, "rule_independent_metrics": [],
    "hypotheses": [dict(C.REG, conditions=["aper"])],
}
