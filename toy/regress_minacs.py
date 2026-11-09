# -*- coding: utf-8 -*-
"""Regression: the common judgment layer (acsjudge) reproduces the MinACS-specific analysis (E6) exactly.
Compares every set, the pair table, the exact checks and closed-loop trajectories (named backgrounds and
the E1 policies on tuning seeds 1-10).  python3 regress_minacs.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from acsjudge.judge import Judge, pair_table as gpt          # noqa: E402
from acsjudge import trajectory as gtr                         # noqa: E402
from acsjudge.checks import exact_checks                       # noqa: E402
from domains import minacs_domain as dm                        # noqa: E402
from minacs.analysis import Model, pair_table as opt           # noqa: E402
from minacs import trajectory as otr                           # noqa: E402

J, M = Judge(dm.D), Model("base")
res = []


def same(name, a, b):
    res.append((name, a == b))


same("viab_stages", J.viab_stages(), M.viab_stages())
same("viab_core", J.viab_core(), M.viab_core())
same("viab_resp", J.viab_resp(), M.viab_resp())
same("robust_all_e_kernel", J.robust_all_e_kernel(), M.robust_all_e_kernel())
same("CR1", J.CR1(lambda x: x.s), M.CR1(lambda x: x.s))
same("pair_table", gpt(J), opt(M))
same("Crit/U_rob/EC/Hor", [(J.Crit(x), J.U_rob(x), J.EC(x)) for x in J.XS] + [J.hor(J.viab_stages())],
     [(M.Crit(x), M.U_rob(x), M.EC(x)) for x in M.XS] + [M.hor(M.viab_stages())])
for bname in ("mild", "cold", "famine"):
    for learn in (True, False):
        o = otr.run(M, bname, learn=learn)
        g = gtr.run(J, dm.MIND, otr.background(bname, 48 + 10 + 1), 48, dm.X0, dm.O0, dm.M0, learn=learn)
        same(f"trajectory {bname}/learn={learn}", g, o)
from e4.adapters import minacs_background, BG_LEN    # noqa: E402
from e4 import policies_minacs as pm                  # noqa: E402
for seed in range(1, 11):
    bg = minacs_background(seed, BG_LEN, 3, 3, 3, gift_window=60)
    for nm, mk in (("P-mech", lambda: None), ("P-Viab-first", lambda: pm.p_viab("first")),
                   ("P-A-greedy", lambda: pm.p_A("greedy")), ("P-fixed", lambda: pm.p_fixed(seed))):
        o = otr.run(M, None, T=60, bg=bg, recover=True, policy=mk())
        g = gtr.run(J, dm.MIND, bg, 60, dm.X0, dm.O0, dm.M0, recover=True, policy=mk())
        same(f"trajectory seed {seed} {nm}", g, o)
ck, *_ = exact_checks(J)
res.append(("exact checks all OK on MinACS via the common layer", all(ok for _, ok, _ in ck)))
for n, ok in res:
    print(("OK " if ok else "NG ") + n)
print(f"NG = {sum(1 for _, ok in res if not ok)} / {len(res)}")
