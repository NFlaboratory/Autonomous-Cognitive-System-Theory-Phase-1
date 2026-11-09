# -*- coding: utf-8 -*-
"""G6: the same furnace world with different Update rules (toy variants of the learning part bo).
sec.5 assumes no universal learning rule, no convergence and no monotonicity.  For every variant we check
the conditions that do NOT depend on the rule (observation factorisation, P1-P3) and exhibit, exactly,
whether M_t converges or keeps changing and whether learning stops on the trajectory.

No comparison of survival between variants is made here (that would be a hypothesis and would need
pre-registration with run_prereg.py).
  M = (bo, rec, pur): bo = learning component M^L, (rec, pur) = working component M^W (toy split).
  orig   : the furnace Update (bo inferred from the record, set to 1 after open)
  frozen : bo is never changed (Update restricted to M^W)
  flip   : bo' = 1 - bo whenever the body is active (a rule that never converges; a counterexample-type
           illustration that Update need not converge)
  forget : bo' = 1 when there is no new evidence, else the inferred value
python3 verification/update_rules.py
"""
import itertools
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import Report                         # noqa: E402
from domains.furnace import model as fm         # noqa: E402
from domains.furnace import mind as fd          # noqa: E402
import check_structure as cs                    # noqa: E402


class Variant(cs.FurnaceMech):
    def __init__(self, rule):
        super().__init__()
        self.rule = rule
        self.name = f"Furnace[{rule}]"

    def Update(self, M, x, e, learn=True):
        M1 = self.m.Update(M, x, e, learn=True)
        if not fm.base_active(x) or self.rule == "orig":
            return M1
        if self.rule == "frozen":
            return M1._replace(bo=M.bo)
        if self.rule == "flip":
            return M1._replace(bo=1 - M.bo)
        if self.rule == "forget":
            return M1 if M1.bo != M.bo else M1._replace(bo=1)
        raise ValueError(self.rule)


def orbit(mech, x0, o0, M0, pat):
    """exact eventually-periodic run: returns (prefix length, cycle states list)."""
    p = len(pat)
    seen = {}
    x, o, M, t = x0, o0, M0, 0
    seq = []
    while (x, o, M, t % p) not in seen:
        seen[(x, o, M, t % p)] = t
        b = pat[t % p]
        e = fm.D.make_e(b, o)
        u = mech.operate(M, x, e)["u"]
        seq.append((x, o, M))
        x, o, M = fm.f(x, u, e), fm.g_O(o, x, u, b), mech.Update(M, x, e)
        t += 1
    t0 = seen[(x, o, M, t % p)]
    return seq, t0


def main():
    R = Report("update_rules")
    B = sorted({fm.D.split(e)[0] for e in fm.ES})
    pats = [pat for p in (1, 2) for pat in itertools.product(B, repeat=p)]
    x0s = [x for x in fm.XS if x.s == 1 and x.tp >= 1][::4]
    for rule in ("orig", "frozen", "flip", "forget"):
        mech = Variant(rule)
        print(f"--- {rule}")
        res = cs.struct_checks(None, mech, mech.name, only=("S01", "S07", "S08", "S09"), report=False)
        for cid in ("S01", "S07", "S08", "S09"):
            labels, n, prem, bad, detail = res[cid]
            R.check(f"U_{cid}_{rule}", labels, mech.name, n, prem, [repr(b)[:150] for b in bad[:2]], detail)
        C = Counter()
        for x0 in x0s:
            for pat in pats:
                seq, t0 = orbit(mech, x0, 1, fd.M0, pat)
                cyc = seq[t0:]
                C["runs"] += 1
                bos = {M.bo for (_, _, M) in cyc}
                Ms = {M for (_, _, M) in cyc}
                C["M_converges" if len(Ms) == 1 else "M_keeps_changing"] += 1
                C["learning_stops" if len(bos) == 1 else "learning_never_stops"] += 1
                for k in range(1, len(seq)):
                    a, b = seq[k - 1][2], seq[k][2]
                    if a.bo != b.bo:
                        C["steps_ML_changed"] += 1
                    elif a != b:
                        C["steps_only_MW_changed"] += 1
        status = "EXAMPLE_ONLY"
        R.add(f"U_census_{rule}", ["def:learning_intertime_change", "def:update_stop_on_trajectory",
              "def:model_learning_working", "def:intertime_update"], mech.name, status, C["runs"], None,
              "exact eventually-periodic runs (initial states x 1/4, background patterns of period 1-2)", dict(C), "census")
        print(dict(C))
    return R.save()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
