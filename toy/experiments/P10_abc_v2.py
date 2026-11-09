# -*- coding: utf-8 -*-
"""Preregistration P10 (v2 toy): experiments A, B1, C for individual i under its own mechanism (certificates)."""
import importlib.util
import os
_s = importlib.util.spec_from_file_location("c", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                              "P10_abc_common.py"))
C = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C)
SPEC = {
    "id": "P10_abc_v2_r1", "model": "e10_v2", "purpose": C.PURPOSE, "hypotheses_note": C.NO_HYPOTHESES,
    "certificate_note": "Viab_f(K) is decided by certificates ('in' / 'not_in' / 'undetermined').  U^Viab_cert is a "
                        "subset of U^Viab, so u in U^Viab_cert is a lower bound and C2, C3 are upper bounds.  B2 is not "
                        "run on v2 (backgrounds are not periodic).",
    "tuning_history": "Nothing tuned (v2 mechanism tuned earlier on seed 1).  Smoke test on tuning seed 1 at one point.",
    "sources": ["acs_toy/*.py", "e4/*.py", "run_prereg.py"],
    "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
    "sweep": {"eat_gain": [4, 5, 6], "regen_period": [2, 3, 4], "snap_jitter": [10], "steps": [300]},
    "conditions": ["alone", "default"],
    "rule_variants": {"R0": {}}, "rule_independent_metrics": [],
    "hypotheses": [dict(C.REG, conditions=["alone", "default"])],
}
