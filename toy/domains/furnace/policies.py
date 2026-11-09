# -*- coding: utf-8 -*-
"""E8-E1 policies on the furnace keeper, the counterparts of the MinACS E1 policies (E4/e4/policies_minacs.py).
Oracle policies read the true Viab_f(K), A(x,e) and e: reference trajectories, NOT realisable by the
individual.  P-greedy reads the observation P_sens only; P-fixed is independent of x and e."""
from . import model as fm
from . import mind as fd

_C = {}


def _sets():
    if "J" not in _C:
        from acsjudge.judge import Judge
        J = Judge(fm.D)
        core = J.viab_core()
        _C.update(J=J, core=core, uv={x: J.U_viab(x, core) for x in core})
    return _C["J"], _C["core"], _C["uv"]


def p_viab(order):
    def pol(x, e):
        J, core, uv = _sets()
        cand = uv[x] if (x in core and uv[x]) else J.A(x, e)
        if not cand:
            return "wait"
        return cand[0] if order == "first" else cand[-1]
    return pol


def p_A(mode):
    """'first' = first u of A in U order; 'greedy' = successor with tp closest to 3, then most fuel."""
    def pol(x, e):
        J, core, uv = _sets()
        A = J.A(x, e)
        if not A:
            return "wait"
        if mode == "first":
            return A[0]
        return max(A, key=lambda u: (-abs(J._succ[(x, u, e)].tp - 3), J._succ[(x, u, e)].fu, -J.U.index(u)))
    return pol


def p_greedy():
    """reflex on the observation only (no memory, no evaluation of K)."""
    def pol(x, e):
        _, fu, tp, s, h, d = fd.P_sens(x, e)
        if h is None:
            return "wait"
        if tp >= 4:
            return "open"
        if tp <= 2 and fu >= 1:
            return "burn"
        if d == 1 and fu <= 2:
            return "gather"
        return "wait"
    return pol


def p_fixed(seed, lcg):
    seq = []
    r = lcg(seed + 104729)
    for _ in range(256):
        seq.append(fm.U[next(r) % 4])
    state = {"k": 0}

    def pol(x, e):
        u = seq[state["k"] % len(seq)]
        state["k"] += 1
        return u
    return pol


def p_wait():
    return lambda x, e: "wait"
