# -*- coding: utf-8 -*-
"""Preregistration P9 r2: identical hypotheses, conditions, seeds and decision rules to P9 r1.
r1 was registered and started, but was stopped at the 2-hour limit of the execution environment before
any result had been written (the log was empty; no evaluation output was seen).  To finish within the limit,
two sources were changed, neither of which changes any unit's result:
  - the kernel oracle's successor tables and in_core answers are shared across units with the same body
    parameters (e4/policies_v2.py, e4/adapters.py);
  - run_prereg.py can run units in parallel (--jobs).
Equality was checked before registration on tuning seeds 1-5 (shared vs fresh oracle, 16 units: 0 differ;
seed 1 smoke values reproduced)."""
import importlib.util
import os
_s = importlib.util.spec_from_file_location("p9r1", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                  "P9_e1_v2_policies.py"))
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
SPEC = dict(_m.SPEC)
SPEC["id"] = "P9_e1_v2_policies_r2"
SPEC["deviation_from_r1"] = (__doc__.split("\n", 1)[1]).strip()
