# -*- coding: utf-8 -*-
"""Preregistration P10 (v2) r2: same metrics, conditions, seeds and check as r1.
r1 was registered and started; a worker process was killed by the memory limit (out of memory) and the run hung
before any result was written (no evaluation output was seen).  The memo of kernel-oracle answers was changed to
store one certificate per in_core call for all states it certifies, and to be cleared above 200,000 entries.
Consequence for the measurement: U^Viab_cert(x) is now taken with respect to the first certificate that covered x,
which can differ from the certificate built at x itself; both are valid lower bounds of U^Viab(x), but the counts of
u in U^Viab_cert (and so C2 / C3) depend on which certificate is used."""
import importlib.util
import os
_s = importlib.util.spec_from_file_location("r1", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                               "P10_abc_v2.py"))
_m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_m)
SPEC = dict(_m.SPEC)
SPEC["id"] = "P10_abc_v2_r2"
SPEC["deviation_from_r1"] = (__doc__.split("\n", 1)[1]).strip()
SPEC["tuning_history"] = SPEC["tuning_history"] + "  Before r2: one unit (seed 1, default world) rerun to check memory."
