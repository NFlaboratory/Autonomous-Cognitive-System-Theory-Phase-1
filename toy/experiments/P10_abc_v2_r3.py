# -*- coding: utf-8 -*-
"""Preregistration P10 (v2) r3: same metrics, conditions, seeds and check as r1 and r2.
r1 and r2 were registered and started; in both, a worker process was killed by the memory limit (out of memory)
and the run hung before any result was written (no evaluation output was seen).
Changes for r3: (1) the successor-table cache of the kernel oracle is cleared above 2,000 tables (the tables are
pure functions of x and are recomputed on demand; results unchanged); (2) the certificate memo is local to each
unit (in r2 it was shared across units, which would have made a unit's U^Viab_cert depend on the order in which
units are run).  Within a unit, U^Viab_cert(x) is taken with respect to the first certificate that covered x, a
valid lower bound of U^Viab(x); the counts of u in U^Viab_cert (and so C2 / C3) depend on which certificate is used.
Order independence was checked before registration on tuning seeds 1-3 (default world): identical results in both
orders."""
import importlib.util
import os
_s = importlib.util.spec_from_file_location("r1", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                               "P10_abc_v2.py"))
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
SPEC = dict(_m.SPEC)
SPEC["id"] = "P10_abc_v2_r3"
SPEC["deviation_from_r1_r2"] = (__doc__.split("\n", 1)[1]).strip()
SPEC["tuning_history"] = SPEC["tuning_history"] + "  Before r3: tuning seeds 1-3 (default world) rerun to check memory and order independence."
